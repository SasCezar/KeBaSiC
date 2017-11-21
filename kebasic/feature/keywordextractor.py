import itertools
import logging
import re
import string
from abc import ABC, abstractmethod

import nltk
import treetaggerwrapper


def load_stop_words(stopwords):
    """
    Utility function to load stop words from a file and return as a list of words

    :param stopwords: Path and file name of a file containing stop words.
    :return list: A list of stop words.
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

    def __init__(self, language, stopwords=None, lemmize=False):
        self._language = language

        self._stopwords = load_stop_words(stopwords) if stopwords else nltk.corpus.stopwords.words(language)
        self._merging_template = "((({keys})\s+({stop}|\s){{0,2}})+\s*({keys}))"
        self._stopwords_pattern = "(" + "|".join(
            [re.escape(word.strip()) for word in self._stopwords]) + "){0,2}"  # Check if 2 is a good values

        self._lemmize = lemmize
        self._lemmatizer = treetaggerwrapper.TreeTagger(TAGLANG=LANGS[self._language]).tag_text if lemmize else None

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
        return [(keyword, weight) for keyword, weight in keywords if keyword not in self._stopwords]

    @staticmethod
    def _sort(keywords):
        return sorted(keywords, key=lambda x: (-x[1], x[0]))

    def configuration(self):
        """
        Returns the model configurations
        :return:
        """
        return self.__dict__

    @abstractmethod
    def run(self, text):
        pass

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
        result = []

        scores = dict([(k.lower(), score) for k, score in keywords])
        keys = scores.keys()

        keywords_pattern = "|".join(keys)
        pattern = self._merging_template.format(keys=keywords_pattern, stop=self._stopwords_pattern)
        merged_keywords = re.findall(pattern, text, re.IGNORECASE)

        seen = set()
        for merged_keyword in merged_keywords:
            keywords_tuple = tuple(kw.lower() for kw in merged_keyword[0].split() if kw.lower() in scores)
            if any(kwtuple in seen for kwtuple in itertools.permutations(keywords_tuple)):
                continue

            seen.add(keywords_tuple)

            score = sum([scores[kw.lower()] for kw in keywords_tuple])
            score = scores[merged_keyword[0].lower()] if merged_keyword[0].lower() in scores and not score else score
            result.append((merged_keyword[0], score))

        for key in keys:
            merged_keywords.append((key, scores[key.lower()]))

        return result

    def _text_lemmatization(self, text):
        lemmed_text = ""
        tagged_text = self._lemmatizer(text)
        for lemmed_word in tagged_text:
            original, tag, lemmed = lemmed_word.split()
            word = " " + lemmed if lemmed not in string.punctuation else lemmed

            lemmed_text += word

        return lemmed_text

    def _keywords_lemmatization(self, keywords):
        result = []
        for keyword, score in keywords:
            lemmed_keyword = self._keyword_lemmatization(keyword)
            result.append((lemmed_keyword, score))

        return result

    def _keyword_lemmatization(self, keyword):
        lemmed_keyword = ""
        lemming_result = self._lemmatizer(keyword)
        for lemma in lemming_result:
            original, pos, lemmed = lemma.split()
            lemmed_keyword += " " + lemmed

        return lemmed_keyword
