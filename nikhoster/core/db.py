"""
NIK HOSTER v1 — storage.

SQLite + WAL + synchronous=NORMAL -> writes ~10x faster than default,
aur ek hi connection (lock ke saath) so panels never "stuck" lagte hain.
"""
from __future__ import annotations

import sqlite3
import threading
import time
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id          INTEGER PRIMARY KEY,
    username    TEXT,
    name        TEXT,
    plan        TEXT    DEFAULT 'free',
    plan_until  INTEGER DEFAULT 0,
    banned      INTEGER DEFAULT 0,
    created     INTEGER DEFAULT 0,
    last_seen   INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS bots (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id      INTEGER NOT NULL,
    name         TEXT    NOT NULL,
    kind         TEXT    DEFAULT 'py',
    path         TEXT    NOT NULL,
    workdir      TEXT    NOT NULL,
    status       TEXT    DEFAULT 'stopped',
    autostart    INTEGER DEFAULT 0,
    autofix      INTEGER DEFAULT 1,
    restarts     INTEGER DEFAULT 0,
    started_at   REAL    DEFAULT 0,
    last_exit    INTEGER DEFAULT 0,
    last_error   TEXT    DEFAULT '',
    created      INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_bots_user ON bots(user_id);

CREATE TABLE IF NOT EXISTS bot_env (
    bot_id INTEGER NOT NULL,
    k      TEXT NOT NULL,
    v      TEXT NOT NULL,
    PRIMARY KEY (bot_id, k)
);

CREATE TABLE IF NOT EXISTS sessions (
    id       INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id  INTEGER NOT NULL,
    label    TEXT NOT NULL,
    api_id   INTEGER NOT NULL,
    api_hash TEXT NOT NULL,
    session  TEXT NOT NULL,
    phone    TEXT DEFAULT '',
    created  INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_sessions_user ON sessions(user_id);

CREATE TABLE IF NOT EXISTS settings (
    k TEXT PRIMARY KEY,
    v TEXT
);

CREATE TABLE IF NOT EXISTS events (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ts      INTEGER DEFAULT 0,
    level   TEXT DEFAULT 'info',
    user_id INTEGER DEFAULT 0,
    bot_id  INTEGER DEFAULT 0,
    text    TEXT DEFAULT ''
);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(ts DESC);
"""


class DB:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(self.path), check_same_thread=False, timeout=20)
        self._conn.row_factory = sqlite3.Row
        with self._lock:
            cur = self._conn.cursor()
            cur.execute("PRAGMA journal_mode=WAL")
            cur.execute("PRAGMA synchronous=NORMAL")
            cur.execute("PRAGMA temp_store=MEMORY")
            cur.execute("PRAGMA mmap_size=67108864")
            cur.execute("PRAGMA foreign_keys=ON")
            cur.executescript(SCHEMA)
            self._conn.commit()

    # ── low level ──────────────────────────────────────────────────────────
    def all(self, sql: str, params: tuple = ()) -> list[sqlite3.Row]:
        with self._lock:
            return self._conn.execute(sql, params).fetchall()

    def one(self, sql: str, params: tuple = ()) -> sqlite3.Row | None:
        with self._lock:
            return self._conn.execute(sql, params).fetchone()

    def scalar(self, sql: str, params: tuple = (), default=0):
        row = self.one(sql, params)
        if row is None:
            return default
        value = row[0]
        return default if value is None else value

    def x(self, sql: str, params: tuple = ()) -> int:
        with self._lock:
            cur = self._conn.execute(sql, params)
            self._conn.commit()
            return cur.lastrowid

    def close(self) -> None:
        with self._lock:
            try:
                self._conn.commit()
                self._conn.close()
            except Exception:
                pass

    # ── users ──────────────────────────────────────────────────────────────
    def touch_user(self, user_id: int, username: str = "", name: str = "") -> None:
        now = int(time.time())
        self.x(
            """INSERT INTO users(id, username, name, created, last_seen)
               VALUES(?,?,?,?,?)
               ON CONFLICT(id) DO UPDATE SET
                 username=excluded.username,
                 name=CASE WHEN excluded.name != '' THEN excluded.name ELSE users.name END,
                 last_seen=excluded.last_seen""",
            (int(user_id), username or "", name or "", now, now),
        )

    def user(self, user_id: int):
        return self.one("SELECT * FROM users WHERE id=?", (int(user_id),))

    def plan_of(self, user_id: int) -> str:
        row = self.user(user_id)
        if not row:
            return "free"
        plan = row["plan"] or "free"
        until = row["plan_until"] or 0
        if until and int(until) < int(time.time()):
            self.x("UPDATE users SET plan='free', plan_until=0 WHERE id=?", (int(user_id),))
            return "free"
        return plan

    def set_plan(self, user_id: int, plan: str, days: int = 0) -> None:
        until = int(time.time() + days * 86400) if days else 0
        self.touch_user(int(user_id))
        self.x("UPDATE users SET plan=?, plan_until=? WHERE id=?", (plan, until, int(user_id)))

    def set_banned(self, user_id: int, banned: bool) -> None:
        self.touch_user(int(user_id))
        self.x("UPDATE users SET banned=? WHERE id=?", (1 if banned else 0, int(user_id)))

    def users_page(self, page: int = 0, per: int = 8, query: str = ""):
        offset = max(0, page) * per
        if query:
            like = f"%{query}%"
            rows = self.all(
                """SELECT * FROM users
                   WHERE CAST(id AS TEXT) LIKE ? OR username LIKE ? OR name LIKE ?
                   ORDER BY last_seen DESC LIMIT ? OFFSET ?""",
                (like, like, like, per, offset),
            )
            total = self.scalar(
                """SELECT COUNT(*) FROM users
                   WHERE CAST(id AS TEXT) LIKE ? OR username LIKE ? OR name LIKE ?""",
                (like, like, like),
            )
        else:
            rows = self.all("SELECT * FROM users ORDER BY last_seen DESC LIMIT ? OFFSET ?", (per, offset))
            total = self.scalar("SELECT COUNT(*) FROM users")
        return rows, int(total or 0)

    # ── bots ───────────────────────────────────────────────────────────────
    def add_bot(self, user_id: int, name: str, kind: str, path: str, workdir: str,
                autostart: int = 0) -> int:
        return self.x(
            """INSERT INTO bots(user_id, name, kind, path, workdir, status,
                                autostart, created, autofix)
               VALUES(?,?,?,?,?, 'stopped', ?, ?, 1)""",
            (int(user_id), name, kind, str(path), str(workdir), autostart, int(time.time())),
        )

    def bot(self, bot_id: int):
        return self.one("SELECT * FROM bots WHERE id=?", (int(bot_id),))

    def bots_of(self, user_id: int):
        return self.all("SELECT * FROM bots WHERE user_id=? ORDER BY id ASC", (int(user_id),))

    def all_bots(self):
        return self.all("SELECT * FROM bots ORDER BY id ASC")

    def count_bots(self, user_id: int) -> int:
        return int(self.scalar("SELECT COUNT(*) FROM bots WHERE user_id=?", (int(user_id),)))

    def count_running(self, user_id: int | None = None) -> int:
        if user_id is None:
            return int(self.scalar("SELECT COUNT(*) FROM bots WHERE status IN ('running','starting')"))
        return int(self.scalar(
            "SELECT COUNT(*) FROM bots WHERE user_id=? AND status IN ('running','starting')",
            (int(user_id),)))

    def set_bot_status(self, bot_id: int, status: str, *, error: str | None = None,
                       restarts: int | None = None, started: bool = False,
                       exit_now: bool = False) -> None:
        fields = ["status=?"]
        params: list = [status]
        if error is not None:
            fields.append("last_error=?")
            params.append(str(error)[:600])
        if restarts is not None:
            fields.append("restarts=?")
            params.append(int(restarts))
        if started:
            fields.append("started_at=?")
            params.append(time.time())
        if exit_now:
            fields.append("last_exit=?")
            params.append(int(time.time()))
        params.append(int(bot_id))
        self.x(f"UPDATE bots SET {', '.join(fields)} WHERE id=?", tuple(params))

    def rename_bot(self, bot_id: int, name: str) -> None:
        self.x("UPDATE bots SET name=? WHERE id=?", (name, int(bot_id)))

    def set_bot_flag(self, bot_id: int, flag: str, value: int) -> None:
        if flag not in {"autostart", "autofix"}:
            raise ValueError(flag)
        self.x(f"UPDATE bots SET {flag}=? WHERE id=?", (int(bool(value)), int(bot_id)))

    def delete_bot(self, bot_id: int) -> None:
        self.x("DELETE FROM bot_env WHERE bot_id=?", (int(bot_id),))
        self.x("DELETE FROM bots WHERE id=?", (int(bot_id),))

    def rotate_names(self, bot_id: int, new_name: str) -> None:
        self.x("UPDATE bots SET name=? WHERE id=?", (new_name, int(bot_id)))

    # ── env ────────────────────────────────────────────────────────────────
    def env_of(self, bot_id: int) -> dict[str, str]:
        return {r["k"]: r["v"] for r in self.all("SELECT k,v FROM bot_env WHERE bot_id=?", (int(bot_id),))}

    def set_env(self, bot_id: int, k: str, v: str) -> None:
        self.x("INSERT INTO bot_env(bot_id,k,v) VALUES(?,?,?) "
               "ON CONFLICT(bot_id,k) DO UPDATE SET v=excluded.v",
               (int(bot_id), k, v))

    def del_env(self, bot_id: int, k: str) -> None:
        self.x("DELETE FROM bot_env WHERE bot_id=? AND k=?", (int(bot_id), k))

    # ── sessions ───────────────────────────────────────────────────────────
    def add_session(self, user_id: int, label: str, api_id: int, api_hash: str,
                    session: str, phone: str = "") -> int:
        return self.x(
            """INSERT INTO sessions(user_id,label,api_id,api_hash,session,phone,created)
               VALUES(?,?,?,?,?,?,?)""",
            (int(user_id), label, int(api_id), api_hash, session, phone, int(time.time())),
        )

    def sessions_of(self, user_id: int):
        return self.all("SELECT * FROM sessions WHERE user_id=? ORDER BY id DESC", (int(user_id),))

    def session(self, session_id: int):
        return self.one("SELECT * FROM sessions WHERE id=?", (int(session_id),))

    def del_session(self, session_id: int) -> None:
        self.x("DELETE FROM sessions WHERE id=?", (int(session_id),))

    # ── settings ───────────────────────────────────────────────────────────
    def get_setting(self, key: str, default: str = "") -> str:
        row = self.one("SELECT v FROM settings WHERE k=?", (key,))
        return row["v"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        self.x("INSERT INTO settings(k,v) VALUES(?,?) "
               "ON CONFLICT(k) DO UPDATE SET v=excluded.v", (key, str(value)))

    # ── events ─────────────────────────────────────────────────────────────
    def log_event(self, text: str, level: str = "info", user_id: int = 0, bot_id: int = 0) -> None:
        self.x("INSERT INTO events(ts,level,user_id,bot_id,text) VALUES(?,?,?,?,?)",
               (int(time.time()), level, int(user_id), int(bot_id), str(text)[:800]))

    def events(self, limit: int = 12):
        return self.all("SELECT * FROM events ORDER BY id DESC LIMIT ?", (int(limit),))

    # ── stats ──────────────────────────────────────────────────────────────
    def fleet(self) -> dict:
        total_users = int(self.scalar("SELECT COUNT(*) FROM users"))
        total_bots = int(self.scalar("SELECT COUNT(*) FROM bots"))
        running = int(self.scalar("SELECT COUNT(*) FROM bots WHERE status IN ('running','starting')"))
        crashed = int(self.scalar("SELECT COUNT(*) FROM bots WHERE status='crashed'"))
        new_today = int(self.scalar("SELECT COUNT(*) FROM users WHERE created >= ?",
                                    (int(time.time()) - 86400,)))
        return {
            "users": total_users,
            "bots": total_bots,
            "running": running,
            "crashed": crashed,
            "new_today": new_today,
        }
