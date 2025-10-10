import warnings
import numpy as np
import pandas as pd
from pandas.api.types import is_integer_dtype, is_float_dtype
from itertools import product
from sklearn.model_selection import (
    KFold,
    LeaveOneOut,
    LeavePOut,
    ShuffleSplit,
    train_test_split,
)
from joblib import Parallel, delayed

from ..utilities import get_logger
from .sampling import (
    Distribution,
    DistributionRegistry,
    CompositeSampling,
)
from .models.histogram import Histogram
from .models.kde import KDE
from .models.empirical_sampler import EmpiricalSampler
from .goodness_of_fit_tests import _ks1_test, _cv1_test


CONTINUOUS_CANDIDATES = [
    "uniform",
    "normal",
    "exponential",
    "lognormal",
    "loguniform",
    "gamma",
    "weibull",
    "beta",
    "chi",
    "chi2",
    "gennorm",
    "gompertz",
    "laplace",
    "powerlaw",
    "triangular",
    "trapezoid",
    "truncnorm",
]


def get_default_candidate_distributions(type):
    """Get the default list of Distribution candidates used for selection functions.

    Args:
        type (str): Either "continuous" or "discrete".

    Returns:
        list of str: List of Distribution candidates.
    """
    # Handle 'type' argument
    if type == "continuous":
        candidates = CONTINUOUS_CANDIDATES.copy()
    elif type == "discrete":
        # Create list of candidate distributions
        candidates = [
            name
            for name in DistributionRegistry.information
            if DistributionRegistry.information[name]["Type"] == "Discrete1D"
        ]
    else:
        raise ValueError("'type' argument value {} is invalid.".format(type))

    return candidates


def _compute_goodness_of_fit_tests(validation_data, model_obj, model_name):
    logger = get_logger(__name__)
    try:
        ks_test = _ks1_test(validation_data, model_obj)
    except Exception as e:
        message = type(e).__name__ + ": " + str(e)
        logger.error(
            f"Could not compute ks-test for model '{model_name}' due to the following error:\n\t"
            + message
            + "\nResult is set to None."
        )
        ks_test = None
    try:
        cv_test = _cv1_test(validation_data, model_obj)
    except Exception as e:
        message = type(e).__name__ + ": " + str(e)
        logger.error(
            f"Could not compute cv-test for model '{model_name}' due to the following error:\n\t"
            + message
            + "\nResult is set to None."
        )
        cv_test = None
    return ks_test, cv_test


# Remove coverage, because cannot capture logs
def _check_goodness_of_fit_test(test_result, test_name):  # pragma: no cover
    logger = get_logger(__name__)
    if test_result is not None:
        if test_result['p-value'] < 0.05:
            logger.warning(
                f"Goodness-of-fit test {test_name} failed with following results:\n\t"
                f"{test_result}.\n The selected model may not fit your dataset.\n"
            )


def _fit_and_score(
    model_name,
    train_data,
    test_data,
    type="continuous",
    variable_name="name",
    raise_fit_error=False,
):
    """Fit the given statistical model to data and compute associated log-likelihood.

    Args:
        model_name (str): String describing which model to fit.
        train_data (array_like): Data used for fitting.
        test_data (array_like): Data used for log-likelihood evaluation.
        type (str, optional): Either "continuous" or "discrete. Defaults to "continuous".
        variable_name (str, optional): Name of the fitted variable.
            Defaults to "name".
        raise_fit_error (bool, optional): If True, raises an Error when a model fit fails. Use this, for example, for debugging purposes.
            If False, statistical models that cannot be fitted are ignored.
            Defaults to False.

    Returns:
        tuple: model_name, loglikelihood, model
            * model_name: Name of fitted model.
            * loglikelihood: loglikelihood value.
            * model: CoMETS object containing the fitted model, e.g. a `Distribution` or a `Histogram`.

    """
    sampling_dict = {"name": variable_name}

    logger = get_logger(__name__)
    if model_name == "histogram":
        hist_type = "int" if type == "discrete" else "float"
        # Fit histogram
        try:
            model = Histogram(train_data, type=hist_type)
            sampling_dict["sampling"] = model
        except Exception:
            logger.warning(
                "Calibration of Histogram returned an error. Histogram will be ignored."
            )
            if raise_fit_error:
                raise
            return (model_name, np.nan, None)
    elif model_name == "kde":
        # Fit KDE
        try:
            model = KDE(train_data)
            sampling_dict["sampling"] = model
        except Exception:
            logger.warning(
                "Calibration of KDE returned an error returned an error. KDE will be ignored."
            )
            if raise_fit_error:
                raise
            return (model_name, np.nan, None)
    else:
        sampling_dict["sampling"] = model_name
        model = Distribution(sampling_dict)
        try:
            # Fit Distribution parameters on data
            model.fit(train_data)
        except Exception:
            logger.warning(
                f"Calibration of Distribution {model_name} parameters returned an error. This Distribution will be ignored."
            )
            if raise_fit_error:
                raise
            return (model_name, np.nan, None)

    score = model.loglikelihood(test_data)

    return (model_name, score, model)


