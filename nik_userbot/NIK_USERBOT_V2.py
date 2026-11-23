#!/usr/bin/env python3
# ═══════════════════════════════════════════════════════════════════════════
#
#   ⚡  ɴɪᴋ  ᴜꜱᴇʀʙᴏᴛ   ᴠ2   ·   multi-session userbot
#
#   • ek hi process me teri saari IDs chalti hain (fleet)
#   • owner (5076760701) sabko yahin se manage karta hai — .sessions .add .kill
#   • menu me hosted account ka naam + ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Nikkkwa
#   • custom emoji (premium bhi) har section ke liye
#   • har feature ka apna delay — .delay fyt 8
#   • fyt mode: gali wale roast, rate-limited (account safe)
#   • crash / disconnect / floodwait pe khud sambhalta hai — hosting nahi rukti
#
#   Run:      python NIK_USERBOT_V2.py
#   Self test:python NIK_USERBOT_V2.py --selftest
#
#   Requirements: telethon   (pip install telethon)
# ═══════════════════════════════════════════════════════════════════════════
from __future__ import annotations

import asyncio
import json
import logging
import os
import random
import re
import signal
import sys
import threading
import time
import traceback
from dataclasses import dataclass, field
from pathlib import Path

try:
    from telethon import TelegramClient, events
    from telethon.errors import (
        AuthKeyDuplicatedError,
        AuthKeyUnregisteredError,
        ChatAdminRequiredError,
        FloodWaitError,
        MessageDeleteForbiddenError,
        PeerIdInvalidError,
        SessionPasswordNeededError,
        SessionRevokedError,
        UserAdminInvalidError,
        UsernameInvalidError,
        UsernameNotOccupiedError,
    )
    from telethon.sessions import StringSession
    from telethon.tl import types as tl
except ModuleNotFoundError as exc:  # pragma: no cover
    print(f"❌ missing dependency: {exc.name}\n   pip install telethon")
    raise SystemExit(1)


# ═══════════════════════════════════════════════════════════════════════════
#  CONFIG  (env > yahan likha hua)
#  Hoster se deploy kar rahe ho? NK_API_ID / NK_API_HASH / NK_SESSION env
#  already set hote hain — kuch edit karne ki zaroorat nahi.
# ═══════════════════════════════════════════════════════════════════════════
OWNER_ID = int(os.getenv("NK_OWNER") or 5076760701)
PREFIX = (os.getenv("NK_PREFIX") or ".").strip()[:2] or "."
POWERED_BY = os.getenv("NK_POWERED_BY") or "@Nikkkwa"
BRAND = os.getenv("NK_BRAND") or "ɴɪᴋ ᴜꜱᴇʀʙᴏᴛ"
VERSION = "v2"

# single-account fallback (jab fleet file nahi hai)
API_ID = int(os.getenv("NK_API_ID") or 0)
API_HASH = os.getenv("NK_API_HASH") or ""
SESSION = os.getenv("NK_SESSION") or ""
ACCOUNT_NAME = os.getenv("NK_NAME") or "main"

BASE_DIR = Path(__file__).resolve().parent
STATE_FILE = Path(os.getenv("NK_STATE") or BASE_DIR / "nikstate.json")
SESSIONS_FILE = Path(os.getenv("NK_SESSIONS_FILE") or BASE_DIR / "sessions.json")

LOG = logging.getLogger("nik")


def setup_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)-5s %(message)s",
        datefmt="%H:%M:%S",
        stream=sys.stdout,
    )
    logging.getLogger("telethon").setLevel(logging.WARNING)


# ═══════════════════════════════════════════════════════════════════════════
#  SMALL HELPERS
# ═══════════════════════════════════════════════════════════════════════════
SMALL = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ",
    "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
    "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ",
    "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
}
LINE = "─" * 18


def sc(text: str) -> str:
    return "".join(SMALL.get(ch.lower(), ch) if ch.isalpha() else ch for ch in str(text))


def human_dur(seconds: float) -> str:
    seconds = max(0, int(seconds))
    d, r = divmod(seconds, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def parse_wait(text: str) -> int | None:
    """'10m' / '2h' / '30s' / '90' → seconds"""
    text = (text or "").strip().lower()
    if not text:
        return None
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}.get(text[-1], 1)
    num = text[:-1] if text[-1] in "smhd" else text
    try:
        return int(float(num) * mult)
    except ValueError:
        return None


def u16len(text: str) -> int:
    """Telegram entity offsets UTF-16 units me hote hain."""
    return len(text.encode("utf-16-le")) // 2


def esc(text: str) -> str:
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


# ═══════════════════════════════════════════════════════════════════════════
#  RICH TEXT  —  premium custom emoji + bold/code/mono, ek hi message me
# ═══════════════════════════════════════════════════════════════════════════
class Rich:
    """Text + formatting entities. Offsets khud manage karta hai (UTF-16)."""

    __slots__ = ("text", "entities")

    def __init__(self) -> None:
        self.text = ""
        self.entities: list = []

    def add(self, text: str, *, b=False, i=False, code=False, pre=False, strike=False,
            underline=False, spoiler=False, quote=False, emoji_id=None, url=None,
            lang: str = "") -> "Rich":
        if not text:
            return self
        off, ln = u16len(self.text), u16len(text)
        self.text += text
        if ln == 0:
            return self
        if emoji_id:
            self.entities.append(tl.MessageEntityCustomEmoji(off, ln, document_id=emoji_id))
        if url:
            self.entities.append(tl.MessageEntityTextUrl(off, ln, url=url))
        if code:
            self.entities.append(tl.MessageEntityCode(off, ln))
        elif pre:
            self.entities.append(tl.MessageEntityPre(off, ln, language=lang))
        if b:
            self.entities.append(tl.MessageEntityBold(off, ln))
        if i:
            self.entities.append(tl.MessageEntityItalic(off, ln))
        if strike:
            self.entities.append(tl.MessageEntityStrike(off, ln))
        if underline:
            self.entities.append(tl.MessageEntityUnderline(off, ln))
        if spoiler:
            self.entities.append(tl.MessageEntitySpoiler(off, ln))
        if quote:
            self.entities.append(tl.MessageEntityBlockquote(off, ln))
        return self

    def nl(self, n: int = 1) -> "Rich":
        self.text += "\n" * n
        return self

    def line(self) -> "Rich":
        return self.add(LINE).nl()

    def __len__(self) -> int:
        return len(self.text)

    def __str__(self) -> str:
        return self.text


# ═══════════════════════════════════════════════════════════════════════════
#  STATE  —  ek json file, atomic save, thread-safe
# ═══════════════════════════════════════════════════════════════════════════
SECTION_ORDER = ["main", "fleet", "fun", "group", "protect", "util", "config"]

SECTIONS = {
    "main": {"icon": "⚡", "title": "ᴄᴏʀᴇ"},
    "fleet": {"icon": "🛰", "title": "ꜰʟᴇᴇᴛ"},
    "fun": {"icon": "🔥", "title": "ꜰʏᴛ · ꜰᴜɴ"},
    "group": {"icon": "🛡", "title": "ɢʀᴏᴜᴘ"},
    "protect": {"icon": "🧿", "title": "ᴘʀᴏᴛᴇᴄᴛ"},
    "util": {"icon": "🧰", "title": "ᴜᴛɪʟꜱ"},
    "config": {"icon": "🎛", "title": "ᴄᴏɴꜰɪɢ"},
}

# delay keys → (min, max, default) seconds
DELAY_SPECS = {
    "fyt": (3, 300, 8),        # ek chat me do roast ke beech
    "roast": (2, 300, 4),      # manual .roast ke beech
    "purge": (0.2, 5, 0.35),   # purge batch ke beech
    "afk": (5, 3600, 30),      # ek banda ko dobara jawab
    "flood": (1, 120, 3),      # antiflood window (sec)
    "notify": (0, 900, 20),    # owner ko notifications
    "reconnect": (3, 600, 5),  # reconnect ka pehla wait
}

DEFAULTS: dict = {
    "prefix": PREFIX,
    "emoji": {},                 # key -> custom emoji document id
    "emoji_char": {},            # key -> fallback char
    "delays": {k: v[2] for k, v in DELAY_SPECS.items()},
    "sudo": [],                  # extra user ids
    "notes": {},                 # name -> text
    "chats": {},                 # "chat_id" -> {"fyt":bool,"antidel":bool,"flood":[n,sec]}
    "fyt_global": False,
    "afk": {"on": False, "reason": "", "since": 0},
    "stats": {"commands": 0, "roasts": 0, "deleted": 0, "floods": 0, "since": 0},
}


class State:
    def __init__(self, path: Path) -> None:
        self.path = Path(path)
        self._lock = threading.RLock()
        self.dirty = False
        self.d = json.loads(json.dumps(DEFAULTS))
        self._load()

    # ── io ────────────────────────────────────────────────────────────────
    def _load(self) -> None:
        try:
            if self.path.is_file():
                raw = json.loads(self.path.read_text(encoding="utf-8") or "{}")
                self.d = self._merge(self.d, raw)
        except Exception as exc:
            LOG.warning("state load fail: %s", exc)
        self.d["stats"].setdefault("since", int(time.time()))

    @staticmethod
    def _merge(base: dict, extra: dict) -> dict:
        out = dict(base)
        for k, v in (extra or {}).items():
            if isinstance(v, dict) and isinstance(out.get(k), dict):
                out[k] = State._merge(out[k], v)
            else:
                out[k] = v
        return out

    def save(self) -> None:
        with self._lock:
            try:
                self.path.parent.mkdir(parents=True, exist_ok=True)
                tmp = self.path.with_suffix(".tmp")
                tmp.write_text(json.dumps(self.d, ensure_ascii=False, indent=1),
                               encoding="utf-8")
                os.replace(tmp, self.path)
                self.dirty = False
            except Exception as exc:
                LOG.warning("state save fail: %s", exc)

    # ── access ────────────────────────────────────────────────────────────
    @property
    def prefix(self) -> str:
        return self.d.get("prefix") or "."

    @property
    def sudo(self) -> set[int]:
        return {int(x) for x in self.d.get("sudo", [])}

    def delay(self, key: str) -> float:
        lo, hi, default = DELAY_SPECS.get(key, (0, 3600, 0))
        try:
            val = float(self.d["delays"].get(key, default))
        except (TypeError, ValueError):
            val = default
        return max(lo, min(hi, val))

    def set_delay(self, key: str, value: float) -> tuple[float, str]:
        lo, hi, _ = DELAY_SPECS[key]
        clamped = max(lo, min(hi, float(value)))
        self.d["delays"][key] = clamped
        self.save()
        note = "" if clamped == float(value) else f" (limit {lo}–{hi}s)"
        return clamped, note

    def chat(self, chat_id: int) -> dict:
        key = str(int(chat_id))
        cfg = self.d["chats"].setdefault(key, {})
        cfg.setdefault("fyt", False)
        cfg.setdefault("antidel", False)
        cfg.setdefault("flood", [0, self.delay("flood")])
        return cfg

    def stat(self, key: str, n: int = 1) -> None:
        """Sirf memory — disk flush heartbeat karta hai (speed)."""
        self.d["stats"][key] = int(self.d["stats"].get(key, 0)) + n
        self.dirty = True


