import numpy as np
from scipy import stats

from ..sampling.sampling import CustomSampling


class KDE(CustomSampling):
    """
    Samples from a Gaussian Kernel Density Estimator (KDE).

    KDE is an estimation of the underlying distribution, built by linear combinations of gaussian distributions centered around the data points.

    Args:
        data (array_like):
            Floating-point data used for estimating the KDE. In case of univariate data, this is a 1-D array,
            otherwise a 2-D array with shape (# of dims, # of data).
        lower_bound (list, optional): List of values with as many value as the number of dimensions, lower bound of the random variable:
            the distribution will be rectified so that the probability mass below this value is null.
        upper_bound (list, optional): List of values with as many value as the number of dimensions, upper bound of the random variable:
            the distribution will be rectified so that the probability mass below this value is null.

    Returns:
        List of samples with length number_of_samples. Each sample is a list of floats which size equals the number of dimensions.
    """

    def __init__(self, data, lower_bound=None, upper_bound=None):
        self._scipy_kde = stats.gaussian_kde(data, bw_method='scott')
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound

    @property
    def data(self):
        """Get the data used to create the KDE model in a 2D array format.

        Returns:
            array: 2-D array with shape (# of dims, # of data).
        """
        # _scipy_kde object always stores an "at_least_2d" array
        return self._scipy_kde.dataset

    def _serialize(self):
        res = {
            "class": self.__class__.__name__,
            "data": self.data.tolist(),
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
        }
        return res

    @classmethod
    def _deserialize(cls, sobj):
        return cls(
            sobj["data"],
            lower_bound=sobj["lower_bound"],
            upper_bound=sobj["upper_bound"],
        )

    def get_samples(self, number_of_samples):
        sample = self._scipy_kde.resample(number_of_samples).transpose()
        if self.lower_bound:
            sample = np.clip(
                sample,
                a_min=np.tile(self.lower_bound, (number_of_samples, 1)),
                a_max=None,
            )
        if self.upper_bound:
            sample = np.clip(
                sample,
                a_min=None,
                a_max=np.tile(self.upper_bound, (number_of_samples, 1)),
            )
        if sample.shape[1] > 1:
            return [list(s) for s in sample]
        else:
            return [s[0] for s in sample]

    def pdf(self, data):
        """Probability density function (pdf) of the KDE.

        Args:
            data (array_like): Locations to evaluate the probability density function.

        Returns:
            array: Probability density function evaluations.
        """
        return self._scipy_kde.evaluate(data)

    def loglikelihood(self, data):
        """Computes the log-likelihood function of the KDE, given some data.

        .. math::

            \\mathrm{logL}( \\theta | x)= \\sum_{x_i} \\log ( \\mathrm{pdf}(x_i, \\theta )),

        with :math:`\\theta` representing the parameters of the KDE.

        Args:
            data (array_like): Data used to compute the log-likelihood function.

        Returns:
            float: log-likelihood value.
        """
        return np.sum(self._scipy_kde.logpdf(data))

    def cdf(self, x):
        """Cumulative distribution function (cdf) of the KDE.

        Args:
            data (array_like): Locations to evaluate the cumulative distribution function.

        Returns:
            array: Cumulative distribution function evaluations.
        """
        func = np.vectorize(lambda x: self._scipy_kde.integrate_box_1d(-np.inf, x))
        return func(x)
