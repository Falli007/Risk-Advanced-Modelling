"""Shared helper for fetching external data with on-disk caching and pull metadata.

Every cached file is written alongside a `<name>.meta.json` sidecar recording the
source URL, query parameters, and pull timestamp, so analyses stay reproducible and
traceable back to the exact API call that produced them.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

DEFAULT_TIMEOUT = 30


def fetch_json(url: str, params: dict[str, Any] | None = None, timeout: int = DEFAULT_TIMEOUT) -> dict:
    """GET a JSON endpoint and return the parsed body. Raises on HTTP errors."""
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.json()


def fetch_text(url: str, params: dict[str, Any] | None = None, timeout: int = DEFAULT_TIMEOUT) -> str:
    """GET a text/CSV endpoint and return the raw body text. Raises on HTTP errors."""
    response = requests.get(url, params=params, timeout=timeout)
    response.raise_for_status()
    return response.text


def cache_path(raw_dir: Path, name: str, ext: str) -> Path:
    raw_dir.mkdir(parents=True, exist_ok=True)
    return raw_dir / f"{name}.{ext}"


def write_meta(path: Path, source_url: str, params: dict[str, Any] | None, extra: dict[str, Any] | None = None) -> None:
    meta = {
        "source_url": source_url,
        "params": params or {},
        "pulled_at_utc": datetime.now(timezone.utc).isoformat(),
    }
    if extra:
        meta.update(extra)
    meta_path = path.with_suffix(path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2))


def load_or_fetch_json(raw_dir: Path, name: str, url: str, params: dict[str, Any] | None = None,
                        force_refresh: bool = False) -> dict:
    """Return cached JSON if present, otherwise fetch, cache, and record metadata."""
    path = cache_path(raw_dir, name, "json")
    if path.exists() and not force_refresh:
        return json.loads(path.read_text())

    data = fetch_json(url, params=params)
    path.write_text(json.dumps(data, indent=2))
    write_meta(path, url, params)
    return data


def load_or_fetch_text(raw_dir: Path, name: str, url: str, params: dict[str, Any] | None = None,
                        ext: str = "csv", force_refresh: bool = False) -> str:
    """Return cached text if present, otherwise fetch, cache, and record metadata."""
    path = cache_path(raw_dir, name, ext)
    if path.exists() and not force_refresh:
        return path.read_text(encoding="utf-8", errors="replace")

    text = fetch_text(url, params=params)
    path.write_text(text, encoding="utf-8")
    write_meta(path, url, params)
    return text
