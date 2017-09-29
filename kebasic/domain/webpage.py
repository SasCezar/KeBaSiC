import json

from sqlalchemy import Column, String, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy.types import TypeDecorator

SIZE = 256


class TextPickleType(TypeDecorator):
    impl = Text(SIZE)

    def process_bind_param(self, value, dialect):
        if value is not None:
            value = json.dumps(value)

        return value

    def process_result_value(self, value, dialect):
        if value is not None:
            value = json.loads(value)
        return value


class WebPage(Base):
    __table_name__ = 'web_pages'
    url = Column(String, primary_key=True)
    domain = Column(String)
    html = Column(String)
    title = Column(String)
    text = Column(String)
    metadata = Column(TextPickleType)
