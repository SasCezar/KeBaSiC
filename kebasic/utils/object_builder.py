from abc import ABC
from importlib import import_module


class ObjectBuilder(ABC):

    def build(self, algorithm, algorithm_parameters):
        algorithm_name, algorithm_object = self._import_class(algorithm)
        algorithm_instance = algorithm_object(**algorithm_parameters)
        return algorithm_instance, algorithm_name

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
