import logging
import math
import multiprocessing
from abc import ABC, abstractmethod
from multiprocessing import Queue

from domain.webpagebuilder import WebPageBuilder


def worker(domains, queue):
    """
        The worker function, invoked in a process. The results are pushed to a queue.
    """
    builder = WebPageBuilder()
    out = []
    for domain in domains:
        try:
            webpage = builder.build(**domain)
            print(webpage.url)
            out.append(webpage)
        except:
            continue

    queue.put(out)


class AbstractCrawling(ABC):
    def __init__(self, config):
        self._config = config

    @abstractmethod
    def run(self, webpages):
        pass


class ParallelCrawling(AbstractCrawling):
    def __init__(self, config, workers):
        super().__init__(config)
        self._workers = workers
        self._processes = []

    def run(self, items):
        result = Queue()
        chunksize = int(math.ceil(len(items) / float(self._workers)))
        print("Chunk size: {}".format(chunksize))

        logging.info("Initializing processes")
        for i in range(self._workers):
            p = multiprocessing.Process(target=worker, args=(items[chunksize * i:chunksize * (i + 1)], result))
            self._processes.append(p)
            p.start()

        logging.info("Joining results")
        webpages = []
        for x in range(len(self._processes)):
            webpages += result.get()

        logging.info("Waiting processes to end")
        for p in self._processes:
            p.join()

        logging.info("Processes ended")
        filtered_webpages = [webpage for webpage in webpages if webpage and ".pdf" not in webpage.url]

        return filtered_webpages
