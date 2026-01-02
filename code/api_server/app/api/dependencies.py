from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from os import getenv


class PostgreSQLHandler:
    
    def __init__(self, dsn: str = None):
        POSTGRES_USER = getenv("POSTGRES_USER", "postgres")
        POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
        DATABASE_NAME = getenv("DATABASE_NAME")

        DATABASE_URL = (
            f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{DATABASE_NAME}"
        )

        engine = create_engine(DATABASE_URL, echo=False, future=True)
        print("Creating session...")
        # Create a configured "Session" class
        self.SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

    def get_db(self):
        """
        Dependency-style generator that yields a SQLAlchemy session.
        Works perfectly with FastAPI, but also fine standalone.
        """
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()