import logging
from collections import OrderedDict

from executions.executor import AbstractPipeline
from feature.sitekeywords import SiteKeywordsExtractor


class FeatureExtractionPipeline(AbstractPipeline):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"extractor_algorithms", "extractor_parameters"}
        self._initialize()
        self.algorithms = self.extractor_algorithms
        self.parameters = self.extractor_parameters if self.extractor_parameters else {}
        self.site_keywords_extractor = SiteKeywordsExtractor(**config['SiteKeywordsExtractor'])
        self._build()

    def process(self, webpage):
        result = OrderedDict()
        logging.info("Extracting features from site: {}".format(webpage.url))
        if not webpage.text:
            logging.info("Empty text webpage: {}".format(webpage.url))
            return False  # TODO Check if better raise exception
        result['url'] = webpage.url
        features = {}
        for name, callable_object in self.callables:
            logging.debug("Running {}".format(name))
            feature = callable_object.run(webpage.text)
            features[name] = feature
            logging.debug("Completed {}".format(name))

        features['site_keywords'] = self.site_keywords_extractor.run(webpage.meta_keywords)
        result['keywords'] = features

        return result


class TextCleaningPipeline(AbstractPipeline):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"preprocessing_algorithms", "preprocessing_parameters"}
        self._initialize()
        self.algorithms = self.preprocessing_algorithms
        self.parameters = self.preprocessing_parameters if self.preprocessing_parameters else {}
        self._build()

    def process(self, text):
        for _, callable_object in self.callables:
            text = callable_object.run(text)
        return text
