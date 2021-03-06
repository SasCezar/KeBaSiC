import logging
import re
import string
from abc import ABC, abstractmethod
from itertools import groupby

import nltk
import treetaggerwrapper


def load_stop_words(stopwords):
    """Utility function to load stop words from a file and return as a list of words

    :param stopwords: Path and file name of a file containing stop words.
    :return: A list of stop words.
    """

    if type(stopwords) is list:
        return stopwords

    stop_words = []
    for line in open(stopwords, "rt", encoding="utf8"):
        if line.strip()[0:1] != "#":
            for word in line.split():  # in case more than one per line
                stop_words.append(word.strip())
    return stop_words


LANGS = {"spanish": "es",
         "english": "en"}

logging.getLogger('TreeTagger').setLevel(logging.CRITICAL)


class AbstractKeywordExtractor(ABC):
    """
    Implements an abstract keyword extraction algorithm
    """

    def __init__(self, language=None, stopwords=None, lemmize=False, limit=50, keep_all=0):
        self._language = language

        self._stopwords = load_stop_words(stopwords) if stopwords else nltk.corpus.stopwords.words(language)
        self._merging_template = "(({keys}){{1}}((\s+({stop})){{0,2}}\s+({keys}){{1}})+)"
        self._stopwords_pattern = "|".join([re.escape(word.strip()) for word in self._stopwords])

        self._lemmize = lemmize
        self._lemmatizer = treetaggerwrapper.TreeTagger(TAGLANG=LANGS[self._language]).tag_text if lemmize else None
        self._keep_all = keep_all
        self._limit = limit

    @abstractmethod
    def run(self, text):
        """
        Executes the feature extraction algorithm on the text, the result is a list of keywords.

        :param text: A string containing the input text for the algorithm
        :return: The features
        """
        pass

    def _filter(self, keywords):
        if not self._stopwords:
            return keywords
        return [(keyword, weight) for keyword, weight in keywords
                if keyword not in self._stopwords and len(keyword.strip()) > 1]

    @staticmethod
    def _sort(keywords):
        """
        Sorts the keywords based on the results in descending order. In two keywords have the same score, they are
        sorted in alphabetical order.

        :param keywords:
        :return:
        """
        return sorted(keywords, key=lambda x: (-x[1], x[0]))

    def configuration(self):
        """
        Returns the model configurations as a dictionary

        :return:
        """
        return self.__dict__

    @abstractmethod
    def _extract_keywords(self, text):
        pass

    def _merge_keywords(self, keywords, text):
        """
        Given a list of keywords, find all the adjacent combinations of keywords in the text. The keywords may be
        separated by a stopword.

        :param keywords:
        :param text:
        :return:
        """
        if not keywords:
            return []

        result = []
        scores = {k.lower(): score for k, score in keywords}
        keys = scores.keys()

        keywords_pattern = "|".join(keys)
        pattern = self._merging_template.format(keys=keywords_pattern, stop=self._stopwords_pattern)
        merged_keywords = re.findall(pattern, text, re.IGNORECASE)

        seen = set()
        for merged_keyword in merged_keywords:
            keywords_tuple = tuple(kw.lower() for kw in merged_keyword[0].strip().split() if kw.lower() in scores)
            if len(keywords_tuple) > 6:
                continue
            if not keywords_tuple:
                continue
            frozen_keyword = frozenset(keywords_tuple)
            if frozen_keyword in seen:
                continue

            seen.add(frozen_keyword)

            score = sum([scores[kw.lower()] for kw in keywords_tuple])
            score = scores[merged_keyword[0].lower()] if merged_keyword[0].lower() in scores and not score else score
            result.append((self._remove_duplicates(merged_keyword[0]), score))

        if self._keep_all:
            used_keywords = set(keyword for kwtuple in seen for keyword in kwtuple)

            for key in keys:
                result.append((key, scores[key.lower()])) if key not in used_keywords else None
        return result

    def _text_lemmatization(self, text):
        """
        Given a text returns the lemmized version using the TreeTagger lemmatizer.

        :param text:
        :return:
        """
        lemmed_text = ""
        tagged_text = self._lemmatizer(text)
        for lemmed_word in tagged_text:
            original, tag, lemmed = lemmed_word.split()
            word = " " + lemmed if lemmed not in string.punctuation else lemmed

            lemmed_text += word

        return lemmed_text

    def _keywords_lemmatization(self, keywords):
        """
        Given a list of keywords, for each of them evaluates the lemma

        :param keywords:
        :return:
        """
        result = []
        for keyword, score in keywords:
            lemmed_keyword = self._keyword_lemmatization(keyword)
            result.append((lemmed_keyword, score))

        return result

    def _keyword_lemmatization(self, keyword):
        """
        Given a keywords, simple or composed, returns the lemma of all its component.

        :param keyword:
        :return:
        """
        lemmed_keyword = ""
        lemming_result = self._lemmatizer(keyword)
        for lemma in lemming_result:
            original, pos, lemmed = lemma.split()
            lemmed_keyword += " " + lemmed

        return lemmed_keyword.strip()

    @staticmethod
    def _remove_duplicates(keyword):
        return " ".join([x[0] for x in groupby(keyword.split())])
