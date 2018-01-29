from abc import ABC, abstractmethod


class AbstractReader(ABC):
    def __init__(self):
        self._file = None

    def read(self):
        self._read()

    @abstractmethod
    def _read(self):
        pass
