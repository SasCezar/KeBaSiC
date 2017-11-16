import itertools
import re
from abc import ABC, abstractmethod

import nltk


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


class AbstractKeywordExtractor(ABC):
    """
    Implements an abstract keyword extraction algorithm
    """

    def __init__(self, language, stopwords=None):
        self._language = language

        self._stopwords = load_stop_words(stopwords) if stopwords else nltk.corpus.stopwords.words(language)
        self._merging_template = "((({keys})\s+({stop}|\s){{0,2}})+\s*({keys}))"
        # self._merging_template = "(({keys})\s*{stop}\s*({keys}))"
        # self._merging_template = "({w_1}|{w_2})\W{{0,3}}({stop}){{0,2}}\W{{0,3}}({w_1}|{w_2})"
        self._stopwords_pattern = "(" + "|".join(
            [re.escape(word.strip()) for word in self._stopwords]) + "){0,2}"  # Check if 2 is a good values

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

        result = []

        scores = dict(keywords)
        keys = scores.keys()

        keywords_pattern = "|".join(keys)
        pattern = self._merging_template.format(keys=keywords_pattern, stop=self._stopwords_pattern)
        merged_keywords = re.findall(pattern, text)

        seen = set()
        for merged_keyword in merged_keywords:
            keywords_tuple = tuple(kw for kw in merged_keyword[0].split() if kw in scores)
            if any(kwtuple in seen for kwtuple in itertools.permutations(keywords_tuple)):
                continue

            seen.add(keywords_tuple)

            score = sum([scores[kw] for kw in keywords_tuple])

            result.append((merged_keyword[0], score))

        """
        for key in keys:
            merged_keywords.append((key, scores[key]))

        """

        return result

    def old_merge_keywords(self, keywords, text):

        merged_keywords = []

        keys = {k for k, v in keywords}
        scores = dict(keywords)
        cartesian_keys = itertools.product(keys, repeat=2)
        # cartesian_keys = list(itertools.combinations(keys, 2))
        for keyword_a, keyword_b in cartesian_keys:
            result = re.search(
                self._merging_template.format(w_1=keyword_a, stop=self._stopwords_pattern, w_2=keyword_b), text)
            if result:
                merged_score = (scores[keyword_a] + scores[keyword_b]) / 2
                merged_keywords.append((result.group(), merged_score))
                keys.discard(keyword_a)
                keys.discard(keyword_b)

        """
        for key in keys:
            merged_keywords.append((key, scores[key]))

        """

        return merged_keywords
