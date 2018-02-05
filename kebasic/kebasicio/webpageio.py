import csv
import json
from abc import ABC, abstractmethod

from kebasicio.writer import AbstractWriter

csv.field_size_limit(2147483647)


class AbstractWebPageReader(ABC):
    """
    Defines an interface for webpages reader from file
    """
    def __init__(self, path):
        self._path = path

    def read(self):
        return self._read()

    @abstractmethod
    def _read(self):
        pass


class AbstractWebPageWriter(AbstractWriter):
    @abstractmethod
    def _write(self, content):
        pass


class CSVWebPageReader(AbstractWebPageReader):
    """
    Reads webpages from a CSV file where the first element is the url and optionally the HTML source for the page
    """
    def _read(self):
        with open(self._path, "rt", encoding="utf-8") as inf:
            reader = csv.reader(inf)
            for line in reader:
                url = line[0]
                html = line[1] if len(line) > 1 else None
                webpage = {"url": url, "html": html}
                yield webpage


class WekaWebPageReader(AbstractWebPageReader):
    """
    Reads webpages from a CSV file where the columns are the following: parent_category_id, category_id, url, text
    """
    def _read(self):
        with open(self._path, "rt", encoding="utf8") as inf:
            next(inf)
            reader = csv.reader(inf)
            for line in reader:
                parent_category_id = line[0]
                category_id = line[1]
                url = line[2]
                text = line[3]
                webpage = {"url": url, "text": text, "parent_category_id": parent_category_id,
                           "category_id": category_id}
                yield webpage


class CSVCatalogactionReader(AbstractWebPageReader):
    """
    Reads webpages from a CSV file where the columns are the following: url, _, category_id, _, _
    """
    def __init__(self, path, ontology):
        super().__init__(path)
        self._ontology = ontology

    def _read(self):
        with open(self._path, "rt", encoding="utf8") as inf:
            reader = csv.reader(inf)
            next(inf)
            for line in reader:
                url = line[0]
                category = line[2]

                category = self._ontology[category]
                webpage = {"url": url}
                webpage.update(category)

                yield webpage


class JSONWebPageReader(AbstractWebPageReader):
    """
    Reads a file containing, on each line, a JSON object representing a webpage
    """
    def _read(self):
        with open(self._path, "rt", encoding="utf8") as inf:
            for line in inf:
                webpage = json.loads(line)
                yield webpage


class BingResultsWebPageReader(AbstractWebPageReader):
    """
    Parses the result from GoogleScraper and returns the results for each query as a webpage
    """
    def __init__(self, path, taxonomy):
        super().__init__(path)
        with open(self._path, "rt", encoding="utf8") as inf:
            self._results = json.load(inf)
        self._taxonomy = taxonomy
        self._unwanted = ["amazon.", "google.", "bing.", "youtube.", "yahoo.", "twitter.",
                          "slideshare.", "facebook.", "scribd."]
        self._extentions = [".doc", ".pdf", ".ppt", ".xml"]

    def _read(self):
        seen = set()
        for query in self._results:
            text_query = query['query'][1:-1].strip()
            category = self._taxonomy[text_query]
            for result in query['results']:
                url = result['link']
                if any([x in url for x in self._unwanted]) or any(
                        [str(url).endswith(x) for x in self._extentions]) or url in seen:
                    continue
                seen.add(url)
                title = result['title']
                webpage = {'url': url, 'title': title}
                webpage.update(category)
                yield webpage
