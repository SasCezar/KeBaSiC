import logging
from abc import ABC, abstractmethod
from utils.object_builder import ObjectBuilder


class AbstractExecutor(ABC):
    """
    Defines an abstract execution class. Implements the common function that are needed to perform a generic computation
    """

    def __init__(self, configs):
        """
        Constructor of the class. Accepts a dictionary of configurations that will be used to define the workflow of the
        class.

        :param configs:
        """
        self._configs = configs
        self._allowed = set()  # all these keys will be initialized as class attributes
        self.algorithms = []
        self.parameters = {}
        self.callables = []
        self.object_builder = ObjectBuilder()

    @abstractmethod
    def run(self):
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
            algorithm_parameters = self.parameters.get(algorithm, {})
            algorithm_instance, algorithm_name = self.object_builder.build(algorithm, algorithm_parameters)
            self.callables.append((algorithm_name, algorithm_instance))


    def _initialize(self):
        """
        Set up the class defining the attributes
        :return:
        """
        # initialize all allowed keys to false
        for key in self._allowed:
            self.__setattr__(key, False)

        for key, value in self._configs.items():
            self.__setattr__(key, value) if key in self._allowed else None

        return self


class AbstractPipeline(AbstractExecutor):
    """
    Defines an abstract execution class for an item.
    """

    def run(self):
        pass

    @abstractmethod
    def process(self, item):
        pass
