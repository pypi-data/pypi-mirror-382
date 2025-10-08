from __future__ import annotations
from typing import Iterable, Optional
from django.http import HttpResponse


def apply_cache_headers(
    response: HttpResponse,
    s_maxage: int,
    swr: int,
    vary: Optional[Iterable[str]] = None,
) -> HttpResponse:
    cache_control = f"public, s-maxage={int(s_maxage)}, stale-while-revalidate={int(swr)}"
    response["Cache-Control"] = cache_control
    if vary:
        existing = (
            set(map(str.strip, response.get("Vary", "").split(",")))
            if response.get("Vary")
            else set()
        )
        response["Vary"] = ", ".join(sorted({v for v in existing if v} | set(vary)))
    return response
