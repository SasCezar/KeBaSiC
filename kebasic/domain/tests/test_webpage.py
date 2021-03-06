import logging
import unittest
from difflib import SequenceMatcher

from domain.webpagebuilder import WebPageBuilder

url = "http://www.abogadosvilagarcia.es/"


def clean(text):
    return ' '.join(text.split())


abogados_html = WebPageBuilder().build(url)
ground_truth_keywords = "Abogado en Vilagarcía, despacho de abogados en Vilagarcía, mediación familiar en Vilagarcía, abogado accidentes en Vilagarcía."


class TestWebPage(unittest.TestCase):
    def test_download(self):
        cleaned_abogados_html = clean(abogados_html.html).replace(" ", "")

        with open("abogadosvilagarcia.html", "rt", encoding="utf8") as inf:
            text = "".join(inf.readlines())
            url_source = clean(text).replace(" ", "")

        similarity = SequenceMatcher(None, cleaned_abogados_html, url_source).ratio()
        logging.info("HTML Similarity: {}".format(similarity))
        self.assertTrue(similarity > 0.85)

    def test_text_extraction(self):
        abogados_text = clean(abogados_html.text)

        with open("abogadosvilagarcia.txt", "rt", encoding="utf8") as inf:
            text = " ".join(inf.readlines())
            visible_text = clean(text)

        similarity = SequenceMatcher(None, abogados_text.lower(), visible_text.lower()).ratio()
        logging.info("Visible Text Similarity: {}".format(similarity))
        self.assertTrue(similarity > 0.95)

    def test_metadata(self):
        abogados_keywords = abogados_html.meta_keywords

        self.assertEqual(abogados_keywords, ground_truth_keywords)

    """
    def test_links(self):
        raise NotImplemented()

    """


if __name__ == '__main__':
    unittest.main()
