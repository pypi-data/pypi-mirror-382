from __future__ import annotations

import threading
import time
from typing import Optional, List, Dict, Any
from queue import Queue, Full, Empty


class QueueFullError(Exception):
    pass


class Batcher:
    def __init__(self, sink, flush_at: int = 20, flush_interval_ms: int = 3000, outbox_path: Optional[str] = None, maxsize: int = 5000):
        self.sink = sink
        self.flush_at = max(1, int(flush_at))
        self.flush_interval_ms = max(100, int(flush_interval_ms))
        # Allow durable outbox via env or param; default remains None
        import os
        self.outbox_path = outbox_path or os.getenv("COST_OUTBOX_PATH")
        self.q: Queue = Queue(maxsize=maxsize)
        self._stop = threading.Event()
        self._worker = threading.Thread(target=self._run, name="llm_cost_batcher", daemon=True)
        self._worker.start()

    def enqueue(self, row: Dict[str, Any]) -> None:
        try:
            self.q.put_nowait(row)
        except Full:
            # drop oldest: drain one then insert
            try:
                self.q.get_nowait()
                self.q.put_nowait(row)
            except Exception:
                raise QueueFullError()

    def _run(self):
        buf: List[Dict[str, Any]] = []
        last = time.time()
        interval = self.flush_interval_ms / 1000.0
        while not self._stop.is_set():
            try:
                item = self.q.get(timeout=0.1)
                buf.append(item)
                if len(buf) >= self.flush_at:
                    self._flush(buf)
                    buf = []
                continue
            except Empty:
                pass
            now = time.time()
            if buf and (now - last) >= interval:
                self._flush(buf)
                buf = []
                last = now
        # final drain
        if buf:
            self._flush(buf)

    def _flush(self, rows: List[Dict[str, Any]]):
        try:
            self.sink.upsert_many(rows)
        except Exception as e:
            import os
            if os.getenv("LLM_COST_DEBUG") == "1":
                import sys
                print(f"[llm_cost DEBUG] Batcher._flush exception: {e}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)
            # best-effort write to outbox
            if self.outbox_path:
                try:
                    import json
                    # Ensure directory exists
                    import pathlib
                    pathlib.Path(self.outbox_path).parent.mkdir(parents=True, exist_ok=True)
                    with open(self.outbox_path, "a") as f:
                        for r in rows:
                            f.write(json.dumps(r) + "\n")
                except Exception:
                    pass

    def flush(self):
        # Drain queue and flush
        rows: List[Dict[str, Any]] = []
        while True:
            try:
                rows.append(self.q.get_nowait())
            except Empty:
                break
        if rows:
            self._flush(rows)

    def stop(self):
        self._stop.set()
        self._worker.join(timeout=1.5)