# ═══════════════════════════════════════════════════════════════════════════
#  EMOJI  —  har section ka apna emoji, premium custom emoji bhi
# ═══════════════════════════════════════════════════════════════════════════
EMOJI_KEYS = {
    "brand": "⚡",
    **{s: SECTIONS[s]["icon"] for s in SECTION_ORDER},
    "user": "👤",
    "time": "🕐",
    "dot": "•",
    "power": "🩸",
    "on": "🟢",
    "off": "🔴",
    "warn": "⚠️",
}


def emo(state: State, key: str) -> tuple[str, int | None]:
    """(fallback char, custom emoji id)"""
    char = state.d["emoji_char"].get(key) or EMOJI_KEYS.get(key, "•")
    cid = state.d["emoji"].get(key)
    return char, (int(cid) if cid else None)


def put(r: Rich, state: State, key: str) -> Rich:
    char, cid = emo(state, key)
    return r.add(char, emoji_id=cid)


# ═══════════════════════════════════════════════════════════════════════════
#  TEXTS  —  fyt / roast (rate-limited, account safe)
# ═══════════════════════════════════════════════════════════════════════════
ROASTS = [
    "abe {u} tera dimaag wifi se bhi slow hai, bc focus kar 😭",
    "{u} sun, teri baatein sun ke router bhi disconnect ho gaya bc 🤡",
    "o {u}, tu wahi hai na jo google me google search karta tha? 😭😂",
    "{u} bc itna slow hai ki packet loss bhi tujhse maafi maang leta hai 🤣",
    "abe {u} tera gyan 2G speed pe chalta hai, madarchod 4G pe aa ja 😩",
    "{u} teri logic dekh ke calculator ne resign de diya bc 🥲",
    "sun {u}, tu reply karta hai ya dial-up se connect hota hai? 😭",
    "{u} bc tu itna dumb hai ki AI bhi tujhse seekh raha hai galtiyan 🤣",
    "abe {u} teri himmat dekh ke oxygen bhi sorry bol deta hai 😮‍💨",
    "{u} mc tu wahi banda hai jo group me aake bhi offline dikhta hai 😭😂",
    "o {u}, teri baaton ka ping 9999ms aata hai bc 🐌",
    "{u} sun bsdk, tera wifi password bhi tujhse smart hai 🤡",
    "abe {u} tu itna useless hai ki Ctrl+Z bhi tujhe undo kar deta hai 😭",
    "{u} bc teri speed dekh ke snail ne bhi overtake kar liya 🐌💨",
    "sun {u}, tujhe argue karna aata hai ya bas keyboard garam karna? 🥲",
    "abe {u} teri personality stock market se bhi zyada crash hai bc 📉😭",
    "{u} mc itna overthink mat kar, tera dimaag load nahi le paayega 🤯",
    "o {u}, tu wahi hai jo WiFi ke bina bhi disconnect rehta hai 😭",
    "{u} bc tera talent sirf notification ignore karna hai 🤡",
    "abe {u} teri baatein sunke battery bhi 1% pe aa gayi bc 🪫",
    "sun {u}, tu mute pe reh, duniya ka bandwidth bachega 😂",
    "{u} mc tera gyaan Wikipedia pe bhi delete ho gaya 🤣",
    "abe {u} tu screenshot me bhi blur dikhta hai bc 📸😭",
    "{u} teri speed pe chakkar aake clock bhi ruk gaya 🕐😂",
    "o {u}, tu wo banda hai jo group me aake sirf 'hmm' bolta hai 🤡",
    "{u} bc tera dimaag airplane mode pe rehta hai 24x7 ✈️😭",
    "abe {u} itni garmi mat kar, server bhi thak jaata hai bc 🥵",
    "{u} mc teri reply speed dekh ke scroll bhi bore ho gaya 😴",
]

AFK_TEXT = (
    "{e} <b>{name}</b> abhi online nahi hai.\n"
    "╰ <i>{reason}</i>\n"
    "╰ <i>message chhod ja, wapas aake dekhta hai</i>"
)

# ═══════════════════════════════════════════════════════════════════════════
#  RATE LIMITERS  —  account ko flood-ban se bachane ke liye
# ═══════════════════════════════════════════════════════════════════════════
class Gate:
    """Simple 'ek key pe itne sec me ek hi baar' gate."""

    def __init__(self) -> None:
        self._last: dict[str, float] = {}
        self._counts: dict[str, list[float]] = {}

    def ready(self, key: str, gap: float) -> bool:
        now = time.time()
        if now - self._last.get(key, 0) < gap:
            return False
        self._last[key] = now
        return True

    def under(self, key: str, limit: int, window: float) -> bool:
        """window me limit se kam events hue hain?"""
        now = time.time()
        bucket = [t for t in self._counts.get(key, []) if now - t < window]
        if len(bucket) >= limit:
            self._counts[key] = bucket
            return False
        bucket.append(now)
        self._counts[key] = bucket
        return True


GATE = Gate()


# ═══════════════════════════════════════════════════════════════════════════
#  COMMAND REGISTRY
# ═══════════════════════════════════════════════════════════════════════════
@dataclass
class Cmd:
    name: str
    fn: object
    section: str = "main"
    desc: str = ""
    usage: str = ""
    aliases: tuple = ()
    owner_only: bool = False
    group_only: bool = False
    pm_only: bool = False


REGISTRY: dict[str, Cmd] = {}


def command(name: str, *, section: str = "main", desc: str = "", usage: str = "",
            aliases: tuple = (), owner_only: bool = False, group_only: bool = False,
            pm_only: bool = False):
    def deco(fn):
        entry = Cmd(name, fn, section, desc, usage, aliases, owner_only,
                    group_only, pm_only)
        REGISTRY[name] = entry
        for alias in aliases:
            REGISTRY[alias] = entry
        return fn
    return deco


def cmds_for(section: str, owner: bool) -> list[Cmd]:
    seen, out = set(), []
    for entry in REGISTRY.values():
        if entry.name in seen or entry.section != section:
            continue
        seen.add(entry.name)
        if entry.owner_only and not owner:
            continue
        out.append(entry)
    return sorted(out, key=lambda c: c.name)

# ═══════════════════════════════════════════════════════════════════════════
#  FLEET  —  ek process, teri saari IDs
# ═══════════════════════════════════════════════════════════════════════════
@dataclass
class Account:
    name: str
    api_id: int
    api_hash: str
    session: str
    client: TelegramClient | None = None
    status: str = "new"          # new | connecting | online | reconnecting | dead | stopped
    me: object = None
    started_at: float = 0.0
    error: str = ""
    reconnects: int = 0
    stopped: bool = False
    primary: bool = False
    task: asyncio.Task | None = None
    commands: int = 0
    revive_tries: int = 0

    @property
    def display(self) -> str:
        try:
            return self.me.first_name or self.name
        except Exception:
            return self.name

    @property
    def username(self) -> str:
        try:
            return self.me.username or ""
        except Exception:
            return ""


STATUS_DOT = {
    "online": "🟢", "connecting": "🟡", "reconnecting": "🟠",
    "dead": "🔴", "stopped": "⚪️", "new": "🔵", "error": "🔴",
}


