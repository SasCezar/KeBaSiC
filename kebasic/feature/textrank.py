import itertools
import re

import networkx as nx
from stanfordcorenlp import StanfordCoreNLP

from kebasic.feature.keywordextractor import AbstractKeywordExtractor


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
        raise Exception("Filter tags cannot be None")
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
        result.append((keyword, round(mean, 9)))

    return result


LANG_CODES = {"spanish": "es"}


class TextRank(AbstractKeywordExtractor):
    """
    A NLTK based implementation of TextRank as defined in: "TextRank: Bringing Order into Texts" by Mihalcea et al. (2004)
    """

    def __init__(self, language, filter_pos_tags=None, core_nlp="http://127.0.0.1:9000", lemmize=False):
        super().__init__(language, lemmize=lemmize)
        self._filter_tags = filter_pos_tags
        if "http" in core_nlp:
            server, port = core_nlp.rsplit(":", maxsplit=1)
            self.nlp = StanfordCoreNLP(server, port=int(port), lang=LANG_CODES[language])
        else:
            self.nlp = StanfordCoreNLP(core_nlp, lang=LANG_CODES[language])

    def run(self, text):
        """
        Return a set list of keyword sorted by score.

        :param text: A string.
        """
        keyword_candidates = self._extract_keywords(text)
        keywords = self._filter(keyword_candidates)
        merged_keywords = self._merge_keywords(keywords, text)
        lemmed_keywords = self._keywords_lemmatization(keywords) if self._lemmize else merged_keywords
        sorted_keywords = self._sort(lemmed_keywords)
        return sorted_keywords

    def _extract_keywords(self, text):
        tagged = self.nlp.pos_tag(text)

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
        one_third = len(word_set_list) // 3
        keyphrases = keyphrases[0:one_third + 1]

        keyword_candidates = [(k, calculated_page_rank[k]) for k in keyphrases if k in calculated_page_rank]

        return keyword_candidates

    def _merge_keywords(self, keywords, text):
        textlist = re.findall(r"(\w+)", text, re.UNICODE)
        merged = postprocessing_key_phrases([k[0] for k in keywords], textlist)
        calculated_page_rank = dict(keywords)
        keyword_candidates = mean_scores(calculated_page_rank, merged)

        return keyword_candidates


class MergingTextRank(TextRank):
    def run(self, text):
        keywords = self._extract_keywords(text)
        filtered_keywords = self._filter(keywords)
        merged_keywords = super(TextRank, self)._merge_keywords(filtered_keywords, text)
        lemmed_keywords = self._keywords_lemmatization(merged_keywords) if self._lemmize else merged_keywords
        # scaled_keywords = self._score_rescaling(lemmed_keywords)
        sorted_keywords = self._sort(lemmed_keywords)
        return sorted_keywords
