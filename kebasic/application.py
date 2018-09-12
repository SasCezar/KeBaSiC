import argparse
import os

from executions.composed import KeywordsExecution
from executions.composed import DatasetCrawlingExecution
from executions.composed import ReformatExecution

from utils import config
from utils.logger import initialize_logger

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-config_file", default="config.json")
    parser.add_argument("-input_path", default="")
    parser.add_argument("-out_path", default="")
    parser.add_argument("-std_out", action='store_true', default=False)

    parser.add_argument('-log', action='store_true', default=False)
    parser.add_argument('-log_path', default="../log")

    args = parser.parse_args()
    configs = config.load_configs(args.config_file)
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    configs.update(vars(args))

    initialize_logger(configs['log_path'], configs['log'])

    KeywordsExecution(configs).run()
    #DatasetCrawlingExecution(configs).run()
    #ReformatExecution(configs).run()
