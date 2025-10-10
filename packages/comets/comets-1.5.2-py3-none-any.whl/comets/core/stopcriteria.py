# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

import time
import datetime
from ..utilities import get_logger, to_list


class StopCriteria:
    """
    StopCriteria class

    Interface for providing stopping criteria to algorithms

    Args:
        stop_dict (dict): dictionary of stopping criteria. Available criteria are:
            "max_evaluations", "max_iterations", "max_duration", "callbacks".
            For "callbacks", the value should be a user-defined function or a list
            of functions, which should return True if the experiment must be stopped
            and False otherwise.
        experiment (Experiment): experiment the StopCriteria will apply to.


    """

    _AVAILABLE_CRITERIA = [
        "max_evaluations",
        "max_iterations",
        "max_duration",
        "callbacks",
        "callback",  # kept for backwards compatibility
    ]

    def __init__(self, stop_dict, experiment):
        self._initial_values = {}
        for key in stop_dict:
            if key not in self._AVAILABLE_CRITERIA:
                raise ValueError("Unknown stopping criterion <{}>".format(key))
        self._criteria = stop_dict

        # Reformat callbacks to list and add 'callback' (if present) to 'callbacks'
        # A little hacky perhaps.
        if 'callbacks' in self._criteria:
            self._criteria['callbacks'] = to_list(self._criteria['callbacks'])
        if 'callback' in self._criteria:
            if 'callbacks' in self._criteria:
                self._criteria['callbacks'].extend(to_list(self._criteria['callback']))
            else:
                self._criteria['callbacks'] = to_list(self._criteria['callback'])
            self._criteria.pop('callback')

        # Deal with the different formats that max_duration can take
        if "max_duration" in self._criteria:
            # Convert duration to seconds
            if isinstance(self._criteria["max_duration"], datetime.timedelta):
                self._criteria["max_duration"] = self._criteria[
                    "max_duration"
                ].total_seconds()
            elif isinstance(self._criteria["max_duration"], dict):
                max_duration_args = self._criteria["max_duration"]
                try:
                    self._criteria["max_duration"] = datetime.timedelta(
                        **max_duration_args
                    ).total_seconds()
                except TypeError:
                    raise ValueError(
                        "Invalid max_duration format {}".format(max_duration_args)
                    )
            else:
                try:
                    self._criteria["max_duration"] = float(
                        self._criteria["max_duration"]
                    )
                except ValueError:
                    raise ValueError(
                        "Invalid max_duration format {}".format(
                            self._criteria["max_duration"]
                        )
                    )

        self.experiment = experiment

    def initialize(self):
        """
        Initialize the starting value for each criterion. When stopping criteria
        are checked, this initial value is subtracted from the current value.
        """
        self._initial_values["max_evaluations"] = self.experiment.number_of_evaluations
        self._initial_values["max_iterations"] = self.experiment.number_of_iterations
        self._initial_values["max_duration"] = time.time()
        self._initial_values["callbacks"] = None

    def is_finished(self):
        """
        Browse all criteria to check if the algorithm should stop
        """
        logger = get_logger(__name__)
        for key, value in self._criteria.items():
            if getattr(self, key)():
                logger.info(
                    "%s stopped: budget exhausted for criterion %s = %s",
                    type(self.experiment).__name__,
                    key,
                    value,
                )

                return True

    def max_evaluations(self):
        '''Return True if the max number of evaluations has been reached'''
        return (
            self.experiment.number_of_evaluations
            - self._initial_values["max_evaluations"]
            >= self._criteria["max_evaluations"]
        )

    def max_iterations(self):
        '''Return True if the max number of iterations has been reached'''
        return (
            self.experiment.number_of_iterations
            - self._initial_values["max_iterations"]
            >= self._criteria["max_iterations"]
        )

    def max_duration(self):
        '''Return True if the max duration has been reached'''
        return (
            time.time() - self._initial_values["max_duration"]
            >= self._criteria["max_duration"]
        )

    def callbacks(self):
        '''Return True if one of the callbacks has reached its condition'''
        return_values = [
            callback(self.experiment) for callback in self._criteria['callbacks']
        ]
        return any(return_values)
