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

    @staticmethod
    def boostBoldKey(keywords, words):
        result = {}
        for i in range(len(words)):
            words[i] = words[i].lower()

        for algoritm in keywords.keys():
            tmp = []
            if keywords[algoritm] is not None:
                for keyword in keywords[algoritm]:
                    if(keyword[0].lower() in words):
                        tmp.append((keyword[0], keyword[1]*5.0))
                    else:
                        tmp.append((keyword[0], keyword[1]))
                result[algoritm] = tmp
            else:
                result[algoritm] = keywords[algoritm]

        return result
