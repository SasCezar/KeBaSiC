from abc import ABC, abstractmethod


class AbstractScoresCombination(ABC):
    """
    Defines an abstract function of combining scores from different algorithms
    """

    @abstractmethod
    def merge(self, scores):
        """
        Given a dictionary of scores return a list of the combined scores
        :param scores:
        :return:
        """
        pass


class SumScores(AbstractScoresCombination):
    """
    The scores are combined using the sum. If the same keyword was extracted by different algorithms the final score
    is the sum of the scores from each algorithm
    """
    def merge(self, scores):
        results = {}

        for alg in scores:
            if not scores[alg]:
                continue
            for key, score in scores[alg]:
                results[key.lower()] = score + results[key.lower()] if key.lower() in results else score

        keywords = results.items()
        return sorted(keywords, key=lambda x: (-x[1], x[0]))


class WeightedSum(AbstractScoresCombination):
    """
    The scores are combined using a weighted sum. If the same keyword was extracted by different algorithms the final score
    is the sum of the scores from each algorithm divided by the number of all algorithms used for keyword extraction (even if
    the keyword was not extracted by an algorithm)
    """
    def merge(self, scores):
        results = {}

        num_algorithms = len(scores)
        for alg in scores:
            if not scores[alg]:
                continue
            for key, score in scores[alg]:
                results[key.lower()] = score + results[key.lower()] if key.lower() in results else score

        for result in results:
            results[result] = results[result] / num_algorithms

        return sorted(results.items(), key=lambda x: (-x[1], x[0]))


class InsertScores(object):
    @staticmethod
    def insert(base1, insert1):
        """
        Given two lists of keywords, the final result is an insertion of the second list into the first. If some element
        are present in both lists, the score is the one present in the second list
        :param base1:
        :param insert1:
        :return:
        """
        keywords = {k.lower(): v for k, v in base1}
        insert = {k.lower(): v for k, v in insert1}

        keywords.update(insert)
        keywords = [(kw, score) for kw, score in keywords.items()]
        return sorted(keywords, key=lambda x: (-x[1], x[0]))
