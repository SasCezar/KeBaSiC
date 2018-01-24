import csv
import json
import logging
from time import strftime, gmtime
from urllib.parse import urlparse

from kebasicio.database.webpagedao import JSONWebPageReader, CSVCatalogactionReader

from datasources.webpagedao import BingResultsWebPageReader
from executions.basic import TextCleaningPipeline, FeatureExtractionPipeline
from executions.datacrawling import ParallelCrawling
from executions.executor import AbstractExecutor
from feature.normalization import MaxScaling
from feature.resultsjoin import SumScores
from kebasicio.weka import WekaWebPageTrainingCSV
from textprocessing.stemmer import Stemmer
from utils.taxonomy import read_reverse_taxonomy


class KeywordsExecution(AbstractExecutor):
    def run(self):
        cleaner = TextCleaningPipeline(self._configs)
        feature = FeatureExtractionPipeline(self._configs)
        scores_normalizer = MaxScaling()
        scores_merger = SumScores()
        file = self._configs['file']
        path = "../data/{}".format(file)
        taxonomy_path = self._configs['taxonomy_path']
        ontology = read_reverse_taxonomy(taxonomy_path)
        # reader = WekaWebPageReader(path)
        reader = CSVCatalogactionReader(path, ontology)

        webpages = reader.load_webpages()
        stemmer = Stemmer(language="spanish")
        now = strftime("%Y_%m_%d-%H_%M", gmtime())
        filename = "training_catalogacion_stemmed.csv".format(file, now)

        writer = WekaWebPageTrainingCSV
        with writer(filename) as outf, open("dump_{}.json".format(file), "wt", encoding="utf8") as dump:
            outf.write_header()
            for webpage in webpages:
                webpage.text = cleaner.process(webpage.text)
                webpage.text = stemmer.run(webpage.text)
                outf.write(webpage.to_dict())
                """
                try:
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
                except Exception as e:
                    print(e)
                    continue
                """

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
            reader("../output/scraper/GoogleScraper_bing_quoted_query_categorized.json", taxonomy).load_webpages())

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
        path = "../data/result.json"
        reader = JSONWebPageReader(path)
        webpages = reader.load_webpages()
        cat_path = "../data/webpages_cleaned.csv"
        cat = read_categories(cat_path)
        n = 800000
        writer = WekaWebPageTrainingCSV
        out_path = "../resuls_1b_retry.csv"
        i = 0
        j = 0
        k = 0
        cleaner = TextCleaningPipeline(self._configs)
        with writer(out_path) as outf:
            outf.write_header()
            for webpage in webpages:
                k += 1
                url = webpage['url']
                domain = get_domain(url)
                i = i + 1
                if domain not in cat:
                    logging.info("Skipped {}".format(url))
                    j += 1
                    continue
                webpage_category = cat[domain]
                webpage['parent_category_id'] = webpage_category[0]
                webpage['category_id'] = webpage_category[1]
                perc = i / n * 100
                logging.info("Percent completed: {}".format(perc))
                webpage['text'] = cleaner.process(webpage['text'])
                outf.write(webpage)
        logging.info("Skipped {} on total of {} - Percent skipped: {}".format(j, k, j / k * 100))
