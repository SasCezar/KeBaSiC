import csv
import logging
from abc import ABC, abstractmethod

from domain.webpagebuilder import WebPageBuilder


class WebPageDAO(ABC):
    @abstractmethod
    def load_webpages(self):
        pass


class CSVWebPageDAO(WebPageDAO):
    def __init__(self, path):
        self.file = path
        self.builder = WebPageBuilder()

    def _load_webpages(self):
        with open(self.file, "rt", encoding="utf-8-sig") as inf:
            reader = csv.reader(inf)
            for line in reader:
                url = line[0]
                html = line[1] if len(line) > 1 else None
                try:
                    webpage = self.builder.build(url, html)
                    yield webpage
                except Exception as e:
                    logging.error(e)
                    continue

    def load_webpages(self):
        webpages = list(self._load_webpages())
        return webpages
