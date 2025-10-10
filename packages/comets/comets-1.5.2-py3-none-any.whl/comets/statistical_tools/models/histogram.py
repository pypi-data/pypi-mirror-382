import numpy as np
from scipy import stats
from ..sampling.sampling import CustomSampling


class Histogram(CustomSampling):
    """
    Build a histogram on the basis of a historical sample.

    Can be either built from data (using `data`, `lower_bound` and `upper_bound` arguments),
    or by directly providing the histogram bin values and edges (using `histogram` argument).

    Args:
        data (array-like floats or integers, optional): Historical observations. Default to None.
        lower_bound (float or int, optional): Lower bound of the random variable.
            Used only if the Histogram is build from `data` argument. Default is min(data).
        upper_bound (float or int, optional): Upper bound of the random variable.
            Used only if the Histogram is build from `data` argument. Default is max(data).
        histogram (tuple of two array_like, optional): Contains the bin values and the bin edges.
            Bin edges should have length equal to len-bin_values) + 1. Default to None.
        type (str): Type of the generated samples, should be either "float" or "int". Default to "float".
    """

    def __init__(
        self,
        data=None,
        lower_bound=None,
        upper_bound=None,
        histogram=None,
        type="float",
    ):
        if histogram is None and data is None:
            raise ValueError(
                "Cannot create Histogram: either 'data' or 'histogram' argument should be provided."
            )

        if type not in ["float", "int"]:
            raise ValueError("\"type\" argument should be either \"float\" or \"int\"")
        else:
            self.type = type

        # Construct from histogram
        if histogram is not None:
            self._scipy_histogram = stats.rv_histogram(histogram)
            self.lower_bound = min(histogram[1])
            self.upper_bound = max(histogram[1])

        # Construct from data
        else:
            if lower_bound is None:
                self.lower_bound = min(data)
            else:
                self.lower_bound = lower_bound
            if upper_bound is None:
                self.upper_bound = max(data)
            else:
                self.upper_bound = upper_bound

            # Build the histogram
            if type == "float":
                self._scipy_histogram = stats.rv_histogram(
                    np.histogram(
                        data, bins='auto', range=(self.lower_bound, self.upper_bound)
                    )
                )
            else:
                bin_edges = np.histogram_bin_edges(data, bins="auto")
                bin_width = max(1, round(bin_edges[1] - bin_edges[0]))
                self.lower_bound = round(self.lower_bound)
                self.upper_bound = round(self.upper_bound)
                bins = (
                    np.arange(
                        self.lower_bound, self.upper_bound + 1 + bin_width, bin_width
                    )
                    - 0.5
                )
                self._scipy_histogram = stats.rv_histogram(
                    np.histogram(data, bins=bins)
                )

    @property
    def parameters(self):
        """
        Get the bin values and bin edges of the histogram.

        If the Histogram has been constructed from data, its format is identical
        to the output of NumPy `histogram` function.

        If the Histogram has been constructed from user-defined bins, the original
        format is preserved.

        Returns:
            (tuple): (bin_values, bin_edges)
                bin_values (array_like): The values of the histogram in each bin.
                bin_edges (array_like of floats): The bin edges, with length len(bin_values)+1.
        """
        return self._scipy_histogram._histogram

    def _serialize(self):
        try:  # Convert to a list if this is a numpy array
            bin_values = self.parameters[0].tolist()
        except AttributeError:
            bin_values = self.parameters[0]
        try:
            bin_edges = self.parameters[1].tolist()
        except AttributeError:
            bin_edges = self.parameters[1]

        res = {
            "class": self.__class__.__name__,
            "bin_values": bin_values,
            "bin_edges": bin_edges,
            "data_type": self.type,
        }
        return res

    @classmethod
    def _deserialize(cls, sobj):
        return cls(
            histogram=(sobj["bin_values"], sobj["bin_edges"]), type=sobj["data_type"]
        )

    def get_samples(self, number_of_samples):
        """Generate samples directly drawn from the histogram

        Args:
            number_of_samples (int): number of samples to draw

        Returns:
            list: List of samples with length number_of_samples.
        """
        sample = self._scipy_histogram.rvs(size=number_of_samples)
        if self.type == "int":
            sample = np.around(sample).astype(int)

        return list(sample)

    def pdf(self, data):
        """Probability density function (pdf) of the Histogram.

        For locations at bin edges, the pdf of the element is the value of the bin on its right.
        For the upper bound bin edge, the pdf is the value of the last bin.

        Args:
            data (array_like): Locations to evaluate the probability density function.

        Returns:
            array_like: Probability density function evaluations.
        """
        data = np.asarray(data)

        # If data is array_like
        pdf_res = self._scipy_histogram.pdf(data)

        if (data == self.upper_bound).any():
            # Scalar case
            if data.shape == ():
                return self._scipy_histogram._hpdf[-2]
            # array_like case
            pdf_res[
                np.argwhere(data == self.upper_bound)
            ] = self._scipy_histogram._hpdf[-2]

        return pdf_res

    def cdf(self, data):
        """Cumulative distribution function (cdf) of the Histogram.

        Args:
            data (array_like): Locations to evaluate the cumulative distribution function.

        Returns:
            array: Cumulative distribution function evaluations.
        """
        return self._scipy_histogram.cdf(data)

    def loglikelihood(self, data):
        """Computes the log-likelihood function of the Histogram, given some data.

        .. math::

            \\mathrm{logL}( \\theta | x)= \\sum_{x_i} \\log ( \\mathrm{pdf}(x_i, \\theta )),

        with :math:`\\theta` representing the parameters of the histogram.

        Args:
            data (array_like): Data used to compute the log-likelihood function.

        Returns:
            float: log-likelihood value.
        """
        data = np.asarray(data)
        return np.sum(np.log(self.pdf(data)))

    def _aic(self, data):
        """Computes the Akaike information criterion (AIC) value of the histogram given some data.

        .. math::

            \\mathrm{AIC} = 2*k - 2 *\\mathrm{nlogL}(x, \\theta),

        with :math:`x` the data, :math:`\\theta` representing the parameters of the histogram and :math:`k` the number of parameters.

        :math:`k` is chosen as the number of non-empty bins, plus 3 for the bins width, lower bound and upper bound.

        Args:
            data (array_like): Data used to compute the AIC.
            parameters (dict, optional): Dictionary specifying the parameters values of the Distribution that maximize the likelihood function. If None, the Distribution `parameters` attribute is used.
                Defaults to None.

        Returns:
            float: AIC value.
        """
        k = np.count_nonzero(self._scipy_histogram._hpdf) + 3
        return -2 * self.loglikelihood(data) + 2 * k

    def _bic(self, data):
        """Computes the Bayesian information criterion (BIC) value of the distribution given some data.

        .. math::

            \\mathrm{BIC} = \\log (n)*k - 2 *\\mathrm{nlogL}(x, \\theta),

        with :math:`x` the data, :math:`n` the number of observations (i.e. the length of :math:`x`), :math:`\\theta` the parameters of the distribution and :math:`k` the number of parameters.

        :math:`k` is chosen as the number of non-empty bins, plus 3 for the bins width, lower bound and upper bound.

        Args:
            data (array_like): Data used to compute the BIC.
            parameters (dict, optional): Dictionary specifying the parameters values of the Distribution that maximize the likelihood function.
                If None, the Distribution `parameters` attribute is used.
                Defaults to None.

        Returns:
            float: BIC value.
        """
        k, n = np.count_nonzero(self._scipy_histogram._hpdf) + 3, len(data)
        return -2 * self.loglikelihood(data) + np.log(n) * k
