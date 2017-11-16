import snowballstemmer


class Stemmer(object):
    def __init__(self, language):
        self._language = language
        self._stemmer = snowballstemmer.stemmer("spanish")

    def stem(self, text):
        return self._stemmer.stemWords(text.split())
