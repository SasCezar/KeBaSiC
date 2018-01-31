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


if __name__ == '__main__':
    test = read_reverse_taxonomy("../../resources/ES/taxonomy/taxonomy.csv")
