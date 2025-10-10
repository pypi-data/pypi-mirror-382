# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from abc import ABC, abstractmethod
from .distributions import Distribution, DistributionRegistry
from .generator import Generator
from . import SequenceRegistry
from . import GeneratorRegistry

import numpy as np


class BaseSampling(ABC):
    """
    Abstract class for sampling
    """

    def __init__(self):
        pass

    @abstractmethod
    def get_samples(self, number_of_samples):
        pass


class CustomSampling(BaseSampling):
    """
    Wrapper for custom generators.

    It freezes the arguments of the generator provided as input. Generated samples can be of any type and will be handled by the task encoder.

    Args:
        generator (callable): A callable object that takes as first argument an integer determining the number of samples and returns a list of the corresponding samples

    """

    def __init__(self, generator, *args, **kwargs):
        self._generator = generator
        self._args = args
        self._kwargs = kwargs

    def get_samples(self, number_of_samples):
        """
        Draw samples from the generator

        Args:
            number_of_samples (int)

        Returns:
            List of samples, with length number_of_samples
        """
        return self._generator(number_of_samples, *self._args, **self._kwargs)


class DistributionSampling(BaseSampling):
    """
    A class to group and sample the variables defined with distributions

    Args:
        variables (list): list of random variables (list of dictionaries) following some distributions.
    """

    def __init__(self, variables, rule="random"):
        # Parse variables as a list of Distribution objects
        self.distributions = [Distribution(variable) for variable in variables]
        self.dimension = None
        self._set_dimension()  # Automatically compute problem dimension
        if rule is None or rule == "random":
            # Default sampler is rvs
            self._rule = "random"
        else:
            self._rule = SequenceRegistry[rule]

    def get_samples(self, number_of_samples):
        """Draw samples assuming independently distributed variables

        Args:
            number_of_samples (int)

        Returns:
            List of ParameterSet, with length number_of_samples
        """
        samples = [{} for _ in range(number_of_samples)]

        if self._rule == "random":
            for dist in self.distributions:
                # Transpose to numpy array with line=number_of_samples, columns=dist.dimension
                samp = dist.get_samples(number_of_samples).T
                if dist.size is None:
                    for i in range(number_of_samples):
                        # Add sample to dictionary as scalar
                        samples[i][dist.name] = np.squeeze(samp[i, ...]).tolist()
                else:
                    for i in range(number_of_samples):
                        # Add sample to dictionary as list
                        samples[i][dist.name] = samp[i, ...].tolist()
        else:
            # Samples on unit hypercube, shape (dimension, number_of_samples)
            usamples = self._rule(number_of_samples, dim=self.dimension)
            # Column counter
            col = 0
            # For each Distribution object, for each of its dimension, transform with ppf
            for dist in self.distributions:
                # Transpose to get shape (number_of_samples, dimension)
                tsamples = dist.ppf(usamples[col : col + dist.dimension, :]).T
                col += dist.dimension
                # Now transform to CoMETS format
                if dist.size is None:
                    for i in range(number_of_samples):
                        # Add sample to dictionary as scalar
                        samples[i][dist.name] = np.squeeze(tsamples[i, ...]).tolist()
                else:
                    for i in range(number_of_samples):
                        # Add sample to dictionary as list
                        samples[i][dist.name] = tsamples[i, ...].tolist()
        return samples

    def get_parameters_names(self):
        return [dist.name for dist in self.distributions]

    def _set_dimension(self):
        self.dimension = 0
        for dist in self.distributions:
            self.dimension += dist.dimension


