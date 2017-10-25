import csv
import os

from googletrans import Translator

from kebasic.utils.utils import camel_case_split, load_configs


def translate_taxonomy(taxonomy_path, src_lang="en", dst_lang="es"):
    """
    Given a taxonomy of second level, translates the categories using Google Translate

    :param taxonomy_path:
    :param src_lang:
    :param dst_lang:
    :return:
    """
    translator = Translator()
    with open(taxonomy_path, "rt", encoding="utf8") as inf:
        reader = csv.reader(inf)
        next(reader)

        categories = []
        for category_id, n1, n2 in reader:
            n1 = camel_case_split(n1)
            n2 = camel_case_split(n2)
            translated_n1 = translator.translate(n1, src=src_lang, dest=dst_lang).text if n1 else ""
            translated_n2 = translator.translate(n2, src=src_lang, dest=dst_lang).text if n1 else ""

            category = [category_id, n1, n2, translated_n1, translated_n2]

            categories.append(category)

    return categories


def write_taxonomy(categories, out_path, header=None, mask=None):
    """
    Saves the taxonomy to files

    :param categories: Taxonomy :param out_path: Path where to save the file
    :param header: An optional header
    :param mask: Filter some values of categories (eg categories=[id, lvl1, lvl2, es_lvl1, es_lvl2], mask=[1,0,0,1,1],
        result=[id, es_lvl1, es_lvl2]
    :return:
    """
    with open(out_path, "wt", newline="", encoding="utf8") as outf:
        writer = csv.writer(outf)
        writer.writerow(header) if header else None

        for category in categories:
            row = [element for element, visible in zip(category, mask) if visible] if mask else category
            writer.writerow(row)


def main():
    config_path = "../config.json"

    config = load_configs(config_path)

    os.chdir("..")

    src = config.get("taxonomy_translate_from", None)
    dst = config.get("taxonomy_translate_to", "es")
    taxonomy = translate_taxonomy(config['original_taxonomy'], src_lang=src, dst_lang=dst)

    header = config.get("taxonomy_header", ["id", "lvl1", "lvl2"])
    mask = config.get("taxonomy_mask", [1, 0, 0, 1, 1])
    write_taxonomy(taxonomy, config['taxonomy_path'], header=header, mask=mask)


if __name__ == "__main__":
    main()
