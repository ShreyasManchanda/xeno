import os
import asyncio
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import httpx

from api import dashboard, customers, segments, campaigns, receipts, ingest
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    from services.campaign_service import start_completion_poller

    app.state.http_client = httpx.AsyncClient(timeout=30.0)
    app.state.completion_poller = asyncio.create_task(start_completion_poller())
    yield
    app.state.completion_poller.cancel()
    try:
        await app.state.completion_poller
    except asyncio.CancelledError:
        pass
    await app.state.http_client.aclose()


app = FastAPI(
    title="Xenion CRM",
    description="AI-native CRM for fashion brands",
    version="1.0.0",
    lifespan=lifespan
)

cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]


import logging
logger = logging.getLogger("uvicorn")
logger.warning(f"CORS Origins configured: {cors_origins}")



app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api")
app.include_router(customers.router, prefix="/api")
app.include_router(segments.router, prefix="/api")
app.include_router(campaigns.router, prefix="/api")
app.include_router(receipts.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
