import csv
import glob

import pandas


class BusinessKeywords(object):
    def __init__(self, path):
        self._workbook = pandas.ExcelFile(path)

    def read_keywords(self):
        sheet = self._workbook.parse(self._workbook.sheet_names[0])

        tuples = sheet.itertuples()
        next(tuples)
        for row in sheet.itertuples():
            print(row)
            if len(row) < 4:
                yield row[1].strip().lower(), str(row[2]).strip(), ""
            else:
                yield row[1].strip().lower(), str(row[2]).strip(), str(row[3]).strip()


if __name__ == '__main__':
    files = glob.glob("C:\\Users\\sasce\\Downloads\\KW data base per business type\\*.xlsx")

    out_path = "keys.txt"

    print(len(files))
    with open(out_path, "wt", encoding="utf8", newline="") as outf, \
            open("keys_mapping.txt", "wt", encoding="utf8", newline="") as outf2:
        writer = csv.writer(outf, quoting=csv.QUOTE_NONE, quotechar="")
        mapping_writer = csv.writer(outf2, quoting=csv.QUOTE_NONE, quotechar="")
        for file in files:
            print("Working file: {}".format(file))
            file_kewyords = BusinessKeywords(file).read_keywords()

            for keyword in file_kewyords:
                writer.writerow(["\"{}\" language:es".format(keyword[0])])
                mapping_writer.writerow(keyword)