class Fleet:
    def __init__(self, state: State) -> None:
        self.state = state
        self.accounts: dict[str, Account] = {}
        self.start_ts = time.time()
        self._lock = asyncio.Lock()

    # ── queries ───────────────────────────────────────────────────────────
    def online(self) -> list[Account]:
        return [a for a in self.accounts.values() if a.status == "online" and a.client]

    @property
    def alive_count(self) -> int:
        return sum(1 for a in self.accounts.values() if a.status == "online")

    def get(self, name: str) -> Account | None:
        if not name:
            return None
        q = name.strip().lstrip("@").lower()
        if q in self.accounts:
            return self.accounts[q]
        for acc in self.accounts.values():
            if acc.name.lower() == q or (acc.username and acc.username.lower() == q):
                return acc
        return None

    def primary(self) -> Account | None:
        for acc in self.accounts.values():
            if acc.primary:
                return acc
        return next(iter(self.accounts.values()), None)

    # ── persistence ───────────────────────────────────────────────────────
    def save_sessions(self) -> None:
        rows = [{"name": a.name, "api_id": a.api_id, "api_hash": a.api_hash,
                 "session": a.session} for a in self.accounts.values()]
        try:
            SESSIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
            tmp = SESSIONS_FILE.with_suffix(".tmp")
            tmp.write_text(json.dumps(rows, indent=1), encoding="utf-8")
            os.chmod(tmp, 0o600)
            os.replace(tmp, SESSIONS_FILE)
        except Exception as exc:
            LOG.warning("sessions save fail: %s", exc)

    @staticmethod
    def load_sessions() -> list[dict]:
        env = os.getenv("NK_SESSIONS", "").strip()
        if env:
            try:
                data = json.loads(env)
                if isinstance(data, list):
                    return data
                if isinstance(data, dict):
                    return [dict(v, name=v.get("name", k)) for k, v in data.items()]
            except Exception:
                LOG.warning("NK_SESSIONS json galat hai — ignore")
        if SESSIONS_FILE.is_file():
            try:
                data = json.loads(SESSIONS_FILE.read_text(encoding="utf-8") or "[]")
                if isinstance(data, list):
                    return data
            except Exception as exc:
                LOG.warning("sessions.json padh nahi paaya: %s", exc)
        if API_ID and API_HASH and SESSION:
            return [{"name": ACCOUNT_NAME, "api_id": API_ID,
                     "api_hash": API_HASH, "session": SESSION}]
        return []

    # ── lifecycle ─────────────────────────────────────────────────────────
    async def boot(self) -> int:
        rows = self.load_sessions()
        if not rows:
            LOG.error("koi session nahi mila — sessions.json banao ya env do")
            return 0
        for i, row in enumerate(rows):
            name = str(row.get("name") or f"acc{i + 1}")
            try:
                acc = Account(
                    name=name,
                    api_id=int(row.get("api_id") or 0),
                    api_hash=str(row.get("api_hash") or ""),
                    session=str(row.get("session") or ""),
                    primary=(i == 0),
                )
            except Exception as exc:
                LOG.warning("%s skip: %s", name, exc)
                continue
            if not (acc.api_id and acc.api_hash and acc.session):
                LOG.warning("%s incomplete (api_id/hash/session) — skip", name)
                continue
            self.accounts[acc.name] = acc
            await self.spawn(acc)
            await asyncio.sleep(0.4)   # ek saath 10 connects = rate limit
        LOG.info("fleet booted: %s accounts", len(self.accounts))
        return len(self.accounts)

    async def spawn(self, acc: Account) -> None:
        if acc.client is None:
            acc.client = TelegramClient(
                StringSession(acc.session), acc.api_id, acc.api_hash,
                device_model="NIK-HOST", system_version="v2",
                app_version="2.0", lang_code="en", system_lang_code="en",
                connection_retries=5, retry_delay=2, auto_reconnect=True,
                request_retries=3, flood_sleep_threshold=120,
                timeout=20,
            )
            attach_handlers(acc, self)
        if acc.task and not acc.task.done():
            return
        acc.stopped = False
        acc.task = asyncio.create_task(self._supervise(acc), name=f"nk-{acc.name}")

    async def _supervise(self, acc: Account) -> None:
        backoff = self.state.delay("reconnect")
        while not acc.stopped:
            try:
                acc.status = "connecting"
                await acc.client.connect()
                if not await acc.client.is_user_authorized():
                    acc.status = "dead"
                    acc.error = "session authorized nahi hai"
                    await self.notify_owner(
                        f"🔴 <b>{esc(acc.name)}</b> — session authorized nahi hai.\n"
                        f"<i>naya session string banao, phir .add karo</i>", key=f"dead:{acc.name}")
                    return

                acc.me = await acc.client.get_me()
                acc.status = "online"
                acc.started_at = time.time()
                acc.error = ""
                backoff = self.state.delay("reconnect")
                LOG.info("🟢 %s online as %s (@%s)", acc.name, acc.display, acc.username)
                await self.notify_owner(
                    f"🟢 <b>{esc(acc.name)}</b> online\n"
                    f"👤 {esc(acc.display)}"
                    + (f" · @{esc(acc.username)}" if acc.username else "")
                    + f"\n🛰 ꜰʟᴇᴇᴛ {self.alive_count}/{len(self.accounts)}",
                    key=f"up:{acc.name}", gap=0)

                await acc.client.run_until_disconnected()
                if acc.stopped:
                    break
                acc.status = "reconnecting"
                acc.error = "disconnected"

            except (AuthKeyUnregisteredError, SessionRevokedError,
                    AuthKeyDuplicatedError, SessionPasswordNeededError) as exc:
                acc.status = "dead"
                acc.error = type(exc).__name__
                LOG.error("⛔ %s dead: %s", acc.name, exc)
                await self.notify_owner(
                    f"⛔ <b>{esc(acc.name)}</b> mar gaya — <code>{esc(acc.error)}</code>\n"
                    f"<i>naya session chahiye, phir .add {esc(acc.name)} …</i>",
                    key=f"dead:{acc.name}", gap=0)
                return
            except asyncio.CancelledError:
                break
            except FloodWaitError as exc:
                wait = int(getattr(exc, "seconds", 30)) + 2
                LOG.warning("floodwait %ss (%s)", wait, acc.name)
                await asyncio.sleep(wait)
                continue
            except Exception as exc:
                acc.status = "error"
                acc.error = f"{type(exc).__name__}: {exc}"[:200]
                LOG.warning("⚠️ %s: %s", acc.name, acc.error)

            if acc.stopped:
                break
            acc.reconnects += 1
            wait = min(backoff * (2 ** min(acc.reconnects, 4)), 300)
            acc.status = "reconnecting"
            LOG.info("♻️ %s reconnect in %ss", acc.name, int(wait))
            try:
                await asyncio.sleep(wait)
            except asyncio.CancelledError:
                break

    async def add(self, name: str, api_id: int, api_hash: str, session: str,
                  *, save: bool = True, start: bool = True) -> tuple[bool, str]:
        name = re.sub(r"[^A-Za-z0-9_-]", "-", (name or "").strip())[:20].lower()
        if not name:
            return False, "naam chahiye"
        if name in self.accounts:
            return False, f"<code>{esc(name)}</code> pehle se hai"
        if not (api_id and api_hash and session):
            return False, "api_id / api_hash / session teeno chahiye"

        acc = Account(name=name, api_id=int(api_id), api_hash=str(api_hash),
                      session=str(session).strip(), primary=not self.accounts)
        # pehle check — galat session save hi na ho
        probe = TelegramClient(StringSession(acc.session), acc.api_id, acc.api_hash,
                               connection_retries=2, retry_delay=1, timeout=15)
        try:
            await probe.connect()
            if not await probe.is_user_authorized():
                return False, "session authorized nahi hai (logout/expired)"
            me = await probe.get_me()
            who = f"{me.first_name or ''}" + (f" @{me.username}" if me.username else "")
        except FloodWaitError as exc:
            return False, f"floodwait {exc.seconds}s — thodi der baad try karo"
        except Exception as exc:
            return False, f"session check fail: {esc(str(exc)[:120])}"
        finally:
            try:
                await probe.disconnect()
            except Exception:
                pass

        self.accounts[name] = acc
        if save:
            self.save_sessions()
        if start:
            await self.spawn(acc)
        return True, f"<code>{esc(name)}</code> add ho gaya — {esc(who)}"

    async def kill(self, name: str) -> tuple[bool, str]:
        acc = self.get(name)
        if not acc:
            return False, "account nahi mila"
        acc.stopped = True
        acc.status = "stopped"
        if acc.task:
            acc.task.cancel()
        try:
            if acc.client:
                await acc.client.disconnect()
        except Exception:
            pass
        return True, f"<code>{esc(acc.name)}</code> band"

    async def revive(self, name: str) -> tuple[bool, str]:
        acc = self.get(name)
        if not acc:
            return False, "account nahi mila"
        acc.stopped = False
        acc.status = "connecting"
        await self.spawn(acc)
        return True, f"<code>{esc(acc.name)}</code> revive"

    async def revive_all(self) -> int:
        n = 0
        for acc in list(self.accounts.values()):
            if acc.status not in {"online", "connecting"}:
                await self.revive(acc.name)
                n += 1
                await asyncio.sleep(0.5)
        return n

    async def remove(self, name: str) -> tuple[bool, str]:
        acc = self.get(name)
        if not acc:
            return False, "account nahi mila"
        await self.kill(acc.name)
        self.accounts.pop(acc.name, None)
        self.save_sessions()
        return True, f"<code>{esc(acc.name)}</code> remove + sessions.json update"

    async def notify_owner(self, text: str, *, key: str = "", gap: float | None = None) -> bool:
        if key:
            gap = self.state.delay("notify") if gap is None else gap
            if gap and not GATE.ready(f"notify:{key}", gap):
                return False
        for acc in self.online():
            try:
                await acc.client.send_message(OWNER_ID, text, parse_mode="html",
                                              link_preview=False)
                return True
            except Exception:
                continue
        for acc in self.online():     # fallback: apne saved messages
            try:
                await acc.client.send_message("me", text, parse_mode="html")
                return True
            except Exception:
                continue
        return False

    async def shutdown(self) -> None:
        LOG.info("shutting down fleet…")
        for acc in list(self.accounts.values()):
            acc.stopped = True
            if acc.task:
                acc.task.cancel()
            try:
                if acc.client:
                    await acc.client.disconnect()
            except Exception:
                pass
        self.state.save()


FLEET: Fleet | None = None


# ═══════════════════════════════════════════════════════════════════════════
#  MENU RENDERING  —  @Nikkkwa branding, hosted account ka naam
# ═══════════════════════════════════════════════════════════════════════════
def _kv(r: Rich, state: State, icon: str, label: str, value: str, *, b=False) -> Rich:
    put(r, state, icon)
    r.add(" ").add(label + " ", i=True).add(value, b=b).nl()
    return r


def render_menu(fleet: Fleet, acc: Account | None, *, owner: bool,
                section: str | None = None, detailed: bool = False) -> Rich:
    state = fleet.state
    r = Rich()

    # ── header ────────────────────────────────────────────────────────────
    put(r, state, "brand")
    r.add(" ").add(sc(BRAND), b=True).add("  ").add(VERSION, i=True).nl()

    if acc is not None and acc.me is not None:
        put(r, state, "user")
        r.add(" ").add(acc.display, b=True)
        if acc.username:
            r.add("  ·  @").add(acc.username)
        r.nl()

    uptime = human_dur(time.time() - (acc.started_at if acc else fleet.start_ts))
    put(r, state, "time")
    r.add(" ").add("ᴜᴘ ", i=True).add(uptime)
    r.add("   ·   ᴘʀᴇꜰɪx ", i=True).add(state.prefix, code=True)
    r.nl()
    r.line()

    # ── body ──────────────────────────────────────────────────────────────
    if section and section in SECTIONS:
        put(r, state, section)
        r.add(" ").add(SECTIONS[section]["title"], b=True).nl()
        for entry in cmds_for(section, owner):
            r.add("  ").add(state.prefix + entry.name, code=True)
            r.add("  ").add(sc(entry.desc or ""), i=True).nl()
            if detailed and entry.usage:
                r.add("      ").add(entry.usage, code=True).nl()
    else:
        for sec in SECTION_ORDER:
            listable = cmds_for(sec, owner)
            if not listable:
                continue
            put(r, state, sec)
            r.add(" ").add(SECTIONS[sec]["title"], b=True).nl()
            for entry in listable[:5]:
                r.add("  ").add(state.prefix + entry.name, code=True)
                r.add("  ").add(sc(entry.desc or ""), i=True).nl()
            if len(listable) > 5:
                r.add("  ").add(f"{state.prefix}help {sec}", code=True)
                r.add("  ").add(f"+{len(listable) - 5} more", i=True).nl()
            r.nl()
        # fleet block
        if len(fleet.accounts) > 1:
            put(r, state, "fleet")
            r.add(" ").add("ꜰʟᴇᴇᴛ ", b=True)
            r.add(f"{fleet.alive_count}/{len(fleet.accounts)} online", i=True).nl()
            for a in list(fleet.accounts.values())[:6]:
                r.add("  ").add(STATUS_DOT.get(a.status, "•") + " ")
                r.add(a.name, code=True)
                if a.me is not None:
                    r.add("  ").add(f"@{a.username}" if a.username else str(a.me.id), i=True)
                r.add("  ").add(human_dur(time.time() - a.started_at) if a.started_at
                                else a.status, i=True).nl()
            r.nl()

    # ── stats line ────────────────────────────────────────────────────────
    if not section:
        st = state.d["stats"]
        r.add("📊 ").add(
            f"cmds {st.get('commands', 0)} · roasts {st.get('roasts', 0)} · "
            f"deleted {st.get('deleted', 0)}", i=True).nl()

    # ── footer ────────────────────────────────────────────────────────────
    r.line()
    put(r, state, "power")
    r.add(" ᴘᴏᴡᴇʀᴇᴅ ʙʏ ", i=True).add(POWERED_BY, b=True)
    r.add("   ·   ").add(f"{state.prefix}help", code=True)
    return r


