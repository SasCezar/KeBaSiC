from sklearn.feature_extraction.text import CountVectorizer

from kebasic.feature.featureextractor import AbstractFeatureExtractor


class TermFrequencies(AbstractFeatureExtractor):
    def run(self, text):
        vectorizer = CountVectorizer()
        term_document = vectorizer.fit_transform([text])  # is a matrix
        result = zip(vectorizer.get_feature_names(), term_document.A[0])
        sorted_result = sorted(result, key=lambda x: -x[1])
        return sorted_result
