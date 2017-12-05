from feature.keywordextractor import AbstractKeywordExtractor


class SiteKeywordsExtractor(AbstractKeywordExtractor):
    def __init__(self, language=None, stopwords=None, lemmize=1, algo_score=None):
        super().__init__(language=language, stopwords=stopwords, lemmize=lemmize)
        if not algo_score:
            raise Exception("Missing value: \'algo_score\'")
        self.algo_score = algo_score

    def _extract_keywords(self, text, score=0):
        keywords = [(keyword.strip(), score) for keyword in text.split(',') if keyword.strip()]
        return keywords

    def run(self, text, score=0):
        if not text:
            return None
        keywords = self._extract_keywords(text, score)
        filtered_keywords = self._filter(keywords)
        lemmed_keywords = self._keywords_lemmatization(filtered_keywords)
        sorted_keywords = self._sort(lemmed_keywords)
        return sorted_keywords
