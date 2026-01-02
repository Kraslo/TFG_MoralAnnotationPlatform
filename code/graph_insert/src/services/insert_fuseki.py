from typing import Union, Literal
from uuid import uuid6
import pandas as pd
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, XSD

# from ..utils.file_manager import FusekiHandler  # adjust if needed
from src.handlers.fuseki_handler import FusekiHandler

# Namespaces
AMOR = Namespace("http://www.gsi.upm.es/ontologies/amor/ns/1.0.0")
MFT = Namespace("http://www.gsi.upm.es/ontologies/amor/models/mft/ns#")
AMOR_MFT = Namespace("http://www.gsi.upm.es/ontologies/amor/models/mft/ns#")
ITSRDF = Namespace("http://www.w3.org/2005/11/its/rdf#")
OA = Namespace("http://www.w3.org/ns/oa#")
DATASETS = Namespace("http://example.org/datasets#")

MORAL_WITH_PREFIXES = {
    "Care": "http://www.gsi.upm.es/ontologies/mft/ns#Care",
    "Fairness": "http://www.gsi.upm.es/ontologies/mft/ns#Fairness",
    "Loyalty": "http://www.gsi.upm.es/ontologies/mft/ns#Loyalty",
    "Authority": "http://www.gsi.upm.es/ontologies/mft/ns#Authority",
    "Purity": "http://www.gsi.upm.es/ontologies/mft/ns#Purity",
}


def add_moral_to_fuseki_rdf(
    p_intensity: float,
    news_article_identifier,
    moral_annotation_uri,
    fuseki: FusekiHandler,
    moral_value: Literal["care", "fairness", "loyalty", "authority", "purity"],
    polarity: Literal["vice", "virtue"],
    confidence: float = None,
):
    g = Graph()

    # Main annotation URI
    annotation = URIRef(moral_annotation_uri)

    # Insert basic triples
    g.add((annotation, RDF.type, AMOR.MoralValueAnnotation))

    # Moral category (skip NO-MORAL)
    if moral_value != "NaN":  # saltar cuando haya un none o no haya anotación.
        category_uri = URIRef(MORAL_WITH_PREFIXES[moral_value])
        g.add((annotation, AMOR_MFT.hasMoralValueCategory, category_uri))

        # Polarity
        g.add((annotation, AMOR_MFT.hasPolarity, MFT[polarity]))
        g.add(
            (
                annotation,
                AMOR_MFT.hasPolarityIntensity,
                Literal(p_intensity, datatype=XSD.float),
            )
        )

    # Confidence
    if confidence:
        g.add(
            (annotation, ITSRDF.taConfidence, Literal(confidence, datatype=XSD.float))
        )

    # Target news article
    g.add((annotation, OA.hasTarget, DATASETS[news_article_identifier]))

    # Serialize to SPARQL INSERT DATA
    triples_turtle = g.serialize(format="nt")  # N-Triples safest in SPARQL

    sparql = f"""
    INSERT DATA {{
        {triples_turtle}
    }}
    """

    # Send to Fuseki
    fuseki.send_update(sparql)
    print(f"Inserted annotation {annotation}")


def insert_annotation(moral_annotation_df: pd.DataFrame, news_article_df: pd.DataFrame):
    pass


def add_newspaper_entry():
    pass


def generate_uuid():
    return uuid6()
