import argparse
import os
from time import gmtime, strftime

from feature.normalization import MaxScaling
from feature.resultsjoin import SumResults, InsertScores
from kebasic.dao.webpagedao import CSVWebPageDAO
from kebasic.execution.basic import FeatureExtractionExecution, TextCleanerExecution
from kebasic.utils import config
from kebasic.utils.logger import initialize_logger
from kebasicio.results import PPrintResultWriter

order = ["site_keywords", "Combined", "MergingRAKE", "MergingTextRank", "MergingTermFrequencies"]


def main(configs):
    feature_extraction(configs)
    # data_crawling(configs)
    return


def feature_extraction(configs):
    cleaner = TextCleanerExecution(configs)
    feature = FeatureExtractionExecution(configs)
    score_normalizer = MaxScaling()

    webpages = CSVWebPageDAO(configs['websites_path']).load_webpages()
    cleaned_webages = cleaner.execute(webpages)
    results = feature.execute(cleaned_webages)

    for result in results:
        for algorithm in result['keywords']:
            keywords = result['keywords']
            keywords[algorithm] = score_normalizer.normalize(result['keywords'][algorithm])

    for result in results:
        site_keywords = result['keywords']['site_keywords']
        result['keywords']['Combined'] = score_normalizer.normalize(SumResults().merge(result['keywords']))
        result['keywords'] = InsertScores().insert(result['keywords']['Combined'], site_keywords)

    executors_configs = {}
    executors_configs.update(cleaner.get_config())
    executors_configs.update(feature.get_config())

    now = strftime("%Y_%m_%d-%H_%M", gmtime())
    filename = "keywords_site_{}_sum_combined_max_normalized.txt".format(now)
    PPrintResultWriter().write("../results/", filename, results, executors_configs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.json")

    args = parser.parse_args()
    configs = config.load_configs(args.config_file)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    initialize_logger(configs['log_path'])

    main(configs)