HELP_TEXT = f"""⚡ <b>ɴɪᴋ ᴜꜱᴇʀʙᴏᴛ ᴠ2</b> — setup

<b>1) single account</b>
<pre>export NK_API_ID=12345
export NK_API_HASH=abcdef…
export NK_SESSION=1BVtsOK…</pre>

<b>2) multiple accounts (fleet)</b>
<pre>sessions.json  →
[{{"name":"main","api_id":1,"api_hash":"…","session":"…"}},
 {{"name":"acc2","api_id":1,"api_hash":"…","session":"…"}}]</pre>

ya runtime pe: <code>{PREFIX}add acc2 12345 hash 1BVtsOK…</code>

<b>owner</b> = {OWNER_ID}   ·   <b>brand</b> = ᴘᴏᴡᴇʀᴇᴅ ʙʏ {POWERED_BY}
"""

# ═══════════════════════════════════════════════════════════════════════════
#  CONTEXT  —  har command ko yahi milta hai
# ═══════════════════════════════════════════════════════════════════════════
@dataclass
class Ctx:
    event: object
    client: TelegramClient
    acc: Account
    fleet: Fleet
    args: str = ""
    argv: list = field(default_factory=list)
    is_owner: bool = False
    sender_id: int = 0
    chat_id: int = 0
    is_group: bool = False
    is_admin: bool = False

    @property
    def state(self) -> State:
        return self.fleet.state

    @property
    def me_id(self) -> int:
        try:
            return int(self.acc.me.id)
        except Exception:
            return 0

    async def send(self, body, *, reply: bool = True, preview: bool = False):
        kw: dict = {"link_preview": preview}
        if reply and self.is_group:
            kw["reply_to"] = self.event.id
        try:
            if isinstance(body, Rich):
                return await self.client.send_message(
                    self.chat_id, body.text, formatting_entities=body.entities, **kw)
            return await self.client.send_message(
                self.chat_id, str(body), parse_mode="html", **kw)
        except FloodWaitError as exc:
            await asyncio.sleep(int(exc.seconds) + 2)
            return await self.send(body, reply=reply, preview=preview)

    async def done(self, text: str):
        return await self.send(f"✅ {text}")

    async def bad(self, text: str):
        return await self.send(f"⚠️ {text}")

    async def target(self):
        """reply > @username > user id"""
        if self.event.reply_to_msg_id:
            msg = await self.event.get_reply_message()
            if msg and msg.sender_id:
                try:
                    return await self.client.get_input_entity(msg.sender_id), int(msg.sender_id)
                except Exception:
                    return None, None
        if not self.argv:
            return None, None
        raw = self.argv[0]
        try:
            ent = await self.client.get_entity(int(raw) if raw.lstrip("-").isdigit() else raw)
            return ent, int(getattr(ent, "id", 0) or 0)
        except (UsernameNotOccupiedError, UsernameInvalidError, ValueError, PeerIdInvalidError):
            return None, None
        except Exception:
            return None, None

    async def rights(self, need: str = "ban_users") -> bool:
        try:
            perms = await self.client.get_permissions(self.chat_id, "me")
            return bool(getattr(perms, need, False)) or bool(getattr(perms, "is_admin", False))
        except ChatAdminRequiredError:
            return False
        except Exception:
            return False

    def span(self, text: str) -> Rich:
        return Rich().add(text)


def is_owner_id(state: State, uid: int) -> bool:
    return uid == OWNER_ID


def is_staff(state: State, uid: int) -> bool:
    return uid == OWNER_ID or uid in state.sudo


# ═══════════════════════════════════════════════════════════════════════════
#  CORE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════
@command("menu", section="main", desc="main menu", aliases=("helpme",), usage=".menu")
@command("help", section="main", desc="section wise help", usage=".help fun")
async def cmd_menu(ctx: Ctx) -> None:
    state = ctx.state
    owner = is_owner_id(state, ctx.sender_id) or ctx.sender_id == ctx.me_id
    section = (ctx.argv[0].lower() if ctx.argv else None)
    detailed = bool(ctx.argv)
    if section in {"all", "full"}:
        section, detailed = None, True
    if section and section not in SECTIONS:
        section = None
    await ctx.send(render_menu(ctx.fleet, ctx.acc, owner=owner,
                               section=section, detailed=detailed))


@command("alive", section="main", desc="status + speed", aliases=("a",), usage=".alive")
async def cmd_alive(ctx: Ctx) -> None:
    state, acc = ctx.state, ctx.acc
    t0 = time.perf_counter()
    msg = await ctx.send("ᴘɪɴɢ…")
    ms = (time.perf_counter() - t0) * 1000
    r = Rich()
    put(r, state, "on")
    r.add(" ").add(sc(BRAND), b=True).add("  ").add(VERSION, i=True).nl()
    r.add("👤 ").add(acc.display, b=True)
    if acc.username:
        r.add(" · @").add(acc.username)
    r.nl()
    r.add("🆔 ").add(str(ctx.me_id), code=True).add("   🌐 ").add(f"{ms:.0f} ms", code=True).nl()
    r.add("🕐 ").add("ᴜᴘ ").add(human_dur(time.time() - acc.started_at)).add("   🔁 ")
    r.add(str(acc.reconnects), code=True).nl()
    r.add("🛰 ").add(f"ꜰʟᴇᴇᴛ {ctx.fleet.alive_count}/{len(ctx.fleet.accounts)}", b=True)
    r.nl().line()
    put(r, state, "power")
    r.add(" ᴘᴏᴡᴇʀᴇᴅ ʙʏ ").add(POWERED_BY, b=True)
    try:
        await msg.edit(r.text, formatting_entities=r.entities)
    except Exception:
        await ctx.send(r)


@command("ping", section="main", desc="latency check", usage=".ping")
async def cmd_ping(ctx: Ctx) -> None:
    t0 = time.perf_counter()
    msg = await ctx.send("🏓")
    ms = (time.perf_counter() - t0) * 1000
    await msg.edit(f"🏓 <b>ᴘᴏɴɢ</b> <code>{ms:.0f} ms</code> · "
                   f"ᴜᴘ <code>{human_dur(time.time() - ctx.acc.started_at)}</code>")


@command("id", section="main", desc="your / chat id", usage=".id")
async def cmd_id(ctx: Ctx) -> None:
    try:
        chat = await ctx.event.get_chat()
        kind = type(chat).__name__.replace("Chat", "").replace("Channel", "Channel") or "User"
    except Exception:
        kind = "?"
    uname = ""
    if ctx.event.sender:
        uname = getattr(ctx.event.sender, "username", "") or ""
    await ctx.send(
        f"🪪 <b>ɪᴅ</b>\n"
        f"├ ᴜꜱᴇʀ <code>{ctx.sender_id}</code>\n"
        f"├ ᴄʜᴀᴛ <code>{ctx.chat_id}</code>\n"
        f"├ ᴛʏᴘᴇ <code>{kind}</code>\n"
        f"└ ᴜꜱᴇʀɴᴀᴍᴇ <code>@{uname or '—'}</code>")


@command("info", section="main", desc="account details", usage=".info")
async def cmd_info(ctx: Ctx) -> None:
    state, acc = ctx.state, ctx.acc
    me = acc.me
    phone = "—"
    try:
        if me.phone_number:
            phone = str(me.phone_number)
            phone = phone[:3] + "•" * max(0, len(phone) - 6) + phone[-3:]
    except Exception:
        pass
    dc = "?"
    try:
        dc = str(ctx.client.session.dc_id)
    except Exception:
        pass
    r = Rich()
    put(r, state, "user")
    r.add(" ").add(acc.name, b=True).add("  ").add(acc.status, i=True).nl()
    r.add("├ ɴᴀᴍᴇ      ").add(acc.display).nl()
    r.add("├ ᴜꜱᴇʀɴᴀᴍᴇ  ").add(f"@{acc.username}" if acc.username else "—").nl()
    r.add("├ ɪᴅ        ").add(str(getattr(me, "id", "—")), code=True).nl()
    r.add("├ ᴘʜᴏɴᴇ     ").add(phone, code=True).nl()
    r.add("├ ᴅᴄ        ").add(dc, code=True).nl()
    r.add("├ ᴘʀᴇꜰɪx    ").add(state.prefix, code=True).nl()
    r.add("├ ꜱᴇꜱꜱɪᴏɴ   ").add(acc.session[:12] + "…", code=True).nl()
    r.add("└ ʀᴇᴄᴏɴɴᴇᴄᴛ ").add(str(acc.reconnects), code=True)
    await ctx.send(r)


@command("stats", section="main", desc="usage counters", usage=".stats")
async def cmd_stats(ctx: Ctx) -> None:
    st = ctx.state.d["stats"]
    since = st.get("since") or int(time.time())
    r = Rich()
    put(r, ctx.state, "main")
    r.add(" ").add("ꜱᴛᴀᴛꜱ", b=True).nl()
    r.add("├ ᴄᴏᴍᴍᴀɴᴅꜱ  ").add(str(st.get("commands", 0)), code=True).nl()
    r.add("├ ʀᴏᴀꜱᴛꜱ    ").add(str(st.get("roasts", 0)), code=True).nl()
    r.add("├ ᴅᴇʟᴇᴛᴇᴅ   ").add(str(st.get("deleted", 0)), code=True).nl()
    r.add("├ ꜰʟᴏᴏᴅꜱ     ").add(str(st.get("floods", 0)), code=True).nl()
    r.add("└ ꜱɪɴᴄᴇ     ").add(human_dur(time.time() - since), code=True)
    await ctx.send(r)


@command("restart", section="main", desc="process restart (owner)", usage=".restart now",
             owner_only=True)
async def cmd_restart(ctx: Ctx) -> None:
    if not ctx.argv or ctx.argv[0].lower() != "now":
        return await ctx.bad(f"confirm: <code>{ctx.state.prefix}restart now</code>")
    await ctx.done("restarting…")
    ctx.state.save()
    await ctx.fleet.shutdown()
    try:
        os.execv(sys.executable, [sys.executable, str(Path(__file__).resolve())] + sys.argv[1:])
    except Exception as exc:
        LOG.error("execv fail: %s", exc)
        os._exit(1)


@command("stop", section="main", desc="shutdown userbot (owner)", usage=".stop now",
         owner_only=True)
async def cmd_stop(ctx: Ctx) -> None:
    if not ctx.argv or ctx.argv[0].lower() != "now":
        return await ctx.bad(f"confirm: <code>{ctx.state.prefix}stop now</code>")
    await ctx.done("band ho raha hoon…")
    ctx.state.save()
    await ctx.fleet.shutdown()
    os._exit(0)


# ═══════════════════════════════════════════════════════════════════════════
#  FLEET COMMANDS  —  saari IDs ek jagah se
# ═══════════════════════════════════════════════════════════════════════════
@command("sessions", section="fleet", desc="all accounts status", aliases=("fleet", "ids"),
         usage=".sessions")