class CompositeSampling(BaseSampling):
    """
    CompositeSampling groups a list of samplers into one sampling interface.

    It can handle sampling from both distributions or custom generators.

    Args:
        variables (list): list of random variables or generators (list of dictionaries).
    """

    def __init__(self, variables, rule="random"):
        # Separate generators and distributions:

        # Generators are saved as a list of variables (list of dictionaries):
        # the CustomSampling object is stored under the dictionary key "sampling" and accessed with generator["sampling"].
        # If size is not None, generator["sampling"] is a list containing copies of the original CustomSampling object.
        self._generators = []

        # Distributions are stored in a DistributionSampler object.
        # We build a temporary list 'distributions' to separate them from custom generators.
        distributions = []

        for variable in variables:
            if "name" not in variable.keys():
                raise ValueError("A variable should have a name")

            if "sampling" not in variable.keys():
                raise ValueError(
                    'Variable {} should define a distribution or a custom generator using key "sampling"'.format(
                        variable["name"]
                    )
                )
            # For custom generators, we might have directly a CustomSampling object as value
            if isinstance(variable["sampling"], CustomSampling):
                self._generators.append(Generator(variable))
            # Else, we look in the different registries
            elif isinstance(variable["sampling"], str):
                if variable["sampling"] in GeneratorRegistry.keys():
                    self._generators.append(Generator(variable))
                elif variable["sampling"] in DistributionRegistry.keys():
                    distributions.append(variable)
                else:
                    raise ValueError(
                        "Unknown generator or distribution {}".format(
                            variable["sampling"]
                        )
                    )
            else:
                raise ValueError(
                    "In variable {}, generator does not have a valid format".format(
                        variable["name"]
                    )
                )

        # Construct DistributionSampler:
        if len(distributions) == 0:
            self._distribution_sampler = None
        else:
            self._distribution_sampler = DistributionSampling(distributions, rule=rule)
        # Set generators as None if list is empty, to match with _distribution_sampler
        if len(self._generators) == 0:
            self._generators = None

        self.dimension = None
        self._set_dimension()  # Automatically compute problem dimension

        # Generate the correct get_samples method depending on inputs
        self._get_samples = self._define_get_samples()

    def get_samples(self, number_of_samples):
        """Draw samples assuming independent generators / distributions in each dimension

        Args:
            number_of_samples (int)

        Returns:
            List of ParameterSet, with length number_of_samples
        """
        return self._get_samples(number_of_samples)

    def _distributions_get_samples(self, number_of_samples):
        return self._distribution_sampler.get_samples(number_of_samples)

    def _generators_get_samples(self, number_of_samples):
        samples = [{} for _ in range(number_of_samples)]
        # To sample from a generator, we need its get_sample method
        # The calling object is stored under key generator["sampling"]
        for generator in self._generators:
            if generator.size is None:
                list_of_samples = generator.generators.get_samples(number_of_samples)
                # Now transform to CoMETS format
                for i, sample in enumerate(samples):
                    sample[generator.name] = list_of_samples[i]
            else:
                for sample in samples:
                    sample[generator.name] = []
                for obj in generator.generators:
                    list_of_samples = obj.get_samples(number_of_samples)
                    # Now transform to CoMETS format
                    for i, sample in enumerate(samples):
                        sample[generator.name].append(list_of_samples[i])
        return samples

    def _general_get_samples(self, number_of_samples):
        distrib_samples = self._distributions_get_samples(number_of_samples)
        generator_samples = self._generators_get_samples(number_of_samples)
        for i in range(number_of_samples):
            generator_samples[i].update(distrib_samples[i])
        return generator_samples

    def _define_get_samples(self):
        if self._generators is None:
            return self._distributions_get_samples
        elif self._distribution_sampler is None:
            return self._generators_get_samples
        else:
            return self._general_get_samples

    def _set_dimension(self):
        if self._distribution_sampler is None:
            self.dimension = 0
        else:
            self.dimension = self._distribution_sampler.dimension
        if self._generators is not None:
            for generator in self._generators:
                self.dimension += generator.dimension


class ARTimeSeriesSampler(CustomSampling):
    """
    Autoregressive Time Series Sampler.
    Generates samples of time series that are correlated in time.
    The value of the serie over time y(t) are generated from the formula y(t) = correlation * y(t-1) + epsilon(t),
    where epsilon(t) is a random variable with provided distribution (and parameters),
    and y(0) is drawn from a (possibly different) initial distribution


    Args:
            distribution (string): probability distribution for epsilon
            parameters (dict): parameters of the distribution
            init_distribution (string): probability distribution for y(0)
            init_distribution_parameters (dict): parameters of the init distribution
            dimension (int): length of each generated serie
            burnin (int): samples are taken after removing burn in time steps to remove the impact of the initial value y(0)
    """

    def __init__(
        self,
        distribution,
        parameters,
        dimension,
        correlation,
        burnin=0,
        init_distribution=None,
        init_distribution_parameters=None,
    ):
        variable = {
            "name": "Distribution",
            "sampling": distribution,
            "parameters": parameters,
            "size": dimension + burnin - 1,
        }
        if init_distribution is None:
            init_distribution = distribution
            init_distribution_parameters = parameters
        init_variable = {
            "name": "InitDistribution",
            "sampling": init_distribution,
            "parameters": init_distribution_parameters,
            "size": 1,
        }
        self.distribution = Distribution(variable)
        self.init_distribution = Distribution(init_variable)
        self.dimension = dimension
        self.burnin = burnin
        self.correlation = correlation

    def _generate_sample(self):
        """
        Generate one sample time serie

        Returns:
            List of floats with length self.dimension.
        """
        serie = np.zeros(self.burnin + self.dimension)

        # Get initial sample for epsilon(0)
        y = self.init_distribution.get_samples(1)[:, 0][0]
        serie[0] = y

        # Generate samples after burnin period
        epsilon = self.distribution.get_samples(1)[:, 0]
        for i in range(1, self.burnin + self.dimension):
            y = self.correlation * y + epsilon[i - 1]
            serie[i] = y

        return serie[self.burnin : self.burnin + self.dimension]

    def get_samples(self, number_of_samples):
        """
        Draw samples from the generator

        Args:
            number_of_samples (int)

        Returns:
            List of samples with length number_of_samples. Each sample is a list of float of size self.dimension.
        """
        samples = [list(self._generate_sample()) for i in range(number_of_samples)]
        return samples


