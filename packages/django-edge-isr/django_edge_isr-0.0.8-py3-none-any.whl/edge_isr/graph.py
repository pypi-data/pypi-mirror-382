from __future__ import annotations
from typing import Iterable, List, Set
import redis
from .settings import settings
from .utils import sha_url


def _client():
    return redis.from_url(settings.redis_url, decode_responses=True)


def _k_url(sha: str) -> str:
    return f"edgeisr:url:{sha}"


def _k_tag(tag: str) -> str:
    return f"edgeisr:tag:{tag}"


def bind(url: str, tags: Iterable[str]) -> None:
    r = _client()
    sha = sha_url(url)
    tags = list(tags)
    if not tags:
        return
    r.sadd(_k_url(sha), *tags)
    for t in tags:
        r.sadd(_k_tag(t), url)


def unbind(url: str) -> None:
    r = _client()
    sha = sha_url(url)
    url_key = _k_url(sha)
    tags = list(r.smembers(url_key)) if r.exists(url_key) else []
    for t in tags:
        r.srem(_k_tag(t), url)
    r.delete(url_key)


def urls_for(tags: Iterable[str]) -> List[str]:
    r = _client()
    out: Set[str] = set()
    for t in tags:
        out |= set(r.smembers(_k_tag(t)))
    return sorted(out)


def tags_for(url: str) -> List[str]:
    r = _client()
    sha = sha_url(url)
    return sorted(r.smembers(_k_url(sha)))
