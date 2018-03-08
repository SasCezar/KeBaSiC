import json
import logging

from domain.webpagebuilder import WebPageBuilder
from executions.basic import TextCleaningPipeline, FeatureExtractionPipeline
from executions.datacrawling import ParallelCrawling
from executions.executor import AbstractExecutor
from feature.normalization import MaxScaling
from feature.resultsjoin import SumScores, InsertScores
from kebasicio.webpageio import BingResultsWebPageReader, WekaWebPageReader, JSONWebPageReader
from kebasicio.weka import WekaWebPageTrainingCSV
from kebasicio.writer import StdOutFileWriter
from utils.taxonomy import read_jot_taxonomy


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
        reader = JSONWebPageReader(path)  # Edit the class according to the structure of the input file
        webpages = reader.read()
        writer = StdOutFileWriter  # Edit the class according to the desired output
        builder = WebPageBuilder()

        out_filename = self._configs['out_path']
        with writer(out_filename, self._configs['std_out']) as outf:
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

                    string_result = json.dumps(result, ensure_ascii=False)
                    outf.write(string_result)
                except Exception:
                    logging.exception("Keyword extraction")
                    continue


class CrawlingExecution(AbstractExecutor):
    def run(self):
        taxonomy = read_jot_taxonomy("../resources/JOT/updated_taxonomy_EN.csv", "../resources/JOT/keys_mapping.txt",
                                     "../resources/JOT/business_type _to_google_category.csv")
        reader = BingResultsWebPageReader
        pages = list(
            reader("../data/GoogleScraper_bing_JOTKeywords_25_pages_language.json", taxonomy).read())

        logging.info("Loaded {}".format(len(pages)))
        crawler = ParallelCrawling({}, 25)
        webpages = crawler.run(pages)
        print("Crawled webpages {}".format(len(webpages)))
        with open("../output/scraper/GoogleScraper_bing_JOTKeywords_25_pages_language_3.json", "wt",
                  encoding="utf8") as jsonout:
            for webpage in webpages:
                jsonout.write(json.dumps(webpage.to_dict(), ensure_ascii=False) + "\n")


class ReformatExecution(AbstractExecutor):
    def run(self):
        # path = "../output/scraper/GoogleScraper_bing_JOTKeywords_25_pages_language_3.json"
        path = "../data/test_set.csv"
        reader = WekaWebPageReader(path)
        webpages = reader.read()
        writer = WekaWebPageTrainingCSV
        out_path = "../test_set_stemmed.csv"
        i = 0
        seen = set()
        builder = WebPageBuilder()
        cleaner = TextCleaningPipeline(self._configs)
        with writer(out_path) as outf:
            outf.write_header()
            for webpage in webpages:
                webpage.pop('text', None)
                built = builder.build(**webpage)
                webpage = built.to_dict()
                if webpage['url'] in seen:
                    continue
                seen.add(webpage['url'])
                i += 1
                logging.info("Completed {} rows".format(i))
                webpage['text'] = cleaner.process(webpage['text'])
                outf.write(webpage)
