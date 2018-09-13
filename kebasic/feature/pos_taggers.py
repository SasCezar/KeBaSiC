import json
import logging
import os
import subprocess
from abc import ABC, abstractmethod
from json import JSONDecodeError

from stanfordcorenlp import StanfordCoreNLP


class AbstractPOSTagger(ABC):
    def __init__(self, language):
        self._language = language
        pass

    @abstractmethod
    def tag(self, text):
        pass

class StanfordPOSTagger(AbstractPOSTagger):
    def __init__(self, language, server="http://127.0.0.1:9000"):
        super().__init__(language)
        self.LANG_CODES = {"spanish": "es", "english": "en"}
        if "http" in server:
            address, port = server.rsplit(":", maxsplit=1)
            self.tagger = StanfordCoreNLP(address, port=int(port), lang=self.LANG_CODES[language])
        else:
            self.tagger = StanfordCoreNLP(server, lang=self.LANG_CODES[language])

    def tag(self, text):
        try:
            return self.tagger.pos_tag(text)
        except JSONDecodeError:
            logging.info("JSONDecodeError")
            return []


class TINTTagger(AbstractPOSTagger):
    def __init__(self, language, tint_exec_path):
        self._tint_exec = tint_exec_path
        self._in_file = ""
        self._out_file = ""
        super().__init__(language)

    def tag(self, text):
        self._create_file(text)
        bashCommand = self._tint_exec + "./tint.sh -f json -i {} -o {}".format(self._in_file, self._out_file)
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        process.terminate()
        self._remove_file(self._in_file)
        result = self._read_results(self._out_file)
        self._remove_file(self._out_file)
        return result

    def _create_file(self, text):
        with open(self._in_file, 'wt', encoding='utf-8') as f:
            f.write(text)


    def _remove_file(self, path):
        os.remove(path)


    def _read_results(self, path):
        with open(path, "rt", encoding="utf8") as tint_output:
            sentences = json.loads(tint_output)['sentences']

        result = []
        for sentence in sentences:
            for token in sentence['tokens']:
                result.append((token['word'],token['pos']))

        return result
