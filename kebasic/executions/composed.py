import csv
import json
import logging
from time import strftime, gmtime
from urllib.parse import urlparse

from domain.webpagebuilder import WebPageBuilder
from executions.basic import TextCleaningPipeline, FeatureExtractionPipeline
from executions.datacrawling import ParallelCrawling
from executions.executor import AbstractExecutor
from feature.normalization import MaxScaling
from feature.resultsjoin import SumScores, InsertScores
from kebasicio.webpageio import BingResultsWebPageReader, JSONWebPageReader
from kebasicio.weka import WekaWebPageTrainingCSV, WekaResultsTrainingCSV
from textprocessing.stemmer import Stemmer
from utils.taxonomy import read_reverse_taxonomy


class KeywordsExecution(AbstractExecutor):
    def run(self):
        cleaner = TextCleaningPipeline(self._configs)
        feature = FeatureExtractionPipeline(self._configs)
        scores_normalizer = MaxScaling()
        scores_merger = SumScores()
        file = self._configs['file']
        path = "../data/{}.json".format(file)
        taxonomy_path = self._configs['taxonomy_path']
        ontology = read_reverse_taxonomy(taxonomy_path)
        # reader = WekaWebPageReader(path)
        # reader = CSVCatalogactionReader(path, ontology)
        reader = JSONWebPageReader(path)

        webpages = reader.read()
        stemmer = Stemmer(language="spanish")
        now = strftime("%Y_%m_%d-%H_%M", gmtime())
        filename = "training_keywords_bing_50_pages_stemmed_{}.csv".format(now)

        writer = WekaResultsTrainingCSV
        builder = WebPageBuilder()
        with writer(filename) as outf, open("dump_{}_{}.json".format(file, now), "wt", encoding="utf8") as dump:
            outf.write_header()
            for json_webpage in webpages:
                try:
                    webpage = builder.build(**json_webpage)
                    webpage.text = cleaner.process(webpage.text)
                    result = feature.process(webpage)
                    if not result:
                        continue
                    for algorithm in result['keywords']:
                        keywords = result['keywords']
                        keywords[algorithm] = scores_normalizer.normalize(result['keywords'][algorithm])

                    combined_scores = scores_normalizer.normalize(scores_merger.merge(result['keywords']))
                    result['keywords']['combined'] = InsertScores().insert(combined_scores,
                                                                           result['keywords']['site_keywords'])
                    dump_result = json.dumps(result, ensure_ascii=False)
                    dump.write(dump_result + "\n")
                    result['keywords'] = result['keywords']['combined']
                    logging.info("Keyword extracted: {}".format(len(result['keywords'])))
                    result['parent_category_id'] = webpage.parent_category_id
                    result['category_id'] = webpage.category_id
                    
                    outf.write(result)
                except Exception:
                    logging.exception("Keyword extraction")
                    continue
        """
        executors_configs = {}
        executors_configs.update(cleaner.get_config())
        executors_configs.update(feature.get_config())
        """


class CrawlingExecution(AbstractExecutor):
    def run(self):
        taxonomy = read_reverse_taxonomy(self._configs['taxonomy_path'])
        reader = BingResultsWebPageReader
        pages = list(
            reader("../output/scraper/GoogleScraper_bing_quoted_50_pages.json", taxonomy).read())

        logging.info("Loaded {}".format(len(pages)))
        writer = WekaWebPageTrainingCSV
        crawler = ParallelCrawling({}, 32)
        webpages = crawler.run(pages)
        print("Crawled webpages {}".format(len(webpages)))
        with writer("../output/scraper/GoogleScraper_bing_quoted_query_categorized_built.csv") as csvout, \
                open("../output/scraper/GoogleScraper_bing_quoted_query_categorized_built.json", "wt",
                     encoding="utf8") as jsonout:
            csvout.write_header()
            for webpage in webpages:
                csvout.write(webpage.to_dict())
                jsonout.write(json.dumps(webpage.to_dict(), ensure_ascii=False) + "\n")


csv.field_size_limit(2147483647)


def read_categories(cat_path):
    categories = {}
    with open(cat_path, "rt", encoding="utf8") as inf:
        reader = csv.reader(inf)
        next(reader)
        for p_c_id, c_id, url, _ in reader:
            categories[get_domain(url)] = [p_c_id, c_id]

    return categories


def get_domain(url):
    parsed = urlparse(url)
    domain = parsed.netloc if "www." not in parsed.netloc else parsed.netloc.replace("www.", "")
    return domain


class ReformatExecution(AbstractExecutor):
    def run(self):
        path = "../output/scraper/GoogleScraper_bing_quoted_50_pages_categorized_built.json"
        reader = JSONWebPageReader(path)
        webpages = reader.read()
        n = 32000
        writer = WekaWebPageTrainingCSV
        out_path = "../GoogleScraper_bing_50_pages_categorized_stemmed.csv"
        i = 0
        j = 0
        k = 0
        cleaner = TextCleaningPipeline(self._configs)
        with writer(out_path) as outf:
            outf.write_header()
            for webpage in webpages:
                k += 1
                i += 1
                perc = i / n * 100
                logging.info("Percent completed: {}".format(perc))
                webpage['text'] = cleaner.process(webpage['text'])
                outf.write(webpage)
        logging.info("Skipped {} on total of {} - Percent skipped: {}".format(j, k, j / k * 100))
