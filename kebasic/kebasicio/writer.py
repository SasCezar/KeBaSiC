from abc import ABC, abstractmethod


class AbstractWriter(ABC):
    def __init__(self, path):
        self._path = path

    def __enter__(self):
        if self._path:
            self._file = open(self._path, "wt", encoding="utf8", newline='')
        else:
            self._file = None
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._path:
            self._file.close()

    def write(self, content):
        self._write(content)

    @abstractmethod
    def _write(self, content):
        pass


class StdOutFileWriter(AbstractWriter):
    def __init__(self, path, print=True):
        super().__init__(path)
        self.stdout = print

    def write(self, content):
        if self.stdout:
            print(content)
        if self._file:
            self._write(content)

    def _write(self, content):
        self._file.write(content + "\n")
