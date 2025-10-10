from scipy import stats

from .sampling import (
    Distribution,
    DistributionRegistry,
)


def _ks1_test(data, model):
    """One-sample Kolmogorov-Smirnov test.

    Test if the sample data is drawn from a population that follows a particular distribution.

    Args:
        data (array_like): Sample data used for the test.
        model (Distribution, Histogram or KDE): a CoMETS statistical model object.
    """
    if isinstance(model, Distribution):
        # Get scipy distribution
        obj = model._scipy_dist
        args = tuple(model.parameters.values())
    else:
        obj = model
        args = ()
    ks_test = stats.ks_1samp(
        data,
        obj.cdf,
        args=args,
        alternative='two-sided',
    )
    return {"statistic": ks_test.statistic, "p-value": ks_test.pvalue}


def _cv1_test(data, model):
    """One-sample Cramér-von Mises test.

    Test if the sample data is drawn from a population that follows a particular distribution.

    Args:
        data (array_like): Sample data used for the test.
        model (Distribution, Histogram or KDE): a CoMETS statistical model object.
    """
    # Get scipy distribution
    if isinstance(model, Distribution):
        # Get scipy distribution
        obj = DistributionRegistry[model.distribution_name]
        args = model.parameters.values()
    else:
        obj = model
        args = ()
    cv_test = stats.cramervonmises(data, obj.cdf, args=args)
    return {"statistic": cv_test.statistic, "p-value": cv_test.pvalue}
