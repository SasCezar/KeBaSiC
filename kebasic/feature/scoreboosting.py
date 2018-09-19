from abc import ABC


class ScorePenalizer(ABC):
    @staticmethod
    def penalize(keywords, penalizers, f=lambda x: x / 2):
        result = []
        for keyword in keywords:
            if any([x for x in penalizers if x.lower() in keyword[0].lower()]):
                result.append((keyword[0], f(keyword[1])))
            else:
                result.append(keyword)

        return sorted(result, key=lambda x: (-x[1], x[0]))

    '''
    @staticmethod
    def boost(keywords, penalizers, f=lambda x: x * 5):
        result = []
        for keyword in keywords:
            if any([x for x in penalizers if x.lower() in keyword[0].lower()]):

                result.append((keyword[0], f(keyword[1])))
            else:
                result.append(keyword)

        return sorted(result, key=lambda x: (-x[1], x[0]))
    '''