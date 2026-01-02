import logging
from typing import Any, Literal as TLiteral
from uuid import uuid4
import pandas as pd
from rdflib import Graph, Namespace, URIRef, Literal as RDFLiteral
from rdflib.namespace import RDF, RDFS, XSD
import urllib.error

# from ..utils.file_manager import FusekiHandler  # adjust if needed
from tfg_fetcher.models.models import MoralAnnotations, NewsArticles
from tfg_fetcher.handlers.fuseki_handler import FusekiHandler


logger = logging.getLogger(__name__)
# Namespaces
AMOR = Namespace("http://www.gsi.upm.es/ontologies/amor/ns/1.0.0")
MFT = Namespace("http://www.gsi.upm.es/ontologies/amor/models/mft/ns#")
AMOR_MFT = Namespace("http://www.gsi.upm.es/ontologies/amor/models/mft/ns#")
ITSRDF = Namespace("http://www.w3.org/2005/11/its/rdf#")
OA = Namespace("http://www.w3.org/ns/oa#")
DATASETS = Namespace("http://example.org/datasets#")
SCHEMA = Namespace("http://schema.org/")
DCTERMS = Namespace("http://purl.org/dc/terms/")

MORAL_WITH_PREFIXES = {
    "care": "http://www.gsi.upm.es/ontologies/mft/ns#Care",
    "fairness": "http://www.gsi.upm.es/ontologies/mft/ns#Fairness",
    "loyalty": "http://www.gsi.upm.es/ontologies/mft/ns#Loyalty",
    "authority": "http://www.gsi.upm.es/ontologies/mft/ns#Authority",
    "purity": "http://www.gsi.upm.es/ontologies/mft/ns#Purity",
}


def add_moral_to_fuseki_rdf(
    p_intensity: float,
    news_article_identifier,
    moral_annotation_uri,
    fuseki: FusekiHandler,
    moral_value: TLiteral["care", "fairness", "loyalty", "authority", "purity"],
    polarity: TLiteral["vice", "virtue"] | None,
    confidence: float = None,
):
    g = Graph()
    annotation = URIRef(moral_annotation_uri)

    # Base type
    g.add((annotation, RDF.type, AMOR.MoralValueAnnotation))

    # Only add category/polarity when there is a moral value
    if moral_value and moral_value != "NaN":
        category_uri = URIRef(MORAL_WITH_PREFIXES[moral_value])
        g.add((annotation, AMOR_MFT.hasMoralValueCategory, category_uri))

        # Polarity and intensity (polarity may be None)
        if polarity:
            # MFT namespace expects lowercase keys (‘vice’, ‘virtue’)
            g.add((annotation, AMOR_MFT.hasPolarity, MFT[polarity]))
        g.add(
            (
                annotation,
                AMOR_MFT.hasPolarityIntensity,
                RDFLiteral(p_intensity, datatype=XSD.float),
            )
        )

        if confidence is not None:
            g.add(
                (
                    annotation,
                    ITSRDF.taConfidence,
                    RDFLiteral(confidence, datatype=XSD.float),
                )
            )

    # Target article
    g.add((annotation, OA.hasTarget, DATASETS[news_article_identifier]))

    triples_nt = g.serialize(format="nt")
    sparql = f"INSERT DATA {{\n{triples_nt}\n}}"
    logging.debug(f"Fuseki moral annotation insert SPARQL:\n{sparql}")

    try:
        fuseki.send_update(sparql)
        logging.info(f"Inserted annotation {annotation}")
    except urllib.error.URLError as e:
        logging.error(f"Fuseki update failed: {e}")
        raise


def _uri_or_literal(value: str) -> URIRef | RDFLiteral:
    value = (value or "").strip()
    if value.startswith("http://") or value.startswith("https://"):
        return URIRef(value)
    return RDFLiteral(value)


