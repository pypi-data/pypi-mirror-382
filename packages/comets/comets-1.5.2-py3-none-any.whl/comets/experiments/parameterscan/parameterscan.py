# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...core.experiment import Experiment


class ParameterScan(Experiment):
    """
    Parameter scan class. The aim of this experiment is to perform a task evaluation for all the ParameterSets in list_of_parametersets. The results
    of these evaluations are stored in the attribute results. It consists of a dict in the following format: {'outputs': list_of_results}.
    list_of_results is a list where element [i] corresponds to the task's output when evaluated with list_of_parameter_set[i]. As this experiment inherits from the Experiment class,
    all the general functionalities remains available (e.g stop_criteria...).

    Args:
        task (Task): Task the analysis will be performed on.
        list_of_parametersets (list or generator): list or generator of ParameterSets on which the task will be evaluated.

        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            CoMETS parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        batch_size (int, optional): Defines the number of evaluations during an iteration of the experiment.
            Default to None, in which case batch_size is set to len(list_of_parametersets).
        blocking (bool, optional): if true, the run method of the analysis will be blocking, otherwise it will run in another thread. Defaults to true.
        stop_criteria (dict, optional): Dictionary giving the criteria to stop an experiment. If all the ParameterSets in list_of_parametersets have been evaluated and the
            stopping criteria isn't reached, the experience will still be stopped. By default the stop criteria is sets to {'max_evaluations': int(10e14)}.
        callbacks: Function or list of functions called at the end of each iteration

    Attributes:
        results: Results of the experiment in the following format: {'outputs': list_of_results}.
            list_of_results is a list where element [i] corresponds to the task's output when evaluated with list_of_parameter_set[i].
    """

    def __init__(
        self,
        task,
        list_of_parametersets,
        n_jobs=1,
        batch_size=None,
        stop_criteria=None,
        blocking=True,
        callbacks=[],
    ):
        self.list_of_parametersets = list_of_parametersets
        self.has_iterations = True

        if stop_criteria is None:
            stop_criteria = {}

        if (
            batch_size is not None
            and isinstance(self.list_of_parametersets, list)
            and batch_size > len(self.list_of_parametersets)
        ):
            batch_size = len(self.list_of_parametersets)

        # Initialize from the parent Experiment class
        super().__init__(
            task=task,
            n_jobs=n_jobs,
            batch_size=batch_size,
            stop_criteria=stop_criteria,
            blocking=blocking,
            callbacks=callbacks,
        )

    def _initialize(self):
        self.list_of_results = []
        if isinstance(self.list_of_parametersets, list):
            self.iterator = iter(self.list_of_parametersets)
        else:
            self.iterator = self.list_of_parametersets

    def _execute(self):
        # Generation of new samples to evaluate
        list_of_samples = self._get_samples(
            batch=self.batch_size,
        )
        # Evaluation of the task on the samples
        self.list_of_results.extend(self._evaluate_tasks(self.task, list_of_samples))

    def _finalize(self):
        # Decode the results in the following format: {'outputs': list_of_results}
        self.results = {
            'outputs': self.list_of_results,
        }

    def _get_samples(self, batch):
        samples = []
        for i in range(batch):
            value = next(self.iterator, None)
            if value is None:
                self.i_am_finished = True
            else:
                samples.append(value)
        return samples
