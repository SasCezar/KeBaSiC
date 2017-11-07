import logging

from kebasic.execution.executor import AbstractExecution


class FeatureExtractionExecution(AbstractExecution):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"extractor_algorithms", "extractor_parameters"}
        self._initialize()
        self.algorithms = self.extractor_algorithms
        self.parameters = self.extractor_parameters if self.extractor_parameters else {}
        self._build()

    def execute(self, webpages):
        result = []
        for webpage in webpages:
            logging.info("Extracting features from site: {}".format(webpage.url))
            if not webpage.text:
                logging.info("Empty text webpage: {}".format(webpage.url))
                continue
            features = self.extract_features(webpage.text)
            features['url'] = webpage.url
            features['site_keywords'] = webpage.meta_keywords
            result.append(features)

        return result

    def extract_features(self, webpage):
        result = {}
        for name, callable_object in self.callables:
            feature = callable_object.run(webpage)
            result[name] = feature

        return result


class TextCleanerExecution(AbstractExecution):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"preprocessing_algorithms", "preprocessing_parameters"}
        self._initialize()
        self.algorithms = self.preprocessing_algorithms
        self.parameters = self.preprocessing_parameters if self.preprocessing_parameters else {}
        self._build()

    def execute(self, webpages):
        result = []
        for webpage in webpages:
            logging.info("Cleaning: {}".format(webpage.url))
            webpage.text = self.clean_text(webpage.text)
            result.append(webpage)
        return result

    def clean_text(self, text):
        for name, callable_object in self.callables:
            text = callable_object.run(text)
        return text
