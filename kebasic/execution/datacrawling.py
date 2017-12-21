import csv
import logging
import math
import multiprocessing
from multiprocessing import Queue

from dao.bingresultsdao import BingResultsDAO
from domain.webpagebuilder import WebPageBuilder
from execution.basic import TextCleanerExecution


def worker(domains, queue):
    """ The worker function, invoked in a process. 'nums' is a
        list of numbers to factor. The results are placed in
        a dictionary that's pushed to a queue.
    """
    builder = WebPageBuilder()
    out = []
    for domain in domains:
        try:
            webpage = builder.build(domain)
            out.append(webpage)
        except:
            out.append(False)
            continue

    queue.put(out)


def data_crawling(configs):
    cleaner = TextCleanerExecution(configs)
    categories, domains = BingResultsDAO().get_website_categories()
    logging.info("NUM DOMAINS {}".format(len(domains)))
    webpages = []

    procs = []
    nprocs = 32
    out_q = Queue()
    chunksize = int(math.ceil(len(domains) / float(nprocs)))
    print("Chunk size: {}".format(chunksize))

    logging.info("Initializing processes")
    # inizializzazione carico per processo
    for i in range(nprocs):
        p = multiprocessing.Process(target=worker, args=(domains[chunksize * i:chunksize * (i + 1)], out_q))
        procs.append(p)
        p.start()

    logging.info("Joining results")
    for x in range(len(procs)):
        webpages += out_q.get()

    logging.info("Waiting processes to end")
    # Wait for all worker processes to finish
    for p in procs:
        p.join()

    logging.info("Processes ended")
    filtered_webpages = [webpage for webpage in webpages if webpage]
    cleaned_webpages = cleaner.execute(filtered_webpages)

    with open("webpages.csv", "wt", encoding="utf8", newline='') as outf:
        writer = csv.writer(outf, quoting=csv.QUOTE_ALL)
        writer.writerow(['parent_id', "category_id", "url", "text"])
        for webpage in cleaned_webpages:
            writer.writerow(categories[webpage.url] + [webpage.url, webpage.text])
