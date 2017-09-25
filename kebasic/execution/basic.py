import logging
from importlib import import_module

from kebasic.execution.executor import AbstractExecutor


class BasicExecution(AbstractExecutor):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"language", "resources", "stopwords", "ke_algorithms", "ke_parameters"}
        self._initialize()

    def execute(self):
        logging.info("Loading KE modules ...")
        # TODO: Extract method
        for ke_algorithm in self.ke_algorithms:
            attribute_name = ke_algorithm.lower()
            logging.debug("Loading {}".format(attribute_name))
            my_module = import_module("keyword_extraction.{}".format(attribute_name))
            model = getattr(my_module, ke_algorithm)
            model_parameters = self.ke_parameters[ke_algorithm]
            self.__setattr__(attribute_name, model(**model_parameters))

        logging.info("KE modules loaded")
        #  logging.info("Loading classifiers ...")
        #  logging.info("Classifiers loaded ...")
