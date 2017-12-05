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

        return sorted(results.items(), key=lambda x: (-x[1], x[0]))
