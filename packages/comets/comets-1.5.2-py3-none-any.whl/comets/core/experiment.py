# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from abc import ABC
import joblib
import types
import threading
import time
import timeit
import math
import copy

from ..core.stopcriteria import StopCriteria
from .task import FunctionalTask
from .parallelmanager import ParallelManager
from ..utilities.utilities import format_duration
from ..utilities import get_logger


class Experiment(ABC):
    """
    Abstract base experiment class

    Args:
        task (Task): Task the experiment deals with.
        n_jobs (int, optional): Number of processes used by the experiment to perform task evaluations in parallel. Default to 1 (no parallelization).
            CoMETS parallel processing is managed by the joblib library.
            For values n_jobs < 0, (cpu_count + 1 + n_jobs) are used. Thus for n_jobs=-1, the maximum number of CPUs is used. For n_jobs = -2, all CPUs but one are used.
        batch_size (int, optional): Defines the number of evaluations during an iteration of an experiment having a loop.
            Default to None, in which case batch_size is set to n_jobs.
            batch_size is not used for experiments without a loop.
        blocking (bool, optional): if true, the run method of the analysis will be blocking, otherwise it will run in another thread. Defaults to true.
        stop_criteria (dict, optional): Dictionary giving the criteria to stop an experiment.

            The following strings correspond to a valid criterion: "max_evaluations", "max_iterations", "max_duration", "callback". A callback function should have the following prototype:

            `` def callback(Experiment experiment):
                    ...
                    return bool ``
        callbacks: Function or list of functions called at the end of each iteration
        save_task_history (bool, optional): Saves the experiment history in the format of a dictionary containing two keys: 'inputs' and 'outputs'.
            Inputs contains a list of all the inputs that have been evaluated during the experiment. Similarly, outputs contains a list of all the results from these task's evaluations.
            This history is stored in the variable Optimization.task_history

    Attributes:
        task (Task): Task the experiment deals with.
        parallelmanager (ParallelManager): ParallelManager used by the Experiment to evaluate Tasks.
        number_of_evaluations (int): Number of times the task has been evaluated.
        number_of_iterations (int): Number of iterations the experiment has performed.
        has_iterations (bool): Tells if the experiment algorithm contains a main loop.
        results (dict): Results of the experiment.
    """

    def __init__(
        self,
        task,
        n_jobs=1,
        blocking=True,
        batch_size=None,
        stop_criteria={'max_evaluations': int(10e4)},
        callbacks=[],
        save_task_history=False,
    ):
        if (
            n_jobs < 0
        ):  # The parallel manager will use the number of CPUs when n_jobs=-1, but so should other parts of the experiment, such as algorithms
            n_jobs += (
                joblib.cpu_count() + 1
            )  # for n_jobs = -2, all CPUs but one are used
        self.n_jobs = max(1, n_jobs)
        self.parallelmanager = ParallelManager(n_jobs=self.n_jobs)

        if batch_size is None:
            self.batch_size = self.n_jobs
        else:
            self.batch_size = batch_size

        if save_task_history:
            self.task_history = {"inputs": [], "outputs": []}
        else:
            self.task_history = None
        # Check that the task is a valid task (it has an 'evaluate' method)
        if callable(getattr(task, "evaluate", None)):
            self.task = task
        elif isinstance(task, types.FunctionType):
            self.task = FunctionalTask(task)
        else:
            raise ValueError(
                "Task provided to the experiment is not a task and has no 'evaluate' method"
            )

        self.number_of_iterations = 0
        self.number_of_evaluations = 0
        self.initial_time = 0
        self.results = {}
        self.blocking = blocking
        self.stop_command = False
        self.thread = None
        self.has_iterations = True
        self.save_task_history = save_task_history
        self.i_am_finished = False

        if callable(callbacks):
            self._callbacks = [callbacks]
        elif isinstance(callbacks, list):
            for callback in callbacks:
                if not callable(callback):
                    raise TypeError(
                        "A callback provided to the experiment is not callable"
                    )
            self._callbacks = list(callbacks)
        else:
            raise TypeError("Provided callbacks do not have a valid type")

        self._set_stop_criteria(stop_criteria)

    def _set_stop_criteria(self, stop_criteria):
        if isinstance(stop_criteria, dict):
            self._stop_criteria = StopCriteria(stop_criteria.copy(), self)
        elif isinstance(stop_criteria, StopCriteria):
            self._stop_criteria = stop_criteria
        else:
            raise TypeError("Stopping criterion does not have a valid type")

    def _check_max_evaluations(self, method_name):
        if 'max_evaluations' not in self._stop_criteria._criteria:
            raise ValueError(
                "Algorithm {} requires max_evaluations".format(method_name)
            )

    def _apply_stop_criteria(self):
        pass

    def run(self):
        """
        Method that runs the experiment
        """
        self.stop_command = False
        if self.blocking:
            self._run()
        else:
            self.thread = threading.Thread(target=self._run, args=())
            self.thread.start()

    def _run(self):
        """
        Method that runs the experiment
        """
        logger = get_logger(__name__)

        if self.number_of_iterations == 0:
            self.initial_time = time.time()
            self._stop_criteria.initialize()
            logger.info("Initializing the %s experiment", type(self).__name__)
            self._initialize()
            logger.info(
                "%s's configuration: n_jobs: %s, batch_size: %s, stop_criteria: %s",
                type(self).__name__,
                self.n_jobs,
                self.batch_size,
                self._stop_criteria._criteria,
            )

        logger.info("Starting the %s's execution", type(self).__name__)

        if not self.has_iterations:
            logger.info(
                "Executing the %s experiment without a loop", type(self).__name__
            )
            self._execute_no_loop()
        else:
            logger.info("Executing the %s experiment with a loop", type(self).__name__)
            while not self._stop_criteria.is_finished() and not self.i_am_finished:
                # This implements a manual stop by the user
                if self.stop_command:
                    break

                logger.info(
                    "Iteration number %s of the %s loop",
                    self.number_of_iterations,
                    type(self).__name__,
                )

                self._execute()

                self.number_of_iterations += 1

                # Monitoring callbacks
                for callback in self._callbacks:
                    callback(self)

        logger.info("Finalizing the %s", type(self).__name__)
        self._finalize()

    def _initialize(self):
        pass

    def _execute(self):
        pass

    def _execute_no_loop(self):
        pass

    def _finalize(self):
        pass

    def _evaluate_tasks(self, task, input_parameter_sets):
        """
        Delegate tasks evaluation to the parallel manager. Increment evaluations counter

        Args:
            tasks (Task): A Task or a list of Tasks
            input_parameter_sets (ParameterSet): A list of ParameterSets
        Returns:
            output_parameter_sets (ParameterSet): A list of ParameterSet
        """
        # Compute tasks
        output_parameter_sets = self.parallelmanager.evaluate_tasks(
            task, input_parameter_sets, n_jobs=self.n_jobs
        )
        # Increment number_of_evaluations counter
        self.number_of_evaluations += len(output_parameter_sets)

        # Add the new inputs and outputs to the history
        if self.save_task_history:
            self.task_history["inputs"].extend(input_parameter_sets)
            self.task_history["outputs"].extend(output_parameter_sets)

        return output_parameter_sets

    def stop(self):
        """
        Set a flag stop_command to True (the _run of the experiment needs to check this flag periodically)
        and wait for the thread running the experiment to terminate
        """
        self.stop_command = True
        if self.is_running():
            self.thread.join()

    def is_running(self):
        """
        Check if the experiment is currently running in another thread
        """
        if self.thread is None:
            return False
        else:
            return self.thread.is_alive()

    def resume(self, stop_criteria=None):
        """
        Resume the experiment

        Args:
            stop_criteria (dict, optional): provide new input stopping criteria. Erases the previous criteria.
        """
        if stop_criteria is not None:
            self._set_stop_criteria(stop_criteria)
            self._apply_stop_criteria()
            self._stop_criteria.initialize()
        self.run()

    def timeit(self, print_to_console=True):
        """Estimate the duration of the experiment.

        Args:
            print_to_console:
                If True, display results to the user in the console, else,
                return the time of execution in seconds as float. Default to True.
        """
        if self.has_iterations:
            # Deep copy of experiment, in order not to modify original experiment state
            experiment = copy.deepcopy(self)
            # Remove task history to save space
            experiment.save_task_history = False
            # Set blocking to True to be able to time the execution
            experiment.blocking = True

            # Dummy execution to open threads and remove associated overhead from timeit
            experiment._initialize()
            experiment._execute()

            # Get actual stop criteria
            max_evaluations = self._stop_criteria._criteria.get(
                'max_evaluations', math.inf
            )
            max_iterations = self._stop_criteria._criteria.get(
                'max_iterations', math.inf
            )
            max_duration = self._stop_criteria._criteria.get('max_duration', math.inf)
            number_of_iterations = min(
                math.ceil(max_evaluations / self.batch_size), max_iterations
            )

            # Compute time per iteration
            # --------------------------
            def setup(experiment):
                # Reset experiment state (in case timeit is called after a run)
                experiment.number_of_evaluations = 0
                experiment.number_of_iterations = 0
                experiment.initial_time = time.time()
                experiment._stop_criteria.initialize()
                experiment._initialize()

            # Create timer
            timer = timeit.Timer(
                lambda: experiment._execute(), setup=lambda: setup(experiment)
            )
            try:
                number, t1 = timer.autorange()
            except:  # noqa: E722, pragma: no cover
                timer.print_exc()
                return 1
            # Long execution case:
            if number == 1:
                # Test if iteration was terminated
                time_per_iteration = t1
            else:
                # Perform "number" iterations
                timer = timeit.Timer(
                    lambda: experiment._execute(), setup=lambda: setup(experiment)
                )
                try:
                    raw_timings = timer.repeat(5, number=number)
                except:  # noqa: E722, pragma: no cover
                    timer.print_exc()
                    return 1
                timings = [dt / number for dt in raw_timings]
                time_per_iteration = min(timings)

            stops = [number_of_iterations * time_per_iteration, max_duration]
            index, total_duration = min(enumerate(stops), key=lambda x: x[1])

            if index == 1:  # pragma: no cover
                print("Experiment finishes due to max_duration criterion reached.")

            # Tell user which criterion stops the experiment (duration or max iterations)
            if print_to_console:  # pragma: no cover
                print(
                    "Estimated duration of experiment main loop: "
                    + format_duration(total_duration)
                )
            else:
                return total_duration
        else:  # pragma: no cover
            print("'timeit' method not available for an experiment without iterations.")
