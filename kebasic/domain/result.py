from abc import ABC


class AbstractResult(ABC):
    def __init__(self):
        pass


class KeywordsExtractionResults(AbstractResult):
    def __init__(self, url, result):
        super().__init__()
        self._url = url
