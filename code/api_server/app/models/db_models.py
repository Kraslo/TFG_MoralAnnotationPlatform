from typing import Optional
from sqlalchemy import Integer
from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MoralAnnotations(Base):
    __tablename__ = "moral_annotations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    moral_foundation = Column(String, nullable=False)
    polarity = Column(String, nullable=False)
    intensity = Column(Float, nullable=False)
    confidence = Optional[Column(Float, nullable=False)]
    hits = Optional[Column(Integer, nullable=False)]
    article_id = Column(Integer, ForeignKey("news_articles.id"), nullable=False)

    article = relationship("NewsArticles", back_populates="moral_annotations")


class NewsArticles(Base):
    __tablename__ = "news_articles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)

    moral_annotations = relationship("MoralAnnotations", back_populates="article")


