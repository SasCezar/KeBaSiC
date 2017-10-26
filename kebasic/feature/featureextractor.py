from abc import ABC, abstractmethod


class AbstractFeatureExtractor(ABC):
    @abstractmethod
    def run(self, text):
        """
        Executes the feature extraction algorithm on the text, the result is a list of keywords.

        :param text: A string containing the input text for the algorithm
        :return: The features
        """
        pass

    def configuration(self):
        """
        Returns the model configurations
        :return:
        """
        return self.__dict__
