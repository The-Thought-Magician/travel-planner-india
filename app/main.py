"""FastAPI application entry point."""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import init_db
from app.api import search, stations, airports, cities


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager."""
    # Startup
    init_db()
    print("Database initialized")
    yield
    # Shutdown
    print("Shutting down...")


app = FastAPI(
    title="India Travel Planner",
    description="Multi-modal journey optimizer for Indian travel",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(search.router, prefix="/api/v1", tags=["search"])
app.include_router(stations.router, prefix="/api/v1", tags=["stations"])
app.include_router(airports.router, prefix="/api/v1", tags=["airports"])
app.include_router(cities.router, prefix="/api/v1", tags=["cities"])


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": "India Travel Planner API",
        "version": "0.1.0",
        "docs": "/docs",
        "endpoints": {
            "search": "/api/v1/search",
            "stations": "/api/v1/stations",
            "airports": "/api/v1/airports",
            "cities": "/api/v1/cities",
        },
    }


@app.get("/health")
async def health() -> dict:
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.environment}
