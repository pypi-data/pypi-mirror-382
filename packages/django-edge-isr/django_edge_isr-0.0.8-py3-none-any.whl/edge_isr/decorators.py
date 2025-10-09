from __future__ import annotations
from typing import Callable, Iterable, Optional
from functools import wraps
from django.http import HttpRequest, HttpResponse
from .policy import apply_cache_headers
from .context import ensure_request_context
from .graph import bind
from .utils import full_url_from_request


def isr(
    tags: Optional[Callable[..., Iterable[str]]] = None,
    s_maxage: int = 300,
    swr: int = 3600,
    vary: Optional[Iterable[str]] = None,
):
    def decorator(view: Callable[..., HttpResponse]):
        @wraps(view)
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            ctx = ensure_request_context(request)

            if callable(tags):
                try:
                    computed = list(tags(request, *args, **kwargs))
                    ctx.add_tags(computed)
                except Exception:
                    pass

            response = view(request, *args, **kwargs)

            response._edge_isr_policy = {
                "s_maxage": s_maxage,
                "swr": swr,
                "vary": list(vary) if vary else [],
            }
            apply_cache_headers(response, s_maxage, swr, vary=vary)

            try:
                if ctx.tags and response.status_code == 200:
                    url = full_url_from_request(request)
                    bind(url, ctx.tags)
            except Exception:
                pass

            return response

        return wrapper

    return decorator
