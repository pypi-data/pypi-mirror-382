from __future__ import annotations
from urllib.parse import urlsplit, urlunsplit
import hashlib


def normalize_url(url: str) -> str:
    parts = urlsplit(url)
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    return urlunsplit((scheme, netloc, parts.path, parts.query, ""))


def sha_url(url: str) -> str:
    return hashlib.sha256(url.encode("utf-8")).hexdigest()


def full_url_from_request(request) -> str:
    return request.build_absolute_uri()
