import os
import logging
from typing import Optional
from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from dotenv import load_dotenv
from simulator import simulate_delivery, set_receipts_url, get_dead_letter, CRM_RECEIPTS_URL

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Xenion Channel Service")

url = os.environ.get("CRM_RECEIPTS_URL")

logger.info("ENV CRM_RECEIPTS_URL=%r", url)

if not url:
    raise RuntimeError("CRM_RECEIPTS_URL is not configured")

set_receipts_url(url)

class Recipient(BaseModel):
    email: Optional[str] = None
    phone: Optional[str] = None


class SendPayload(BaseModel):
    communication_id: str
    recipient: Recipient
    message: str
    channel: str


@app.on_event("startup")
async def startup_event():
    logger.info(f"Channel service starting. Receipts URL: {CRM_RECEIPTS_URL}")
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(CRM_RECEIPTS_URL.replace("/api/receipts", "/docs"))
            if response.status_code == 200:
                logger.info("Backend CRM is reachable")
            else:
                logger.warning(f"Backend CRM returned status {response.status_code}")
    except Exception as e:
        logger.warning(f"Backend CRM is not reachable: {e}. Callbacks will retry.")


@app.post("/send")
async def send_message(payload: SendPayload, background_tasks: BackgroundTasks):
    background_tasks.add_task(simulate_delivery, payload.communication_id)
    return {"status": "queued", "communication_id": payload.communication_id}


@app.get("/health")
async def health_check():
    dead_letter = get_dead_letter()
    status = "healthy"
    if len(dead_letter) > 10:
        status = "degraded"
    if len(dead_letter) > 50:
        status = "unhealthy"
    return {
        "status": status,
        "dead_letter_count": len(dead_letter),
        "receipts_url": CRM_RECEIPTS_URL
    }


@app.get("/dead-letter")
async def list_dead_letter():
    dead_letter = get_dead_letter()
    return {"count": len(dead_letter), "items": dead_letter}
