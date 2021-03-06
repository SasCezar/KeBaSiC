# NOTE: The original code (from https://github.com/aneesha/RAKE)
# has been extended by a_medelyan (zelandiya)
# with a set of heuristics to decide whether a phrase is an acceptable candidate
# as well as the ability to set frequency and phrase length parameters
# important when dealing with longer documents
#
# NOTE 2: The code published by a_medelyan (https://github.com/zelandiya/RAKE-tutorial)
# has been additionally extended by Marco Pegoraro to implement the adjoined candidate
# feature described in section 1.2.3 of the original paper. Note that this creates the
# need to modify the metric for the candidate score, because the adjoined candidates
# have a very high score (because of the nature of the original score metric)
#
# NOTE 3: The code published by zelandiya (https://github.com/zelandiya/RAKE-tutorial)
# and subsequently edited by Marco Pegoraro has been wrapped and modified to conform
# to our needs. This includes the extension of an abstract class and some minor edits to code.
import logging
import re
from collections import Counter

from feature.keywordextractor import AbstractKeywordExtractor


def is_number(s):
    try:
        float(s) if '.' in s else int(s)
        return True
    except ValueError:
        return False


def separate_words(text, min_word_return_size):
    """
    Utility function to return a list of all words that are have a length greater than a specified number of characters.

    :param text: The text that must be split in to words.
    :param min_word_return_size: The minimum no of characters a word must have to be included.
    """
    splitter = re.compile('[^a-zA-Z0-9_\\+\\-/]')
    words = []
    for single_word in splitter.split(text):
        current_word = single_word.strip().lower()
        # leave numbers in phrase, but don't count as words, since they tend to invalidate
        # textrank_scores of their phrases
        if len(current_word) > min_word_return_size and current_word != '' and not is_number(current_word):
            words.append(current_word)
    return words


def build_stop_word_regex(stop_word_list):
    """
    Given a list of stopwords builds a regexp

    :param stop_word_list:
    :return:
    """
    stop_word_regex_list = []
    for word in set(stop_word_list):
        word_regex = '\\b' + word + '\\b'
        stop_word_regex_list.append(word_regex)
    stop_word_pattern = re.compile('|'.join(stop_word_regex_list), re.IGNORECASE)
    return stop_word_pattern


def extract_adjoined_candidates(sentence_list, keywords_separator, min_keywords, max_keywords, min_freq):
    """
    Extracts the adjoined candidates from a list of sentences and filters them by frequency

    :param sentence_list:
    :param keywords_separator:
    :param min_keywords:
    :param max_keywords:
    :param min_freq:
    :return:
    """
    adjoined_candidates = []
    for s in sentence_list:
        # Extracts the candidates from each single sentence and adds them to the list
        adjoined_candidates += adjoined_candidates_from_sentence(s, keywords_separator, min_keywords, max_keywords)
    # Filters the candidates and returns them
    return filter_adjoined_candidates(adjoined_candidates, min_freq)


def adjoined_candidates_from_sentence(sentence, keywords_separator, min_keywords, max_keywords):
    """
    Extracts the adjoined candidates from a single sentence

    :param sentence:
    :param keywords_separator:
    :param min_keywords:
    :param max_keywords:
    :return:
    """
    # Initializes the candidate list to empty
    candidates = []
    # Splits the sentence to get a list of lowercase words
    sl = sentence.lower().split()
    # For each possible length of the adjoined candidate
    for num_keywords in range(min_keywords, max_keywords + 1):
        # Until the third-last word
        for i in range(0, len(sl) - num_keywords):
            # Position i marks the first word of the candidate. Proceeds only if it'sentence not a stopword
            if sl[i] not in keywords_separator:
                candidate = sl[i]
                # Initializes j (the pointer to the next word) to 1
                j = 1
                # Initializes the word counter. This counts the non-stopwords words in the candidate
                keyword_counter = 1
                contains_stopword = False
                # Until the word count reaches the maximum number of keywords or the end is reached
                while keyword_counter < num_keywords and i + j < len(sl):
                    # Adds the next word to the candidate
                    candidate = candidate + ' ' + sl[i + j]
                    # If it'sentence not a stopword, increase the word counter. If it is, turn on the flag
                    if sl[i + j] not in keywords_separator:
                        keyword_counter += 1
                    else:
                        contains_stopword = True
                    # Next position
                    j += 1

                # Adds the candidate to the list only if:
                # 1) it contains at least a stopword (if it doesn't it'sentence already been considered)
                # AND
                # 2) the last word is not a stopword
                # AND
                # 3) the adjoined candidate keyphrase contains exactly the correct number of keywords (to avoid doubles)
                if contains_stopword and candidate.split()[-1] not in keywords_separator \
                        and keyword_counter == num_keywords:
                    candidates.append(candidate)
    return candidates


