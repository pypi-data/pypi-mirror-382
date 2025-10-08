"""
llm_cost - Plug-and-play LLM token/cost tracking SDK

DX goals:
- init() via env or one-liner
- set_context(dict) with arbitrary key/values (JSON-serializable)
- @track_cost for non-streaming functions (auto usage extract) or defer mode for streaming
- finalize_llm_call for streaming totals (requires request_id)
- track wrapper for arbitrary call sites

Implementation notes:
- Non-blocking background batcher with bounded queue and atexit/signal flush
- Pluggable sinks: SQLite (default), Postgres/Supabase, HTTP collector
- Idempotent upserts via (workspace_id, request_id) in embedded mode or (project_id, request_id) in service mode
- Privacy by default: we do not capture prompts/responses; only numeric usage and context JSON

WARNING:
- Do NOT use Supabase SERVICE_ROLE_KEY in untrusted runtimes (frontend/desktop). Use embedded SQLite/Postgres
  or HTTP collector mode from untrusted apps. SERVICE_ROLE_KEY is server-only.
"""

from __future__ import annotations

from typing import Any, Callable, Optional, Dict, Tuple
import json
import hashlib
import atexit
import os
import signal

from .context import set_sticky_context, get_effective_context, merge_contexts, ContextManager
from .extractors import extract_usage
from .pricing import compute_cost, DEFAULT_PRICING
try:
    from .pricing import _base as _pricing_base  # normalization helper
except Exception:
    _pricing_base = None
from .idempotency import default_request_id, new_request_id
from .background import Batcher, QueueFullError
from .sinks import build_sink

__all__ = [
    "init",
    "set_context",
    "track_cost",
    "finalize_llm_call",
    "track",
    "flush",
    "new_request_id",
]


class _State:
    batcher: Optional[Batcher] = None
    sink = None
    server_pricing: bool = False
    pricing_override: Optional[Dict[str, Dict[str, float]]] = None
    pricing_table: Optional[Dict[str, Dict[str, float]]] = None
    pricing_fp: Optional[str] = None
    redaction_keys: Tuple[str, ...] = ("prompt", "content", "blob", "raw")
    initialized: bool = False


_state = _State()


