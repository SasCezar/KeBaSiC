from abc import ABC, abstractmethod
from importlib import import_module


class Context(object):
    def __init__(self, strategy):
        self._strategy = strategy

    def execute(self):
        self._strategy.execute()


class AbstractExecutor(ABC):
    """
    Defines an abstract execution class. Implements the common function that are needed to perform a generic computation
    """
    def __init__(self, config):
        """
        Constructor of the class. Accepts a dicionary of configurations that will be used to define the workflow of the
        class.

        :param config:
        """
        self._config = config
        self._allowed = set()  # all those keys will be initialized as class attributes

    @abstractmethod
    def execute(self):
        pass

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

    def _import_classes(self, package):
        """
        Imports the packages needed for the execution
        :param package:
        :return:
        """
        module_name = ".".join(package.split('.')[:-1])
        my_module = import_module("{}".format(module_name))
        class_name = package.split('.')[-1]
        model = getattr(my_module, class_name)
        return class_name, model
