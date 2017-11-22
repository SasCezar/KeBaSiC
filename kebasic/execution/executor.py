import logging
from abc import ABC, abstractmethod
from importlib import import_module


class AbstractExecution(ABC):
    """
    Defines an abstract execution class. Implements the common function that are needed to perform a generic computation
    """

    def __init__(self, config):
        """
        Constructor of the class. Accepts a dictionary of configurations that will be used to define the workflow of the
        class.

        :param config:
        """
        self._config = config
        self._allowed = set()  # all those keys will be initialized as class attributes
        self.algorithms = []
        self.parameters = {}
        self.callables = []

    @abstractmethod
    def execute(self, webpages):
        pass

    def get_config(self):
        configs = {}
        for name, callable_object in self.callables:
            object_config = callable_object.configuration()

            configs[name] = object_config

        return configs

    def _build(self):
        """
        Builds the objects that the class will use
        :return:
        """
        logging.info("Loading modules...")
        for algorithm in self.algorithms:
            logging.info("Loading {}".format(algorithm))
            algorithm_name, algorithm_object = self._import_class(algorithm)
            algorithm_parameters = self.parameters.get(algorithm, {})
            self.callables.append((algorithm_name, algorithm_object(**algorithm_parameters)))

    def _initialize(self):
        """
        Set up the class defining the attributes
        :return:
        """
        # initialize all allowed keys to false
        for key in self._allowed:
            self.__setattr__(key, False)

        for key, value in self._config.items():
            self.__setattr__(key, value) if key in self._allowed else None

        return self

    @staticmethod
    def _import_class(module):
        """
        Imports the class from the specified module needed for the execution
        :param module:
        :return:
        """
        module_name = ".".join(module.split('.')[:-1])
        my_module = import_module("{}".format(module_name))
        class_name = module.split('.')[-1]
        model = getattr(my_module, class_name)
        return class_name, model
