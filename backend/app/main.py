from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from . import models
from .database import engine
from .routes import router

from util.logger import intialize_logger, get_logger

# Initialize logging
intialize_logger()

logger = get_logger()

# Create database tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Meal Maker API")

# Comma-separated list of allowed frontend origins, e.g. "http://localhost:3000,https://app.example.com"
cors_allow_origins = [
    origin.strip()
    for origin in os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000").split(",")
    if origin.strip()
]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)