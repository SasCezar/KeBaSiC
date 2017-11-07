from abc import ABC, abstractmethod


class AbstractResultWriter(ABC):
    def __init__(self, path):
        self._path = path

    @abstractmethod
    def write(self, filename, content):
        pass


class JSONResultWriter(AbstractResultWriter):
    def write(self, filename, content):
        pass


class CSVResultWriter(AbstractResultWriter):
    def write(self, filename, content):
        pass
