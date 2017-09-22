from kebasic.execution.executor import AbstractExecutor


class BasicExecution(AbstractExecutor):
    def __init__(self, config):
        super().__init__(config)
        self._allowed = {"language", "resources", "stopwords", "keywords_extraction_algorithms", "rake", "text_rank"}

    def execute(self):
        pass
