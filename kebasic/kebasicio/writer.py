from abc import ABC, abstractmethod


class AbstractWriter(ABC):
    def __init__(self, path):
        self._path = path

    def __enter__(self):
        self._file = open(self._path, "wt", encoding="utf8", newline='')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._file.close()

    def write(self, content):
        self._write(content)

    @abstractmethod
    def _write(self, content):
        pass
