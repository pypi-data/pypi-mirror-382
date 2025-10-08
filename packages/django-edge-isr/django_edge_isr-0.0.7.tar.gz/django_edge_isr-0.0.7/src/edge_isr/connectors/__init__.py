from __future__ import annotations
from typing import Optional
from .base import BaseConnector
from .cloudflare import CloudflareConnector
from .cloudfront import CloudFrontConnector
from ..settings import settings


def get_cdn_connector() -> Optional[BaseConnector]:
    p = settings.provider
    if p == "cloudflare":
        return CloudflareConnector.from_settings(settings.provider_settings)
    if p == "cloudfront":
        return CloudFrontConnector.from_settings(settings.provider_settings)
    return None
