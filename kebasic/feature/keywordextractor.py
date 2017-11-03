from abc import ABC, abstractmethod

import nltk


def load_stop_words(stopwords):
    """
    Utility function to load stop words from a file and return as a list of words

    :param stopwords: Path and file name of a file containing stop words.
    :return list: A list of stop words.
    """

    if type(stopwords) is list:
        return stopwords

    stop_words = []
    for line in open(stopwords, "rt", encoding="utf8"):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word.strip())
    return stop_words


class AbstractKeywordExtractor(ABC):
    """
    Implements an abstract keyword extraction algorithm
    """

    def __init__(self, language, stopwords=None):
        self._language = language

        self._stopwords = load_stop_words(stopwords) if stopwords else nltk.corpus.stopwords.words(language)

    @abstractmethod
    def run(self, text):
        """
        Executes the feature extraction algorithm on the text, the result is a list of keywords.

        :param text: A string containing the input text for the algorithm
        :return: The features
        """
        pass

    def _filter(self, keywords):
        return [(keyword, weight) for keyword, weight in keywords if keyword not in self._stopwords]

    @staticmethod
    def _sort(keywords):
        return sorted(keywords, key=lambda x: (-x[1], x[0]))

    def configuration(self):
        """
        Returns the model configurations
        :return:
        """
        return self.__dict__

    @abstractmethod
    def run(self, text):
        pass