def init(
    dsn: Optional[str] = None,
    supabase_url: Optional[str] = None,
    supabase_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    write_key: Optional[str] = None,
    flush_at: int = 20,
    flush_interval_ms: int = 3000,
    timeout_s: float = 2.0,
    pricing: Optional[Dict[str, Dict[str, float]]] = None,
    server_pricing: bool = False,
    outbox_path: Optional[str] = None,
    redaction_keys: Optional[list[str]] = None,
    max_queue_size: int = 5000,
    force_reinit: bool = False,
    # Explicit-over-implicit controls
    sink: Optional[str] = None,  # one of: "sqlite" | "supabase" | "http" | "none"
    allow_autodetect: bool = True,
) -> None:
    """Initialize SDK. Env-only also supported.

    Args are optional; values can be supplied via env:
      COST_SINK_DSN, SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY, COST_COLLECTOR_ENDPOINT, COST_WRITE_KEY,
      COST_FLUSH_AT, COST_FLUSH_INTERVAL_MS, COST_TIMEOUT_S
    """
    if _state.initialized and _state.batcher is not None and not force_reinit:
        return
    
    # Stop existing batcher if reinitializing
    if _state.batcher is not None:
        try:
            _state.batcher.stop()
        except Exception:
            pass

    # Resolve config (env defaults)
    env_sink = os.getenv("COST_SINK")
    sink = sink or env_sink
    dsn = dsn or os.getenv("COST_SINK_DSN", "sqlite:///./llm_cost.db")
    supabase_url = supabase_url or os.getenv("SUPABASE_URL")
    supabase_key = supabase_key or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    endpoint = endpoint or os.getenv("COST_COLLECTOR_ENDPOINT")
    write_key = write_key or os.getenv("COST_WRITE_KEY")
    flush_at = int(os.getenv("COST_FLUSH_AT", str(flush_at)))
    flush_interval_ms = int(os.getenv("COST_FLUSH_INTERVAL_MS", str(flush_interval_ms)))
    timeout_s = float(os.getenv("COST_TIMEOUT_S", str(timeout_s)))
    if redaction_keys is None:
        rk_env = os.getenv("COST_REDACTION_KEYS")
        _state.redaction_keys = tuple((rk_env.split(",") if rk_env else _state.redaction_keys))
    else:
        _state.redaction_keys = tuple(redaction_keys)

    _state.server_pricing = bool(server_pricing)
    _state.pricing_override = pricing
    _state.pricing_table = pricing or DEFAULT_PRICING
    # Create a stable fingerprint of the active pricing table for audit trails
    try:
        _state.pricing_fp = hashlib.sha256(json.dumps(_state.pricing_table, sort_keys=True).encode()).hexdigest()[:12]
    except Exception:
        _state.pricing_fp = None

    # Choose sink explicitly when provided; otherwise optionally autodetect
    if sink:
        s = sink.lower()
        if s == "none":
            from .sinks import NoopSink
            _state.sink = NoopSink()
        elif s == "sqlite":
            _state.sink = build_sink(
                dsn=dsn,
                supabase_url=None,
                supabase_key=None,
                endpoint=None,
                write_key=None,
                timeout_s=timeout_s,
            )
        elif s == "supabase":
            if not (supabase_url and supabase_key):
                raise RuntimeError("llm_cost.init(sink='supabase') requires supabase_url and supabase_key")
            _state.sink = build_sink(
                dsn=None,
                supabase_url=supabase_url,
                supabase_key=supabase_key,
                endpoint=None,
                write_key=None,
                timeout_s=timeout_s,
            )
        elif s == "http":
            if not (endpoint and write_key):
                raise RuntimeError("llm_cost.init(sink='http') requires endpoint and write_key")
            _state.sink = build_sink(
                dsn=None,
                supabase_url=None,
                supabase_key=None,
                endpoint=endpoint,
                write_key=write_key,
                timeout_s=timeout_s,
            )
        else:
            raise ValueError("sink must be one of: sqlite | supabase | http | none")
    else:
        if not allow_autodetect:
            raise RuntimeError("llm_cost.init: explicit sink required (set sink=..., or COST_SINK env)")
        # Autodetect priority: HTTP > Supabase > SQLite
        _state.sink = build_sink(
            dsn=dsn,
            supabase_url=supabase_url,
            supabase_key=supabase_key,
            endpoint=endpoint,
            write_key=write_key,
            timeout_s=timeout_s,
        )
    _state.batcher = Batcher(sink=_state.sink, flush_at=flush_at, flush_interval_ms=flush_interval_ms, outbox_path=outbox_path, maxsize=max_queue_size)

    def _graceful(*_args):
        try:
            _state.batcher.flush()
        except Exception:
            pass
    atexit.register(_graceful)
    try:
        signal.signal(signal.SIGINT, lambda *args: _graceful())
        signal.signal(signal.SIGTERM, lambda *args: _graceful())
    except Exception:
        # Not all environments allow signal handling
        pass

    _state.initialized = True


def _resolve_rates(model: str) -> Tuple[Dict[str, float], str]:
    """Return (rates_entry, resolved_key) from the active pricing table.

    rates_entry keys may include: input, cached_input, output, reasoning.
    """
    table = _state.pricing_table or DEFAULT_PRICING
    entry = table.get(model)
    resolved_key = model
    if entry is None and _pricing_base is not None:
        base_key = _pricing_base(model)
        entry = table.get(base_key)
        resolved_key = base_key
    if entry is None:
        entry = DEFAULT_PRICING.get("gpt-4o-mini", {"input": 0.15, "output": 0.60})
        resolved_key = "gpt-4o-mini"
    return entry, resolved_key


