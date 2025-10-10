import numpy as np
from ...utilities import get_logger


class _ConstraintHandler:
    def __init__(self, constraint_list, method="adaptive_barrier"):
        if not isinstance(constraint_list, list):
            raise ValueError("Unsupported type for constraints. Should have type list.")

        self.method = method
        self.constraint_list = constraint_list

        for constraint in constraint_list:
            if not isinstance(constraint, dict):
                raise ValueError(
                    f"Constraint with index {constraint_list.index(constraint)} should have type dict"
                )
            if "name" not in constraint.keys():
                raise ValueError(
                    f"Please provide a name for constraint with index {constraint_list.index(constraint)}."
                )

            if "type" not in constraint.keys():
                raise ValueError(
                    f"Please provide a type for constraint {constraint['name']}"
                )

            if "threshold" not in constraint.keys():
                raise ValueError(
                    f"Threshold not found for constraint {constraint['name']}."
                )

            if not isinstance(constraint['name'], str):
                raise ValueError(
                    f"Unsupported name for constraint {constraint['name']}, 'name' should have type str"
                )

            if not isinstance(constraint['threshold'], (int, float)):
                raise ValueError(
                    f"Unsupported threshold for constraint {constraint['name']}, 'threshold' should have type int or float"
                )

            if not isinstance(constraint['type'], str):
                raise ValueError(
                    f"Unsupported type for constraint {constraint['name']}, 'type' should have type str"
                )

            if constraint["type"] not in ['greater_than', 'less_than', 'equal_to']:
                raise ValueError(
                    f"Type {constraint['type']} of constraint {constraint['name']} is not available."
                    "Available types are 'greater_than', 'less_than' and 'equal_to'"
                )

    @staticmethod
    def greater_than(output, threshold):
        return threshold - output

    @staticmethod
    def less_than(output, threshold):
        return -threshold + output

    @staticmethod
    def equal_to(output, threshold):
        return abs(output - threshold) - threshold * 1e-03

    def __str__(self):
        resume = ""
        for index in range(len(self.constraint_list)):
            resume += f"Constraint {index}: variable {self.constraint_list[index]['name']} {self.constraint_list[index]['type']} {self.constraint_list[index]['threshold']}\n"
        return resume

    def compute_violation(self, task_outputs):
        """Computes the constraint violation of each sample in the batch and each constraint function defined"""

        constraint_violation = np.zeros([len(self.constraint_list), len(task_outputs)])
        for index_function, constraint in enumerate(self.constraint_list):
            for index_sample in range(len(task_outputs)):
                try:
                    constraint_violation[index_function, index_sample] = getattr(
                        self, constraint['type']
                    )(
                        task_outputs[index_sample][constraint['name']],
                        constraint['threshold'],
                    )
                except KeyError:
                    logger = get_logger(__name__)
                    logger.debug(
                        f"Available Task outputs for constraint violation computation are: {list(task_outputs[index_sample].keys())}"
                    )
                    raise ValueError(
                        f"When computing constraint violation, output key {constraint['name']} not found in Task outputs. Available outputs are listed in the 'debug' log level."
                    )

        return constraint_violation

    @staticmethod
    def transform_constraint_violation(constraint_violation):
        """Takes in a matrix of constraint violations and transform it to a vector for each batch sample."""
        constraint_violation = np.maximum(
            constraint_violation, 0
        )  # Set negative values to 0
        constraint_violation = constraint_violation[
            np.nonzero(np.max(constraint_violation, axis=1))
        ]  # Remove constraints that are respected by all samples in the batch
        if constraint_violation.shape[0] == 0:
            return np.zeros(
                constraint_violation.shape[1]
            )  # If all constraints are respected, return a 0 vector with size equal the number of samples in the batch

        sample_mean = np.mean(
            constraint_violation, axis=0
        )  # Vector with samples mean constraint violation
        pounded_constraint_violation = constraint_violation * sample_mean
        function_mean = np.mean(pounded_constraint_violation, axis=1).reshape(
            -1, 1
        )  # Vector with mean constraint violations for each constraint function, weighted by their samples mean
        transformed_constraint_violation = np.sum(
            pounded_constraint_violation / function_mean, axis=0
        )  # Transformed constraint violation
        return transformed_constraint_violation

    def compute_simple_penalization(self, constraint_violation):
        """Computes the penalty for the constraint violation of each sample in the batch using a simple penalization scheme based on provided coefficient"""
        constraint_violation = np.maximum(
            constraint_violation, 0
        )  # Set negative values to 0

        for index_function, constraint in enumerate(self.constraint_list):
            try:
                constraint_violation[index_function, :] *= constraint['coefficient']
            except KeyError:  # pragma: no cover
                logger = get_logger(__name__)
                logger.debug(
                    f"Trying to compute a penalty for constraint {constraint['name']}, no penalization coefficient found in constraint definition"
                )
                raise ValueError(
                    f"When computing constraint violation, coefficient not found for constraint {constraint['name']}."
                )
        return constraint_violation

    @staticmethod
    def compute_adaptive_penalty(tcv, list_of_loss):
        # If all samples are feasible -> the penalty is zero
        if np.all(tcv <= 0):
            return np.zeros(len(list_of_loss))

        # If the best solution is not a feasible solution
        if np.any(tcv <= 0) and tcv[list_of_loss.index(np.min(list_of_loss))] > 0:
            p_min = np.max(
                [
                    -np.min(np.abs(list_of_loss))
                    + np.min(np.where(tcv <= 0, list_of_loss, np.max(list_of_loss))),
                    1,
                ]
            )  # Minimal penalty to be applied - The maximum value between one and the difference between the best and the best feasible solution
        else:
            p_min = np.max(
                [1, np.max(np.abs(list_of_loss))]
            )  # Minimal penalty to be applied

        p_max = (
            p_min + np.max(np.abs(list_of_loss))
        ) * 100  # Maximal penalty to be applied

        tcv_max = np.max(tcv)  # Greatest constraint violation in the batch

        weight_1 = np.log(p_max / p_min) / (tcv_max)
        weight_2 = p_min * np.exp(weight_1)
        penalty = np.where(
            tcv > 0, weight_2 * (np.exp(tcv * weight_1)), 0
        )  # penalty = w2*e^(w1*tcv)
        return penalty

    def compute_penalties(self, constraint_violation, list_of_loss):
        """Takes in a matrix of constraint violations and transform it to a penalty for each batch sample."""

        if self.method == "adaptive_barrier":
            tcv = self.transform_constraint_violation(constraint_violation)
            return self.compute_adaptive_penalty(tcv, list_of_loss)

        elif self.method == "simple_penalization":
            constraint_violation = self.compute_simple_penalization(
                constraint_violation
            )
            penalties = np.sum(constraint_violation, axis=0)
            return penalties

        elif self.method == "relative_penalization":
            constraint_violation = self.compute_simple_penalization(
                constraint_violation
            )
            penalties = np.sum(constraint_violation, axis=0)
            return penalties * np.max([1, np.max(np.abs(list_of_loss))])

        else:  # pragma: no cover
            raise ValueError(
                f"Method {self.method} not available. Available methods are 'adaptive_barrier' and 'simple_penalization'"
            )
