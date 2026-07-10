from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from backend.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autoflush= False, autocommit= False, bind= engine)

def test_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT version();"))
        return result.fetchone()[0]