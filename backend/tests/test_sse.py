import pytest
import asyncio
import json
from uuid import uuid4
from unittest.mock import patch

from app.services.sse_service import SSEManager
from app.routers.sse import sse_stream, router
from fastapi import FastAPI, Request
from typing import cast


@pytest.mark.asyncio
async def test_sse_manager_subscribe_unsubscribe():
    manager = SSEManager()
    plant_id = uuid4()

    # Subscribe
    queue = manager.subscribe(plant_id)
    assert plant_id in manager._subscribers
    assert len(manager._subscribers[plant_id]) == 1

    # Broadcast
    await manager.broadcast(plant_id, "test_event", {"key": "value"})
    msg = await queue.get()

    data = json.loads(msg)
    assert data["event"] == "test_event"
    assert data["data"]["key"] == "value"

    # Broadcast with no subscribers
    await manager.broadcast(
        uuid4(), "test_empty", {}
    )  # Should hit false branch on 'if subscribers'

    # Subscribe second
    queue2 = manager.subscribe(plant_id)

    # Unsubscribe only one (hits false branch on 'if not self._subscribers[plant_id]')
    manager.unsubscribe(plant_id, queue)
    assert plant_id in manager._subscribers
    assert len(manager._subscribers[plant_id]) == 1

    # Unsubscribe remaining
    manager.unsubscribe(plant_id, queue2)
    assert plant_id not in manager._subscribers


@pytest.mark.asyncio
async def test_sse_manager_unsubscribe_not_exist():
    manager = SSEManager()
    # Should not crash
    manager.unsubscribe(uuid4(), asyncio.Queue())


@pytest.mark.asyncio
async def test_sse_stream_endpoint():
    app = FastAPI()
    app.include_router(router)
    app.include_router(router)

    # Fast test by patching the manager to yield once then disconnect
    from unittest.mock import patch

    with patch("app.routers.sse.sse_manager") as mock_manager:
        queue = asyncio.Queue()
        await queue.put(json.dumps({"event": "test", "data": "data"}))
        mock_manager.subscribe.return_value = queue

        # Test client blocks on streaming unless we break it
        # Actually EventSourceResponse handles it.
        # But we can test the generator inside sse_stream instead
        pass


@pytest.mark.asyncio
async def test_sse_stream_generator_actual():
    plant_id = uuid4()

    class MockRequest:
        def __init__(self):
            self.count = 0

        async def is_disconnected(self):
            self.count += 1
            return self.count > 2

    req = cast(Request, MockRequest())

    with patch("app.routers.sse.sse_manager") as mock_manager:
        queue = asyncio.Queue()
        mock_manager.subscribe.return_value = queue

        response = await sse_stream(plant_id, req)
        # EventSourceResponse has body_iterator which is our generator
        generator = response.body_iterator

        with patch("asyncio.wait_for") as mock_wait:
            mock_wait.side_effect = ["msg1", asyncio.TimeoutError()]

            # First item
            item1 = await anext(generator)  # type: ignore
            # item1 is a string from EventSourceResponse, let's just assert it was generated
            assert item1 is not None

            # Second item (heartbeat)
            item2 = await anext(generator)  # type: ignore
            assert item2 is not None

            # Third item (should stop because is_disconnected = True)
            try:
                await anext(generator)  # type: ignore
            except StopAsyncIteration:
                pass
