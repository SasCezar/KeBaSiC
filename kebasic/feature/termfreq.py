import nltk
from sklearn.feature_extraction.text import CountVectorizer

from kebasic.feature.featureextractor import AbstractFeatureExtractor


class TermFrequencies(AbstractFeatureExtractor):
    def __init__(self, language=None, stopwords=None):
        self._language = language
        self._stopwords = stopwords
        if not stopwords and language:
            self._stopwords = nltk.corpus.stopwords.words(language)

    def run(self, text):
        vectorizer = CountVectorizer()
        term_document = vectorizer.fit_transform([text])  # is a matrix
        result = zip(vectorizer.get_feature_names(), term_document.A[0])
        sorted_result = sorted(result, key=lambda x: -x[1])
        return self._stopwords_filter(sorted_result)

    def _stopwords_filter(self, terms):
        result = [(term, freq) for term, freq in terms if term not in self._stopwords] if terms else terms
        return result
