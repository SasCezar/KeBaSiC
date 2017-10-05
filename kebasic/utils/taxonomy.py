import csv
import json

from googletrans import Translator

from kebasic.utils.utils import camel_case_split

translator = Translator()

SRC_LANG = "en"
DST_LANG = "es"


def translate_taxonomy(taxonomy_path):
    with open(taxonomy_path, "rt", encoding="utf8") as inf:
        reader = csv.reader(inf)
        next(reader)

        categories = []
        for category_id, n1, n2 in reader:
            n1 = camel_case_split(n1)
            n2 = camel_case_split(n2)
            translated_n1 = translator.translate(n1, src=SRC_LANG, dest=DST_LANG).text if n1 else ""
            translated_n2 = translator.translate(n2, src=SRC_LANG, dest=DST_LANG).text if n1 else ""

            category = [category_id, n1, n2, translated_n1, translated_n2]

            categories.append(category)

    return categories


def write_taxonomy(categories, out_path, header=None, mask=None):
    with open(out_path, "wt", newline="", encoding="utf8") as outf:
        writer = csv.writer(outf)
        writer.writerow(header) if header else None

        for category in categories:
            row = [element for element, visible in zip(category, mask) if visible] if mask else category
            writer.writerow(row)


def load_configs(config_file):
    with open(config_file) as config_file:
        configs = json.load(config_file)

    return configs


if __name__ == "__main__":
    base_path = "../../resources/taxonomy/"
    filtered_path = base_path + "clean_update_categories.csv"
    out = base_path + "spanish_taxonomy.csv"

    taxonomy = translate_taxonomy(filtered_path)

    write_taxonomy(taxonomy, out, header=['id', 'lvl1', 'lvl2'], mask=[1, 0, 0, 1, 1])
