import sys
import os
import asyncio
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from services.sse_bus import create_queue, create_queue_sync, publish, cleanup, get_queue, _queues


def test_create_queue():
    session_id = "test_session_1"
    q = create_queue_sync(session_id)
    
    assert session_id in _queues
    assert isinstance(q, asyncio.Queue)


def test_create_queue_replaces_existing():
    session_id = "test_session_2"
    q1 = create_queue_sync(session_id)
    q2 = create_queue_sync(session_id)
    
    assert q1 is q2
    assert get_queue(session_id) is q2


@pytest.mark.asyncio
async def test_publish_to_queue():
    session_id = "test_session_3"
    create_queue_sync(session_id)
    
    event = {"type": "test_event", "data": {"key": "value"}}
    await publish(session_id, event)
    
    q = get_queue(session_id)
    result = await asyncio.wait_for(q.get(), timeout=1.0)
    assert result == event


@pytest.mark.asyncio
async def test_publish_to_nonexistent_queue():
    result = await publish("nonexistent_session", {"type": "test"})
    assert result is None


def test_cleanup():
    session_id = "test_session_4"
    create_queue_sync(session_id)
    
    assert session_id in _queues
    
    cleanup(session_id)
    assert session_id not in _queues


def test_cleanup_nonexistent():
    cleanup("nonexistent_session")
    pass


def test_get_queue():
    session_id = "test_session_5"
    q = create_queue_sync(session_id)
    
    result = get_queue(session_id)
    assert result is q


def test_get_queue_nonexistent():
    result = get_queue("nonexistent_session")
    assert result is None


@pytest.mark.asyncio
async def test_queue_event_order():
    session_id = "test_session_6"
    q = create_queue_sync(session_id)
    
    events = [
        {"type": "event_1"},
        {"type": "event_2"},
        {"type": "event_3"}
    ]
    
    for event in events:
        await publish(session_id, event)
    
    results = []
    for _ in range(3):
        evt = await asyncio.wait_for(q.get(), timeout=1.0)
        results.append(evt)
    
    assert results == events


@pytest.mark.asyncio
async def test_multiple_sessions_independent():
    session_a = "session_a"
    session_b = "session_b"
    
    q_a = create_queue_sync(session_a)
    q_b = create_queue_sync(session_b)
    
    await publish(session_a, {"type": "for_a"})
    await publish(session_b, {"type": "for_b"})
    
    result_a = await asyncio.wait_for(q_a.get(), timeout=1.0)
    result_b = await asyncio.wait_for(q_b.get(), timeout=1.0)
    
    assert result_a["type"] == "for_a"
    assert result_b["type"] == "for_b"
    
    cleanup(session_a)
    cleanup(session_b)


@pytest.mark.asyncio
async def test_async_create_queue():
    session_id = "test_async_session"
    q = await create_queue(session_id)
    
    assert session_id in _queues
    assert isinstance(q, asyncio.Queue)
    
    cleanup(session_id)
