import csv

from kebasicio.writer import AbstractWriter


class WekaTrainigCSV(AbstractWriter):
    def __init__(self, path):
        super().__init__(path)
        self._header = ['parent_category_id', "category_id", "url", "text"]

    def __enter__(self):
        super().__enter__()
        self._csv = csv.writer(self._file, quoting=csv.QUOTE_ALL)
        return self

    def write_header(self, header=None):
        if not header:
            header = self._header
        self._csv.writerow(header)

    def _write(self, webpage):
        row = self._create_row(webpage)
        if row:
            self._csv.writerow(row)
        return

    def _create_row(self, webpage):
        parent_category_id = webpage.parent_category_id
        category_id = webpage.category_id
        url = webpage.url
        text = webpage.text.strip()
        if not text:
            return False
        row = [parent_category_id, category_id, url, text]
        return row


class WekaKeywordTrainingCSV(WekaTrainigCSV):
    def __init__(self, path):
        super().__init__(path)
        self._header = ['parent_category_id', "category_id", "url", "keywords"]

    def _create_row(self, result):
        parent_category_id = result['parent_category_id']
        category_id = result['category_id']
        url = result['url']
        keywords = " ".join([keyword for keyword, _ in result['keywords']])
        if not keywords:
            return False
        row = [parent_category_id, category_id, url, keywords]
        return row