async def cmd_sessions(ctx: Ctx) -> None:
    fleet = ctx.fleet
    r = Rich()
    put(r, ctx.state, "fleet")
    r.add(" ").add("ꜰʟᴇᴇᴛ", b=True).add(f"  {fleet.alive_count}/{len(fleet.accounts)} online", i=True).nl()
    r.line()
    if not fleet.accounts:
        r.add("koi account nahi — ").add(f"{ctx.state.prefix}add", code=True).nl()
    for acc in fleet.accounts.values():
        r.add(STATUS_DOT.get(acc.status, "•") + " ")
        r.add(f"{acc.name:<8}", code=True)
        who = f"@{acc.username}" if acc.username else (
            str(acc.me.id) if acc.me else "—")
        r.add(" ").add(who, b=True).nl()
        info = human_dur(time.time() - acc.started_at) if acc.started_at else acc.status
        extra = f"  ♻️{acc.reconnects}" if acc.reconnects else ""
        r.add("    ").add(info + extra + (f"  ⚠️ {acc.error}" if acc.error else ""), i=True).nl()
    r.line()
    r.add(ctx.state.prefix + "add ", code=True).add("<name> <api_id> <api_hash> [session]", i=True).nl()
    r.add(ctx.state.prefix + "kill ", code=True).add("<name>   ", i=True)
    r.add(ctx.state.prefix + "reviveall", code=True).add("  restore", i=True)
    await ctx.send(r)


@command("add", section="fleet", desc="new account add karo", owner_only=True,
         usage=".add name api_id api_hash 1BVtsOK…  |  reply to session msg + .add name")
async def cmd_add(ctx: Ctx) -> None:
    if not ctx.argv:
        return await ctx.bad(
            f"<code>{ctx.state.prefix}add name api_id api_hash session</code>\n"
            f"ya session message pe reply karke <code>{ctx.state.prefix}add name</code>")

    name = ctx.argv[0]
    rest = ctx.argv[1:]

    if not rest:
        reply = await ctx.event.get_reply_message()
        text = (reply.raw_text or "").strip() if reply else ""
        parts = re.split(r"\s+", text)
        if len(parts) >= 3 and parts[0].isdigit():
            api_id, api_hash, session = parts[0], parts[1], parts[2]
        elif text:
            api_id, api_hash, session = str(API_ID), API_HASH, text
        else:
            return await ctx.bad("session nahi mila")
    elif len(rest) >= 3:
        api_id, api_hash, session = rest[0], rest[1], rest[2]
    else:
        api_id, api_hash, session = str(API_ID), API_HASH, rest[0]

    if not api_id.isdigit() or not api_hash or not session:
        return await ctx.bad("api_id number hona chahiye")

    msg = await ctx.send(f"🛰 <code>{esc(name)}</code> check kar raha hoon…")
    ok, why = await ctx.fleet.add(name, int(api_id), api_hash, session)
    text = f"{'✅' if ok else '❌'} {why}"
    try:
        await msg.edit(text)
    except Exception:
        await ctx.send(text)


@command("kill", section="fleet", desc="account band karo", owner_only=True,
         usage=".kill acc2")
async def cmd_kill(ctx: Ctx) -> None:
    if not ctx.argv:
        return await ctx.bad(f"<code>{ctx.state.prefix}kill acc2</code>")
    ok, why = await ctx.fleet.kill(ctx.argv[0])
    await ctx.send(("✅ " if ok else "❌ ") + why)


@command("revive", section="fleet", desc="account wapas chalao", owner_only=True,
         usage=".revive acc2")
async def cmd_revive(ctx: Ctx) -> None:
    if not ctx.argv:
        return await ctx.bad(f"<code>{ctx.state.prefix}revive acc2</code>")
    ok, why = await ctx.fleet.revive(ctx.argv[0])
    await ctx.send(("✅ " if ok else "❌ ") + why)


@command("reviveall", section="fleet", desc="sab dead accounts uthao", owner_only=True,
         usage=".reviveall")
async def cmd_reviveall(ctx: Ctx) -> None:
    n = await ctx.fleet.revive_all()
    await ctx.done(f"{n} accounts revive kiye")


@command("remove", section="fleet", desc="account hata do (file se bhi)", owner_only=True,
         usage=".remove acc2")
async def cmd_remove(ctx: Ctx) -> None:
    if not ctx.argv:
        return await ctx.bad(f"<code>{ctx.state.prefix}remove acc2</code>")
    if ctx.argv[0].lower() in {ctx.acc.name.lower()}:
        return await ctx.bad("khud ko remove nahi kar sakta")
    ok, why = await ctx.fleet.remove(ctx.argv[0])
    await ctx.send(("✅ " if ok else "❌ ") + why)


# ═══════════════════════════════════════════════════════════════════════════
#  FUN / FYT
# ═══════════════════════════════════════════════════════════════════════════
def _mention(entity_id: int, name: str) -> str:
    return f'<a href="tg://user?id={entity_id}">{esc(name or "user")}</a>'


@command("fyt", section="fun", desc="auto roast on/off (group)", group_only=True,
         usage=".fyt on | .fyt off | .fyt global on")
async def cmd_fyt(ctx: Ctx) -> None:
    state = ctx.state
    arg = (ctx.argv[0].lower() if ctx.argv else "")
    if len(ctx.argv) >= 2 and ctx.argv[0].lower() == "global":
        arg = ctx.argv[1].lower()
        if arg not in {"on", "off"}:
            return await ctx.bad("global on / global off")
        state.d["fyt_global"] = arg == "on"
        state.save()
        return await ctx.done(f"ꜰʏᴛ ɢʟᴏʙᴀʟ {arg}")

    if arg not in {"on", "off"}:
        cfg = state.chat(ctx.chat_id)
        return await ctx.send(
            f"🔥 <b>ꜰʏᴛ</b> — <code>{'on' if cfg['fyt'] else 'off'}</code>\n"
            f"global: <code>{'on' if state.d['fyt_global'] else 'off'}</code>\n"
            f"delay: <code>{state.delay('fyt'):.1f}s</code>\n"
            f"use: <code>{state.prefix}fyt on</code>")

    state.chat(ctx.chat_id)["fyt"] = arg == "on"
    state.save()
    await ctx.done(f"ꜰʏᴛ {arg} — delay <code>{state.delay('fyt'):.0f}s</code>")


@command("roast", section="fun", desc="ek roast maaro", aliases=("gali", "fytx"),
         usage=".roast (reply) | .roast @user")
async def cmd_roast(ctx: Ctx) -> None:
    state = ctx.state
    if not GATE.ready(f"roast:{ctx.chat_id}", state.delay("roast")):
        return await ctx.bad(f"thoda ruk — delay <code>{state.delay('roast'):.0f}s</code>")
    ent, uid = await ctx.target()
    if not uid:
        if ctx.event.reply_to_msg_id:
            return await ctx.bad("kisko? reply karo ya @username do")
        uid = ctx.sender_id
        name = (ctx.event.sender.first_name if ctx.event.sender else "") or "you"
    else:
        name = (getattr(ent, "first_name", "") or getattr(ent, "title", "") or "user")
    if uid in {OWNER_ID, ctx.me_id} or uid in state.sudo:
        return await ctx.bad("apne logon pe gali nahi 😌")
    line = random.choice(ROASTS).format(u=_mention(uid, name))
    await ctx.send(line)
    state.stat("roasts")


@command("rate", section="fun", desc="fyt delay / rate info", usage=".rate")
async def cmd_rate(ctx: Ctx) -> None:
    state = ctx.state
    cfg = state.chat(ctx.chat_id)
    await ctx.send(
        f"🔥 <b>ꜰʏᴛ ʀᴀᴛᴇ</b>\n"
        f"├ chat fyt <code>{'on' if cfg['fyt'] else 'off'}</code>\n"
        f"├ global <code>{'on' if state.d['fyt_global'] else 'off'}</code>\n"
        f"├ roast delay <code>{state.delay('roast'):.1f}s</code>\n"
        f"├ chat delay <code>{state.delay('fyt'):.1f}s</code>\n"
        f"└ roasts sent <code>{state.d['stats'].get('roasts', 0)}</code>\n"
        f"<i>delay badalne ke liye</i> <code>{state.prefix}delay fyt 10</code>")

# ═══════════════════════════════════════════════════════════════════════════
#  GROUP ADMIN
# ═══════════════════════════════════════════════════════════════════════════
def _protected(ctx: Ctx, uid: int) -> bool:
    return uid in {OWNER_ID, ctx.me_id} or uid in ctx.state.sudo


@command("ban", section="group", desc="user ban (reply)", group_only=True, usage=".ban")
async def cmd_ban(ctx: Ctx) -> None:
    if not await ctx.rights("ban_users"):
        return await ctx.bad("mujhe <b>ban users</b> rights nahi hain")
    ent, uid = await ctx.target()
    if not uid:
        return await ctx.bad("reply karo ya @username do")
    if _protected(ctx, uid):
        return await ctx.bad("apne logon ko nahi 😌")
    try:
        await ctx.client.edit_permissions(ctx.chat_id, ent, view_messages=False)
        await ctx.done("ban ho gaya 🚫")
    except UserAdminInvalidError:
        await ctx.bad("wo admin hai, main kuch nahi kar sakta")
    except Exception as exc:
        await ctx.bad(esc(str(exc)[:120]))


@command("unban", section="group", desc="user unban", group_only=True, usage=".unban")
async def cmd_unban(ctx: Ctx) -> None:
    if not await ctx.rights("ban_users"):
        return await ctx.bad("rights nahi hain")
    ent, uid = await ctx.target()
    if not uid:
        return await ctx.bad("reply karo")
    try:
        await ctx.client.edit_permissions(ctx.chat_id, ent, view_messages=True)
        await ctx.done("unban ✅")
    except Exception as exc:
        await ctx.bad(esc(str(exc)[:120]))


@command("kick", section="group", desc="user kick (ban+unban)", group_only=True, usage=".kick")
async def cmd_kick(ctx: Ctx) -> None:
    if not await ctx.rights("ban_users"):
        return await ctx.bad("rights nahi hain")
    ent, uid = await ctx.target()
    if not uid or _protected(ctx, uid):
        return await ctx.bad("target nahi mila / protected")
    try:
        await ctx.client.edit_permissions(ctx.chat_id, ent, view_messages=False)
        await ctx.client.edit_permissions(ctx.chat_id, ent, view_messages=True)
        await ctx.done("kick 👢")
    except Exception as exc:
        await ctx.bad(esc(str(exc)[:120]))


@command("mute", section="group", desc="mute (reply) [10m]", group_only=True,
         usage=".mute | .mute 10m")
