from __future__ import annotations

import asyncio
from typing import DefaultDict, Set
from collections import defaultdict

from fastapi import WebSocket


class ConnectionManager:
    """Simple in-memory manager for WebSocket connections grouped by order_id.

    This is intentionally simple (in-memory). For multi-worker deployments you
    must replace it with a pub/sub system (Redis, etc.).
    """

    def __init__(self) -> None:
        # Map order_id -> set of WebSocket connections
        self._connections: DefaultDict[str, Set[WebSocket]] = defaultdict(set)
        self._lock = asyncio.Lock()

    async def connect(self, order_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            self._connections[str(order_id)].add(websocket)

    async def disconnect(self, order_id: str, websocket: WebSocket) -> None:
        async with self._lock:
            conns = self._connections.get(str(order_id))
            if conns and websocket in conns:
                conns.remove(websocket)
            if conns and len(conns) == 0:
                # remove empty set to avoid memory growth
                self._connections.pop(str(order_id), None)

    async def broadcast(self, order_id: str, message: str) -> None:
        # Snapshot connections under lock then send without holding lock
        async with self._lock:
            conns = list(self._connections.get(str(order_id), set()))

        send_coros = [conn.send_text(message) for conn in conns]
        if not send_coros:
            return
        # Gather sends and ignore individual failures (disconnects handled elsewhere)
        await asyncio.gather(*send_coros, return_exceptions=True)


# Single global manager instance used by the router
manager = ConnectionManager()
