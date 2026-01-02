import json
import logging
from fastapi import APIRouter, HTTPException, Request
from fastapi.param_functions import Depends
import pandas as pd

from app.models.db_models import MoralAnnotations, NewsArticles
from app.models.models import (
    AnnotateBatchArticleRequest,
    AnnotateResponse,
    AnnotateSingleArticleRequest,
)
from app.services import fetch_news_service

# from src.services.fetch_news import fetch_news

from tfg_fetcher.services.fetch_news import fetch_news
from tfg_fetcher.models.models import ArticleModel
from tfg_fetcher.services.moral_annotations import process_article_moralstrength
from tfg_fetcher.services.insert_annotations import insert_annotations
from tfg_fetcher.services.insert_fuseki import insert_annotation_to_fuseki

moral_annotation_router = APIRouter(
    prefix="/moral-annotator",
    tags=["moral-annotator"],
)


logger = logging.getLogger(__name__)


def get_db(request: Request):
    """
    Yields a SQLAlchemy session created from the SessionLocal stored on the app.
    """
    SessionLocal = request.app.state.SessionLocal
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_fuseki(request: Request):
    """
    Yields the Fuseki handler stored on the app.
    """
    fuseki = request.app.state.fuseki
    try:
        yield fuseki
    finally:
        pass


@moral_annotation_router.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# GET PETITIONS


@moral_annotation_router.get(
    "/annotations/{article_id}",
    response_model=list[AnnotateResponse],
)
async def get_annotations(
    article_id: int, db=Depends(get_db)
) -> list[AnnotateResponse]:
    annotations = (
        db.query(MoralAnnotations)
        .filter(MoralAnnotations.article_id == article_id)
        .all()
    )
    response = []
    for annotation in annotations:
        response.append(
            AnnotateResponse(
                text="",
                annotations={
                    "moral_foundation": annotation.moral_foundation,
                    "polarity": annotation.polarity,
                    "intensity": annotation.intensity,
                    "confidence": annotation.confidence,
                    "hits": annotation.hits,
                },
            )
        )
    return response


# POST PETITIONS


@moral_annotation_router.post("/annotate/single", response_model=AnnotateResponse)
async def annotate_single(
    payload: AnnotateSingleArticleRequest, db=Depends(get_db)
) -> AnnotateResponse:
    # TODO: Replace with real model/service call.
    try:
        fetched_articles: list[ArticleModel]
        article_moral_annotations: list[pd.DataFrame]
        fetched_articles, article_moral_annotations = (
            fetch_news_service.fetch_and_annotate_single(payload=payload)
        )

        logger.info(f"Inserting annotations to DB: {article_moral_annotations}")

        article_return_list: list[NewsArticles]
        annotation_return_list: list[MoralAnnotations]
        article_return_list, annotation_return_list = insert_annotations(
            db=db,
            annotated_articles_raw=fetched_articles,
            moral_annotations=article_moral_annotations,
        )
        logger.info(f"Inserted annotations to DB: {annotation_return_list}")

        return AnnotateResponse(
            text="Succesfully annotated article.",
            annotations=[article.to_dict() for article in article_return_list],
        )

    except Exception as e:
        logger.error(f"Error processing article with url {payload.url}: {e}")

        raise HTTPException(status_code=500, detail="Internal Server Error")


