from abc import ABC, abstractmethod


class AbstractTextProcessor(ABC):
    @abstractmethod
    def run(self, text):
        pass
