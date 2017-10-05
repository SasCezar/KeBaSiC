import json
from re import finditer

from jsmin import jsmin


def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0) for m in matches])


def load_configs(config_file):
    with open(config_file, "rt", encoding="utf8") as config_file:
        minified = jsmin(" ".join(config_file.readlines()))
        configs = json.loads(minified)

    return configs
