import argparse
import csv
import os
from time import gmtime, strftime

from feature.normalization import MaxScaling
from feature.resultsjoin import SumResults, InsertScores
from kebasic.datasources.webpagedao import CSVCatalogactionReader, MongoWebPageReader
from kebasic.execution.basic import FeatureExtractionExecution, TextCleanerExecution
from kebasic.utils import config
from kebasic.utils.logger import initialize_logger
from kebasicio.results import PPrintResultWriter
from kebasicio.weka import WekaTrainigCSV
from utils.taxonomy import read_reverse_taxonomy

order = ["site_keywords", "Combined", "MergingRAKE", "MergingTextRank", "MergingTermFrequencies"]


def main(configs):
    feature_extraction(configs)
    # data_crawling(configs)
    return


def data_crawling(configs):
    configs['preprocessing_algorithms'].insert(-2, 'textprocessing.cleaner.StopWordsCleaner')
    configs['preprocessing_algorithms'].insert(-4, 'textprocessing.cleaner.Clean4SQL')
    cleaner = TextCleanerExecution(configs)
    ontology = read_reverse_taxonomy(configs['taxonomy_path'])

    reader = CSVCatalogactionReader("catalogación_test.csv", ontology)
    webpages = list(reader.load_webpages())
    # crawler = ParallelCrawling(configs, 5)
    # webpages = crawler.run(urls)
    cleaned_webpages = cleaner.execute(webpages)
    writer = WekaTrainigCSV("catalogacion_test.csv")
    writer.write(cleaned_webpages)


def feature_extraction(configs):
    cleaner = TextCleanerExecution(configs)
    feature = FeatureExtractionExecution(configs)
    score_normalizer = MaxScaling()

    ontology = read_reverse_taxonomy(configs['taxonomy_path'])
    # webpages = CSVWebPageReader(configs['websites_path']).load_webpages()
    # reader = CSVCatalogactionReader("catalogación_test.csv", ontology)
    # webpages = reader.load_webpages()
    webpages = MongoWebPageReader(None).load_webpages()
    cleaned_webages = cleaner.execute(webpages)
    results = feature.execute(cleaned_webages)

    for result in results:
        for algorithm in result['keywords']:
            keywords = result['keywords']
            keywords[algorithm] = score_normalizer.normalize(result['keywords'][algorithm])

    webpages_category = {}
    for webpage in cleaned_webages:
        webpages_category[webpage.url] = {'category_id': webpage.category_id,
                                          'parent_category_id': webpage.parent_category_id, }

    with open("bing_results.txt", "wt", encoding="utf8", newline='') as outf:
        writer = csv.writer(outf, quoting=csv.QUOTE_ALL)
        for result in results:
            site_keywords = result['keywords']['site_keywords']
            result['keywords']['Combined'] = score_normalizer.normalize(SumResults().merge(result['keywords']))
            result['keywords'] = InsertScores().insert(result['keywords']['Combined'], site_keywords)
            result.update(webpages_category[result['url']])

            parent_category_id = result['parent_category_id']
            category_id = result['category_id']
            url = result['url']
            keywords = " ".join([keyword for keyword, _ in result['keywords']])
            if not keywords:
                continue
            row = [parent_category_id, category_id, url, keywords]
            writer.writerow(row)

    executors_configs = {}
    executors_configs.update(cleaner.get_config())
    executors_configs.update(feature.get_config())

    now = strftime("%Y_%m_%d-%H_%M", gmtime())
    filename = "keywords_bing_{}_sum_combined_max_normalized.txt".format(now)
    PPrintResultWriter().write("../results/", filename, results, executors_configs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.json")

    args = parser.parse_args()
    configs = config.load_configs(args.config_file)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    initialize_logger(configs['log_path'])

    main(configs)
