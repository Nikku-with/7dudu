"""
NIK HOSTER v1 — configuration.

Sab kuch env se aata hai, code me kuch hardcode nahi hai.
Copy `.env.example` -> `.env` (ya host ke dashboard me env vars daal do).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def _load_dotenv() -> None:
    """Chhota .env loader (koi dependency nahi). Repo root + package folder."""
    for candidate in (BASE_DIR / ".env", BASE_DIR.parent / ".env"):
        if not candidate.is_file():
            continue
        try:
            for raw in candidate.read_text(encoding="utf-8").splitlines():
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip().strip('"').strip("'")
                os.environ.setdefault(key, value)
        except Exception:
            pass


_load_dotenv()
DATA_DIR = Path(os.getenv("NK_DATA_DIR") or (BASE_DIR / "data"))
USERS_DIR = DATA_DIR / "users"
LOGS_DIR = DATA_DIR / "logs"
DB_PATH = Path(os.getenv("NK_DB_PATH") or (DATA_DIR / "nikhoster.db"))


def _int(name: str, default: int) -> int:
    raw = os.getenv(name, "")
    try:
        return int(str(raw).strip())
    except (TypeError, ValueError):
        return default


def _bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None or str(raw).strip() == "":
        return default
    return str(raw).strip().lower() in {"1", "true", "yes", "on", "y"}


def _ids(name: str) -> set[int]:
    raw = os.getenv(name, "")
    out: set[int] = set()
    for chunk in raw.replace(";", ",").replace(" ", ",").split(","):
        chunk = chunk.strip()
        if chunk.lstrip("-").isdigit():
            out.add(int(chunk))
    return out


# ── Telegram ────────────────────────────────────────────────────────────────
BOT_TOKEN = (os.getenv("BOT_TOKEN") or os.getenv("NK_BOT_TOKEN") or "").strip()
OWNER_ID = _int("OWNER_ID", 0)
ADMIN_IDS = _ids("ADMIN_IDS")
if OWNER_ID:
    ADMIN_IDS.add(OWNER_ID)

SUPPORT_URL = (os.getenv("SUPPORT_URL") or "https://t.me/nikku").strip()
UPDATES_URL = (os.getenv("UPDATES_URL") or "").strip()

# ── Brand ───────────────────────────────────────────────────────────────────
BRAND = os.getenv("NK_BRAND", "ɴɪᴋ ʜᴏꜱᴛᴇʀ")
VERSION = "v1"
TAGLINE = os.getenv("NK_TAGLINE", "ꜰᴀꜱᴛ · ᴄʟᴇᴀɴ · ɴᴇᴠᴇʀ ꜱʟᴇᴇᴘꜱ")

# ── Engine ──────────────────────────────────────────────────────────────────
PYTHON_BIN = os.getenv("NK_PYTHON") or sys.executable
MAX_RESTARTS = _int("NK_MAX_RESTARTS", 5)          # crash-loop guard
RESTART_BACKOFF = float(os.getenv("NK_RESTART_BACKOFF", "4"))  # seconds, x2 har restart
WATCHDOG_INTERVAL = float(os.getenv("NK_WATCHDOG_INTERVAL", "3"))
STOP_GRACE = float(os.getenv("NK_STOP_GRACE", "5"))
LOG_RING = _int("NK_LOG_RING", 500)               # memory me last N lines
LOG_HARD_CAP_MB = _int("NK_LOG_HARD_CAP_MB", 8)   # log file rotate
ENV_INJECT = {
    "PYTHONUNBUFFERED": "1",
    "PYTHONIOENCODING": "utf-8",
    "PYTHONDONTWRITEBYTECODE": "0",
    "TERM": "xterm-256color",
}
AUTOFIX = _bool("NK_AUTOFIX", True)               # missing module auto-install
AUTOSTART = _bool("NK_AUTOSTART", True)           # boot pe bots wapas uthao

# ── Limits / plans ──────────────────────────────────────────────────────────
MAX_UPLOAD_MB = _int("NK_MAX_UPLOAD_MB", 20)
MAX_LOG_CHARS = _int("NK_MAX_LOG_CHARS", 3300)

PLANS: dict[str, dict] = {
    "free": {
        "label": "ꜰʀᴇᴇ",
        "bots": _int("NK_FREE_BOTS", 1),
        "ram_mb": 512,
        "autofix": True,
        "note": "1 bot · basic engine",
    },
    "pro": {
        "label": "ᴘʀᴏ",
        "bots": _int("NK_PRO_BOTS", 5),
        "ram_mb": 1536,
        "autofix": True,
        "note": "5 bots · live logs · priority",
    },
    "elite": {
        "label": "ᴇʟɪᴛᴇ",
        "bots": _int("NK_ELITE_BOTS", 15),
        "ram_mb": 4096,
        "autofix": True,
        "note": "15 bots · autostart · no limits",
    },
    "owner": {
        "label": "ᴏᴡɴᴇʀ",
        "bots": 999,
        "ram_mb": 99999,
        "autofix": True,
        "note": "unlimited",
    },
}
DEFAULT_PLAN = "free"

# ── Speed / UX ──────────────────────────────────────────────────────────────
CACHE_TTL = float(os.getenv("NK_CACHE_TTL", "2.0"))   # dashboard cache seconds
LIVE_LOG_REFRESH = float(os.getenv("NK_LIVE_REFRESH", "4"))
STATE_TTL = 900                                        # wizard timeout
BROADCAST_SLEEP = float(os.getenv("NK_BROADCAST_SLEEP", "0.06"))


def limits_for(plan: str) -> dict:
    return PLANS.get(plan or DEFAULT_PLAN, PLANS[DEFAULT_PLAN])


def is_admin(user_id: int) -> bool:
    return int(user_id) in ADMIN_IDS
