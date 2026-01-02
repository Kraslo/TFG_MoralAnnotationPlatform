import newspaper
import pandas as pd
from sqlalchemy.orm import Session
from tfg_fetcher.models.models import ArticleModel, NewsArticles, MoralAnnotations
from tfg_fetcher.utils.article_processing import process_article_metadata

# from tfg_fetcher.handlers.postgre1_handler import get_db


def insert_annotations(
    db: Session,
    annotated_articles_raw: list[ArticleModel],
    moral_annotations: list[pd.DataFrame],
) -> tuple[list[NewsArticles], list[MoralAnnotations]]:
    """
    Inserts news articles and their corresponding moral annotations into the database.
    """
    # db: Session = get_db()  # however you get your session

    try:
        annotated_articles: list[pd.DataFrame] = process_article_metadata(
            articles=annotated_articles_raw
        )
        article_return_list, annotation_return_list = insert_annotations_to_db(
            db=db,
            annotated_articles=annotated_articles,
            moral_annotations=moral_annotations,
        )

    except Exception as e:
        db.rollback()
        article_return_list = []
        annotation_return_list = []
        raise e

    # NOTE: do not close the session here. The caller (e.g. `main`) manages session lifecycle.
    return article_return_list, annotation_return_list


def insert_annotations_to_db(
    db: Session,
    annotated_articles: list[pd.DataFrame],
    moral_annotations: list[pd.DataFrame],
) -> tuple[list[NewsArticles], list[MoralAnnotations]]:
    """
    Inserts processed data to relational database.
    """
    article_return_list = []
    annotation_return_list = []

    for article_df, annotation_df in zip(annotated_articles, moral_annotations):
        
        article_data = article_df.to_dict(orient="records")[0]
        article = NewsArticles(title=article_data["title"], url=article_data["url"])

        for _, annotation in annotation_df.iterrows():
            annotation_data = {
                "moral_foundation": annotation["moral_foundation"],
                "polarity": annotation["polarity"],
                "intensity": float(annotation["intensity"]),
                "confidence": float(annotation["confidence"])
                if "confidence" in annotation_df
                else None,
                "hits": int(annotation["hits"]) if "hits" in annotation_df else None,
            }

            annotation = MoralAnnotations(
                # TODO: fix df logic. List[pd.DataFrame] -> pd.DataFrame (multiple columns)
                moral_foundation=annotation_data["moral_foundation"],
                polarity=annotation_data["polarity"],
                intensity=annotation_data["intensity"],
                confidence=annotation_data.get("confidence", None),  # optional field
                hits=annotation_data.get("hits", None),  # optional field
                # purity=annotation_data["purity"],
            )

            # Attach via relationship
            article.moral_annotations.append(annotation)

            # Collect for return if needed
            annotation_return_list.append(annotation)

        article_return_list.append(article)

        # Add to session
        db.add(article)
        print("succesfull insert to db")

    db.commit()
    return article_return_list, annotation_return_list
