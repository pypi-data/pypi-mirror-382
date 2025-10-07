from __future__ import annotations

from typing import Dict, Optional
import os


DEFAULT_PRICING: Dict[str, Dict[str, float]] = {
    # $ per 1M tokens — Standard tier (Oct 2025)
    # Reasoning billed at output rate unless specified otherwise

    # GPT‑5 families
    "gpt-5":       {"input": 1.25,  "cached_input": 0.125, "output": 10.00,  "reasoning": 10.00},
    "gpt-5-mini":  {"input": 0.25,  "cached_input": 0.025, "output": 2.00,   "reasoning": 2.00},
    "gpt-5-nano":  {"input": 0.05,  "cached_input": 0.005, "output": 0.40,   "reasoning": 0.40},
    "gpt-5-pro":   {"input": 15.00, "output": 120.00, "reasoning": 120.00},
    # Aliases often used in docs
    "gpt-5-chat-latest": {"input": 1.25,  "output": 10.00,  "reasoning": 10.00},
    "gpt-5-codex":       {"input": 1.25,  "output": 10.00,  "reasoning": 10.00},

    # gpt-4.x / -o families
    "gpt-4.1":      {"input": 2.00,  "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40,  "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10,  "output": 0.40},
    "gpt-4o":       {"input": 2.50,  "output": 10.00},
    "gpt-4o-mini":  {"input": 0.15,  "output": 0.60},

    # o-series
    "o4":       {"input": 2.50,  "output": 10.00, "reasoning": 10.00},
    "o4-mini":  {"input": 1.10,  "output": 4.40,  "reasoning": 8.80},
    "o3":       {"input": 2.00,  "output": 8.00,  "reasoning": 8.00},
    "o3-pro":   {"input": 20.00, "output": 80.00, "reasoning": 80.00},
    "o3-mini":  {"input": 1.10,  "output": 4.40,  "reasoning": 4.40},
    "o1":       {"input": 15.00, "output": 60.00},
    "o1-pro":   {"input": 150.00, "output": 600.00},
}


def _base(model_id: str) -> str:
    mid = model_id.lower()
    # normalize variants by prefix matching
    if mid.startswith("o4-pro"):
        return "o4-pro"
    if mid.startswith("o4"):
        return "o4"
    if mid.startswith("o3-pro"):
        return "o3-pro"
    if mid.startswith("o3-mini"):
        return "o3-mini"
    if mid.startswith("o3"):
        return "o3"
    if mid.startswith("o4-mini"):
        return "o4-mini"
    if mid.startswith("o1-pro"):
        return "o1-pro"
    if mid.startswith("o1"):
        return "o1"
    if mid.startswith("gpt-5-mini"):
        return "gpt-5-mini"
    if mid.startswith("gpt-5-nano"):
        return "gpt-5-nano"
    if mid.startswith("gpt-5-pro"):
        return "gpt-5-pro"
    if mid.startswith("gpt-5-chat-latest"):
        return "gpt-5-chat-latest"
    if mid.startswith("gpt-5-codex"):
        return "gpt-5-codex"
    if mid.startswith("gpt-5"):
        return "gpt-5"
    if mid.startswith("gpt-4.1-mini"):
        return "gpt-4.1-mini"
    if mid.startswith("gpt-4.1-nano"):
        return "gpt-4.1-nano"
    if mid.startswith("gpt-4.1"):
        return "gpt-4.1"
    if mid.startswith("gpt-4o-mini"):
        return "gpt-4o-mini"
    if mid.startswith("gpt-4o"):
        return "gpt-4o"
    return "gpt-4o-mini"  # default fallback


def compute_cost(
    model: str,
    tokens_in: int,
    tokens_out: int,
    pricing: Optional[Dict[str, Dict[str, float]]] = None,
    reasoning_tokens: int = 0,
    cached_input_tokens: int = 0,
) -> float:
    table = pricing or DEFAULT_PRICING
    base_key = _base(model)
    base = table.get(model) or table.get(base_key)
    if base is None:
        # Strict mode: error if pricing unknown
        if os.getenv("COST_PRICING_STRICT", "0") == "1":
            raise ValueError(f"No pricing configured for model '{model}' (base='{base_key}')")
        base = DEFAULT_PRICING["gpt-4o-mini"]
    # Split output into non-reasoning and reasoning portions when supported
    out_rate = base.get("output", 0.0)
    reason_rate = base.get("reasoning", out_rate)
    cached_rate = base.get("cached_input", base.get("input", 0.0))

    pt = max(0, int(tokens_in))
    cached = max(0, int(cached_input_tokens))
    cached = min(cached, pt)
    non_cached_in = pt - cached

    non_reason_out = max(0, int(tokens_out) - int(reasoning_tokens))

    return (
        (non_cached_in * base["input"]) +
        (cached * cached_rate) +
        (non_reason_out * out_rate) +
        (int(reasoning_tokens) * reason_rate)
    ) / 1_000_000.0
