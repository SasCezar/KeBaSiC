import logging

from kebasic.execution.executor import AbstractExecution


class FeatureExtractionExecution(AbstractExecution):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"extractor_algorithms", "extractor_parameters"}
        self.feature_extractors = []
        self._initialize()
        self._build()

    def _build(self):
        logging.info("Loading KE modules ...")
        for ke_algorithm in self.extractor_algorithms:
            logging.debug("Loading {}".format(ke_algorithm))
            ke_name, ke_class = self._import_class(ke_algorithm)
            model_parameters = self.extractor_parameters.get(ke_algorithm, {})
            self.feature_extractors.append((ke_name, ke_class(**model_parameters)))

    def execute(self, webpages):
        result = []
        for webpage in webpages:
            logging.info("Extracting features from site: {}".format(webpage.url))
            if not webpage.text.strip():
                print("Empty text webpage: {}".format(webpage.url))
                continue
            keywords = self.extract_feature(webpage.text)
            keywords['url'] = webpage.url
            keywords['site_keywords'] = webpage.meta_keywords
            result.append(keywords)

        return result

    def extract_feature(self, webpage):
        result = {}
        for ke_algorithm in self.feature_extractors:
            ke_object = ke_algorithm[1]
            keywords = ke_object.run(webpage)
            result[ke_algorithm[0]] = keywords

        return result
