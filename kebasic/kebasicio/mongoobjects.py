from mongoengine import *


class WebPage(Document):
    meta = {
        'collection': "webpages"
    }

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