def init_sqlite(
    *,
    dsn: str = "sqlite:///./llm_cost.db",
    flush_at: int = 20,
    flush_interval_ms: int = 3000,
    timeout_s: float = 2.0,
    outbox_path: Optional[str] = None,
    pricing: Optional[Dict[str, Dict[str, float]]] = None,
    server_pricing: bool = False,
    max_queue_size: int = 5000,
    force_reinit: bool = False,
) -> None:
    init(
        dsn=dsn,
        flush_at=flush_at,
        flush_interval_ms=flush_interval_ms,
        timeout_s=timeout_s,
        outbox_path=outbox_path,
        pricing=pricing,
        server_pricing=server_pricing,
        max_queue_size=max_queue_size,
        force_reinit=force_reinit,
        sink="sqlite",
        allow_autodetect=False,
    )


def init_supabase(
    *,
    supabase_url: str,
    supabase_key: str,
    flush_at: int = 20,
    flush_interval_ms: int = 3000,
    timeout_s: float = 2.0,
    outbox_path: Optional[str] = None,
    pricing: Optional[Dict[str, Dict[str, float]]] = None,
    server_pricing: bool = False,
    max_queue_size: int = 5000,
    force_reinit: bool = False,
) -> None:
    init(
        supabase_url=supabase_url,
        supabase_key=supabase_key,
        flush_at=flush_at,
        flush_interval_ms=flush_interval_ms,
        timeout_s=timeout_s,
        outbox_path=outbox_path,
        pricing=pricing,
        server_pricing=server_pricing,
        max_queue_size=max_queue_size,
        force_reinit=force_reinit,
        sink="supabase",
        allow_autodetect=False,
    )


def init_http(
    *,
    endpoint: str,
    write_key: str,
    flush_at: int = 20,
    flush_interval_ms: int = 3000,
    timeout_s: float = 2.0,
    outbox_path: Optional[str] = None,
    pricing: Optional[Dict[str, Dict[str, float]]] = None,
    server_pricing: bool = False,
    max_queue_size: int = 5000,
    force_reinit: bool = False,
) -> None:
    init(
        endpoint=endpoint,
        write_key=write_key,
        flush_at=flush_at,
        flush_interval_ms=flush_interval_ms,
        timeout_s=timeout_s,
        outbox_path=outbox_path,
        pricing=pricing,
        server_pricing=server_pricing,
        max_queue_size=max_queue_size,
        force_reinit=force_reinit,
        sink="http",
        allow_autodetect=False,
    )


def set_context(context: dict) -> None:
    """Set sticky arbitrary context (JSON-serializable dict).

    WARNING: In embedded DB mode (direct Postgres/Supabase/SQLite), effective context MUST include 'workspace_id'.
    """
    # redact potentially sensitive keys
    safe = {k: (None if k in _state.redaction_keys else v) for k, v in context.items()}
    # prune None
    safe = {k: v for k, v in safe.items() if v is not None}
    set_sticky_context(safe)


def _enqueue_row(row: dict) -> None:
    if not _state.batcher:
        raise RuntimeError("llm_cost.init() must be called before tracking")
    try:
        _state.batcher.enqueue(row)
    except QueueFullError:
        # Drop oldest is implemented in batcher; if still full, we log by raising silently
        # Intentionally avoid throwing to user code
        pass


