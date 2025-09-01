from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from src.controllers.notification_controller import router
from config.settings import settings
from src.messaging.consumer import start_consumer
import threading

# logging config
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    logger.info(f"Starting {settings.mongo.database} Notification Service")
    # Start RabbitMQ consumer in background thread
    threading.Thread(target=start_consumer, daemon=True).start()
    yield
    logger.info("Shutting down Notification Service")

app = FastAPI(
    title="Notification Service",
    description="Microservice quản lý thông báo (notifications)",
    version="1.0.0",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include notification router
app.include_router(router)

@app.get("/")
async def root():
    return {"service": "notification", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "mongo_db": settings.mongo.database,
        "rabbitmq": settings.rabbitmq.host
    }
