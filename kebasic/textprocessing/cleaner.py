import re
from abc import ABC


class AbstractCleaner(ABC):
    def __init__(self):
        self.re_match = None
        self.sub = " "

    def run(self, text):
        cleaned_text = self.re_match.sub(self.sub, text)
        return cleaned_text

    def configuration(self):
        return self.__dict__


class WordsWithNumbersCleaner(AbstractCleaner):
    """
    Removes words that contain digits.

    Example: "Hello Earth! This is WorldA90" --> "Hello Earth! This is "
    """
    def __init__(self):
        super().__init__()
        self.re_match = re.compile(r"\S*\d+\S*", re.IGNORECASE)


class URLCleaner(AbstractCleaner):
    """
    Removes URLs from the text

    Example: "Check out this page: google.com" --> "Check out this page: "
    """
    def __init__(self):
        super().__init__()
        self.re_match = re.compile(
            r"""(?i)\b((?:https?:(?:/{1,3}|[a-z0-9%])|[a-z0-9.\-]+[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)/)(?:[^\s()<>{}\[\]]+|\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\))+(?:\([^\s()]*?\([^\s()]+\)[^\s()]*?\)|\([^\s]+?\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’])|(?:(?<!@)[a-z0-9]+(?:[.\-][a-z0-9]+)*[.](?:com|net|org|edu|gov|mil|aero|asia|biz|cat|coop|info|int|jobs|mobi|museum|name|post|pro|tel|travel|xxx|ac|ad|ae|af|ag|ai|al|am|an|ao|aq|ar|as|at|au|aw|ax|az|ba|bb|bd|be|bf|bg|bh|bi|bj|bm|bn|bo|br|bs|bt|bv|bw|by|bz|ca|cc|cd|cf|cg|ch|ci|ck|cl|cm|cn|co|cr|cs|cu|cv|cx|cy|cz|dd|de|dj|dk|dm|do|dz|ec|ee|eg|eh|er|es|et|eu|fi|fj|fk|fm|fo|fr|ga|gb|gd|ge|gf|gg|gh|gi|gl|gm|gn|gp|gq|gr|gs|gt|gu|gw|gy|hk|hm|hn|hr|ht|hu|id|ie|il|im|in|io|iq|ir|is|it|je|jm|jo|jp|ke|kg|kh|ki|km|kn|kp|kr|kw|ky|kz|la|lb|lc|li|lk|lr|ls|lt|lu|lv|ly|ma|mc|md|me|mg|mh|mk|ml|mm|mn|mo|mp|mq|mr|ms|mt|mu|mv|mw|mx|my|mz|na|nc|ne|nf|ng|ni|nl|no|np|nr|nu|nz|om|pa|pe|pf|pg|ph|pk|pl|pm|pn|pr|ps|pt|pw|py|qa|re|ro|rs|ru|rw|sa|sb|sc|sd|se|sg|sh|si|sj|Ja|sk|sl|sm|sn|so|sr|ss|st|su|sv|sx|sy|sz|tc|td|tf|tg|th|tj|tk|tl|tm|tn|to|tp|tr|tt|tv|tw|tz|ua|ug|uk|us|uy|uz|va|vc|ve|vg|vi|vn|vu|wf|ws|ye|yt|yu|za|zm|zw)\b/?(?!@)))""",
            re.IGNORECASE)


class MailCleaner(AbstractCleaner):
    """
    Removes e-mail address like strings from the text

    Example: "Send me an email at this address: some.random@mail.com" --> "Send me an email at this address: "
    """
    def __init__(self):
        super().__init__()
        self.re_match = re.compile(
            r"""([a-z0-9!#$%&'*+\/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+\/=?^_`{|}~-]+)*(@|\sat\s)(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?(\.|\sdot\s))+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?)""")


class MultipleSpacesCleaner(AbstractCleaner):
    """
    Removes multiple spaces

    Example "This  is a poor    formatted text" --> "This is a poor formatted text"
    """
    def run(self, text):
        result = " ".join(text.split())
        return result


class NonPunctuationSymbolsCleaner(AbstractCleaner):
    """
    Removes unwanted chars from text, it maintains punctuation, chars, and digits

    Example: "This is a symbol € for euro, another one is (." --> This is a symbol  for euro, another one is ."
    """
    def __init__(self):
        super().__init__()
        self.re_match = re.compile(r"""[^!"&':;?,\.\w\d ]+""")


class DigitsCleaner(AbstractCleaner):
    """
    Removes numbers
    """
    def __init__(self):
        super().__init__()
        self.re_match = re.compile(r"""\b\d+\b""")


class CommonWords(AbstractCleaner):
    """
    Removes common words from the text
    """
    def __init__(self, words_path):
        """
        :param words_path: The path od the file containing the words, one for each line
        """
        super().__init__()
        with open(words_path, "rt", encoding="utf8") as inf:
            words = set(inf.readlines())

        pattern = []
        for word in words:
            word = word.strip()
            pattern.append(r"\b" + word + r"\b")

        pattern = "|".join(pattern)
        self.re_match = re.compile(pattern, re.IGNORECASE)


class PunctuationSpacesCleaner(AbstractCleaner):
    """
    Removes spaces between words and punctuation, it also removes duplicate punctuation preferring the first one.

    Example: "This is fixed , also this!!!!! and this .,."  -->  This is fixed, also this! and this."
    """

    def __init__(self):
        super().__init__()
        self.re_match = re.compile(r"""(\s*(?P<punctuation>[!\"&':;?,\.]+))+""")
        self.sub = lambda x: x.group("punctuation").strip()[0]
