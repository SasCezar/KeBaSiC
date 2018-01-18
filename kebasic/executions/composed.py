import json
import logging
from time import strftime, gmtime

from datasources.webpagedao import JSONWebPageReader, WekaWebPageReader
from executions.basic import TextCleaningPipeline, FeatureExtractionPipeline
from executions.datacrawling import ParallelCrawling
from executions.executor import AbstractExecutor
from feature.normalization import MaxScaling
from feature.resultsjoin import SumScores, InsertScores
from kebasicio.weka import WekaResultsTrainingCSV


class KeywordsExecution(AbstractExecutor):
    def run(self):
        cleaner = TextCleaningPipeline(self._configs)
        feature = FeatureExtractionPipeline(self._configs)
        scores_normalizer = MaxScaling()
        scores_merger = SumScores()
        file = self._configs['file']
        path = "../data/{}".format(file)
        reader = WekaWebPageReader(path)

        webpages = reader.load_webpages()

        now = strftime("%Y_%m_%d-%H_%M", gmtime())
        filename = "keywords_{}_{}_sum_combined_max_normalized.txt".format(file, now)

        writer = WekaResultsTrainingCSV
        with writer(filename) as outf, open("dump_{}.json".format(file), "wt", encoding="utf8") as dump:
            for webpage in webpages:
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
                    # result.update(webpages_category[result['url']])
                    result['parent_category_id'] = webpage.parent_category_id
                    result['category_id'] = webpage.category_id

                    outf.write(result)
                except Exception as e:
                    print(e)
                    continue

        """
        executors_configs = {}
        executors_configs.update(cleaner.get_config())
        executors_configs.update(feature.get_config())
        """


class CrawlingExecution(AbstractExecutor):
    def run(self):
        pages = list(
            JSONWebPageReader("../output/scraper/GoogleScraper_bing_quoted_query_categorized.json").load_webpages())

        writer = WekaWebPageTrainingCSV
        crawler = ParallelCrawling({}, 32)
        webpages = crawler.run(pages)
        print("crawled webpages {}".format(len(webpages)))
        with writer("../output/scraper/GoogleScraper_bing_quoted_query_categorized_built.csv") as csvout, \
                open("../output/scraper/GoogleScraper_bing_quoted_query_categorized_built.json", "wt",
                     encoding="utf8") as jsonout:
            csvout.write_header()
            for webpage in webpages:
                csvout.write(webpage.to_dict())
                jsonout.write(json.dumps(webpage.to_dict(), ensure_ascii=False) + "\n")
