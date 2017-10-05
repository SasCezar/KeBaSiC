import json
from re import finditer


def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0) for m in matches])


def load_configs(config_file):
    with open(config_file) as config_file:
        configs = json.load(config_file)

    return configs
