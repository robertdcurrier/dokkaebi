"""
DOKKAEBI FastAPI Web Application
A REAL web interface for our price downloader system!

Based on the shardrunner pattern but built for ACTUAL DATA DOMINATION!
Viper's implementation - REBELLIOUSLY ELEGANT as always.
"""

import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
import uvicorn

from app.core.config import settings
from app.api.routes import router as api_router


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

# Mount static files
static_path = Path(__file__).parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(api_router, prefix="/api", tags=["api"])


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Serve the main DOKKAEBI web interface.
    
    Returns:
        HTMLResponse: The main interface page
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: Health status
    """
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": "development" if settings.debug else "production"
    }


@app.on_event("startup")
async def startup_event():
    """Handle application startup events."""
    print("🚀 DOKKAEBI Price System starting up...")
    print(f"📝 API Documentation: http://localhost:8000/docs")
    print(f"🔍 Health Check: http://localhost:8000/health")
    print(f"💰 Main Interface: http://localhost:8000/")
    
    # Check for Alpaca credentials
    if not settings.alpaca_api_key or not settings.alpaca_api_secret:
        print("⚠️  WARNING: Alpaca API credentials not set!")
        print("   Set ALPACA_API_KEY and ALPACA_API_SECRET environment variables")
    else:
        print("✅ Alpaca API credentials detected")


@app.on_event("shutdown")
async def shutdown_event():
    """Handle application shutdown events."""
    print("🛑 DOKKAEBI shutting down...")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )