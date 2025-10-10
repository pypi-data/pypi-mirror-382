# Copyright (C) 2021-2025 Cosmo Tech
# This document and all information contained herein is the exclusive property -
# including all intellectual property rights pertaining thereto - of Cosmo Tech.
# Any use, reproduction, translation, broadcasting, transmission, distribution,
# etc., to any person is prohibited unless it has been previously and
# specifically authorized by written means by Cosmo Tech.

from ...utilities.registry import partialclass

from .optimalgorithm import (
    BaseOptimizationAlgorithm,
    OptimizationAlgorithmRegistry,
)

PYMOO_AVAILABLE = True
_pymoo_unavailable_error_message = (
    "This functionality is only available with optional dependency Pymoo. Either install CoMETS with:\n"
    "  - `pip install comets[opt]`, \n"
    "  - `pip install comets[all]`,\n"
    "  - or install Pymoo with `pip install pymoo`."
)

try:
    import numpy as np
    from pymoo.core.problem import Problem
    from pymoo.core.evaluator import Evaluator
    from pymoo.problems.static import StaticProblem
    from pymoo.algorithms.soo.nonconvex.ga import GA
    from pymoo.operators.sampling.rnd import (
        FloatRandomSampling,
        IntegerRandomSampling,
        BinaryRandomSampling,
    )
    from pymoo.core.crossover import Crossover
    from pymoo.core.mutation import Mutation
    from pymoo.core.sampling import Sampling
    from pymoo.operators.crossover.sbx import SBX
    from pymoo.operators.repair.rounding import RoundingRepair
    from pymoo.operators.mutation.pm import PM
    from pymoo.operators.crossover.spx import SPX
    from pymoo.operators.mutation.bitflip import BitflipMutation
except ImportError:  # pragma: no cover
    PYMOO_AVAILABLE = False

    class Sampling:
        pass

    class Crossover:
        pass

    class Mutation:
        pass


class CustomInitializer(Sampling):
    """
    This class represents a custom initializer for the population of a genetic algorithm.

    Args:
        initialization_function : Function taking as input pop_size (int), the size of the population,
            and returning a numpy array (of ints or floats) of shape (pop_size, size) containing the initial population.,
            where size is the size of the decision variable.
    """

    def __init__(self, initialization_function):
        if not PYMOO_AVAILABLE:
            raise ImportError(_pymoo_unavailable_error_message)

        self.initialization_function = initialization_function
        super().__init__()

    def _do(self, problem, n_samples, **kwargs):
        X = self.initialization_function(n_samples)
        return X


class CustomMutation(Mutation):
    """
    This class represents a custom mutation for the population of a genetic algorithm.

    Args:
        mutation_function : Function taking as input the population given as a numpy array of shape (pop_size, size),
            where popsize is the number of individuals in the population, and size is the size of the decision variable.
            It should return an array of the same shape where some or all the individuals have been mutated.
    """

    def __init__(self, mutation_function):
        if not PYMOO_AVAILABLE:  # pragma: no cover
            raise ImportError(_pymoo_unavailable_error_message)

        self.mutation_function = mutation_function
        super().__init__()

    def _do(self, problem, X, **kwargs):
        Y = self.mutation_function(X)
        return Y


class CustomCrossover(Crossover):
    """
    This class represents a custom crossover for the population of a genetic algorithm.

    Args:

        crossover_function : Function taking as input a numpy array of shape (n_matings, n_parents, size),
            where for each mating the array of shape (n_parents, size) contains the parents used in the crossover (size is the size of the decision variable).
            The function should return a numpy array of shape (n_matings, n_offsprings, size),
            where for each mating the array of shape (n_offsprings, size) contains the offsprings produced by the crossover.
        n_parents (int): Number of parents to be used in each mating. Defaults to 2, as most crossovers consist of a mating of two parents,
            to produce one or several offsprings.
        n_offsprings (int): Number of offsprings to be produced by each mating.
            Defaults to 2, as most crossovers produce 2 offsprings from 2 parents (an example is the one-point crossover), but some crossovers may produce only one offspring for each mating.
    """

    def __init__(self, crossover_function, n_parents=2, n_offsprings=2) -> None:
        if not PYMOO_AVAILABLE:  # pragma: no cover
            raise ImportError(_pymoo_unavailable_error_message)

        self.crossover_function = crossover_function
        super().__init__(n_parents=n_parents, n_offsprings=n_offsprings)

    def _do(self, problem, X, **kwargs):
        X_ = np.copy(X)
        X_ = np.swapaxes(X_, 0, 1)
        Y = self.crossover_function(X_)
        Y = np.swapaxes(Y, 0, 1)
        return Y


