from contextlib import asynccontextmanager
import os
import logging

from fastapi import FastAPI, Request

from app.routers.moral_annotator_router import moral_annotation_router
from app.api.dependencies import PostgreSQLHandler

from tfg_fetcher.handlers.fuseki_handler import FusekiHandler

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Initialize PostgreSQL handler and store it in app state
    postgres_handler = PostgreSQLHandler()
    app.state.postgres_handler = postgres_handler
    app.state.SessionLocal = postgres_handler.SessionLocal

    # Initialize Fuseki connection
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

    app.state.fuseki = fuseki


    try:
        yield
    finally:
        # Optional: add cleanup if your handler owns resources that must be closed.
        # e.g., app.state.postgres_handler.dispose()
        pass


app = FastAPI(
    title="API Server",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(moral_annotation_router)

