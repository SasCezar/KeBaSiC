import csv


class WekaTrainigCSV(object):
    def __init__(self, path):
        self._path = path
        self._header = ['parent_category_id', "category_id", "url", "text"]

    def write(self, webpages):
        with open(self._path, "wt", encoding="utf8", newline='') as outf:
            writer = csv.writer(outf, quoting=csv.QUOTE_ALL)
            for webpage in webpages:
                row = self._create_row(webpage)
                if not row:
                    continue
                writer.writerow(row)

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
