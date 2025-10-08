from __future__ import annotations

from typing import Any, Dict


def extract_usage(resp: Any) -> Dict[str, int]:
    """Extract prompt/completion tokens from common response shapes.

    Supported:
      - OpenAI-like objects: resp.usage.prompt_tokens, resp.usage.completion_tokens,
        and resp.usage.completion_tokens_details.reasoning_tokens (if present),
        resp.usage.prompt_tokens_details.cached_tokens (if present)
      - Dicts: resp["usage"]["prompt_tokens"], resp["usage"]["completion_tokens"],
        resp["usage"]["completion_tokens_details"]["reasoning_tokens"],
        resp["usage"]["prompt_tokens_details"]["cached_tokens"]
    Fallback:
      - total_tokens (assigned to completion_tokens)
      - zeros
    """
    try:
        if hasattr(resp, "usage") and resp.usage is not None:
            u = resp.usage
            pt = getattr(u, "prompt_tokens", 0) or 0
            ct = getattr(u, "completion_tokens", 0) or 0
            # Reasoning tokens for o-series/GPT-5
            rtd = getattr(u, "completion_tokens_details", None)
            rt = 0
            if rtd is not None:
                rt = int(getattr(rtd, "reasoning_tokens", 0) or 0)
            # Cached input tokens (OpenAI cached inputs)
            ptd = getattr(u, "prompt_tokens_details", None)
            cached = 0
            if ptd is not None:
                cached = int(getattr(ptd, "cached_tokens", 0) or 0)
            if (pt == 0 and ct == 0) and hasattr(u, "total_tokens"):
                return {"prompt_tokens": 0, "completion_tokens": int(getattr(u, "total_tokens", 0) or 0), "reasoning_tokens": 0, "cached_input_tokens": 0}
            return {"prompt_tokens": int(pt), "completion_tokens": int(ct), "reasoning_tokens": int(rt), "cached_input_tokens": int(cached)}
        if isinstance(resp, dict) and "usage" in resp:
            u = resp.get("usage") or {}
            pt = u.get("prompt_tokens", 0) or 0
            ct = u.get("completion_tokens", 0) or 0
            rtd = u.get("completion_tokens_details") or {}
            rt = rtd.get("reasoning_tokens", 0) or 0
            ptd = u.get("prompt_tokens_details") or {}
            cached = ptd.get("cached_tokens", 0) or 0
            if (pt == 0 and ct == 0) and ("total_tokens" in u):
                return {"prompt_tokens": 0, "completion_tokens": int(u.get("total_tokens", 0) or 0), "reasoning_tokens": 0, "cached_input_tokens": 0}
            return {"prompt_tokens": int(pt), "completion_tokens": int(ct), "reasoning_tokens": int(rt), "cached_input_tokens": int(cached)}
    except Exception:
        pass
    return {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0, "cached_input_tokens": 0}
