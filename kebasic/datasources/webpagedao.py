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


class WekaWebPageReader(WebPageReader):
    def _load_webpages(self):
        with open(self._path, "rt", encoding="utf8") as inf:
            next(inf)
            reader = csv.reader(inf)
            for line in reader:
                parent_category_id = line[0]
                category_id = line[1]
                url = line[2]
                text = line[3]
                yield WebPage(
                    **{"url": url, "text": text, "parent_category_id": parent_category_id, "category_id": category_id})


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
                    webpage = page
                except:
                    continue

                yield webpage


class BingResultsWebPageReader(WebPageReader):
    def __init__(self, path, taxonomy):
        super().__init__(path)
        with open(self._path, "rt", encoding="utf8") as inf:
            self._results = json.load(inf)
        self._taxonomy = taxonomy
        self._unwanted = ["amazon.", "google.", "bing.", "youtube.", "yahoo."]
        self._extentions = [".doc", ".pdf", ".ppt", ".xml"]

    def _load_webpages(self):
        for query in self._results:
            text_query = query['query']
            category = self._taxonomy[text_query]
            for result in query['results']:
                url = result['url']
                if any([x in url for x in self._unwanted]) or any([str(url).endswith(x) for x in self._extentions]):
                    continue
                title = result['title']
                webpage = {'url': url, 'title': title}
                webpage.update(category)
                yield webpage
