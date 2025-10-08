from __future__ import annotations

from typing import List, Dict, Any, Optional
import time


class SinkBase:
    requires_workspace_id: bool = True  # embedded mode default

    def upsert_many(self, rows: List[Dict[str, Any]]) -> None:
        raise NotImplementedError


class SqliteSink(SinkBase):
    def __init__(self, dsn: str, timeout_s: float = 2.0):
        import os
        if os.getenv("LLM_COST_DEBUG") == "1":
            import sys
            print(f"[llm_cost DEBUG] SqliteSink.__init__ called with dsn={dsn}", file=sys.stderr)
        import sqlite3
        import threading
        # dsn expected as sqlite:///path
        path = dsn.replace("sqlite:///", "")
        if os.getenv("LLM_COST_DEBUG") == "1":
            print(f"[llm_cost DEBUG] SqliteSink creating DB at path={path}", file=sys.stderr)
        self._lock = threading.Lock()
        self.conn = sqlite3.connect(path, check_same_thread=False, isolation_level=None, timeout=timeout_s)
        cur = self.conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=NORMAL;")
        # create table if not exists
        cur.execute(
            """
            create table if not exists billing_ledger (
              id text primary key,
              created_at text default (datetime('now')),
              workspace_id text not null,
              provider text not null,
              model text not null,
              input_tokens integer not null,
              output_tokens integer not null,
              cost_usd real not null,
              request_id text,
              context text not null
            )
            """
        )
        cur.execute("create index if not exists ix_billing_created on billing_ledger(created_at);")
        cur.execute("create unique index if not exists ux_billing_ws_req on billing_ledger(workspace_id, request_id);")
        self.conn.commit()
        if os.getenv("LLM_COST_DEBUG") == "1":
            print(f"[llm_cost DEBUG] SqliteSink.__init__ complete, table created", file=sys.stderr)

    def upsert_many(self, rows: List[Dict[str, Any]]) -> None:
        import json, uuid
        import os
        if os.getenv("LLM_COST_DEBUG") == "1":
            import sys
            print(f"[llm_cost DEBUG] SqliteSink.upsert_many called with {len(rows)} rows", file=sys.stderr)
        with self._lock:
            cur = self.conn.cursor()
            for r in rows:
                if os.getenv("LLM_COST_DEBUG") == "1":
                    print(f"[llm_cost DEBUG] SqliteSink upserting row: ws={r.get('workspace_id')}, req={r.get('request_id')}, model={r.get('model')}", file=sys.stderr)
                try:
                    rid = r.get("request_id") or str(uuid.uuid4())
                    ws = r.get("workspace_id")
                    ctx = json.dumps(r.get("context") or {})
                    # SQLite upsert emulation: try update then insert if no row changed
                    cur.execute(
                        """
                        update billing_ledger
                        set provider=?, model=?, input_tokens=?, output_tokens=?, cost_usd=?, context=?
                        where workspace_id=? and request_id=?
                        """,
                        (r["provider"], r["model"], r["input_tokens"], r["output_tokens"], r["cost_usd"], ctx, ws, rid),
                    )
                    if os.getenv("LLM_COST_DEBUG") == "1":
                        print(f"[llm_cost DEBUG] SqliteSink update rowcount={cur.rowcount}", file=sys.stderr)
                    if cur.rowcount == 0:
                        if os.getenv("LLM_COST_DEBUG") == "1":
                            print(f"[llm_cost DEBUG] SqliteSink inserting new row", file=sys.stderr)
                        cur.execute(
                            """
                            insert into billing_ledger (id, workspace_id, provider, model, input_tokens, output_tokens, cost_usd, request_id, context)
                            values (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (str(uuid.uuid4()), ws, r["provider"], r["model"], r["input_tokens"], r["output_tokens"], r["cost_usd"], rid, ctx),
                        )
                except Exception as e:
                    if os.getenv("LLM_COST_DEBUG") == "1":
                        import sys
                        print(f"[llm_cost DEBUG] SqliteSink row upsert exception: {e}", file=sys.stderr)
                        import traceback
                        traceback.print_exc(file=sys.stderr)
                    raise
            self.conn.commit()
            if os.getenv("LLM_COST_DEBUG") == "1":
                print(f"[llm_cost DEBUG] SqliteSink.upsert_many committed", file=sys.stderr)


class SupabaseSink(SinkBase):
    def __init__(self, url: str, key: str, timeout_s: float = 2.0, table: str = "billing_ledger"):
        from supabase import create_client
        self.client = create_client(url, key)
        self.table = table
        self.timeout_s = timeout_s

    def upsert_many(self, rows: List[Dict[str, Any]]) -> None:
        import os
        import uuid
        import time
        import random
        # Prepare batch payload
        payload = []
        for r in rows:
            pruned = dict(r)
            if "created_at" in pruned and pruned["created_at"] is None:
                del pruned["created_at"]
            if "id" not in pruned or not pruned["id"]:
                pruned["id"] = str(uuid.uuid4())
            payload.append(pruned)

        if not payload:
            return

        # Batched upsert with limited retries and exponential backoff for 429/5xx
        max_retries = int(os.getenv("COST_SUPABASE_MAX_RETRIES", "4"))
        backoff_base = float(os.getenv("COST_SUPABASE_BACKOFF_BASE", "0.25"))  # seconds
        last_err = None
        for attempt in range(max_retries + 1):
            try:
                # upsert=true leverages unique constraint on (workspace_id, request_id)
                if os.getenv("LLM_COST_DEBUG") == "1":
                    import sys
                    print(f"[llm_cost DEBUG] SupabaseSink upsert attempt={attempt} size={len(payload)}", file=sys.stderr)
                self.client.table(self.table).upsert(payload, on_conflict="workspace_id,request_id").execute()
                return
            except Exception as e:
                last_err = e
                msg = str(e).lower()
                is_retryable = any(code in msg for code in ["429", "timeout", "503", "500", "504"]) or "rate" in msg
                if attempt < max_retries and is_retryable:
                    sleep_s = backoff_base * (2 ** attempt) * (0.5 + random.random())
                    time.sleep(min(sleep_s, 5.0))
                    continue
                # non-retryable or exhausted attempts → raise to background to trigger outbox
                raise last_err


class HttpSink(SinkBase):
    requires_workspace_id = False

    def __init__(self, endpoint: str, write_key: str, timeout_s: float = 2.0):
        import httpx
        self.endpoint = endpoint.rstrip("/") + "/v1/batch"
        self.write_key = write_key
        self.client = httpx.Client(timeout=timeout_s)

    def upsert_many(self, rows: List[Dict[str, Any]]) -> None:
        # Send events; server handles idempotency on (project_id, request_id)
        events = []
        for r in rows:
            e = {k: v for k, v in r.items() if k != "workspace_id"}
            events.append({"event": "llm_call", **e})
        headers = {"Authorization": f"Bearer {self.write_key}"}
        self.client.post(self.endpoint, json={"events": events}, headers=headers)


class NoopSink(SinkBase):
    requires_workspace_id = False

    def upsert_many(self, rows: List[Dict[str, Any]]) -> None:
        # Intentionally do nothing
        return


def build_sink(
    *,
    dsn: Optional[str],
    supabase_url: Optional[str],
    supabase_key: Optional[str],
    endpoint: Optional[str],
    write_key: Optional[str],
    timeout_s: float,
):
    import os
    if os.getenv("LLM_COST_DEBUG") == "1":
        import sys
        print(f"[llm_cost DEBUG] build_sink called: dsn={dsn}, endpoint={endpoint}, supabase_url={supabase_url}", file=sys.stderr)
    # Priority 1: HTTP collector (highest priority for service mode)
    if endpoint and write_key:
        if os.getenv("LLM_COST_DEBUG") == "1":
            import sys
            print(f"[llm_cost DEBUG] build_sink -> HttpSink", file=sys.stderr)
        return HttpSink(endpoint=endpoint, write_key=write_key, timeout_s=timeout_s)
    # Priority 2: Supabase (preferred for embedded mode with cloud DB)
    if supabase_url and supabase_key:
        if os.getenv("LLM_COST_DEBUG") == "1":
            import sys
            print(f"[llm_cost DEBUG] build_sink -> SupabaseSink", file=sys.stderr)
        return SupabaseSink(url=supabase_url, key=supabase_key, timeout_s=timeout_s)
    # Priority 3: Explicit SQLite DSN (starts with sqlite:///)
    if dsn and dsn.startswith("sqlite:///"):
        if os.getenv("LLM_COST_DEBUG") == "1":
            import sys
            print(f"[llm_cost DEBUG] build_sink -> SqliteSink (explicit dsn={dsn})", file=sys.stderr)
        return SqliteSink(dsn=dsn, timeout_s=timeout_s)
    # Priority 4: Default SQLite
    if os.getenv("LLM_COST_DEBUG") == "1":
        import sys
        print(f"[llm_cost DEBUG] build_sink -> SqliteSink with dsn={dsn or 'sqlite:///./llm_cost.db'}", file=sys.stderr)
    return SqliteSink(dsn=dsn or "sqlite:///./llm_cost.db", timeout_s=timeout_s)
