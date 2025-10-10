# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from abc import ABC, abstractmethod
import timeit

from ..utilities import get_logger
from ..utilities.utilities import format_duration


class Task(ABC):
    """
    Abstract Task class.
    """

    @abstractmethod
    def evaluate(self, input_parameter_set=None):
        """
        Method mapping a ParameterSet to another ParameterSet.

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet

        Returns:
            ParameterSet: the output ParameterSet
        """
        pass

    def timeit(self, input_parameter_set=None, print_to_console=True):
        """Time the execution of the Task using a similar method as python `timeit`.

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet. Default to {}.
            print_to_console:
                If True, display results to the user in the console, else,
                return the time of execution in seconds as float. Default to True.

        Returns:
            If print_to_console=False, returns the time of execution in seconds.
        """
        if input_parameter_set is None:
            input_parameter_set = {}

        timer = timeit.Timer(
            lambda: self.evaluate(input_parameter_set=input_parameter_set)
        )
        try:
            number, t1 = timer.autorange()
        except:  # noqa: E722, pragma: no cover
            timer.print_exc()
            return 1

        if number == 1:
            if print_to_console:
                print("Duration of Task evaluation:" + format_duration(t1))
                print(
                    "Analysis on one evaluation, hence results are likely unreliable."
                )
            else:
                return t1
        else:
            try:
                raw_timings = timer.repeat(5, number)
            except:  # noqa: E722, pragma: no cover
                timer.print_exc()
                return 1
            timings = [dt / number for dt in raw_timings]
            best = min(timings)
            if print_to_console:
                print("Duration of Task evaluation:" + format_duration(best))
                print("Number of evaluations per second: {}".format(int(1 / best)))
            else:
                return best


class FunctionalTask(Task):
    """
    Task for which the evaluation corresponds to the evaluation of a function provided at the creation of the FunctionalTask.

    Args:
        function (callable): A python function taking a ParameterSet as input and returning a ParameterSet.
        cold_input_parameter_set (ParameterSet, optional): Input ParameterSet of 'cold' parameters that will not change.
            These parameters will be appended to any additional input ParameterSet of the task. New parameters may replace the 'cold' parameters values.

    Example
    -------
    Imagine we have a function f that returns a dictionary of the form: ``{'y': y}``.

    >>> def f(input_parameter_set):
    >>>     return {'y': input_parameter_set['x'] + 1}
    >>> task = FunctionalTask(f)
    >>> task.evaluate({'x': 0})
    {'y': 1}

    """

    def __init__(self, function, cold_input_parameter_set=None):
        """
        Constructor of the FunctionalTask
        """
        self.function = function
        if cold_input_parameter_set is None:
            self.cold_input_parameter_set = {}
        else:
            self.cold_input_parameter_set = cold_input_parameter_set

    def evaluate(self, input_parameter_set=None, *args, **kwargs):
        """
        Apply the function to an input ParameterSet and return the resulting ParameterSet.

        Args:
            input_parameter_set (ParameterSet): the input ParameterSet
        Returns:
            ParameterSet: output ParameterSet
        """
        logger = get_logger(__name__)
        logger.debug(
            "Running task with cold input parameter set %s and input parameter set: %s",
            self.cold_input_parameter_set,
            input_parameter_set,
        )

        if input_parameter_set is None:
            input_parameter_set = {}

        inputs = {}
        inputs.update(self.cold_input_parameter_set)
        inputs.update(input_parameter_set)

        outputs = self.function(inputs, *args, **kwargs)

        logger.debug("Output of task: %s", outputs)

        return outputs
