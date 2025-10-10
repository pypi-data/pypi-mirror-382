# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.


import importlib
import numpy as np
from functools import reduce

from .sensitivityanalyzer import (
    BaseSensitivityAnalyzer,
    SensitivityAnalyzerRegistry,
)
from ...statistical_tools.sampling import DistributionSampling

try:
    from SALib.sample import fast_sampler, latin
    from SALib.sample import morris as morris_sampler
    from SALib.sample import ff as ff_sampler
    from SALib.analyze import sobol, fast, rbd_fast, morris, ff

    sobol_spec = importlib.util.find_spec('.sobol', package='SALib.sample')
    if sobol_spec is None:  # pragma: no cover
        from SALib.sample import saltelli as sobol_sampler
    else:
        from SALib.sample import sobol as sobol_sampler
except ImportError:  # pragma: no cover
    SALIB_AVAILABLE = False
else:
    SALIB_AVAILABLE = True

from ...utilities.registry import partialclass
from ...utilities import get_logger
from ...utilities.utilities import next_power_of_2, filter_method_optional_arguments

# Default number of trajectories in Morris (will be multiplied by the number of dimensions)
DEFAULT_MORRIS_N_TRAJECTORIES = 10
# Default values for parameter N in variance-based methods
DEFAULT_SOBOL_N = 128
DEFAULT_FAST_N = 100
DEFAULT_RBDFAST_N = 1000  # For RDB-FAST, N is the total number of evaluations

if SALIB_AVAILABLE:
    SALIB_METHODS = {
        "Sobol": {
            "sampler": sobol_sampler.sample,
            "analyzer": sobol.analyze,
            "default_N": DEFAULT_SOBOL_N,
        },
        "FAST": {
            "sampler": fast_sampler.sample,
            "analyzer": fast.analyze,
            "default_N": DEFAULT_FAST_N,
        },
        "RBD-FAST": {
            "sampler": latin.sample,
            "analyzer": rbd_fast.analyze,
            "default_N": DEFAULT_RBDFAST_N,
        },
        "Morris": {
            "sampler": morris_sampler.sample,
            "analyzer": morris.analyze,
            "default_N": DEFAULT_MORRIS_N_TRAJECTORIES,
        },
        "Fractional Factorial": {
            "sampler": ff_sampler.sample,
            "analyzer": ff.analyze,
            "default_N": None,
        },
    }
else:  # pragma: no cover
    SALIB_METHODS = ["Sobol", "FAST", "RBD-FAST", "Morris", "Fractional Factorial"]

SUPPORTS_GROUPS = ["Sobol", "Morris"]

REQUIRES_BOUNDED_DISTRIBUTIONS = ["Morris", "Fractional Factorial"]

BOUNDED_DISTRIBUTIONS = [
    "arcsine",
    "beta",
    "cosine",
    "powerlaw",
    "trapezoid",
    "triangular",
    "truncnorm",
    "uniform",
    "vonmises",
    "discreteuniform",
]

VARIABLE_TYPES = [
    'float',
    'int',
]


