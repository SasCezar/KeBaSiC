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
        for extractor_algorithm in self.callables:
            extractor = extractor_algorithm[1]
            feature = extractor.run(webpage)
            result[extractor_algorithm[0]] = feature

        return result


class TextCleaningExecution(AbstractExecution):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"cleaner_algorithms", "cleaner_parameters"}
        self._initialize()
        self._cleaners = []
        self._build()

    def execute(self, webpages):
        pass