def add_article_to_fuseki(
    *,
    article_id: int | None,
    identifier: str,
    title: str | None,
    url: str | None,
    fuseki: FusekiHandler,
):
    """Insert minimal article metadata triples.

    The moral annotation triples target `DATASETS[identifier]` via `oa:hasTarget`.
    This helper ensures the target resource exists with title/url metadata.
    """

    if not identifier:
        raise ValueError("identifier is required to insert article into Fuseki")

    g = Graph()
    article_uri = DATASETS[str(identifier).strip()]

    g.add((article_uri, RDF.type, SCHEMA.NewsArticle))

    if article_id is not None:
        try:
            g.add(
                (
                    article_uri,
                    DCTERMS.identifier,
                    RDFLiteral(int(article_id), datatype=XSD.integer),
                )
            )
        except Exception:
            # Keep going; id is helpful but not required.
            pass

    if title:
        g.add((article_uri, SCHEMA.headline, RDFLiteral(str(title))))
        g.add((article_uri, RDFS.label, RDFLiteral(str(title))))

    if url:
        # schema:url is typically an IRI, but allow literals for malformed values.
        g.add((article_uri, SCHEMA.url, _uri_or_literal(str(url))))

    triples_nt = g.serialize(format="nt")
    sparql = f"INSERT DATA {{\n{triples_nt}\n}}"
    logging.debug(f"Fuseki article insert SPARQL:\n{sparql}")

    try:
        fuseki.send_update(sparql)
        logging.info(f"Inserted article metadata {article_uri}")
    except urllib.error.URLError as e:
        logging.error(f"Fuseki article update failed: {e}")
        raise


