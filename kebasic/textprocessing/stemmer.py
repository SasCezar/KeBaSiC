from nltk import SnowballStemmer

from textprocessing.textprocessor import AbstractTextProcessor


class Stemmer(AbstractTextProcessor):
    def __init__(self, language):
        self._stemmer = SnowballStemmer(language)

    def run(self, text):
        stemmed_text = self._stem_text(text)
        return stemmed_text

    def _stem_text(self, text):
        return ' '.join([self._stemmer.stem(w) for w in text.split()])
