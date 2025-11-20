from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/algotrading")

engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommint=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass