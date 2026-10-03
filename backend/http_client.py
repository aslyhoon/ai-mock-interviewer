"""Shared httpx client factory.

Works around httpx's env-proxy parsing (it chokes on bracketed IPv6 entries
like `[::1]` in NO_PROXY): we read the proxy URL ourselves and disable
httpx's own env handling. In environments without a proxy (e.g. Render),
requests go direct.
"""

import os

import httpx


def _proxy_url() -> str | None:
    for key in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        val = os.getenv(key, "").strip()
        if val:
            return val
    return None


def make_client(**kwargs) -> httpx.Client:
    kwargs.setdefault("trust_env", False)
    proxy = _proxy_url()
    if proxy:
        kwargs.setdefault("proxy", proxy)
    return httpx.Client(**kwargs)
