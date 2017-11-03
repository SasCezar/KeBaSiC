import itertools
import logging

import networkx as nx
import nltk

from kebasic.feature.keywordextractor import AbstractKeywordExtractor


def setup_environment():
    """
    Download required resources.
    """
    nltk.download('punkt')
    nltk.download('averaged_perceptron_tagger')
    logging.info('Completed resource downloads.')


def filter_for_tags(tagged, tags=None):
    """
    Apply syntactic filters based on POS tags.

    :param tagged:
    :param tags:
    :return:
    """
    if tags is []:
        return tagged
    if tags is None:
        tags = ['NN']
    return [item for item in tagged if item[1] in tags]


def normalize(tagged):
    """
    Return a list of tuples with the first item's periods removed.

    :param tagged:
    :return:
    """
    return [(item[0].replace('.', ''), item[1]) for item in tagged]


def unique_everseen(iterable, key=None):
    """
    List unique elements in order of appearance.

    Examples:
        unique_everseen('AAAABBBCCDAABBB') --> A B C D
        unique_everseen('ABBCcAD', str.lower) --> A B C D
    """
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in [x for x in iterable if x not in seen]:
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element


def levenshtein_distance(first, second):
    """
    Return the Levenshtein distance between two strings.

    Based on:
        http://rosettacode.org/wiki/Levenshtein_distance#Python
    """
    if len(first) > len(second):
        first, second = second, first
    distances = range(len(first) + 1)
    for index2, char2 in enumerate(second):
        new_distances = [index2 + 1]
        for index1, char1 in enumerate(first):
            if char1 == char2:
                new_distances.append(distances[index1])
            else:
                new_distances.append(1 + min((distances[index1],
                                              distances[index1 + 1],
                                              new_distances[-1])))
        distances = new_distances
    return distances[-1]


def build_graph(nodes):
    """
    Return a networkx graph instance.

    :param nodes: List of hashables that represent the nodes of a graph.
    """
    gr = nx.Graph()  # initialize an undirected graph
    gr.add_nodes_from(nodes)
    node_pairs = list(itertools.combinations(nodes, 2))

    # add edges to the graph (weighted by Levenshtein distance)
    for pair in node_pairs:
        first_string = pair[0]
        second_string = pair[1]
        strings_distance = levenshtein_distance(first_string, second_string)
        gr.add_edge(first_string, second_string, weight=strings_distance)

    return gr


def postprocessing_key_phrases(keyphrases, textlist):
    """
    Take keyphrases with multiple words into consideration as done in the paper.
    If two words are adjacent in the text and are selected as keywords, join them together

    :param keyphrases:
    :param textlist:
    :return:
    """
    modified_key_phrases = set([])
    # keeps track of individual keywords that have been joined to form a keyphrase
    dealt_with = set([])
    i = 0
    j = 1
    while j < len(textlist):
        first = textlist[i]
        second = textlist[j]
        if first in keyphrases and second in keyphrases:
            keyphrase = first + ' ' + second
            modified_key_phrases.add(keyphrase)
            dealt_with.add(first)
            dealt_with.add(second)
        else:
            if first in keyphrases and first not in dealt_with:
                modified_key_phrases.add(first)

            # if this is the last word in the text, and it is a keyword, it
            # definitely has no chance of being a keyphrase at this point
            if j == len(textlist) - 1 and second in keyphrases and second not in dealt_with:
                modified_key_phrases.add(second)

        i = i + 1
        j = j + 1

    return modified_key_phrases


def mean_scores(scores, keywords):
    result = []
    for keyword in keywords:
        weight = 0
        words = keyword.split()
        elements = 0
        for word in words:
            weight += scores.get(word, 0)
            elements += 1

        mean = weight / elements if weight else 0
        result.append((keyword, mean))

    return result


class TextRank(AbstractKeywordExtractor):
    """
    A NLTK based implementation of TextRank as defined in: "TextRank: Bringing Order into Texts" by Mihalcea et al. (2004)
    """

    def __init__(self, language, limit=None, filter_pos_tags=None):
        super().__init__(language)
        self._filter_tags = filter_pos_tags
        self._limit = limit

    def run(self, text):
        """
        Return a set of key phrases.

        :param text: A string.
        """
        # tokenize the text using nltk
        word_tokens = nltk.word_tokenize(text, language=self._language)

        # assign POS tags to the words in the text
        tagged = nltk.pos_tag(word_tokens)
        textlist = [x[0] for x in tagged]

        tagged = filter_for_tags(tagged, tags=self._filter_tags)
        tagged = normalize(tagged)

        unique_word_set = unique_everseen([x[0] for x in tagged])
        word_set_list = list(unique_word_set)

        # this will be used to determine adjacent words in order to construct
        # keyphrases with two words

        graph = build_graph(word_set_list)

        # Page Rank - initial value of 1.0, error tolerance of 0,0001,
        calculated_page_rank = nx.pagerank(graph, weight='weight')

        # most important words in descending order of importance
        keyphrases = sorted(calculated_page_rank, key=calculated_page_rank.get, reverse=True)

        # the number of keyphrases returned will be relative to the size of the
        # text (a third of the number of vertices)
        one_third = len(word_set_list) // 3 if not self._limit else self._limit
        keyphrases = keyphrases[0:one_third + 1]

        modified_key_phrases = postprocessing_key_phrases(keyphrases, textlist)

        # sorted_scores = sorted([(k, v) for k, v in calculated_page_rank.items()], key=lambda x: x[1], reverse=True)
        result = self._sort(mean_scores(calculated_page_rank, modified_key_phrases))

        return result
