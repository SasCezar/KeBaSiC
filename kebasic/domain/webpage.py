from sqlalchemy import Column, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class WebPage(Base):
    """
    Defines a serializable SQLAlchemy object describing a web-page
    """
    __table_name__ = 'web_pages'
    url = Column(String, primary_key=True)
    domain = Column(String)
    html = Column(String)
    title = Column(String)
    text = Column(String)
    meta_keywords = Column(String)
    meta_description = Column(String)
