from __future__ import annotations
from typing import List


class BaseConnector:
    def purge_urls(self, urls: List[str]) -> None:
        raise NotImplementedError
