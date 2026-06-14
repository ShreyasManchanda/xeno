import asyncio
from typing import Dict

_queues: Dict[str, asyncio.Queue] = {}
_queue_lock = asyncio.Lock()


async def create_queue(session_id: str) -> asyncio.Queue:
    async with _queue_lock:
        if session_id in _queues:
            return _queues[session_id]
        q = asyncio.Queue()
        _queues[session_id] = q
        return q


def create_queue_sync(session_id: str) -> asyncio.Queue:
    if session_id in _queues:
        return _queues[session_id]
    q = asyncio.Queue()
    _queues[session_id] = q
    return q


async def publish(session_id: str, event: dict):
    if session_id in _queues:
        await _queues[session_id].put(event)


def cleanup(session_id: str):
    _queues.pop(session_id, None)


def get_queue(session_id: str) -> asyncio.Queue:
    return _queues.get(session_id)


def get_all_session_ids() -> list:
    return list(_queues.keys())
