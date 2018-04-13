from abc import ABC, abstractmethod


class AbstractClassifier(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def classify(self, text):
        pass