def _cross_validation_model_selection(
    data,
    candidates,
    cv=None,
    type="continuous",
    variable_name="name",
    raise_fit_error=False,
    n_jobs=1,
):
    """Performs a cross-validation and compute selection metrics.

    The computed metrics for each candidate model are the following:
        * Log-likelihood for each split: key "cv_loglikelihood"
        * The mean log-likelihood for all splits: key "mean_cv_loglikelihood"
        * The standard deviation of splits log-likelihoods: key "std_cv_loglikelihood"

    Args:
        data (array_like): Data used for the cross-validation.
        candidates (list of str, optional): List of candidate statistical models.
        cv (int or scikit-learn cross-validation generator, optional): Cross-validation scheme used.
            If an integer is given, it specifies the number of folds in the K-Fold cross-validation.
            Accepted scikit-learn cross-validation generators are KFold, LeaveOneOut, LeavePOut, ShuffleSplit.
            Defaults to None, in which case 5-Fold cross-validation is used.
        type (str, optional): Either "discrete" or "continuous", depending on the type of data generated by the statistical model.
            Defaults to "continuous".
        variable_name (str, optional): Name of the fitted variable.
            Defaults to "name".
        raise_fit_error (bool, optional): If True, raises an Error when a model fit fails. Use this, for example, for debugging purposes.
            If False, statistical models that cannot be fitted are ignored.
            Defaults to False.
        n_jobs (int, optional): Number of processes used during cross-validation.
            Defaults to 1.

    Returns:
        dict: Dictionary with the following structure:
            {<candidate name1>:{"cv_loglikelihood":array_like, "mean_cv_loglikelihood":float,
            "std_cv_loglikelihood":float}, <candidate name2>:...}
    """
    if cv is None:
        cv = KFold(n_splits=5)
    elif isinstance(cv, int):
        cv = KFold(cv)

    if not isinstance(cv, (KFold, LeaveOneOut, LeavePOut, ShuffleSplit)):
        raise ValueError("This CV method is not available in CoMETS")

    cv_results = Parallel(n_jobs=n_jobs, backend="loky")(
        delayed(_fit_and_score)(
            model,
            data[train],
            data[test],
            type=type,
            variable_name=variable_name,
            raise_fit_error=raise_fit_error,
        )
        for model, (train, test) in product(candidates, cv.split(data))
    )
    reformat_cv_results = {key: {"cv_loglikelihood": []} for key in candidates}
    for t in cv_results:
        reformat_cv_results[t[0]]["cv_loglikelihood"].append(t[1])
    for _, val in reformat_cv_results.items():
        val["cv_loglikelihood"] = np.asarray(val["cv_loglikelihood"])
        val["mean_cv_loglikelihood"] = np.mean(val["cv_loglikelihood"])
        val["std_cv_loglikelihood"] = np.std(val["cv_loglikelihood"])

    return reformat_cv_results