def filter_adjoined_candidates(candidates, min_freq):
    """
    Filters the adjoined candidates to keep only those that appears with a certain frequency
    :param candidates:
    :param min_freq:
    :return:
    """

    # Creates a dictionary where the key is the candidate and the value is the frequency of the candidate
    candidates_freq = Counter(candidates)
    filtered_candidates = []

    # Uses the dictionary to filter the candidates
    for candidate in candidates:
        freq = candidates_freq[candidate]
        if freq >= min_freq:
            filtered_candidates.append(candidate)
    return filtered_candidates


def generate_candidate_keywords(sentence_list, stopword_pattern, stop_word_list, min_char_length=1, max_words_length=5,
                                min_words_length_adj=1, max_words_length_adj=1, min_phrase_freq_adj=2):
    phrase_list = []
    for s in sentence_list:
        tmp = re.sub(stopword_pattern, '|', s.strip())
        phrases = tmp.split("|")
        for phrase in phrases:
            phrase = phrase.strip().lower()
            if phrase != "" and is_acceptable(phrase, min_char_length, max_words_length):
                phrase_list.append(phrase)
    phrase_list += extract_adjoined_candidates(sentence_list, stop_word_list, min_words_length_adj,
                                               max_words_length_adj, min_phrase_freq_adj)
    return phrase_list


def is_acceptable(phrase, min_char_length, max_words_length):
    """
    Checks if the phrase respect the constraints imposed in the model creation
    :param phrase:
    :param min_char_length:
    :param max_words_length:
    :return:
    """
    # a phrase must have a min length in characters
    if len(phrase) < min_char_length:
        return 0

    # a phrase must have a max number of words
    words = phrase.split()
    if len(words) > max_words_length:
        return 0

    digits = 0
    alpha = 0
    for i in range(0, len(phrase)):
        if phrase[i].isdigit():
            digits += 1
        elif phrase[i].isalpha():
            alpha += 1

    # a phrase must have at least one alpha character
    if alpha == 0:
        return 0

    # a phrase must have more alpha than digits characters
    if digits > alpha:
        return 0
    return 1


def calculate_word_scores(phrase_list):
    word_frequency = {}
    word_degree = {}
    for phrase in phrase_list:
        word_list = separate_words(phrase, 0)
        word_list_length = len(word_list)
        word_list_degree = word_list_length - 1
        # if word_list_degree > 3: word_list_degree = 3 #exp.
        for word in word_list:
            word_frequency.setdefault(word, 0)
            word_frequency[word] += 1
            word_degree.setdefault(word, 0)
            word_degree[word] += word_list_degree  # orig.
            # word_degree[word] += 1/(word_list_length*1.0) #exp.
    for item in word_frequency:
        word_degree[item] = word_degree[item] + word_frequency[item]

    # Calculate Word textrank_scores = deg(w)/frew(w)
    word_score = {}
    for item in word_frequency:
        word_score.setdefault(item, 0)
        word_score[item] = word_degree[item] / (word_frequency[item] * 1.0)  # orig.
    # word_score[item] = word_frequency[item]/(word_degree[item] * 1.0) # exp.
    return word_score


def generate_candidate_keyword_scores(phrase_list, word_score, min_keyword_frequency=1):
    keyword_candidates = {}
    for phrase in phrase_list:
        if min_keyword_frequency > 1:
            if phrase_list.count(phrase) < min_keyword_frequency:
                continue
        keyword_candidates.setdefault(phrase, 0)
        word_list = separate_words(phrase, 0)
        candidate_score = 0
        for word in word_list:
            candidate_score += word_score[word]
        keyword_candidates[phrase] = candidate_score
    return keyword_candidates


