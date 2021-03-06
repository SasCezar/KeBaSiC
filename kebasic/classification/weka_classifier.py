"""
@author: debora.nozza
"""
import csv
import os

import weka.core.serialization as serialization
from weka.classifiers import Classifier, Evaluation, PredictionOutput
# %%
from weka.core.converters import Loader
from weka.filters import StringToWordVector

from classification.classifier import AbstractClassifier
from textprocessing.cleaner import Clean4SQL
from textprocessing.stemmer import Stemmer


class WEKAClassifier(AbstractClassifier):
    """
    Implements a WEKA classifier
    """

    def __init__(self, model_path, language):
        super().__init__()
        objects_read = serialization.read_all(model_path)
        self._classifier = Classifier(jobject=objects_read[0])
        self._filter_model = StringToWordVector(jobject=objects_read[1])
        self._loader = Loader(classname="weka.core.converters.CSVLoader", options=["-H", "True", "-S", "2", "-N", "1"])
        self._input_name = "classification/classifier.tmp"
        self._stemmer = Stemmer(language=language)
        self._cleaner = Clean4SQL()

    def classify(self, text):
        stemmed_text = self._stemmer.run(text).strip()
        self._create_file(stemmed_text)
        input_file = self._loader.load_file(self._input_name)
        filtered_input = self._filter_model.filter(input_file)
        filtered_input.class_is_first()
        evl = Evaluation(filtered_input)
        prediction_output = PredictionOutput(classname="weka.classifiers.evaluation.output.prediction.CSV")
        evl.test_model(self._classifier, filtered_input, output=prediction_output)
        prediction = str(prediction_output).split(",")[2].split(":")[1]
        self._delete_file()
        return prediction

    def _create_file(self, text):
        with open(self._input_name, "wt", encoding="utf8", newline="") as inf:
            writer = csv.writer(inf, quoting=csv.QUOTE_ALL)
            writer.writerow(["temp", self._cleaner.run(text.strip())])
        return

    def _delete_file(self):
        try:
            os.remove(self._input_name)
        except OSError:
            pass

