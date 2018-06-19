from abc import ABC, abstractmethod


class AbstractNormalizer(ABC):
    """
    Defines an abstract function for score normalization
    """
    name = "AbstractNormalizer"

    @abstractmethod
    def normalize(self, keywords):
        """
        Given a list of tuples (keyword, score) normalizes using a specific function.
        :param keywords:
        :return:
        """
        pass

    def config(self):
        return self.name


class MaxScaling(AbstractNormalizer):
    name = "MaxScaling"

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
    name = "SumScaling"

    def normalize(self, keywords):
        if not keywords:
            return []
        scores = [score for _, score in keywords]

        rescaled_keywords = []

        for keyword, score in keywords:
            scaled_score = score / sum(scores) if sum(scores) else 0
            rescaled_keywords.append((keyword, scaled_score))

        return rescaled_keywords
