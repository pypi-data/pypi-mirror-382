from __future__ import annotations
from typing import Dict, List

try:
    import boto3  # optional
except Exception:
    boto3 = None

from .base import BaseConnector


class CloudFrontConnector(BaseConnector):
    def __init__(self, distribution_id: str):
        self.distribution_id = distribution_id

    @classmethod
    def from_settings(cls, cfg: Dict[str, str]):
        return cls(distribution_id=cfg.get("distribution_id", ""))

    def purge_urls(self, urls: List[str]) -> None:
        if not boto3 or not self.distribution_id or not urls:
            return
        from urllib.parse import urlsplit

        paths = []
        for u in urls:
            parts = urlsplit(u)
            path = parts.path or "/"
            if parts.query:
                path = f"{path}?{parts.query}"
            paths.append(path)
        client = boto3.client("cloudfront")
        client.create_invalidation(
            DistributionId=self.distribution_id,
            InvalidationBatch={
                "Paths": {"Quantity": len(paths), "Items": paths[:3000]},
                "CallerReference": "edge-isr-warmup",
            },
        )