def track_cost(
    *,
    model_arg: str = "model",
    provider: str = "openai",
    context_arg: Optional[str] = "context",
    request_id_arg: Optional[str] = "request_id",
    tokens_fn: Optional[Callable[[Any], Dict[str, int]]] = None,
    mode: str = "auto",  # 'auto' or 'defer'
):
    """Decorator to track non-streaming or streaming (defer) LLM calls.

    - auto: extracts usage → computes cost → upserts once
    - defer: do not write; caller MUST call finalize_llm_call with the same request_id
    """
    if mode not in ("auto", "defer"):
        raise ValueError("track_cost: mode must be 'auto' or 'defer'")

    def _decorator(func: Callable):
        def _sync(*args, **kwargs):
            result = func(*args, **kwargs)
            if mode == "defer":
                return result

            # auto mode
            # context
            sticky = ContextManager.current()
            call_ctx = kwargs.get(context_arg) if context_arg else None
            effective_ctx = merge_contexts(sticky, call_ctx)

            # request_id
            req_id = kwargs.get(request_id_arg) if request_id_arg else None
            if not req_id:
                req_id = default_request_id(effective_ctx.get("session_id"))

            # tokens
            usage = extract_usage(result) if tokens_fn is None else tokens_fn(result)
            tokens_in = int(usage.get("prompt_tokens", 0) or 0)
            tokens_out = int(usage.get("completion_tokens", 0) or 0)
            reasoning_tokens = int(usage.get("reasoning_tokens", 0) or 0)
            cached_input_tokens = int(usage.get("cached_input_tokens", 0) or 0)

            # cost
            if _state.server_pricing:
                cost_usd = 0.0
            else:
                # Use the same table source as _resolve_rates to avoid divergence
                cost_usd = compute_cost(
                    kwargs.get(model_arg) or effective_ctx.get("model") or "unknown",
                    tokens_in,
                    tokens_out,
                    _state.pricing_table,
                    reasoning_tokens=reasoning_tokens,
                    cached_input_tokens=cached_input_tokens,
                )

            # embedded mode requires workspace_id in effective context
            if _state.sink.requires_workspace_id and not effective_ctx.get("workspace_id"):
                # Skip write; developer must provide workspace_id in context
                return result

            # Enrich metadata with usage and rates used (audit trail) under context.metadata.billing
            model_used = kwargs.get(model_arg) or effective_ctx.get("model") or "unknown"
            rates_entry, resolved_key = _resolve_rates(model_used)
            meta = dict(effective_ctx.get("metadata", {}))
            billing_meta = {
                "usage_raw": {
                    "prompt_tokens": int(tokens_in),
                    "completion_tokens": int(tokens_out),
                    "reasoning_tokens": int(reasoning_tokens or 0),
                    "cached_input_tokens": int(cached_input_tokens or 0),
                },
                "rates_used": {
                    "input_rate": float(rates_entry.get("input", 0.0)),
                    "cached_input_rate": float(rates_entry.get("cached_input", rates_entry.get("input", 0.0))),
                    "output_rate": float(rates_entry.get("output", 0.0)),
                    "reasoning_rate": float(rates_entry.get("reasoning", rates_entry.get("output", 0.0))),
                    "model_resolved": resolved_key,
                    "pricing_source": ("override" if _state.pricing_override else "default"),
                    "pricing_version": _state.pricing_fp,
                },
            }
            meta.setdefault("billing", {}).update(billing_meta)
            effective_ctx["metadata"] = meta

            # Loud per-event pricing log (optional)
            if os.getenv("LLM_COST_LOG_RATES", "0") == "1":
                try:
                    import sys
                    print(
                        "\n================ [LLM_COST RATES USED] ================\n"
                        f"provider={provider} model={model_used} resolved={resolved_key}\n"
                        f"input_rate={rates_entry.get('input')} cached_input_rate={rates_entry.get('cached_input', rates_entry.get('input'))}\n"
                        f"output_rate={rates_entry.get('output')} reasoning_rate={rates_entry.get('reasoning', rates_entry.get('output'))}\n"
                        f"usage_in={tokens_in} usage_out={tokens_out} cached_in={cached_input_tokens} reasoning_out={reasoning_tokens}\n"
                        f"pricing_version={_state.pricing_fp}\n"
                        "==================================================\n",
                        file=sys.stderr,
                    )
                except Exception:
                    pass

            # Optional consistency check: recompute from rates_used and compare
            if os.getenv("LLM_COST_CONSISTENCY_CHECK", "1") == "1":
                try:
                    in_rate = float(rates_entry.get("input", 0.0))
                    out_rate = float(rates_entry.get("output", 0.0))
                    cached_rate = float(rates_entry.get("cached_input", in_rate))
                    reason_rate = float(rates_entry.get("reasoning", out_rate))
                    non_cached_in = max(0, int(tokens_in) - int(cached_input_tokens))
                    expected = (
                        non_cached_in * in_rate
                        + int(cached_input_tokens) * cached_rate
                        + max(0, int(tokens_out) - int(reasoning_tokens)) * out_rate
                        + int(reasoning_tokens) * reason_rate
                    ) / 1_000_000.0
                    if abs(float(cost_usd) - float(expected)) > 1e-9:
                        import sys
                        print(
                            "[LLM_COST MISMATCH] compute_cost vs rates_used diverge: "
                            f"cost_usd={float(cost_usd):.12f} expected_from_rates={float(expected):.12f} "
                            f"(model={model_used} resolved={resolved_key})",
                            file=sys.stderr,
                        )
                except Exception:
                    pass

            row = {
                "created_at": None,  # server/default
                "provider": provider,
                "model": model_used,
                "input_tokens": tokens_in,
                "output_tokens": tokens_out,
                "cost_usd": float(cost_usd),
                "request_id": req_id,
                "context": effective_ctx,
            }
            # workspace_id scalar field for embedded mode
            if _state.sink.requires_workspace_id:
                row["workspace_id"] = effective_ctx.get("workspace_id")

            _enqueue_row(row)
            return result

        async def _async(*args, **kwargs):
            result = await func(*args, **kwargs)
            if mode == "defer":
                return result

            sticky = ContextManager.current()
            call_ctx = kwargs.get(context_arg) if context_arg else None
            effective_ctx = merge_contexts(sticky, call_ctx)

            req_id = kwargs.get(request_id_arg) if request_id_arg else None
            if not req_id:
                req_id = default_request_id(effective_ctx.get("session_id"))

            usage = extract_usage(result) if tokens_fn is None else tokens_fn(result)
            tokens_in = int(usage.get("prompt_tokens", 0) or 0)
            tokens_out = int(usage.get("completion_tokens", 0) or 0)
            reasoning_tokens = int(usage.get("reasoning_tokens", 0) or 0)
            cached_input_tokens = int(usage.get("cached_input_tokens", 0) or 0)

            if _state.server_pricing:
                cost_usd = 0.0
            else:
                cost_usd = compute_cost(
                    kwargs.get(model_arg) or effective_ctx.get("model") or "unknown",
                    tokens_in,
                    tokens_out,
                    _state.pricing_table,
                    reasoning_tokens=reasoning_tokens,
                    cached_input_tokens=cached_input_tokens,
                )

            if _state.sink.requires_workspace_id and not effective_ctx.get("workspace_id"):
                return result

            model_used = kwargs.get(model_arg) or effective_ctx.get("model") or "unknown"
            rates_entry, resolved_key = _resolve_rates(model_used)
            meta = dict(effective_ctx.get("metadata", {}))
            billing_meta = {
                "usage_raw": {
                    "prompt_tokens": int(tokens_in),
                    "completion_tokens": int(tokens_out),
                    "reasoning_tokens": int(reasoning_tokens or 0),
                    "cached_input_tokens": int(cached_input_tokens or 0),
                },
                "rates_used": {
                    "input_rate": float(rates_entry.get("input", 0.0)),
                    "cached_input_rate": float(rates_entry.get("cached_input", rates_entry.get("input", 0.0))),
                    "output_rate": float(rates_entry.get("output", 0.0)),
                    "reasoning_rate": float(rates_entry.get("reasoning", rates_entry.get("output", 0.0))),
                    "model_resolved": resolved_key,
                    "pricing_source": ("override" if _state.pricing_override else "default"),
                    "pricing_version": _state.pricing_fp,
                },
            }
            meta.setdefault("billing", {}).update(billing_meta)
            effective_ctx["metadata"] = meta

            if os.getenv("LLM_COST_LOG_RATES", "0") == "1":
                try:
                    import sys
                    print(
                        "\n================ [LLM_COST RATES USED] ================\n"
                        f"provider={provider} model={model_used} resolved={resolved_key}\n"
                        f"input_rate={rates_entry.get('input')} cached_input_rate={rates_entry.get('cached_input', rates_entry.get('input'))}\n"
                        f"output_rate={rates_entry.get('output')} reasoning_rate={rates_entry.get('reasoning', rates_entry.get('output'))}\n"
                        f"usage_in={tokens_in} usage_out={tokens_out} cached_in={cached_input_tokens} reasoning_out={reasoning_tokens}\n"
                        f"pricing_version={_state.pricing_fp}\n"
                        "==================================================\n",
                        file=sys.stderr,
                    )
                except Exception:
                    pass

            if os.getenv("LLM_COST_CONSISTENCY_CHECK", "1") == "1":
                try:
                    in_rate = float(rates_entry.get("input", 0.0))
                    out_rate = float(rates_entry.get("output", 0.0))
                    cached_rate = float(rates_entry.get("cached_input", in_rate))
                    reason_rate = float(rates_entry.get("reasoning", out_rate))
                    non_cached_in = max(0, int(tokens_in) - int(cached_input_tokens))
                    expected = (
                        non_cached_in * in_rate
                        + int(cached_input_tokens) * cached_rate
                        + max(0, int(tokens_out) - int(reasoning_tokens)) * out_rate
                        + int(reasoning_tokens) * reason_rate
                    ) / 1_000_000.0
                    if abs(float(cost_usd) - float(expected)) > 1e-9:
                        import sys
                        print(
                            "[LLM_COST MISMATCH] compute_cost vs rates_used diverge: "
                            f"cost_usd={float(cost_usd):.12f} expected_from_rates={float(expected):.12f} "
                            f"(model={model_used} resolved={resolved_key})",
                            file=sys.stderr,
                        )
                except Exception:
                    pass

            row = {
                "created_at": None,
                "provider": provider,
                "model": model_used,
                "input_tokens": tokens_in,
                "output_tokens": tokens_out,
                "cost_usd": float(cost_usd),
                "request_id": req_id,
                "context": effective_ctx,
            }
            if _state.sink.requires_workspace_id:
                row["workspace_id"] = effective_ctx.get("workspace_id")

            _enqueue_row(row)
            return result

        # preserve sync/async
        return _async if hasattr(func, "__await__") else _sync

    return _decorator


