from abc import ABC, abstractmethod


class AbstractKeywordExtractor(ABC):
    """
    Implements an abstract keyword extraction algorithm
    """

    def __init__(self, language, stopwords=None):
        self._language = language
        self._stop_words = stopwords

    @abstractmethod
    def run(self, text):
        """
        Executes the keyword extraction algorithm on the text, the result is a list of keywords.
        Depending on the implementation the results could also contain the rank of the keyword.

        :param text: A string containing the input text for the algorithm
        :return: A list containing the extracted keywords
        """
        pass

    def configuration(self):
        """
        Returns the model configurations
        :return:
        """
        return self.__dict__