async def cmd_mute(ctx: Ctx) -> None:
    if not await ctx.rights("ban_users"):
        return await ctx.bad("rights nahi hain")
    seconds = 0
    if ctx.argv:
        seconds = parse_wait(ctx.argv[0]) or 0
    ent, uid = await ctx.target()
    if not uid or _protected(ctx, uid):
        return await ctx.bad("target nahi mila / protected")
    from datetime import timedelta
    try:
        await ctx.client.edit_permissions(
            ctx.chat_id, ent, send_messages=False,
            until_date=timedelta(seconds=seconds) if seconds else None)
        await ctx.done(f"muted 🤐{' · ' + human_dur(seconds) if seconds else ''}")
    except Exception as exc:
        await ctx.bad(esc(str(exc)[:120]))


@command("unmute", section="group", desc="unmute user", group_only=True, usage=".unmute")
async def cmd_unmute(ctx: Ctx) -> None:
    if not await ctx.rights("ban_users"):
        return await ctx.bad("rights nahi hain")
    ent, uid = await ctx.target()
    if not uid:
        return await ctx.bad("reply karo")
    try:
        await ctx.client.edit_permissions(ctx.chat_id, ent, send_messages=True)
        await ctx.done("unmuted 🔊")
    except Exception as exc:
        await ctx.bad(esc(str(exc)[:120]))


@command("purge", section="group", desc="messages delete (reply/last N)", group_only=True,
         usage=".purge 50")
async def cmd_purge(ctx: Ctx) -> None:
    if not await ctx.rights("delete_messages"):
        return await ctx.bad("delete rights nahi hain")
    state = ctx.state
    limit = 30
    if ctx.argv and ctx.argv[0].isdigit():
        limit = max(1, min(300, int(ctx.argv[0])))
    reply_id = ctx.event.reply_to_msg_id
    ids: list[int] = []
    try:
        async for msg in ctx.client.iter_messages(ctx.chat_id, limit=limit,
                                                  max_id=ctx.event.id):
            if reply_id and msg.id < reply_id:
                break
            ids.append(msg.id)
    except FloodWaitError as exc:
        await asyncio.sleep(int(exc.seconds) + 2)
    if not ids:
        return await ctx.bad("kuch nahi mila")
    deleted = 0
    for i in range(0, len(ids), 50):
        chunk = ids[i:i + 50]
        try:
            await ctx.client.delete_messages(ctx.chat_id, chunk)
            deleted += len(chunk)
        except MessageDeleteForbiddenError:
            await ctx.bad("kuch messages delete nahi ho sakte (purane/admin)")
            break
        except FloodWaitError as exc:
            await asyncio.sleep(int(exc.seconds) + 2)
        await asyncio.sleep(state.delay("purge"))
    state.stat("deleted", deleted)
    await ctx.done(f"{deleted} messages clean 🧹")


@command("pin", section="group", desc="message pin (reply)", group_only=True, usage=".pin")
async def cmd_pin(ctx: Ctx) -> None:
    if not ctx.event.reply_to_msg_id:
        return await ctx.bad("jis message ko pin karna hai uspe reply karo")
    try:
        await ctx.client.pin_message(ctx.chat_id, ctx.event.reply_to_msg_id, notify=True)
        await ctx.done("pinned 📌")
    except Exception as exc:
        await ctx.bad(esc(str(exc)[:120]))


@command("unpin", section="group", desc="pin hatao", group_only=True, usage=".unpin")
async def cmd_unpin(ctx: Ctx) -> None:
    try:
        await ctx.client.unpin_message(ctx.chat_id,
                                       ctx.event.reply_to_msg_id or None)
        await ctx.done("unpinned")
    except Exception as exc:
        await ctx.bad(esc(str(exc)[:120]))


@command("lock", section="group", desc="chat lock (sirf admin bol sakte)", group_only=True,
         usage=".lock")
async def cmd_lock(ctx: Ctx) -> None:
    if not await ctx.rights("change_info"):
        return await ctx.bad("change info rights nahi hain")
    try:
        await ctx.client.edit_permissions(ctx.chat_id, None, send_messages=False)
        await ctx.done("chat locked 🔒")
    except Exception as exc:
        await ctx.bad(esc(str(exc)[:120]))


@command("unlock", section="group", desc="chat unlock", group_only=True, usage=".unlock")
async def cmd_unlock(ctx: Ctx) -> None:
    if not await ctx.rights("change_info"):
        return await ctx.bad("change info rights nahi hain")
    try:
        await ctx.client.edit_permissions(ctx.chat_id, None, send_messages=True)
        await ctx.done("chat unlocked 🔓")
    except Exception as exc:
        await ctx.bad(esc(str(exc)[:120]))


# ═══════════════════════════════════════════════════════════════════════════
#  PROTECTION
# ═══════════════════════════════════════════════════════════════════════════
@command("antidel", section="protect", desc="deleted msg ka mirror", group_only=True,
         usage=".antidel on | off")
async def cmd_antidel(ctx: Ctx) -> None:
    arg = (ctx.argv[0].lower() if ctx.argv else "")
    cfg = ctx.state.chat(ctx.chat_id)
    if arg not in {"on", "off"}:
        return await ctx.send(f"🛡 antidel <code>{'on' if cfg['antidel'] else 'off'}</code>")
    cfg["antidel"] = arg == "on"
    ctx.state.save()
    if arg == "off":
        ANTIDEL_CACHE.pop(str(ctx.chat_id), None)
    await ctx.done(f"antidel {arg}")


@command("antiflood", section="protect", desc="flood guard [n sec]", group_only=True,
         usage=".antiflood on | .antiflood 5 10 | off")
async def cmd_antiflood(ctx: Ctx) -> None:
    state = ctx.state
    cfg = state.chat(ctx.chat_id)
    args = [a.lower() for a in ctx.argv]
    if not args or args[0] in {"on", "off"}:
        if args and args[0] == "off":
            cfg["flood"] = [0, state.delay("flood")]
            state.save()
            return await ctx.done("antiflood off")
        n, sec = cfg.get("flood", [0, 3])
        return await ctx.send(
            f"🧿 <b>antiflood</b> <code>{'on' if n else 'off'}</code>\n"
            f"limit <code>{n or '—'}</code> / <code>{sec}s</code>\n"
            f"use: <code>{state.prefix}antiflood 5 10</code>")
    if len(args) >= 2 and args[0].isdigit() and args[1].isdigit():
        n = max(2, min(30, int(args[0])))
        sec = max(1, min(120, int(args[1])))
        cfg["flood"] = [n, sec]
        state.save()
        return await ctx.done(f"antiflood on · {n} msg / {sec}s")
    await ctx.bad(f"format: <code>{state.prefix}antiflood 5 10</code>")


# ═══════════════════════════════════════════════════════════════════════════
#  UTILS
# ═══════════════════════════════════════════════════════════════════════════
@command("afk", section="util", desc="AFK on (auto reply)", usage=".afk padhai kar raha hoon")
async def cmd_afk(ctx: Ctx) -> None:
    reason = " ".join(ctx.argv).strip() or "abhi busy hoon"
    ctx.state.d["afk"] = {"on": True, "reason": reason[:120], "since": int(time.time())}
    ctx.state.save()
    await ctx.done(f"ᴀꜰᴋ · <i>{esc(reason[:120])}</i>")


@command("unafk", section="util", desc="AFK off", usage=".unafk")
async def cmd_unafk(ctx: Ctx) -> None:
    ctx.state.d["afk"] = {"on": False, "reason": "", "since": 0}
    ctx.state.save()
    await ctx.done("wapas online 🟢")


@command("save", section="util", desc="note save (reply)", usage=".save wifi")
async def cmd_save(ctx: Ctx) -> None:
    if not ctx.argv:
        return await ctx.bad(f"<code>{ctx.state.prefix}save name</code> (message pe reply)")
    name = ctx.argv[0].lower()[:24]
    reply = await ctx.event.get_reply_message()
    text = (reply.raw_text or "").strip() if reply else " ".join(ctx.argv[1:]).strip()
    if not text:
        return await ctx.bad("text nahi mila")
    ctx.state.d["notes"][name] = text[:3500]
    ctx.state.save()
    await ctx.done(f"note <code>{esc(name)}</code> saved")


@command("get", section="util", desc="note nikalo", usage=".get wifi")
async def cmd_get(ctx: Ctx) -> None:
    if not ctx.argv:
        return await ctx.bad(f"<code>{ctx.state.prefix}get name</code>")
    name = ctx.argv[0].lower()
    note = ctx.state.d["notes"].get(name)
    if not note:
        return await ctx.bad("note nahi mila")
    await ctx.send(f"📝 <b>{esc(name)}</b>\n<blockquote>{esc(note)}</blockquote>")


@command("notes", section="util", desc="saare notes", usage=".notes")
async def cmd_notes(ctx: Ctx) -> None:
    notes = ctx.state.d["notes"]
    if not notes:
        return await ctx.bad("koi note nahi")
    lines = [f"📝 <b>ɴᴏᴛᴇꜱ</b> ({len(notes)})", ""]
    for name in sorted(notes):
        lines.append(f"• <code>{esc(name)}</code>")
    lines.append("")
    lines.append(f"<i>{ctx.state.prefix}get &lt;name&gt;</i>")
    await ctx.send("\n".join(lines))


@command("delnote", section="util", desc="note delete", usage=".delnote wifi")
async def cmd_delnote(ctx: Ctx) -> None:
    if not ctx.argv:
        return await ctx.bad("naam do")
    name = ctx.argv[0].lower()
    if ctx.state.d["notes"].pop(name, None) is None:
        return await ctx.bad("note nahi mila")
    ctx.state.save()
    await ctx.done(f"deleted <code>{esc(name)}</code>")


# ═══════════════════════════════════════════════════════════════════════════
#  CONFIG  —  prefix, emoji, delay, sudo
# ═══════════════════════════════════════════════════════════════════════════
@command("prefix", section="config", desc="command prefix badlo", usage=".prefix !")
async def cmd_prefix(ctx: Ctx) -> None:
    if not ctx.argv:
        return await ctx.send(f"prefix <code>{ctx.state.prefix}</code>")
    new = ctx.argv[0].strip()[:2]
    if not new or new.isalnum():
        return await ctx.bad("symbol prefix do, jaise <code>.</code> <code>!</code> <code>/</code>")
    ctx.state.d["prefix"] = new
    ctx.state.save()
    await ctx.done(f"prefix → <code>{esc(new)}</code>")