@OptimizationAlgorithmRegistry.register_with_info(
    SupportsParallelization=True,
    RequiresMaxEvaluations=False,
    Supports1D=True,
    HasIterations=True,
)
class configGA(BaseOptimizationAlgorithm):
    """
    Configurable genetic algorithm where the user can define his own initial population, mutation and crossover functions.

    Args:
        space : The space of the decision variables over which to optimize.
        batch_size (int): Number of task evaluations which will be run in parallel.
        max_evaluations (int): Maximum number of times the task should been evaluated.
        name (string, optional): Name of the optimization algorithm to use.
        algorithm_options (dict,optional): Additional keyword arguments passed to the algorithm. May include:

            * initializer: CustomInitializer object (or Pymoo Sampling operator) ;
            * mutation: CustomMutation object (or Pymoo Mutation operator) ;
            * crossover: CustomCrossover object (or Pymoo Crossover operator).

    """

    def __init__(
        self, space, max_evaluations, batch_size, binary=False, **algorithm_options
    ):
        if not PYMOO_AVAILABLE:
            raise ImportError(
                "This algorithm (binaryGA/configGA) is only available with optional dependency Pymoo. Either install CoMETS with:\n"
                "  - `pip install comets[opt]`, \n"
                "  - `pip install comets[all]`,\n"
                "  - or install Pymoo with `pip install pymoo`."
            )

        self.space = space
        self.batch_size = batch_size

        # Note that unlike the class PymooOptimizationAlgorithm, this class doesn't use a standardized space.
        if len(space.list_of_variables) != 1:  # pragma: no cover
            raise ValueError(
                "This algorithm only supports optimization problems with one variable (eventually with size>1)"
            )
        self.parameter = space.list_of_variables[0]
        if self.parameter.type == "int":
            self.type = int
        elif self.parameter.type == "float":
            self.type = float
        else:  # pragma: no cover
            raise ValueError("This algorithm only supports integer or float variables")

        self.dimension = self.parameter.dimension

        self.problem = Problem(
            n_var=self.dimension,
            n_obj=1,
            n_constr=0,
            xl=self.parameter.bounds[0],
            xu=self.parameter.bounds[1],
        )

        if binary:
            self.initializer = BinaryRandomSampling()
            self.crossover = SPX()
            self.mutation = BitflipMutation()
        else:
            if "initializer" in algorithm_options:
                self.initializer = algorithm_options["initializer"]
            else:
                if self.parameter.type == "int":
                    self.initializer = IntegerRandomSampling()
                elif self.parameter.type == "float":
                    self.initializer = FloatRandomSampling()

            if "crossover" in algorithm_options:
                self.crossover = algorithm_options["crossover"]
            else:
                if self.parameter.type == "int":
                    self.crossover = SBX(repair=RoundingRepair())
                elif self.parameter.type == "float":
                    self.crossover = SBX()

            if "mutation" in algorithm_options:
                self.mutation = algorithm_options["mutation"]
            else:
                if self.parameter.type == "int":
                    self.mutation = PM(repair=RoundingRepair())
                elif self.parameter.type == "float":
                    self.mutation = PM()

        self.pymoo_algorithm = GA(
            pop_size=batch_size,
            sampling=self.initializer,
            crossover=self.crossover,
            mutation=self.mutation,
            eliminate_duplicates=False,
        )

        self.pymoo_algorithm.setup(
            self.problem, termination=('n_eval', max_evaluations), verbose=False
        )

    def ask(self):
        """
        Returns batch_size samples in the form of a list of ParameterSets
        """
        self.pop = self.pymoo_algorithm.ask()  # returns a list of numpy arrays
        array_population = np.array(self.pop.get("X"), dtype=self.type)
        return [{self.parameter.name: i} for i in array_population]

    def tell(self, list_of_samples, list_of_loss):
        """
        Receives batch_size samples in the form of a list of ParameterSets (list_of_samples) and a list of values of the objective function evaluated on these samples.
        Updates the optimization algorithm.
        """
        static = StaticProblem(self.problem, F=np.array(list_of_loss))
        Evaluator().eval(static, self.pop)
        self.pymoo_algorithm.tell(infills=self.pop)

    def provide_optimal_solution(self):
        """
        Returns the optimal decision variables, in the form of a ParameterSet
        """
        return {
            self.parameter.name: list(
                np.array(self.pymoo_algorithm.result().X, dtype=self.type)
            )
        }


OptimizationAlgorithmRegistry["binaryGA"] = partialclass(configGA, binary=True)
OptimizationAlgorithmRegistry.information.setdefault(
    "binaryGA",
    {
        'SupportsParallelization': True,
        'RequiresMaxEvaluations': False,
        'HasIterations': True,
        'Supports1D': True,
    },
)
