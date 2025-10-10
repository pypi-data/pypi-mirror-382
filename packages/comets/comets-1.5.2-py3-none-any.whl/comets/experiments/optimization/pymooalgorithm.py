# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...utilities.registry import partialclass
from ...utilities import get_logger

from .optimalgorithm import (
    BaseOptimizationAlgorithm,
    OptimizationAlgorithmRegistry,
)
from .space_optim import StandardizedSpace

import numpy as np

PYMOO_AVAILABLE = True
try:
    from pymoo.core.termination import NoTermination
    from pymoo.core.problem import Problem
    from pymoo.core.evaluator import Evaluator
    from pymoo.problems.static import StaticProblem
    from pymoo.algorithms.soo.nonconvex.de import DE
    from pymoo.algorithms.soo.nonconvex.cmaes import CMAES
    from pymoo.algorithms.soo.nonconvex.es import ES
    from pymoo.algorithms.soo.nonconvex.sres import SRES
    from pymoo.algorithms.soo.nonconvex.isres import ISRES
    from pymoo.algorithms.soo.nonconvex.ga import GA
except ImportError:  # pragma: no cover
    PYMOO_AVAILABLE = False


class PymooOptimizationAlgorithm(BaseOptimizationAlgorithm):
    """
    Optimization algorithm from Pymoo library

    Args:
        space : The space of the decision variables over which to optimize.
        batch_size (int): Number of task evaluations which will be run in parallel.
        max_evaluations (int): Maximum number of times the task should been evaluated.
        name (string, optional): Name of the optimization algorithm to use.
        algorithm_options (dict,optional): Additional keyword arguments passed to the algorithm. See the documentation for explanation of different arguments.
    """

    def __init__(
        self,
        space,
        max_evaluations,
        batch_size,
        algorithm_name='DE',
        **algorithm_options,
    ):
        if not PYMOO_AVAILABLE:
            raise ImportError(
                f"This algorithm ({algorithm_name}) is only available with optional dependency Pymoo. Either install CoMETS with:\n"
                f"  - `pip install comets[opt]`, \n"
                f"  - `pip install comets[all]`,\n"
                f"  - or install Pymoo with `pip install pymoo`."
            )

        if batch_size < 2:  # pragma: no cover
            logger = get_logger(__name__)
            logger.warning(
                "This algorithm requires a batch size of at least 2, batch sized used by the algorithm is changed to 2, note that this doesn't change the attribute batch_size of the experiment"
            )
            batch_size = 2

        self.space = space
        self.batch_size = batch_size
        self.standardized_space = StandardizedSpace(space)
        self.dimension = self.standardized_space.dimension
        self.problem = Problem(
            n_var=self.dimension,
            n_obj=1,
            n_constr=0,
            xl=np.zeros(self.dimension),
            xu=np.ones(self.dimension),
        )

        if algorithm_name == "DE":
            self.pymoo_algorithm = DE(pop_size=batch_size, **algorithm_options)
        elif algorithm_name == "CMAES":
            algorithm_options.update(
                {"tolflatfitness": 1e14, "tolfunhist": 0, "tolfun": 0, "tolx": 0}
            )
            self.pymoo_algorithm = CMAES(
                popsize=batch_size, **algorithm_options
            )  # Note the different syntax of popsize compared to other algorithms
        elif algorithm_name == "ES":
            self.pymoo_algorithm = ES(n_offsprings=batch_size, **algorithm_options)
        elif algorithm_name == "GA":
            self.pymoo_algorithm = GA(
                pop_size=batch_size, eliminate_duplicates=False, **algorithm_options
            )
        elif algorithm_name == "SRES":
            self.pymoo_algorithm = SRES(n_offsprings=batch_size, **algorithm_options)
        elif algorithm_name == "ISRES":
            self.pymoo_algorithm = ISRES(n_offsprings=batch_size, **algorithm_options)
        else:  # pragma: no cover
            raise ValueError("Unsupported Pymoo algorithm : " + algorithm_name)

        # let the algorithm object never terminate and let the stopping criteria control it
        self.pymoo_algorithm.setup(
            self.problem, termination=NoTermination(), verbose=False
        )

    def ask(self):
        """
        Returns batch_size samples in the form of a list of ParameterSets
        """
        self.population = (
            self.pymoo_algorithm.ask()
        )  # returns a Pymoo population object
        return self.standardized_space.map_to_original_space(
            np.array(self.population.get("X"))
        )

    def tell(self, list_of_samples, list_of_loss):
        """
        Receives batch_size samples in the form of a list of ParameterSets (list_of_samples) and a list of values of the objective function evaluated on these samples.
        Updates the optimization algorithm.
        """
        static = StaticProblem(self.problem, F=np.array(list_of_loss))
        Evaluator().eval(static, self.population)
        self.pymoo_algorithm.tell(infills=self.population)

    def provide_optimal_solution(self):
        """
        Returns the optimal decision variables, in the form of a ParameterSet
        """
        return self.standardized_space.map_to_original_space(
            self.pymoo_algorithm.result().X
        )


for algo_name in ["DE", "CMAES", "ES", "GA", "SRES", "ISRES"]:
    OptimizationAlgorithmRegistry[
        "config" + algo_name if algo_name in ["DE", "CMAES", "ES"] else algo_name
    ] = partialclass(PymooOptimizationAlgorithm, algorithm_name=algo_name)
    OptimizationAlgorithmRegistry.information.setdefault(
        "config" + algo_name if algo_name in ["DE", "CMAES", "ES"] else algo_name,
        {
            'SupportsParallelization': True,
            'RequiresMaxEvaluations': False,
            'HasIterations': True,
            'Supports1D': True if algo_name != "CMAES" else False,
        },
    )
