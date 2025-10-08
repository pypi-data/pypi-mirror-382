from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Literal, Dict, Any
from django.conf import settings as dj_settings


@dataclass(frozen=True)
class EdgeISRSettings:
    redis_url: str = "redis://localhost:6379/0"
    defaults: Dict[str, int] = None  # {"s_maxage": 300, "stale_while_revalidate": 3600}
    provider: Optional[Literal["cloudflare", "cloudfront"]] = None
    provider_settings: Dict[str, Any] = None
    queue_backend: Optional[Literal["celery", "rq", "inline"]] = "inline"
    queue_name: str = "edge_isr"


def load_settings() -> EdgeISRSettings:
    cfg = getattr(dj_settings, "EDGE_ISR", {})
    defaults = cfg.get("DEFAULTS", {"s_maxage": 300, "stale_while_revalidate": 3600})
    cdn = cfg.get("CDN", {})
    provider = cdn.get("provider")
    return EdgeISRSettings(
        redis_url=cfg.get("REDIS_URL", "redis://localhost:6379/0"),
        defaults=defaults,
        provider=provider,
        provider_settings=cdn,
        queue_backend=(cfg.get("QUEUE", {}) or {}).get("backend", "inline"),
        queue_name=(cfg.get("QUEUE", {}) or {}).get("queue_name", "edge_isr"),
    )


settings = load_settings()
