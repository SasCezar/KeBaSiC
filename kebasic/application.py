import argparse
import os

from executions.composed import CrawlingExecution
from utils import config
from utils.logger import initialize_logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.json")

    args = parser.parse_args()
    configs = config.load_configs(args.config_file)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    initialize_logger(configs['log_path'])

    # KeywordsExecution(configs).run()
    CrawlingExecution(configs).run()
    # ReformatExecution(configs).run()