@command("setemoji", section="config", desc="menu emoji set (premium bhi)", usage=".setemoji fun 🔥")
async def cmd_setemoji(ctx: Ctx) -> None:
    state = ctx.state
    if not ctx.argv:
        keys = ", ".join(EMOJI_KEYS)
        return await ctx.bad(f"<code>{state.prefix}setemoji &lt;key&gt; &lt;emoji&gt;</code>\n"
                             f"keys: <code>{keys}</code>")
    key = ctx.argv[0].lower()
    if key == "reset":
        state.d["emoji"].clear()
        state.d["emoji_char"].clear()
        state.save()
        return await ctx.done("saare emoji default pe reset")

    raw = ctx.event.raw_text or ""
    after = raw.split(key, 1)[1] if key in raw else ""
    lead = len(after) - len(after.lstrip())
    value = after.strip()
    if not value:
        return await ctx.bad("emoji do — jaise <code>.setemoji fun 🔥</code>")

    start_cp = raw.find(key) + len(key) + lead
    off = u16len(raw[:start_cp])
    doc_id = None
    for ent in (ctx.event.message.entities or []):
        if isinstance(ent, tl.MessageEntityCustomEmoji) and ent.offset == off:
            doc_id = ent.document_id
            break

    if doc_id:
        state.d["emoji"][key] = int(doc_id)
        state.d["emoji_char"][key] = value
        state.save()
        return await ctx.done(f"<code>{esc(key)}</code> → premium custom emoji set ✅")
    if len(value) > 6:
        return await ctx.bad("ye emoji nahi lag raha — chhota emoji bhejo")
    state.d["emoji"].pop(key, None)
    state.d["emoji_char"][key] = value
    state.save()
    await ctx.done(f"<code>{esc(key)}</code> → {value}")


@command("emoji", section="config", desc="emoji list", usage=".emoji")
async def cmd_emoji(ctx: Ctx) -> None:
    state = ctx.state
    r = Rich()
    put(r, state, "brand")
    r.add(" ").add("ᴇᴍᴏᴊɪ ꜱᴇᴛ", b=True).nl()
    for key in EMOJI_KEYS:
        char, cid = emo(state, key)
        r.add("├ ").add(f"{key:<6}", code=True).add(" ")
        r.add(char, emoji_id=cid)
        if cid:
            r.add("  ").add("ᴘʀᴇᴍɪᴜᴍ", i=True)
        r.nl()
    r.nl().add(f"{state.prefix}setemoji fun 🔥", code=True).nl()
    r.add(f"{state.prefix}setemoji reset", code=True)
    await ctx.send(r)


@command("delay", section="config", desc="har feature ka delay", usage=".delay fyt 10")
async def cmd_delay(ctx: Ctx) -> None:
    state = ctx.state
    if not ctx.argv:
        r = Rich()
        put(r, state, "config")
        r.add(" ").add("ᴅᴇʟᴀʏ", b=True).nl()
        for key, (lo, hi, default) in DELAY_SPECS.items():
            r.add("├ ").add(f"{key:<9}", code=True)
            r.add(f"{state.delay(key):>6.1f}s").add(f"  ({lo}–{hi})", i=True).nl()
        r.add(f"{state.prefix}delay <key> <sec>", code=True)
        return await ctx.send(r)

    if ctx.argv[0].lower() == "reset":
        state.d["delays"] = {k: v[2] for k, v in DELAY_SPECS.items()}
        state.save()
        return await ctx.done("saare delays default")

    key = ctx.argv[0].lower()
    if key not in DELAY_SPECS:
        return await ctx.bad(f"keys: <code>{', '.join(DELAY_SPECS)}</code>")
    if len(ctx.argv) < 2:
        lo, hi, _ = DELAY_SPECS[key]
        return await ctx.send(f"{key} = <code>{state.delay(key):.1f}s</code> "
                              f"<i>({lo}–{hi})</i>")
    try:
        value = float(ctx.argv[1])
    except ValueError:
        return await ctx.bad("number do, jaise <code>.delay fyt 10</code>")
    clamped, note = state.set_delay(key, value)
    await ctx.done(f"{key} = <code>{clamped:.1f}s</code>{esc(note)}")


@command("sudo", section="config", desc="extra owner ids", usage=".sudo add | del | list")
async def cmd_sudo(ctx: Ctx) -> None:
    state = ctx.state
    action = (ctx.argv[0].lower() if ctx.argv else "list")
    if action == "list":
        ids = sorted(state.sudo)
        body = "\n".join(f"• <code>{i}</code>" for i in ids) or "<i>koi nahi</i>"
        return await ctx.send(f"👑 <b>ꜱᴜᴅᴏ</b>\n"
                              f"owner <code>{OWNER_ID}</code>\n{body}")
    if action == "add":
        uid = None
        if len(ctx.argv) > 1:
            raw = ctx.argv[1].lstrip("@")
            if raw.isdigit():
                uid = int(raw)
            else:
                try:
                    ent = await ctx.client.get_entity(raw)
                    uid = int(ent.id)
                except Exception:
                    uid = None
        if not uid:
            _ent, uid = await ctx.target()
        if not uid:
            return await ctx.bad("reply karo ya id/@username do")
        if not uid or uid == OWNER_ID:
            return await ctx.bad("ye id add nahi hoti")
        state.d["sudo"] = sorted(set(state.d["sudo"]) | {int(uid)})
        state.save()
        return await ctx.done(f"sudo added <code>{uid}</code>")
    if action in {"del", "remove", "rm"}:
        uid = None
        if len(ctx.argv) > 1:
            raw = ctx.argv[1].lstrip("@")
            if raw.isdigit():
                uid = int(raw)
            else:
                try:
                    ent = await ctx.client.get_entity(raw)
                    uid = int(ent.id)
                except Exception:
                    uid = None
        if not uid:
            _ent, uid = await ctx.target()
        if not uid:
            return await ctx.bad("id do ya reply karo")
        state.d["sudo"] = sorted(set(state.d["sudo"]) - {int(uid)})
        state.save()
        return await ctx.done(f"sudo removed <code>{uid}</code>")
    await ctx.bad(f"<code>{state.prefix}sudo add|del|list</code>")

# ═══════════════════════════════════════════════════════════════════════════
#  RUNTIME CACHES
# ═══════════════════════════════════════════════════════════════════════════
ANTIDEL_CACHE: dict[str, dict[int, tuple[int, str]]] = {}
FLOOD: dict[str, list[tuple[float, int]]] = {}
ANTIDEL_CAP = 250


# ═══════════════════════════════════════════════════════════════════════════
#  DISPATCH
# ═══════════════════════════════════════════════════════════════════════════
async def _should_respond(event, acc: Account, text: str) -> bool:
    """Group me multiple accounts na bole — sirf primary / mentioned / reply."""
    if acc.primary or event.out:
        return True
    if acc.username and f"@{acc.username}".lower() in text.lower():
        return True
    if event.reply_to_msg_id:
        try:
            replied = await event.get_reply_message()
            if replied and replied.sender_id == int(acc.me.id):
                return True
        except Exception:
            pass
    return False


async def handle_command(event, acc: Account, fleet: Fleet, text: str) -> None:
    state = fleet.state
    prefix = state.prefix
    raw = text[len(prefix):].strip()
    if not raw:
        return
    parts = raw.split(None, 1)
    name = parts[0].lower()
    args = parts[1].strip() if len(parts) > 1 else ""
    entry = REGISTRY.get(name)
    sender = int(event.sender_id or 0)
    chat_id = int(event.chat_id or 0)
    me_id = int(acc.me.id) if acc.me else 0
    staff = is_staff(state, sender) or sender == me_id

    if entry is None:
        if staff and GATE.ready(f"hint:{chat_id}", 15):
            await acc.client.send_message(
                chat_id,
                f"🤔 <code>{esc(prefix + name)}</code> command nahi hai — "
                f"<code>{prefix}menu</code> dekho",
                parse_mode="html")
        return

    if event.is_group and not await _should_respond(event, acc, text):
        return
    if not staff:
        return                       # chup-chaap ignore (no info leak)
    if entry.owner_only and sender != OWNER_ID:
        if GATE.ready(f"own:{sender}", 10):
            await acc.client.send_message(chat_id, "⛔ <b>owner only</b>", parse_mode="html")
        return
    if entry.group_only and not event.is_group:
        if GATE.ready(f"grp:{chat_id}", 10):
            await acc.client.send_message(chat_id, "ℹ️ ye command group me chalti hai",
                                          parse_mode="html")
        return
    if entry.pm_only and event.is_group:
        return
    if not GATE.under(f"cmd:{sender}", 8, 2.0):
        return

    ctx = Ctx(event=event, client=acc.client, acc=acc, fleet=fleet, args=args,
              argv=args.split(), is_owner=sender == OWNER_ID, sender_id=sender,
              chat_id=chat_id, is_group=bool(event.is_group))
    acc.commands += 1
    state.stat("commands")
    try:
        await entry.fn(ctx)
    except FloodWaitError as exc:
        wait = int(exc.seconds) + 2
        LOG.warning("floodwait %ss (%s)", wait, acc.name)
        await asyncio.sleep(wait)
        if GATE.ready(f"fw:{chat_id}", 20):
            await acc.client.send_message(
                chat_id, f"⏳ floodwait <code>{wait}s</code> — thoda ruk gaya", parse_mode="html")
    except ChatAdminRequiredError:
        await acc.client.send_message(chat_id, "⛔ admin rights chahiye", parse_mode="html")
    except Exception as exc:
        LOG.exception("command %s crash (%s)", name, acc.name)
        if GATE.ready(f"err:{name}", 20):
            await acc.client.send_message(
                chat_id, f"❌ <code>{esc(type(exc).__name__)}</code>: {esc(str(exc)[:150])}",
                parse_mode="html")


async def handle_passive(event, acc: Account, fleet: Fleet) -> None:
    """AFK · fyt roast · antiflood — sab delay ke saath."""
    state = fleet.state
    sender = int(event.sender_id or 0)
    chat_id = int(event.chat_id or 0)
    if not sender or not acc.me:
        return
    if sender == int(acc.me.id) or is_staff(state, sender):
        return
    sender_name = ""
    try:
        sender_name = getattr(event.sender, "first_name", "") or "user"
    except Exception:
        pass

    # ── private: AFK ─────────────────────────────────────────────────────
    if event.is_private:
        afk = state.d.get("afk", {})
        if afk.get("on") and GATE.ready(f"afk:{sender}", state.delay("afk")):
            try:
                await acc.client.send_message(
                    chat_id,
                    f"😴 <b>ᴀꜰᴋ</b>\n"
                    f"╰ <i>{esc(afk.get('reason') or 'abhi online nahi')}</i>\n"
                    f"╰ <i>message chhod ja, wapas aake dekhta hai</i>",
                    parse_mode="html", reply_to=event.id)
            except Exception:
                pass
        return

    if not event.is_group:
        return

    cfg = state.chat(chat_id)

    # ── fyt roast ────────────────────────────────────────────────────────
    if cfg.get("fyt") or state.d.get("fyt_global"):
        if (GATE.ready(f"fyt:{chat_id}", state.delay("fyt"))
                and GATE.under(f"fytm:{chat_id}", 2, 60)):
            await asyncio.sleep(random.uniform(0.6, 1.8))
            line = random.choice(ROASTS).format(u=_mention(sender, sender_name))
            try:
                await acc.client.send_message(chat_id, line, parse_mode="html",
                                              reply_to=event.id, link_preview=False)
                state.stat("roasts")
            except FloodWaitError as exc:
                await asyncio.sleep(int(exc.seconds) + 2)
            except Exception:
                pass

    # ── antiflood ────────────────────────────────────────────────────────
    flood = cfg.get("flood") or [0, 3]
    limit, window = int(flood[0] or 0), float(flood[1] or 3)
    if limit < 2:
        return
    key = f"fl:{chat_id}:{sender}"
    now = time.time()
    bucket = [x for x in FLOOD.get(key, []) if now - x[0] < window]
    bucket.append((now, event.id))
    FLOOD[key] = bucket[-80:]
    if len(bucket) > limit:
        ids = [mid for _, mid in bucket[-limit:]]
        FLOOD[key] = []
        try:
            await acc.client.delete_messages(chat_id, ids)
            state.stat("floods")
        except Exception:
            pass
        if GATE.ready(f"flwarn:{chat_id}:{sender}", 90):
            try:
                await acc.client.send_message(
                    chat_id,
                    f"🧿 <a href=\"tg://user?id={sender}\">{esc(sender_name)}</a> "
                    f"flood kar raha tha — <code>{len(ids)}</code> msg clean",
                    parse_mode="html", link_preview=False)
            except Exception:
                pass