@moral_annotation_router.post("/annotate/batch", response_model=list[AnnotateResponse])
async def annotate_batch(
    payloads: AnnotateBatchArticleRequest, db=Depends(get_db)
) -> list[AnnotateResponse]:
    # TODO: Replace with real model/service call.

    article_moral_annotations: list[pd.DataFrame]
    fetched_articles: list[ArticleModel]

    try:
        fetched_articles, article_moral_annotations = (
            fetch_news_service.fetch_and_annotate_batch(payloads=payloads)
        )

    except Exception as e:
        logger.error(f"Error annotating batch articles: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    logger.info(f"Inserting annotations to DB: {article_moral_annotations}")

    try:
        article_return_list: list[NewsArticles]
        annotation_return_list: list[MoralAnnotations]
        article_return_list, annotation_return_list = insert_annotations(
            db=db,
            annotated_articles_raw=fetched_articles,
            moral_annotations=article_moral_annotations,
        )
        logger.info(f"Inserted annotations to DB: {annotation_return_list}")
        return [
            AnnotateResponse(
                text="Succesfully annotated articles.",
                annotations=[article.to_dict() for article in article_return_list],
            )
        ]
    except Exception as e:
        logger.error(f"Error inserting annotations to DB: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal Server Error: DB Insertion Failed: {e}"
        )


@moral_annotation_router.post("/annotate/rss", response_model=list[AnnotateResponse])
async def annotate_rss(
    payloads: AnnotateSingleArticleRequest, db=Depends(get_db)
) -> list[AnnotateResponse]:
    article_moral_annotations: list[pd.DataFrame]
    fetched_articles: list[ArticleModel]

    try:
        fetched_articles, article_moral_annotations = (
            fetch_news_service.fetch_and_annotate_rss(payload=payloads)
        )

        logger.info(f"Inserting annotations to DB: {article_moral_annotations}")
        article_return_list: list[NewsArticles]
        annotation_return_list: list[MoralAnnotations]
        article_return_list, annotation_return_list = insert_annotations(
            db=db,
            annotated_articles_raw=fetched_articles,
            moral_annotations=article_moral_annotations,
        )
        logger.info(f"Inserted annotations to DB: {annotation_return_list}")

        return [
            AnnotateResponse(
                text="Succesfully annotated RSS articles.",
                annotations=[{"text": "test_text"}],
            )
        ]
    except Exception as e:
        logger.error(f"Error processing RSS feed with url {payloads.url}: {e}")

        raise HTTPException(status_code=500, detail="Internal Server Error")


@moral_annotation_router.post("/annotate/e2e", response_model=list[AnnotateResponse])
async def annotate_e2e(
    payloads: AnnotateBatchArticleRequest,
    db=Depends(get_db),
    fuseki=Depends(get_fuseki),
) -> list[AnnotateResponse]:
    article_moral_annotations: list[pd.DataFrame]
    fetched_articles: list[ArticleModel]

    # Fetching and annotation
    try:
        fetched_articles, article_moral_annotations = (
            fetch_news_service.fetch_and_annotate_batch(payloads=payloads)
        )

    except Exception as e:
        logger.error(f"Error annotating batch articles: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

    # Insertion to DB
    try:
        article_return_list: list[NewsArticles]
        annotation_return_list: list[MoralAnnotations]
        article_return_list, annotation_return_list = insert_annotations(
            db=db,
            annotated_articles_raw=fetched_articles,
            moral_annotations=article_moral_annotations,
        )
        logger.info(f"Inserted annotations to DB: {annotation_return_list}")

    except Exception as e:
        logger.error(f"Error inserting annotations to DB: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal Server Error: DB Insertion Failed: {e}"
        )

    # Insertion to Fuseki
    try:
        insert_annotation_to_fuseki(
            moral_annotations=annotation_return_list,
            annotated_articles=article_return_list,
            fuseki=fuseki,
        )
        logger.info("Inserted annotations to Fuseki")

        return [
            AnnotateResponse(
                text="Succesfully annotated articles.",
                annotations=[article.to_dict() for article in article_return_list],
            )
        ]
    except Exception as e:
        logger.error(f"Error inserting annotations to Fuseki: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: Fuseki Insertion Failed: {e}",
        )

    

@moral_annotation_router.post("/insert/postgre_to_fuseki", response_model=dict)
async def insert_postgre_to_fuseki(
    db=Depends(get_db),
    fuseki=Depends(get_fuseki),
):
    """
    Endpoint to perform Fuseki insertion independently.
    """
    try:
        article_return_list: list[NewsArticles] = (
            db.query(NewsArticles).all()
        )
        annotation_return_list: list[MoralAnnotations] = (
            db.query(MoralAnnotations).all()
        )

        insert_annotation_to_fuseki(
            moral_annotations=annotation_return_list,
            annotated_articles=article_return_list,
            fuseki=fuseki,
        )
        logger.info("Inserted annotations to Fuseki")

        return {"status": "success", "message": "Inserted annotations to Fuseki"}

    except Exception as e:
        logger.error(f"Error inserting annotations to Fuseki: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal Server Error: Fuseki Insertion Failed: {e}",
        )
