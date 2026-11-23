"""
Preview ke liye sample data — real DB + fake engine.

Isse screens bilkul waise hi bante hain jaise live bot me,
bas process ke bajaye thos (deterministic) numbers aate hain.
"""
from __future__ import annotations

import tempfile
import time
from pathlib import Path

from .. import config
from ..core.app_context import Runtime
from ..core.db import DB

SAMPLE_LOGS = """[nik-hoster] starting runner…
[telethon] connecting to 149.154.167.51:443
[telethon] connection retry 1/5 — dc 2
[telethon] auth key verified
[nik-hoster] online as Nik (@nikku)
[nik-hoster] prefix = .
[2026-11-23 10:41:07] .ping → 122 ms
[2026-11-23 10:41:19] .alive → ok
[2026-11-23 10:42:02] message from @arjun: hi
[2026-11-23 10:42:02] reply sent (0.8s)
[2026-11-23 10:43:11] floodwait 12s → waiting
[2026-11-23 10:43:23] resumed
[2026-11-23 10:44:38] auto-restart kept alive · uptime 2h 14m"""


class FakeEngine:
    """Sirf UI ke liye — koi real process nahi."""

    max_restarts = 5

    def __init__(self):
        self._rt = {
            1: {"status": "running", "pid": 4127, "uptime": 2 * 3600 + 14 * 60,
                "cpu": 3.0, "ram_mb": 58.3},
            2: {"status": "stopped", "pid": None, "uptime": 0, "cpu": 0.0, "ram_mb": 0.0},
        }

    def runtime(self, bot_id: int) -> dict:
        return self._rt.get(int(bot_id),
                            {"status": "stopped", "pid": None, "uptime": 0,
                             "cpu": 0.0, "ram_mb": 0.0})

    def is_running(self, bot_id: int) -> bool:
        return self.runtime(bot_id)["status"] in {"running", "starting", "queued"}

    def host_stats(self) -> dict:
        return {
            "uptime": 6 * 3600 + 41 * 60, "cpu": 18.4, "ram_pct": 41.0,
            "ram_used": 786 * 1024 * 1024, "ram_total": 1920 * 1024 * 1024,
            "disk_pct": 23.0, "disk_free": 14 * 1024 ** 3, "disk_total": 19 * 1024 ** 3,
            "load": 0.42, "cores": 2, "engine_procs": 1,
        }

    def logs(self, bot_id: int, lines: int = 22) -> str:
        return "\n".join(SAMPLE_LOGS.splitlines()[-lines:])

    def logs_size(self, bot_id: int) -> int:
        return 18_432

    def handle(self, bot_id: int):
        return None

    def safe_name(self, raw: str, fallback: str = "bot") -> str:
        return (raw or fallback).strip().replace(" ", "-")[:24] or fallback


def build_sample(ctx_dir: Path | None = None) -> Runtime:
    tmp = Path(ctx_dir or tempfile.mkdtemp(prefix="nk-preview-"))
    db = DB(tmp / "preview.db")
    now = int(time.time())

    db.x("INSERT INTO users(id,username,name,plan,created,last_seen) VALUES(?,?,?,?,?,?)",
         (111, "nikku", "ɴɪᴋ", "pro", now - 86400 * 9, now - 40))
    db.x("INSERT INTO users(id,username,name,plan,created,last_seen) VALUES(?,?,?,?,?,?)",
         (222, "arjun_x", "ᴀʀᴊᴜɴ", "free", now - 86400 * 3, now - 600))
    db.x("INSERT INTO users(id,username,name,plan,created,last_seen) VALUES(?,?,?,?,?,?)",
         (333, "sonu", "ꜱᴏɴᴜ", "elite", now - 86400 * 21, now - 120))
    db.x("INSERT INTO users(id,username,name,plan,banned,created,last_seen) VALUES(?,?,?,?,?,?,?)",
         (444, "spam_king", "ꜱᴘᴀᴍ", "free", 1, now - 86400, now - 86400))

    b1 = db.add_bot(111, "ᴋɪɴɢ-x", "session", "/opt/nik/users/111/king/runner.py",
                    "/opt/nik/users/111/king", autostart=1)
    b2 = db.add_bot(111, "ꜱɴɪᴘᴇʀ", "py", "/opt/nik/users/111/sniper/main.py",
                    "/opt/nik/users/111/sniper", autostart=1)
    db.add_bot(222, "ᴀʀᴊᴜɴ-01", "py", "/opt/nik/users/222/a1/main.py",
               "/opt/nik/users/222/a1", autostart=0)
    db.set_bot_status(b1, "running", started=True)
    db.set_bot_status(b2, "stopped")
    db.x("UPDATE bots SET restarts=? WHERE id=?", (1, b1))
    db.x("UPDATE bots SET last_error=? WHERE id=?",
         ("ModuleNotFoundError: No module named 'telethon' — auto-fix ne install kar diya", b2))

    db.set_env(b1, "NK_API_ID", "36526099")
    db.set_env(b1, "NK_API_HASH", "5269e9b4dfdef6a38cd30df4dfa11285")
    db.set_env(b1, "NK_SESSION", "1BVtsOK7x_long_session_string_value_here")
    db.set_env(b1, "NK_PREFIX", ".")

    db.add_session(111, "ᴋɪɴɢ-x", 36526099, "5269e9b4dfdef6a38cd30df4dfa11285",
                   "1BVtsOK7x_long_session_string_value_here", "+919999999999")
    db.add_session(111, "ꜱᴇᴄᴏɴᴅ", 29846112, "b8f2c1d9e4a7460fb1c2d3e4f5a6b7c8",
                   "1BVtsOK_another_session_string_value_2", "+918888888888")

    db.log_event("deploy · ᴋɪɴɢ-x (session)", "deploy", 111, b1)
    db.log_event("start · ᴋɪɴɢ-x (pid 4127)", "start", 111, b1)
    db.log_event("user @arjun_x joined", "admin", 222, 0)
    db.log_event("plan pro → 222", "admin", 111, 0)
    db.log_event("delete · old.py", "delete", 222, 0)
    db.log_event("crash · ᴀʀᴊᴜɴ-01 rc=1 — restart #1/5", "error", 222, 3)

    return Runtime(db=db, engine=FakeEngine(), cfg=config, bot=None)