def _probability_density_selection(  # noqa: C901
    data,
    validation_data,
    method="AIC",
    cv=None,
    type="continuous",
    candidates=None,
    include_histogram=False,
    include_kde=False,
    goodness_of_fit_tests=True,
    variable_name="name",
    size=None,
    raise_fit_error=False,
    n_jobs=1,
):
    logger = get_logger(__name__)
    # Construct the list of candidates
    if candidates is None:
        candidates = get_default_candidate_distributions(type)
    if include_histogram and "histogram" not in candidates:
        candidates.append("histogram")
    if (
        include_kde
        and type != "discrete"
        and method in ["MLE", "CV"]
        and "kde" not in candidates
    ):
        candidates.append("kde")

    # Get method
    if method == "CV":
        cv_results = _cross_validation_model_selection(
            np.asarray(data),
            candidates,
            cv=cv,
            type=type,
            variable_name=variable_name,
            raise_fit_error=raise_fit_error,
            n_jobs=n_jobs,
        )
    elif method == "AIC":
        method_name = "_aic"
    elif method == "BIC":
        method_name = "_bic"
    elif method == "MLE":
        method_name = "loglikelihood"
    else:
        raise ValueError("'method' argument value {} is invalid.".format(method))

    # Fit each distribution on full dataset and compute criterion
    all_models_results = {}
    best_fit = np.inf
    best_model_name = None

    for model_name in candidates:
        fit_results = {}
        _, loglikelihood, model_obj = _fit_and_score(
            model_name,
            data,
            validation_data,
            type=type,
            variable_name=variable_name,
            raise_fit_error=raise_fit_error,
        )
        # Handle fit error case
        if model_obj is None:
            continue

        # Compute criterion on validation data
        if method in ["CV", "MLE"]:
            # MLE = Minimize the negative log likelihood
            fit_value = -loglikelihood
            # Try also to compute AIC if available
            try:
                fit_results["AIC"] = model_obj._aic(validation_data)
            except AttributeError:
                fit_results["AIC"] = np.inf
        else:
            try:
                criterion = getattr(model_obj, method_name)
                fit_value = criterion(validation_data)
            except AttributeError:
                logger.warning(
                    f"Cannot use model {model_name} with method {method}. Criterion is set to NaN."
                )
                fit_value = np.nan
            fit_results[method] = fit_value

        # Add other metrics
        fit_results["loglikelihood"] = loglikelihood

        if model_name in ["histogram", "kde"]:
            fit_results["dict"] = {
                "name": variable_name,
                "sampling": model_obj,
            }
        else:
            # to_dict() includes fitted parameters
            fit_results["dict"] = model_obj.to_dict()

        # Compute goodness of fit tests
        if goodness_of_fit_tests and type == "continuous":
            (
                fit_results["ks_test"],
                fit_results["cv_test"],
            ) = _compute_goodness_of_fit_tests(validation_data, model_obj, model_name)

        # Add size if provided
        if size is not None:
            fit_results["dict"]["size"] = size

        if fit_value < best_fit:
            best_fit = fit_value
            best_model_name = model_name

        all_models_results[model_name] = fit_results

    # Raise a warning if all model fits failed
    if not all_models_results:  # pragma: no cover
        logger.warning(f"Could not fit any of the candidate models in {candidates}.")

    # If all models have infinite fit value, use the first fitted model anyway
    if all_models_results and best_model_name is None:  # pragma: no cover
        # Get the first valid model
        best_model_name = list(all_models_results.keys())[0]
        logger.warning(
            f"During statistical model selection, all candidate models ({candidates}) have infinite fit or failed to be fit. Model {best_model_name} is used as default."
        )

    # Add CV results
    if method == "CV":
        all_models_results = {
            key: dict(val, **cv_results[key]) for key, val in all_models_results.items()
        }
        best_model_name = max(
            all_models_results,
            key=lambda x: all_models_results[x]["mean_cv_loglikelihood"],
        )
    return all_models_results, best_model_name


