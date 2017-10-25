import logging

from kebasic.execution.executor import AbstractExecution


class BasicExecution(AbstractExecution):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"language", "resources", "stopwords", "ke_algorithms", "ke_parameters"}
        self.ke = []
        self._initialize()

    def execute(self):
        logging.info("Loading KE modules ...")
        for ke_algorithm in self.ke_algorithms:
            logging.debug("Loading {}".format(ke_algorithm))
            ke_name, ke_class = self._import_classes(ke_algorithm)
            model_parameters = self.ke_parameters[ke_algorithm]
            self.ke += (ke_name, ke_class(**model_parameters))

        logging.info("KE modules loaded")
        #  logging.info("Loading classifiers ...")
        #  logging.info("Classifiers loaded ...")
