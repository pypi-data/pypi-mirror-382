# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import numpy as np
from scipy import stats
from ...utilities import get_logger
from ...utilities import utilities
from .distributionregistry import (
    DistributionRegistry,
)


class Distribution:
    """
    A class to create iid distributions.

    A Distribution object in CoMETS is a wrapper around a distribution defined by an external library (scipy.stats).
    The list of available distributions and their corresponding parameters are stored in the DistributionRegistry.
    It exposes a method `get_samples` that takes as argument a single integer and returns the corresponding number of samples randomly drawn from the distribution.
    The distribution parameters are stored in the attribute `parameters`.
    This attribute is optional at object creation, but it is required when wanting to call the `get_samples` method.
    If `parameters` is empty or does not contain the correct parameter names, a call to `get_samples` will return an error.
    It is possible to fit the distribution parameters according to data using the `fit` method.
    `fit` is a wrapper around the `fit` method of the underlying scipy distribution.

    A Distribution object handle iid distributions with optional input key 'size'.

    Args:
        variable (dict): a dictionary containing the following key:value pairs:

            * "name":str, defining the variable name
            * "sampling":str, defining the distribution name
            * "parameters":dict, (optional) defining the dictionary of parameters to pass to the distribution
            * "size":int, (optional) specifies how many iid copies of the variable to construct
    """

    def __init__(self, variable):
        # Get arguments and check values
        try:
            self.name = variable["name"]
        except KeyError:
            raise ValueError("A variable should have a name")
        try:
            self.distribution_name = variable["sampling"]
        except KeyError:
            raise ValueError(
                "Provide distribution name for variable {}".format(self.name)
            )
        # Parse parameters: default to None if not provided
        self.parameters = variable.get("parameters", None)

        utilities.check_size(variable)

        if 'size' in variable:
            self.size = variable['size']
            self.dimension = self.size
        else:
            self.size = None
            self.dimension = 1

        # Construct the distribution from the registry
        try:
            self._scipy_dist = DistributionRegistry[self.distribution_name]
        except KeyError:
            raise ValueError("Unknown distribution: {}".format(self.distribution_name))

        self._discrete = False
        # Set _discrete to True for discrete distributions
        self._set_discrete()

    def _set_discrete(self):
        if (
            DistributionRegistry.information[self.distribution_name]["Type"]
            == "Discrete1D"
        ):
            self._discrete = True

    def to_dict(self):
        """Returns the Distribution in the dictionary format required by CoMETS.

        Example::

            >>> Distribution({"name": 'Demand',"sampling": "normal","size": 2}).to_dict()
            {'name': 'Demand', 'sampling': 'normal', 'size': 2}

        Returns:
            dict: a dictionary that can be passed as an argument 'sampling' in a CoMETS experiment.
        """
        out = {
            "name": self.name,
            "sampling": self.distribution_name,
        }
        if self.parameters is not None:
            out["parameters"] = self.parameters
        if self.size is not None:
            out["size"] = self.size
        return out

    def get_samples(self, number_of_samples, random_state=None):
        """Get random variate samples of the distribution

        Args:
            number_of_samples (int): number of samples to draw
            random_state (optional): Random state object. Defaults to None.

        Returns:
            numpy array: array of shape (dimension, number_of_samples), where 'dimension' represents the number of iid distributions requested
        """
        try:
            return self._scipy_dist.rvs(
                **self.parameters,
                size=self.dimension * number_of_samples,
                random_state=random_state,
            ).reshape((self.dimension, number_of_samples))
        except TypeError as e:
            if self.parameters is None:
                raise TypeError(
                    "Parameters attribute of Distribution {} is empty. Parameters are required to be able to sample from it.".format(
                        self.to_dict()
                    )
                )
            else:
                logger = get_logger(__name__)
                logger.error(
                    "Distribution parameters are incorrect: {}".format(self.to_dict())
                )
                raise e

    def ppf(self, usamples):
        """Percent point function (inverse of cdf) of the given distribution.

        Takes samples from the unit hypercube of dimension 'size', transform them into samples of the distribution.
        The transformation is called independently on each line (iid hypothesis).

        Args:
            usamples (numpy array): Samples in the unit hypercube, with shape (size, number_of_samples)

        Returns:
            numpy array: array of shape (size, number_of_samples), where size represents the number of iid distributions requested
        """
        size, number_of_samples = usamples.shape
        # Transformed samples for current distribution
        tsamples = np.empty((size, number_of_samples))
        for j in range(size):
            tsamples[j, :] = self._scipy_dist.ppf(usamples[j, :], **self.parameters)
        # Cast to int for discrete type, because for some reason ppf returns floats
        if self._discrete:
            tsamples = tsamples.astype(int)
        return tsamples

    def _get_validated_parameters(self, parameters):
        if parameters is None:
            parameters = self.parameters
        # If not given, loc is 0 for discrete distributions
        if self._discrete and "loc" not in parameters:
            parameters["loc"] = 0
        try:
            _validated_parameters = [
                parameters[key]
                for key in DistributionRegistry.information[self.distribution_name][
                    "parameters"
                ]
            ]
            _validated_parameters = tuple(_validated_parameters)
        except TypeError:
            raise TypeError(
                "Cannot parse parameters of Distribution {}. Its parameters attribute is empty or invalid.".format(
                    self.to_dict()
                )
            )
        except KeyError:
            raise KeyError(
                "Unknown parameters in {} for distribution '{}'.".format(
                    parameters, self.distribution_name
                )
            )
        return _validated_parameters

    def pdf(self, data, parameters=None):
        """Probability density function of the Distribution.

        This method is only applicable for continuous distributions.

        Args:
            data (array_like): Locations to evaluate the probability density function.
            parameters (dict, optional): Dictionary specifying the parameters values of the Distribution probability density function.
                If None, the Distribution `parameters` attribute is used. Defaults to None.

        Returns:
            array_like: Probability density function evaluations.
        """
        validated_parameters = self._get_validated_parameters(parameters)
        # If data is a list, np.asarray is required for scipy version < 1.10. (Fixed in scipy for versions >= 1.10)
        if self._discrete:
            return self._scipy_dist.pmf(np.asarray(data), *validated_parameters)
        else:
            return self._scipy_dist.pdf(np.asarray(data), *validated_parameters)

    def loglikelihood(self, data, parameters=None):
        """Computes the log-likelihood function of the Distribution, given some data.

        .. math::

            \\mathrm{logL}( \\theta | x) = \\sum_{x_i} \\log ( \\mathrm{pdf}(x_i, \\theta)),

        with :math:`\\theta` representing the parameters of the distribution.

        Args:
            data (array_like): Data used to compute the log-likelihood function.
            parameters (dict, optional): Dictionary specifying the parameters values of the Distribution probability density function.
                If None, the Distribution `parameters` attribute is used. Defaults to None.

        Returns:
            float: log-likelihood value.
        """
        validated_parameters = self._get_validated_parameters(parameters)
        # If data is a list, np.asarray is required for scipy version < 1.10. (Fixed in scipy for versions >= 1.10)
        return -self._scipy_dist.nnlf(validated_parameters, np.asarray(data))

    def _aic(self, data, parameters=None):
        """Computes the Akaike information criterion (AIC) value of the distribution given some data.

        .. math::

            \\mathrm{AIC} = 2*k - 2 *\\mathrm{nlogL}(x, \\theta),

        with :math:`x` the data, :math:`\\theta` representing the parameters of the distribution and :math:`k` the number of parameters.

        Args:
            data (array_like): Data used to compute the AIC.
            parameters (dict, optional): Dictionary specifying the parameters values of the Distribution that maximize the likelihood function. If None, the Distribution `parameters` attribute is used.
                Defaults to None.

        Returns:
            float: AIC value.
        """
        validated_parameters = self._get_validated_parameters(parameters)
        k = len(validated_parameters)
        # If data is a list, np.asarray is required for scipy version < 1.10. (Fixed in scipy for versions <= 1.10)
        return 2 * self._scipy_dist.nnlf(validated_parameters, np.asarray(data)) + 2 * k

    def _bic(self, data, parameters=None):
        """Computes the Bayesian information criterion (BIC) value of the distribution given some data.

        .. math::

            \\mathrm{BIC} = \\log (n)*k - 2 *\\mathrm{nlogL}(x, \\theta),

        with :math:`x` the data, :math:`n` the number of observations (i.e. the length of :math:`x`), :math:`\\theta` the parameters of the distribution and :math:`k` the number of parameters.

        Args:
            data (array_like): Data used to compute the BIC.
            parameters (dict, optional): Dictionary specifying the parameters values of the Distribution that maximize the likelihood function.
                If None, the Distribution `parameters` attribute is used.
                Defaults to None.

        Returns:
            float: BIC value.
        """
        validated_parameters = self._get_validated_parameters(parameters)
        k, n = len(validated_parameters), len(data)
        # If data is a list, np.asarray is required for scipy version < 1.10. (Fixed in scipy for versions <= 1.10)
        return (
            2 * self._scipy_dist.nnlf(validated_parameters, np.asarray(data))
            + np.log(n) * k
        )

    def fit(self, data, *args, **kwds):
        """Fit the distribution parameters from given data.

        This method is only available for continuous distributions.

        It replaces all parameters defined in the 'parameters' argument with the one obtained during the calibration.

        Args:
            data (array_like): Data used to estimate distribution parameters.

            args: floats, optional.
                Can be any argument accepted by scipy.
        """
        data = np.asarray(data)

        if self._discrete:
            # Get method to fit the discrete distribution
            from . import _discrete_distribution_fitting

            _get_fit_args = getattr(
                _discrete_distribution_fitting, f"_{self.distribution_name}_fit_args"
            )

            bounds, guess = _get_fit_args(data)

            fit_results = stats.fit(self._scipy_dist, data, bounds=bounds, guess=guess)

            self.parameters = fit_results.params._asdict()

            # Convert some parameters to integers, as they are returned as floats
            if (
                self.distribution_name == "binomial"
                or self.distribution_name == "betabinom"
            ):
                self.parameters["n"] = int(self.parameters["n"])
            elif self.distribution_name == "hypergeom":
                self.parameters["n"] = int(self.parameters["n"])
                self.parameters["N"] = int(self.parameters["N"])
                self.parameters["M"] = int(self.parameters["M"])

        else:
            parameters = self._scipy_dist.fit(data, *args, **kwds)
            param_names = DistributionRegistry.information[self.distribution_name][
                "parameters"
            ]
            self.parameters = dict(zip(param_names, parameters))
