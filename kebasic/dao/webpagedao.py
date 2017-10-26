import csv
from abc import ABC, abstractmethod

from kebasic.domain.webpage import WebPage


class WebPageDAO(ABC):
    @abstractmethod
    def load_webpages(self):
        pass


class CSVWebPageDAO(WebPageDAO):
    def __init__(self, path):
        self.file = path

    def _load_webpages(self):
        with open(self.file, "rt", encoding="utf-8-sig") as inf:
            reader = csv.reader(inf)
            for line in reader:
                url = line[0]
                html = line[1] if len(line) > 1 else None
                webpage = WebPage(url=url, html=html)
                yield webpage

    def load_webpages(self):
        webpages = list(self._load_webpages())
        return webpages
