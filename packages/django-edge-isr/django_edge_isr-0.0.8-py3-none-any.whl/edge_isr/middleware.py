from __future__ import annotations
from django.utils.deprecation import MiddlewareMixin
from .context import ensure_request_context
from .policy import apply_cache_headers
from .settings import settings
from .graph import bind
from .utils import full_url_from_request


class EdgeISRMiddleware(MiddlewareMixin):
    def process_request(self, request):
        ensure_request_context(request)

    def process_response(self, request, response):
        policy = getattr(response, "_edge_isr_policy", None)
        if policy:
            apply_cache_headers(
                response,
                s_maxage=int(policy.get("s_maxage")),
                swr=int(policy.get("swr")),
                vary=policy.get("vary") or None,
            )
        else:
            if not response.has_header("Cache-Control"):
                defaults = settings.defaults or {}
                s_max = int(defaults.get("s_maxage", 300))
                swr = int(defaults.get("stale_while_revalidate", 3600))
                apply_cache_headers(response, s_max, swr)

        try:
            ctx = getattr(request, "_edge_isr_ctx", None)
            if ctx and getattr(response, "status_code", 200) == 200 and ctx.tags:
                url = full_url_from_request(request)
                bind(url, ctx.tags)
        except Exception:
            pass

        return response