def autofit(
    data,
    validation_data=None,
    method="AIC",
    cv=None,
    type="continuous",
    candidates=None,
    include_histogram=False,
    include_kde=False,
    goodness_of_fit_tests=False,
    variable_name="name",
    size=None,
    raise_fit_error=False,
    n_jobs=1,
):
    """Probability density selection and fitting based on the given data.

    'autofit' fits a pre-defined series of distributions and 1D statistical models,
    then choses amongst them the candidate having the lowest value of selection criterion.

    It returns the chosen statistical model and its parameters in the format used by CoMETS experiments.

    Args:
        data (array_like): Data used for model fitting.
        validation_data (array_like): Data used for validation.
        method (str, optional): Criterion used for selection.
            Either "AIC" for the Akaike information criterion, "BIC" for the Bayesian information criterion,
            MLE for maximum log-likelihood or "CV" for MLE cross-validation.
            Defaults to "AIC".
        cv (int or scikit-learn cross-validation generator, optional): Cross-validation scheme used.
            If an integer is given, it specifies the number of folds in the K-Fold cross-validation.
            Accepted scikit-learn cross-validation generators are KFold, LeaveOneOut, LeavePOut, ShuffleSplit.
            Defaults to None, in which case 5-Fold cross-validation is used.
        type (str, optional): Either "discrete" or "continuous", depending on the type of data generated by the statistical model.
            Defaults to "continuous".
        candidates (list of str, optional): List of candidate statistical models.
            Candidates can be chosen amongst CoMETS distributions.
            "histogram" for Histogram and "kde" for KDE are also accepted.
            Default list can be queried using `get_default_candidate_distributions(type)` function.
        include_histogram (bool, optional): If True, add "histogram" to the list of candidate models.
            If False, the candidates list is left unchanged.
            Default to False.
        include_kde (bool, optional): If True, add "kde" to the list of candidate models.
            If False, the candidates list is left unchanged.
            Default to False.
        goodness_of_fit_tests (bool, optional): If True, compute also the following goodness-of-fit test
            for the selected model:

                * Kolmogorov-Smirnov test,
                * Cramér-von Mises test,

            and raises a warning if a test reject the null hypothesis.
            Default to False.
        variable_name (str, optional): Name of the fitted variable.
            Defaults to "name".
        size (int, optional): Specifies how many iid copies of the variable to construct. Defaults to None.
        raise_fit_error (bool, optional): If True, raises an Error when a model fit fails. Use this, for example, for debugging purposes.
            If False, statistical models that cannot be fitted are ignored.
            Defaults to False.
        n_jobs (int, optional): Number of processes used during cross-validation.
            Defaults to 1.

    Returns:
        dict: Dictionary containing required information to sample from the obtained probability density model in CoMETS experiments.
    """
    # Specify validation data
    if validation_data is None:
        validation_data = data
    # Fit all distributions
    results, best_key = _probability_density_selection(
        data,
        validation_data,
        method=method,
        cv=cv,
        type=type,
        candidates=candidates,
        include_histogram=include_histogram,
        include_kde=include_kde,
        goodness_of_fit_tests=False,
        variable_name=variable_name,
        size=size,
        raise_fit_error=raise_fit_error,
        n_jobs=n_jobs,
    )
    # Compute goodness_of_fit_tests for the best model only
    if goodness_of_fit_tests and type == "continuous":
        if best_key in ["histogram", "kde"]:
            model_obj = results[best_key]["dict"]["sampling"]
        else:
            model_obj = Distribution(results[best_key]["dict"])
        ks_test, cv_test = _compute_goodness_of_fit_tests(
            validation_data, model_obj, best_key
        )
        _check_goodness_of_fit_test(ks_test, "ks_test")
        _check_goodness_of_fit_test(cv_test, "cv_test")

    # Return the best model sampling dictionary
    logger = get_logger(__name__)
    logger.info(f"'autofit' selected model {best_key} for variable {variable_name}.")
    sampling_res = results.get(best_key)
    if sampling_res is None:
        logger.warning(
            f"Could not fit any of the candidate models in {candidates}. autofit will return an empty value."
        )
        return None
    return sampling_res.get("dict")


