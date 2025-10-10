# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...core.experiment import Experiment
from .analyzer import StatAnalyzer, OnlineStatAnalyzer
from ...statistical_tools.sampling.sampling import CompositeSampling
from ...statistical_tools.sampling.sequenceregistry import SequenceRegistry
from ...utilities.utilities import to_list
from ...utilities import get_logger
from ...utilities.utilities import next_power_of_2


class UncertaintyAnalysis(Experiment):
    """
    Perform an uncertainty analysis on a task.

    Args:
        sampling (dict or list of dicts): defines the function to generate samples on the input parameters. It consists of a list of distributions or generators.
        task (Task): Task the analysis will be performed on.
        method (string, optional, default to "random"): Sampling method to use.
        analyzer (string or list of strings, optional, default to “standard”): string or list of strings, specifies the list of output statistics computed at the end of the experiment.
        online_stats (bool): Switch determining whether statistics will be
            calculated online (on-the-fly, i.e. at the end of a batch), or at
            the end of the experiment. Only experiments that have iterations
            can use this feature (having iterations or not depends on the
            sampling method). Default False.
            Statistics will be updated every batch_size simulations. Therefore,
            to make optimal use of online stats, it is advised that the batch
            size is significantly smaller than the (expected) max number of
            evaluations carried out in the experiment.
        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            CoMETS parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        batch_size (int, optional): Defines the number of evaluations during an iteration of an experiment having a loop.
            Default to None, in which case batch_size is set to n_jobs.
            batch_size is not used for experiments without a loop.
        blocking (bool, optional): if true, the run method of the analysis will be blocking, otherwise it will run in another thread. Defaults to true.
        stop_criteria (dict, optional) : Stopping criteria of the experiment. The available criteria are ["max_evaluations", "max_iterations", "max_duration", "callback"].
        callbacks: Function or list of functions called at the end of each iteration.
        save_task_history (bool, optional): Saves the experiment history in the format of a dictionary containing two keys: 'inputs' and 'outputs'.
            Inputs contains a list of all the inputs that have been evaluated during the experiment. Similarly, outputs contains a list of all the results from these task's evaluations.
            This history is stored in the variable UncertaintyAnalysis.task_history

    Example
    -------
    Imagine that we have a function f that takes as an input a parameter 'orders' and returns the profit.
    We want to perform an uncertainty analysis on this function where the uncertainty on the orders is
    modeled by a variable following a discrete uniform distribution.

    >>> import comets
    >>>
    >>> def f(parameter):
    >>>    profit = parameter['orders']*3.2 - 12
    >>>    return {'profit': profit}
    >>> mytask = comets.FunctionalTask(f)
    >>>
    >>> sampling = [
    >>>    {
    >>>        "name": 'orders',
    >>>        "sampling": "discreteuniform",
    >>>        "parameters": {'low': 0, 'high': 201},
    >>>    }]
    >>>
    >>> ua = comets.UncertaintyAnalysis(
    >>>    task = mytask,
    >>>    sampling = sampling,
    >>>    stop_criteria = {'max_evaluations' : 1000})
    >>>
    >>> ua.run()
    >>> ua.results
    {'statistics':             mean      std         sem       confidence interval of the mean at 95%
                       profit  305.3568  182.796618  5.780537  (294.0134133497827, 316.70018665021735)}

    """

    def __init__(
        self,
        sampling,
        task,
        method='random',
        analyzer='standard',
        online_stats=False,
        n_jobs=1,
        batch_size=None,
        stop_criteria={'max_evaluations': int(10e4)},
        blocking=True,
        callbacks=[],
        save_task_history=False,
    ):
        # Initialize from the parent Experiment class
        super().__init__(
            task=task,
            n_jobs=n_jobs,
            batch_size=batch_size,
            blocking=blocking,
            stop_criteria=stop_criteria,
            callbacks=callbacks,
            save_task_history=save_task_history,
        )
        self.input_sampling = to_list(sampling)

        # Set number of samples to the next power of 2 for Sobol sampler
        if method == "sobol":
            N = next_power_of_2(self._stop_criteria._criteria['max_evaluations'])
            # Check if max evaluations is a power of 2. If not, replace it by the next power of 2.
            if N != self._stop_criteria._criteria['max_evaluations']:
                self._stop_criteria._criteria['max_evaluations'] = N
                logger = get_logger(__name__)
                logger.warning(
                    "Number of samples in the Sobol sequence should be a power of 2, argument max_evaluations is set to {}".format(
                        N
                    )
                )

        # Check if the experiment has loops:
        if not SequenceRegistry.information[method]["HasIterations"]:
            self.has_iterations = False
            self._check_max_evaluations(method)
        self.sampler = CompositeSampling(self.input_sampling, rule=method)

        # Determine whether we use online stats. Only possible
        # if we use a sampling method that has iterations.
        self.online_stats = online_stats if self.has_iterations else False

        # Set up which type of analyzer we use, based on whether stats
        # are online or offline
        if self.online_stats:
            self.analyzer = OnlineStatAnalyzer(to_list(analyzer))
        else:
            self.analyzer = StatAnalyzer(to_list(analyzer))

    def _initialize(self):
        self.list_of_results = []

    def _execute(self):
        """
        Method to sample and evaluate tasks when the uncertainty analysis is performed with iterations
        """

        # Generation of new samples to evaluate
        list_of_samples = self.sampler.get_samples(number_of_samples=self.batch_size)

        # Evaluation of the task on the samples
        list_of_results = self._evaluate_tasks(self.task, list_of_samples)

        # For online stats, update analyzer with the current data (and don't store results)
        if self.online_stats:
            for result in list_of_results:
                self.analyzer.update(result)
        # Offline stats: extend the stored list of results with the current data
        else:
            self.list_of_results.extend(list_of_results)

    def _execute_no_loop(self):
        """
        Method to sample and evaluate tasks when the uncertainty analysis is performed without iterations
        """
        # Generation of new samples to evaluate
        list_of_samples = self.sampler.get_samples(
            number_of_samples=self._stop_criteria._criteria['max_evaluations']
        )

        # Evaluation of the task on the samples
        self.list_of_results = self._evaluate_tasks(self.task, list_of_samples)

    def _finalize(self):
        if self.online_stats:
            self.results = self.analyzer.compute_statistics()
        else:
            self.results = self.analyzer.compute_statistics(self.list_of_results)
