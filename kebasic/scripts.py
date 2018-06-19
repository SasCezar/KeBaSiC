import argparse

from classification.compute_training_category_classification import train_classifier
from executions.composed import DatasetCrawlingExecution
from utils.config import load_configs
from utils.querygeneration import generate_queries


def generate_keywords(conf):
    template_path = conf.template
    query_out_path = conf.out
    keywords_path = conf.keys

    generate_queries(template_path, query_out_path, keywords_path)


def create_training_dataset(conf):
    configs = load_configs(conf.config)
    configs['output'] = conf.out
    configs['input'] = conf.input
    configs['workers'] = conf.workers
    DatasetCrawlingExecution(configs).run()


def training(configs):
    train_classifier(configs.input, configs.out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    subparser = parser.add_subparsers(dest="subparser")
    script_parser = subparser.add_parser("query")

    script_parser.add_argument("--out", type=str)
    script_parser.add_argument("--template", type=str)
    script_parser.add_argument("--keys", type=str)

    script_parser = subparser.add_parser("dataset")
    script_parser.add_argument("--input", type=str)
    script_parser.add_argument("--out", type=str)
    script_parser.add_argument("--workers", type=int)
    script_parser.add_argument("--config", default="config.json")

    script_parser = subparser.add_parser("train")
    script_parser.add_argument("--input", type=str)
    script_parser.add_argument("--out", type=str)

    args = parser.parse_args()

    if args.subparser == "query":
        generate_keywords(args)

    if args.subparser == "dataset":
        create_training_dataset(args)

    if args.subparser == "train":
        training(args)
