"""
main.py

FastAPI application entry point for the Kindle Learning Digest system.
"""

import logging
from fastapi import FastAPI
from dotenv import load_dotenv

from routers.topics import router as topics_router

# Load environment variables from .env file (if present)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
)

app = FastAPI(
    title="Bitty Bettr — Daily Learning Digest",
    description=(
        "A personal digest engine for curious minds. "
        "Track any topic — software, economics, history, science, GK — "
        "and get a clean, concise daily digest to read on your Kindle or anywhere."
    ),
    version="0.1.0",
)

# Register routers
app.include_router(topics_router)


@app.get("/health")
def health():
    return {"status": "ok"}
