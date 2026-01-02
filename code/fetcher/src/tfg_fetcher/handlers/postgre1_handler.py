from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from os import getenv

load_dotenv(override=True)

# Example: postgresql://user:password@localhost:5432/mydatabase
POSTGRES_USER = getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = getenv("POSTGRES_PASSWORD")
DATABASE_NAME = getenv("DATABASE_NAME")

DATABASE_URL = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@localhost:5432/{DATABASE_NAME}"
)
print(f"Connecting to databse at endpoint {DATABASE_URL}...")
# Create the engine (use echo=True to log SQL)
engine = create_engine(DATABASE_URL, echo=False, future=True)
print("Creating session...")
# Create a configured "Session" class
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
print("Connection setup succesful!")


def get_db():
    """
    Dependency-style generator that yields a SQLAlchemy session.
    Works perfectly with FastAPI, but also fine standalone.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
