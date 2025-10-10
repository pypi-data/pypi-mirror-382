# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import pandas as pd

from ...core.experiment import Experiment
from ...core.parameterset import ParameterSet
from .sensitivityanalyzer import SensitivityAnalyzerRegistry
from ...utilities.utilities import to_list


class GlobalSensitivityAnalysis(Experiment):
    """
    Sensitivity analysis class

    Sensitivity analysis is the study of how variations in the output of a Task can be divided and allocated to variations in the inputs of the Task

    Args:
        variables : The list of input variables and associated information.
        task (Task): Task the analysis will be performed on.
        method (string, optional): Sensitivity analysis method to use.
        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            CoMETS parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        blocking (bool, optional): if true, the run method of the analysis will be blocking, otherwise it will run in another thread. Defaults to true.
        callbacks: Function or list of functions called at the end of each iteration.
        save_task_history (bool, optional): Saves the experiment history in the format of a dictionary containing two keys: 'inputs' and 'outputs'.
            Inputs contains a list of all the inputs that have been evaluated during the experiment. Similarly, outputs contains a list of all the results from these task's evaluations.
            This history is stored in the variable GlobalSensitivityAnalysis.task_history

    """

    def __init__(
        self,
        variables,
        task,
        method='FAST',
        n_jobs=1,
        blocking=True,
        callbacks=[],
        save_task_history=False,
        method_arguments={},
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

        # SensitivityAnalyzerRegistry[method] contains a partial Analyzer class with method "method"
        self.sensitivityanalyzer = SensitivityAnalyzerRegistry[method](
            variables=self.variables,
            method_arguments=dict(method_arguments),
        )
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
        self.list_of_samples = self.sensitivityanalyzer.get_samples(
            number_of_samples=self.sensitivityanalyzer.N
        )

        # Evaluation of the task on the samples
        self.list_of_results = self._evaluate_tasks(self.task, self.list_of_samples)

    def _finalize(self):
        flattened_list_of_results = [
            ParameterSet.flatten(result) for result in self.list_of_results
        ]
        # Compute sensitivity indices
        indices = self.sensitivityanalyzer.sensitivity_analysis(
            flattened_list_of_results
        )
        # Construct Multi-index Dataframe, stack to have one column
        df = pd.DataFrame.from_dict(indices).stack().to_frame()
        # Unroll inner dict of input variables
        df = pd.DataFrame(df[0].values.tolist(), index=df.index).stack().to_frame()
        # Set outer level (the indices) as columns, give a name to line indexes
        df = (
            df.unstack(level=0)
            .droplevel(0, axis=1)
            .rename_axis(index=["Output variable", "Input variable"])
        )
        self.results = df
