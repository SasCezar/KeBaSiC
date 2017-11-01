from abc import abstractmethod

from kebasic.feature.featureextractor import AbstractFeatureExtractor


def load_stop_words(stop_word_file):
    """
    Utility function to load stop words from a file and return as a list of words

    :param stop_word_file: Path and file name of a file containing stop words.
    :return list: A list of stop words.
    """
    stop_words = []
    for line in open(stop_word_file, "rt", encoding="utf8"):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word.strip())
    return stop_words


class AbstractKeywordExtractor(AbstractFeatureExtractor):
    """
    Implements an abstract keyword extraction algorithm
    """

    def __init__(self, language, stopwords=None):
        self._language = language

        self._stopwords = load_stop_words(stopwords) if stopwords else None

    @abstractmethod
    def run(self, text):
        pass
