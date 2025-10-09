from __future__ import annotations
from typing import Iterable, List
import requests
from .queue import get_queue_adapter
from ..settings import settings
from ..graph import urls_for
from ..connectors import get_cdn_connector

WARMUP_HEADER = {"X-Edge-ISR-Warmup": "1"}


def revalidate_by_tags(tags: Iterable[str]) -> List[str]:
    urls = urls_for(tags)
    if not urls:
        return []
    cdn = get_cdn_connector()
    if cdn is not None:
        try:
            cdn.purge_urls(urls)
        except Exception:
            pass
    queue = get_queue_adapter(settings.queue_backend, settings.queue_name)
    for u in urls:
        queue.enqueue(warmup_url, u)
    return urls


def warmup_url(url: str) -> None:
    try:
        requests.get(url, headers=WARMUP_HEADER, timeout=15)
    except Exception:
        pass
