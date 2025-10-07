from __future__ import annotations

import os
from typing import Dict, Any


def _strip_provider_prefix(model_id: str) -> str:
    mid = (model_id or "").lower()
    return mid.split("/", 1)[1] if "/" in mid else mid


from typing import Optional, Tuple


def fetch_openrouter_pricing(timeout_s: float = 5.0, etag: Optional[str] = None, last_modified: Optional[str] = None) -> Tuple[Dict[str, Dict[str, float]], Optional[str], Optional[str]]:
    """
    Fetch pricing from OpenRouter public models API and convert to our table:
      { base_model: { input: $/1M, output: $/1M, reasoning: $/1M } }

    Notes:
    - API: https://openrouter.ai/api/v1/models (no auth required for listing)
    - Pricing units in API vary; we treat numeric fields as USD/token and scale to /1M.
    - Reasoning rate is not provided separately → default to output rate.
    - We create entries for both provider-prefixed id (e.g., "openai/gpt-4o") and base ("gpt-4o").
    """
    import httpx

    url = os.getenv("OPENROUTER_MODELS_URL", "https://openrouter.ai/api/v1/models")
    headers = {"Accept": "application/json"}
    # Optional: allow setting API key if their API requires for higher rate limits
    key = os.getenv("OPENROUTER_API_KEY")
    if key:
        headers["Authorization"] = f"Bearer {key}"
    # Optional app identity headers per OpenRouter guidelines
    ref = os.getenv("OPENROUTER_HTTP_REFERER")
    ttl = os.getenv("OPENROUTER_APP_TITLE")
    if ref:
        headers["HTTP-Referer"] = ref
    if ttl:
        headers["X-Title"] = ttl

    if etag: headers["If-None-Match"] = etag
    if last_modified: headers["If-Modified-Since"] = last_modified
    with httpx.Client(timeout=timeout_s) as client:
        r = client.get(url, headers=headers)
        r.raise_for_status()
        if r.status_code == 304:
            return {}, etag, last_modified
        data = r.json()

    # Data can be either { data: [...] } or just a list
    models = data.get("data", data)
    result: Dict[str, Dict[str, float]] = {}
    for m in models or []:
        mid = m.get("id") or m.get("model") or ""
        if not mid:
            continue
        pricing: Dict[str, Any] = m.get("pricing") or {}
        # Prefer per-token numeric fields if present
        inp = pricing.get("input", pricing.get("prompt", pricing.get("input_token")))
        out = pricing.get("output", pricing.get("completion", pricing.get("output_token")))
        # Some entries may report per-million directly; detect if numbers look already scaled
        def to_per_million(v):
            try:
                v = float(v)
                # Heuristic: if v > 100, assume already per 1M; else per token → scale
                return v if v > 100 else v * 1_000_000.0
            except Exception:
                return None

        input_per_million = to_per_million(inp)
        output_per_million = to_per_million(out)
        if input_per_million is None or output_per_million is None:
            continue

        entry = {
            "input": float(input_per_million),
            "output": float(output_per_million),
            "reasoning": float(output_per_million),  # default reasoning at output rate
        }

        # Store under both full id and base id to maximize hit rate
        result[_strip_provider_prefix(mid)] = entry
        result[mid.lower()] = entry

    new_etag = r.headers.get("ETag")
    new_last_mod = r.headers.get("Last-Modified")
    return result, new_etag, new_last_mod



def get_openrouter_pricing_cached(*, timeout_s: float = 5.0, cache_path: str = None, ttl_sec: int = None) -> Dict[str, Dict[str, float]]:
    import json, time
    cache_path = cache_path or os.getenv("OPENROUTER_PRICING_CACHE", "./openrouter_pricing_cache.json")
    ttl_sec = int(os.getenv("OPENROUTER_PRICING_TTL_SEC", str(ttl_sec or 86400)))
    now = time.time()
    cache = None
    try:
        with open(cache_path, "r", encoding="utf-8") as f:
            cache = json.load(f)
    except Exception:
        cache = None
    if cache and isinstance(cache, dict):
        ts = float(cache.get("_ts", 0))
        if (now - ts) < ttl_sec and isinstance(cache.get("table"), dict):
            return cache["table"]
    etag = cache.get("_etag") if cache else None
    last_mod = cache.get("_last_modified") if cache else None
    try:
        table, new_etag, new_last_mod = fetch_openrouter_pricing(timeout_s=timeout_s, etag=etag, last_modified=last_mod)
        if table:
            payload = {"_ts": now, "_etag": new_etag or etag, "_last_modified": new_last_mod or last_mod, "table": table}
            try:
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(payload, f)
            except Exception:
                pass
            return table
        if cache and isinstance(cache.get("table"), dict):
            cache["_ts"] = now
            try:
                with open(cache_path, "w", encoding="utf-8") as f:
                    json.dump(cache, f)
            except Exception:
                pass
            return cache["table"]
    except Exception:
        if cache and isinstance(cache.get("table"), dict):
            return cache["table"]
        raise
