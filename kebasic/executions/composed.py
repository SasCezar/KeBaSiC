import json
import logging

from domain.webpagebuilder import WebPageBuilder
from executions.basic import TextCleaningPipeline, FeatureExtractionPipeline
from executions.datacrawling import ParallelCrawling
from executions.executor import AbstractExecutor
from feature.normalization import MaxScaling
from feature.resultsjoin import SumScores, InsertScores
from kebasicio.webpageio import BingResultsWebPageReader, JSONWebPageReader
from kebasicio.weka import WekaWebPageTrainingCSV
from kebasicio.writer import JSONWriter
from utils.taxonomy import read_reverse_taxonomy


class KeywordsExecution(AbstractExecutor):
    """
    Implements an execution for keywords extraction
    """
    def run(self):
        cleaner = TextCleaningPipeline(self._configs)
        feature = FeatureExtractionPipeline(self._configs)
        scores_normalizer = MaxScaling()
        scores_merger = SumScores()

        path = self._configs['input_path']
        reader = JSONWebPageReader(path)
        webpages = reader.read()
        writer = JSONWriter
        builder = WebPageBuilder()

        out_filename = self._configs['out_path']
        with writer(out_filename) as outf:
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
                    result['keywords'] = result['keywords']['combined']
                    logging.info("Keyword extracted: {}".format(len(result['keywords'])))
                    result['parent_category_id'] = webpage.parent_category_id
                    result['category_id'] = webpage.category_id
                    
                    outf.write(result)
                except Exception:
                    logging.exception("Keyword extraction")
                    continue


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


class ReformatExecution(AbstractExecutor):
    def run(self):
        path = "../output/scraper/GoogleScraper_bing_quoted_50_pages_categorized_built.json"
        reader = JSONWebPageReader(path)
        webpages = reader.read()
        writer = WekaWebPageTrainingCSV
        out_path = "../GoogleScraper_bing_50_pages_categorized_stemmed.csv"
        i = 0
        cleaner = TextCleaningPipeline(self._configs)
        with writer(out_path) as outf:
            outf.write_header()
            for webpage in webpages:
                i += 1
                if i % 1000:
                    logging.info("Completed {} rows".format(i))
                webpage['text'] = cleaner.process(webpage['text'])
                outf.write(webpage)
