from __future__ import annotations

import time
import uuid
from typing import Optional


def default_request_id(session_id: Optional[str]) -> str:
    return f"{session_id or 'sess'}:{int(time.time()*1e9)}:{uuid.uuid4().hex[:8]}"


def new_request_id(prefix: Optional[str] = None) -> str:
    return f"{prefix + ':' if prefix else ''}{uuid.uuid4().hex}:{int(time.time()*1e9)}"
