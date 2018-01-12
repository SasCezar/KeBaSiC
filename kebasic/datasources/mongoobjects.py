from mongoengine import *


class Results(EmbeddedDocument):
    domain = StringField()
    id = StringField()
    language = StringField()
    link = StringField()
    serp_id = StringField()
    snippet = StringField()
    rank = StringField()
    title = StringField()
    visible_link = StringField()


class BingResults(Document):
    meta = {
        'collection': 'bing_clean'
    }

    category = StringField()
    category_id = StringField()
    no_results = StringField()
    num_results = StringField()
    num_results_for_query = StringField()
    page_number = StringField()
    parent_category = StringField()
    parent_id = StringField()
    query = StringField()
    query_cleaned = StringField()
    results = ListField(EmbeddedDocumentField(Results))


class WebPage(Document):

    def __init__(self, *args, **values):
        super().__init__(*args, **values)
        self.category = values['category'] if 'category' in values else ''
        self.category_id = values['category_id'] if 'category_id' in values else ''
        self.parent_category = values['parent_category'] if 'parent_category' in values else ''
        self.parent_category_id = values['parent_category_id'] if 'parent_category_id' in values else ''
        self.url = values['url'] if 'url' in values else ''
        self.html = values['html'] if 'html' in values else ''
        self.title = values['title'] if 'title' in values else ''
        self.text = values['text'] if 'text' in values else ''
        self.meta_keywords = values['meta_keywords'] if 'meta_keywords' in values else ''
        self.meta_description = values['meta_description'] if 'meta_description' in values else ''

    meta = {
        'collection': "webpages"
    }

    url = StringField()
    html = StringField()
    title = StringField()
    text = StringField()
    meta_keywords = StringField()
    meta_description = StringField()
    category = StringField()
    category_id = StringField()
    parent_category = StringField()
    parent_category_id = StringField()
