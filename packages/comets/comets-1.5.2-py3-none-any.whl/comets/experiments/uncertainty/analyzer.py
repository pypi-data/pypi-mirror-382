# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import inspect
import warnings

import numpy as np
import pandas as pd
import scipy.stats

try:
    from ddsketch import DDSketch
except ImportError:  # pragma: no cover
    DDSKETCH_AVAILABLE = False
else:
    DDSKETCH_AVAILABLE = True


from . import descriptivestats
from ...core.parameterset import ParameterSet
from ...utilities import get_logger
from ...utilities.registry import Registry

# set up an empty statistics registry
StatisticsRegistry = Registry()


class StatAnalyzer:
    """
    Statistical data analyzer
    """

    def __init__(self, list_of_statistics):
        self._requested_statistics = []
        for key in list_of_statistics:
            if key in StatisticsRegistry.keys():
                self._requested_statistics.append(key)
            else:
                logger = get_logger(__name__)
                logger.warning(
                    "Key {} is not in the StatisticsRegistry and will be ignored".format(
                        key
                    )
                )
        if len(self._requested_statistics) == 0:
            raise ValueError(
                'No valid statistics were requested. '
                'See the StatisticsRegistry for valid statistics.'
            )
        # Change to True if the user wants to see warnings
        self.show_warnings = False

    def compute_statistics(self, data):
        '''
        Calculates the actual stats based on the input data

        Args
            data (list of ParameterSets): the dataset on which the statistics
                will be computed.
        '''
        # Filter to keep only columns having a numeric type
        df = ParameterSet.to_dataframe(data, keep_numeric_only=True)
        output_dfs = {}
        output_scalars = {}
        with warnings.catch_warnings():
            if not self.show_warnings:
                warnings.simplefilter("ignore")
            for func in self._requested_statistics:
                if StatisticsRegistry.information[func]["Results key"] == func:
                    # If the output estimator format is a DataFrame, add the DataFrame to the results
                    output_dfs.update(StatisticsRegistry[func](df))
                else:
                    # If the output estimator format is a Series, add the Series to the general DataFrame
                    output_scalars.update(StatisticsRegistry[func](df))

        results = {"statistics": pd.DataFrame(output_scalars)}
        results.update(output_dfs)
        return results


