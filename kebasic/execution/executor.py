from abc import ABC, abstractmethod


class Context(object):
    def __init__(self, strategy):
        self._strategy = strategy

    def execute(self):
        self._strategy.execute()


class AbstractExecutor(ABC):
    def __init__(self, config):
        self._config = config
        self._allowed = set()  # all those keys will be initialized as class attributes

    @abstractmethod
    def execute(self):
        pass

    def _initialize(self):
        # initialize all allowed keys to false
        for key in self._allowed:
            self.__setattr__(key, False)

        for key, value in self._config.items():
            self.__setattr__(key, value) if key in self._allowed else None

        return self