def probability_density_selection(
    data,
    method="AIC",
    validation_data=None,
    cv=None,
    type="continuous",
    candidates=None,
    include_histogram=False,
    include_kde=False,
    goodness_of_fit_tests=True,
    variable_name="name",
    size=None,
    raise_fit_error=False,
    n_jobs=1,
):
    """Probability density selection and fitting based on the given data.

    'probability_density_selection' fits a pre-defined series of distributions to the data,
    then returns a dictionary containing, for each candidate, their estimated parameters and model selection criteria.

    Args:
        data (array_like): Data used for model fitting.
        validation_data (array_like): Data used for validation.
        method (str, optional): Criterion used for model selection.
            Either "AIC" for the Akaike information criterion, "BIC" for the Bayesian information criterion,
            MLE for maximum log-likelihood or "CV" for MLE cross-validation.
            Defaults to "AIC".
        cv (int or scikit-learn cross-validation generator, optional): Cross-validation scheme used.
            If an integer is given, it specifies the number of folds in the K-Fold cross-validation.
            Accepted scikit-learn cross-validation generators are KFold, LeaveOneOut, LeavePOut, ShuffleSplit.
            Defaults to None, in which case 5-Fold cross-validation is used.
        type (str, optional): Either "discrete" or "continuous", depending on the type of data generated by the statistical model.
            Defaults to "continuous".
        candidates (list of str, optional): List of candidate statistical models.
            Candidates can be chosen amongst CoMETS distributions.
            "histogram" for Histogram and "kde" for KDE are also accepted.
            Default list can be queried using `get_default_candidate_distributions(type)` function.
        include_histogram (bool, optional): If True, add "histogram" to the list of candidate models.
            If False, the candidates list is left unchanged.
            Default to False.
        include_kde (bool, optional): If True, add "kde" to the list of candidate models.
            If False, the candidates list is left unchanged.
            Default to False.
        goodness_of_fit_tests (bool, optional): If True, compute also the following goodness-of-fit tests
            for each model:

                * Kolmogorov-Smirnov test
                * Cramér-von Mises test

            This option applies only to the continuous case.
            Default to True.
        variable_name (str, optional): Name of the fitted variable.
            Defaults to "name".
        size (int, optional): Specifies how many iid copies of the variable to construct. Defaults to None.
        raise_fit_error (bool, optional): If True, raises an Error when a model fit fails. Use this, for example, for debugging purposes.
            If False, statistical models that cannot be fitted are ignored.
            Defaults to False.
        n_jobs (int, optional): Number of processes used during cross-validation.
            Defaults to 1.

    Returns:
        dict: Output dictionary ordered by the selection criterion value (best statistical model first).
            Each key of the dictionary is the name of a fitted model.
            Each value is a dictionary containing fitting information for the statistical model, with following items:

                - "rank": integer, ranking the model in relation to the others,
                - "<criterion>": float, score of the selection criterion. It is usually "AIC", or "BIC" if method="BIC is specified.
                - "loglikelihood": float, loglikelihood value for given data and fitted parameters,
                - "dict": dict, probability density model dictionary in CoMETS format,
                - "ks_test": dict, results of the Kolmogorov-Smirnov test,
                - "cv_test": dict, results of the Cramér-von Mises test.

            For the cross-validation method, the following items are also added:

                - "cv_loglikelihood": array_like, loglikelihood value for each split,
                - "mean_cv_loglikelihood": float, average of all splits ,
                - "std_cv_loglikelihood": float, standard deviation of all splits.
    """
    # Specify validation data
    if validation_data is None:
        validation_data = data
    # Fit all distributions
    results, _ = _probability_density_selection(
        data,
        validation_data,
        method=method,
        cv=cv,
        type=type,
        candidates=candidates,
        include_histogram=include_histogram,
        include_kde=include_kde,
        goodness_of_fit_tests=goodness_of_fit_tests,
        variable_name=variable_name,
        size=size,
        raise_fit_error=raise_fit_error,
        n_jobs=n_jobs,
    )

    # Sort results according to criterion
    if method == "CV":
        key = "mean_cv_loglikelihood"
        reverse = True
    elif method == "MLE":
        key = "loglikelihood"
        reverse = True
    else:
        key = method
        reverse = False
    sort_results = dict(
        sorted(results.items(), key=lambda x: x[1][key], reverse=reverse)
    )

    # Add rank
    sort_results = {
        key: dict(value, rank=i + 1)
        for i, (key, value) in enumerate(sort_results.items())
    }
    return sort_results


