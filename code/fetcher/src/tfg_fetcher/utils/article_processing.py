import pandas as pd

from tfg_fetcher.models.models import ArticleModel


def process_article_metadata(articles: list[ArticleModel]) -> list[pd.DataFrame]:
    """
    Extracts metadata from ArticleModel objects and instantiates a List of DataFrames to ready it for relational database insertion.
    """
    article_df_return_list: list[pd.DataFrame] = list()

    for article in articles:
        article_title = article.title
        article_url = article.url

        try:
            df_dict: dict = {"title": [article_title], "url": [article_url]}
            df: pd.DataFrame = pd.DataFrame(df_dict)
            print(f"[process_article_metadata] df: {df}")
            article_df_return_list.append(df)

        except Exception as e:
            print(
                f"Failed to process article metadata for article with title: {article_title}: {e}"
            )
            continue
    print(f"[process_article_metadata] article_df_return_list: {article_df_return_list}")
    return article_df_return_list
