import csv
import json
import logging
from abc import ABC, abstractmethod

from mongoengine import *

from datasources.mongoobjects import WebPage
from domain.webpagebuilder import WebPageBuilder

connect('kebasic')


class WebPageReader(ABC):
    def __init__(self, path):
        self._path = path
        self._builder = WebPageBuilder()

    def load_webpages(self):
        return self._load_webpages()

    @abstractmethod
    def _load_webpages(self):
        pass


class CSVWebPageReader(WebPageReader):
    def _load_webpages(self):
        with open(self._path, "rt", encoding="utf-8-sig") as inf:
            reader = csv.reader(inf)
            for line in reader:
                url = line[0]
                html = line[1] if len(line) > 1 else None
                try:
                    webpage = self._builder.build(url, html)
                    yield webpage
                except Exception as e:
                    logging.error(e)
                    continue


class MongoWebPageReader(WebPageReader):
    def _load_webpages(self):
        i = 0
        n = WebPage.objects().count()
        for webpage in WebPage.objects()[459:1000]:
            percent = i / n * 100
            logging.info("Webpage percentage: {}".format(percent))
            yield webpage


class CSVCatalogactionReader(WebPageReader):
    def __init__(self, path, ontology):
        super().__init__(path)
        self._ontology = ontology

    def _load_webpages(self):
        with open(self._path, "rt", encoding="utf8") as inf:
            reader = csv.reader(inf)
            next(inf)
            for line in reader:
                url = line[0]
                category = (line[3] + " " + line[4]).strip()

                category = self._ontology[category]

                page = {"url": url}
                page.update(category)

                try:
                    webpage = self._builder.build(**page)
                except:
                    continue

                yield webpage


class JSONWebPageReader(WebPageReader):
    def _load_webpages(self):
        with open(self._path, "rt", encoding="utf8") as inf:
            for line in inf:
                page = json.loads(line)
                try:
                    webpage = self._builder.build(**page)
                except:
                    continue

                yield webpage
