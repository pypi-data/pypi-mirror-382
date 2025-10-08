from __future__ import annotations
from typing import Dict, List
import requests
from .base import BaseConnector


class CloudflareConnector(BaseConnector):
    def __init__(self, zone_id: str, api_token: str):
        self.zone_id = zone_id
        self.api_token = api_token

    @classmethod
    def from_settings(cls, cfg: Dict[str, str]):
        return cls(zone_id=cfg.get("zone_id", ""), api_token=cfg.get("api_token", ""))

    def purge_urls(self, urls: List[str]) -> None:
        if not self.zone_id or not self.api_token or not urls:
            return
        endpoint = f"https://api.cloudflare.com/client/v4/zones/{self.zone_id}/purge_cache"
        headers = {"Authorization": f"Bearer {self.api_token}", "Content-Type": "application/json"}
        BATCH = 30
        for i in range(0, len(urls), BATCH):
            chunk = urls[i : i + BATCH]
            try:
                requests.post(endpoint, headers=headers, json={"files": chunk}, timeout=15)
            except Exception:
                pass
