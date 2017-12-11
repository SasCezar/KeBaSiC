import logging
from collections import OrderedDict
from operator import itemgetter

from feature.sitekeywords import SiteKeywordsExtractor
from kebasic.execution.executor import AbstractExecution


class FeatureExtractionExecution(AbstractExecution):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"extractor_algorithms", "extractor_parameters"}
        self._initialize()
        self.algorithms = self.extractor_algorithms
        self.parameters = self.extractor_parameters if self.extractor_parameters else {}
        self.site_keywords_extractor = SiteKeywordsExtractor(**config['SiteKeywordsExtractor'])
        self._build()

    def execute(self, webpages):
        results = []
        for webpage in webpages:
            result = OrderedDict()
            logging.info("Extracting features from site: {}".format(webpage.url))
            if not webpage.text:
                logging.info("Empty text webpage: {}".format(webpage.url))
                continue
            result['url'] = webpage.url
            features = self._extract_features(webpage.text)
            scores = features[self.site_keywords_extractor.algo_score]
            site_keyword_score = max(scores, key=itemgetter(1))[1] if scores else 1
            features['site_keywords'] = self.site_keywords_extractor.run(webpage.meta_keywords,
                                                                         score=site_keyword_score)
            result['keywords'] = features
            results.append(result)

        return results

    def _extract_features(self, webpage):
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
            webpage.text = self._clean_text(webpage.text)
            result.append(webpage)
        return result

    def _clean_text(self, text):
        for name, callable_object in self.callables:
            text = callable_object.run(text)
        return text
