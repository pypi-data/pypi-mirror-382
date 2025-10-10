# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from .OAT import OAT
from ...core.experiment import Experiment
from ...utilities.utilities import to_list


class LocalSensitivityAnalysis(Experiment):
    """
    Local Sensitivity analysis class

    Local sensitivity analysis studies the impact of factors on a model around a reference point in space

    Args:
        variables : The list of input variables and associated information.
        task (Task): Task the analysis will be performed on.
        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            CoMETS parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        blocking (bool, optional): if true, the run method of the analysis will be blocking, otherwise it will run in another thread. Defaults to true.
        callbacks: Function or list of functions called at the end of each iteration.
        save_task_history (bool, optional): Saves the experiment history in the format of a dictionary containing two keys: 'inputs' and 'outputs'.
            Inputs contains a list of all the inputs that have been evaluated during the experiment. Similarly, outputs contains a list of all the results from these task's evaluations.
            This history is stored in the variable LocalSensitivityAnalysis.task_history

    """

    def __init__(
        self,
        variables,
        task,
        n_jobs=1,
        blocking=True,
        callbacks=[],
        save_task_history=False,
    ):
        # Initialize from the parent Experiment class
        super().__init__(
            task=task,
            n_jobs=n_jobs,
            stop_criteria={},
            blocking=blocking,
            callbacks=callbacks,
            save_task_history=save_task_history,
        )

        self.variables = to_list(variables)

        # Choose the analyzer : OAT by default (the only one available )for now
        self.sensitivityanalyzer = OAT(variables=self.variables)
        # Create a shortcut for the expected number of evaluations, if it exists
        try:
            self.expected_number_of_evaluations = (
                self.sensitivityanalyzer.expected_number_of_evaluations
            )
        # Just in case a new method does not implement expected_number_of_evaluations, but should not happen.
        except AttributeError:  # pragma: no cover
            self.expected_number_of_evaluations = None

        # None of the actual algorithm has iterations yet
        self.has_iterations = False

    def _initialize(self):
        pass

    def _execute_no_loop(self):
        # Generation of samples to evaluate
        self.list_of_samples = self.sensitivityanalyzer.get_samples()

        # Evaluation of the task on the samples
        self.list_of_results = self._evaluate_tasks(self.task, self.list_of_samples)

    def _finalize(self):
        self.results = self.sensitivityanalyzer.sensitivity_analysis(
            self.list_of_results
        )
