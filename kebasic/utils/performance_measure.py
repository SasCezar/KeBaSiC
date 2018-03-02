import csv

from utils.taxonomy import read_reverse_taxonomy


def read_predicted(path):
    with open(path, "rt", encoding="ansi") as inf:
        reader = csv.reader(inf, delimiter="\t")
        next(reader)
        for h1, h2, url, text, predicted_level_1, predicted_level_2 in reader:
            yield h1, h2, url, text, predicted_level_1, predicted_level_2


def read_results(file):
    classes_file = file + "_class.txt"
    prob_file = file + "_prob.txt"
    with open(classes_file, "rt", encoding="utf8") as inf:
        classes = inf.readlines()
        classes = [c.strip() for c in classes]

    with open(prob_file, "rt", encoding="utf8") as inf:
        reader = csv.reader(inf, delimiter='\t')
        for line in reader:
            probabilities = [float(x) for x in line if x]
            result = zip(classes, probabilities)
            sorted_result = sorted(result, key=lambda x: x[1], reverse=True)
            yield sorted_result


if __name__ == '__main__':
    lvl1_probs = list(read_results("C:\\Users\\sasce\\Downloads\\results\\data_98cl1"))
    lvl2_probs = list(read_results("C:\\Users\\sasce\\Downloads\\results\\data_98cl2"))
    predicted_classes = list(read_predicted("C:\\Users\\sasce\\Downloads\\results\\predicted_web_98.csv"))

    taxonomy = read_reverse_taxonomy("../../resources/ES/taxonomy/taxonomy.csv")

    with open("prediction_results_top_n_oldfiles.txt", "wt", encoding="utf8", newline="") as outf:
        writer = csv.writer(outf)
        header = ["n", "lvl1", "lvl1 percent", "lvl2", "lvl2 percent"]
        writer.writerow(header)
        for top_n in range(1, 11):
            n = 0
            i_lvl1 = 0
            i_lvl2 = 0
            for lvl1_prob, lvl2_prob, predicted in zip(lvl1_probs, lvl2_probs, predicted_classes):
                h1, h2, url, text, predicted_level_1, predicted_level_2 = predicted
                top_lvl1_predicted = [category.strip() for category, probability in lvl1_prob[:top_n]]
                top_lvl2_predicted = [category.strip() for category, probability in lvl2_prob[:top_n]]

                h1 = taxonomy[h1.strip()]['category_id']
                predicted_file = taxonomy[predicted_level_1.strip()]['category_id']
                if h1.strip() in top_lvl1_predicted:
                    i_lvl1 += 1
                if h2.strip() in top_lvl2_predicted:
                    i_lvl2 += 1
                n += 1

            out_row = [top_n, i_lvl1, i_lvl1 / n * 100, i_lvl2, i_lvl2 / n * 100]
            writer.writerow(out_row)
