from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, declarative_base 
import dotenv
import os

dotenv.load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False}
)

@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

SessionLocal = sessionmaker(
     bind=engine
)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()