"""Shared runtime object — sab modules ek hi jagah se db/engine/bot lete hain."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Runtime:
    db: object
    engine: object
    cfg: object
    bot: object | None = None
    state: dict = field(default_factory=dict)
    lock: object | None = None

    def owner_name(self) -> str:
        owner = getattr(self.cfg, "OWNER_ID", 0)
        try:
            row = self.db.user(owner) if owner else None
        except Exception:
            row = None
        if row:
            return row["name"] or (f"@{row['username']}" if row["username"] else str(owner))
        return "owner"


_RT: Runtime | None = None


def set_rt(rt: Runtime) -> None:
    global _RT
    _RT = rt


def rt() -> Runtime:
    if _RT is None:
        raise RuntimeError("runtime not initialised")
    return _RT
