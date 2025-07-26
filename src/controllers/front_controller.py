from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.controllers.user_controller import router as user_router
from config import settings
from config import test_db_connection, init_db
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app with settings
@asynccontextmanager
async def lifespan(app):
    logger.info(f"Starting {settings.app.title} v{settings.app.version}")
    try:
        if test_db_connection():
            logger.info("Database connection successful")
            init_db()
            logger.info("Database tables initialized")
        else:
            logger.error("Database connection failed - check your database configuration")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
    yield
    logger.info("Shutting down application")

app = FastAPI(
    title=settings.app.title,
    description=settings.app.description,
    version=settings.app.version,
    debug=settings.app.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
)

# Include routers


app.include_router(user_router)
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.app.title}",
        "version": settings.app.version,
        "status": "running"
    }

@app.get("/health")
async def health_check():
    db_status = "healthy" if test_db_connection() else "unhealthy"
    return {
        "status": "healthy",
        "version": settings.app.version,
        "database": db_status,
        "message": "Service is running"
    }