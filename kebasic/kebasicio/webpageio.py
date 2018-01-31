import csv
import json
from abc import ABC, abstractmethod

from kebasicio.writer import AbstractWriter

csv.field_size_limit(2147483647)


class AbstractWebPageReader(ABC):
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
    def _read(self):
        with open(self._path, "rt", encoding="utf-8-sig") as inf:
            reader = csv.reader(inf)
            for line in reader:
                url = line[0]
                html = line[1] if len(line) > 1 else None
                webpage = {"url": url, "html": html}
                yield webpage


class WekaWebPageReader(AbstractWebPageReader):
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
    def __init__(self, path, ontology):
        super().__init__(path)
        self._ontology = ontology

    def _read(self):
        with open(self._path, "rt", encoding="utf8") as inf:
            reader = csv.reader(inf)
            next(inf)
            for line in reader:
                url = line[0]
                category = (line[3] + " " + line[4]).strip()

                category = self._ontology[category]
                webpage = {"url": url}
                webpage.update(category)

                yield webpage


class JSONWebPageReader(AbstractWebPageReader):
    def _read(self):
        with open(self._path, "rt", encoding="utf8") as inf:
            for line in inf:
                webpage = json.loads(line)
                yield webpage


class BingResultsWebPageReader(AbstractWebPageReader):
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


class JSONWebPageWriter(AbstractWebPageWriter):
    def _write(self, content):
        json_content = json.dumps(content, ensure_ascii=False)
        self._file.write(json_content)