def split_sentences(text):
    """
    Utility function to return a list of sentences.

    :param text: The text that must be split in to sentences.
    """
    sentence_delimiters = re.compile(u'[\\[\\]\n&*.!?,;:\t\\-\\"\\(\\)\\\'\u2019\u2013]')  # Added chars: '&' and '*'
    sentences = sentence_delimiters.split(text)
    return sentences


class RAKE(AbstractKeywordExtractor):
    def __init__(self, language, stopwords, keyword_separator, min_char_length=1, max_words_length=5,
                 min_keyword_frequency=1, min_words_length_adj=1, max_words_length_adj=1,
                 min_phrase_freq_adj=2, lemmize=False, limit=50, keep_all=0):
        """

        Implementation of RAKE - Rapid Automatic Keyword Extraction algorithm as described in:
        Rose, S., D. Engel, N. Cramer, and W. Cowley (2010).
        Automatic keyword extraction from individual documents.
        In M. W. Berry and J. Kogan (Eds.), Text Mining: Applications and Theory. Unknown: John Wiley and Sons, Ltd.


        :param language: Defines the text language, used to load NLTK stopwords in case no stopwords are passed
        :param stopwords: Stopwords that the algorithm uses to delimit sentences and keywords as described in the
        original authors publication
        :param min_char_length: The minimum length for a word to be considered a keyword
        :param max_words_length: The maximum number of words that are considerate a keyword
        :param min_keyword_frequency: The minimum times a words needs to appear in text to be considerate a keyword
        :param min_words_length_adj:
        :param max_words_length_adj:
        :param min_phrase_freq_adj:
        """

        super().__init__(language, stopwords, lemmize, limit, keep_all)

        self._keyword_separator = keyword_separator
        self._min_char_length = min_char_length
        self._max_words_length = max_words_length
        self._min_keyword_frequency = min_keyword_frequency
        self._min_words_length_adj = min_words_length_adj
        self._max_words_length_adj = max_words_length_adj
        self._min_phrase_freq_adj = min_phrase_freq_adj

    def configuration(self, extended=True):
        config_dict = self.__dict__
        if not extended:
            config_dict.pop("_stopwords", None)

        return config_dict

    @property
    def min_char_length(self):
        return self._min_char_length

    @property
    def max_words_length(self):
        return self._max_words_length

    @property
    def min_keyword_frequency(self):
        return self._min_keyword_frequency

    @property
    def min_words_length_adj(self):
        return self.min_words_length_adj

    @property
    def max_words_length_adj(self):
        return self._min_words_length_adj

    @property
    def min_phrase_freq_adj(self):
        return self._min_phrase_freq_adj

    def _extract_keywords(self, text):
        sentence_list = split_sentences(text)
        stop_words_pattern = build_stop_word_regex(self._keyword_separator)
        phrase_list = generate_candidate_keywords(sentence_list, stop_words_pattern, self._keyword_separator,
                                                  self._min_char_length, self._max_words_length,
                                                  self._min_words_length_adj, self._max_words_length_adj,
                                                  self._min_phrase_freq_adj)
        word_scores = calculate_word_scores(phrase_list)
        keyword_candidates = generate_candidate_keyword_scores(phrase_list, word_scores, self._min_keyword_frequency)
        keyword_candidates = keyword_candidates.items()
        return keyword_candidates

    def run(self, text):
        lemmed_text = self._text_lemmatization(text) if self._lemmize else text
        keywords = self._extract_keywords(lemmed_text)
        filtered_keywords = self._filter(keywords)
        sorted_keywords = self._sort(filtered_keywords)
        return sorted_keywords


class MergingRAKE(RAKE):
    """
    Extends the basic RAKE algorithm adding a keyword merge logic based on the proximity of the keywords.
    See :func:'~keywordextractor.AbstractKeywordExtractor._merge' for more details about merging logic.
    """

    def run(self, text):
        lemmed_text = self._text_lemmatization(text) if self._lemmize else text
        keywords = self._extract_keywords(lemmed_text)
        if not keywords:
            return []
        filtered_keywords = self._filter(keywords)
        logging.debug("Keywords extracted")
        merged_keywords = self._merge_keywords(filtered_keywords, text)
        logging.debug("Keywords merged")
        # scaled_keywords = self._score_rescaling(merged_keywords)
        sorted_keywords = self._sort(merged_keywords)
        if self._limit:
            sorted_keywords = sorted_keywords[:self._limit]
        return sorted_keywords
