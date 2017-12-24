

class WebPage(object):
    def __init__(self, url, html, title, text, meta_keywords, meta_description):
        """
        Represents a generic web page. The class implements methods for decomposing the web page.
        :param url:
        :param html:
        """
        self._url = url
        self._html = html
        self._title = title
        self._text = text
        self._meta_keywords = meta_keywords
        self._meta_description = meta_description

    @property
    def url(self):
        return self._url

    @property
    def html(self):
        return self._html

    @property
    def title(self):
        return self._title

    @property
    def meta_keywords(self):
        return self._meta_keywords

    @property
    def meta_description(self):
        return self._meta_description

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    def to_json(self):
        webpage = {'url': self.url, 'html': self.html, 'title': self.title, 'text': self.text,
                   'meta_keywords': self.meta_keywords, 'meta_description': self.meta_description}

        return webpage