class SALib(BaseSensitivityAnalyzer):
    """
    SALib sensitivity analyzer
    """

    def __init__(  # noqa: C901
        self,
        variables,
        method='FAST',
        method_arguments={},
    ):
        if not SALIB_AVAILABLE:  # pragma: no cover
            raise ImportError(
                f"This method ({method}) is only available with optional dependency SALib. Either install CoMETS with:\n"
                f"  - `pip install comets[gsa]`, \n"
                f"  - `pip install comets[all]`,\n"
                f"  - or install SALib with `pip install salib`."
            )

        logger = get_logger(__name__)

        # Check all variables and put them into the same format using distributions
        variables_sampling_format = variables.copy()
        for variable in variables_sampling_format:
            if "bounds" in variable:
                if 'type' not in variable:
                    raise ValueError(
                        "Variable {} should have a type".format(variable["name"])
                    )
                if variable["type"] == "int":
                    variable["sampling"] = "discreteuniform"
                    variable["parameters"] = {
                        "low": variable["bounds"][0],
                        "high": variable["bounds"][1] + 1,
                    }
                elif variable["type"] == "float":
                    variable["sampling"] = "uniform"
                    variable["parameters"] = {
                        "loc": variable["bounds"][0],
                        "scale": variable["bounds"][1] - variable["bounds"][0],
                    }
                else:
                    raise ValueError(
                        "Type of variable {} should be in {}".format(
                            variable["name"], VARIABLE_TYPES
                        )
                    )
        # Check that sampling method allows unbounded distributions; if some are present
        if SensitivityAnalyzerRegistry.information[method][
            'RequiresBoundedDistributions'
        ]:
            for variable in variables_sampling_format:
                if variable["sampling"] not in BOUNDED_DISTRIBUTIONS:
                    raise ValueError(
                        "Algorithm {} can sample only from bounded distributions. Cannot use {} distribution for variable {}".format(
                            method, variable["sampling"], variable["name"]
                        )
                    )
        self.distributions = DistributionSampling(variables_sampling_format)
        # Test if input variables have groups
        self.has_groups = False
        for variable in variables:
            if "group" in variable:
                self.has_groups = True
                break
        # Build parameter and group names
        self.parameter_names = []
        self.groups = []
        for variable in variables:
            if "size" in variable:
                for i in range(variable["size"]):
                    name = "{key}.{index}".format(key=variable["name"], index=i)
                    self.parameter_names.append(name)
                    if self.has_groups:
                        self.groups.append(variable.get("group", name))
            else:
                self.parameter_names.append(variable["name"])
                if self.has_groups:
                    self.groups.append(variable.get("group", variable["name"]))

        # Create a mock SALib problem to sample on the unit hypercube
        self.problem = {
            "num_vars": self.distributions.dimension,
            "names": self.parameter_names,
            "bounds": [[0, 1] for _ in range(self.distributions.dimension)],
        }
        if self.has_groups:
            if SensitivityAnalyzerRegistry.information[method]['SupportsGroups']:
                self.problem["groups"] = self.groups
            else:
                logger.warning(
                    "Global Sensitivity analysis method {} does not support groups, they will not be considered".format(
                        method
                    )
                )
                self.has_groups = False

        # Construct the algorithm with its arguments
        self.method = method

        if "N" in method_arguments:
            self.N = method_arguments["N"]
        else:
            # Default value
            self.N = SALIB_METHODS[method]["default_N"]

        # Set number of evaluations to the next power of 2 for Sobol method
        if method == "Sobol":
            N = next_power_of_2(self.N)
            # Check if N is a power of 2. If not, replace it by the next power of 2.
            if N != self.N:
                self.N = N
                logger = get_logger(__name__)
                logger.warning(
                    "Number of samples in the Sobol sequence should be a power of 2, argument N is set to {}".format(
                        N
                    )
                )

        # a) sampling method
        self.sampler = self._build_sampler(self.method)

        # Get sampler options
        self.sampler_options = filter_method_optional_arguments(
            self.sampler, method_arguments
        )
        logger.debug(
            "Pass the following options to {} sample function: {}".format(
                method, self.sampler_options
            )
        )

        # b) analyzer
        self.analyzermethod = SALIB_METHODS[method]["analyzer"]
        self.analyzer_options = filter_method_optional_arguments(
            self.analyzermethod, method_arguments
        )
        logger.debug(
            "Pass the following options to {} analyze function: {}".format(
                method, self.analyzer_options
            )
        )

        self.expected_number_of_evaluations = self._compute_number_of_evaluations()

    def _build_sampler(self, method):
        if method == "Fractional Factorial":

            def func(problem, _):
                return SALIB_METHODS[method]["sampler"](problem)

            return func
        else:
            return SALIB_METHODS[method]["sampler"]

    def _compute_number_of_evaluations(self):
        # Problem dimension depends on groups
        if self.has_groups:
            dim = len(set(self.groups))
        else:
            dim = self.distributions.dimension
        # Compute expected evaluations, following Salib doc
        if self.method == "Sobol":
            if not self.sampler_options.get("calc_second_order", True):
                return self.N * (dim + 2)
            else:
                return self.N * (2 * dim + 2)
        elif self.method == "FAST":
            return self.N * dim
        elif self.method == "RBD-FAST":
            return self.N
        elif self.method == "Morris":
            if 'optimal_trajectories' in self.sampler_options:
                return self.sampler_options["optimal_trajectories"] * (dim + 1)
            else:
                return self.N * (dim + 1)
        elif self.method == "Fractional Factorial":
            return 2 * next_power_of_2(dim)
        # This should never happen:
        else:  # pragma: no cover
            return None

    def get_samples(self, number_of_samples):
        self.X = self.sampler(
            self.problem, number_of_samples, **self.sampler_options
        )  # Storing samples for some analysis methods
        # Compute ppf:
        first_col = 0
        for dist in self.distributions.distributions:
            self.X[:, first_col : first_col + dist.dimension] = dist.ppf(
                self.X[:, first_col : first_col + dist.dimension]
            )
            first_col += dist.dimension
        return self.decoder(self.X)

    def sensitivity_analysis(self, list_of_results):
        results = {}
        if self.has_groups:
            # Remove duplicates in list of names, keeping same order
            output_names = list(dict.fromkeys(self.groups))
        else:
            output_names = self.parameter_names
        for kpi_num, kpi in enumerate(list(list_of_results[0].keys())):
            # Transform results from a list of dictionaries into an array
            Y = np.array([list(i.values())[kpi_num] for i in list_of_results])
            if self.method == 'RBD-FAST':
                Si = self.analyzermethod(
                    self.problem, self.X, Y, **self.analyzer_options
                )
                results[kpi] = {
                    "Sobol main effects": dict(zip(output_names, Si["S1"])),
                    "Sobol main effects confidence width": dict(
                        zip(output_names, Si["S1_conf"])
                    ),
                }
            elif self.method == 'Morris':
                Si = self.analyzermethod(
                    self.problem, self.X, Y, **self.analyzer_options
                )
                results[kpi] = {
                    "mu": dict(zip(output_names, Si["mu"])),
                    "mu_star": dict(zip(output_names, Si["mu_star"])),
                    "sigma": dict(zip(output_names, Si["sigma"])),
                    "mu_star confidence width": dict(
                        zip(output_names, Si["mu_star_conf"])
                    ),
                }
            elif self.method == "Fractional Factorial":
                Si = self.analyzermethod(
                    self.problem, self.X, Y, **self.analyzer_options
                )
                results[kpi] = {
                    "Main effects": dict(zip(output_names, Si["ME"])),
                }
            else:
                Si = self.analyzermethod(self.problem, Y, **self.analyzer_options)
                results[kpi] = {
                    "Sobol main effects": dict(zip(output_names, Si["S1"])),
                    "Sobol total effects": dict(zip(output_names, Si["ST"])),
                    "Sobol main effects confidence width": dict(
                        zip(output_names, Si["S1_conf"])
                    ),
                    "Sobol total effects confidence width": dict(
                        zip(output_names, Si["ST_conf"])
                    ),
                }
        return results

    def decoder(self, samples):
        # Change format to construct a list of dict of the form {'name of param1' : value1, 'name of param2' : value2}
        sample_inputs = []
        first_col = 0
        for dist in self.distributions.distributions:
            array = samples[:, first_col : first_col + dist.dimension]
            first_col += dist.dimension
            array = array.tolist()
            if dist.size is None:
                sample_inputs.append(
                    [dict(zip([dist.name], element)) for element in array]
                )
            else:
                sample_inputs.append(
                    [dict(zip([dist.name], [element])) for element in array]
                )
        parameterset = [reduce(lambda a, b: {**a, **b}, k) for k in zip(*sample_inputs)]
        return parameterset


# Register different SALib methods
for method_name in SALIB_METHODS:
    SensitivityAnalyzerRegistry[method_name] = partialclass(SALib, method=method_name)
    SensitivityAnalyzerRegistry.information.setdefault(method_name, {})[
        'SupportsGroups'
    ] = (method_name in SUPPORTS_GROUPS)
    SensitivityAnalyzerRegistry.information[method_name][
        'RequiresBoundedDistributions'
    ] = (method_name in REQUIRES_BOUNDED_DISTRIBUTIONS)
