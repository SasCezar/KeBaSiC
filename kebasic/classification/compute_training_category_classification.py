# -*- coding: utf-8 -*-
"""
Created on Mon Apr  9 17:24:39 2018

@author: debora.nozza
"""

import weka.core.jvm as jvm
import weka.core.serialization as serialization
from weka.classifiers import Classifier
from weka.core.converters import Loader
from weka.core.tokenizers import Tokenizer
from weka.filters import StringToWordVector, Filter


def get_bow(data):
    separators = " \\r \\t.,;:\\\'\\\"()?!\\\\|£$\\\%&/()=?^*+-][#@-_:.;,\”"
    tokenizer = Tokenizer(classname="weka.core.tokenizers.WordTokenizer", options=["-delimiters", separators])
    s2wv = StringToWordVector(options=["-W", "1000", "-L", "-C", "-R", "last"])
    s2wv.tokenizer = tokenizer
    s2wv.inputformat(data)
    filtered = s2wv.filter(data)

    return filtered, s2wv


def train_classifier(training_path, outpath):
    jvm.start(packages=True)
    loader = Loader(classname="weka.core.converters.CSVLoader", options=["-H", "True", "-S", "3", "-N", "2", "-R", "1"])
    training_data = loader.load_file(training_path)
    remove = Filter(classname="weka.filters.unsupervised.attribute.Remove", options=["-R", "first"])
    remove.inputformat(training_data)
    training_data = remove.filter(training_data)

    filtered_train, filter_model = get_bow(training_data)

    filtered_train.class_is_first()

    # %% Classify Training Data

    classifier = Classifier("weka.classifiers.functions.LibSVM", options=["-K", "0"])
    classifier.build_classifier(filtered_train)

    # %% Save Models
    serialization.write_all(outpath, [classifier, filter_model])
    jvm.stop()
