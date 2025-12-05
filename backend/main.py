from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logger import logger

from app.api.v1.api import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set all CORS enabled origins
if settings.ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"CORS enabled for origins: {settings.ALLOWED_ORIGINS}")

app.include_router(api_router, prefix=settings.API_V1_STR)
logger.info(f"API router included with prefix: {settings.API_V1_STR}")

@app.on_event("startup")
async def startup_event():
    logger.info(f"Starting {settings.PROJECT_NAME} in {settings.ENVIRONMENT} mode")
    logger.info(f"API documentation available at: {settings.API_V1_STR}/docs")

@app.on_event("shutdown")
async def shutdown_event():
    logger.info(f"Shutting down {settings.PROJECT_NAME}")

@app.get("/health")
def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@app.get("/")
def root():
    logger.debug("Root endpoint called")
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
