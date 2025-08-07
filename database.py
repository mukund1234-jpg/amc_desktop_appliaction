from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base

ENV = "production"  # Change this to "development" for local testing
if ENV == "production":
    DATABASE_URL = "postgresql+psycopg2://postgres:mukund123@localhost:5432/amc_db"
else:
    DATABASE_URL = "sqlite:///amc.db"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = scoped_session(sessionmaker(bind=engine))

def init_db():
    Base.metadata.create_all(bind=engine)
