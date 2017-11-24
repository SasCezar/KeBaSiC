import argparse
import os
from time import gmtime, strftime

from kebasic.dao.webpagedao import CSVWebPageDAO
from kebasic.execution.basic import FeatureExtractionExecution, TextCleanerExecution
from kebasic.utils import utils
from kebasic.utils.logger import initialize_logger
from kebasicio.results import SortedPPrintResultWriter

order = ["url", "site_keywords", "MergingRAKE", "MergingTextRank", "MergingTermFrequencies"]


def main(configs):
    cleaner = TextCleanerExecution(configs)
    feature = FeatureExtractionExecution(configs)
    webpages = CSVWebPageDAO(configs['websites_path']).load_webpages()
    cleaned_webages = cleaner.execute(webpages)
    result = feature.execute(cleaned_webages)
    filename = 'keywords_{}.json'.format(strftime("%Y_%m_%d-%H_%M", gmtime()))
    cleaner_configs = cleaner.get_config()
    feature_config = feature.get_config()
    executors_configs = {}
    executors_configs.update(cleaner_configs)
    executors_configs.update(feature_config)
    SortedPPrintResultWriter(order).write("../results/", result, executors_configs)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.json")

    args = parser.parse_args()
    configs = utils.load_configs(args.config_file)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    initialize_logger(configs['log_path'])

    main(configs)
