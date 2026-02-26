"""
In-memory hub for Server-Sent Events.
Maps user_id -> list of queues. When the backend has a new event for a user
(e.g. new Slack message tagged with the selected emoji), it broadcasts to all
that user's active SSE connections.
"""

import queue
import threading
from typing import Dict, List, Tuple

# user_id (str) -> list of queue.Queue; each queue receives (event_type: str, data: dict)
_connections: Dict[str, List[queue.Queue]] = {}
_lock = threading.Lock()


def register(user_id: str) -> queue.Queue:
    """Register a new SSE connection for user_id. Returns its queue."""
    q: queue.Queue[Tuple[str, dict]] = queue.Queue()
    with _lock:
        if user_id not in _connections:
            _connections[user_id] = []
        _connections[user_id].append(q)
    return q


def unregister(user_id: str, q: queue.Queue) -> None:
    """Remove an SSE connection's queue for user_id."""
    with _lock:
        if user_id in _connections:
            try:
                _connections[user_id].remove(q)
            except ValueError:
                pass
            if not _connections[user_id]:
                del _connections[user_id]


def broadcast(user_id: str, event_type: str, data: dict) -> None:
    """
    Send an event to all SSE connections for this user.
    user_id should be the JWT identity (string).
    """
    with _lock:
        queues = list(_connections.get(user_id, []))
    for q in queues:
        try:
            q.put_nowait((event_type, data))
        except queue.Full:
            # If a client is too slow, skip rather than blocking.
            continue

