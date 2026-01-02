async def main(*args, **kwargs):
    import os
    import sys
    import pandas as pd
    import logging
    import time

    from tfg_fetcher.handlers.fuseki_handler import FusekiHandler
    from tfg_fetcher.services.moral_annotations import process_article_moralstrength
    from tfg_fetcher.utils.logging_config import setup_logging
    from tfg_fetcher.services.insert_fuseki import insert_annotation_to_fuseki
    from tfg_fetcher.handlers.postgre1_handler import get_db
    from tfg_fetcher.services.fetch_news import fetch_news
    from tfg_fetcher.services.insert_annotations import insert_annotations

    # Initialize logging
    setup_logging()
    global logger
    logger = logging.getLogger("fetcher")

    logger.info("******** BASIC FETCHER PROTOTYPE [WIP] ********")
    logger.info("Author: Ignacio Escribano Benavente")

    # Setup fuseki db
    fuseki_endpoint: str = os.getenv("FUSEKI_ENDPOINT")
    # fuseki_port: str = os.getenv("FUSEKI_PORT")
    fuseki_user: str = os.getenv("FUSEKI_USER", "admin")
    fuseki_pass: str = os.getenv("FUSEKI_PASSWORD")
    fuseki_db: str = os.getenv("MORAL_DB")
    fuseki = FusekiHandler(
        endpoint=fuseki_endpoint,
        dataset=fuseki_db,
        # database_port=fuseki_port,
        user=fuseki_user,
        password=fuseki_pass,
    )

    # Obtain launch arguments
    try:
        main_url: str = sys.argv[1]
        driver: str = sys.argv[2] if len(sys.argv) > 2 else "default"
    except IndexError:
        logger.error("Usage: python fetcher.py <URL> [driver]")
        sys.exit(1)

    logger.info(f"Fetching articles from: {main_url} | driver={driver}")

    t0 = time.perf_counter()
    articles = fetch_news(url=main_url, driver=driver)
    logger.info(
        f"fetch_news took {time.perf_counter() - t0:.2f}s; articles={len(articles)}"
    )
    results_df_list: list[pd.DataFrame] = []
    for i, article in enumerate(articles):
        t1 = time.perf_counter()
        try:
            article_moral_annotations: pd.DataFrame = process_article_moralstrength(
                article
            )
            results_df_list.append(article_moral_annotations)
        except Exception as e:
            logger.exception(f"Error processing article '{article.title}': {e}")
        finally:
            logger.info(
                f"process_article_moralstrength[{i}] took {time.perf_counter() - t1:.2f}s"
            )
    logger.info("Starting DB + Fuseki ingestion...")
    t2 = time.perf_counter()
    try:
        with next(get_db()) as session:
            article_return_list, annotation_return_list = insert_annotations(
                db=session,
                annotated_articles_raw=articles,
                moral_annotations=results_df_list,
            )
            insert_annotation_to_fuseki(
                moral_annotations=annotation_return_list,
                annotated_articles=article_return_list,
                fuseki=fuseki,
            )
        logger.info(f"Ingestion completed in {time.perf_counter() - t2:.2f}s")
    except Exception as e:
        logger.exception(f"Failed database annotation insertion: {e}")
