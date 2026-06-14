import asyncio
import random
import logging
from datetime import datetime, timezone
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CRM_RECEIPTS_URL = "http://localhost:8000/api/receipts"

dead_letter: list[dict] = []

# Shared HTTP client — lazily initialized, reused across all concurrent deliveries.
# This prevents connection exhaustion when many simulate_delivery tasks run at once.
_http_client: httpx.AsyncClient | None = None
_receipt_semaphore = asyncio.Semaphore(10)  # limit concurrent receipt POSTs


def _get_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(
            timeout=10.0,
            limits=httpx.Limits(max_connections=20, max_keepalive_connections=10),
        )
    return _http_client


async def send_receipt(payload: dict, max_retries: int = 3) -> bool:
    client = _get_client()
    async with _receipt_semaphore:
        for attempt in range(max_retries):
            if attempt > 0:
                delay = min(1 * (2 ** (attempt - 1)), 10) + random.uniform(0, 0.5)
                await asyncio.sleep(delay)
            
            try:
                response = await client.post(CRM_RECEIPTS_URL, json=payload)
                if response.status_code == 200:
                    return True
                if response.status_code == 409:
                    logger.info(f"Receipt 409 (expected): {payload.get('communication_id')} - {payload.get('event')}")
                    return True
                logger.warning(f"Receipt unexpected status {response.status_code}: {payload.get('communication_id')}")
            except Exception as e:
                logger.error(f"Receipt callback attempt {attempt + 1} failed for {payload.get('communication_id')}: {e}")
    
    logger.error(f"Receipt callback FAILED after {max_retries} attempts: {payload.get('communication_id')}")
    dead_letter.append(
        {
            "payload": payload,
            "failed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return False


async def simulate_delivery(communication_id: str) -> None:
    await asyncio.sleep(0.1)

    sent_ts = datetime.now(timezone.utc).isoformat()
    await send_receipt(
        {
            "communication_id": communication_id,
            "event": "sent",
            "timestamp": sent_ts,
        }
    )

    await asyncio.sleep(random.uniform(0.5, 2.0))

    if random.random() < 0.8:
        delivered_ts = datetime.now(timezone.utc).isoformat()
        await send_receipt(
            {
                "communication_id": communication_id,
                "event": "delivered",
                "timestamp": delivered_ts,
            }
        )

        await asyncio.sleep(random.uniform(2.0, 8.0))

        if random.random() < 0.55:
            read_ts = datetime.now(timezone.utc).isoformat()
            await send_receipt(
                {
                    "communication_id": communication_id,
                    "event": "read",
                    "timestamp": read_ts,
                }
            )

            await asyncio.sleep(random.uniform(3.0, 10.0))

            if random.random() < 0.30:
                clicked_ts = datetime.now(timezone.utc).isoformat()
                await send_receipt(
                    {
                        "communication_id": communication_id,
                        "event": "clicked",
                        "timestamp": clicked_ts,
                    }
                )

                await asyncio.sleep(random.uniform(30.0, 180.0))

                if random.random() < 0.30:
                    order_ts = datetime.now(timezone.utc).isoformat()
                    revenue = round(random.uniform(800, 8000), 2)
                    await send_receipt(
                        {
                            "communication_id": communication_id,
                            "event": "order_attributed",
                            "timestamp": order_ts,
                            "revenue": revenue,
                        }
                    )
    else:
        failed_ts = datetime.now(timezone.utc).isoformat()
        await send_receipt(
            {
                "communication_id": communication_id,
                "event": "failed",
                "timestamp": failed_ts,
            }
        )


def set_receipts_url(url: str) -> None:
    global CRM_RECEIPTS_URL
    CRM_RECEIPTS_URL = url


def get_dead_letter() -> list[dict]:
    return dead_letter.copy()


def clear_dead_letter() -> None:
    dead_letter.clear()

