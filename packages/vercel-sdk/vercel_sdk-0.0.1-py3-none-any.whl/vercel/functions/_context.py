from __future__ import annotations

from dataclasses import dataclass
from typing import Awaitable, Callable, Mapping


@dataclass
class RuntimeContext:
    wait_until: Callable[[Awaitable[object]], None] | None = None
    cache: object | None = None
    purge: object | None = None
    headers: Mapping[str, str] | None = None


_context: RuntimeContext = RuntimeContext()


def get_context() -> RuntimeContext:
    return _context


def set_context(ctx: RuntimeContext) -> None:
    global _context
    _context = ctx
