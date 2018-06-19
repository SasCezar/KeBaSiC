import csv


class Taxonomy(object):
    @staticmethod
    def read(path, header=True):
        taxonomy = Taxonomy._read(path, header)
        reverse_taxonomy = Taxonomy._read_reverse(path, header)
        return Taxonomy._find_parents(taxonomy, reverse_taxonomy)

    @staticmethod
    def read_reverse(path, header=True):
        taxonomy = Taxonomy.read(path, header)

        reversed_taxonomy = {}

        for category_id in taxonomy:
            key = taxonomy[category_id]['parent_category'] + " " + taxonomy[category_id]['category']
            reversed_taxonomy[key.strip()] = taxonomy[category_id]
            reversed_taxonomy[taxonomy[category_id]['category']] = taxonomy[category_id]

        return reversed_taxonomy

    @staticmethod
    def _find_parents(taxonomy, reverse_taxonomy):
        parent_taxonomy = {}
        for category_id in taxonomy:
            result = {}
            is_top_level = len(taxonomy[category_id]) > 1

            parent_category = taxonomy[category_id][0] if is_top_level else ''
            result['parent_category'] = parent_category
            result['parent_category_id'] = reverse_taxonomy[parent_category] if is_top_level else '0'
            x = 1 if is_top_level else 0
            result['category'] = taxonomy[category_id][x]
            result['category_id'] = category_id

            parent_taxonomy[category_id] = result

        return parent_taxonomy

    @staticmethod
    def write(dest, taxonomy, header=None):
        """
        Saves the taxonomy to files

        :param dest: Path where to save the _path
        :param taxonomy:
        :param header: An optional header
        :return:
        """
        with open(dest, "wt", encoding="utf8", newline="") as outf:
            writer = csv.writer(outf)
            writer.writerow(header) if header else None

            for category in taxonomy:
                writer.writerow(category)

    @staticmethod
    def _read_reverse(path, header):
        taxonomy = Taxonomy._read(path, header)

        reversed_taxonomy = {}
        for category_id in taxonomy:
            category = taxonomy[category_id]
            reversed_taxonomy[" ".join(category).strip()] = category_id
            if len(category) > 1:
                reversed_taxonomy[category[1].strip()] = category_id

        return reversed_taxonomy

    @staticmethod
    def _read(path, header=False):
        with open(path, "rt", encoding="utf8") as inf:
            reader = csv.reader(inf)
            next(reader) if header else None
            taxonomy = {}
            for category in reader:
                category_id = category[0].strip()
                lvls = [text.strip() for text in category[1:] if text.strip()]
                taxonomy[category_id] = lvls

        return taxonomy


def read_reverse_taxonomy(path):
    taxonomy = Taxonomy().read_reverse(path, True)
    return taxonomy


def read_taxonomy(path):
    taxonomy = Taxonomy().read(path, True)
    return taxonomy


def read_keys_mapping(query_keys_mapping_path):
    res = {}
    with open(query_keys_mapping_path, "rt", encoding="utf8") as inf:
        reader = csv.reader(inf)
        for query, lvl1, lvl2 in reader:
            res[query] = (lvl1.strip(), lvl2.strip())

    return res


def read_businnes_type_mapping(business_type_mapping_path):
    mapping = {}
    with open(business_type_mapping_path, "rt", encoding="utf8") as inf:
        next(inf)
        for line in inf:
            splitted = line.split(",")
            lvl1 = splitted[0].strip()
            lvl2 = splitted[1].strip()

            result = {'parent_category': lvl1, 'parent_category_id': lvl1,
                      'category': lvl2, 'category_id': lvl2}

            mapping[lvl1.lower()] = result if lvl1 and not lvl2 else None
            mapping[lvl2.lower()] = result if lvl2 else None

    return mapping


def read_jot_taxonomy(query_keys_mapping_path, business_type_mapping_path):
    query_keys_mapping = read_keys_mapping(query_keys_mapping_path)
    business_type_mapping = read_businnes_type_mapping(business_type_mapping_path)

    jot2google = {}
    for query_key in query_keys_mapping:
        lvl1, lvl2 = query_keys_mapping[query_key]
        category = lvl2.lower() if lvl2 and lvl2.lower() in business_type_mapping else lvl1.lower()
        if category == "nan":
            jot2google[query_key] = {}
        else:
            jot2google[query_key] = business_type_mapping[category]

    return jot2google


if __name__ == '__main__':
    test = read_reverse_taxonomy("../../resources/ES/taxonomy/taxonomy.csv")
