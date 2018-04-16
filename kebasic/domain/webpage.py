class WebPage(object):
    """
    Represents a generic web page.
    """

    def __init__(self, url, html, title=None, text=None, meta_keywords=None, meta_description=None, category=None,
                 parent_category=None, category_id=None, parent_category_id=None, meta_tags=None, links_text=None):
        """
        :param url:
        :param html:
        """
        self._url = url
        self._html = html
        self._title = title
        self._text = text
        self._meta_keywords = meta_keywords
        self._meta_description = meta_description
        self._category = category
        self._category_id = category_id
        self._parent_category_id = parent_category_id
        self._parent_category = parent_category
        self._meta_tags = meta_tags
        self._links_text = links_text

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

    @meta_keywords.setter
    def meta_keywords(self, value):
        self._meta_keywords = value

    @property
    def meta_description(self):
        return self._meta_description

    @meta_description.setter
    def meta_description(self, value):
        self._meta_description = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value

    @property
    def category(self):
        return self._category

    @category.setter
    def category(self, value):
        self._category = value

    @property
    def parent_category(self):
        return self._parent_category

    @parent_category.setter
    def parent_category(self, value):
        self._parent_category = value

    @property
    def category_id(self):
        return self._category_id

    @category_id.setter
    def category_id(self, value):
        self._category_id = value

    @property
    def parent_category_id(self):
        return self._parent_category_id

    @parent_category_id.setter
    def parent_category_id(self, value):
        self._parent_category_id = value

    def to_dict(self):
        webpage = {'url': self.url, 'html': self.html, 'title': self.title, 'text': self.text,
                   'meta_keywords': self.meta_keywords, 'meta_description': self.meta_description,
                   "parent_category_id": self._parent_category_id, "category_id": self.category_id,
                   "meta_tags": self.meta_keywords}

        return webpage

    @property
    def meta_tags(self):
        return self._meta_tags

    @meta_tags.setter
    def meta_tags(self, value):
        self._meta_tags = value

    @property
    def links_text(self):
        return self._links_text