class TimeSeriesSampler(CustomSampling):
    """
    Autoregressive Time Series Sampler. Generate samples of time series that follow a mean trend with a given uncertainty (std) and are correlated in time

    Args:
            correlation (float): Amount of autocorrelation at lag 1 of the generated time series.
                Between 0 and 1, 0 corresponding to uncorrelated values, and 1 to fully correlated values. Significant changes are mostly observed in the range 0.8-1.0.
            dimension (int): Length of the time series
            forecast (list of float): At each time step,
                the average over generated time series will be equal to the forecast for this time step.
                Defaults to None, in which case the average will be 0. Should have length equal to dimension.
            uncertainties (list of float): At each time step, the standard deviation over generated time series will be equal to "uncertainties" for this time step.
                Defaults to None, in which case the standard deviation will be 1. Should have length equal to dimension.
            minimum (float or list of float): Generated time series will be clipped to min if the values fall below min. Can be a number, or a list of numbers of size dimension.
            maximum (float or list of float): Generated time series will be clipped to max if the values rise above max. Can be a number, or a list of numbers of size dimension.
    """

    def __init__(
        self,
        correlation=0,
        dimension=10,
        forecast=None,
        uncertainties=None,
        minimum=None,
        maximum=None,
    ):
        self.std = 1
        self.correlation = correlation
        self.dimension = dimension
        if minimum is not None:
            self.minimum = np.array(minimum)
            if self.minimum.size != dimension and self.minimum.size != 1:
                raise ValueError(
                    "Minimum should be a scalar or have the same length as dimension"
                )
        else:
            self.minimum = minimum
        if maximum is not None:
            self.maximum = np.array(maximum)
            if self.maximum.size != dimension and self.maximum.size != 1:
                raise ValueError(
                    "Maximum should be a scalar or have the same length as dimension"
                )
        else:
            self.maximum = maximum
        if forecast is not None:
            self.has_forecast = True
            self.forecast = np.array(forecast)
            if len(self.forecast) != dimension:
                raise ValueError(
                    "Forecast should have the same length as dimension if it is provided"
                )
        else:
            self.has_forecast = False
            self.forecast = np.array([])
        if uncertainties is not None:
            self.has_uncertainties = True
            self.uncertainties = np.array(uncertainties)
            if len(self.uncertainties) != dimension:
                raise ValueError(
                    "Uncertainties should have the same length as dimension if it is provided"
                )
        else:
            self.has_uncertainties = False
            self.uncertainties = np.array([])
        if self.correlation < 0 or self.correlation > 1:
            raise ValueError(
                f"Correlation is {self.correlation} but should be between 0 and 1"
            )
        self.sigma = np.sqrt(1 - self.correlation**2) * self.std
        self.sampler = ARTimeSeriesSampler(
            distribution="normal",
            parameters={"loc": 0, "scale": self.sigma},
            init_distribution="normal",
            init_distribution_parameters={"loc": 0, "scale": 1},
            correlation=self.correlation,
            dimension=self.dimension,
        )

    def _clip_sample(self, serie):
        if self.minimum is None and self.maximum is None:
            return serie
        else:
            return np.clip(serie, self.minimum, self.maximum)

    def _map_to_forecast_and_uncertainties(self, serie):
        if self.has_uncertainties and self.has_forecast:
            return self._clip_sample(self.forecast + serie * self.uncertainties)
        elif self.has_forecast:
            return self._clip_sample(self.forecast + serie)
        elif self.has_uncertainties:
            return self._clip_sample(serie * self.uncertainties)
        else:
            return self._clip_sample(serie)

    def get_samples(self, number_of_samples):
        """
        Draw samples from the generator

        Args:
            number_of_samples (int)

        Returns:
            List of samples with length number_of_samples. Each sample is a list of float of size self.dimension.
        """
        samples = self.sampler.get_samples(number_of_samples)
        newsamples = []
        for sample in samples:
            shifted_sample = list(self._map_to_forecast_and_uncertainties(sample))
            newsamples.append(shifted_sample)
        return newsamples
