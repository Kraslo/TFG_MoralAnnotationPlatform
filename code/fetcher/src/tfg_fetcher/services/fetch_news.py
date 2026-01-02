import logging
from typing import Optional
import newspaper
from tfg_fetcher.models.models import ArticleModel
import trafilatura
from langdetect import detect  # add fallback language detection
from langdetect.lang_detect_exception import LangDetectException

# import pandas as pd
from trafilatura.settings import Document

logger = logging.getLogger(__name__)

def fetch_news(
    driver: str = "default", topic: Optional[str] = None, url: str = None
) -> list[ArticleModel]:  # TODO: check type output
    """
    Fetch news articles from a given URL.

    Args:
        driver (str): The driver to use for fetching articles. Options are 'default', 'single', 'rss'.
        topic (Optional[str]): Topic to filter articles (not implemented yet).
        url (Optional[str]): The URL to fetch articles from.
    Returns:
        list[ArticleModel]: A list of fetched articles as ArticleModel instances.
    """
    logger.info("Init fetch news")
    logger.warning(f"Building Source instance with the following url: {url}")
    if driver == "single":
        # use trafilatura for better performance on single article fetching
        articles = [get_article_trafilatura(url)]
    elif driver == "rss":
        articles = get_article_rss(url)
    else:
        news_paper: newspaper.Source = newspaper.build(url)
        articles = [article_to_model(article) for article in news_paper.articles]
    return articles


def article_to_model(article: newspaper.Article) -> ArticleModel:
    """
    Converts a newspaper.Article to an ArticleModel (Pydantic).
    """
    return ArticleModel(
        title=article.title,
        url=article.url,
        text=article.text,
        meta_lang=article.meta_lang,
    )


def get_article(article: newspaper.Article) -> None:
    """
    Download and parse article from a given url.
    """
    article.download()
    article.parse()


def get_article_trafilatura(url: str) -> ArticleModel:
    """
    Fetch article content using trafilatura library.
    """
    downloaded = trafilatura.fetch_url(url, no_ssl=True)
    if not downloaded:
        return ArticleModel(title="", url=url, text="", meta_lang=None)

    # Use full extract with metadata; returns a dict-like result when with_metadata=True
    data = trafilatura.bare_extraction(downloaded, with_metadata=True)
    if not data:
        return ArticleModel(title="", url=url, text="", meta_lang=None)

    title = data.title
    text = data.text
    language = data.language  # may be None

    # Fallback to langdetect if trafilatura couldn't detect language
    if not language and text:
        try:
            language = detect(text)
        except LangDetectException:
            language = None

    print(f"Creating ArticleModel from trafilatura result: {data}")
    print(f"Title: {title}, URL: {url}, Text length: {len(text)}, Language: {language}")

    return ArticleModel(title=title, url=url, text=text, meta_lang=language)


def get_article_rss(url: str) -> ArticleModel:
    """
    Process each article found in an RSS feed using feedparser and trafilatura.
    """
    import feedparser
    feed = feedparser.parse(url)
    articles = []

    for entry in feed.entries:
        article_url = entry.link
        article: ArticleModel = get_article_trafilatura(article_url)
        articles.append(article)

    return articles
