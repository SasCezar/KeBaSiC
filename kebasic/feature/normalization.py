from abc import ABC, abstractmethod


class AbstractNormalizer(ABC):
    @abstractmethod
    def normalize(self, keywords):
        pass


class FeatureScaling(AbstractNormalizer):
    def normalize(self, keywords):
        if not keywords:
            return []
        scores = [score for _, score in keywords]
        max_score = max(scores)

        rescaled_keywords = []

        for keyword, score in keywords:
            scaled_score = score / max_score if max_score else 0
            rescaled_keywords.append((keyword, scaled_score))

        return rescaled_keywords


class SumScaling(AbstractNormalizer):

    def normalize(self, keywords):
        if not keywords:
            return []
        scores = [score for _, score in keywords]

        rescaled_keywords = []

        for keyword, score in keywords:
            scaled_score = score / sum(scores) if sum(scores) else 0
            rescaled_keywords.append((keyword, scaled_score))

        return rescaled_keywords
