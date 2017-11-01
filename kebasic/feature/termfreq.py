import nltk
from sklearn.feature_extraction.text import CountVectorizer

from feature.keywordextractor import AbstractKeywordExtractor


class TermFrequencies(AbstractKeywordExtractor):
    def __init__(self, language=None, stopwords=None, min_count=1):
        super().__init__(language, stopwords)
        self._language = language

        if not self._stopwords:
            self._stopwords = nltk.corpus.stopwords.words(language)

        self._min_count = min_count
        self._vectorizer = CountVectorizer()

    def run(self, text):
        term_document = self._vectorizer.fit_transform([text])  # is a matrix
        result = zip(self._vectorizer.get_feature_names(), term_document.A[0])
        sorted_result = sorted(result, key=lambda x: -x[1])
        return self._filter(sorted_result)

    def _filter(self, terms):
        result = [(term, freq) for term, freq in terms if term not in self._stopwords and freq >= self._min_count]
        return result
