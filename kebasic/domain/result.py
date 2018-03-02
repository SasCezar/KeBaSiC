class Result(object):
    def __init__(self, url, keywords):
        self._url = url
        self.keywords = keywords


class Keywords(object):
    def __init__(self, algorithm, keywords):
        self._algorithm = algorithm
        self._keywords = keywords