def finalize_llm_call(
    *,
    provider: str,
    model: str,
    tokens_in: int,
    tokens_out: int,
    cost_usd: Optional[float] = None,
    request_id: str,
    context: Optional[dict] = None,
) -> None:
    sticky = ContextManager.current()
    effective_ctx = merge_contexts(sticky, context)

    if cost_usd is None:
        if _state.server_pricing:
            cost_usd = 0.0
        else:
            # If caller put reasoning_tokens into context, honor it
            rt = 0
            cit = 0
            try:
                rt = int((effective_ctx or {}).get("reasoning_tokens", 0) or 0)
            except Exception:
                rt = 0
            try:
                cit = int((effective_ctx or {}).get("cached_input_tokens", 0) or 0)
            except Exception:
                cit = 0
            cost_usd = compute_cost(
                model,
                tokens_in,
                tokens_out,
                _state.pricing_table,
                reasoning_tokens=rt,
                cached_input_tokens=cit,
            )

    if _state.sink.requires_workspace_id and not effective_ctx.get("workspace_id"):
        # Cannot write without a tenant scope in embedded mode
        return

    # Enrich metadata with usage and rates used
    rates_entry, resolved_key = _resolve_rates(model)
    meta = dict(effective_ctx.get("metadata", {}))
    billing_meta = {
        "usage_raw": {
            "prompt_tokens": int(tokens_in),
            "completion_tokens": int(tokens_out),
            "reasoning_tokens": int((effective_ctx or {}).get("reasoning_tokens", 0) or 0),
            "cached_input_tokens": int((effective_ctx or {}).get("cached_input_tokens", 0) or 0),
        },
        "rates_used": {
            "input_rate": float(rates_entry.get("input", 0.0)),
            "cached_input_rate": float(rates_entry.get("cached_input", rates_entry.get("input", 0.0))),
            "output_rate": float(rates_entry.get("output", 0.0)),
            "reasoning_rate": float(rates_entry.get("reasoning", rates_entry.get("output", 0.0))),
            "model_resolved": resolved_key,
            "pricing_source": ("override" if _state.pricing_override else "default"),
            "pricing_version": _state.pricing_fp,
        },
    }
    meta.setdefault("billing", {}).update(billing_meta)
    effective_ctx["metadata"] = meta

    if os.getenv("LLM_COST_LOG_RATES", "0") == "1":
        try:
            import sys
            print(
                "\n================ [LLM_COST RATES USED] ================\n"
                f"provider={provider} model={model} resolved={resolved_key}\n"
                f"input_rate={rates_entry.get('input')} cached_input_rate={rates_entry.get('cached_input', rates_entry.get('input'))}\n"
                f"output_rate={rates_entry.get('output')} reasoning_rate={rates_entry.get('reasoning', rates_entry.get('output'))}\n"
                f"usage_in={int(tokens_in)} usage_out={int(tokens_out)} cached_in={(effective_ctx or {}).get('cached_input_tokens', 0)} reasoning_out={(effective_ctx or {}).get('reasoning_tokens', 0)}\n"
                f"pricing_version={_state.pricing_fp}\n"
                "==================================================\n",
                file=sys.stderr,
            )
        except Exception:
            pass

    # Optional consistency check for finalize path as well
    if os.getenv("LLM_COST_CONSISTENCY_CHECK", "1") == "1":
        try:
            in_rate = float(rates_entry.get("input", 0.0))
            out_rate = float(rates_entry.get("output", 0.0))
            cached_rate = float(rates_entry.get("cached_input", in_rate))
            reason_rate = float(rates_entry.get("reasoning", out_rate))
            non_cached_in = max(0, int(tokens_in) - int((effective_ctx or {}).get("cached_input_tokens", 0) or 0))
            expected = (
                non_cached_in * in_rate
                + int((effective_ctx or {}).get("cached_input_tokens", 0) or 0) * cached_rate
                + max(0, int(tokens_out) - int((effective_ctx or {}).get("reasoning_tokens", 0) or 0)) * out_rate
                + int((effective_ctx or {}).get("reasoning_tokens", 0) or 0) * reason_rate
            ) / 1_000_000.0
            if abs(float(cost_usd) - float(expected)) > 1e-9:
                import sys
                print(
                    "[LLM_COST MISMATCH] compute_cost vs rates_used diverge: "
                    f"cost_usd={float(cost_usd):.12f} expected_from_rates={float(expected):.12f} "
                    f"(model={model} resolved={resolved_key})",
                    file=sys.stderr,
                )
        except Exception:
            pass

    row = {
        "created_at": None,
        "provider": provider,
        "model": model,
        "input_tokens": int(tokens_in),
        "output_tokens": int(tokens_out),
        "cost_usd": float(cost_usd),
        "request_id": request_id,
        "context": effective_ctx,
    }
    if _state.sink.requires_workspace_id:
        row["workspace_id"] = effective_ctx.get("workspace_id")
    _enqueue_row(row)