class OnlineStatAnalyzer:

    """
    Statistical data analyzer for the online computation of descriptive stats.
    It is initialised with a list of statistics which will be computed.
    Upon addition of a sample in the .update() method, the requested statistics
    are updated for each of the output values of the sample.

    Most results are exact (i.e. they are the same as the offline stats), but
    all stats that are based on a quantile (e.g. median, 75th quantile) are
    _approximations_ based on the DDSketch algorithm.

    Computations for multiple simulation outputs (KPIs) are vectorized for all
    the non-quantile stats.

    Note:
        It is assumed that all subsequent samples have exactly the same
        structure.

    Args:
        list_of_statistics (list of strings): user-supplied list of statistics
            that will be calculated in OnlineStatAnalyzer.
            These statistics are described in the StatisticsRegistry with
            the 'Online available' flag.
    """

    # Define stats that are recursive (and always need to be stored)
    _recursive_stats = ['count', 'mean', 'min', 'max', 'M2']

    # Define statistics which depend on a quantile store
    _quantile_stats = ['all', 'quantiles', 'box_plot', 'median', 'Q1', 'Q3']

    # Define stats that don't have a direct corresponding function but
    # are derived from a different existing function.
    _no_function_stats = [
        'confidence_intervals_of_the_mean',
        'conf_int_mean_95pct',
        'Q1',
        'Q3',
        'median',
        'quantiles',
    ]

    # Define umbrella stats
    _umbrella_stats = dict(
        minmax=['min', 'max'],
        standard=['mean', 'std', 'sem', 'conf_int_mean_95pct'],
        box_plot=['mean', 'median', 'Q1', 'Q3', 'min', 'max'],
        # not implemented at this point:
        # high_order=['skewness', 'kurtosis'],
        # central=['mean', 'geometric_mean', 'harmonic_mean'],
    )

    def __init__(self, list_of_statistics):
        if not DDSKETCH_AVAILABLE:
            raise ImportError(
                "This method (online_stats=True) is only available with optional dependency ddsketch. Either install CoMETS with:\n"
                "  - `pip install comets[ua]`, \n"
                "  - `pip install comets[all]`,\n"
                "  - or install DDSketch with `pip install ddsketch`."
            )

        self._first_update = True
        # Info gathered at first task execution, to make manipulation of parameterset faster
        self._parametersets_are_flat = False
        self._parameterset_non_numerical_keys = []
        # initialise a "registry" with method names pointing to methods
        self._create_function_registry()

        # create 'all' element of umbrella stats
        self._umbrella_stats['all'] = [
            k
            for k in StatisticsRegistry.keys()
            if StatisticsRegistry.information[k]['Online available']
        ]

        # initialise the list of statistics (requested and expanded to all necessary values)
        self._check_requested_statistics(list_of_statistics)

        # initialise stats objects (to None)
        self.df_stats = None
        # if '_quantile' in self._requested_statistics:
        if self._computing_quantiles:
            self._quantile_store = None
        # Change to True if the user wants to see warnings
        self.show_warnings = False

    def _create_function_registry(self):
        '''
        Create a list of all methods in OnlineStatAnalyzer.
        This is not a real registry in the CoMETS sense, just a dict.
        '''

        self._FunctionRegistry = dict(inspect.getmembers(self, inspect.ismethod))

    def _check_requested_statistics(self, list_of_statistics):
        '''
        Process the supplied list_of_statistics to check their availability
        * expand the 'umbrella' terms ('minmax', 'standard') to the actual
          statistics that are desired.
        * remove statistics that cannot be supplied (and issue a warning)
        '''

        # copy so that the input list isn't modified
        list_of_statistics = list(list_of_statistics)

        # Check if every requested stat is available.
        cleaned_up_list = []
        for key in list_of_statistics:
            if (
                key in StatisticsRegistry.keys()
                and StatisticsRegistry.information[key]['Online available']
            ) or key == 'all':
                cleaned_up_list.append(key)
            else:
                logger = get_logger(__name__)
                logger.warning(
                    "Key {} is not available and will be ignored".format(key)
                )
        self._requested_statistics = cleaned_up_list

        # Reject analyzer if no valid stats were requested
        if len(self._requested_statistics) == 0:
            raise ValueError(
                'No valid statistics were requested. '
                'See the StatisticsRegistry for valid statistics.'
            )

        # Check if quantiles need to be stored
        quantile_overlap = set.intersection(
            set(self._requested_statistics), set(self._quantile_stats)
        )
        if len(quantile_overlap) > 0:
            self._computing_quantiles = True
        else:
            self._computing_quantiles = False

    def update(self, sample):
        '''
        Update the OnlineStatAnalyzer object with a sample consisting of the
        output of a single simulation.

        Args
            sample (ParameterSet): the output of a single Task in ParameterSet
                format.
        '''
        if self._first_update:
            # Check if the parameterset is flat
            self._parametersets_are_flat = len(ParameterSet.flatten(sample)) == len(
                sample
            )

        # Flatten only if necessary
        if not self._parametersets_are_flat:
            sample = ParameterSet.flatten(sample)

        # Filter out non-numerical values
        if self._first_update:
            for key, val in sample.items():
                if not isinstance(val, (int, float)):
                    # List key as an element to remove
                    self._parameterset_non_numerical_keys.append(key)

        for key in self._parameterset_non_numerical_keys:
            sample.pop(key, None)  # error-safe removal

        # Transform to an 1-D numpy array
        samplenp = np.asarray(list(sample.values()))

        # For the first iteration: create initial stats objects.
        # These objects are created in .update() rather than in __init__()
        # because at the __init__ stage we don't yet know the sample
        # length and therefore the shape of the stats objects.
        if self._computing_quantiles and self._first_update:
            # initialise empty DDSketch objects for each element in the sample
            self._quantile_store = [DDSketch() for _ in samplenp]
        if self._first_update:
            self.df_stats = self._create_initial_df_stats(sample, samplenp)
            self._first_update = False

        # Update all stats that require recursive bookkeeping
        self._update_recursive_stats(sample, samplenp)

    @staticmethod
    def _create_empty_stats_df(sample, list_of_statistics, fill_value=np.nan):
        return pd.DataFrame(
            data=np.full((len(sample), len(list_of_statistics)), fill_value),
            columns=list_of_statistics,
            index=sample.keys(),
        )

    def _create_initial_df_stats(self, sample, samplenp):
        '''
        When there is no df_stats yet, create one when the first
        sample is received. This dataframe has columns for all the
        stats that are based on recursive computations. Other stats
        can be derived from these.
        '''

        df_stats_init = self._create_empty_stats_df(sample, self._recursive_stats)

        # deal with the stats that should initialise at zero.
        init_at_zero = ['mean', 'count', 'M2']
        df_stats_init[init_at_zero] = 0

        # deal with min and max (initialise to sample value)
        init_at_sample = ['min', 'max']
        df_stats_init[init_at_sample] = np.column_stack(
            [samplenp] * len(init_at_sample)
        )

        return df_stats_init

    def _update_recursive_stats(self, sample, samplenp):
        '''Update all stats that have a recursive relationship'''

        dfnew = self._create_empty_stats_df(sample, self._recursive_stats)

        # Update stats, except quantiles
        for stat in self._recursive_stats:
            dfnew[stat] = self._FunctionRegistry[f'_compute_new_{stat}'](samplenp)

        # Update the quantile store, if quantiles are being computed
        if self._computing_quantiles:
            for sketch, samplevalue in zip(self._quantile_store, samplenp):
                sketch.add(samplevalue)

        # update df_stats with the new df.
        self.df_stats = dfnew

    def compute_statistics(self, replace_nan_with=None):
        '''
        Create a complete statistics dataframe based on the values that were
        stored on-the-fly. --> conform StatAnalyzer output

        Args
            replace_nan_with (value): value passed to pandas.DataFrame.fillna()
                which replaces any NaNs that are in the finalised dataframe with
                the supplied value. Such NaNs may be present e.g. if variance or
                standard deviation (or derived values) are requested by the user
                but only a single sample has been added to the OnlineStatAnalyzer
                instance.
        '''

        # Raise an error if there are no stats
        if self.df_stats is None:
            raise ValueError(
                'No statistics can be displayed. Have you added any samples?'
            )

        # Expand umbrella stats into single statistics in the list of requested stats
        req_stats = self._expand_umbrella_stats(self._requested_statistics)

        # Separate out the 'normal' stats and 'special cases'.
        # Special cases are stats where columns in the final dataframe
        # have a name with special formatting and/or where a stat
        # method must be called with an argument.
        regular_req_stats = [x for x in req_stats if x not in self._no_function_stats]

        with warnings.catch_warnings():
            if not self.show_warnings:
                warnings.simplefilter("ignore")

            # Compute 'normal' stats in a loop
            final_stats = {}
            for stat in regular_req_stats:
                final_stats[stat] = self._FunctionRegistry[stat]()

            # Deal with the stats that don't have a single dedicated function
            if 'confidence_intervals_of_the_mean' in req_stats:
                for confidence in [0.68, 0.95, 0.99]:
                    final_stats[
                        f'confidence interval of the mean at {confidence*100:.0f}%'
                    ] = self._conf_int_mean(confidence)
            if 'conf_int_mean_95pct' in req_stats:
                confidence = 0.95
                final_stats[
                    f'confidence interval of the mean at {confidence*100:.0f}%'
                ] = self._conf_int_mean(confidence)
            if 'quantiles' in req_stats:
                for q in np.arange(0.05, 1, 0.05):
                    final_stats[f'quantile {q*100:.0f}%'] = self.quantile(quantile=q)
            for qname, qval in {'Q1': 0.25, 'median': 0.5, 'Q3': 0.75}.items():
                if qname in req_stats:
                    final_stats[qname] = self.quantile(quantile=qval)

        dffinal = pd.DataFrame(final_stats, index=self.df_stats.index)

        # replace any NaNs in the dataframe with `replace_nan_with`
        if replace_nan_with is not None:
            dffinal.fillna(replace_nan_with, inplace=True)

        # Return the statistics as a dictionary
        return {'statistics': dffinal}

    def _expand_umbrella_stats(self, list_of_statistics):
        '''Expand the umbrella stat names (e.g. minmax and box_plot) to actual statistics'''

        # Create a copy of requested stats to work on.
        req_stats = list(list_of_statistics)

        # Remove the umbrella stat names from the full list and insert
        # their dependencies into the list:
        for umbrella, expansion in self._umbrella_stats.items():
            if umbrella in req_stats:
                req_stats.extend(expansion)
        # remove (all instances of) umbrella terms
        return [y for y in req_stats if y not in self._umbrella_stats.keys()]

    # Computation of recursive stats:

    def _compute_new_count(self, sample):
        '''Compute new count based on previous value and new sample.'''

        # The usage of `~np.isnan()` ensures that NaN samples are ignored
        return self.df_stats['count'].to_numpy() + ~np.isnan(sample)

    def _compute_new_min(self, sample):
        '''Compute new min based on previous value and new sample.'''

        # The usage of fmin ensures that NaN samples are ignored
        return np.fmin(self.df_stats['min'].to_numpy(), sample)

    def _compute_new_max(self, sample):
        '''Compute new max based on previous value and new sample.'''

        # The usage of fmax ensures that NaN samples are ignored
        return np.fmax(self.df_stats['max'], sample)

    def _compute_new_mean(self, sample):
        '''Compute new mean based on previous value and new sample.'''

        oldmean = self.mean()
        delta_old = sample - oldmean

        # The usage of np.nan_to_num ensures that NaN samples are ignored
        result = oldmean + np.nan_to_num(delta_old / self._compute_new_count(sample))

        return result

    def _compute_new_M2(self, sample):
        '''
        Compute new M2 based on previous value and new sample.
        The quantity M2 is part of Welford's algorithm, a stable way of
        computing variance/std online -- see:
        https://stackoverflow.com/questions/5543651/computing-standard-deviation-in-a-stream
        '''

        oldmean = self.mean()
        oldM2 = self.M2()

        delta_old = sample - oldmean
        delta_new = sample - self._compute_new_mean(sample)

        # np.nan_to_num() ensures that samples with NaN are ignored.
        result = oldM2 + np.nan_to_num(delta_old * delta_new)

        return result

    def count(self):
        '''Return the count of the data ingested so far.'''
        return self.df_stats['count'].to_numpy()

    def min(self):
        '''Return the minimum of the data ingested so far.'''
        return self.df_stats['min'].to_numpy()

    def max(self):
        '''Return the maximum of the data ingested so far.'''
        return self.df_stats['max'].to_numpy()

    def mean(self):
        '''Return the mean of the data ingested so far.'''
        return self.df_stats['mean'].to_numpy()

    def M2(self):
        '''
        Return the M2 of the data ingested so far.
        The quantity M2 is part of Welford's algorithm, a stable way of
        computing variance/std online -- see:
        https://stackoverflow.com/questions/5543651/computing-standard-deviation-in-a-stream
        '''

        return self.df_stats['M2'].to_numpy()

    def variance(self, ddof=1):
        '''
        Compute the variance of the data ingested so far.

        Args
            ddof (int): controls whether the returned result is considered
            the unbiased sample variance (ddof=1), or the variance of an
            entire population.
        '''

        # Here we use np.divide in order to avoid divide-by-zero
        # and negative-variance shenanigans
        result = np.divide(
            self.M2(),
            self.count() - ddof,
            # return nan where count-ddof<1
            out=np.full(self.M2().shape, np.nan),
            where=self.count() - ddof > 0,
        )

        return result

    def std(self, ddof=1):
        '''
        Compute the standard deviation.

        Args
            ddof (int): controls whether the returned result is considered
            the unbiased sample variance (ddof=1), or the variance of an
            entire population.
        '''

        return np.sqrt(self.variance(ddof))

    def sem(self, ddof=1):
        '''
        Compute the standard error of the mean.

        Args
            ddof (int): controls whether the returned result is considered
                the unbiased sample variance (ddof=1), or the variance of
                an entire population.
        '''

        new_std = self.std(ddof=ddof)
        new_count = self.count()
        return new_std / np.sqrt(new_count)

    def _conf_int_mean(self, confidence):
        '''
        Compute the confidence interval of the mean at a given confidence level.
        The confidence level must be between 0 and 1 inclusive.

        Args
            confidence (float between 0 and 1): the confidence level at which
                the interval must be given.
        '''

        mask_scale_pos = self.sem() > 0
        df = self.count() - 1
        loc = self.mean()
        scale = self.sem()

        kwargs_for_t_interval = {
            'confidence': confidence,
            'df': df[mask_scale_pos],
            'loc': loc[mask_scale_pos],
            'scale': scale[mask_scale_pos],
        }

        lower_sub, upper_sub = scipy.stats.t.interval(**kwargs_for_t_interval)

        # Set up arrays of nan of the shape of scale
        lower = np.full(scale.shape, np.nan)
        upper = np.full(scale.shape, np.nan)
        # fill with actual values that we masked
        # Nans will only remain where scale <=0
        lower[mask_scale_pos] = lower_sub
        upper[mask_scale_pos] = upper_sub

        # return as a list of tuples
        return [(x, y) for x, y in zip(lower, upper)]

    def quantile(self, quantile):
        '''
        Compute the approximate quantile value for each of the KPIs in the dataset.
        This is based on the DDSketch method, an approximate quantile computation
        algorithm.

        Args
            quantile (float between 0 and 1): the quantile for which to return the value.
        '''

        return np.asarray(
            [
                # sketch is a DDSketch object
                sketch.get_quantile_value(quantile)
                for sketch in self._quantile_store
            ]
        )


