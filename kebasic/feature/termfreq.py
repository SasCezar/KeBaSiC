from sklearn.feature_extraction.text import CountVectorizer

from feature.keywordextractor import AbstractKeywordExtractor


class TermFrequencies(AbstractKeywordExtractor):
    def __init__(self, language=None, stopwords=None, min_count=1, lemmize=False, limit=50, keep_all=0):
        super().__init__(language=language, stopwords=stopwords, lemmize=lemmize, limit=limit, keep_all=keep_all)
        self._language = language

        self._min_count = min_count
        self._vectorizer = CountVectorizer()

    def run(self, text):
        lemmed_text = self._text_lemmatization(text) if self._lemmize else text
        keywords = self._extract_keywords(lemmed_text)
        filtered_keywords = self._filter(keywords)
        sorted_result = self._sort(filtered_keywords)
        return sorted_result

    def _extract_keywords(self, text):
        term_document = self._vectorizer.fit_transform([text])  # is a matrix
        keyword_candidates = zip(self._vectorizer.get_feature_names(), term_document.A[0])
        return keyword_candidates

    def _filter(self, terms):
        result = [(term, freq) for term, freq in terms
                  if term not in self._stopwords and freq >= self._min_count and len(term.strip()) > 1]
        return result


class MergingTermFrequencies(TermFrequencies):
    def run(self, text):
        lemmed_text = self._text_lemmatization(text) if self._lemmize else text
        keywords = self._extract_keywords(lemmed_text)

        if not keywords:
            return []
        filtered_keywords = self._filter(keywords)
        merged_keywords = self._merge_keywords(filtered_keywords, text)
        # scaled_keywords = self._score_rescaling(merged_keywords)
        sorted_keywords = self._sort(merged_keywords)
        if self._limit:
            sorted_keywords = sorted_keywords[:self._limit]
        return sorted_keywords
