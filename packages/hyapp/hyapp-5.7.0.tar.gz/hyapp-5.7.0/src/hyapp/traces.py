from __future__ import annotations

import uuid
from contextvars import ContextVar
from typing import Any

# See also: https://github.com/snok/asgi-correlation-id
TRACE_ID_VAR: ContextVar[str | None] = ContextVar("trace_id", default=None)
LOG_EXTRAS_VAR: ContextVar[dict[str, Any] | None] = ContextVar("log_extras", default=None)


def new_trace_id(
    subprefix: str, prefix: str = "", total_len: int = 16, parent: str | None = None, parent_sep: str = "__"
) -> str:
    uuid_len = total_len - len(prefix) - len(subprefix)
    uuid_val = uuid.uuid4().hex[:uuid_len]  # This could be simple `getrandbits` though.
    result = f"{prefix}{subprefix}{uuid_val}"
    if parent:
        result = f"{parent}{parent_sep}{result}"
    return result
