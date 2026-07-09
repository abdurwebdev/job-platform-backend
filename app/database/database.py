from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base,sessionmaker
from app.config.config import setting

engine = create_engine(str(setting.database_url))

SessionLocal = sessionmaker(
  autocommit = False,
  autoflush = False,
  bind = engine
)

def get_db():
   db = SessionLocal()
   try:
       yield db
   finally:
       db.close()

Base = declarative_base()