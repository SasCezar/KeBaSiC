import pprint
from abc import abstractmethod
from collections import OrderedDict

from kebasicio.writer import AbstractWriter


class AbstractResultWriter(AbstractWriter):
    @abstractmethod
    def _write(self, content):
        pass


class PPrintResultWriter(AbstractResultWriter):

    def write_header(self):
        pass

    def __enter__(self):
        super().__enter__()
        self._pp = pprint.PrettyPrinter(stream=self._file, indent=4, width=120)
        return self

    def _write(self, content):
        self._pp.pprint(content)


class SortedPPrintResultWriter(PPrintResultWriter):
    def __init__(self, path, order=None):
        super().__init__(path)
        if order is None:
            order = ["site_keywords", "Combined", "MergingRAKE", "MergingTextRank", "MergingTermFrequencies"]
        self._order = order

    def write(self, content):
        content = self._sort_content(content)
        super(SortedPPrintResultWriter, self).write(content)

    def _sort_content(self, content):
        results = []
        for result in content:
            sorted_result = OrderedDict([(i, result['keywords'][i]) for i in self._order if i in result['keywords']])
            result['keywords'] = sorted_result
            results.append(result)

        return results
