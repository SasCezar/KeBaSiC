import re
import string

from feature.keywordextractor import AbstractKeywordExtractor, load_stop_words


class SiteKeywordsExtractor(AbstractKeywordExtractor):
    def __init__(self, language=None, stopwords=None, commonwords=None, lemmize=1, limit=50, keep_all=0):
        super().__init__(language=language, stopwords=stopwords, lemmize=lemmize, limit=limit, keep_all=keep_all)
        self._remove = {char: None for char in string.punctuation}
        self._commonwords = load_stop_words(commonwords) if commonwords else []
        self._filterlist = self._stopwords + self._commonwords

    def _extract_keywords(self, text, score=0):
        keywords = [(self._clean(keyword.strip()), score) for keyword in re.split(r"[,.]", text) if keyword.strip()]
        return keywords

    def run(self, text, score=1):
        if not text:
            return None
        keywords = self._extract_keywords(text, score)
        if not keywords:
            return []
        filtered_keywords = self._filter(keywords)
        lemmed_keywords = self._keywords_lemmatization(filtered_keywords)
        sorted_keywords = self._sort(lemmed_keywords)
        return sorted_keywords

    def _clean(self, keyword):
        keyword.translate(self._remove)
        return keyword

    def _filter(self, keywords):
        if not self._filterlist:
            return keywords
        return [(keyword, weight) for keyword, weight in keywords
                if keyword not in self._filterlist and len(keyword.strip()) > 1]
