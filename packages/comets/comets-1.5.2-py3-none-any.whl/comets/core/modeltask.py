# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from .task import Task
from ..utilities import get_logger


class ModelTask(Task):
    """
    A ModelTask is a Task that uses a ModelInterface to evaluate the input ParameterSet,
    it allows the user to specify its own encode and get_outcomes methods.

    Args:
        modelinterface (ModelInterface): ModelInterface used by the Task to communicate with a model
        encode (callable, optional): An encoding function taking as argument a ParameterSet and returning a ParameterSet,
            is applied to every ParameterSet input to the task before setting the input parameters of the model with the ModelInterface.
            If no encoding function is provided, the input ParameterSet of the task is provided as it is to the ModelInterface.
        get_outcomes (callable, optional): A function taking as argument a modelinterface and returning a ParameterSet,
            is used to specify which outputs of the model are of interest to the experiment and to post-process them.
            If no function is provided, the default behavior is to return all default output parameters of the model,
            which is done by calling get_outputs(['all'] on the ModelInterface.
        cold_input_parameter_set (ParameterSet, optional): Input ParameterSet of 'cold' parameters that will not change.
            These parameters will not be encoded but provided directly to the model through the modelinterface. They will be appended to any additional encoded input ParameterSet. New parameters may replace the 'cold' parameters values.
    """

    def __init__(
        self,
        modelinterface,
        encode=None,
        get_outcomes=None,
        cold_input_parameter_set=None,
    ):
        self.modelinterface = modelinterface
        self.encode = encode
        self.get_outcomes = get_outcomes
        if cold_input_parameter_set is None:
            self.cold_input_parameter_set = {}
        else:
            self.cold_input_parameter_set = cold_input_parameter_set

    def evaluate(self, input_parameter_set=None):
        """Evaluate the model on the input_parameter_set

        Args:
            input_parameter_set (ParameterSet): input ParameterSet of the Task

        Returns:
            ParameterSet: output of the Task
        """
        self.modelinterface.initialize()
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
        if self.encode is None:
            inputs.update(input_parameter_set)
            self.modelinterface.set_inputs(inputs)
        else:
            inputs.update(self.encode(input_parameter_set))
            self.modelinterface.set_inputs(inputs)
        self.modelinterface.run()
        if self.get_outcomes is None:
            outputs = self.modelinterface.get_outputs(['all'])
        else:
            outputs = self.get_outcomes(self.modelinterface)
        self.modelinterface.terminate()
        logger.debug("Output of task: %s", outputs)

        return outputs