def track(
    *,
    fn: Callable,
    args: Tuple[Any, ...] = (),
    kwargs: Dict[str, Any] = {},
    model: str,
    provider: str,
    request_id: Optional[str] = None,
    context: Optional[dict] = None,
) -> Any:
    result = fn(*args, **kwargs)
    sticky = ContextManager.current()
    effective_ctx = merge_contexts(sticky, context)

    if not request_id:
        request_id = default_request_id(effective_ctx.get("session_id"))

    usage = extract_usage(result)
    tokens_in = int(usage.get("prompt_tokens", 0) or 0)
    tokens_out = int(usage.get("completion_tokens", 0) or 0)

    if _state.server_pricing:
        cost_usd = 0.0
    else:
        cost_usd = compute_cost(model, tokens_in, tokens_out, _state.pricing_table)

    if _state.sink.requires_workspace_id and not effective_ctx.get("workspace_id"):
        return result

    row = {
        "created_at": None,
        "provider": provider,
        "model": model,
        "input_tokens": tokens_in,
        "output_tokens": tokens_out,
        "cost_usd": float(cost_usd),
        "request_id": request_id,
        "context": effective_ctx,
    }
    if _state.sink.requires_workspace_id:
        row["workspace_id"] = effective_ctx.get("workspace_id")
    _enqueue_row(row)
    return result


def flush() -> None:
    """Force a flush of any queued events (useful in tests/shutdown)."""
    if _state.batcher:
        _state.batcher.flush()
