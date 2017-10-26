from abc import abstractmethod

from kebasic.feature.featureextractor import AbstractFeatureExtractor


class AbstractKeywordExtractor(AbstractFeatureExtractor):
    """
    Implements an abstract keyword extraction algorithm
    """

    def __init__(self, language, stopwords=None):
        self._language = language
        self._stop_words = stopwords

    @abstractmethod
    def run(self, text):
        pass