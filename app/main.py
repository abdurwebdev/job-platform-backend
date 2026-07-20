import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.sql import text  # Used to safely ping the DB

from app.database.database import Base, engine
from app.core.logger import logger
from app.routes.job_routes import router as job_router
from app.routes.health_routes import router as health_router
from app.config.config import settings

from app.middleware.request_id import RequestIDMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up backend application...")

    try:
        # Create tables
        Base.metadata.create_all(bind=engine)

        # Check database connection
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        logger.info("Database connected and tables verified successfully.")

    except Exception as e:
        logger.critical(
            f"FATAL: Database startup failed. Error: {e}",
            exc_info=True,
        )
        sys.exit(1)

    yield

    logger.info("Shutting down backend application...")

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
    lifespan=lifespan,
)

app.add_middleware(RequestIDMiddleware)
# Updated CORS settings to support both local and production traffic
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_router)
app.include_router(health_router)

@app.get("/")
def home():
    return {
        "message": "Welcome to job portaliessss"
    }