from abc import ABC, abstractmethod


def load_stop_words(stop_word_file):
    """
    Utility function to load stop words from a file and return as a list of words

    :param stop_word_file: Path and file name of a file containing stop words.
    :return list: A list of stop words.
    """
    stop_words = []
    for line in open(stop_word_file, "r"):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word)
    return stop_words


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

    @abstractmethod
    def configuration(self):
        """
        Returns the model configurations
        :return:
        """
        pass
