"""
NIK HOSTER v1 — hosting engine.

Design goals (why ye tez hai):
  • Popen turant, buffered nahi (-u) -> pehla log line ~1s me
  • output memory ring buffer me -> "logs" button 0ms, file I/O nahi
  • watchdog single thread, 3s tick -> crash 3s ke andar pakda jaata hai
  • missing module detect -> background pip install -> auto restart
  • WAL sqlite -> panel kabhi block nahi hota
  • per-bot process group -> stop karte hi poora tree clean
"""
from __future__ import annotations

import os
import re
import shutil
import signal
import subprocess
import sys
import threading
import time
import zipfile
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

from . import templates

try:  # optional — RAM/CPU dikhane ke liye
    import psutil  # type: ignore
except Exception:  # pragma: no cover
    psutil = None


# missing module -> sahi pip package
PIP_MAP = {
    "telebot": "pyTelegramBotAPI",
    "telegram": "python-telegram-bot",
    "PIL": "Pillow",
    "cv2": "opencv-python",
    "yaml": "PyYAML",
    "dotenv": "python-dotenv",
    "bs4": "beautifulsoup4",
    "Crypto": "pycryptodome",
    "dateutil": "python-dateutil",
    "discord": "discord.py",
    "nacl": "PyNaCl",
    "google": "protobuf",
    "aiohttp": "aiohttp",
    "requests": "requests",
    "psutil": "psutil",
    "pytz": "pytz",
    "redis": "redis",
    "motor": "motor",
    "pymongo": "pymongo",
    "sqlalchemy": "SQLAlchemy",
    "flask": "Flask",
    "fastapi": "fastapi",
    "uvicorn": "uvicorn",
    "openai": "openai",
    "httpx": "httpx",
    "orjson": "orjson",
}

BAD_NAME = re.compile(r"[^A-Za-z0-9._-]+")
MODULE_RE = re.compile(r"No module named '([^']+)'")
IMPORT_RE = re.compile(r"cannot import name '([^']+)' from '([^']+)'")


@dataclass
class Handle:
    bot_id: int
    user_id: int
    name: str
    kind: str
    path: Path
    workdir: Path
    log_path: Path
    proc: subprocess.Popen | None = None
    status: str = "stopped"
    started_at: float = 0.0
    restarts: int = 0
    expected: bool = False
    exit_code: int | None = None
    last_error: str = ""
    ring: deque = field(default_factory=lambda: deque(maxlen=500))
    saw_output: bool = False
    notice_at: float = 0.0
    ephemeral_note: str = ""
    cpu: float = 0.0
    ram_mb: float = 0.0


