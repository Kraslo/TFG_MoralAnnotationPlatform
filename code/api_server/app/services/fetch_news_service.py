import logging

import pandas as pd

from app.models.db_models import MoralAnnotations, NewsArticles
from app.models.models import (
    AnnotateBatchArticleRequest,
    AnnotateSingleArticleRequest,
)

from tfg_fetcher.services.fetch_news import fetch_news
from tfg_fetcher.models.models import ArticleModel
from tfg_fetcher.services.moral_annotations import process_article_moralstrength


logger = logging.getLogger(__name__)


def fetch_and_annotate_single(
    payload: AnnotateSingleArticleRequest,
) -> tuple[list[ArticleModel], list[pd.DataFrame]]:
    try:
        fetched_articles: list[ArticleModel] = fetch_news(
            url=payload.url, driver="single"
        )

        logger.info(f"Annotating article with URL: {payload.url}")
        article_moral_annotations: pd.DataFrame = process_article_moralstrength(
            fetched_articles[0]
        )

        return fetched_articles, [article_moral_annotations]

    except Exception as e:
        logger.error(f"Error annotating article: {e}")
        raise e


def fetch_and_annotate_batch(
    payloads: AnnotateBatchArticleRequest,
) -> tuple[list[ArticleModel], list[MoralAnnotations]]:
    moral_annotations_list: list[pd.DataFrame] = []
    fetched_articles_list: list[ArticleModel] = []

    for url in payloads.url_list:
        logger.info(f"Annotating article with URL: {url}")
        try:
            fetched_articles: list[ArticleModel] = fetch_news(
                url=url, driver="single"
            )

            article_moral_annotations: pd.DataFrame = process_article_moralstrength(
                fetched_articles[0]
            )

            moral_annotations_list.append(article_moral_annotations)
            # Extend as fetch_news returns list and not a single article
            fetched_articles_list.extend(fetched_articles)

        except Exception as e:
            logger.error(f"Error processing article with url {url}: {e}")
            continue

    return fetched_articles_list, moral_annotations_list


def fetch_and_annotate_rss(
    payload: AnnotateSingleArticleRequest,
) -> tuple[list[ArticleModel], list[pd.DataFrame]]:
    moral_annotations_list: list[pd.DataFrame] = []

    try:
        fetched_articles: list[ArticleModel] = fetch_news(url=payload.url, driver="rss")

        for article in fetched_articles:
            logger.info(f"Annotating article with URL: {article.url}")
            article_moral_annotations: pd.DataFrame = process_article_moralstrength(
                article
            )
            moral_annotations_list.append(article_moral_annotations)

        return fetched_articles, moral_annotations_list

    except Exception as e:
        logger.error(f"Error annotating RSS articles: {e}")
        raise e
