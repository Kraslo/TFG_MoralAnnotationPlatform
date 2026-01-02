from typing import Any
import pandas as pd
from rdflib import logger
from tfg_fetcher.models.models import ArticleModel
from tfg_fetcher.services.llm_service import LLMChat
from moralstrength.moralstrength import estimate_morals


def process_article_moralstrength(
    article: ArticleModel,
) -> pd.DataFrame:
    """
    Parses articles and returns moral value estimations using moralstrength module.
    """
    article_text: str = article.text

    # if article.meta_lang != "en":
    #     print(
    #         f"Article not in english. Detected language: {article.meta_lang}. Translating to english..."
    #     )
    #     llm_chat: LLMChat = LLMChat()
    #     article_text = llm_chat.translate_text_llm(article_text)
    #     article_text = article_text.strip()

    logger.info(f"Article text for moral analysis: {article_text[:200]}...")
    result = estimate_morals([article_text], process=True)
    logger.info(f"    Moral estimation result: {result}")
    # placeholder
    confidence: int = 1
    hits: int = 1
    # end placeholder

    processed_result: list[dict[str, Any]] = []

    for column in result.columns:
        intensity_value = result[column].iloc[0]
        # Handle None/NaN values from moralstrength
        if pd.isna(intensity_value) or intensity_value is None:
            intensity_value = 0.0
        
        procesed_annotation: dict[str, Any] = {
            "moral_foundation": column,
            "polarity": "virtue" if intensity_value >= 5 else "vice",
            "intensity": float(intensity_value),
            "confidence": confidence,
            "hits": hits,
        }

        processed_result.append(procesed_annotation)

    processed_result_df: pd.DataFrame = pd.DataFrame(processed_result)

    # insert to db
    return processed_result_df


# {
#  'care':      {'polarity': 'none',   'intensity': 0.0,  'hits': 0},
#  'fairness':  {'polarity': 'vice',   'intensity': 0.71, 'hits': 1},
#  'loyalty':   {'polarity': 'vice',   'intensity': 0.85, 'hits': 1},
#  'authority': {'polarity': 'virtue', 'intensity': 0.62, 'hits': 1},
#  'purity':    {'polarity': 'none',   'intensity': 0.0,  'hits': 0}
# }
