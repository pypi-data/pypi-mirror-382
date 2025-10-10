from .optimalgorithm import (
    BaseOptimizationAlgorithm,
    OptimizationAlgorithmRegistry,
)


# Make sure CoMETS doesn't give an error if the library is not installed and the algorithm is not used
SKOPT_IMPORTED = False
try:
    import skopt
    from skopt.space import Real, Categorical

    SKOPT_IMPORTED = True
except ModuleNotFoundError:  # pragma: no cover
    pass


# @OptimizationAlgorithmRegistry.register_with_info(
#     SupportsParallelization=True,
#     RequiresMaxEvaluations=False,
#     Supports1D=True,
#     HasIterations=True,
# )
class BayesianOptimizer(BaseOptimizationAlgorithm):
    '''Bayesian optimization algorithm from scikit-optimize library

    Args:
        space : The space of the decision variables over which to optimize.
        batch_size (int): Number of task evaluations which will be run in one batch.
        max_evaluations (int): Maximum number of times the task should been evaluated.
        algorithm_options (dict,optional): Additional keyword arguments passed to skopt.Optimizer. https://scikit-optimize.github.io/stable/modules/generated/skopt.Optimizer.html. May include:

            * 'base_estimator' : "GP", "RF", "ET", "GBRT" or sklearn regressor, default: "GP"
            * 'n_initial_points' : Number of evaluations of func with initialization points before approximating it with base_estimator, default: 10
            * 'n_jobs' : The number of jobs to run in parallel in the base_estimator. If -1, then the number of jobs is set to the number of cores, default: -1
            * 'acq_func' : Function to minimize over the posterior distribution, default : 'gp_hedge'
            * 'acq_optimizer' : Method to minimize the acquisition function, default: 'sampling'
            * 'acq_func_kwargs' : Additional arguments to be passed to the acquisition function, find the arguments for each acquitions function in https://scikit-optimize.github.io/stable/modules/classes.html#module-skopt.acquisition
            * 'model_queue_size' : Keeps list of models only as long as the argument given, default : None

    '''

    def __init__(self, space, batch_size, **algorithm_options):
        # Dictionary that contains the default values for the Optimizer
        default_dict = {
            'base_estimator': 'GP',
            'n_initial_points': 10,
            'n_jobs': -1,
            'acq_func': "gp_hedge",
            'acq_optimizer': 'sampling',
            'acq_func_kwargs': {},
            'model_queue_size': 1,
        }

        arguments_dict = {}
        for elt in default_dict.keys():
            arguments_dict[elt] = algorithm_options.get(elt, default_dict[elt])

        self.counter = 0
        self.space = space
        self.batch_size = batch_size

        self.dimensions = self.map_space_to_skopt(self.space)

        if not SKOPT_IMPORTED:  # pragma: no cover
            raise ValueError(
                "Please install library scikit-optimize to use this algorithm"
            )

        self.bayesian_optimizer = skopt.Optimizer(
            dimensions=self.dimensions, **arguments_dict
        )

    def _decode_skopt(self, x):
        x_values = {}
        # We create a dict of ParameterSet that would be understood by CoMETS
        start_list = 0
        param_counter = 0
        for parameter in self.space.list_of_variables:
            if parameter.size is not None:
                size = parameter.size
                end_list = start_list + size
                x_values[parameter.name] = x[start_list:end_list]
                start_list = end_list
                param_counter += size
                if parameter.type == 'categorical':
                    index_list = [int(i) for i in x_values[parameter.name]]

                    # Decoding the previously encoded list of parameters in order to get the real value returned by ask()
                    x_values[parameter.name] = [parameter.values[i] for i in index_list]

            else:
                x_values[parameter.name] = x[param_counter]

                if parameter.type == 'categorical':
                    # Same decoder
                    x_values[parameter.name] = parameter.values[
                        int(x_values[parameter.name])
                    ]

                param_counter += 1
                start_list += 1

        return x_values

    def map_space_to_skopt(self, space):
        """
        Map a space of decision variables from CoMETS format to skopt format

        Args:
            space : The space of the decision variables over which to optimize.
        Returns:
            parameter_list: list of seach space dimensions
        """
        parameter_list = []
        for parameter in space.list_of_variables:
            if parameter.size is not None:
                size = parameter.size
            else:
                size = parameter.dimension

            if parameter.type == 'int':
                param_value = [
                    (parameter.bounds[0], parameter.bounds[1]) for i in range(size)
                ]

            if parameter.type == 'float':
                param_value = [
                    Real(parameter.bounds[0], parameter.bounds[1]) for i in range(size)
                ]

            if parameter.type == 'categorical':
                list = [str(i) for i in range(len(parameter.values))]
                param_value = [Categorical(list) for i in range(size)]
                # We encode the parameter values list into a list of indexes if it's categorical in order to bypass a problem with skopt
            parameter_list += param_value

        return parameter_list

    def ask(self):
        """
        Return a list of samples points to evaluate

        Returns:
            list of ParameterSet: list of ParameterSet on which the task should be evaluated
        """
        self.counter += 1

        list_of_x = []
        list_of_samples = []
        if self.batch_size == 1:
            x_list = [self.bayesian_optimizer.ask()]
        else:
            x_list = self.bayesian_optimizer.ask(self.batch_size)
        for x in x_list:
            x_values = self._decode_skopt(x)

            list_of_x.append(x)
            list_of_samples.append(x_values)

        self.lastask = list_of_x
        return list_of_samples

    def tell(self, list_of_samples, list_of_loss):
        """
        Return a list of samples points to evaluate

        Args:
            list_of_samples  (list of ParameterSet): list of ParameterSet on which the task should be evaluated
            list_of_loss : list of values of the objective function evaluated on list_of_samples
        """
        self.bayesian_optimizer.tell(self.lastask, list_of_loss)

    def provide_optimal_solution(self):
        """
        Return the optimal decision variables found so far

        Returns:
            ParameterSet: Optimal decision variables
        """
        # Note that this method uses the same decoders and encoders used in the ask method implemented above

        x = self.bayesian_optimizer.get_result()['x']
        x_values = self._decode_skopt(x)

        return x_values
