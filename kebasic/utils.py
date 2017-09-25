import csv
from re import finditer

from googletrans import Translator

translator = Translator()


def camel_case_split(identifier):
    matches = finditer('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', identifier)
    return " ".join([m.group(0) for m in matches])


def reformat_taxonomy(taxonomy_path, out_path):
    with open(taxonomy_path, "rt", encoding="utf8") as inf, \
            open(out_path, "wt", newline="", encoding="utf8") as outf:
        writer = csv.writer(outf)
        reader = csv.reader(inf)
        next(reader)
        category = ["ID", "N1", "N2", "SN1", "SPN2"]
        writer.writerow(category)
        for category_id, n1, n2 in reader:
            n1 = camel_case_split(n1)
            n2 = camel_case_split(n2)
            translated_n1 = translator.translate(n1, src="en", dest="es").text if n1 else ""
            translated_n2 = translator.translate(n2, src="en", dest="es").text if n1 else ""

            category = [category_id, n1, n2, translated_n1, translated_n2]

            writer.writerow(category)
            outf.flush()


if __name__ == "__main__":
    base_path = "../resources/taxonomy/"
    verticals_path = base_path + "verticals.csv"
    client_path = base_path + "client.csv"
    filtered_path = base_path + "filtered.csv"

    out = base_path + "taxonomy.csv"

    reformat_taxonomy(filtered_path, out)