class AutomaticFitter:
    """Helper tool for distribution calibration of multiple variables.

    Args:
        data (DataFrame): Dataset on which to perform the calibration.
            Each column of the DataFrame is considered as 1D data and is calibrated independently.
            NaN values in the data are ignored.
            The column name is used as variable name.
        types (dict, optional): Specifies the type of model to fit for each column in the dataset.
            The dictionary contains the column names as keys, and values can be chosen amongst "continuous",
            "discrete" and "categorical".
            For column names that are not provided, the type of model is chosen automatically from the column data type,
            depending on the DataFrame ``dtype`` attribute. For integer dtypes, "discrete" model type is automatically chosen.
            For float dtypes, "continuous" model type is chosen. For all other cases, the default model type will be
            "categorical".
        sizes (dict, optional): Specifies the ``size`` of the variable to fit for each column in the dataset.
            The dictionary contains the variable names as keys, and an integer representing the ``size`` as values.
            In CoMETS distributions, ``size`` specifies how many iid copies of the variable to construct.
        split_validation_data (float, optional): Proportion of the dataset to use as validation data.
            Default to 0.25. If None, training and validation are performed on the full dataset.
        continuous_models (list, optional): List of candidate statistical models for continuous type.
            Candidates can be chosen amongst CoMETS distributions.
            "histogram" for Histogram and "kde" for KDE are also accepted.
            Default to None, in which case a default list with usual distributions is used.
            It can be queried using `get_default_candidate_distributions("continuous")`.
        discrete_models (list, optional): List of candidate statistical models for discrete type.
            Candidates can be chosen amongst CoMETS distributions. "histogram" for Histogram is also accepted.
            Default to None, in which case a default list with usual distributions is used.
            It can be queried using `get_default_candidate_distributions("discrete")`.
        method (str, optional):  Criterion used for model selection.
            Either "AIC" for the Akaike information criterion, "BIC" for the Bayesian information criterion,
            MLE for maximum log-likelihood or "CV" for MLE cross-validation. Default to "AIC".
        warnings (bool, optional): Display warnings raised during calibration. Default to False.
        raise_fit_error (bool, optional): If True, raises an Error when a model fit fails. Use this, for example, for debugging purposes.
            If False, statistical models that cannot be fitted are ignored.
            Defaults to False.
        n_jobs (int, optional): Number of processes used during calibration. Default to 1.
    Arguments provided at object creation are stored as class attributes and
    can be accessed and modified later on. Example:

    .. code:: python

        >>> import pandas as pd
        >>> af = AutomaticFitter(
        >>>      pd.DataFrame([0, 1, 1, 2, 4], columns=["Demo"], split_validation_data=0.2)
        >>> )
        >>> # Print current values
        >>> print(af.split_validation_data)
        0.2
        >>> print(af.types)
        {'Demo': 'discrete'}
        >>> # Modify and print attributes
        >>> af.split_validation_data = 0.1
        >>> af.types.update({'Demo': 'continuous'}))
        >>> # Print new values
        >>> print(af.split_validation_data)
        0.1
        >>> print(af.types)
        {'Demo': 'continuous'}
    """

    def __init__(
        self,
        data,
        types=None,
        sizes=None,
        split_validation_data=0.25,
        continuous_models=None,
        discrete_models=None,
        method="AIC",
        show_warnings=False,
        raise_fit_error=False,
        n_jobs=1,
    ):
        if any(not isinstance(item, str) for item in data.columns):
            raise TypeError(
                f"All column names of the DataFrame should be of type string. Current names are:\n {list(data.columns)}"
            )

        self.data = data
        self.show_warnings = show_warnings
        self.raise_fit_error = raise_fit_error
        self.n_jobs = n_jobs
        self.split_validation_data = split_validation_data
        self.continuous_models = continuous_models
        self.discrete_models = discrete_models
        self.method = method
        # Compute default types
        self.types = self.data.dtypes.to_dict()
        for key, value in self.types.items():
            if is_integer_dtype(value):
                self.types[key] = "discrete"
            elif is_float_dtype(value):
                self.types[key] = "continuous"
            else:
                self.types[key] = "categorical"

        # Update default types with user-provided types
        if types is not None:
            self.types.update(types)

        if sizes is None:
            self.sizes = {}
        else:
            self.sizes = sizes

        # Define output attribute
        self._output_dict = None

    def get_dict(self):
        """Returns the fitted distributions in CoMETS sampling format,
        that can be used as *sampling* argument in an UncertaintyAnalysis experiment.

        Returns:
            list of dictionaries: a list, with each contained dictionary describing the statistical model of a variable.
        """
        return self._output_dict

    def get_dataframe(self):
        """Returns the fitted distributions in a pandas *DataFrame* 'long' format.

        Returns:
            DataFrame: table describing the fitted distributions.
        """
        df = pd.DataFrame(self._output_dict)
        if "size" not in df:
            df["size"] = np.nan
        df["size"] = df["size"].astype("Int64")
        params = (
            pd.json_normalize(df["parameters"])
            .stack()
            .reset_index()
            .rename(columns={'level_1': 'parameters', 0: 'value'})
            .set_index("level_0")
        )
        df = df.drop(columns="parameters").merge(
            params, how="left", left_index=True, right_index=True
        )
        return df

    @staticmethod
    def _fit_col(
        col_name,
        data_array,
        type,
        size,
        method,
        continuous_models,
        discrete_models,
        split_data,
        show_warning,
        raise_fit_error,
    ):
        if data_array.size == 0:
            raise ValueError(
                f"Empty data for column {col_name}. Impossible to calibrate this variable."
            )

        with warnings.catch_warnings():
            if not show_warning:
                warnings.simplefilter("ignore")
            # size is None if not specified
            if (
                type == "categorical"
            ):  # Use empirical sampler, no need to split data as there is no model selection
                sampler = EmpiricalSampler(data=data_array)
                variable = {"name": col_name, "sampling": sampler}
                if size is not None:
                    variable["size"] = size
            else:  # Use autofit
                if type == "discrete":
                    candidates = discrete_models
                elif type == "continuous":
                    candidates = continuous_models
                else:
                    raise ValueError(
                        f"Unknown type of model: {type}. Cannot calibrate variable {col_name}"
                    )

                # Build splitted dataset
                if split_data is not None:
                    X_train, X_test = train_test_split(data_array, test_size=split_data)
                else:
                    X_train = data_array
                    X_test = None
                # Need to remove NaN values
                variable = autofit(
                    X_train,
                    validation_data=X_test,
                    method=method,
                    candidates=candidates,
                    type=type,
                    include_histogram=False,
                    include_kde=False,
                    variable_name=col_name,
                    size=size,
                    raise_fit_error=raise_fit_error,
                )
        return variable

    def fit(self):
        """Fit the data in each column of the dataset with `autofit` function,
        using the configuration specified in AutomaticFitter attributes.
        """
        self._output_dict = Parallel(n_jobs=self.n_jobs, backend="loky")(
            delayed(self._fit_col)(
                col_name,
                self.data[col_name].dropna().values,  # Remove NaNs from data
                self.types[col_name],
                self.sizes.get(col_name, None),
                self.method,
                self.continuous_models,
                self.discrete_models,
                self.split_validation_data,
                self.show_warnings,
                self.raise_fit_error,
            )
            for col_name in self.data.columns
        )


