from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config.config import settings

engine = create_engine(
    str(settings.database_url),
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,  # Verifies connections before using them
    pool_recycle=3600,   # Recycle connections every hour
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

Base = declarative_base()