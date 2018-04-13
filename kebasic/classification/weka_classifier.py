"""
@author: debora.nozza
"""

import weka.core.serialization as serialization
from weka.classifiers import Classifier, Evaluation, PredictionOutput
# %%
from weka.core.converters import Loader
from weka.filters import StringToWordVector

from classification.classifier import AbstractClassifier


class WEKAClassifier(AbstractClassifier):
    """
    Implements a WEKA classifier
    """

    def __init__(self, model_path):
        super().__init__()
        objects_read = serialization.read_all(model_path)
        self._classifier = Classifier(jobject=objects_read[0])
        self._filter_model = StringToWordVector(jobject=objects_read[1])
        self._loader = Loader(classname="weka.core.converters.CSVLoader", options=["-H", "True", "-S", "2", "-N", "1"])
        self._input_name = "../classification/classifier.tmp"
        self._predion_output = PredictionOutput(classname="weka.classifiers.evaluation.output.prediction.CSV")

    def classify(self, text):
        self._create_file(text)
        input = self._loader.load_file(self._input_name)
        filtered_input = self._filter_model.filter(input)
        filtered_input.class_is_first()
        evl = Evaluation(filtered_input)
        evl.test_model(self._classifier, filtered_input, output=self._predion_output)
        prediction = str(self._predion_output).split(",")[2].split(":")[1]
        return prediction

    def _create_file(self, text):
        text_file = open(self._input_name, "w")
        text_file.write("temp," + text)
        text_file.close()

        return
