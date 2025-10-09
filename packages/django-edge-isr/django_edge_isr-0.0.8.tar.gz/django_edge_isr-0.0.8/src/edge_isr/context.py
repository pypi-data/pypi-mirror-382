from __future__ import annotations
from dataclasses import dataclass, field
from typing import List


@dataclass
class RequestContext:
    tags: List[str] = field(default_factory=list)

    def add_tags(self, tags: List[str]) -> None:
        self.tags.extend(tags)


def ensure_request_context(request) -> RequestContext:
    if not hasattr(request, "_edge_isr_ctx"):
        request._edge_isr_ctx = RequestContext()
    return request._edge_isr_ctx
