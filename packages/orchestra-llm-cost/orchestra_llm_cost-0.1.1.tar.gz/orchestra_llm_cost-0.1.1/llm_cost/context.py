from __future__ import annotations

from typing import Optional, Dict, Any
import threading


class ContextManager:
    _local = threading.local()

    @classmethod
    def current(cls) -> Dict[str, Any]:
        ctx = getattr(cls._local, "ctx", None)
        if ctx is None:
            ctx = {}
            setattr(cls._local, "ctx", ctx)
        return ctx

    @classmethod
    def set(cls, ctx: Dict[str, Any]) -> None:
        setattr(cls._local, "ctx", dict(ctx))


def set_sticky_context(ctx: Dict[str, Any]) -> None:
    ContextManager.set(ctx)


def merge_contexts(sticky: Dict[str, Any], call_ctx: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not call_ctx:
        return dict(sticky)
    merged = dict(sticky)
    for k, v in call_ctx.items():
        if v is None:
            # prune None
            merged.pop(k, None)
        else:
            merged[k] = v
    return merged


def get_effective_context(call_ctx: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    return merge_contexts(ContextManager.current(), call_ctx)
