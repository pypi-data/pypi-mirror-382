from __future__ import annotations
from typing import Callable, Optional, Any
import threading
from ..settings import settings


class InlineQueue:
    def enqueue(self, fn: Callable, *args, **kwargs) -> Any:
        th = threading.Thread(target=fn, args=args, kwargs=kwargs, daemon=True)
        th.start()
        return th


def get_queue_adapter(backend: Optional[str] = None, queue_name: str = "edge_isr"):
    backend = backend or settings.queue_backend or "inline"
    if backend == "inline":
        return InlineQueue()
    if backend == "celery":
        from celery import current_app

        class CeleryQueue:
            def enqueue(self, fn: Callable, *args, **kwargs):
                return current_app.send_task(
                    fn.__module__ + "." + fn.__name__, args=args, kwargs=kwargs, queue=queue_name
                )

        return CeleryQueue()
    if backend == "rq":
        import rq
        import redis

        class RQQueue:
            def __init__(self):
                self.q = rq.Queue(queue_name, connection=redis.from_url("redis://localhost:6379/0"))

            def enqueue(self, fn: Callable, *args, **kwargs):
                return self.q.enqueue(fn, *args, **kwargs)

        return RQQueue()
    return InlineQueue()
