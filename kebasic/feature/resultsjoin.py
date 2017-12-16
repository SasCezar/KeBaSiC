from abc import ABC, abstractmethod


class AbstractScoresCombination(ABC):
    @abstractmethod
    def merge(self, scores):
        pass


class SumResults(AbstractScoresCombination):
    def merge(self, scores):
        results = {}

        for alg in scores:
            if not scores[alg]:
                continue
            for key, score in scores[alg]:
                results[key.lower()] = score + results[key.lower()] if key.lower() in results else score

        keywords = results.items()
        max_score = max([x for _, x in keywords])
        max_score = max_score if max_score else 1

        keywords = [(kw, score / max_score) for kw, score in keywords]
        return sorted(keywords, key=lambda x: (-x[1], x[0]))


class WeightedSum(AbstractScoresCombination):
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