def normalize_moral_annotations_df(
    moral_annotations_df: list[MoralAnnotations] | pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize `moral_annotations_df` to a DataFrame if it's a list of ORM objects.
    Produces a wide row per article_id with keys: care, fairness, loyalty, authority, purity.
    """
    MORAL_FOUNDATIONS = ["care", "fairness", "loyalty", "authority", "purity"]

    # Already a DataFrame
    if isinstance(moral_annotations_df, pd.DataFrame):
        return moral_annotations_df

    # Guard empty list
    if not moral_annotations_df:
        return pd.DataFrame(
            [{"article_id": None, **{f: None for f in MORAL_FOUNDATIONS}}]
        ).iloc[:0]

    moral_rows_by_article: dict = {}
    try:
        for ma in moral_annotations_df:
            aid = getattr(ma, "article_id", None)
            if aid is None:
                continue

            # init article row
            if aid not in moral_rows_by_article:
                moral_rows_by_article[aid] = {"article_id": aid}
                for f in MORAL_FOUNDATIONS:
                    moral_rows_by_article[aid][f] = None

            # normalize foundation key to lowercase to match our columns
            key_raw = getattr(ma, "moral_foundation", None)
            key = (key_raw or "").strip().lower()
            if key in MORAL_FOUNDATIONS:
                moral_rows_by_article[aid][key] = {
                    "polarity": getattr(ma, "polarity", None),
                    "intensity": float(ma.intensity)
                    if getattr(ma, "intensity", None) is not None
                    else None,
                    "confidence": float(ma.confidence)
                    if getattr(ma, "confidence", None) is not None
                    else None,
                }
            # else: ignore unknown foundation labels

    except Exception:
        logging.exception("Failed to normalize moral_annotations_df from ORM objects")
        raise

    df = pd.DataFrame(list(moral_rows_by_article.values()))

    logger.debug(f"Normalized moral_annotations_df:\n{df}")
    # Optional: drop rows where all moral foundations are None
    # keep rows with at least one foundation annotated
    if not df.empty:
        mask_all_none = (
            df[MORAL_FOUNDATIONS].map(lambda x: pd.isna(x) or x is None).all(axis=1)
        )
        df = df[~mask_all_none]

    return df


def normalize_annotated_articles_df(
    annotated_articles_df: list[NewsArticles] | pd.DataFrame,
) -> pd.DataFrame:
    """
    Normalize `annotated_articles_df` to a DataFrame if it's a list of ORM objects.
    
    Produces a DataFrame with columns: article_id, identifier, title, url.
    """
    # Normalize `annotated_articles_df` to a DataFrame if it's a list of ORM objects
    if not isinstance(annotated_articles_df, pd.DataFrame):
        articles_rows = []
        try:
            for annotated_article in annotated_articles_df:
                articles_rows.append(
                    {
                        "article_id": annotated_article.id,
                        "identifier": getattr(
                            annotated_article,
                            "identifier",
                            f"article:{annotated_article.id}",
                        ),
                        "title": annotated_article.title,
                        "url": annotated_article.url,
                    }
                )

        except Exception:
            logging.exception("Failed to normalize annotated_articles_df to DataFrame")
            raise

        return pd.DataFrame(articles_rows)
    # already a df
    return annotated_articles_df


def insert_annotation_to_fuseki(
    moral_annotations: list[MoralAnnotations] | pd.DataFrame,
    annotated_articles: list[NewsArticles] | pd.DataFrame,
    fuseki: FusekiHandler,
):
    MORAL_FOUNDATIONS: list[str] = ["care", "fairness", "loyalty", "authority", "purity"]
    logging.info("=== Starting RDF insertion into Fuseki ===")

    annotated_articles_df: pd.DataFrame = (
        annotated_articles
        if isinstance(annotated_articles, pd.DataFrame)
        else normalize_annotated_articles_df(annotated_articles)
    )
    moral_annotations_df: pd.DataFrame = (
        moral_annotations
        if isinstance(moral_annotations, pd.DataFrame)
        else normalize_moral_annotations_df(moral_annotations)
    )

    for _, annotation_row in moral_annotations_df.iterrows():
        article_id = annotation_row["article_id"]
        try:
            article_entry: pd.DataFrame = annotated_articles_df[
                annotated_articles_df["article_id"] == article_id
            ].iloc[0]
        except Exception:
            logging.error(f"Article metadata missing for article_id={article_id}")
            continue

        dataset_identifier: str = article_entry["identifier"]

        # Insert article here
        try:
            add_article_to_fuseki(
                article_id=int(article_id) if article_id is not None else None,
                identifier=str(dataset_identifier),
                title=str(article_entry.get("title"))
                if "title" in article_entry
                else None,
                url=str(article_entry.get("url")) if "url" in article_entry else None,
                fuseki=fuseki,
            )
        except Exception as e:
            logging.error(
                f"Fuseki article insertion failed for article_id={article_id}: {e}"
            )
            raise
        

        for moral in MORAL_FOUNDATIONS:
            moral_data: Any = annotation_row[moral]
            if moral_data is None or (
                isinstance(moral_data, float) and pd.isna(moral_data)
            ):
                continue

            polarity: str = None
            intensity: float = None
            confidence: float = None

            if isinstance(moral_data, dict):
                polarity = moral_data.get("polarity")
                intensity = moral_data.get("intensity")
                confidence = moral_data.get("confidence")
            else:
                polarity = getattr(moral_data, "polarity", None)
                intensity = getattr(moral_data, "intensity", None)
                confidence = getattr(moral_data, "confidence", None)

            # Derive polarity if intensity present (map to lowercase for MFT)
            if intensity is not None:
                try:
                    intensity_val: float = float(intensity)
                    polarity: str = "virtue" if intensity_val >= 5.0 else "vice"
                except Exception:
                    pass
            elif polarity:
                polarity = str(polarity).strip().lower()

            annotation_uuid: str = generate_uuid()
            annotation_uri = f"http://example.org/annotation/{annotation_uuid}"

            try:
                add_moral_to_fuseki_rdf(
                    p_intensity=float(intensity) if intensity is not None else 0.0,
                    news_article_identifier=dataset_identifier,
                    moral_annotation_uri=annotation_uri,
                    fuseki=fuseki,
                    moral_value=moral,
                    polarity=polarity,
                    confidence=confidence,
                )
                logging.info(
                    f"[OK] Inserted moral annotation for {moral} ({polarity}) "
                    f"article_id={article_id} uuid={annotation_uuid}"
                )
            except Exception as e:
                logging.error(
                    f"Fuseki insertion failed for article={article_id}, moral={moral}: {e}"
                )
                raise e

    logging.info("=== Completed RDF moral annotation ingestion ===")


def add_newspaper_entry():
    pass


def generate_uuid():
    return uuid4()
