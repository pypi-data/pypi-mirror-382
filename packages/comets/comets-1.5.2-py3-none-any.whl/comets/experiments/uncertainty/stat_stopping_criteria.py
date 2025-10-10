# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...utilities import get_logger


class StatsCallback:
    """
    StatsCallback class

    A customizable callback that can be used to provide multiple statistics-based stopping
    criteria to an Uncertainty Analysis experiment (for instance, to stop the experiment
    when the confidence interval of the mean at 95% for a certain task output parameter has
    shrunk to a certain threshold value). Works with both online and offline stats.

    Criteria can be added using the method .add().

    An instance of this class is a callable that returns True if *all* criteria defined
    within are True, and can thus be passed to an experiment as a stopping criterion
    callback.

    Note:
        This type of callback only makes sense for statistics that are (roughly)
        monotonically decreasing - in practice this means the standard error of the mean
        or a confidence interval of the mean.
    """

    def __init__(self) -> None:
        self.stats_callbacks = []

    def __call__(self, experiment):

        n_eval = experiment.number_of_evaluations
        if n_eval > 0:

            # retrieve the statistics dataframe
            if experiment.online_stats:
                stats = experiment.analyzer.compute_statistics(replace_nan_with=None)[
                    'statistics'
                ]
            else:  # pragma: no cover
                stats = experiment.analyzer.compute_statistics(
                    experiment.list_of_results
                )['statistics']
            results = [
                cb._check_condition(stats, experiment.number_of_evaluations)
                for cb in self.stats_callbacks
            ]

            return all(results)
        else:
            return False

    def __repr__(self):

        repr_text = [
            "StatsCallback object returning True if all of the following criteria hold:"
        ]
        repr_text += ['  -' + repr(cb).split('if')[-1] for cb in self.stats_callbacks]
        return '\n'.join(repr_text)

    def add(self, *args, **kwargs):
        '''
        Add a new stopping criterion to the StatsCallback instance.

        Note:
            If the statistic is a confidence interval of the mean (which is a
            tuple), the diff between the tuple values is taken.

        Args:
            *args: Arguments for SingleStatsCallback
            **kwargs: Keyword arguments for SingleStatsCallback
        '''

        self.stats_callbacks.append(SingleStatsCallback(*args, **kwargs))


class SingleStatsCallback:
    """
    SingleStatsCallback class

    A customizable callback that can be used to provide stopping criteria based on the
    computed statistics in an Uncertainty Analysis experiment. Works with both online
    and offline stats. Once defined, an instance of this class can be passed as a callback
    to StopCriteria.

    This class enables the user to easily stop the experiment when the (e.g.) confidence
    interval of the mean for a certain task output key has gone below the threshold value.

    Note:
        This type of callback only makes sense for statistics that are (roughly)
        monotonically decreasing - in practice this means the standard error of the mean
        or a confidence interval of the mean.


    Args:
        task_output_key (str): the key of the output ParameterSet of the Task on which the
            experiment is performed for which we set up this stopping criterion.
        statistic (str): statistic whose value should be checked to determine whether the
            experiment should stop. Statistic must be valid in the StatisticsRegistry, but
            must also be available in the experiment in which the callback is used.
            If the statistic is a confidence interval of the mean (which is a tuple),
            the diff between the tuple values is taken.
        threshold (float): threshold value below which the experiment should stop.
        threshold_relative_to_mean (bool): if set to `True`, the threshold value is interpreted
            as a fraction of the mean, in other words a relative stopping criterion. This
            requires the mean to be a stat declared in the analyzer along with ``statistic``.
            Here, "fraction of the mean" means that if ``threshold=0.1``, it is interpreted as
            10% of the mean.
        minimum_number_of_evaluations (int, default 100): minimum number of task
            evaluations that needs to be run before the stat-based stopping mechanism can
            be incited. This number ensures that at least some statistical stability has
            occurred, and should not be too low.
    """

    def __init__(
        self,
        task_output_key,
        statistic,
        threshold,
        threshold_relative_to_mean=False,
        minimum_number_of_evaluations=100,
    ):
        '''
        Set up the callback instance.
        '''
        self.task_output_key = task_output_key
        self.statistic = statistic
        self.threshold = threshold
        self.threshold_relative_to_mean = threshold_relative_to_mean
        self.minimum_number_of_evaluations = minimum_number_of_evaluations

    def __call__(self, experiment):

        '''
        Check whether the callback's condition holds.
        '''

        # start checking the stop criteria if there are more than 0 task evaluations
        n_eval = experiment.number_of_evaluations
        if n_eval > 0 and n_eval >= self.minimum_number_of_evaluations:
            # retrieve the statistics dataframe
            if experiment.online_stats:
                stats = experiment.analyzer.compute_statistics(replace_nan_with=None)[
                    'statistics'
                ]
            else:  # pragma: no cover
                stats = experiment.analyzer.compute_statistics(
                    experiment.list_of_results
                )['statistics']

            return self._check_condition(stats, experiment.number_of_evaluations)
        else:
            return False

    def __repr__(self):
        phrase = f"SingleStatCallback object returning True if (the width of) the {self.statistic} for {self.task_output_key} goes below {self.threshold}"
        if self.threshold_relative_to_mean:
            phrase += " times the mean"
        return phrase

    def _check_condition(self, stats, n_eval):

        '''
        Returns True if the value of `self.statistic` has met the `self.threshold` value for
        the task output key `self.task_output_key` (these values are set at initialisation).
        Returns False otherwise.

        Args:
            stats (pd.DataFrame): the statistics dataframe as output by an StatAnalyzer or
                OnlineStatAnalyzer.
            n_eval (int): the number of Task evaluations carried out in the experiment.
        '''

        logger = get_logger(__name__)

        if n_eval > self.minimum_number_of_evaluations:

            try:
                stat_value = stats.loc[self.task_output_key, self.statistic]
            except KeyError:
                raise ValueError(
                    f'The statistic with which the StatsCallback is defined, {self.statistic}, '
                    'is not available in this experiment\'s statistics analyzer.'
                )

            # calculate the diff if the returned stat is a tuple - a hacky way to get
            # the width of a confidence interval (which is the only tuple stat)
            if "confidence interval" in self.statistic and isinstance(
                stat_value, tuple
            ):
                stat_value = stat_value[1] - stat_value[0]
                extra_phrase = "the width of "
            else:
                extra_phrase = ""

            # Convert threshold to a value relative to the mean if required
            if self.threshold_relative_to_mean:
                try:
                    current_mean = stats.loc[self.task_output_key, 'mean']
                except KeyError as e:
                    raise ValueError(
                        f"No mean is provided in the stats, so a relative threshold cannot be computed. {str(e)}"
                    )
                threshold = self.threshold * current_mean
            else:
                threshold = self.threshold

            if stat_value < threshold:
                logger.debug(
                    f"After {n_eval} evaluations, "
                    f"{extra_phrase}{self.statistic} = {stat_value:.3f} for {self.task_output_key}"
                )
                return True
        return False
