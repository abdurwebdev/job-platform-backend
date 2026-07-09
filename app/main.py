import sys
from contextlib import asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.sql import text  # Used to safely ping the DB

from app.database.database import Base, engine
from app.core.logger import logger
from app.routes.job import router as job_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up backend application...")
    
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
            
        Base.metadata.create_all(bind=engine)
        logger.info("Database connected and tables verified successfully.")
        
    except Exception as e:
        logger.critical(
            f"FATAL: Database connection failed at startup. "
            f"Aborting boot sequence. Error: {e}", 
            exc_info=True
        )
        sys.exit(1)

    yield 

    logger.info("Shutting down backend application...")


app = FastAPI(lifespan=lifespan)

# Updated CORS settings to support both local and production traffic
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://job-platform-frontend-62ud.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to job portal"
    }