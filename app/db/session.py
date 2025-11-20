from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

# Use SQLite for development
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session_sync():
    return Session(engine)
