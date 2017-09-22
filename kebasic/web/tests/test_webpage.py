import logging
import unittest
from difflib import SequenceMatcher

from kebasic.web.webpage import WebPage

url = "http://www.abogadosvilagarcia.es/"


def clean(text):
    return ' '.join(text.split())


abogados_html = WebPage(url).download()
abogados_html.parse()


class TestWebPage(unittest.TestCase):
    def test_download(self):
        """
        Tests if the class downloads all and the same content contained in the page.
        :return:
        """
        cleaned_abogados_html = clean(abogados_html.html).replace(" ", "")

        with open("abogadosvilagarcia.html", "rt", encoding="utf8") as inf:
            text = "".join(inf.readlines())
            url_source = clean(text).replace(" ", "")

        similarity = SequenceMatcher(None, cleaned_abogados_html, url_source).ratio()
        logging.info("HTML Similarity: {}".format(similarity))

        # Threshold denominated using euristics
        # Differences are due to order of attributes
        self.assertTrue(similarity > 0.85)

    def test_text_extraction(self):
        """
        Test the result of visible test extracted by the class

        :return:
        """
        abogados_text = clean(abogados_html.text)

        with open("abogadosvilagarcia.txt", "rt", encoding="utf8") as inf:
            text = " ".join(inf.readlines())
            visible_text = clean(text)

        similarity = SequenceMatcher(None, abogados_text.lower(), visible_text.lower()).ratio()
        logging.info("Visible Text Similarity: {}".format(similarity))
        # Threshold denominated using euristics
        # Differences are due to spaces and minor chars
        self.assertTrue(similarity > 0.95)

    """
    def test_metadata(self):
        raise NotImplemented()

    def test_links(self):
        raise NotImplemented()

    """


if __name__ == '__main__':
    unittest.main()
