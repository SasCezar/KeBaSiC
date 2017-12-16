import json

from jsmin import jsmin


def load_configs(config_file):
    with open(config_file, "rt", encoding="utf8") as config_file:
        minified = jsmin(" ".join(config_file.readlines()))
        configs = json.loads(minified)

    return configs
