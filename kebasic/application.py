import argparse
import os
from time import gmtime, strftime

from feature.resultsjoin import SumResults
from kebasic.dao.webpagedao import CSVWebPageDAO
from kebasic.execution.basic import FeatureExtractionExecution, TextCleanerExecution
from kebasic.utils import config
from kebasic.utils.logger import initialize_logger
from kebasicio.results import SortedPPrintResultWriter

order = ["site_keywords", "Combined", "MergingRAKE", "MergingTextRank", "MergingTermFrequencies"]


def main(configs):
    feature_extraction(configs)
    # data_crawling(configs)
    return


def feature_extraction(configs):
    cleaner = TextCleanerExecution(configs)
    feature = FeatureExtractionExecution(configs)
    webpages = CSVWebPageDAO(configs['websites_path']).load_webpages()
    cleaned_webages = cleaner.execute(webpages)
    results = feature.execute(cleaned_webages)
    cleaner_configs = cleaner.get_config()
    feature_config = feature.get_config()
    executors_configs = {}
    executors_configs.update(cleaner_configs)
    executors_configs.update(feature_config)
    for result in results:
        result['keywords']['Combined'] = SumResults().merge(result['keywords'])
    now = strftime("%Y_%m_%d-%H_%M", gmtime())
    filename = "keywords_site_2_{}_sum_combined_max_normalized.txt".format(now)
    SortedPPrintResultWriter(order).write("../results/", filename, results, executors_configs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.json")

    args = parser.parse_args()
    configs = config.load_configs(args.config_file)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    initialize_logger(configs['log_path'])

    main(configs)
