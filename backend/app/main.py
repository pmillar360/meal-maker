from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from . import models
from .database import engine, SQLALCHEMY_DATABASE_URL
from .routes import router

from util.logger import intialize_logger, get_logger

# Initialize logging
intialize_logger()

logger = get_logger()

if SQLALCHEMY_DATABASE_URL.startswith("sqlite"):
    # Keep local SQLite bootstrap simple; production should rely on Alembic migrations.
    models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meal Maker API")

# Comma-separated list of allowed frontend origins, e.g. "http://localhost:3000,https://app.example.com"
cors_origins_env = os.getenv("CORS_ALLOW_ORIGINS")
if cors_origins_env:
    cors_allow_origins = [origin.strip().rstrip("/") for origin in cors_origins_env.split(",") if origin.strip()]
else:
    cors_allow_origins = ["*"] # Allow all origins for development; change to specific origins for production

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins,  # Allow all origins for development; change to cors_allow_origins for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)