# Fill the StatisticsRegistry

offline_stats = dict(inspect.getmembers(descriptivestats, inspect.isfunction))
online_methods = dict(inspect.getmembers(OnlineStatAnalyzer, inspect.isfunction))

# Loop over all offline stats to create StatisticsRegistry
# NOTE: This relies on all stats being offline available.
for stat in offline_stats.keys():
    if stat in ["covariance", "correlation", "mode"]:
        parameters = {"Results key": stat}
    else:
        parameters = {"Results key": "statistics"}
    # `Online available` key from online_methods and umbrella stats
    parameters['Online available'] = (
        stat in online_methods
        or stat in OnlineStatAnalyzer._umbrella_stats
        or stat in OnlineStatAnalyzer._no_function_stats
    )

    StatisticsRegistry.register(offline_stats[stat], name=stat, info=parameters)


def create_mapping_statkeys_df_keys():
    """
    Create mapping between keys in StatisticsRegistry and keys in output dataframe
    """

    # set up empty mapping
    mapping = {}

    # Exact stats (i.e. online & offline results are exact)
    mapping.update(
        {
            k: [k]
            for k in [
                'count',
                'mean',
                'min',
                'max',
                'std',
                'sem',
            ]
        }
    )
    mapping.update(
        {
            'confidence_intervals_of_the_mean': [
                'confidence interval of the mean at 68%',
                'confidence interval of the mean at 95%',
                'confidence interval of the mean at 99%',
            ],
            'minmax': ['min', 'max'],
            'standard': [
                'mean',
                'std',
                'sem',
                'confidence interval of the mean at 95%',
            ],
        }
    )

    # Quantile based stats (online results are approximate)
    mapping.update({k: [k] for k in ['median']})
    mapping.update(
        {
            'quantiles': [f'quantile {q:.0f}%' for q in range(5, 100, 5)],
            'box_plot': ['mean', 'median', 'Q1', 'Q3', 'min', 'max'],
        }
    )
    # stats that are not implemented online
    mapping.update(
        {
            k: [k]
            for k in [
                'harmonic_mean',
                'geometric_mean',
                'kurtosis',
                'skewness',
            ]
        }
    )
    mapping.update(
        {
            'high_order': ['skewness', 'kurtosis'],
            'central': ['mean', 'geometric_mean', 'harmonic_mean'],
        }
    )

    return mapping


STAT_KEY_MAPPING = create_mapping_statkeys_df_keys()
