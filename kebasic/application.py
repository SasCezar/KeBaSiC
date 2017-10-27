import argparse
import csv
import os

from kebasic.dao.webpagedao import CSVWebPageDAO
from kebasic.execution.basic import FeatureExtractionExecution
from kebasic.utils import utils
from kebasic.utils.logger import initialize_logger


def write_csv(result):
    with open('keywords.csv', 'wt', encoding="utf8", newline="") as output_file:
        dict_writer = csv.DictWriter(output_file,
                                     fieldnames=["url", "site_keywords", "RAKE", "TextRank", "TermFrequencies"])
        dict_writer.writeheader()
        dict_writer.writerows(result)


def main(configs):
    executor = FeatureExtractionExecution(configs)
    webpages = CSVWebPageDAO(configs['websites_path']).load_webpages()
    result = executor.execute(webpages)
    write_csv(result)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.json")

    args = parser.parse_args()
    configs = utils.load_configs(args.config_file)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    initialize_logger(configs['log_path'])

    main(configs)