def convert_sampling_dataframe_to_list_of_dict(df, error="raise"):
    """Converts fitted distributions from pandas *DataFrame* 'long' format to CoMETS sampling format
    as a list of dict.

    Args:
        df (DataFrame): DataFrame containing the fitted distributions.
        error (str): at the end of `convert_sampling_dataframe_to_list_of_dict` function, a test checks if the returned value
            is compatible with CoMETS experiments sampling format.
            In the eventuality that it is not compatible, the error produced by the format error is caught.
            `error` argument specifies how to handle this error. Can be either:

                * 'raise': raises the error,
                * 'warn': the error is displayed as a log warning, and execution continues,
                * 'ignore': the error is ignored.

            Default to 'raise'.
    Returns:
        list of dictionaries: each dictionary describes the statistical model of a variable.
    """
    df2 = (
        df.pivot(
            index=["name", "sampling", "size"],
            columns=["parameters"],
            values='value',
        )
        .drop(np.nan, axis=1, errors='ignore')
        .reset_index()
    )
    l1 = (
        df2[["name", "sampling", "size"]]
        .apply(lambda x: x.dropna().to_dict(), axis=1)
        .tolist()
    )
    l2 = (
        df2.drop(columns=["name", "sampling", "size"])
        .apply(lambda x: x.dropna().to_dict(), axis=1)
        .tolist()
    )
    resulting_list = [dict(d1, parameters=d2) if d2 else d1 for d1, d2 in zip(l1, l2)]
    # Test if format is compatible with CoMETS sampling
    try:
        CompositeSampling(resulting_list)
    except ValueError as e:
        import io

        buffer = io.StringIO()
        df.info(buf=buffer)
        message = (
            f"The output of convert_sampling_dataframe_to_list_of_dict call is not compatible with CoMETS experiments sampling format. "
            f"This is caused by the following DataFrame: {buffer.getvalue()}"
        )

        if error == "ignore":
            pass
        elif error == "warn":
            logger = get_logger(__name__)
            logger.warning(message)
        else:
            logger = get_logger(__name__)
            message += f"\n {df}"
            logger.error(message)
            raise e
    return resulting_list
