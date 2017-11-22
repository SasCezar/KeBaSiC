import hashlib
import pprint
from abc import ABC, abstractmethod
from collections import OrderedDict
from os.path import join
from time import strftime, gmtime


class AbstractResultWriter(ABC):
    @abstractmethod
    def write(self, dest_path, content, config):
        pass

    def _create_content(self, dest_path, content, config):
        if config:
            hash_config = self._save_config(dest_path, config)
            result = self._inject_config(content, hash_config)
            return result
        else:
            return content

    @staticmethod
    def _inject_config(content, config_hash):
        return {"results": content, "config_hash": config_hash} if config_hash else {"results": content}

    def _save_config(self, dest_path, config):
        sha = hashlib.sha256()
        sha.update(pprint.pformat(config).encode('utf-8'))
        hashed = sha.hexdigest()
        filename = join(dest_path, "config_{}.txt".format(hashed))

        with open(filename, "wt", encoding="utf8") as out:
            pp = pprint.PrettyPrinter(stream=out, indent=4, width=200)
            pp.pprint(config)

        return hashed


class PPrintResultWriter(AbstractResultWriter):
    def write(self, dest_path, content, config):
        result = self._create_content(dest_path, content, config)
        now = strftime("%Y_%m_%d-%H_%M", gmtime())
        file = join(dest_path, "keywords_{}.txt".format(now))
        with open(file, 'wt', encoding="utf8") as out:
            pp = pprint.PrettyPrinter(stream=out, indent=4)
            pprint._sorted = lambda x: x
            pp.pprint(result)


class SortedPPrintResultWriter(PPrintResultWriter):
    def __init__(self, order):
        self._order = order

    def write(self, dest_path, content, config):
        content = self._sort_content(content)
        super(SortedPPrintResultWriter, self).write(dest_path, content, config)

    def _sort_content(self, content):
        results = []
        for result in content:
            sorted_result = OrderedDict([(i, result[i]) for i in self._order])
            results.append(sorted_result)

        return results
