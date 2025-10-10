import numpy as np
from ..sampling.sampling import CustomSampling


class EmpiricalSampler(CustomSampling):
    """
    Class used to generate samples directly drawn from a historical sample.

    The samples returned by the `get_samples` method are all members of the input sample.

    Args:
        data (list of object):
            List of the historical observations of the random variable.

    Returns:

    """

    def __init__(self, data):
        self.values = data

    def _serialize(self):
        try:
            values = self.values.tolist()
        except AttributeError:
            values = self.values
        res = {
            "class": self.__class__.__name__,
            "values": values,
        }
        return res

    @classmethod
    def _deserialize(cls, sobj):
        return cls(sobj["values"])

    def get_samples(self, number_of_samples):
        """Generate samples directly drawn from the historical data.

        Args:
            number_of_samples (int): number of samples to draw.

        Returns:
            list: List of samples with length number_of_samples. Each sample is an element of the historical data.
        """
        return list(np.random.choice(self.values, size=number_of_samples))