async def handle_deleted(event, acc: Account, fleet: Fleet) -> None:
    state = fleet.state
    pairs: list[tuple] = []
    chats = getattr(event, "chats", None)
    if chats:
        pairs = list(chats.items())
    elif event.chat_id:
        pairs = [(event.chat_id, event.deleted_ids)]
    for chat, ids in pairs:
        if chat is None:
            continue
        try:
            key = str(int(chat))
        except Exception:
            key = str(chat)
        cfg = state.d["chats"].get(key)
        if not cfg or not cfg.get("antidel"):
            continue
        cache = ANTIDEL_CACHE.get(key) or {}
        for mid in ids:
            item = cache.pop(int(mid), None)
            if not item:
                continue
            sender, body = item
            try:
                await acc.client.send_message(
                    chat,
                    f"🛡 <b>ᴀɴᴛɪ-ᴅᴇʟ</b> · "
                    f"<a href=\"tg://user?id={sender}\">deleted</a>\n"
                    f"<blockquote>{esc(body)}</blockquote>",
                    parse_mode="html", link_preview=False)
            except Exception:
                pass


async def dispatch(event, acc: Account, fleet: Fleet) -> None:
    state = fleet.state
    if acc.me is None:
        try:
            acc.me = await acc.client.get_me()
        except Exception:
            return
    text = event.raw_text or ""
    chat_id = int(event.chat_id or 0)
    sender = int(event.sender_id or 0)

    # antidel cache (sirf jahan on hai)
    if not event.out:
        cfg = state.d["chats"].get(str(chat_id))
        if cfg and cfg.get("antidel"):
            cache = ANTIDEL_CACHE.setdefault(str(chat_id), {})
            body = text or ("[media]" if event.media else "[empty]")
            cache[event.id] = (sender, body[:500])
            if len(cache) > ANTIDEL_CAP:
                for k in list(cache)[:60]:
                    cache.pop(k, None)

    if text.startswith(state.prefix) and len(text) > len(state.prefix):
        await handle_command(event, acc, fleet, text)
        return
    if event.out:
        return
    await handle_passive(event, acc, fleet)


def attach_handlers(acc: Account, fleet: Fleet) -> None:
    client = acc.client

    @client.on(events.NewMessage())
    async def _on_new(event):
        try:
            await dispatch(event, acc, fleet)
        except FloodWaitError as exc:
            LOG.warning("floodwait %ss", exc.seconds)
            await asyncio.sleep(int(exc.seconds) + 2)
        except asyncio.CancelledError:
            raise
        except Exception:
            LOG.error("handler crash (%s)\n%s", acc.name, traceback.format_exc())

    @client.on(events.MessageDeleted())
    async def _on_del(event):
        try:
            await handle_deleted(event, acc, fleet)
        except Exception:
            LOG.error("antidel crash (%s)", acc.name)


# ═══════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════
async def async_main() -> int:
    global FLEET
    state = State(STATE_FILE)
    fleet = Fleet(state)
    FLEET = fleet
    n = await fleet.boot()
    if not n:
        LOG.error("koi account online nahi hua — setup dekho")
        print(HELP_TEXT)
        return 2

    await fleet.notify_owner(
        f"⚡ <b>{esc(BRAND)} {VERSION}</b> boot\n"
        f"🛰 ꜰʟᴇᴇᴛ <code>{n}</code> · ᴏᴡɴᴇʀ <code>{OWNER_ID}</code>\n"
        f"<i>{state.prefix}menu se shuru karo</i>",
        key="boot", gap=0)
    LOG.info("⚡ online — %s accounts", n)

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, stop.set)
        except (NotImplementedError, RuntimeError):
            try:
                signal.signal(sig, lambda *_: stop.set())
            except Exception:
                pass

    async def heartbeat() -> None:
        ticks = 0
        while not stop.is_set():
            try:
                await asyncio.wait_for(stop.wait(), timeout=20)
            except asyncio.TimeoutError:
                pass
            ticks += 1
            if state.dirty:
                state.save()                   # dirty state flush (disk pe kam load)
            if ticks % 3 == 0:                 # ~1 min
                LOG.info("💓 online %s/%s · bot %s · cmds %s · roasts %s",
                         fleet.alive_count, len(fleet.accounts),
                         sum(1 for a in fleet.accounts.values() if a.commands),
                         state.d["stats"].get("commands", 0),
                         state.d["stats"].get("roasts", 0))
                for acc in fleet.accounts.values():
                    if acc.status == "dead" and acc.revive_tries < 3:
                        acc.revive_tries += 1
                        LOG.info("revive try %s for %s", acc.revive_tries, acc.name)
                        await fleet.revive(acc.name)

    hb = asyncio.create_task(heartbeat())
    try:
        await stop.wait()
    finally:
        hb.cancel()
        await fleet.shutdown()
    return 0


def main() -> int:
    setup_logging()
    if "--selftest" in sys.argv:
        return selftest()
    LOG.info("⚡ %s %s · owner %s · %s", BRAND, VERSION, OWNER_ID, POWERED_BY)
    try:
        return asyncio.run(async_main())
    except KeyboardInterrupt:
        return 0
    except Exception:
        traceback.print_exc()
        return 1


# ═══════════════════════════════════════════════════════════════════════════
#  SELF TEST  —  bina telegram / internet
# ═══════════════════════════════════════════════════════════════════════════
def selftest() -> int:
    import tempfile

    passed: list[str] = []
    failed: list[str] = []

    def check(name: str, cond: bool, detail: str = "") -> None:
        (passed if cond else failed).append(name)
        print(f"  {'✅' if cond else '❌'} {name}{(' — ' + detail) if detail and not cond else ''}")

    print("⚡ NIK USERBOT v2 · selftest\n")

    # rich text
    r = Rich()
    r.add("hi ").add("🔥", emoji_id=12345).add(" ok", b=True).add("\n").add("x", code=True)
    emoji_ents = [e for e in r.entities if isinstance(e, tl.MessageEntityCustomEmoji)]
    bold_ents = [e for e in r.entities if isinstance(e, tl.MessageEntityBold)]
    check("rich: text", r.text == "hi 🔥 ok\nx", r.text)
    check("rich: custom emoji offset/length",
          bool(emoji_ents) and emoji_ents[0].offset == 3 and emoji_ents[0].length == 2,
          str([(e.offset, e.length) for e in emoji_ents]))
    check("rich: bold offset", bool(bold_ents) and bold_ents[0].offset == 5,
          str([(e.offset, e.length) for e in bold_ents]))
    check("utf-16 length", u16len("🔥") == 2 and u16len("abc") == 3)

    # state
    tmp = Path(tempfile.mkdtemp(prefix="nikub-"))
    st = State(tmp / "s.json")
    check("state: defaults", st.prefix == PREFIX and st.delay("fyt") == 8)
    val, note = st.set_delay("fyt", 0)
    check("state: delay clamp low", val == 3, str(val))
    val, note = st.set_delay("fyt", 9999)
    check("state: delay clamp high", val == 300, str(val))
    st.d["sudo"] = [123]
    st.d["notes"]["wifi"] = "pass"
    st.save()
    st2 = State(tmp / "s.json")
    check("state: reload", st2.sudo == {123} and st2.d["notes"]["wifi"] == "pass")
    check("state: chat cfg default", st2.chat(-100123)["fyt"] is False)

    # registry + menu
    check("registry: commands registered", len({c.name for c in REGISTRY.values()}) >= 25,
          str(len(REGISTRY)))
    bad_sections = [c.name for c in REGISTRY.values() if c.section not in SECTIONS]
    check("registry: sections valid", not bad_sections, str(bad_sections))
    for sec in SECTION_ORDER:
        check(f"section {sec}: commands", bool(cmds_for(sec, owner=True)))

    class FakeMe:
        def __init__(self, i, n, u):
            self.id, self.first_name, self.username = i, n, u
            self.phone_number = "+919999999999"

    fake = Fleet(st2)
    a1 = Account("main", 1, "h", "s", status="online",
                 me=FakeMe(1, "Nik", "nikku"), started_at=time.time() - 800)
    a1.primary = True
    a2 = Account("acc2", 1, "h", "s", status="online",
                 me=FakeMe(2, "Arjun", "arjun_x"), started_at=time.time() - 60)
    fake.accounts = {"main": a1, "acc2": a2}

    menu = render_menu(fake, a1, owner=True)
    check("menu: account name", "Nik" in menu.text, menu.text[:120])
    check("menu: powered by", POWERED_BY in menu.text)
    check("menu: fleet block", "acc2" in menu.text)
    check("menu: length ok", 0 < len(menu.text) <= 4000, str(len(menu.text)))
    for sec in SECTION_ORDER:
        m = render_menu(fake, a1, owner=True, section=sec, detailed=True)
        check(f"menu[{sec}]: length", len(m.text) <= 4000, str(len(m.text)))
    guest = render_menu(fake, a2, owner=False)
    check("menu: non-owner me owner cmds nahi",
          ".restart" not in guest.text and ".stop" not in guest.text)

    # texts
    check("roasts: placeholders", all("{u}" in line for line in ROASTS))
    check("roasts: count", len(ROASTS) >= 20, str(len(ROASTS)))
    check("afk text", "{reason}" in AFK_TEXT)

    # helpers
    check("parse_wait 10m", parse_wait("10m") == 600)
    check("parse_wait 2h", parse_wait("2h") == 7200)
    check("parse_wait junk", parse_wait("abc") is None)
    check("sc()", sc("menu") == "ᴍᴇɴᴜ")

    print(f"\n{'─' * 44}\n  PASS {len(passed)}   FAIL {len(failed)}")
    if failed:
        print("  failed:", ", ".join(failed))
    print("─" * 44)
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