class Engine:
    def __init__(self, db, notify: Callable[[int, str], None] | None = None, *,
                 python_bin: str | None = None, users_dir: Path | str | None = None,
                 logs_dir: Path | str | None = None, max_restarts: int = 5,
                 backoff: float = 4.0, watchdog: float = 3.0, stop_grace: float = 5.0,
                 autofix: bool = True, log_cap_mb: int = 8, ring: int = 500,
                 env_inject: dict | None = None):
        self.db = db
        self.notify = notify or (lambda uid, text: None)
        self.python_bin = python_bin or sys.executable
        self.users_dir = Path(users_dir or "data/users")
        self.logs_dir = Path(logs_dir or "data/logs")
        self.max_restarts = max_restarts
        self.backoff = backoff
        self.watchdog_interval = watchdog
        self.stop_grace = stop_grace
        self.autofix = autofix
        self.log_cap = log_cap_mb * 1024 * 1024
        self.ring_size = ring
        self.env_inject = env_inject or {}
        self._handles: dict[int, Handle] = {}
        self._lock = threading.RLock()
        self._stop_flag = threading.Event()
        self._watch_thread: threading.Thread | None = None
        self._pip_locks: dict[str, threading.Lock] = {}
        self.boot_ts = time.time()
        self.users_dir.mkdir(parents=True, exist_ok=True)
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        if psutil:
            try:
                psutil.cpu_percent(None)
            except Exception:
                pass

    # ── helpers ────────────────────────────────────────────────────────────
    @staticmethod
    def safe_name(raw: str, fallback: str = "bot") -> str:
        name = BAD_NAME.sub("-", (raw or "").strip()).strip("-._")
        return (name or fallback)[:24]

    def user_dir(self, user_id: int) -> Path:
        path = self.users_dir / str(int(user_id))
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _unique_dir(self, parent: Path, name: str) -> Path:
        target = parent / name
        n = 2
        while target.exists():
            target = parent / f"{name}-{n}"
            n += 1
        target.mkdir(parents=True)
        return target

    def _log_path(self, bot_id: int) -> Path:
        return self.logs_dir / f"bot_{int(bot_id)}.log"

    # ── deploy ─────────────────────────────────────────────────────────────
    def save_upload(self, user_id: int, filename: str, data: bytes) -> dict:
        """Upload ko disk pe rakho aur metadata lauta do (db me abhi nahi)."""
        filename = os.path.basename(filename or "script.py")
        stem = Path(filename).stem
        base = self.safe_name(stem, "script")
        root = self.user_dir(user_id)

        if filename.lower().endswith(".zip"):
            workdir = self._unique_dir(root, base)
            archive = workdir / "_upload.zip"
            archive.write_bytes(data)
            with zipfile.ZipFile(archive) as zf:
                for member in zf.infolist():
                    if member.is_dir():
                        continue
                    target = (workdir / member.filename).resolve()
                    if not str(target).startswith(str(workdir.resolve())):
                        continue  # zip-slip guard
                    target.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(member) as src, open(target, "wb") as dst:
                        shutil.copyfileobj(src, dst)
            archive.unlink(missing_ok=True)
            candidates = sorted(workdir.rglob("*.py"),
                                key=lambda p: (len(p.parts), -p.stat().st_size))
            if not candidates:
                raise ValueError("zip me koi .py file nahi mili")
            entry = candidates[0]
            return {
                "name": self.safe_name(entry.stem, base),
                "kind": "py",
                "path": entry,
                "workdir": workdir,
            }

        kind = "js" if filename.lower().endswith(".js") else "py"
        workdir = self._unique_dir(root, base)
        target = workdir / f"{base}.{kind}"
        target.write_bytes(data)
        return {"name": base, "kind": kind, "path": target, "workdir": workdir}

    def register(self, user_id: int, meta: dict, autostart: int = 1) -> int:
        bot_id = self.db.add_bot(
            user_id, meta["name"], meta["kind"], str(meta["path"]),
            str(meta["workdir"]), autostart=autostart,
        )
        self.db.log_event(f"deploy · {meta['name']} ({meta['kind']})", "deploy", user_id, bot_id)
        return bot_id

    def deploy_upload(self, user_id: int, filename: str, data: bytes,
                      autostart: bool = True) -> int:
        meta = self.save_upload(user_id, filename, data)
        return self.register(user_id, meta, autostart=1 if autostart else 0)

    def deploy_session(self, user_id: int, label: str, api_id: int, api_hash: str,
                       session: str, prefix: str = ".", sudo: list[int] | None = None,
                       autostart: bool = True) -> int:
        name = self.safe_name(label or "account", "account")
        workdir = self._unique_dir(self.user_dir(user_id), name)
        runner = workdir / "runner.py"
        runner.write_text(templates.SESSION_RUNNER, encoding="utf-8")

        bot_id = self.db.add_bot(user_id, self.safe_name(f"{name}", name), "session",
                                 str(runner), str(workdir),
                                 autostart=1 if autostart else 0)
        self.db.set_env(bot_id, "NK_API_ID", str(int(api_id)))
        self.db.set_env(bot_id, "NK_API_HASH", str(api_hash))
        self.db.set_env(bot_id, "NK_SESSION", str(session))
        self.db.set_env(bot_id, "NK_PREFIX", prefix or ".")
        if sudo:
            self.db.set_env(bot_id, "NK_SUDO", ",".join(str(s) for s in sudo))
        self.db.log_event(f"deploy · session {name}", "deploy", user_id, bot_id)
        return bot_id

    # ── process control ────────────────────────────────────────────────────
    def _handle_for(self, row) -> Handle:
        h = self._handles.get(row["id"])
        if h:
            h.name = row["name"]
            h.path = Path(row["path"])
            h.workdir = Path(row["workdir"])
            return h
        h = Handle(
            bot_id=row["id"], user_id=row["user_id"], name=row["name"],
            kind=row["kind"], path=Path(row["path"]), workdir=Path(row["workdir"]),
            log_path=self._log_path(row["id"]),
            ring=deque(maxlen=self.ring_size),
            restarts=int(row["restarts"] or 0),
            last_error=row["last_error"] or "",
        )
        self._handles[row["id"]] = h
        return h

    def _env_for(self, h: Handle) -> dict:
        env = os.environ.copy()
        env.update(self.env_inject)
        env["NK_BOT_ID"] = str(h.bot_id)
        env["NK_OWNER"] = str(h.user_id)
        try:
            env.update({str(k): str(v) for k, v in self.db.env_of(h.bot_id).items()})
        except Exception:
            pass
        return env

    def start(self, bot_id: int, *, by: int | None = None) -> tuple[bool, str]:
        self.start_watchdog()  # pehla bot uthate hi watchdog bhi zinda
        with self._lock:
            row = self.db.bot(bot_id)
            if not row:
                return False, "bot nahi mila"
            h = self._handle_for(row)
            if h.proc and h.proc.poll() is None:
                return True, "pehle se running hai"

            if not h.path.exists():
                self.db.set_bot_status(bot_id, "crashed", error="script file missing")
                return False, "script file missing — dobara upload karo"

            if h.kind == "js":
                cmd = ["node", str(h.path)]
            else:
                cmd = [self.python_bin, "-u", str(h.path)]

            self._rotate_log(h)
            h.ring.clear()
            h.saw_output = False
            h.expected = True
            h.exit_code = None
            self.db.set_bot_status(bot_id, "starting", started=True)
            h.status = "starting"
            h.started_at = time.time()

            try:
                h.proc = subprocess.Popen(
                    cmd,
                    cwd=str(h.workdir),
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    bufsize=1,
                    env=self._env_for(h),
                    start_new_session=(os.name != "nt"),
                )
            except FileNotFoundError as exc:
                h.status = "crashed"
                self.db.set_bot_status(bot_id, "crashed", error=f"runtime missing: {exc}")
                return False, f"runtime missing: {exc}"
            except Exception as exc:  # pragma: no cover
                h.status = "crashed"
                self.db.set_bot_status(bot_id, "crashed", error=str(exc))
                return False, f"start fail: {exc}"

            h.pid = h.proc.pid  # type: ignore[attr-defined]
            threading.Thread(target=self._reader, args=(h,), daemon=True,
                             name=f"reader-{bot_id}").start()
            self.db.log_event(f"start · {h.name} (pid {h.proc.pid})", "start", h.user_id, bot_id)
            return True, f"started · pid {h.proc.pid}"

    def _rotate_log(self, h: Handle) -> None:
        try:
            if h.log_path.exists() and h.log_path.stat().st_size > self.log_cap:
                os.replace(h.log_path, h.log_path.with_suffix(".log.1"))
        except Exception:
            pass

    def _reader(self, h: Handle) -> None:
        proc = h.proc
        if not proc or not proc.stdout:
            return
        fh = None
        try:
            fh = open(h.log_path, "ab", buffering=0)
        except Exception:
            fh = None
        try:
            for raw in proc.stdout:
                line = raw.rstrip("\n")
                h.ring.append(line)
                if fh is not None:
                    try:
                        fh.write((line + "\n").encode("utf-8", "replace"))
                    except Exception:
                        fh = None
                if not h.saw_output and line.strip():
                    h.saw_output = True
        except Exception:
            pass
        finally:
            if fh is not None:
                try:
                    fh.close()
                except Exception:
                    pass

    def _kill_tree(self, h: Handle) -> None:
        proc = h.proc
        if not proc:
            return
        if proc.poll() is not None:
            return
        try:
            if os.name == "nt":
                subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                               capture_output=True, check=False)
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except Exception:
            try:
                proc.terminate()
            except Exception:
                pass
        try:
            proc.wait(timeout=self.stop_grace)
            return
        except Exception:
            pass
        try:
            if os.name == "nt":
                proc.kill()
            else:
                os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
        except Exception:
            try:
                proc.kill()
            except Exception:
                pass
        try:
            proc.wait(timeout=3)
        except Exception:
            pass

    def stop(self, bot_id: int, *, by: int | None = None) -> tuple[bool, str]:
        with self._lock:
            row = self.db.bot(bot_id)
            if not row:
                return False, "bot nahi mila"
            h = self._handle_for(row)
            h.expected = False
            if not h.proc or h.proc.poll() is not None:
                h.status = "stopped"
                self.db.set_bot_status(bot_id, "stopped")
                return True, "pehle se stopped"
            self._kill_tree(h)
            h.status = "stopped"
            h.exit_code = h.proc.returncode if h.proc else None
            self.db.set_bot_status(bot_id, "stopped", exit_now=True)
            self.db.log_event(f"stop · {h.name}", "stop", h.user_id, bot_id)
            return True, "stopped"

    def stop_fast(self, bot_id: int, *, by: int | None = None) -> tuple[bool, str]:
        """UI ke liye: SIGTERM bhejo, max 0.8s wait. Baaki background me finish."""
        with self._lock:
            row = self.db.bot(bot_id)
            if not row:
                return False, "bot nahi mila"
            h = self._handle_for(row)
            h.expected = False
            proc = h.proc
            if not proc or proc.poll() is not None:
                h.status = "stopped"
                self.db.set_bot_status(bot_id, "stopped")
                return True, "already stopped"
            h.status = "stopping"
            self.db.set_bot_status(bot_id, "stopping")
            try:
                if os.name == "nt":
                    subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                                   capture_output=True, check=False)
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
            except Exception:
                try:
                    proc.terminate()
                except Exception:
                    pass
            try:
                proc.wait(timeout=0.8)
                h.status = "stopped"
                h.exit_code = proc.returncode
                self.db.set_bot_status(bot_id, "stopped", exit_now=True)
                self.db.log_event(f"stop · {h.name}", "stop", h.user_id, bot_id)
                return True, "stopped"
            except Exception:
                self._thread(self._finish_stop, h)
                return True, "stopping…"

    def _finish_stop(self, h: Handle) -> None:
        proc = h.proc
        if not proc:
            return
        try:
            proc.wait(timeout=self.stop_grace)
        except Exception:
            try:
                if os.name == "nt":
                    proc.kill()
                else:
                    os.killpg(os.getpgid(proc.pid), signal.SIGKILL)
            except Exception:
                pass
            try:
                proc.wait(timeout=3)
            except Exception:
                pass
        h.status = "stopped"
        h.exit_code = proc.returncode
        if not h.expected:
            self.db.set_bot_status(h.bot_id, "stopped", exit_now=True)
            self.db.log_event(f"stop · {h.name}", "stop", h.user_id, h.bot_id)

    def restart_fast(self, bot_id: int, *, by: int | None = None) -> tuple[bool, str]:
        ok, msg = self.stop_fast(bot_id)
        if not ok:
            return False, msg

        def _go():
            for _ in range(80):
                if not self.is_running(bot_id):
                    break
                time.sleep(0.1)
            self.db.set_bot_status(bot_id, "stopped", restarts=0)
            self.start(bot_id)

        self._thread(_go)
        return True, "restarting…"

    def restart(self, bot_id: int, *, by: int | None = None) -> tuple[bool, str]:
        self.stop(bot_id)
        time.sleep(0.35)
        row = self.db.bot(bot_id)
        if row:
            self.db.set_bot_status(bot_id, "stopped", restarts=0)
        return self.start(bot_id)

    def send_input(self, bot_id: int, text: str) -> tuple[bool, str]:
        h = self._handles.get(int(bot_id))
        if not h or not h.proc or h.proc.poll() is not None or not h.proc.stdin:
            return False, "process running nahi hai"
        try:
            h.proc.stdin.write(text.rstrip("\n") + "\n")
            h.proc.stdin.flush()
            return True, "bhej diya"
        except Exception as exc:
            return False, f"stdin fail: {exc}"

    def delete(self, bot_id: int) -> tuple[bool, str]:
        self.stop_fast(bot_id)
        time.sleep(0.2)
        row = self.db.bot(bot_id)
        if not row:
            return False, "bot nahi mila"
        h = self._handles.pop(int(bot_id), None)
        if h:
            try:
                h.proc = None
            except Exception:
                pass
        try:
            shutil.rmtree(row["workdir"], ignore_errors=True)
        except Exception:
            pass
        try:
            self._log_path(bot_id).unlink(missing_ok=True)
        except Exception:
            pass
        self.db.delete_bot(bot_id)
        self.db.log_event(f"delete · {row['name']}", "delete", row["user_id"], bot_id)
        return True, "delete ho gaya"

    # ── query ──────────────────────────────────────────────────────────────
    def runtime(self, bot_id: int) -> dict:
        h = self._handles.get(int(bot_id))
        if not h:
            return {"status": "stopped", "pid": None, "uptime": 0, "cpu": 0.0, "ram_mb": 0.0}
        alive = bool(h.proc and h.proc.poll() is None)
        if alive and h.status == "starting" and (h.saw_output or time.time() - h.started_at > 2.5):
            h.status = "running"
            try:
                self.db.set_bot_status(bot_id, "running")
            except Exception:
                pass
        if not alive and h.status in {"running", "starting"}:
            h.status = "crashed"
        if alive:
            self._sample(h)
        return {
            "status": h.status,
            "pid": h.proc.pid if alive and h.proc else None,
            "uptime": (time.time() - h.started_at) if alive else 0,
            "cpu": h.cpu,
            "ram_mb": h.ram_mb,
        }

    def _sample(self, h: Handle) -> None:
        if not psutil or not h.proc:
            return
        try:
            p = psutil.Process(h.proc.pid)
            with p.oneshot():
                h.ram_mb = p.memory_info().rss / (1024 * 1024)
                h.cpu = p.cpu_percent(None)
                for child in p.children(recursive=True):
                    try:
                        h.ram_mb += child.memory_info().rss / (1024 * 1024)
                    except Exception:
                        continue
        except Exception:
            pass

    def logs(self, bot_id: int, lines: int = 22) -> str:
        h = self._handles.get(int(bot_id))
        if h and h.ring:
            return "\n".join(list(h.ring)[-lines:])
        path = self._log_path(bot_id)
        try:
            if not path.exists():
                return ""
            size = path.stat().st_size
            with open(path, "rb") as fh:
                fh.seek(max(0, size - 64 * 1024))
                chunk = fh.read().decode("utf-8", "replace")
            return "\n".join(chunk.strip().splitlines()[-lines:])
        except Exception:
            return ""

    def logs_size(self, bot_id: int) -> int:
        try:
            return self._log_path(bot_id).stat().st_size
        except Exception:
            return 0

    def clear_logs(self, bot_id: int) -> None:
        h = self._handles.get(int(bot_id))
        if h:
            h.ring.clear()
        try:
            self._log_path(bot_id).unlink(missing_ok=True)
        except Exception:
            pass

    def is_running(self, bot_id: int) -> bool:
        h = self._handles.get(int(bot_id))
        return bool(h and h.proc and h.proc.poll() is None)

    def handle(self, bot_id: int) -> Handle | None:
        return self._handles.get(int(bot_id))

    # ── fleet health ───────────────────────────────────────────────────────
    def host_stats(self) -> dict:
        stats = {
            "uptime": time.time() - self.boot_ts,
            "cpu": 0.0, "ram_pct": 0.0, "ram_used": 0, "ram_total": 0,
            "disk_pct": 0.0, "disk_free": 0, "disk_total": 0,
            "load": 0.0, "cores": os.cpu_count() or 1, "engine_procs": 0,
        }
        if psutil:
            try:
                stats["cpu"] = psutil.cpu_percent(None)
                vm = psutil.virtual_memory()
                stats["ram_pct"] = vm.percent
                stats["ram_used"] = vm.used
                stats["ram_total"] = vm.total
                du = psutil.disk_usage(str(self.users_dir))
                stats["disk_pct"] = du.percent
                stats["disk_free"] = du.free
                stats["disk_total"] = du.total
            except Exception:
                pass
        try:
            stats["load"] = os.getloadavg()[0]
        except Exception:
            stats["load"] = 0.0
        stats["engine_procs"] = sum(
            1 for h in self._handles.values() if h.proc and h.proc.poll() is None)
        return stats

    # ── watchdog ───────────────────────────────────────────────────────────
    def start_watchdog(self) -> None:
        if self._watch_thread and self._watch_thread.is_alive():
            return
        self._stop_flag.clear()
        self._watch_thread = threading.Thread(target=self._watch_loop, daemon=True,
                                              name="nk-watchdog")
        self._watch_thread.start()

    def shutdown(self) -> None:
        self._stop_flag.set()
        for bot_id in list(self._handles):
            try:
                self.stop(bot_id)
            except Exception:
                pass

    def _watch_loop(self) -> None:
        while not self._stop_flag.is_set():
            try:
                self._tick()
            except Exception:
                pass
            self._stop_flag.wait(self.watchdog_interval)

    def _tick(self) -> None:
        for bot_id, h in list(self._handles.items()):
            proc = h.proc
            if proc is None:
                continue
            rc = proc.poll()
            if rc is None:
                if h.status == "starting" and (h.saw_output or time.time() - h.started_at > 2.5):
                    h.status = "running"
                    try:
                        self.db.set_bot_status(bot_id, "running")
                    except Exception:
                        pass
                continue
            # process exited
            if h.exit_code != rc:
                h.exit_code = rc
                h.status = "stopped" if not h.expected else "crashed"
                self._on_exit(h, rc)

    def _on_exit(self, h: Handle, rc: int) -> None:
        error = self._detect_error(h)
        h.last_error = error
        row = self.db.bot(h.bot_id)
        if not row:
            return
        autostart = bool(row["autostart"])
        autofix_on = bool(row["autofix"]) and self.autofix

        try:
            self.db.set_bot_status(h.bot_id, h.status, error=error, exit_now=True)
        except Exception:
            pass

        if not h.expected:
            return

        module = self._missing_module(error)
        if module and autofix_on:
            self._thread(self._autofix, h, module)
            return

        # crash → backoff restart (agar autostart on hai)
        if autostart and h.restarts < self.max_restarts:
            h.restarts += 1
            h.status = "queued"
            try:
                self.db.set_bot_status(h.bot_id, "queued", restarts=h.restarts)
            except Exception:
                pass
            self._notify(h, (
                f"♻️ <b>{h.name}</b> crash ho gaya (rc {rc}) — "
                f"restart #{h.restarts}/{self.max_restarts}…"
            ), cooldown=25)
            self._thread(self._delayed_restart, h)
            return

        h.expected = False
        h.status = "crashed"
        try:
            self.db.set_bot_status(h.bot_id, "crashed", error=error, exit_now=True)
        except Exception:
            pass
        self.db.log_event(f"crash · {h.name} rc={rc}", "error", h.user_id, h.bot_id)
        tail = "\n".join(list(h.ring)[-6:]) or "no output"
        self._notify(h, (
            f"🔴 <b>{h.name}</b> band ho gaya <code>(rc {rc})</code>\n"
            f"<blockquote>{self._safe(err_tail(tail))}</blockquote>"
        ), cooldown=0)

    def _delayed_restart(self, h: Handle) -> None:
        delay = min(self.backoff * (2 ** max(0, h.restarts - 1)), 45)
        time.sleep(delay)
        if not h.expected:
            return
        if h.status in {"queued", "crashed"}:
            self.start(h.bot_id)

    def _autofix(self, h: Handle, module: str) -> None:
        lock = self._pip_locks.setdefault(module, threading.Lock())
        with lock:
            pkg = PIP_MAP.get(module, module)
            h.status = "autofixing"
            try:
                self.db.set_bot_status(h.bot_id, "autofixing", error=f"installing {pkg}")
            except Exception:
                pass
            self._notify(h, f"🛠 <b>{h.name}</b> — missing module "
                            f"<code>{self._safe(module)}</code>, install kar raha hoon…",
                         cooldown=0)
            cmd = [self.python_bin, "-m", "pip", "install", "--disable-pip-version-check",
                   "--no-input", pkg]
            ok = False
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
                ok = res.returncode == 0
                for line in (res.stdout or "").splitlines()[-4:]:
                    h.ring.append(f"[pip] {line}")
                if not ok:
                    for line in (res.stderr or "").splitlines()[-4:]:
                        h.ring.append(f"[pip!] {line}")
            except Exception as exc:
                h.ring.append(f"[pip!] {exc}")
            if ok:
                h.ring.append(f"[autofix] {pkg} installed — restarting")
                h.restarts += 1
                time.sleep(0.8)
                h.expected = True
                self.start(h.bot_id)
            else:
                h.expected = False
                h.status = "crashed"
                self.db.set_bot_status(h.bot_id, "crashed",
                                       error=f"pip install failed for {pkg}")
                self._notify(h, f"❌ <b>{h.name}</b> — <code>{self._safe(pkg)}</code> "
                                f"install nahi hua. Manual check karo.", cooldown=0)

    # ── small utils ────────────────────────────────────────────────────────
    def _thread(self, fn, *args) -> None:
        threading.Thread(target=fn, args=args, daemon=True).start()

    def _detect_error(self, h: Handle) -> str:
        for line in reversed(list(h.ring)[-60:]):
            s = line.strip()
            if not s:
                continue
            if ("Error" in s or "Exception" in s or "Traceback" in s
                    or s.startswith("File \"")):
                return s[:300]
        tail = [l for l in list(h.ring)[-15:] if l.strip()]
        return tail[-1][:300] if tail else ""

    @staticmethod
    def _missing_module(error: str) -> str | None:
        m = MODULE_RE.search(error)
        if m:
            return m.group(1).split(".")[0]
        m = IMPORT_RE.search(error)
        if m:
            return m.group(2).split(".")[0]
        return None

    def _notify(self, h: Handle, text: str, cooldown: float = 0) -> None:
        now = time.time()
        if cooldown and now - h.notice_at < cooldown:
            return
        h.notice_at = now
        try:
            self.notify(int(h.user_id), text)
        except Exception:
            pass

    @staticmethod
    def _safe(text: str) -> str:
        return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    # ── boot ───────────────────────────────────────────────────────────────
    def boot(self) -> int:
        """Autostart wale bots wapas uthao. Returns count."""
        if not self._restore_autostart:
            return 0
        started = 0
        banned_cache: dict[int, bool] = {}
        for row in self.db.all_bots():
            if not row["autostart"]:
                continue
            owner = int(row["user_id"])
            if owner not in banned_cache:
                user = self.db.user(owner)
                banned_cache[owner] = bool(user and user["banned"])
            if banned_cache[owner]:
                continue
            if row["status"] in {"running", "starting"}:
                continue
            if not Path(row["path"]).exists():
                self.db.set_bot_status(row["id"], "crashed", error="script file missing")
                continue
            ok, _ = self.start(row["id"])
            started += 1 if ok else 0
        self.start_watchdog()
        return started

    _restore_autostart = True

    def disable_autostart(self) -> None:
        self._restore_autostart = False


def err_tail(text: str) -> str:
    lines = [l for l in str(text).splitlines() if l.strip()]
    return "\n".join(lines[-4:])[-420:]
