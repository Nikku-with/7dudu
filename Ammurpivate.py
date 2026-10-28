import logging
try:
    from telethon import TelegramClient, functions, types
    from telethon.sessions import StringSession
    from telethon.errors import FloodWaitError, UserAlreadyParticipantError
    from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest, JoinChannelRequest
    from telethon.tl.functions.chatlists import CheckChatlistInviteRequest, JoinChatlistInviteRequest
    from telethon.tl.functions.messages import ImportChatInviteRequest, EditChatAdminRequest, CheckChatInviteRequest
    from telethon.tl.types import ChatAdminRights
    HAS_TELETHON = True
except ImportError:
    HAS_TELETHON = False

import asyncio
import os
import json
import random
import time
import io
import urllib.request
import urllib.parse
from typing import Set, Dict, List, Any, Optional
from telegram import (
    Update,
    Chat,
    ChatPermissions,
    ReactionTypeEmoji,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.error import RetryAfter, TimedOut, NetworkError, BadRequest, Forbidden
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ChatMemberHandler,
    filters,
    ContextTypes,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.CRITICAL
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.CRITICAL)
logging.getLogger("telegram").setLevel(logging.CRITICAL)
logging.getLogger("http.server").setLevel(logging.CRITICAL)

# ══════════════════════════════════════════════════════════════════
#  90-DAYS BASE UPTIME ENGINE
# ══════════════════════════════════════════════════════════════════
_UPTIME_BASE_OFFSET = 90 * 86400
_BOT_START_TIMESTAMP = time.time() - _UPTIME_BASE_OFFSET

def get_uptime() -> str:
    elapsed = int(time.time() - _BOT_START_TIMESTAMP)
    days = elapsed // 86400
    hours = (elapsed % 86400) // 3600
    minutes = (elapsed % 3600) // 60
    seconds = elapsed % 60
    return f"{days}d {hours}h {minutes}m {seconds}s"

TOKENS_FILE = "tokens.json"
GROUPS_FILE = "groups.json"
SUDO_FILE   = "sudo_users.json"
MEDIA_FILE  = "menu_media.json"
OWNER_ID = 8652812134
_OWNER_IDS_RAW = "7878403531,8825325097"
OWNER_IDS: Set[int] = ({OWNER_ID} if OWNER_ID > 0 else set()) | {
    int(value.strip())
    for value in (_OWNER_IDS_RAW.split(",") if _OWNER_IDS_RAW else ([str(OWNER_ID)] if OWNER_ID > 0 else []))
    if value.strip() and int(value.strip()) > 0
}

def _is_owner(user_id: Optional[int]) -> bool:
    return user_id is not None and user_id in OWNER_IDS

def get_base_tokens() -> List[str]:
    raw = "8861210976:AAEUZ53uz2EoFklcIICWhMD7X6rtJHB1Vbs,8776883981:AAGOz9G1dw4aWHxUZPhCieL-TMdeSNKgj60,8661016916:AAHkRoJMwVq1IKB50x3YiCAZfWmDQlxTtus,8944869106:AAFV2bPabdkUAMagX_HXrYF5mX-zUwuWXPI,8963493316:AAGjCArE1ShopOo7EfCVDb7Ox03JzuqPkvg"
    if not raw:
        return []
    tokens = [t.strip() for t in raw.replace("\n", ",").split(",") if t.strip()]
    for i in range(1, 11):
        ov = os.environ.get(f"BOT_TOKEN_{i}", "").strip()
        if ov:
            if i <= len(tokens):
                tokens[i-1] = ov
            else:
                tokens.append(ov)
    return tokens

# ══════════════════════════════════════════════════════════════════
#  📁 ZERO-TOUCH FOLDER JOINER CREDENTIALS
#  (Agar aap bina touch kiye saare bots 25 groups me add karwana chahte hain)
# ══════════════════════════════════════════════════════════════════
# ══════════════════════════════════════════════════════════════════
#  ⚡ USERBOT & MULTI-ACCOUNT ROTATION (ANTI-FLOOD-WAIT) CONFIG
#  (Direct yahan fill kar sakte hain ya Environment Variables se)
# ══════════════════════════════════════════════════════════════════
USERBOT_API_ID    = int(os.environ.get("30158957") or os.environ.get("TELEGRAM_API_ID") or "0")
USERBOT_API_HASH  = os.environ.get("143ac7b1111331422c3bfe88213995e1") or os.environ.get("TELEGRAM_API_HASH") or ""
USERBOT_SESSION   = os.environ.get("USERBOT_SESSION") or os.environ.get("STRING_SESSION") or ""
USERBOT_SESSIONS_RAW = os.environ.get("USERBOT_SESSIONS", "")
USERBOT_SESSIONS_LIST: List[str] = [
    s.strip() for s in (USERBOT_SESSIONS_RAW.split(",") if USERBOT_SESSIONS_RAW else ([USERBOT_SESSION] if USERBOT_SESSION else []))
    if s.strip()
]

def load_groups() -> Set[int]:
    try:
        if os.path.exists(GROUPS_FILE):
            with open(GROUPS_FILE, "r") as f:
                return set(json.load(f))
    except Exception:
        pass
    return set()

def save_groups(groups: Set[int]):
    try:
        with open(GROUPS_FILE, "w") as f:
            json.dump(list(groups), f)
    except Exception:
        pass

def load_sudo() -> Set[int]:
    try:
        if os.path.exists(SUDO_FILE):
            with open(SUDO_FILE, "r") as f:
                return set(int(x) for x in json.load(f))
    except Exception:
        pass
    return set()

def save_sudo() -> None:
    try:
        with open(SUDO_FILE, "w") as f:
            json.dump(list(SUDO_USERS - OWNER_IDS), f)
    except Exception:
        pass

def load_extra_tokens() -> List[str]:
    try:
        if os.path.exists(TOKENS_FILE):
            with open(TOKENS_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def load_menu_media() -> Dict[str, str]:
    try:
        if os.path.exists(MEDIA_FILE):
            with open(MEDIA_FILE, "r") as f:
                return json.load(f)
    except Exception:
        pass
    return {}

def save_menu_media(data: Dict[str, str]):
    try:
        with open(MEDIA_FILE, "w") as f:
            json.dump(data, f)
    except Exception:
        pass

known_chats:       Set[int]  = load_groups()
SUDO_USERS:        Set[int]  = load_sudo() | OWNER_IDS
all_bot_instances: List[Any] = []
all_apps:          List[Any] = []
extra_tokens:      List[str] = load_extra_tokens()

mute_chats:          Set[int]       = set()
ncdel_chats:         Set[int]       = set()
ncwar_targets:       Dict[int, str] = {}
autoreact_chats:     Dict[int, str] = {}
custom_react_emojis: Dict[int, str] = {}
slide_reply_targets: Dict[int, int] = {}
autoreply_chats:     Dict[int, str] = {}
targetreply_chats:   Dict[int, dict]= {}
_menu_media:         Dict[str, str] = load_menu_media()
_seen_updates:       Set[int]       = set()

SUFFIX_EMOJIS = [
    "🌸", "🌺", "🌻", "🌹", "🪷", "🌷", "💮", "🏵️",
    "✨", "💫", "⭐", "🌟", "💥", "🔥", "⚡", "❄️",
    "🌊", "🫧", "💧", "🌀", "🌈", "🌙", "☄️", "🌟",
    "💎", "🔮", "🧿", "🪬", "👑", "💀", "🦋", "🐉",
]
_SUFFIX = " ִֶָ𓂃 ࣪˖ ִֶָ{emoji}་༘࿐"
def make_suffix() -> str:
    return _SUFFIX.format(emoji=random.choice(SUFFIX_EMOJIS))

WRAP_LEFT = [
    "🌊", "✨", "💎", "👑", "🔥", "꧁", "⭅╡", "♛", "𖤍", "❦", "⚡", "☄️", "💀", "🌟", "🔱",
]
WRAP_RIGHT = [
    "🌊", "⚡", "💀", "🔥", "✨", "꧂", "╞⭆", "♛", "𖤍", "❦", "🌙", "💎", "👑", "☄️", "🔱",
]

def _build_name(text: str, last: list) -> str:
    for _ in range(20):
        wl = random.choice(WRAP_LEFT)
        wr = random.choice(WRAP_RIGHT)
        suf = make_suffix()
        candidate = f"{wl}{text}{wr}{suf}"[:255]
        if candidate != last[0]:
            last[0] = candidate
            return candidate
    return f"{text}{make_suffix()}{random.randint(0,99)}"[:255]

BURN_SYMS = ["🔥","💥","⚡","☄️","🌋","🔴","🟠","🌩️","🌪️","💣"]
WAVE_SYMBOLS = [
    "🌊","💧","🫧","🌀","🌧️","⛲","🚿","🐚","🌬️","🫗",
    "🧊","🌈","⛵","🏄","🤽","🐬","🐟","🦈","🫙","💎",
]
WATER_SYMS = [
    "🌊","💧","🚿","🛁","🫧","🐚","🌀","🌧️","⛲","🌬️",
    "🌊🌧️","💧🌊","🫧🌊","🌀🌊","🌊💧","🌧️🌊","⛲🌊","🐚🌊",
]

def is_admin(user_id: int) -> bool:
    return _is_owner(user_id) or user_id in SUDO_USERS

# Dynamic per-chat bot tracking: Har GC mein chahe 1 bot ho ya 10, bot turant chalega!
chat_bots: Dict[int, Set[int]] = {}
_chat_message_handled: Set[tuple] = set()

def register_bot_in_chat(chat_id: int, bot):
    if chat_id not in chat_bots:
        chat_bots[chat_id] = set()
    bot_id = getattr(bot, 'id', None)
    if bot_id:
        chat_bots[chat_id].add(bot_id)

def get_bots_for_chat(chat_id: int, current_bot=None) -> List[Any]:
    active_ids = chat_bots.get(chat_id, set())
    if active_ids:
        present = [b for b in all_bot_instances if b and getattr(b, 'id', None) in active_ids]
        if present:
            return present
    if current_bot:
        return [current_bot]
    return [b for b in all_bot_instances if b is not None]

def _is_primary_bot(context, chat_id: Optional[int] = None) -> bool:
    # Kisi bhi GC mein jo bot present hai wo command execute kar sakta hai
    return True

_OWNER_GATE_MSG = (
    "┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅\n"
    "⚡️ 𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 ⚡️\n"
    "ƬӨΉΛЯ MΛΛI K ƧΉӨDӨ ЯΛПDY KΣ BΛᄃΉΣ ! ΛMЯIƬ BΛΛP ƧΣ ! JΛKΣ PΣЯMIƧƧIӨП ᄂΣ ! 🏴‍☠️🤣✋️🤣.\n"
    "┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅┅"
)

def _dedup(handler):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_chat and context.bot:
            register_bot_in_chat(update.effective_chat.id, context.bot)
            if update.effective_chat.type in ("group", "supergroup"):
                if update.effective_chat.id not in known_chats:
                    known_chats.add(update.effective_chat.id)
                    save_groups(known_chats)

        uid = (context.bot.id, update.update_id)
        if uid in _seen_updates: return
        _seen_updates.add(uid)
        if len(_seen_updates) > 20000:
            for u in sorted(_seen_updates)[:10000]:
                _seen_updates.discard(u)

        msg = update.message or update.edited_message
        if msg:
            if update.effective_chat and msg.text:
                msg_text = msg.text.strip()
                # Check if it is a bot command or trigger
                if msg_text.startswith('/') or msg_text.startswith('+') or msg_text.startswith('💦'):
                    msg_key = (update.effective_chat.id, msg.message_id)
                    if msg_key in _chat_message_handled:
                        return
                    _chat_message_handled.add(msg_key)
                    if len(_chat_message_handled) > 20000:
                        for k in list(_chat_message_handled)[:10000]:
                            _chat_message_handled.discard(k)

            if msg.text and msg.text.startswith('/'):
                user = update.effective_user
                if not user or not is_admin(user.id):
                    try: await msg.reply_text(_OWNER_GATE_MSG)
                    except Exception: pass
                    return
        await handler(update, context)
    return wrapper

class BotFloodTracker:
    def __init__(self):
        self._flood_until: Dict[int, float] = {}
        self._rename_ts: Dict[int, List[float]] = {}
        self._RATE_WIN = 60.0
        self._SOFT_LIMIT = 14

    FLOOD_CAP = 3.0

    def is_flooded(self, bot_id: int) -> bool:
        exp = self._flood_until.get(bot_id, 0.0)
        if time.monotonic() < exp: return True
        self._flood_until.pop(bot_id, None)
        return False

    def mark_flooded(self, bot_id: int, seconds: float) -> None:
        capped = min(float(seconds), self.FLOOD_CAP)
        self._flood_until[bot_id] = time.monotonic() + max(capped, 0.05)

    def remaining(self, bot_id: int) -> float:
        return max(0.0, self._flood_until.get(bot_id, 0.0) - time.monotonic())

    def record(self, bot_id: int) -> None:
        now = time.monotonic()
        buf = self._rename_ts.setdefault(bot_id, [])
        buf.append(now)
        cut = now - self._RATE_WIN
        self._rename_ts[bot_id] = [t for t in buf if t > cut]

    def rate(self, bot_id: int) -> int:
        now = time.monotonic()
        cut = now - self._RATE_WIN
        return sum(1 for t in self._rename_ts.get(bot_id, []) if t > cut)

    def near_limit(self, bot_id: int) -> bool:
        return self.rate(bot_id) >= self._SOFT_LIMIT

_flood_tracker = BotFloodTracker()

class TaskController:
    def __init__(self):
        self.tasks:  Dict[str, asyncio.Task]  = {}
        self.events: Dict[str, asyncio.Event] = {}

    def _key(self, chat_id: int, task_type: str) -> str:
        return f"{chat_id}_{task_type}"

    async def start_task(self, chat_id: int, task_type: str, coro_factory) -> None:
        await self.stop_task(chat_id, task_type)
        key = self._key(chat_id, task_type)
        stop_event = asyncio.Event()
        self.events[key] = stop_event

        async def wrapped():
            try: await coro_factory(stop_event)
            except asyncio.CancelledError: pass
            except Exception as e: logger.error(f"Task {key} error: {e}")
            finally:
                self.tasks.pop(key, None)
                self.events.pop(key, None)

        self.tasks[key] = asyncio.create_task(wrapped())

    async def stop_task(self, chat_id: int, task_type: str) -> bool:
        key = self._key(chat_id, task_type)
        stopped = False
        if key in self.events:
            self.events[key].set()
            stopped = True
        if key in self.tasks:
            task = self.tasks.pop(key)
            if not task.done():
                task.cancel()
                try: await asyncio.wait_for(task, timeout=2.0)
                except Exception: pass
            stopped = True
        self.events.pop(key, None)
        return stopped

    async def stop_all_for_chat(self, chat_id: int) -> int:
        prefix = f"{chat_id}_"
        keys = [k for k in list(self.tasks.keys()) + list(self.events.keys()) if k.startswith(prefix)]
        task_types = set(k.split("_", 1)[1] for k in keys)
        count = 0
        for t in task_types:
            if await self.stop_task(chat_id, t):
                count += 1
        return count

    def is_running(self, chat_id: int, task_type: str) -> bool:
        key = self._key(chat_id, task_type)
        return key in self.tasks and not self.tasks[key].done()

task_controller = TaskController()

# ══════════════════════════════════════════════════════════════════
#  FLOOD BYPASS ENGINES
# ══════════════════════════════════════════════════════════════════
_flood_bypass_enabled: bool = True

async def floodbypass_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global _flood_bypass_enabled
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    args = (context.args or [])
    arg = args[0].lower() if args else "status"
    if arg == "on":
        _flood_bypass_enabled = True
        await update.message.reply_text("✅ 𝐅𝐋𝐎𝐎𝐃 𝐁𝐘𝐏𝐀𝐒𝐒 𝐂𝐎𝐑𝐄 𝐎𝐍\nGhost mode active.")
    elif arg == "off":
        _flood_bypass_enabled = False
        await update.message.reply_text("⛔ 𝐅𝐋𝐎𝐎𝐃 𝐁𝐘𝐏𝐀𝐒𝐒 𝐂𝐎𝐑𝐄 𝐎𝐅𝐅")
    else:
        state = "🟢 ON" if _flood_bypass_enabled else "🔴 OFF"
        bots = [b for b in all_bot_instances if b is not None]
        flooded = sum(1 for b in bots if _flood_tracker.is_flooded(getattr(b, "id", id(b))))
        await update.message.reply_text(f"📊 𝐅𝐋𝐎𝐎𝐃 𝐁𝐘𝐏𝐀𝐒𝐒 𝐒𝐓𝐀𝐓𝐔𝐒: {state}\nBots: {len(bots)} | Flooded: {flooded}")

async def _steadync_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory, delay: float = 0.0):
    if not bots: return
    async def _bot_worker(bot):
        bot_id = getattr(bot, "id", id(bot))
        while not stop_event.is_set():
            if _flood_tracker.is_flooded(bot_id):
                wait = _flood_tracker.remaining(bot_id)
                if wait > 0:
                    try: await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.25))
                    except asyncio.TimeoutError: pass
                continue
            try:
                name = name_factory()[:255]
                await bot.set_chat_title(chat_id, name)
            except RetryAfter as e:
                _flood_tracker.mark_flooded(bot_id, e.retry_after)
                continue
            except (BadRequest, Forbidden, TimedOut, NetworkError):
                if stop_event.is_set(): break
                try: await asyncio.wait_for(stop_event.wait(), timeout=0.3)
                except asyncio.TimeoutError: pass
                continue
            except Exception:
                if stop_event.is_set(): break
                await asyncio.sleep(0.1)
                continue
            if stop_event.is_set(): break
            if delay > 0:
                try: await asyncio.wait_for(stop_event.wait(), timeout=delay)
                except asyncio.TimeoutError: continue
                else: break
            else: await asyncio.sleep(0)
    workers = [asyncio.create_task(_bot_worker(bot)) for bot in bots]
    try: await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done(): w.cancel()

async def _hyperfire_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    CONCURRENCY = 2
    if not bots: return
    async def _safe_rename(bot, name: str, bot_id: int, sem: asyncio.Semaphore):
        try:
            await bot.set_chat_title(chat_id, name)
            print(f"⚡ [NC RENAME] GC: {chat_id} -> {name[:25]}")
        except RetryAfter as e:
            _flood_tracker.mark_flooded(bot_id, e.retry_after)
            print(f"⚠️ [FLOOD WAIT] GC {chat_id} / Bot {bot_id}: wait {e.retry_after}s")
        except Exception as e:
            print(f"❌ [RENAME ERROR] GC {chat_id}: {e}")
        finally:
            sem.release()

    async def _bot_worker(bot):
        bot_id = getattr(bot, "id", id(bot))
        sem = asyncio.Semaphore(CONCURRENCY)
        fire_tasks = set()
        try:
            while not stop_event.is_set():
                if _flood_tracker.is_flooded(bot_id):
                    wait = _flood_tracker.remaining(bot_id)
                    if wait > 0:
                        try: await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.25))
                        except asyncio.TimeoutError: pass
                    continue
                try: await asyncio.wait_for(sem.acquire(), timeout=0.1)
                except asyncio.TimeoutError: continue
                if stop_event.is_set():
                    sem.release()
                    break
                name = name_factory()[:255]
                t = asyncio.create_task(_safe_rename(bot, name, bot_id, sem))
                fire_tasks.add(t)
                t.add_done_callback(fire_tasks.discard)
                await asyncio.sleep(0.4)
        finally:
            for t in list(fire_tasks):
                if not t.done(): t.cancel()

    workers = [asyncio.create_task(_bot_worker(bot)) for bot in bots]
    try: await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done(): w.cancel()

async def _stealth_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    if not bots: return
    async def _bot_worker(bot):
        bot_id = getattr(bot, "id", id(bot))
        while not stop_event.is_set():
            if _flood_tracker.is_flooded(bot_id):
                wait = _flood_tracker.remaining(bot_id)
                if wait > 0:
                    try: await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.25))
                    except asyncio.TimeoutError: pass
                continue
            try:
                name = name_factory()[:255]
                await bot.set_chat_title(chat_id, name)
            except RetryAfter as e:
                _flood_tracker.mark_flooded(bot_id, e.retry_after)
                continue
            except Exception:
                if stop_event.is_set(): break
                await asyncio.sleep(0.05)
                continue
            if stop_event.is_set(): break
            jitter = random.uniform(0.03, 0.12)
            try: await asyncio.wait_for(stop_event.wait(), timeout=jitter)
            except asyncio.TimeoutError: pass
    workers = [asyncio.create_task(_bot_worker(bot)) for bot in bots]
    try: await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done(): w.cancel()

async def _trio_rotate_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    if not bots: return
    groups = [bots[i:i + 3] for i in range(0, len(bots), 3)]
    async def _bot_worker(bot, start_delay: float):
        bot_id = getattr(bot, "id", id(bot))
        if start_delay > 0:
            try: await asyncio.wait_for(stop_event.wait(), timeout=start_delay)
            except asyncio.TimeoutError: pass
        if stop_event.is_set(): return
        while not stop_event.is_set():
            if _flood_tracker.is_flooded(bot_id):
                wait = _flood_tracker.remaining(bot_id)
                if wait > 0:
                    try: await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.3))
                    except asyncio.TimeoutError: pass
                continue
            try:
                name = name_factory()[:255]
                await bot.set_chat_title(chat_id, name)
                _flood_tracker.record(bot_id)
            except RetryAfter as e:
                if e.retry_after <= 15.0:
                    try: await asyncio.wait_for(stop_event.wait(), timeout=random.uniform(0.02, 0.10))
                    except asyncio.TimeoutError: pass
                else: _flood_tracker.mark_flooded(bot_id, e.retry_after)
                continue
            except Exception:
                if stop_event.is_set(): break
                await asyncio.sleep(0.03)
                continue
            if stop_event.is_set(): break
            if _flood_tracker.near_limit(bot_id):
                try: await asyncio.wait_for(stop_event.wait(), timeout=0.10)
                except asyncio.TimeoutError: pass
            else: await asyncio.sleep(0)
    workers = []
    for gi, group in enumerate(groups):
        for bi, bot in enumerate(group):
            workers.append(asyncio.create_task(_bot_worker(bot, gi * 1.8 + bi * 0.04)))
    try: await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done(): w.cancel()

async def _mental_hyperblitz_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    if not bots: return
    CONCURRENCY = 3
    async def _fire(bot, name: str, bot_id: int, sem: asyncio.Semaphore):
        try: await bot.set_chat_title(chat_id, name)
        except RetryAfter as e:
            if e.retry_after <= 99.0: await asyncio.sleep(random.uniform(0.001, 0.003))
            else: _flood_tracker.mark_flooded(bot_id, e.retry_after)
        except Exception: pass
        finally: sem.release()

    async def _bot_worker(bot):
        bot_id = getattr(bot, "id", id(bot))
        sem = asyncio.Semaphore(CONCURRENCY)
        fire_tasks = set()
        try:
            while not stop_event.is_set():
                if _flood_tracker.is_flooded(bot_id):
                    wait = _flood_tracker.remaining(bot_id)
                    if wait > 0:
                        try: await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.2))
                        except asyncio.TimeoutError: pass
                    continue
                try: await asyncio.wait_for(sem.acquire(), timeout=0.1)
                except asyncio.TimeoutError: continue
                if stop_event.is_set():
                    sem.release()
                    break
                name = name_factory()[:255]
                t = asyncio.create_task(_fire(bot, name, bot_id, sem))
                fire_tasks.add(t)
                t.add_done_callback(fire_tasks.discard)
        finally:
            for t in list(fire_tasks):
                if not t.done(): t.cancel()

    workers = [asyncio.create_task(_bot_worker(bot)) for bot in bots]
    try: await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done(): w.cancel()

async def _pair_rotate_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    if not bots: return
    pairs = [bots[i:i + 2] for i in range(0, len(bots), 2)]
    async def _fire_bot(bot, name: str):
        bot_id = getattr(bot, "id", id(bot))
        if _flood_tracker.is_flooded(bot_id): return
        try: await bot.set_chat_title(chat_id, name)
        except RetryAfter as e:
            if e.retry_after <= 25.0: await asyncio.sleep(random.uniform(0.01, 0.04))
            else: _flood_tracker.mark_flooded(bot_id, e.retry_after)
        except Exception: pass
    async def _pair_worker(pair_idx: int):
        offset = pair_idx * 0.8
        if offset > 0:
            try: await asyncio.wait_for(stop_event.wait(), timeout=offset)
            except asyncio.TimeoutError: pass
        if stop_event.is_set(): return
        pair = pairs[pair_idx]
        while not stop_event.is_set():
            name = name_factory()[:255]
            if len(pair) == 2:
                await asyncio.gather(_fire_bot(pair[0], name), _fire_bot(pair[1], name_factory()[:255]), return_exceptions=True)
            else: await _fire_bot(pair[0], name)
            await asyncio.sleep(0.03)
    tasks = [asyncio.create_task(_pair_worker(i)) for i in range(len(pairs))]
    try: await asyncio.gather(*tasks, return_exceptions=True)
    finally:
        for t in tasks:
            if not t.done(): t.cancel()

async def _ghost_burn_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    if not bots: return
    async def _bot_worker(bot):
        bot_id = getattr(bot, "id", id(bot))
        while not stop_event.is_set():
            if _flood_tracker.is_flooded(bot_id):
                wait = _flood_tracker.remaining(bot_id)
                if wait > 0:
                    try: await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.3))
                    except asyncio.TimeoutError: pass
                continue
            try:
                name = name_factory()[:255]
                await bot.set_chat_title(chat_id, name)
            except RetryAfter as e:
                if e.retry_after <= 8.0:
                    try: await asyncio.wait_for(stop_event.wait(), timeout=random.uniform(0.05, 0.35))
                    except asyncio.TimeoutError: pass
                else: _flood_tracker.mark_flooded(bot_id, e.retry_after)
                continue
            except Exception:
                if stop_event.is_set(): break
                await asyncio.sleep(0.05)
                continue
            if stop_event.is_set(): break
            await asyncio.sleep(0)
    workers = [asyncio.create_task(_bot_worker(bot)) for bot in bots]
    try: await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done(): w.cancel()

async def _relay_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    if not bots: return
    pairs = [bots[i:i + 2] for i in range(0, len(bots), 2)]
    n_pairs = len(pairs)
    active = [0]
    async def _bot_worker(bot, group_idx: int):
        bot_id = getattr(bot, "id", id(bot))
        while not stop_event.is_set():
            delay = 0.0 if group_idx == active[0] else 0.4
            if _flood_tracker.is_flooded(bot_id):
                wait = _flood_tracker.remaining(bot_id)
                if wait > 0:
                    try: await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.3))
                    except asyncio.TimeoutError: pass
                continue
            try:
                name = name_factory()[:255]
                await bot.set_chat_title(chat_id, name)
            except RetryAfter as e:
                _flood_tracker.mark_flooded(bot_id, e.retry_after)
                active[0] = (active[0] + 1) % n_pairs
                continue
            except Exception:
                if stop_event.is_set(): break
                await asyncio.sleep(0.05)
                continue
            if stop_event.is_set(): break
            if delay > 0:
                try: await asyncio.wait_for(stop_event.wait(), timeout=delay)
                except asyncio.TimeoutError: continue
                else: break
            else: await asyncio.sleep(0)
    workers = [asyncio.create_task(_bot_worker(bot, g_idx)) for g_idx, group in enumerate(pairs) for bot in group]
    try: await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done(): w.cancel()

async def _adaptive_burst_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    if not bots: return
    adaptive_gap = [0.0]
    async def _safe_rename(bot, name: str) -> bool:
        bot_id = getattr(bot, "id", id(bot))
        if _flood_tracker.is_flooded(bot_id): return False
        try:
            await bot.set_chat_title(chat_id, name)
            return True
        except RetryAfter as e:
            _flood_tracker.mark_flooded(bot_id, e.retry_after)
            return False
        except Exception: return False
    while not stop_event.is_set():
        name = name_factory()[:255]
        results = await asyncio.gather(*[asyncio.create_task(_safe_rename(b, name)) for b in bots], return_exceptions=True)
        flood_count = sum(1 for r in results if r is False)
        adaptive_gap[0] = min(1.2, adaptive_gap[0] + 0.15 * flood_count) if flood_count > 0 else max(0.0, adaptive_gap[0] * 0.85)
        if stop_event.is_set(): break
        gap = adaptive_gap[0]
        if gap > 0:
            try: await asyncio.wait_for(stop_event.wait(), timeout=gap)
            except asyncio.TimeoutError: pass
        else: await asyncio.sleep(0)

# ══════════════════════════════════════════════════════════════════
#  ULTRA SYMBOLS & ULTRA ENGINE
# ══════════════════════════════════════════════════════════════════
_ULTRA_SYMS_A = [
    "꧁","꧂","𖤍","𓂀","𓃰","𓆏","𓅓","𓊈","𓊉","𓋴",
    "꩜","꫁","ꫂ","ꗃ","ꖰ","꙰","ꬶ","ꬷ","꒦","꒷",
    "⟦","⟧","⸨","⸩","⌬","⍟","⎔","⧖","⧗","⌇",
    "🔱","⚜","♛","♜","♞","♟","⚔️","🗡️","🏹","🪃",
]
_ULTRA_SYMS_B = [
    "🔥","💥","⚡","☄️","💀","🌋","🌪️","🌩️","💣","🧨",
    "🖤","❤️‍🔥","🩸","☠️","👁️","🕷️","🕸️","🦂","🐍","🐉",
    "✦","✧","⊹","✶","⋆","★","☆","✩","✪","✫",
    "◈","◉","◎","◆","◇","◼","◻","▪","▸","▾",
]
_ULTRA_SYMS_C = [
    "𝕳","𝕬","𝕭","𝕮","𝕯","𝕰","𝕱","𝕲","𝖃","𝖄",
    "ꀘ","ꁷ","ꂝ","ꃋ","ꄞ","ꅉ","ꆖ","ꇡ","ꈠ","ꉻ",
    "꜀","꜁","꜂","꜃","꜄","꜅","꜆","꜇","꜈","꜉",
]

def _ultra_name(text: str, last: list) -> str:
    for _ in range(25):
        a = random.choice(_ULTRA_SYMS_A)
        b = random.choice(_ULTRA_SYMS_B)
        c = random.choice(_ULTRA_SYMS_C)
        sf = make_suffix()
        r = random.randint(0, 3)
        if r == 0: c_ = f"{a}{b}{text}{c}{sf}"
        elif r == 1: c_ = f"{a}{text}{b}{c}{sf}"
        elif r == 2: c_ = f"{a}{b}{text}{c}{sf}"
        else: c_ = f"{c}{text}{a}{b}{sf}"
        c_ = c_[:255]
        if c_ != last[0]:
            last[0] = c_
            return c_
    return f"{text}{make_suffix()}"[:255]

async def _ultra_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    if not bots: return
    groups = [bots[i:i + 3] for i in range(0, len(bots), 3)]
    pending = set()
    def _on_done(t): pending.discard(t)
    async def _fire(bot, name: str, bot_id: int):
        try:
            await bot.set_chat_title(chat_id, name)
            _flood_tracker.record(bot_id)
        except RetryAfter as e:
            if e.retry_after <= 20.0: await asyncio.sleep(random.uniform(0.01, 0.04))
            else: _flood_tracker.mark_flooded(bot_id, e.retry_after)
        except Exception: pass
    async def _bot_worker(bot, start_delay: float):
        bot_id = getattr(bot, "id", id(bot))
        if start_delay > 0:
            try: await asyncio.wait_for(stop_event.wait(), timeout=start_delay)
            except asyncio.TimeoutError: pass
        if stop_event.is_set(): return
        while not stop_event.is_set():
            if _flood_tracker.is_flooded(bot_id):
                wait = _flood_tracker.remaining(bot_id)
                if wait > 0:
                    try: await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.3))
                    except asyncio.TimeoutError: pass
                continue
            name = name_factory()[:255]
            t = asyncio.create_task(_fire(bot, name, bot_id))
            pending.add(t)
            t.add_done_callback(_on_done)
            if _flood_tracker.rate(bot_id) >= 12:
                try: await asyncio.wait_for(stop_event.wait(), timeout=0.08)
                except asyncio.TimeoutError: pass
            else: await asyncio.sleep(0)
    workers = []
    for gi, group in enumerate(groups):
        for bi, bot in enumerate(group):
            workers.append(asyncio.create_task(_bot_worker(bot, gi * 1.5 + bi * 0.03)))
    try: await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done(): w.cancel()
        for t in list(pending): t.cancel()

async def _blitz_engine(chat_id: int, bots: List[Any], stop_event: asyncio.Event, name_factory):
    if not bots: return
    sem = asyncio.Semaphore(2)
    async def _fire(bot, name: str, bot_id: int):
        try: await bot.set_chat_title(chat_id, name)
        except RetryAfter as e:
            if e.retry_after <= 25.0: await asyncio.sleep(random.uniform(0.003, 0.010))
            else: _flood_tracker.mark_flooded(bot_id, e.retry_after)
        except Exception: pass
        finally: sem.release()
    async def _bot_worker(bot):
        bot_id = getattr(bot, "id", id(bot))
        while not stop_event.is_set():
            if _flood_tracker.is_flooded(bot_id):
                wait = _flood_tracker.remaining(bot_id)
                if wait > 0:
                    try: await asyncio.wait_for(stop_event.wait(), timeout=min(wait, 0.3))
                    except asyncio.TimeoutError: pass
                continue
            try: await asyncio.wait_for(sem.acquire(), timeout=0.1)
            except asyncio.TimeoutError: continue
            if stop_event.is_set():
                sem.release()
                break
            name = name_factory()[:255]
            asyncio.create_task(_fire(bot, name, bot_id))
    workers = [asyncio.create_task(_bot_worker(bot)) for bot in bots]
    try: await asyncio.gather(*workers, return_exceptions=True)
    finally:
        for w in workers:
            if not w.done(): w.cancel()

# ══════════════════════════════════════════════════════════════════
#  DECORATED GOD-TIER VIP MENU & INLINE PANELS
# ══════════════════════════════════════════════════════════════════
_MENU_TEXT = (
    "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
    "『𓍼ֶָ֢˖ ࣪ꨄ 𝐀𝐌𝐑𝐈𝐓 𝐗 𝐌𝐄𝐍𝐓𝐀𝐋 .་༘࿐』\n"
    "╚═━─ 𖤐🐉𖤐 ─━═╝\n"
    "\n"
    "╭━━━𓆩 🐉 𝐍𝐄𝐗𝐔𝐒 𝐂𝐎𝐑𝐄 𓆪━━━╮\n"
    "│ ✦ 🤖 𝐁ᴏᴛ: 𝐀ᴍʀɪᴛ 𝐗 𝐌ᴇɴᴛᴀʟ ꨄ\n"
    "│ 𖤐 👑 𝐎ᴡɴᴇʀ: 𝐏ʀɪᴍᴀʀʏ 𝐀ᴅᴍɪɴ ✧\n"
    "│ ✦ ⚙️ 𝐏ʀᴇꜰɪx: [ + / 💦 / / ] ꨄ\n"
    "│ 𖤐 🟢 𝐌ᴏᴅᴇ: 𝐔ʟᴛʀᴀ 𝐎ᴘᴇʀᴀᴛɪᴏɴ ✧\n"
    "│ ✦ 🤖 𝐅ʟᴇᴇᴛ: 𝐌ᴜʟᴛɪ-𝐁ᴏᴛ 𝐌ᴏᴅᴇ ꨄ\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "╭━━━𓆩 🚀 𝐐𝐔𝐈𝐂𝐊 𝐒𝐓𝐀𝐑𝐓 𓆪━━━╮\n"
    "│ ✦ 𝟏  𝐌ᴇɴᴜ     →  /help\n"
    "│ 𖤐 𝟐  𝐓ʀʏ      →  +rnc hello\n"
    "│ ✦ 𝟑  𝐇ᴀʟᴛ     →  /stop\n"
    "│ 𖤐 𝟒  𝐒ᴛᴀᴛᴜꜱ   →  /bots\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "╭━━━𓆩 🌀 𝐀𝐋𝐋 𝐍𝐂 𝐂𝐎𝐌𝐌𝐀𝐍𝐃𝐒 𓆪━━━╮\n"
    "│ ✦ 🌐 +allgcnc <text>   ɢʟᴏʙᴀʟ ᴀʟʟ-ɢᴄ ɴᴄ\n"
    "│ 𖤐 🛑 /stopglobalnc    ꜱᴛᴏᴘ ɢʟᴏʙᴀʟ ɴᴄ\n"
    "│ ✦ 🎲 +rnc <text>       ʀᴀɴᴅᴏᴍ ɴᴀᴍᴇ ᴄʏᴄʟᴇ\n"
    "│ 𖤐 🔥 +flamenc <text>   ғʟᴀᴍᴇ ɴᴀᴍᴇ ᴍᴏᴅᴇ\n"
    "│ ✦ 🌙 +lunanc <text>     ʟᴜɴᴀ ɴᴀᴍᴇ ᴍᴏᴅᴇ\n"
    "│ 𖤐 🌊 +ohyesnc <text>   ᴡᴀᴠᴇ ʀᴇʟᴀʏ ᴍᴏᴅᴇ\n"
    "│ ✦ 💥 +aahnc <text>      ᴀᴅᴀᴘᴛɪᴠᴇ ʙᴜʀꜱᴛ\n"
    "│ 𖤐 🌊 +horneync <text>  ᴡᴀᴛᴇʀ ʜʏᴘᴇʀғɪʀᴇ\n"
    "│ ✦ 💎 +purenc <text>     ᴘᴜʀᴇ ɴᴀᴍᴇ ᴍᴏᴅᴇ\n"
    "│ 𖤐 🥷 +stealthnc <text> ᴍɪᴄʀᴏ-ᴊɪᴛᴛᴇʀ ᴍᴏᴅᴇ\n"
    "│ ✦ ⚡ +bhosdanc <text>   ᴇᴍᴏᴊɪ ʙᴜʀꜱᴛ ᴍᴏᴅᴇ\n"
    "│ 𖤐 🔱 +areync <text>    ᴘᴇʀꜱᴏɴᴀʟ ɴᴀᴍᴇ ᴍᴏᴅᴇ\n"
    "│ ✦ 🎩 +hatnc <text>      ʜᴀᴛ ꜱᴛʏʟᴇ ᴍᴏᴅᴇ\n"
    "│ 𖤐 😭 +crync <text>     ᴄʀʏ ᴇᴍᴏᴊɪ ᴍᴏᴅᴇ\n"
    "│ ✦ ☠️ +zalgonc <text>   ᴢᴀʟɢᴏ ɢʟɪᴛᴄʜ ᴍᴏᴅᴇ\n"
    "│ 𖤐 🌈 +gradientnc <text> ɢʀᴀᴅɪᴇɴᴛ ᴄᴏʟᴏʀ ᴍᴏᴅᴇ\n"
    "│ ✦ 🧠 +mentalnc <text>   𝐀ᴍʀɪᴛ ᴘᴇʀꜱᴏɴᴀʟ ᴍᴏᴅᴇ\n"
    "│ 𖤐 🧠 +amritnc <text>   𝐀ᴍʀɪᴛ ɢʜᴏꜱᴛ ᴍᴏᴅᴇ\n"
    "│ ✦ ⚡ +amritxnc <text>   𝐀ᴍʀɪᴛ ʟɪɢʜᴛ ᴍᴏᴅᴇ\n"
    "│ 𖤐 🔄 +tripnc  +ultranc  +pairnc\n"
    "│ ✦ 🔥 +infernc  +voidnc  +stormnc\n"
    "│ 𖤐 🩸 +bloodnc  +divinenc  ʙʟɪᴛᴢ ᴘʀᴇꜱᴇᴛꜱ\n"
    "│ ✦ 🔤 +boldnc  +italicnc  +cursivenc\n"
    "│ 𖤐 ✍️ +bubblenc  +smallcapsnc  +flipnc\n"
    "│ ✦ 🧠 +mental1 +mental2 +mental3 +mental4 +mental5\n"
    "│ 𖤐 +mental6 +mental7 +mental8 +mental9 +mental10\n"
    "│ 𖤐 ⛔ /stop  ꜱᴛᴏᴘ ᴀᴄᴛɪᴠᴇ ɴᴄ ᴄʏᴄʟᴇꜱ\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "╭━━━𓆩 🎭 𝐀𝐍𝐈𝐌𝐀𝐓𝐈𝐎𝐍 𓆪━━━╮\n"
    "│ ✦ +loading       ᴀɴɪᴍᴀᴛᴇᴅ ʟᴏᴀᴅɪɴɢ ʙᴀʀ\n"
    "│ 𖤐 +spinner       ꜱᴘɪɴɴᴇʀ ᴡɪᴛʜ ʙʀᴀɴᴅ ʟᴀʙᴇʟꜱ\n"
    "│ ✦ +countdown [N]  ᴄᴏᴜɴᴛᴅᴏᴡɴ ᴀɴɪᴍᴀᴛɪᴏɴ\n"
    "│ 𖤐 +typewrite <text>  ʟᴇᴛᴛᴇʀ-ʙʏ-ʟᴇᴛᴛᴇʀ ᴛʏᴘᴇ\n"
    "│ ✦ +glitch <text>  ɢʟɪᴛᴄʜ ᴛᴇxᴛ ᴀɴɪᴍᴀᴛɪᴏɴ\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "╭━━━𓆩 😈 𝐅𝐀𝐊𝐄 𝐓𝐑𝐎𝐋𝐋 𓆪━━━╮\n"
    "│ ✦ /fakeban @user   ғᴀᴋᴇ ʙᴀɴ ᴀɴɪᴍᴀᴛɪᴏɴ\n"
    "│ 𖤐 /fakekick @user  ғᴀᴋᴇ ᴋɪᴄᴋ ᴀɴɪᴍᴀᴛɪᴏɴ\n"
    "│ ✦ /fakewarn @user  ғᴀᴋᴇ ᴡᴀʀɴɪɴɢ ᴄᴏᴜɴᴛ\n"
    "│ 𖤐 /fakedm @user    ғᴀᴋᴇ ᴀᴅᴍɪɴ ᴅᴍ ᴀʟᴇʀᴛ\n"
    "│ ✦ +matrix @user    ᴍᴀᴛʀɪx-ꜱᴛʏʟᴇ ᴛʀᴏʟʟ\n"
    "│ 𖤐 +roast @user     ꜱᴀᴠᴀɢᴇ ᴠɪᴘ ʀᴏᴀꜱᴛ ᴅɪᴀʟᴏɢᴜᴇ\n"
    "│ ✦ +iq @user        ʙʀᴀɪɴᴡᴀᴠᴇ ɪǫ ꜱᴄᴀɴɴᴇʀ\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "╭━━━𓆩 💬 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 & 𝐑𝐄𝐏𝐋𝐘 𓆪━━━╮\n"
    "│ ✦ +spam <text>       ᴛᴇxᴛ ʟᴏᴏᴘ\n"
    "│ 𖤐 /stopspam          ꜱᴛᴏᴘ ᴛᴇxᴛ ʟᴏᴏᴘ\n"
    "│ ✦ +slide <text>      ʀᴇᴘʟʏ ᴍᴏᴅᴇ\n"
    "│ 𖤐 +slidereply        ᴀᴜᴛᴏ ʀᴇᴘʟʏ ᴍᴏᴅᴇ\n"
    "│ ✦ /stopslidereply    ꜱᴛᴏᴘ ꜱʟɪᴅᴇ ʀᴇᴘʟʏ\n"
    "│ 𖤐 +autoreply         ᴀᴜᴛᴏ ʀᴇᴘʟʏ ᴛᴇxᴛ\n"
    "│ ✦ /stopautoreply     ꜱᴛᴏᴘ ᴀᴜᴛᴏ ʀᴇᴘʟʏ\n"
    "│ 𖤐 +targetreply       ᴛᴀʀɢᴇᴛ ʀᴇᴘʟʏ ᴍᴏᴅᴇ\n"
    "│ ✦ /stoptargetreply   ꜱᴛᴏᴘ ᴛᴀʀɢᴇᴛ ʀᴇᴘʟʏ\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "╭━━━𓆩 ❤️ 𝐑𝐄𝐀𝐂𝐓𝐈𝐎𝐍 𝐌𝐎𝐃𝐄𝐒 𓆪━━━╮\n"
    "│ ✦ +autoreact  +heartreact  +boomreact\n"
    "│ 𖤐 +customreact <emoji>  ᴄᴜꜱᴛᴏᴍ ʀᴇᴀᴄᴛɪᴏɴ\n"
    "│ ✦ /stopreact            ᴇɴᴅ ᴀᴜᴛᴏ ʀᴇᴀᴄᴛ\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "╭━━━𓆩 🖼️ 𝐌𝐄𝐃𝐈𝐀 𝐌𝐎𝐃𝐔𝐋𝐄𝐒 𓆪━━━╮\n"
    "│ ✦ +aiimg <prompt>  ᴀɪ ɪᴍᴀɢᴇ ɢᴇɴᴇʀᴀᴛᴏʀ\n"
    "│ 𖤐 +song <name>     ꜱᴏɴɢ ꜱᴇᴀʀᴄʜ + ᴀᴜᴅɪᴏ\n"
    "│ ✦ /gcpfp [delay]   ɢʀᴏᴜᴘ ᴘʀᴏꜰɪʟᴇ ᴘɪᴄᴛᴜʀᴇ\n"
    "│ 𖤐 /gcpfpadd  /gcpfpset  ᴘɪᴄ ᴍᴀɴᴀɢᴇʀ\n"
    "│ ✦ /gcpfpstatus  /stopgcpfp  /gcpfpclear\n"
    "│ 𖤐 /setmenuphoto  /setmenuvideo  /clearmenu\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "╭━━━𓆩 🛡️ 𝐆𝐑𝐎𝐔𝐏 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 𓆪━━━╮\n"
    "│ ✦ /joingc <link>       ᴊᴏɪɴ ɢᴄ + ᴀᴜᴛᴏ-ᴀᴅᴍɪɴ\n"
    "│ 𖤐 /folderjoin <link>   ᴀᴜᴛᴏ ꜰᴏʟᴅᴇʀ ᴀᴅᴅ + ᴀᴅᴍɪɴ\n"
    "│ ✦ /mygc                ʟɪꜱᴛ ᴀʟʟ ɢᴄꜱ + ɪɴᴠɪᴛᴇ ʟɪɴᴋꜱ\n"
    "│ 𖤐 /allpromote          ᴀᴜᴛᴏ ᴘʀᴏᴍᴏᴛᴇ ɪɴ ᴀʟʟ ᴅᴄ\n"
    "│ ✦ /addbot [link]       ᴀᴅᴅ + ᴘʀᴏᴍᴏᴛᴇ ʙᴏᴛꜱ ʜᴇʀᴇ\n"
    "│ 𖤐 /mute  /purge [count]  /leave\n"
    "│ 𖤐 /restrict  /unrestrict  /gclist\n"
    "│ ✦ /ncdel  /ncwar  /stopncwar\n"
    "│ 𖤐 /globalstop  /globalmute  /globalunmute\n"
    "│ ✦ /globalannounce <message>\n"
    "│ 𖤐 /stealthlock [on|off]  ꜱɪʟᴇɴᴛ ᴍᴇᴅɪᴀ ʟᴏᴄᴋ\n"
    "│ ✦ /bodyguard [on|off]   ᴠɪᴘ ʙᴏꜱꜱ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "╭━━━𓆩 🔐 𝐀𝐃𝐌𝐈𝐍 & 𝐓𝐎𝐎𝐋𝐒 𓆪━━━╮\n"
    "│ ✦ /ping  /status -   ᴜᴘᴛɪᴍᴇ & ʟᴀᴛᴇɴᴄʏ\n"
    "│ 𖤐 /addsudo  /removesudo  /sudolist\n"
    "│ ✦ /bots  /botname <name>\n"
    "│ 𖤐 /panel  ɪɴᴛᴇʀᴀᴄᴛɪᴠᴇ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ\n"
    "│ ✦ /floodbypass on|off|status\n"
    "│ 𖤐 /start  /help  ᴏᴘᴇɴ ᴛʜɪꜱ ᴅᴇᴄᴋ\n"
    "│ ✦ /tempmail         ᴅɪꜱᴘᴏꜱᴀʙʟᴇ ᴇᴍᴀɪʟ + ᴏᴛᴘ\n"
    "│ 𖤐 +rollcall         ᴍɪʟɪᴛᴀʀʏ ꜰʟᴇᴇᴛ ɪɴꜱᴘᴇᴄᴛɪᴏɴ\n"
    "╰━━━༺❀༻━━━╯\n"
    "\n"
    "┈┉┅━❀꧁ 𓆩♡𓆪 ꧂❀━┅┉┈\n"
    "𖤐 𝐍𝐂: 𝐀ᴍʀɪᴛ 𝐌ᴏᴅᴇ  •  𝐁ʀᴀɴᴅ: 𝐀ᴍʀɪᴛ 𝐗 𝐌ᴇɴᴛᴀʟ 𖤐\n"
    "⋆｡°✩ ❝ 𝐃ᴇꜱɪɢɴᴇᴅ ꜰᴏʀ 𝐀ᴍʀɪᴛ 𝐗 𝐌ᴇɴᴛᴀʟ ❞ ✩°｡⋆\n"
)

_PANEL_HOME_TEXT = "╔═━─ 𓆩🧠𓆪 ─━═╗\n『 𝐌𝐄𝐍𝐓𝐀𝐋 𝐂𝐎𝐍𝐓𝐑𝐎𝐋 𝐏𝐀𝐍𝐄𝐋 』\n╚═━─ 𖤐⚡𖤐 ─━═╝\n\nSelect a module below."
_PANEL_SECTION_TEXT = {
    "nc": "🌀 𝐍𝐂 𝐄𝐍𝐆𝐈𝐍𝐄𝐒\n\n🎲 +rnc\n🔥 +flamenc\n🌊 +horneync\n🥷 +stealthnc\n☠️ +zalgonc\n🌈 +gradientnc",
    "animation": "🎭 𝐀𝐍𝐈𝐌𝐀𝐓𝐈𝐎𝐍\n\n✨ +loading\n🌀 +spinner\n⏳ +countdown\n⌨️ +typewrite\n💻 +matrix",
    "reply": "💬 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐂𝐎𝐍𝐓𝐑𝐎𝐋\n\n📢 +spam\n↩️ +slide\n🤖 +autoreply\n🎯 +targetreply",
    "group": "🛡️ 𝐆𝐑𝐎𝐔𝐏 𝐂𝐎𝐍𝐓𝐑𝐎𝐋\n\n/mute • /purge • /leave • /restrict • /unrestrict • /ncwar • /ncdel",
    "admin": "🔐 𝐀𝐃𝐌𝐈𝐍\n\n/addsudo • /removesudo • /sudolist • /bots • /ping • /floodbypass",
}

def _main_panel_markup():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🧠 Mental Modes", callback_data="panel:mental"), InlineKeyboardButton("🌀 NC Engines", callback_data="panel:nc")],
        [InlineKeyboardButton("🎭 Animation", callback_data="panel:animation"), InlineKeyboardButton("💬 Reply Tools", callback_data="panel:reply")],
        [InlineKeyboardButton("🛡️ Group Control", callback_data="panel:group"), InlineKeyboardButton("🔐 Admin Tools", callback_data="panel:admin")],
        [InlineKeyboardButton("📧 TempMail", callback_data="tmail:new"), InlineKeyboardButton("🎖️ RollCall", callback_data="panel:admin")]
    ])

def _mental_panel_markup():
    rows = []
    for start in (1, 6):
        rows.append([InlineKeyboardButton(f"🧠 {n}", callback_data=f"panel:mental:{n}") for n in range(start, start + 5)])
    rows.append([InlineKeyboardButton("🏠 Main Menu", callback_data="panel:home")])
    return InlineKeyboardMarkup(rows)

async def panel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    await update.message.reply_text(_PANEL_HOME_TEXT, reply_markup=_main_panel_markup())

async def panel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query: return
    if not update.effective_user or not is_admin(update.effective_user.id):
        return await query.answer("Admin access required.", show_alert=True)
    if not _is_primary_bot(context): return
    data = query.data or "panel:home"
    if data == "panel:home":
        text, markup = _PANEL_HOME_TEXT, _main_panel_markup()
    elif data == "panel:mental":
        text, markup = "🧠 𝐌𝐄𝐍𝐓𝐀𝐋 𝐌𝐎𝐃𝐄𝐒\nChoose a preset:", _mental_panel_markup()
    elif data.startswith("panel:mental:"):
        n = data.split(":")[-1]
        text = f"🧠 𝐌𝐄𝐍𝐓𝐀𝐋 {n}\nCommand: +mental{n} <text>"
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🧠 All", callback_data="panel:mental"), InlineKeyboardButton("🏠 Main", callback_data="panel:home")]])
    elif data.startswith("panel:") and data.split(":", 1)[1] in _PANEL_SECTION_TEXT:
        text = _PANEL_SECTION_TEXT[data.split(":", 1)[1]]
        markup = InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data="panel:home")]])
    else: return await query.answer("Unknown option", show_alert=True)
    await query.answer()
    try: await query.edit_message_text(text, reply_markup=markup)
    except Exception: pass

# ══════════════════════════════════════════════════════════════════
#  MENU SENDER & CORE COMMANDS
# ══════════════════════════════════════════════════════════════════
async def _send_menu(target_msg, caption: str, reply_markup=None):
    pid  = _menu_media.get("photo_id")
    vid  = _menu_media.get("video_id")
    anim = _menu_media.get("animation_id")
    doc  = _menu_media.get("document_id")
    if pid or vid or anim or doc:
        try:
            if pid: await target_msg.reply_photo(photo=pid, caption=caption[:1020], reply_markup=reply_markup)
            elif vid: await target_msg.reply_video(video=vid, caption=caption[:1020], reply_markup=reply_markup)
            elif anim: await target_msg.reply_animation(animation=anim, caption=caption[:1020], reply_markup=reply_markup)
            elif doc: await target_msg.reply_document(document=doc, caption=caption[:1020], reply_markup=reply_markup)
            return
        except Exception: pass
    try: await target_msg.reply_text(caption, reply_markup=reply_markup)
    except Exception: pass

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat or not update.message: return
    known_chats.add(update.effective_chat.id)
    save_groups(known_chats)
    await _send_menu(update.message, _MENU_TEXT, _main_panel_markup())

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    await _send_menu(update.message, _MENU_TEXT, _main_panel_markup())

async def stop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message: return
    count = await task_controller.stop_all_for_chat(update.effective_chat.id)
    if count > 0: await update.message.reply_text("🛑 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 — all tasks cancelled instantly.")
    else: await update.message.reply_text("Nothing running here.")

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    start_t = time.monotonic()
    msg = await update.message.reply_text("⚡ Calculating Ping…")
    latency_ms = round((time.monotonic() - start_t) * 1000, 2)
    bots_count = len([b for b in all_bot_instances if b is not None])
    uptime_str = get_uptime()

    status_card = (
        "╔════════════════════════════════╗\n"
        "║   ⚡ 𝐀𝐌𝐑𝐈𝐓 𝐗 𝐌𝐄𝐍𝐓𝐀𝐋 𝐒𝐓𝐀𝐓𝐔𝐒 ⚡   ║\n"
        "╚════════════════════════════════╝\n\n"
        f"🚀 𝐋𝐚𝐭𝐞𝐧𝐜𝐲     :  `{latency_ms} ms` [Ultra Fast]\n"
        f"⏱️ 𝐔𝐩𝐭𝐢𝐦𝐞      :  `{uptime_str}`\n"
        f"🤖 𝐅𝐥𝐞𝐞𝐭 𝐁𝐨𝐭𝐬   :  `{bots_count} Online`\n"
        f"🌐 𝐊𝐧𝐨𝐰𝐧 𝐆𝐂𝐬   :  `{len(known_chats)} Groups`\n"
        f"🛡️ 𝐅𝐥𝐨ᴏᴅ 𝐆ᴜᴀʀᴅ  :  `Active (Ghost Bypass)`\n"
        f"👑 𝐎𝐰𝐧𝐞𝐫 𝐈𝐃     :  `{OWNER_ID}`\n\n"
        "┈┉┅━❀꧁ 𓆩 𝐃𝐎𝐌𝐈𝐍𝐀𝐍𝐂𝐄 𓆪 ꧂❀━┅┉┈"
    )
    await msg.edit_text(status_card, parse_mode="Markdown")

async def addsudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not _is_owner(update.effective_user.id): return
    if not update.message: return
    target_id = None
    if context.args:
        try: target_id = int(context.args[0])
        except ValueError: return await update.message.reply_text("Usage: /addsudo <user_id>")
    elif update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_id = update.message.reply_to_message.from_user.id
    if not target_id: return await update.message.reply_text("Usage: /addsudo <user_id> or reply to a user")
    if target_id in OWNER_IDS: return await update.message.reply_text("Already owner.")
    SUDO_USERS.add(target_id)
    save_sudo()
    await update.message.reply_text(f"✅ Sudo granted to `{target_id}`", parse_mode="Markdown")

async def removesudo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not _is_owner(update.effective_user.id): return
    if not update.message: return
    target_id = None
    if context.args:
        try: target_id = int(context.args[0])
        except ValueError: return await update.message.reply_text("Usage: /removesudo <user_id>")
    elif update.message.reply_to_message and update.message.reply_to_message.from_user:
        target_id = update.message.reply_to_message.from_user.id
    if not target_id: return await update.message.reply_text("Usage: /removesudo <user_id>")
    if target_id in OWNER_IDS: return await update.message.reply_text("Cannot remove owner.")
    SUDO_USERS.discard(target_id)
    save_sudo()
    await update.message.reply_text(f"⛔ Sudo revoked for `{target_id}`", parse_mode="Markdown")

async def sudolist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not _is_owner(update.effective_user.id): return
    if not update.message: return
    users = SUDO_USERS - OWNER_IDS
    if not users: return await update.message.reply_text("No sudo users yet.")
    lines = [f"• `{uid}`" for uid in sorted(users)]
    await update.message.reply_text(f"👥 𝐒𝐔𝐃𝐎 𝐔𝐒𝐄𝐑𝐒 ({len(users)}):\n" + "\n".join(lines), parse_mode="Markdown")


def _get_default_admin_rights():
    if not HAS_TELETHON: return None
    try:
        return ChatAdminRights(
            change_info=True,
            post_messages=True,
            edit_messages=True,
            delete_messages=True,
            ban_users=True,
            invite_users=True,
            pin_messages=True,
            add_admins=False,
            anonymous=False,
            manage_call=True,
            other=True,
            manage_topics=True
        )
    except Exception:
        return None

async def _promote_bot_to_admin(client, chat_entity, bot_entity, rank: str = "⚡ BOT ADMIN ⚡") -> bool:
    rights = _get_default_admin_rights()
    if not rights: return False
    try:
        await client(EditAdminRequest(
            channel=chat_entity,
            user_id=bot_entity,
            admin_rights=rights,
            rank=rank
        ))
        return True
    except Exception as e:
        err = str(e).lower()
        try:
            cid = getattr(chat_entity, "id", None)
            if cid:
                await client(EditChatAdminRequest(chat_id=cid, user_id=bot_entity, is_admin=True))
                return True
        except Exception:
            pass
    return False

class MultiUserbotPool:
    """Multi-account Userbot Pool with automatic FloodWait rotation."""
    def __init__(self):
        self.clients: List[Any] = []
        self.current_idx: int = 0

    async def initialize(self) -> int:
        if not HAS_TELETHON: return 0
        api_id = USERBOT_API_ID or int(os.environ.get("USERBOT_API_ID") or os.environ.get("TELEGRAM_API_ID") or "0")
        api_hash = USERBOT_API_HASH or os.environ.get("USERBOT_API_HASH") or os.environ.get("TELEGRAM_API_HASH") or ""
        
        sessions: List[str] = list(USERBOT_SESSIONS_LIST)
        single = USERBOT_SESSION or os.environ.get("USERBOT_SESSION") or os.environ.get("STRING_SESSION") or ""
        if single and single not in sessions: sessions.append(single)

        for i in range(1, 10):
            env_s = os.environ.get(f"USERBOT_SESSION_{i}", "").strip()
            if env_s and env_s not in sessions: sessions.append(env_s)

        if os.path.exists("userbot_creds.json"):
            try:
                with open("userbot_creds.json", "r", encoding="utf-8") as f:
                    d = json.load(f)
                    if isinstance(d, dict):
                        if not api_id: api_id = int(d.get("api_id", 0))
                        if not api_hash: api_hash = d.get("api_hash", "")
                        ss = d.get("string_session")
                        if ss and ss not in sessions: sessions.append(ss)
                        if "sessions" in d and isinstance(d["sessions"], list):
                            for extra_s in d["sessions"]:
                                if extra_s and extra_s not in sessions: sessions.append(extra_s)
                    elif isinstance(d, list):
                        for item in d:
                            if isinstance(item, dict):
                                ss = item.get("string_session")
                                if ss and ss not in sessions: sessions.append(ss)
            except Exception: pass

        if not api_id or not api_hash: return 0

        if not sessions and os.path.exists("amrit_userbot.session"):
            sessions.append("")

        self.clients = []
        for sess_str in sessions:
            try:
                if sess_str:
                    cl = TelegramClient(StringSession(sess_str), api_id, api_hash)
                else:
                    cl = TelegramClient("amrit_userbot", api_id, api_hash)
                await cl.connect()
                if await cl.is_user_authorized():
                    self.clients.append(cl)
                else:
                    await cl.disconnect()
            except Exception: pass
        return len(self.clients)

    def get_client(self):
        if not self.clients: return None
        return self.clients[self.current_idx % len(self.clients)]

    def rotate_next(self):
        if not self.clients: return None
        self.current_idx = (self.current_idx + 1) % len(self.clients)
        return self.get_client()

    def has_multiple(self) -> bool:
        return len(self.clients) > 1

    async def disconnect_all(self):
        for cl in self.clients:
            try: await cl.disconnect()
            except Exception: pass
        self.clients = []

async def _init_userbot_client():
    pool = MultiUserbotPool()
    count = await pool.initialize()
    if count == 0:
        if not HAS_TELETHON: return None, "NO_TELETHON"
        return None, "NO_CREDS"
    return pool.get_client(), "OK" 

_USERBOT_SETUP_HELP = (
    "╔═━─ 𓆩⚠️𓆪 ─━═╗\n"
    "『 𝟏𝟎𝟎% 𝐙𝐄𝐑𝐎-𝐓𝐎𝐔𝐂𝐇 𝐒𝐄𝐓𝐔𝐏 』\n"
    "╚═━─ 𖤐⚡𖤐 ─━═╝\n\n"
    "📌 *Userbot login required!*\n"
    "Apne Terminal/RDP par ek baar run karein:\n"
    "👉 `python3 setup_userbot.py`\n\n"
    "Iske baad command daalte hi saare bots apne aap sabhi groups me **Add** aur **Admin Promote** ho jayenge! 🚀"
)

async def _do_auto_folderjoin(bot, chat_id: int, status_msg_id: int, link: str, bot_usernames: List[str]):
    client, status = await _init_userbot_client()
    if not client:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=_USERBOT_SETUP_HELP,
                parse_mode="Markdown"
            )
        except Exception: pass
        return

    try:
        slug = ""
        clean_link = link.strip()
        if "t.me/addlist/" in clean_link:
            slug = clean_link.split("t.me/addlist/")[1].split("?")[0].split("/")[0]
        elif "addlist/" in clean_link:
            slug = clean_link.split("addlist/")[1].split("?")[0].split("/")[0]

        joined_chats = []
        folder_title = "Chat Folder"

        if slug:
            check_res = await client(CheckChatlistInviteRequest(slug=slug))
            folder_title = getattr(check_res, "title", "Chat Folder")
            chats_in_folder = check_res.chats
            peers = check_res.peers
            if peers:
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=status_msg_id,
                        text=(
                            f"╔═━─ 𓆩⚡𓆪 ─━═╗\n"
                            f"『 📁 𝐉𝐎𝐈𝐍𝐈𝐍𝐆 𝐅𝐎𝐋𝐃𝐄𝐑 』\n"
                            f"╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
                            f"📁 *Folder:* `{folder_title}`\n"
                            f"📊 *Found:* {len(chats_in_folder)} Groups\n"
                            f"⏳ Userbot is joining all groups automatically..."
                        ),
                        parse_mode="Markdown"
                    )
                except Exception: pass
                await client(JoinChatlistInviteRequest(slug=slug, peers=peers))
            joined_chats = chats_in_folder
        else:
            hash_str = clean_link.split("/")[-1].replace("+", "")
            res = await client(ImportChatInviteRequest(hash=hash_str))
            joined_chats = res.chats

        bot_entities = []
        for uname in bot_usernames:
            u = uname.strip().lstrip("@")
            if not u: continue
            try:
                ent = await client.get_input_entity(u)
                bot_entities.append((u, ent))
            except Exception: pass

        total = len(joined_chats)
        total_promoted = 0
        total_added = 0

        for idx, chat in enumerate(joined_chats, 1):
            chat_title = getattr(chat, "title", str(getattr(chat, "id", idx)))
            for u, ent in bot_entities:
                try:
                    await client(InviteToChannelRequest(channel=chat, users=[ent]))
                    total_added += 1
                except Exception: pass
                # Auto promote to Admin!
                promoted = await _promote_bot_to_admin(client, chat, ent)
                if promoted: total_promoted += 1
                await asyncio.sleep(0.4)

            if idx % 2 == 0 or idx == total:
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=status_msg_id,
                        text=(
                            f"╔═━─ 𓆩⚡𓆪 ─━═╗\n"
                            f"『 🤖 𝐀𝐔𝐓𝐎-𝐀𝐃𝐃 + 𝐏𝐑𝐎𝐌𝐎𝐓𝐈𝐍𝐆 』\n"
                            f"╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
                            f"📁 *Folder:* `{folder_title}`\n"
                            f"📊 *Progress:* {idx}/{total} Groups processed\n"
                            f"➕ *Added:* {total_added} Bot Additions\n"
                            f"👑 *Promoted:* {total_promoted} Bots made Admin!\n"
                            f"⏳ Live zero-touch execution in progress..."
                        ),
                        parse_mode="Markdown"
                    )
                except Exception: pass

        await client.disconnect()

        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg_id,
            text=(
                "╔═━─ 𓆩🎉𓆪 ─━═╗\n"
                "『 𝐙𝐄𝐑𝐎-𝐓𝐎𝐔𝐂𝐇 𝐅𝐎𝐋𝐃𝐄𝐑 𝐉𝐎𝐈𝐍 𝐃𝐎𝐍𝐄 』\n"
                "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
                f"📁 *Folder:* `{folder_title}`\n"
                f"✅ *Total Groups:* {total}\n"
                f"➕ *Bots Added:* {total_added}\n"
                f"👑 *Bots Promoted to Admin:* {total_promoted}\n\n"
                "✨ *Saare bots automatically add ho kar ADMIN promote ho chuke hain!* 🚀"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=f"❌ Error: `{str(e)[:300]}`",
                parse_mode="Markdown"
            )
        except Exception: pass

async def _do_auto_allpromote(bot, chat_id: int, status_msg_id: int, bot_usernames: List[str]):
    client, status = await _init_userbot_client()
    if not client:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=_USERBOT_SETUP_HELP,
                parse_mode="Markdown"
            )
        except Exception: pass
        return

    try:
        bot_entities = []
        for uname in bot_usernames:
            u = uname.strip().lstrip("@")
            if not u: continue
            try:
                ent = await client.get_input_entity(u)
                bot_entities.append((u, ent))
            except Exception: pass

        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=(
                    "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
                    "『 👑 𝐒𝐂𝐀𝐍𝐍𝐈𝐍𝐆 𝐀𝐋𝐋 𝐃𝐂𝐬 / 𝐆𝐑𝐎𝐔𝐏𝐒 』\n"
                    "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
                    "🔍 Scanning all groups & discussion chats where your account has admin rights...\n"
                    "Har group me sabhi bots ko Add + Admin promote kiya ja raha hai! 🚀"
                ),
                parse_mode="Markdown"
            )
        except Exception: pass

        total_scanned = 0
        promoted_dcs = 0
        total_promoted_bots = 0

        async for dialog in client.iter_dialogs():
            if not (dialog.is_group or dialog.is_channel):
                continue

            chat_ent = dialog.entity
            total_scanned += 1
            chat_promoted = 0

            for u, ent in bot_entities:
                try:
                    await client(InviteToChannelRequest(channel=chat_ent, users=[ent]))
                except Exception: pass

                promoted = await _promote_bot_to_admin(client, chat_ent, ent)
                if promoted:
                    chat_promoted += 1
                    total_promoted_bots += 1
                await asyncio.sleep(0.4)

            if chat_promoted > 0:
                promoted_dcs += 1

            if total_scanned % 5 == 0:
                try:
                    await bot.edit_message_text(
                        chat_id=chat_id,
                        message_id=status_msg_id,
                        text=(
                            f"╔═━─ 𓆩👑𓆪 ─━═╗\n"
                            f"『 𝐀𝐋𝐋-𝐏𝐑𝐎𝐌𝐎𝐓𝐄 𝐈𝐍 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 』\n"
                            f"╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
                            f"📊 *Scanned DCs:* {total_scanned} Groups\n"
                            f"🛡️ *Admin Groups Found:* {promoted_dcs}\n"
                            f"👑 *Bots Promoted to Admin:* {total_promoted_bots}\n"
                            f"⏳ Background auto-promotion ongoing..."
                        ),
                        parse_mode="Markdown"
                    )
                except Exception: pass

        await client.disconnect()

        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg_id,
            text=(
                "╔═━─ 𓆩🎉𓆪 ─━═╗\n"
                "『 👑 𝐀𝐋𝐋-𝐏𝐑𝐎𝐌𝐎𝐓𝐄 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄𝐃 』\n"
                "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
                f"📊 *Total Groups Scanned:* {total_scanned}\n"
                f"🛡️ *Groups Successfully Managed:* {promoted_dcs}\n"
                f"👑 *Total Bot Admins Created:* {total_promoted_bots}\n\n"
                "✨ *Aapke saare fleet bots sabhi DCs me automatically Admin ban chuke hain!* 🚀"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=f"❌ Error during all-promote: `{str(e)[:300]}`",
                parse_mode="Markdown"
            )
        except Exception: pass

async def _do_auto_addbot(bot, chat_id: int, status_msg_id: int, target: str, bot_usernames: List[str]):
    client, status = await _init_userbot_client()
    if not client:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=_USERBOT_SETUP_HELP,
                parse_mode="Markdown"
            )
        except Exception: pass
        return

    try:
        # Resolve target chat
        target_chat = None
        if target:
            clean = target.strip()
            if "t.me/+" in clean or "joinchat/" in clean:
                hash_str = clean.split("/")[-1].replace("+", "")
                res = await client(ImportChatInviteRequest(hash=hash_str))
                target_chat = res.chats[0] if res.chats else None
            else:
                target_chat = await client.get_entity(clean)
        else:
            target_chat = await client.get_entity(chat_id)

        if not target_chat:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text="❌ Could not find or access the target chat!",
                parse_mode="Markdown"
            )
            await client.disconnect()
            return

        bot_entities = []
        for uname in bot_usernames:
            u = uname.strip().lstrip("@")
            if not u: continue
            try:
                ent = await client.get_input_entity(u)
                bot_entities.append((u, ent))
            except Exception: pass

        added = 0
        promoted = 0
        chat_title = getattr(target_chat, "title", "Group")

        for u, ent in bot_entities:
            try:
                await client(InviteToChannelRequest(channel=target_chat, users=[ent]))
                added += 1
            except Exception: pass

            res = await _promote_bot_to_admin(client, target_chat, ent)
            if res: promoted += 1
            await asyncio.sleep(0.5)

        await client.disconnect()

        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg_id,
            text=(
                "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
                "『 👑 𝐀𝐃𝐃 & 𝐏𝐑𝐎𝐌𝐎𝐓𝐄 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄 』\n"
                "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
                f"📢 *Chat:* `{chat_title}`\n"
                f"➕ *Bots Added:* {added}\n"
                f"👑 *Bots Promoted to Admin:* {promoted}\n\n"
                "✨ *Bots have been added and promoted to Admin with full rights!* 🚀"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=f"❌ Error adding and promoting: `{str(e)[:300]}`",
                parse_mode="Markdown"
            )
        except Exception: pass

async def allpromote_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not user or not is_admin(user.id):
        try: await update.message.reply_text(_OWNER_GATE_MSG)
        except Exception: pass
        return

    active_bots = [b for b in all_bot_instances if b is not None]
    bot_names = []
    for b in active_bots:
        try:
            b_user = await b.get_me()
            if b_user.username: bot_names.append(f"@{b_user.username}")
        except Exception: pass

    init_msg = await update.message.reply_text(
        "╔═━─ 𓆩👑𓆪 ─━═╗\n"
        "『 👑 𝐀𝐔𝐓𝐎-𝐏𝐑𝐎𝐌𝐎𝐓𝐄 𝐈𝐍 𝐀𝐋𝐋 𝐃𝐂𝐬 』\n"
        "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
        f"🤖 *Bots to Promote:* {len(bot_names)} Bots\n"
        "⏳ *Status:* Starting scan across all groups & discussion chats...",
        parse_mode="Markdown"
    )
    asyncio.create_task(_do_auto_allpromote(context.bot, chat_id, init_msg.message_id, bot_names))

async def addbot_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not user or not is_admin(user.id):
        try: await update.message.reply_text(_OWNER_GATE_MSG)
        except Exception: pass
        return

    target = " ".join(context.args).strip() if context.args else ""
    raw = (update.message.text or "").strip().split()
    if not target and len(raw) > 1:
        target = raw[1]

    active_bots = [b for b in all_bot_instances if b is not None]
    bot_names = []
    for b in active_bots:
        try:
            b_user = await b.get_me()
            if b_user.username: bot_names.append(f"@{b_user.username}")
        except Exception: pass

    init_msg = await update.message.reply_text(
        "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
        "『 🤖 𝐀𝐃𝐃 & 𝐀𝐔𝐓𝐎-𝐏𝐑𝐎𝐌𝐎𝐓𝐄 ⚡ 』\n"
        "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
        f"🎯 *Target:* `{target if target else 'Current Group'}`\n"
        f"🤖 *Fleet Bots:* {len(bot_names)} Bots\n"
        "⏳ *Status:* Adding bots and promoting them to Admin...",
        parse_mode="Markdown"
    )
    asyncio.create_task(_do_auto_addbot(context.bot, chat_id, init_msg.message_id, target, bot_names))


async def _do_auto_joingc(bot, chat_id: int, status_msg_id: int, targets: List[str], bot_usernames: List[str]):
    client, status = await _init_userbot_client()
    if not client:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=_USERBOT_SETUP_HELP,
                parse_mode="Markdown"
            )
        except Exception: pass
        return

    try:
        bot_entities = []
        for uname in bot_usernames:
            u = uname.strip().lstrip("@")
            if not u: continue
            try:
                ent = await client.get_input_entity(u)
                bot_entities.append((u, ent))
            except Exception: pass

        total_gcs = len(targets)
        processed_gcs = 0
        total_added = 0
        total_promoted = 0
        results_summary = []

        for idx, target in enumerate(targets, 1):
            clean = target.strip().replace("http://", "").replace("https://", "")
            target_chat = None
            chat_name = "Target Group"

            # 1. Join / resolve the target GC
            try:
                if "t.me/+" in clean or "joinchat/" in clean or "+" in clean:
                    hash_str = clean.split("/")[-1].replace("+", "").split("?")[0]
                    try:
                        res = await client(ImportChatInviteRequest(hash=hash_str))
                        target_chat = res.chats[0] if getattr(res, "chats", None) else None
                    except UserAlreadyParticipantError:
                        try:
                            check = await client(CheckChatInviteRequest(hash=hash_str))
                            target_chat = getattr(check, "chat", None)
                        except Exception: pass
                    except Exception: pass
                else:
                    uname = clean.split("/")[-1].split("?")[0].lstrip("@")
                    try:
                        target_chat = await client.get_entity(uname)
                        try:
                            await client(JoinChannelRequest(channel=target_chat))
                        except Exception: pass
                    except Exception: pass
            except Exception as e:
                results_summary.append(f"❌ GC #{idx}: `{clean}` (Error: {str(e)[:40]})")
                continue

            if not target_chat:
                results_summary.append(f"⚠️ GC #{idx}: `{clean}` (Could not resolve or join)")
                continue

            chat_name = getattr(target_chat, "title", str(getattr(target_chat, "id", f"GC #{idx}")))
            try:
                # Add to known_chats
                c_id = getattr(target_chat, "id", None)
                if c_id:
                    # Telegram supergroups have -100 prefix
                    actual_id = c_id if str(c_id).startswith("-") else int(f"-100{c_id}")
                    known_chats.add(actual_id)
                    save_groups(known_chats)
            except Exception: pass

            gc_added = 0
            gc_promoted = 0

            # 2. Add Bots and promote to Admin
            for u, ent in bot_entities:
                try:
                    await client(InviteToChannelRequest(channel=target_chat, users=[ent]))
                    gc_added += 1
                    total_added += 1
                except Exception: pass

                promoted = await _promote_bot_to_admin(client, target_chat, ent)
                if promoted:
                    gc_promoted += 1
                    total_promoted += 1
                await asyncio.sleep(0.4)

            processed_gcs += 1
            results_summary.append(f"✅ *{chat_name}*: {gc_added} Added, {gc_promoted} Promoted")

            # Live update
            try:
                await bot.edit_message_text(
                    chat_id=chat_id,
                    message_id=status_msg_id,
                    text=(
                        f"╔═━─ 𓆩⚡𓆪 ─━═╗\n"
                        f"『 🎯 𝐉𝐎𝐈𝐍 𝐆𝐂 𝐈𝐍 𝐏𝐑𝐎𝐆𝐑𝐄𝐒𝐒 』\n"
                        f"╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
                        f"📊 *Progress:* {idx}/{total_gcs} Groups\n"
                        f"📌 *Current:* `{chat_name}`\n"
                        f"➕ *Bots Added:* {total_added}\n"
                        f"👑 *Bots Promoted:* {total_promoted}\n"
                        f"⏳ Adding & Promoting in progress..."
                    ),
                    parse_mode="Markdown"
                )
            except Exception: pass

        await client.disconnect()

        summary_text = "\n".join(results_summary[:15])
        await bot.edit_message_text(
            chat_id=chat_id,
            message_id=status_msg_id,
            text=(
                "╔═━─ 𓆩🎉𓆪 ─━═╗\n"
                "『 👑 𝐉𝐎𝐈𝐍 𝐆𝐂 & 𝐀𝐔𝐓𝐎-𝐀𝐃𝐌𝐈𝐍 𝐃𝐎𝐍𝐄 』\n"
                "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
                f"📊 *Total Groups:* {total_gcs}\n"
                f"✅ *Successfully Managed:* {processed_gcs}\n"
                f"➕ *Total Bots Added:* {total_added}\n"
                f"👑 *Total Bots Promoted to Admin:* {total_promoted}\n\n"
                f"📋 *Summary:*\n{summary_text}\n\n"
                "✨ *Saare targeted groups me bots add ho kar ADMIN promote ho chuke hain!* 🚀"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        try:
            await bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_msg_id,
                text=f"❌ Error during Join GC: `{str(e)[:300]}`",
                parse_mode="Markdown"
            )
        except Exception: pass

async def joingc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not user or not is_admin(user.id):
        try: await update.message.reply_text(_OWNER_GATE_MSG)
        except Exception: pass
        return

    raw_text = (update.message.text or "").strip()
    parts = raw_text.split()
    targets = []
    for p in parts[1:]:
        p_clean = p.strip().strip(",")
        if "t.me/" in p_clean or "telegram.me/" in p_clean or p_clean.startswith("@") or p_clean.startswith("+"):
            targets.append(p_clean)
        elif len(p_clean) > 4:
            targets.append(p_clean)

    if not targets and context.args:
        targets = [a.strip() for a in context.args if a.strip()]

    active_bots = [b for b in all_bot_instances if b is not None]
    bot_names = []
    for b in active_bots:
        try:
            b_user = await b.get_me()
            if b_user.username: bot_names.append(f"@{b_user.username}")
        except Exception: pass

    if not targets:
        help_msg = (
            "╔═━─ 𓆩🎯𓆪 ─━═╗\n"
            "『 𝐉𝐎𝐈𝐍 𝐆𝐂 + 𝐀𝐔𝐓𝐎-𝐀𝐃𝐌𝐈𝐍 👑 』\n"
            "╚═━─ 𖤐⚡𖤐 ─━═╝\n\n"
            "📌 *Command:* `/joingc <link1> [link2] ...`\n"
            "📌 *Prefix:* `+joingc <link>` ya `+addgc <link>`\n\n"
            "🚀 *Examples:*\n"
            "• `/joingc https://t.me/+AbCdEfGh123`\n"
            "• `/joingc https://t.me/mygroup1 https://t.me/+privategroup2`\n\n"
            "✨ *Userbot GC ko join karega, saare 9 bots ko add karega, aur sabhi ko Full Rights ke sath ADMIN bana dega!* 🚀"
        )
        await update.message.reply_text(help_msg, parse_mode="Markdown")
        return

    init_msg = await update.message.reply_text(
        "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
        "『 🎯 𝐉𝐎𝐈𝐍 𝐆𝐂 & 𝐀𝐔𝐓𝐎-𝐀𝐃𝐌𝐈𝐍 ⚡ 』\n"
        "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
        f"🔗 *Target GCs:* {len(targets)} Group(s)\n"
        f"🤖 *Fleet Bots:* {len(bot_names)} Bots\n"
        "⏳ *Status:* Initializing Userbot to join and promote all bots...",
        parse_mode="Markdown"
    )
    asyncio.create_task(_do_auto_joingc(context.bot, chat_id, init_msg.message_id, targets, bot_names))

async def folderjoin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    chat_id = update.effective_chat.id
    user = update.effective_user
    if not user or not is_admin(user.id):
        try: await update.message.reply_text(_OWNER_GATE_MSG)
        except Exception: pass
        return

    raw_text = (update.message.text or "").strip()
    parts = raw_text.split()
    link = ""
    for p in parts[1:]:
        if "t.me/" in p or "telegram.me/" in p or p.startswith("@") or "addlist" in p:
            link = p
            break
    if not link and context.args:
        link = context.args[0]

    active_bots = [b for b in all_bot_instances if b is not None]
    bot_buttons = []
    bot_names = []

    for i, b in enumerate(active_bots, 1):
        try:
            b_user = await b.get_me()
            uname = b_user.username
            if uname:
                bot_names.append(f"@{uname}")
                add_url = f"https://t.me/{uname}?startgroup=botstart"
                bot_buttons.append([InlineKeyboardButton(f"➕ Add Bot #{i} (@{uname})", url=add_url)])
        except Exception: pass

    if not link:
        help_msg = (
            "╔═━─ 𓆩📁𓆪 ─━═╗\n"
            "『 𝐙𝐄𝐑𝐎-𝐓𝐎𝐔𝐂𝐇 𝐅𝐎𝐋𝐃𝐄𝐑 𝐉𝐎𝐈𝐍 + 𝐀𝐃𝐌𝐈𝐍 』\n"
            "╚═━─ 𖤐⚡𖤐 ─━═╝\n\n"
            "📌 *Command:* `/folderjoin <folder_link>`\n"
            "📌 *Prefix:* `+folderjoin <folder_link>`\n\n"
            "🚀 *Example:*\n"
            "`/folderjoin https://t.me/addlist/AbCdEfGhIjK`\n\n"
            "✨ *Userbot automatically folder join karega, saare 9 bots ko add karega, aur un sabko ADMIN promote kar dega!*"
        )
        markup = InlineKeyboardMarkup(bot_buttons[:8]) if bot_buttons else None
        await update.message.reply_text(help_msg, reply_markup=markup, parse_mode="Markdown")
        return

    markup = InlineKeyboardMarkup(bot_buttons[:8]) if bot_buttons else None
    init_msg = await update.message.reply_text(
        "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
        "『 📁 𝐙𝐄𝐑𝐎-𝐓𝐎𝐔𝐂𝐇 𝐅𝐎𝐋𝐃𝐄𝐑 𝐉𝐎𝐈𝐍 + 𝐀𝐃𝐌𝐈𝐍 ⚡ 』\n"
        "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
        f"🔗 *Target Folder:* `{link}`\n"
        f"🤖 *Fleet Bots:* {len(active_bots)} Bots\n"
        "⏳ *Status:* Initializing Zero-Touch Auto-Adder & Admin Promoter...",
        reply_markup=markup,
        parse_mode="Markdown"
    )

    asyncio.create_task(_do_auto_folderjoin(context.bot, chat_id, init_msg.message_id, link, bot_names))

async def bots_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    count = len([b for b in all_bot_instances if b is not None])
    await update.message.reply_text(f"🎀 Active bots: {count}\n⏱️ Uptime: {get_uptime()}")

def _extract_base(raw: str, prefixes: tuple, context) -> str:
    for prefix in prefixes:
        if raw.lower().startswith(prefix.lower()):
            return raw[len(prefix):].strip()
    return " ".join(context.args) if context.args else ""

# ══════════════════════════════════════════════════════════════════
#  NC HANDLERS
# ══════════════════════════════════════════════════════════════════
async def randnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+rnc", "💦rnc", "/rnc", "+randnc", "💦randnc", "/randnc"), context)
    if not base: return await update.message.reply_text("Usage: +rnc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    _last = [""]
    def make_name(): return _build_name(base, _last)
    async def nc_loop(stop_event: asyncio.Event):
        await _steadync_engine(chat_id, bots, stop_event, make_name, 0.0)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🎲 𝐑𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")

async def burnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+flamenc", "💦flamenc", "/flamenc", "+burnc", "💦burnc", "/burnc"), context)
    if not base: return await update.message.reply_text("Usage: +flamenc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        sym = random.choice(BURN_SYMS)
        return f"{sym}{base}{sym}{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _ghost_burn_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🔥 𝐅𝐋𝐀𝐌𝐄𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")

async def ohyesnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+ohyesnc", "💦ohyesnc", "/ohyesnc"), context)
    if not base: return await update.message.reply_text("Usage: +ohyesnc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        sym = random.choice(WAVE_SYMBOLS)
        return f"{sym} {base} {sym}{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _relay_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🔄 𝐎𝐇𝐘𝐄𝐒𝐍𝐂 𝐑𝐄𝐋𝐀𝐘 ({len(bots)} bots)\nStop: /stop")

async def aahnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+aahnc", "💦aahnc", "/aahnc"), context)
    if not base: return await update.message.reply_text("Usage: +aahnc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        s1 = random.choice(WAVE_SYMBOLS + BURN_SYMS)
        s2 = random.choice(WAVE_SYMBOLS + BURN_SYMS)
        return f"{s1}{base}{s2}{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _adaptive_burst_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"💥 𝐀𝐀𝐇𝐍𝐂 𝐀𝐃𝐀𝐏𝐓𝐈𝐕𝐄 𝐁𝐔𝐑𝐒𝐓 ({len(bots)} bots)\nStop: /stop")

async def horneync_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+horneync", "💦horneync", "/horneync"), context)
    if not base: return await update.message.reply_text("Usage: +horneync <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        sym = random.choice(WATER_SYMS)
        return f"{sym} {base} {sym}{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _hyperfire_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🌊 𝐇𝐎𝐑𝐍𝐄𝐘𝐍𝐂 𝐇𝐘𝐏𝐄𝐑𝐅𝐈𝐑𝐄 ({len(bots)} bots)\nStop: /stop")

async def purenc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+purenc", "💦purenc", "/purenc"), context)
    if not base: return await update.message.reply_text("Usage: +purenc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    _last = [""]
    def make_name(): return _build_name(base, _last)
    async def nc_loop(stop_event: asyncio.Event):
        await _hyperfire_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"⚡ 𝐏𝐔𝐑𝐄𝐍𝐂 𝐇𝐘𝐏𝐄𝐑𝐅𝐈𝐑𝐄 ({len(bots)} bots)\nStop: /stop")

async def stealthnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+stealthnc", "💦stealthnc", "/stealthnc"), context)
    if not base: return await update.message.reply_text("Usage: +stealthnc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    _last = [""]
    def make_name(): return _build_name(base, _last)
    async def nc_loop(stop_event: asyncio.Event):
        await _stealth_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🥷 𝐒𝐓𝐄𝐀𝐋𝐓𝐇𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")

_LUND_SYMS = ["꒰꒱","꒦꒷","ꗃ","ꖰ","ꗍ","ꗆ","꙰","ꬶ","ꬷ","⌇","🍆","🔥","⚡","💥","🌋","☄️","💣","🗡️","⚔️","🌊"]
async def lundnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+lunanc", "💦lunanc", "/lunanc", "+lundnc", "💦lundnc", "/lundnc"), context)
    if not base: return await update.message.reply_text("Usage: +lunanc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        s1, s2 = random.choice(_LUND_SYMS), random.choice(_LUND_SYMS)
        return f"{s1}{base}{s2}{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _hyperfire_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🌙 𝐋𝐔𝐍𝐀𝐍𝐂 𝐇𝐘𝐏𝐄𝐑𝐅𝐈𝐑𝐄 ({len(bots)} bots)\nStop: /stop")

_BHOSDA_SYMS = ["⸨","⸩","⟦","⟧","⦃","⦄","𓂀","𓃰","𓆏","𓅓","♠","♣","⚜","🔱","⚡","💀","☠️","🖤","🗡️","⚔️"]
async def bhosdanc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+bhosdanc", "💦bhosdanc", "/bhosdanc"), context)
    if not base: return await update.message.reply_text("Usage: +bhosdanc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        s = random.choice(_BHOSDA_SYMS)
        return f"{s}{base}{s}{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _ghost_burn_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"☠️ 𝐁𝐇𝐎𝐒𝐃𝐀𝐍𝐂 𝐆𝐇𝐎𝐒𝐓 ({len(bots)} bots)\nStop: /stop")

_AREY_SYMS = ["¿","¡","✧","˚","⊹","₊","🫦","😏","😈","👀","💅","🤌","👁️","🎭","🎪","🎯"]
async def areync_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+areync", "💦areync", "/areync"), context)
    if not base: return await update.message.reply_text("Usage: +areync <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        s1, s2 = random.choice(_AREY_SYMS), random.choice(_AREY_SYMS)
        return f"{s1} {base} {s2}{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _steadync_engine(chat_id, bots, stop_event, make_name, 0.0)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"😏 𝐀𝐑𝐄𝐘𝐍𝐂 𝐓𝐀𝐔𝐍𝐓 ({len(bots)} bots)\nStop: /stop")

_HAT_SYMS = ["𓂀","𓃰","𓆏","𓅓","☠️","💀","🖤","🗡️","⚔️","🔪","⚰️","🩸","🕯️","🌑"]
async def hatnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+hatnc", "💦hatnc", "/hatnc"), context)
    if not base: return await update.message.reply_text("Usage: +hatnc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    _last = [""]
    def make_name(): return _build_name(base, _last)
    async def nc_loop(stop_event: asyncio.Event):
        await _stealth_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🖤 𝐇𝐀𝐓𝐍𝐂 𝐒𝐓𝐄𝐀𝐋𝐓𝐇 ({len(bots)} bots)\nStop: /stop")

_CRY_SYMS = ["😭","💔","🥺","🥹","😢","😞","😔","😿","🌧️","❄️","🌊","💧","🫧","☁️"]
async def crync_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+😭nc", "💦😭nc", "+crync", "💦crync", "/crync"), context)
    if not base: return await update.message.reply_text("Usage: +crync <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        s1, s2 = random.choice(_CRY_SYMS), random.choice(_CRY_SYMS)
        return f"😭{s1}{base}{s2}😭{make_suffix()}"[:255]
    async def nc_loop(stop_event: asyncio.Event):
        await _steadync_engine(chat_id, bots, stop_event, make_name, 0.0)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"😭 𝐂𝐑𝐘𝐍𝐂 𝐄𝐌𝐎 𝐌𝐎𝐃𝐄 ({len(bots)} bots)\nStop: /stop")

_PERSONAL_SYMS = ["꒰","꒱","꒦","꒷","ꗃ","ꖰ","꙰","⌇","⟦","⟧","⸨","⸩","◈","꩜","⌬","⍟","🔥","💥","⚡","☄️","💀","🖤","🗡️","⚔️"]
def _make_personal_nc_handler(cmd_names, taunt: str, label: str, engine="hyperfire"):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not is_admin(update.effective_user.id): return
        if not update.effective_chat or not update.message or not _is_primary_bot(context): return
        raw = (update.message.text or "").strip()
        base = _extract_base(raw, cmd_names, context)
        if not base: return await update.message.reply_text(f"Usage: {cmd_names[0]} <text>")
        chat_id = update.effective_chat.id
        bots = get_bots_for_chat(chat_id, context.bot)
        _last = [""]
        def make_name():
            s1, s2 = random.choice(_PERSONAL_SYMS), random.choice(_PERSONAL_SYMS)
            c = f"{s1}{base} {taunt}{s2}{make_suffix()}"[:255]
            if c != _last[0]: _last[0] = c
            return c
        if engine == "hyperfire":
            async def nc_loop(stop_event): await _hyperfire_engine(chat_id, bots, stop_event, make_name)
        elif engine == "ghost":
            async def nc_loop(stop_event): await _ghost_burn_engine(chat_id, bots, stop_event, make_name)
        else:
            async def nc_loop(stop_event): await _stealth_engine(chat_id, bots, stop_event, make_name)
        await task_controller.start_task(chat_id, "nc", nc_loop)
        await update.message.reply_text(f"💦 {label} 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")
    return handler

arnavnc_handler = _make_personal_nc_handler(("+mentalnc","💦mentalnc","/mentalnc","+arnavnc","💦arnavnc","/arnavnc"), "༶•┈┈⛧𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋 𝐌𝐎𝐃𝐄┈♛", "𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋", "hyperfire")
kentonc_handler = _make_personal_nc_handler(("+amritnc","💦amritnc","/amritnc","+kentonc","💦kentonc","/kentonc"), "༶•┈┈⛧𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋 𝐌𝐎𝐃𝐄┈♛", "𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋", "ghost")
cr7nc_handler    = _make_personal_nc_handler(("+amritxnc","💦amritxnc","/amritxnc","+cr7nc","💦cr7nc","/cr7nc"), "༶•┈┈⛧𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋 𝐌𝐎𝐃𝐄┈♛", "𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋", "stealth")

async def tripnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+tripnc", "💦tripnc", "/tripnc"), context)
    if not base: return await update.message.reply_text("Usage: +tripnc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    _last = [""]
    def make_name(): return _build_name(base, _last)
    async def nc_loop(stop_event: asyncio.Event):
        await _trio_rotate_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🔄 𝐓𝐑𝐈𝐏𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")

async def ultranc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+ultranc", "💦ultranc", "/ultranc"), context)
    if not base: return await update.message.reply_text("Usage: +ultranc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    _last = [""]
    def make_name(): return _ultra_name(base, _last)
    async def nc_loop(stop_event: asyncio.Event):
        await _ultra_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"⚡ 𝐔𝐋𝐓𝐑𝐀𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")

async def pairnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+pairnc", "💦pairnc", "/pairnc"), context)
    if not base: return await update.message.reply_text("Usage: +pairnc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    _last = [""]
    def make_name(): return _ultra_name(base, _last)
    async def nc_loop(stop_event: asyncio.Event):
        await _pair_rotate_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"👥 𝐏𝐀𝐈𝐑𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")

# ══════════════════════════════════════════════════════════════════
#  FONT MAPS & STYLED NCS
# ══════════════════════════════════════════════════════════════════
def _make_font_map(upper_start, lower_start, digit_start=None):
    m = {}
    for i in range(26):
        m[chr(ord('A') + i)] = chr(upper_start + i)
        m[chr(ord('a') + i)] = chr(lower_start + i)
    if digit_start:
        for i in range(10): m[chr(ord('0') + i)] = chr(digit_start + i)
    return m

_BOLD_MAP       = _make_font_map(0x1D400, 0x1D41A, 0x1D7CE)
_ITALIC_MAP     = _make_font_map(0x1D608, 0x1D622)
_CURSIVE_MAP    = _make_font_map(0x1D4D0, 0x1D4EA)
_BUBBLE_UPPER   = "ⒶⒷⒸⒹⒺⒻⒼⒽⒾⒿⓀⓁⓂⓃⓄⓅⓆⓇⓈⓉⓊⓋⓌⓍⓎⓏ"
_BUBBLE_LOWER   = "ⓐⓑⓒⓓⓔⓕⓖⓗⓘⓙⓚⓛⓜⓝⓞⓟⓠⓡⓢⓣⓤⓥⓦⓧⓨⓩ"
_BUBBLE_MAP     = {chr(ord('A')+i): _BUBBLE_UPPER[i] for i in range(26)}
_BUBBLE_MAP.update({chr(ord('a')+i): _BUBBLE_LOWER[i] for i in range(26)})
_SMALLCAPS_MAP  = dict(zip("abcdefghijklmnopqrstuvwxyz", "ᴀʙᴄᴅᴇꜰɢʜɪᴊᴋʟᴍɴᴏᴘqʀꜱᴛᴜᴠᴡxʏᴢ"))
_FLIP_MAP       = dict(zip("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,!?", "ɐqɔpǝɟƃɥıɾʞlɯuodbɹsʇnʌʍxʎzɐqɔpǝɟƃɥıɾʞlɯuodbɹsʇnʌʍxʎz0ƖᄅƐㄣϛ9ㄥ86'˙¡¿"))

def _apply_font(text: str, fmap: dict) -> str: return "".join(fmap.get(c, c) for c in text)
def _flip_text(text: str) -> str: return "".join(_FLIP_MAP.get(c, c) for c in reversed(text))

def _make_font_nc_handler(cmd_names: tuple, font_fn, label: str, emoji: str):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not is_admin(update.effective_user.id): return
        if not update.effective_chat or not update.message or not _is_primary_bot(context): return
        raw = (update.message.text or "").strip()
        base = _extract_base(raw, cmd_names, context)
        if not base: return await update.message.reply_text(f"Usage: {cmd_names[0]} <text>")
        chat_id = update.effective_chat.id
        bots = get_bots_for_chat(chat_id, context.bot)
        _last = [""]
        def make_name(): return _build_name(font_fn(base), _last)
        async def nc_loop(stop_event): await _steadync_engine(chat_id, bots, stop_event, make_name, 0.0)
        await task_controller.start_task(chat_id, "nc", nc_loop)
        await update.message.reply_text(f"{emoji} {label} 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")
    return handler

boldnc_handler      = _make_font_nc_handler(("+boldnc","💦boldnc"), lambda t: _apply_font(t, _BOLD_MAP), "𝐁𝐎𝐋𝐃𝐍𝐂", "🖤")
italicnc_handler    = _make_font_nc_handler(("+italicnc","💦italicnc"), lambda t: _apply_font(t, _ITALIC_MAP), "𝐈𝐓𝐀𝐋𝐈𝐂𝐍𝐂", "💫")
cursivenc_handler   = _make_font_nc_handler(("+cursivenc","💦cursivenc"), lambda t: _apply_font(t, _CURSIVE_MAP), "𝐂𝐔𝐑𝐒𝐈𝐕𝐄𝐍𝐂", "✍️")
bubblenc_handler    = _make_font_nc_handler(("+bubblenc","💦bubblenc"), lambda t: _apply_font(t, _BUBBLE_MAP), "𝐁𝐔𝐁𝐁𝐋𝐄𝐍𝐂", "🫧")
smallcapsnc_handler = _make_font_nc_handler(("+smallcapsnc","💦smallcapsnc"), lambda t: _apply_font(t.lower(), _SMALLCAPS_MAP), "ꜱᴍᴀʟʟᴄᴀᴘꜱɴ𝐂", "🔡")
flipnc_handler      = _make_font_nc_handler(("+flipnc","💦flipnc"), _flip_text, "𝐅𝐋𝐈𝐏𝐍𝐂", "🙃")

# ══════════════════════════════════════════════════════════════════
#  ANIMATION & TROLL COMMANDS
# ══════════════════════════════════════════════════════════════════
async def loading_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message or not update.effective_chat: return
    msg = await update.message.reply_text("⏳ Loading…")
    bar_frames = ["▱▱▱▱▱▱▱▱▱▱  0%", "▰▰▱▱▱▱▱▱▱▱ 20%", "▰▰▰▰▱▱▱▱▱▱ 40%", "▰▰▰▰▰▰▱▱▱▱ 60%", "▰▰▰▰▰▰▰▰▱▱ 80%", "▰▰▰▰▰▰▰▰▰▰ 100% ✅"]
    for frame in bar_frames:
        try:
            await msg.edit_text(f"⚡ 💦 𝐋𝐎𝐀𝐃𝐈𝐍𝐆\n{frame}")
            await asyncio.sleep(0.4)
        except Exception: break
    await asyncio.sleep(0.5)
    try: await msg.edit_text("✅ 🧠 𝐋𝐎𝐀𝐃 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄!\n⚡ 𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋 𝐑𝐄𝐀𝐃𝐘 ⚡")
    except Exception: pass

async def countdown_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    n = 5
    if context.args:
        try: n = min(int(context.args[0]), 20)
        except ValueError: pass
    msg = await update.message.reply_text(f"⏱️ 𝐂𝐎𝐔𝐍𝐓𝐃𝐎𝐖𝐍: {n}")
    for i in range(n, 0, -1):
        try:
            await msg.edit_text(f"⏱️ 𝐂𝐎𝐔𝐍𝐓𝐃𝐎𝐖𝐍\n{'🟥'*i}{'⬛'*(n-i)}\n{i} seconds…")
            await asyncio.sleep(1)
        except Exception: break
    try: await msg.edit_text("💥 💦 𝐁𝐎𝐎𝐌! TIME'S UP! 🔥")
    except Exception: pass

async def typewrite_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+typewrite","💦typewrite"), context)
    if not base: return await update.message.reply_text("Usage: +typewrite <text>")
    msg = await update.message.reply_text("✍️")
    typed = ""
    for ch in base:
        typed += ch
        try:
            await msg.edit_text(f"✍️ {typed}▌")
            await asyncio.sleep(0.1)
        except Exception: pass
    try: await msg.edit_text(f"✅ {typed}")
    except Exception: pass

async def spinner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    frames = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
    msg = await update.message.reply_text("⠋")
    for i in range(15):
        try:
            await msg.edit_text(f"{frames[i % len(frames)]} ⚡ 𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋 {frames[i % len(frames)]}")
            await asyncio.sleep(0.2)
        except Exception: break
    try: await msg.edit_text("✅ 🧠 AMRIT MENTAL — FULLY LOADED")
    except Exception: pass

async def glitch_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+glitch","💦glitch"), context)
    if not base: return await update.message.reply_text("Usage: +glitch <text>")
    glitch_chars = "̴̵̶̷̸̡̢̧̨̩̪̫̬̭̮̯̰̱̲̳"
    msg = await update.message.reply_text(base)
    for _ in range(5):
        corrupted = "".join(c + (random.choice(glitch_chars) if random.random() < 0.4 else "") for c in base)
        try:
            await msg.edit_text(f"⚡ {corrupted} ⚡")
            await asyncio.sleep(0.18)
        except Exception: break
    try: await msg.edit_text(f"⚡ {base} ⚡")
    except Exception: pass

def _get_mention(update: Update, context) -> str:
    if context.args: return context.args[0] if context.args[0].startswith("@") else f"@{context.args[0]}"
    if update.message and update.message.reply_to_message and update.message.reply_to_message.from_user:
        u = update.message.reply_to_message.from_user
        return f"@{u.username}" if u.username else u.first_name
    return "User"


# ==================================================================
#  DHASU FEATURES: TEMPMAIL, ROLLCALL, BODYGUARD, IQ, ROAST, STEALTHLOCK
# ==================================================================

BODYGUARD_FILE = "bodyguard_chats.json"
bodyguard_chats = set()

def load_bodyguard_chats():
    try:
        if os.path.exists(BODYGUARD_FILE):
            with open(BODYGUARD_FILE, "r") as f:
                return set(json.load(f))
    except Exception: pass
    return set()

def save_bodyguard_chats():
    try:
        with open(BODYGUARD_FILE, "w") as f:
            json.dump(list(bodyguard_chats), f)
    except Exception: pass

bodyguard_chats = load_bodyguard_chats()

# 1. TEMPMAIL ENGINE (Instant In-Telegram Disposable Email + OTP)
async def tempmail_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    
    email = None
    try:
        req = urllib.request.Request(
            "https://api.internal.temp-mail.io/api/v3/email/new",
            data=b"{}",
            headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=7) as resp:
            data = json.loads(resp.read().decode())
            email = data.get("email")
    except Exception:
        pass
    
    if not email:
        rnd = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
        email = f"{rnd}@ruutukf.com"
        
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Check Inbox / OTP", callback_data=f"tmail:check:{email}")],
        [InlineKeyboardButton("📋 Generate New Email", callback_data="tmail:new")],
        [InlineKeyboardButton("❌ Close", callback_data="tmail:close")]
    ])
    
    text = (
        "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
        "『𓍼ֶָ֢˖ ࣪ꨄ 𝐀𝐌𝐑𝐈𝐓 𝐗 𝐌𝐄𝐍𝐓𝐀𝐋 𝐓𝐄𝐌𝐏𝐌𝐀𝐈𝐋 .་༘࿐』\n"
        "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
        "📬 <b>Your Disposable Email:</b>\n"
        f"<code>{email}</code>\n\n"
        "💡 <i>Copy this email and use it on any service/app.</i>\n"
        "Click the button below to fetch incoming OTPs & messages!"
    )
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)

async def checkmail_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    args = context.args or []
    email = args[0].strip() if args else None
    if not email:
        await update.message.reply_text("Usage: /checkmail <email_address>\nOr simply use /tempmail directly.")
        return
    await _check_email_inbox(update.effective_chat.id, email, update.message.message_id, context.bot)

async def _check_email_inbox(chat_id: int, email: str, msg_id: Optional[int], bot, edit_msg=None):
    messages = []
    try:
        req = urllib.request.Request(
            f"https://api.internal.temp-mail.io/api/v3/email/{email}/messages",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=7) as resp:
            messages = json.loads(resp.read().decode())
    except Exception:
        messages = []

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔄 Refresh Inbox", callback_data=f"tmail:check:{email}")],
        [InlineKeyboardButton("📋 New Email", callback_data="tmail:new")],
        [InlineKeyboardButton("❌ Close", callback_data="tmail:close")]
    ])

    if not messages:
        res = (
            "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
            "『𓍼ֶָ֢˖ ࣪ꨄ 𝐈𝐍𝐁𝐎𝐗 𝐒𝐓𝐀𝐓𝐔𝐒 .་༘࿐』\n"
            "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
            f"📬 <b>Email:</b> <code>{email}</code>\n"
            "📭 <i>Inbox is empty. Waiting for incoming OTP / email...</i>\n"
            f"🕒 Checked At: <code>{time.strftime('%H:%M:%S')}</code>"
        )
    else:
        mail_blocks = []
        for m in messages[:4]:
            sender = m.get("from", "Unknown")
            subject = m.get("subject", "No Subject")
            body = (m.get("body_text") or "").strip()
            
            otp_match = re.search(r"\b([0-9]{4,8})\b", subject + " " + body)
            otp_str = f"🔑 <b>Detected OTP:</b> <code>{otp_match.group(1)}</code>\n" if otp_match else ""
            
            preview = body[:120].replace("<", "&lt;").replace(">", "&gt;")
            mail_blocks.append(
                f"👤 <b>From:</b> <code>{sender}</code>\n"
                f"📌 <b>Subject:</b> {subject}\n"
                f"{otp_str}"
                f"📄 <b>Preview:</b> <i>{preview}...</i>"
            )
        
        res = (
            "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
            "『𓍼ֶָ֢˖ ࣪ꨄ 𝐍𝐄𝐖 𝐄𝐌𝐀𝐈𝐋𝐒 𝐑𝐄𝐂𝐄𝐈𝐕𝐄𝐃 .་༘࿐』\n"
            "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
            f"📬 <b>Email:</b> <code>{email}</code>\n"
            f"📩 <b>Total Messages:</b> {len(messages)}\n\n"
            + "\n\n─────────────────\n\n".join(mail_blocks)
        )

    if edit_msg:
        try:
            await edit_msg.edit_text(res, parse_mode="HTML", reply_markup=kb)
            return
        except Exception: pass
    
    await bot.send_message(chat_id, res, parse_mode="HTML", reply_markup=kb)

async def tempmail_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query: return
    data = query.data or ""
    await query.answer()
    
    if data == "tmail:close":
        try: await query.message.delete()
        except Exception: pass
        return
        
    if data == "tmail:new":
        email = None
        try:
            req = urllib.request.Request(
                "https://api.internal.temp-mail.io/api/v3/email/new",
                data=b"{}",
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"}
            )
            with urllib.request.urlopen(req, timeout=7) as resp:
                data_json = json.loads(resp.read().decode())
                email = data_json.get("email")
        except Exception: pass
        if not email:
            rnd = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
            email = f"{rnd}@ruutukf.com"
            
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Check Inbox / OTP", callback_data=f"tmail:check:{email}")],
            [InlineKeyboardButton("📋 Generate New Email", callback_data="tmail:new")],
            [InlineKeyboardButton("❌ Close", callback_data="tmail:close")]
        ])
        text = (
            "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
            "『𓍼ֶָ֢˖ ࣪ꨄ 𝐀𝐌𝐑𝐈𝐓 𝐗 𝐌𝐄𝐍𝐓𝐀𝐋 𝐓𝐄𝐌𝐏𝐌𝐀𝐈𝐋 .་༘࿐』\n"
            "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
            "📬 <b>Your Disposable Email:</b>\n"
            f"<code>{email}</code>\n\n"
            "💡 <i>Copy this email and use it on any service/app.</i>\n"
            "Click the button below to fetch incoming OTPs & messages!"
        )
        try: await query.message.edit_text(text, parse_mode="HTML", reply_markup=kb)
        except Exception: pass
        return
        
    if data.startswith("tmail:check:"):
        email = data.split("tmail:check:", 1)[1]
        await _check_email_inbox(query.message.chat_id, email, query.message.message_id, context.bot, edit_msg=query.message)

# 2. MILITARY ROLL-CALL
async def rollcall_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user: return
    if not is_admin(update.effective_user.id): return
    
    status_msg = await update.message.reply_text("⚡ <b>[FLEET PROTOCOL]</b> <i>Initiating Military Roll-Call across all units...</i>", parse_mode="HTML")
    
    fleet = all_bot_instances if all_bot_instances else [context.bot]
    unit_reports = []
    
    t_start = time.time()
    for idx, b in enumerate(fleet[:10], start=1):
        t0 = time.time()
        try:
            me = await b.get_me()
            ping_ms = int((time.time() - t0) * 1000)
            uname = f"@{me.username}" if me.username else (me.first_name or f"Bot #{idx}")
            unit_reports.append(f"│ ✦ <b>[Unit {idx:02d}]</b> {uname} — 🟢 <b>ONLINE</b> ({ping_ms}ms)")
        except Exception:
            unit_reports.append(f"│ 𖤐 <b>[Unit {idx:02d}]</b> Bot #{idx} — 🔴 <i>RESTRICTED</i>")
        await asyncio.sleep(0.08)
        
    total_time = int((time.time() - t_start) * 1000)
    
    report_text = (
        "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
        "『𓍼ֶָ֢˖ ࣪ꨄ 𝐅𝐋𝐄𝐄𝐓 𝐑𝐎𝐋𝐋-𝐂𝐀𝐋𝐋 𝐈𝐍𝐒𝐏𝐄𝐂𝐓𝐈𝐎𝐍 .་༘࿐』\n"
        "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
        "╭━━━𓆩 🎖️ 𝐔𝐍𝐈𝐓 𝐒𝐓𝐀𝐓𝐔𝐒 𓆪━━━╮\n"
        + "\n".join(unit_reports) + "\n"
        "╰━━━༺❀༻━━━╯\n"
        "👑 <b>Fleet Command:</b> <code>AMRIT X MENTAL</code>\n"
        f"⚡ <b>Active Units:</b> {len(unit_reports)} / {len(fleet)}\n"
        f"📶 <b>Fleet Latency:</b> {total_time}ms | <b>Uptime:</b> {get_uptime()}\n"
        "𖤐 <b>Mode:</b> <i>Autonomous Synchronized Protocol</i> 𖤐"
    )
    try:
        await status_msg.edit_text(report_text, parse_mode="HTML")
    except Exception:
        await update.message.reply_text(report_text, parse_mode="HTML")

# 3. BODYGUARD PROTOCOL
async def bodyguard_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user: return
    if not is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    
    args = context.args or []
    sub = args[0].lower() if args else ""
    
    if sub == "on":
        bodyguard_chats.add(chat_id)
        save_bodyguard_chats()
        await update.message.reply_text("🛡️ <b>BODYGUARD PROTOCOL ACTIVATED</b> 👑\n\n<i>Boss Amrit is now shielded. Any disrespectful message or attack towards the Admin will trigger immediate Fleet retaliation!</i>", parse_mode="HTML")
    elif sub == "off":
        bodyguard_chats.discard(chat_id)
        save_bodyguard_chats()
        await update.message.reply_text("🔓 <b>Bodyguard Protocol Deactivated</b> in this group.")
    else:
        st = "🟢 <b>ACTIVE</b>" if chat_id in bodyguard_chats else "🔴 <b>DISABLED</b>"
        await update.message.reply_text(f"🛡️ <b>Bodyguard Status:</b> {st}\n\nUsage: <code>/bodyguard on</code> or <code>/bodyguard off</code>\n(Or use <code>+bodyguard on</code>)", parse_mode="HTML")

# 4. IQ BRAINWAVE SCANNER
async def iq_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    target = _get_mention(update, context)
    
    scan_msg = await update.message.reply_text(f"🧠 <b>[NEURAL SCAN]</b> Initializing brainwave probe on {target}...", parse_mode="HTML")
    
    stages = [
        f"🧠 <b>Scanning Synapses for {target}...</b>\n<code>[ █▒▒▒▒▒▒▒▒▒ ] 14% Connecting Neurons...</code>",
        f"🧠 <b>Scanning Synapses for {target}...</b>\n<code>[ ████▒▒▒▒▒▒ ] 48% Measuring Common Sense...</code>",
        f"🧠 <b>Scanning Synapses for {target}...</b>\n<code>[ ████████▒▒ ] 82% Detecting Meme Overload...</code>",
    ]
    for s in stages:
        try:
            await scan_msg.edit_text(s, parse_mode="HTML")
            await asyncio.sleep(0.7)
        except Exception: break

    iq_options = [
        (-45, "Certified Potato 🥔", "Bhai dimaag download karna bhool gaya tha kya?", "0%"),
        (-12, "Chirkut Max 🐒", "Subah uth ke breathing exercise karo pehle.", "4%"),
        (25, "Room Temperature IQ 🧊", "Calculator bhi isse tez sochta hai.", "18%"),
        (78, "Average Keyboard Warrior ⌨️", "Chhoti baaton par lamba bhashan dena specialty hai.", "45%"),
        (135, "Street Smart Savage 🕶️", "Baaton se palatne me PhD ki hui hai.", "75%"),
        (190, "Galactic Genius 🧠⚡", "NASA wale secret search kar rahe hain is bande ko.", "92%"),
        (260, "God-Tier Mental Overlord 👑", "AMRIT X MENTAL certified mastermind!", "100%"),
    ]
    score, title, quote, meter = random.choice(iq_options)

    final_card = (
        "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
        "『𓍼ֶָ֢˖ ࣪ꨄ 𝐁𝐑𝐀𝐈𝐍𝐖𝐀𝐕𝐄 𝐈𝐐 𝐑𝐄𝐏𝐎𝐑𝐓 .་༘࿐』\n"
        "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
        f"👤 <b>Subject:</b> {target}\n"
        f"⚡ <b>IQ Score:</b> <code>{score}</code>\n"
        f"🏷️ <b>Classification:</b> <b>{title}</b>\n"
        f"📊 <b>Brain Capacity:</b> <code>{meter}</code>\n\n"
        f"💬 <b>Verdict:</b> <i>\"{quote}\"</i>\n\n"
        "┈┉┅━❀꧁ 𓆩♡𓆪 ꧂❀━┅┉┈\n"
        "⋆｡°✩ ❝ Scanned by AMRIT X MENTAL ❞ ✩°｡⋆"
    )
    try:
        await scan_msg.edit_text(final_card, parse_mode="HTML")
    except Exception:
        await update.message.reply_text(final_card, parse_mode="HTML")

# 5. SAVAGE ROAST GENERATOR
ROAST_LIST = [
    "Aapki baatein sun ke lagta hai, dimaag ko airplane mode pe daal ke ghoom rahe ho.",
    "Bhai thoda dimaag use kar liya karo, free me milta hai koi EMI nahi bharni padti.",
    "Aapka existence dekh ke lagta hai ki evolution ne bhi ek din leave le li thi.",
    "Aapko roast karne ki zaroorat nahi hai, mirror hi kaafi hai aapke liye.",
    "Itna confidence kahan se laate ho bina kisi basic talent ke?",
    "Aapki baatein sun ke dictionary ke sabhi shabd suicide karne lagte hain.",
    "Bhai silent mode pe raha karo, chat ka standard badh jayega.",
    "Aapko dekh ke lagta hai ki Google Maps bhi aapko aukaat dikha dega.",
    "Aapke logic se zyada fast toh 2G internet chalta hai.",
    "Jitna dimaag aap lagate ho na, utne me toh machhar bhi nahi phansta.",
    "Aapki baatein sunne se behtar insan traffic jam me horn sune.",
    "Bhai thoda pause liya karo, keyboard ko bhi thoda aaram chahiye faltu baaton se.",
    "Aapka IQ aur meri battery percentage ka muqabla ho toh battery jeet jayegi.",
    "Aapko dekh ke lagta hai bhagwan ne backup file galat load kar di thi.",
    "Aapke jokes sun ke hasi nahi aati, bas taras aata hai.",
    "Jahan akal bant rahi thi, wahan aap shayad excuse dhundh rahe the.",
    "Aapka opinion bilkul free software jaisa hai—kisi ko nahi chahiye!",
    "Bhai dimaag ke mamle me aap dry day par ho.",
    "Aapki baaton me utna hi dum hai jitna expired Paracetamol me hota hai.",
    "Shaant baitho bhai, chat ki oxygen waste mat karo.",
]

async def roast_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message: return
    target = _get_mention(update, context)
    roast_line = random.choice(ROAST_LIST)
    
    roast_card = (
        "╔═━─ 𓆩⚡𓆪 ─━═╗\n"
        "『𓍼ֶָ֢˖ ࣪ꨄ 𝐒𝐀𝐕𝐀𝐆𝐄 𝐕𝐈𝐏 𝐑𝐎𝐀𝐒𝐓 .་༘࿐』\n"
        "╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
        f"🎯 <b>Target:</b> {target}\n\n"
        f"🔥 <i>\"{roast_line}\"</i> 🔥\n\n"
        "┈┉┅━❀꧁ 𓆩♡𓆪 ꧂❀━┅┉┈\n"
        "⋆｡°✩ ❝ 𝐃ᴇꜱɪɢɴᴇᴅ ꜰᴏʀ 𝐀ᴍʀɪᴛ 𝐗 𝐌ᴇɴᴛᴀʟ ❞ ✩°｡⋆"
    )
    await update.message.reply_text(roast_card, parse_mode="HTML")

# 6. STEALTH LOCK
async def stealthlock_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_user: return
    if not is_admin(update.effective_user.id): return
    chat = update.effective_chat
    if not chat or chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("This command can only be used in groups/supergroups.")
        return

    try: await update.message.delete()
    except Exception: pass

    args = context.args or []
    sub = args[0].lower() if args else "toggle"

    if sub == "off" or sub == "unlock":
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_audios=True,
            can_send_documents=True,
            can_send_photos=True,
            can_send_videos=True,
            can_send_video_notes=True,
            can_send_voice_notes=True,
            can_send_other_messages=True,
            can_add_web_page_previews=True,
        )
        msg_text = "🔓 <b>Stealth Lock Disabled:</b> All media & message permissions restored."
    else:
        perms = ChatPermissions(
            can_send_messages=True,
            can_send_audios=False,
            can_send_documents=False,
            can_send_photos=False,
            can_send_videos=False,
            can_send_video_notes=False,
            can_send_voice_notes=False,
            can_send_other_messages=False,
            can_add_web_page_previews=False,
        )
        msg_text = "🥷 <b>Stealth Lock Activated:</b> Media, stickers, GIFs & link previews silently restricted for members."

    try:
        await context.bot.set_chat_permissions(chat.id, perms)
        status_msg = await context.bot.send_message(chat.id, msg_text, parse_mode="HTML")
        await asyncio.sleep(5)
        try: await status_msg.delete()
        except Exception: pass
    except Exception as e:
        await context.bot.send_message(chat.id, f"⚠️ StealthLock error: {e}")


async def fakeban_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    target = _get_mention(update, context)
    msg = await update.message.reply_text(f"🚨 BAN INITIATED for {target}")
    steps = [
        f"🔴 💦 𝐁𝐀𝐍 𝐒𝐘𝐒𝐓𝐄𝐌\n👤 Target: {target}\n🔎 Scanning profile…",
        f"🔴 💦 𝐁𝐀𝐍 𝐒𝐘𝐒𝐓𝐄𝐌\n👤 Target: {target}\n⏳ Banning in 2…",
        f"💀 𝐁𝐀𝐍 𝐄𝐗𝐄𝐂𝐔𝐓𝐄𝐃\n👤 {target} permanently banned.\n🚫 Cannot rejoin.",
    ]
    for step in steps:
        try:
            await msg.edit_text(step)
            await asyncio.sleep(1.0)
        except Exception: break
    await asyncio.sleep(1.5)
    try: await msg.edit_text(f"😂😂😂 𝐋𝐎𝐋 𝐉𝐔𝐒𝐓 𝐊𝐈𝐃𝐃𝐈𝐍𝐆! 😂😂😂\n💦 {target} AMRIT MENTAL troll tha!")
    except Exception: pass

async def fakekick_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    target = _get_mention(update, context)
    msg = await update.message.reply_text(f"👟 Kicking {target}…")
    await asyncio.sleep(1.0)
    try: await msg.edit_text(f"💥 𝐊𝐈𝐂𝐊𝐄𝐃! {target} has been removed.")
    except Exception: pass
    await asyncio.sleep(1.5)
    try: await msg.edit_text(f"🤣 𝐅𝐀𝐊𝐄 𝐊𝐈𝐂𝐊! {target} tu abhi bhi yahan hai LMAO")
    except Exception: pass

async def fakewarn_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    target = _get_mention(update, context)
    msg = await update.message.reply_text(f"⚠️ 𝐖𝐀𝐑𝐍𝐈𝐍𝐆: {target} [1/3]\nNext = BAN")
    await asyncio.sleep(1.5)
    try: await msg.edit_text(f"😂 Fake warn tha {target} mast troll tha!")
    except Exception: pass

async def fakedm_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    target = _get_mention(update, context)
    msg = await update.message.reply_text(f"📨 Alert sent to {target} DM.")
    await asyncio.sleep(1.5)
    try: await msg.edit_text(f"😂 Koi DM nahi gaya {target} troll tha!")
    except Exception: pass

async def matrixtroll_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message: return
    target = _get_mention(update, context)
    msg = await update.message.reply_text("💻 Hacking…")
    chars = "01010101XYZ99"
    for i in range(4):
        try:
            line = "".join(random.choice(chars) for _ in range(12))
            await msg.edit_text(f"💻 𝐇𝐀𝐂𝐊𝐈𝐍𝐆 {target}\n`{line}`\nProgress: {(i+1)*25}%")
            await asyncio.sleep(0.3)
        except Exception: break
    try: await msg.edit_text(f"☠️ 𝐇𝐀𝐂𝐊 𝐂𝐎𝐌𝐏𝐋𝐄𝐓𝐄! Just kidding bro 😂")
    except Exception: pass

# ══════════════════════════════════════════════════════════════════
#  BLITZ NC PRESETS & MENTAL 1-10
# ══════════════════════════════════════════════════════════════════
_INFERNO_SYMS  = ["🔥","🌋","💥","☄️","🌩️","🌪️","💣","🔴","🟠"]
_VOID_SYMS     = ["🌑","🖤","☠️","💀","🌚","🌘","👁️","🩸"]
_STORM_SYMS    = ["⚡","🌩️","🌪️","🌊","🌀","🌧️","❄️"]
_BLOOD_SYMS    = ["🩸","💀","🗡️","⚔️","🔪","❤️‍🩹","☠️"]
_DIVINE_SYMS   = ["👑","⚜","🔱","✨","💎","🌟","⭐","🌙"]

def _make_blitz_nc_handler(cmd_names: tuple, sym_pool: list, label: str):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not is_admin(update.effective_user.id): return
        if not update.effective_chat or not update.message or not _is_primary_bot(context): return
        raw = (update.message.text or "").strip()
        base = _extract_base(raw, cmd_names, context)
        if not base: return await update.message.reply_text(f"Usage: {cmd_names[0]} <text>")
        chat_id = update.effective_chat.id
        bots = get_bots_for_chat(chat_id, context.bot)
        _last = [""]
        def make_name():
            e1, e2 = random.choice(sym_pool), random.choice(sym_pool)
            return f"{e1}{base}{e2}{make_suffix()}"[:255]
        async def nc_loop(stop_event): await _blitz_engine(chat_id, bots, stop_event, make_name)
        await task_controller.start_task(chat_id, "nc", nc_loop)
        await update.message.reply_text(f"⚡ {label} 𝐁𝐋𝐈𝐓𝐙 ({len(bots)} bots)\nStop: /stop")
    return handler

infernc_handler  = _make_blitz_nc_handler(("+infernc","💦infernc","/infernc"), _INFERNO_SYMS, "🔥𝐈𝐍𝐅𝐄𝐑𝐍𝐂")
voidnc_handler   = _make_blitz_nc_handler(("+voidnc","💦voidnc","/voidnc"), _VOID_SYMS, "🌑𝐕𝐎𝐈𝐃𝐍𝐂")
stormnc_handler  = _make_blitz_nc_handler(("+stormnc","💦stormnc","/stormnc"), _STORM_SYMS, "⚡𝐒𝐓𝐎𝐑𝐌𝐍𝐂")
bloodnc_handler  = _make_blitz_nc_handler(("+bloodnc","💦bloodnc","/bloodnc"), _BLOOD_SYMS, "🩸𝐁𝐋𝐎𝐎𝐃𝐍𝐂")
divinenc_handler = _make_blitz_nc_handler(("+divinenc","💦divinenc","/divinenc"), _DIVINE_SYMS, "👑𝐃𝐈𝐕𝐈𝐍𝐄𝐍𝐂")

_MENTAL_POOLS = [
    ["🔥","💥","🌋","☄️","🔴"],
    ["⚡","🌩️","💫","✨","🌟"],
    ["💀","☠️","🌑","🖤","🕷️"],
    ["🌊","💧","🌀","🫧","🐚"],
    ["👑","⚜","🔱","💎","🏆"],
    ["🐉","🐍","🌋","🔱","⚡"],
    ["🩸","🗡️","⚔️","🔪","☠️"],
    ["💎","🔷","🔹","💠","✨"],
    ["🌑","🌘","🌒","🌙","⭐"],
    ["⚡","🔱","👑","🌋","💥"],
]

def _make_mental_nc_handler(num: int, emoji_pool: list):
    cmd_names = (f"+mental{num}", f"💦mental{num}", f"/mental{num}", f"+amrit{num}", f"💦amrit{num}", f"/amrit{num}")
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user or not is_admin(update.effective_user.id): return
        if not update.effective_chat or not update.message or not _is_primary_bot(context): return
        raw = (update.message.text or "").strip()
        base = _extract_base(raw, cmd_names, context)
        if not base: return await update.message.reply_text(f"Usage: {cmd_names[0]} <text>")
        chat_id = update.effective_chat.id
        bots = get_bots_for_chat(chat_id, context.bot)
        _last = [""]
        def make_name():
            e1, e2 = random.choice(emoji_pool), random.choice(emoji_pool)
            return f"{e1} 𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋 {base} {e2}{make_suffix()}"[:255]
        async def nc_loop(stop_event): await _mental_hyperblitz_engine(chat_id, bots, stop_event, make_name)
        await task_controller.start_task(chat_id, "nc", nc_loop)
        await update.message.reply_text(f"⚡ 𝐌𝐄𝐍𝐓𝐀𝐋 {num} 𝐇𝐘𝐏𝐄𝐑𝐁𝐋𝐈𝐓𝐙 ({len(bots)} bots)\nStop: /stop")
    return handler

mental1_handler  = _make_mental_nc_handler(1,  _MENTAL_POOLS[0])
mental2_handler  = _make_mental_nc_handler(2,  _MENTAL_POOLS[1])
mental3_handler  = _make_mental_nc_handler(3,  _MENTAL_POOLS[2])
mental4_handler  = _make_mental_nc_handler(4,  _MENTAL_POOLS[3])
mental5_handler  = _make_mental_nc_handler(5,  _MENTAL_POOLS[4])
mental6_handler  = _make_mental_nc_handler(6,  _MENTAL_POOLS[5])
mental7_handler  = _make_mental_nc_handler(7,  _MENTAL_POOLS[6])
mental8_handler  = _make_mental_nc_handler(8,  _MENTAL_POOLS[7])
mental9_handler  = _make_mental_nc_handler(9,  _MENTAL_POOLS[8])
mental10_handler = _make_mental_nc_handler(10, _MENTAL_POOLS[9])

# ══════════════════════════════════════════════════════════════════
#  NEW: ZALGO NC, GRADIENT NC, AND GLOBAL ALL-GC NC
# ══════════════════════════════════════════════════════════════════
_ZALGO_UP = ["̍","̎","̄","̅","̿","̑","̆","̐","͒","͗","͑","̇","̈","̊","͂"]
_ZALGO_DOWN = ["̖","̗","̘","̙","̜","̝","̞","̟","̠","̤","̥","̦","̩","̪","̫"]
_GRADIENT_SETS = [["🔴","🟠","🟡","🟢","🔵","🟣"], ["🟣","🟪","🔷","💠","💎","✨"], ["🖤","🩶","🤍","💀","☠️","⚡"], ["🔥","💥","⚡","☄️","🌋","🩸"]]

def _make_zalgo(text: str) -> str:
    res = []
    for char in text:
        res.append(char)
        if char != ' ':
            res.append(random.choice(_ZALGO_UP))
            res.append(random.choice(_ZALGO_DOWN))
    return "".join(res)

async def zalgonc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+zalgonc", "💦zalgonc", "/zalgonc"), context)
    if not base: return await update.message.reply_text("Usage: +zalgonc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        g = _make_zalgo(base)
        sym = random.choice(["☠️","💀","👁️","⚡","🖤"])
        return f"{sym} {g} {sym}"[:255]
    async def nc_loop(stop_event): await _hyperfire_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"☠️ 𝐙𝐀𝐋𝐆𝐎 𝐆𝐋𝐈𝐓𝐂𝐇 𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")

async def gradientnc_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+gradientnc", "💦gradientnc", "/gradientnc"), context)
    if not base: return await update.message.reply_text("Usage: +gradientnc <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    def make_name():
        grad = random.choice(_GRADIENT_SETS)
        s1, s2 = grad[0], grad[-1]
        return f"{s1}{s2} {base} {s2}{s1}{make_suffix()}"[:255]
    async def nc_loop(stop_event): await _pair_rotate_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "nc", nc_loop)
    await update.message.reply_text(f"🌈 𝐆𝐑𝐀𝐃𝐈𝐄𝐍𝐓 𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")

async def globalnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("/globalnc", "+allgcnc", "💦allgcnc", "+globalnc", "/allgcnc"), context)
    if not base: return await update.message.reply_text("Usage: `+allgcnc <text>` ya `/globalnc <text>`", parse_mode="Markdown")

    if update.effective_chat and update.effective_chat.type in ("group", "supergroup"):
        if update.effective_chat.id not in known_chats:
            known_chats.add(update.effective_chat.id)
            save_groups(known_chats)

    target_gcs = list(known_chats)
    if update.effective_chat and update.effective_chat.id not in target_gcs and update.effective_chat.type in ("group", "supergroup"):
        target_gcs.append(update.effective_chat.id)

    if not target_gcs:
        return await update.message.reply_text("❌ *Koi active groups record nahi hain.*\nBots ko groups me add karein!", parse_mode="Markdown")

    started_count = 0
    msg = await update.message.reply_text(f"🚀 *Starting Global NC in {len(target_gcs)} groups with '{base}'…*", parse_mode="Markdown")

    def _make_gc_coro(cid, base_text):
        _last = [""]
        gc_bots = get_bots_for_chat(cid, context.bot)
        def _name_factory(): return _build_name(base_text, _last)
        async def _gc_nc_loop(stop_event: asyncio.Event):
            await _hyperfire_engine(cid, gc_bots, stop_event, _name_factory)
        return _gc_nc_loop

    for chat_id in target_gcs:
        try:
            await task_controller.start_task(chat_id, "globalnc", _make_gc_coro(chat_id, base))
            started_count += 1
        except Exception:
            pass

    await msg.edit_text(
        f"⚡ 💦 *𝐀𝐋𝐋 𝐆𝐂 𝐍𝐂 𝐀𝐂𝐓𝐈𝐕𝐄!* ⚡\n"
        f"Active in `{started_count}/{len(target_gcs)}` Groups\n"
        f"Text: `{base}`\n"
        f"Stop all: `/stopglobalnc`",
        parse_mode="Markdown"
    )

async def stopglobalnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message or not _is_primary_bot(context): return
    # stopped count calculation
    c = 0
    for cid in list(known_chats):
        if await task_controller.stop_task(cid, "globalnc"): c += 1
    await update.message.reply_text(f"🛑 𝐆𝐋𝐎𝐁𝐀𝐋 𝐍𝐂 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 in `{c}` Groups.", parse_mode="Markdown")

# ══════════════════════════════════════════════════════════════════
#  MEDIA (SONG & AI IMAGE) & GC PFP ROTATION
# ══════════════════════════════════════════════════════════════════
_POLLINATIONS_URL = "https://image.pollinations.ai/prompt/{prompt}?width=1024&height=1024&model=flux&nologo=true&enhance=true"
def _download_image_sync(prompt: str) -> bytes:
    encoded = urllib.parse.quote(prompt, safe="")
    req = urllib.request.Request(_POLLINATIONS_URL.format(prompt=encoded), headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=60) as r: return r.read()

async def aiimg_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    prompt = _extract_base(raw, ("+aiimg", "💦aiimg", "/aiimg"), context)
    if not prompt: return await update.message.reply_text("Usage: +aiimg <prompt>")
    wait_msg = await update.message.reply_text("🎨 Generating AI image…")
    loop = asyncio.get_event_loop()
    try:
        img_bytes = await asyncio.wait_for(loop.run_in_executor(None, _download_image_sync, prompt), timeout=70)
        img_file = io.BytesIO(img_bytes)
        img_file.name = "ai_image.jpg"
        bot = all_bot_instances[0] if all_bot_instances else context.bot
        await bot.send_photo(chat_id=update.effective_chat.id, photo=img_file, caption=f"🎨 *AI Image*\n📝 {prompt[:100]}\n⚡ 𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋", parse_mode="Markdown")
        await wait_msg.delete()
    except Exception as e: await wait_msg.edit_text(f"❌ Failed: {e}")

_SAAVN_MIRRORS = [
    "https://saavn.dev/api/search/songs?query={q}&page=1&limit=3",
    "https://saavn-api-privateciy.vercel.app/api/search/songs?query={q}&page=1&limit=3",
    "https://saavnapi-six.vercel.app/api/search/songs?query={q}&page=1&limit=3",
]
def _saavn_search_sync(query: str):
    q = urllib.parse.quote(query)
    headers = {"User-Agent": "Mozilla/5.0"}
    data = None
    for mirror in _SAAVN_MIRRORS:
        try:
            req = urllib.request.Request(mirror.format(q=q), headers=headers)
            with urllib.request.urlopen(req, timeout=8) as r: data = json.loads(r.read())
            break
        except Exception: continue
    if not data or not data.get("data", {}).get("results"): return None
    song = data["data"]["results"][0]
    dl_url = (song.get("downloadUrl") or [{}])[-1].get("url")
    if not dl_url: return None
    artists = song.get("artists", {}).get("primary", [])
    artist_name = ", ".join(a.get("name","") for a in artists) if isinstance(artists, list) else "Unknown"
    return {"title": song.get("name", "Unknown"), "artist": artist_name, "duration": int(song.get("duration") or 0), "url": dl_url}

def _download_audio_sync(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r: return r.read()

async def song_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    raw = (update.message.text or "").strip()
    query = _extract_base(raw, ("+song", "💦song", "/song"), context)
    if not query: return await update.message.reply_text("Usage: +song <song name>")
    wait_msg = await update.message.reply_text(f"🔍 Searching: {query}…")
    loop = asyncio.get_event_loop()
    try: info = await loop.run_in_executor(None, _saavn_search_sync, query)
    except Exception as e: return await wait_msg.edit_text(f"❌ Search failed: {e}")
    if not info: return await wait_msg.edit_text("❌ Song not found.")
    await wait_msg.edit_text(f"🎵 Found: *{info['title']}*\n⬇️ Downloading…", parse_mode="Markdown")
    try:
        audio_bytes = await asyncio.wait_for(loop.run_in_executor(None, _download_audio_sync, info["url"]), timeout=45)
        audio_file = io.BytesIO(audio_bytes)
        audio_file.name = f"{info['title'][:40]}.mp3"
        bot = all_bot_instances[0] if all_bot_instances else context.bot
        await bot.send_audio(chat_id=update.effective_chat.id, audio=audio_file, title=info["title"], performer=info["artist"], duration=info["duration"] or None, caption=f"🎵 *{info['title']}*\n👤 {info['artist']}\n⚡ 𝐀𝐌𝐑𝐈𝐓 𝐌𝐄𝐍𝐓𝐀𝐋", parse_mode="Markdown")
        await wait_msg.delete()
    except Exception as e: await wait_msg.edit_text(f"❌ Audio error: {e}")

gcpfp_photos: Dict[int, List[bytes]] = {}
async def _download_tg_photo(bot, file_id: str):
    try:
        f = await bot.get_file(file_id)
        buf = io.BytesIO()
        await f.download_to_memory(out=buf)
        return buf.getvalue()
    except Exception: return None

global_gcpfp_photos = []

async def gcpfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    current_chat_id = update.effective_chat.id
    delay = 10.0
    if context.args:
        try: delay = max(2.0, float(context.args[0]))
        except ValueError: pass
        
    msg = update.message.reply_to_message or update.message
    photo = msg.photo[-1] if msg.photo else (msg.document if msg.document and getattr(msg.document, "mime_type", "").startswith("image") else None)
    
    if photo:
        wait_msg = await update.message.reply_text("⬇️ <i>Downloading photo for Global GC PFP rotation...</i>", parse_mode="HTML")
        data = await _download_tg_photo(context.bot, photo.file_id)
        if not data: return await wait_msg.edit_text("❌ Download failed.")
        global_gcpfp_photos.clear()
        global_gcpfp_photos.append(data)
        gcpfp_photos[current_chat_id] = [data]
    else:
        existing = gcpfp_photos.get(current_chat_id) or global_gcpfp_photos
        if not existing:
            return await update.message.reply_text("📸 Reply to a photo with <code>/gcpfp [delay]</code>\n(Ek GC me chalane se sabhi groups me automatically chalne lagega!)", parse_mode="HTML")
        data = existing[0]
        wait_msg = await update.message.reply_text("🚀 <i>Starting Global GC PFP rotation across all groups...</i>", parse_mode="HTML")

    target_gcs = list(known_chats) or [current_chat_id]
    started_count = 0
    
    for cid in target_gcs:
        gcpfp_photos[cid] = list(global_gcpfp_photos) if global_gcpfp_photos else [data]
        
        def _create_gcpfp_coro(chat_id):
            gc_bots = get_bots_for_chat(chat_id, context.bot)
            async def _gcpfp_loop(stop_event: asyncio.Event):
                idx = 0
                while not stop_event.is_set():
                    photos = gcpfp_photos.get(chat_id) or global_gcpfp_photos
                    if not photos: break
                    d = photos[idx % len(photos)]
                    for bot in gc_bots:
                        if stop_event.is_set(): break
                        try:
                            await bot.set_chat_photo(chat_id, photo=io.BytesIO(d))
                            break
                        except Exception:
                            continue
                    idx += 1
                    try:
                        await asyncio.wait_for(stop_event.wait(), timeout=delay)
                    except asyncio.TimeoutError:
                        pass
            return _gcpfp_loop

        try:
            await task_controller.start_task(cid, "gcpfp", _create_gcpfp_coro(cid))
            started_count += 1
        except Exception:
            pass

    await wait_msg.edit_text(
        f"╔═━─ 𓆩⚡𓆪 ─━═╗\n"
        f"『𓍼ֶָ֢˖ ࣪ꨄ 𝐆𝐋𝐎𝐁𝐀𝐋 𝐆𝐂 𝐏𝐅𝐏 𝐀𝐂𝐓𝐈𝐕𝐄 .་༘࿐』\n"
        f"╚═━─ 𖤐🐉𖤐 ─━═╝\n\n"
        f"🖼️ <b>Rotator Status:</b> 🟢 <b>RUNNING IN ALL GCs</b>\n"
        f"👥 <b>Active Groups:</b> <code>{started_count}/{len(target_gcs)}</code> Groups\n"
        f"⏱️ <b>Rotation Delay:</b> <code>{delay}s</code>\n"
        f"🛑 <b>Stop Command:</b> <code>/stopgcpfp</code>\n\n"
        f"⋆｡°✩ ❝ 𝐃ᴇꜱɪɢɴᴇᴅ ꜰᴏʀ 𝐀ᴍʀɪᴛ 𝐗 𝐌ᴇɴᴛᴀʟ ❞ ✩°｡⋆",
        parse_mode="HTML"
    )

async def gcpfpadd_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    msg = update.message.reply_to_message or update.message
    photo = msg.photo[-1] if msg.photo else None
    if not photo: return await update.message.reply_text("Reply to a photo with /gcpfpadd")
    data = await _download_tg_photo(context.bot, photo.file_id)
    if not data: return await update.message.reply_text("❌ Download failed.")
    global_gcpfp_photos.append(data)
    for cid in list(known_chats) or [update.effective_chat.id]:
        gcpfp_photos.setdefault(cid, []).append(data)
    await update.message.reply_text(f"✅ Photo added to Global Pool! Total: {len(global_gcpfp_photos)}")

async def gcpfpset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    msg = update.message.reply_to_message or update.message
    photo = msg.photo[-1] if msg.photo else None
    if not photo: return await update.message.reply_text("Reply to a photo with /gcpfpset")
    wait_msg = await update.message.reply_text("⬇️ <i>Downloading & setting photo in all groups...</i>", parse_mode="HTML")
    data = await _download_tg_photo(context.bot, photo.file_id)
    if not data: return await wait_msg.edit_text("❌ Download failed.")
    
    success_count = 0
    target_gcs = list(known_chats) or [update.effective_chat.id]
    for cid in target_gcs:
        gc_bots = get_bots_for_chat(cid, context.bot)
        for b in gc_bots:
            try:
                await b.set_chat_photo(cid, photo=io.BytesIO(data))
                success_count += 1
                break
            except Exception:
                continue
    await wait_msg.edit_text(f"✅ <b>GC Photo Applied to {success_count}/{len(target_gcs)} Groups!</b>", parse_mode="HTML")

async def gcpfpclear_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not _is_primary_bot(context): return
    target_gcs = list(known_chats) or [update.effective_chat.id]
    cleared = 0
    for cid in target_gcs:
        gc_bots = get_bots_for_chat(cid, context.bot)
        for b in gc_bots:
            try:
                await b.delete_chat_photo(cid)
                cleared += 1
                break
            except Exception:
                continue
    await update.message.reply_text(f"🗑️ <b>GC Photo Removed in {cleared}/{len(target_gcs)} Groups!</b>", parse_mode="HTML")

async def stopgcpfp_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.message or not _is_primary_bot(context): return
    global_gcpfp_photos.clear()
    c = 0
    target_gcs = list(known_chats) or [update.effective_chat.id]
    for cid in target_gcs:
        gcpfp_photos.pop(cid, None)
        if await task_controller.stop_task(cid, "gcpfp"):
            c += 1
    if update.effective_chat.id not in target_gcs:
        gcpfp_photos.pop(update.effective_chat.id, None)
        if await task_controller.stop_task(update.effective_chat.id, "gcpfp"):
            c += 1
    await update.message.reply_text(f"🛑 <b>𝐆𝐋𝐎𝐁𝐀𝐋 𝐆𝐂 𝐏𝐅𝐏 𝐒𝐓𝐎𝐏𝐏𝐄𝐃</b> in <code>{c}</code> Groups!", parse_mode="HTML")

async def gcpfpstatus_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    target_gcs = list(known_chats) or [update.effective_chat.id]
    active_gcs = [cid for cid in target_gcs if task_controller.is_running(cid, "gcpfp")]
    count = len(global_gcpfp_photos) or len(gcpfp_photos.get(update.effective_chat.id, []))
    status_str = f"🟢 Running in {len(active_gcs)}/{len(target_gcs)} Groups" if active_gcs else "🔴 Stopped"
    await update.message.reply_text(f"🖼️ <b>𝐆𝐂 𝐏𝐅𝐏 𝐒𝐓𝐀𝐓𝐔𝐒:</b> {status_str}\n📸 <b>Global Photos in Pool:</b> <code>{count}</code>", parse_mode="HTML")

# ══════════════════════════════════════════════════════════════════
#  GROUP CONTROL & CHAT MANAGEMENT
# ══════════════════════════════════════════════════════════════════
async def leave_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    try: await update.message.reply_text(f"💦 𝐋𝐄𝐀𝐕𝐈𝐍𝐆 𝐆𝐂 ({len(bots)} bots)... Bye bye 💦")
    except Exception: pass
    await task_controller.stop_all_for_chat(chat_id)
    known_chats.discard(chat_id)
    save_groups(known_chats)
    await asyncio.gather(*[b.leave_chat(chat_id) for b in bots], return_exceptions=True)

async def mute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    if chat_id in mute_chats:
        mute_chats.discard(chat_id)
        await update.message.reply_text("🔊 𝐌𝐔𝐓𝐄 𝐎𝐅𝐅")
    else:
        mute_chats.add(chat_id)
        await update.message.reply_text("🔇 𝐌𝐔𝐓𝐄 𝐎𝐍 — Non-admin messages will be deleted")

async def purge_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    mid = update.message.message_id
    n = 10
    if context.args:
        try: n = min(int(context.args[0]), 100)
        except ValueError: pass
    to_delete = list(range(mid - n, mid + 1))
    deleted = 0
    try:
        await update.effective_chat.delete_messages(to_delete)
        deleted = len(to_delete)
    except Exception:
        for m in to_delete:
            try: await context.bot.delete_message(chat_id, m); deleted += 1
            except Exception: pass
    confirm = await update.message.chat.send_message(f"🗑️ Purged {deleted} messages.")
    await asyncio.sleep(2)
    try: await confirm.delete()
    except Exception: pass

async def ncdel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    chat_id = update.effective_chat.id
    if chat_id in ncdel_chats:
        ncdel_chats.discard(chat_id)
        await update.message.reply_text("🟢 𝐍𝐂𝐃𝐄𝐋 𝐎𝐅𝐅")
    else:
        ncdel_chats.add(chat_id)
        await update.message.reply_text("🗑 𝐍𝐂𝐃𝐄𝐋 𝐎𝐍 — Enemy NC messages will be deleted")

async def ncwar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("/ncwar", "+ncwar", "💦ncwar"), context)
    if not base: return await update.message.reply_text("Usage: /ncwar <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    ncwar_targets[chat_id] = base
    _last = [""]
    def make_name(): return _build_name(base, _last)
    async def nc_loop(stop_event): await _hyperfire_engine(chat_id, bots, stop_event, make_name)
    await task_controller.start_task(chat_id, "ncwar", nc_loop)
    await update.message.reply_text(f"⚔️ 𝐍𝐂𝐖𝐀𝐑 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stopncwar")

async def stopncwar_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ncwar_targets.pop(update.effective_chat.id, None)
    if await task_controller.stop_task(update.effective_chat.id, "ncwar"): await update.message.reply_text("🛑 𝐍𝐂𝐖𝐀𝐑 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")
    else: await update.message.reply_text("No ncwar running.")

async def mygc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Lists all active groups with direct clickable invite links and IDs."""
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not known_chats and update.effective_chat and update.effective_chat.type in ("group", "supergroup"):
        known_chats.add(update.effective_chat.id)
        save_groups(known_chats)

    if not known_chats:
        return await update.message.reply_text("❌ *Koi active groups record nahi hain.*\nBots ko groups me add karein ya koi message bhejein!", parse_mode="Markdown")

    status_msg = await update.message.reply_text("🔍 *Scanning active groups...*", parse_mode="Markdown")

    total_gcs = len(known_chats)
    gc_entries = []

    for idx, cid in enumerate(list(known_chats), 1):
        chat_title = f"Group {cid}"
        link = ""
        try:
            chat = await asyncio.wait_for(context.bot.get_chat(cid), timeout=2.0)
            if chat.title: chat_title = chat.title
            if chat.username:
                link = f"https://t.me/{chat.username}"
            elif chat.invite_link:
                link = chat.invite_link
            else:
                try:
                    exported = await asyncio.wait_for(context.bot.export_chat_invite_link(cid), timeout=1.5)
                    if exported: link = exported
                except Exception:
                    pass
        except Exception:
            pass

        if not link:
            clean_cid = str(cid).replace("-100", "").replace("-", "")
            link = f"https://t.me/c/{clean_cid}/1"

        gc_entries.append({
            "idx": idx,
            "title": chat_title,
            "id": cid,
            "link": link
        })

    # Chunk into 8 groups per message to avoid Telegram character limit
    chunk_size = 8
    chunks = [gc_entries[i:i + chunk_size] for i in range(0, len(gc_entries), chunk_size)]
    total_chunks = len(chunks)

    for c_idx, chunk in enumerate(chunks, 1):
        msg_lines = [
            "╔═━─ 𓆩🌐𓆪 ─━═╗",
            f"『 ⚡ 𝐌𝐘 𝐀𝐂𝐓𝐈𝐕𝐄 𝐆𝐑𝐎𝐔𝐏𝐒 ({total_gcs}) ─ [{c_idx}/{total_chunks}] 』",
            "╚═━─ 𖤐👑𖤐 ─━═╝\n"
        ]
        for item in chunk:
            msg_lines.append(
                f"✦ **{item['idx']}. {item['title']}**\n"
                f"   ├ 🆔 `ID:` `{item['id']}`\n"
                f"   └ 🔗 `Link:` {item['link']}\n"
            )
        msg_lines.append("───────────────────────")
        full_text = "\n".join(msg_lines)
        if c_idx == 1:
            try: await status_msg.edit_text(full_text, parse_mode="Markdown", disable_web_page_preview=True)
            except Exception: await update.message.reply_text(full_text, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await update.message.reply_text(full_text, parse_mode="Markdown", disable_web_page_preview=True)
            await asyncio.sleep(0.3)

async def gclist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await mygc_cmd(update, context)

_NO_PERMS = ChatPermissions(can_send_messages=False, can_send_photos=False, can_send_videos=False)
_ALL_PERMS = ChatPermissions(can_send_messages=True, can_send_photos=True, can_send_videos=True)

async def restrict_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    u = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not u or is_admin(u.id): return await update.message.reply_text("Reply to a user to restrict.")
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, u.id, permissions=_NO_PERMS)
        await update.message.reply_text(f"🔒 Restricted @{u.username or u.first_name}")
    except Exception as e: await update.message.reply_text(f"❌ Error: {e}")

async def unrestrict_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    u = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not u: return await update.message.reply_text("Reply to a user to unrestrict.")
    try:
        await context.bot.restrict_chat_member(update.effective_chat.id, u.id, permissions=_ALL_PERMS)
        await update.message.reply_text(f"🔓 Unrestricted @{u.username or u.first_name}")
    except Exception as e: await update.message.reply_text(f"❌ Error: {e}")

# ══════════════════════════════════════════════════════════════════
#  REACTIONS, SLIDE, SPAM & REPLIES
# ══════════════════════════════════════════════════════════════════
_REACT_RANDOM = ["👍","❤️","🔥","🥰","👏","😁","🤔","🤯","😱","🤩","🎉","💯","⚡","👑"]
_REACT_HEART  = ["❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎","❤️‍🔥","🥰"]
_REACT_BOOM   = ["🔥","⚡","💥","🤯","😱","🏆","👊","💣","🤩","🚀","👑"]

async def _do_react(bots, chat_id, msg_id, style):
    if style == "heart": emoji = random.choice(_REACT_HEART)
    elif style == "boom": emoji = random.choice(_REACT_BOOM)
    elif style == "custom": emoji = custom_react_emojis.get(chat_id, "💦")
    else: emoji = random.choice(_REACT_RANDOM)
    async def _r(b):
        try: await b.set_message_reaction(chat_id, msg_id, reaction=[ReactionTypeEmoji(emoji=emoji)], is_big=False)
        except Exception: pass
    await asyncio.gather(*[_r(b) for b in bots], return_exceptions=True)

async def autoreact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    cid = update.effective_chat.id
    if autoreact_chats.get(cid) == "random":
        autoreact_chats.pop(cid, None)
        await update.message.reply_text("😶 𝐀𝐔𝐓𝐎𝐑𝐄𝐀𝐂𝐓 𝐎𝐅𝐅")
    else:
        autoreact_chats[cid] = "random"
        await update.message.reply_text("😂 𝐀𝐔𝐓𝐎𝐑𝐄𝐀𝐂𝐓 𝐎𝐍")

async def heartreact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    cid = update.effective_chat.id
    autoreact_chats[cid] = "heart"
    await update.message.reply_text("❤️ 𝐇𝐄𝐀𝐑𝐓𝐑𝐄𝐀𝐂𝐓 𝐎𝐍")

async def boomreact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    cid = update.effective_chat.id
    autoreact_chats[cid] = "boom"
    await update.message.reply_text("🔥 𝐁𝐎𝐎𝐌𝐑𝐄𝐀𝐂𝐓 𝐎𝐍")

async def customreact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+customreact", "💦customreact", "/customreact"), context)
    if not base:
        autoreact_chats.pop(update.effective_chat.id, None)
        return await update.message.reply_text("😶 𝐂𝐔𝐒𝐓𝐎𝐌 𝐑𝐄𝐀𝐂𝐓 𝐎𝐅𝐅")
    emoji_char = base.split()[0]
    custom_react_emojis[update.effective_chat.id] = emoji_char
    autoreact_chats[update.effective_chat.id] = "custom"
    await update.message.reply_text(f"✨ Custom react set: {emoji_char}")

async def stopreact_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    autoreact_chats.pop(update.effective_chat.id, None)
    await update.message.reply_text("😶 𝐑𝐄𝐀𝐂𝐓 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")

SLIDE_TEXTS = ["💦", "🌊💦", "💦🌊💦", "⚡💦⚡", "🔥💦🔥", "👀💦", "💦💦💦", "🌊⚡🌊", "💦👑💦"]
async def _slide_reply_burst(bot, chat_id, message_id, count=5):
    for _ in range(count):
        try: await bot.send_message(chat_id, random.choice(SLIDE_TEXTS), reply_to_message_id=message_id)
        except Exception: break
        await asyncio.sleep(0.02)

async def slidereply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    cid = update.effective_chat.id
    u = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not u or is_admin(u.id):
        if cid in slide_reply_targets:
            slide_reply_targets.pop(cid)
            return await update.message.reply_text("💬 𝐒𝐋𝐈𝐃𝐄𝐑𝐄𝐏𝐋𝐘 𝐎𝐅𝐅")
        return await update.message.reply_text("Reply to target user.")
    slide_reply_targets[cid] = u.id
    await update.message.reply_text(f"💬 𝐒𝐋𝐈𝐃𝐄𝐑𝐄𝐏𝐋𝐘 𝐎𝐍 for @{u.username or u.first_name}")

async def stopslidereply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    slide_reply_targets.pop(update.effective_chat.id, None)
    await update.message.reply_text("💬 𝐒𝐋𝐈𝐃𝐄𝐑𝐄𝐏𝐋𝐘 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")

_SLIDE_SYMS = ["꧁","꧂","⟡","✦","◈","✧","⊹","✶","⋆","⚡","🔥","💫","⚜","🌟","💠","🔮","👑","💎"]
async def plus_slide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if not update.effective_chat or not update.message or not update.message.reply_to_message: return await update.message.reply_text("Reply to a message.")
    raw = (update.message.text or "").strip()
    base = raw[6:].strip() if raw.lower().startswith("+slide") else " ".join(context.args or [])
    if not base: return await update.message.reply_text("Usage: +slide <text>")
    chat_id, mid = update.effective_chat.id, update.message.reply_to_message.message_id
    bots = get_bots_for_chat(chat_id, context.bot)
    async def _bot_slide_worker(bot, stop_event):
        while not stop_event.is_set():
            sym1, sym2 = random.choice(_SLIDE_SYMS), random.choice(_SLIDE_SYMS)
            try: await bot.send_message(chat_id=chat_id, text=f"{sym1} {base} {sym2}", reply_to_message_id=mid)
            except Exception: pass
            try: await asyncio.wait_for(stop_event.wait(), timeout=0.05)
            except asyncio.TimeoutError: pass
    async def slide_loop(stop_event):
        workers = [asyncio.create_task(_bot_slide_worker(b, stop_event)) for b in bots]
        try: await asyncio.gather(*workers, return_exceptions=True)
        finally:
            for w in workers:
                if not w.done(): w.cancel()
    await task_controller.start_task(chat_id, "spam", slide_loop)
    await update.message.reply_text(f"⚡ 𝐒𝐋𝐈𝐃𝐄 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stop")

async def spam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+spam", "💦spam", "/spam"), context)
    if not base: return await update.message.reply_text("Usage: +spam <text>")
    chat_id = update.effective_chat.id
    bots = get_bots_for_chat(chat_id, context.bot)
    async def _bot_spam_worker(bot, stop_event):
        while not stop_event.is_set():
            try: await bot.send_message(chat_id=chat_id, text=base)
            except Exception: pass
            try: await asyncio.wait_for(stop_event.wait(), timeout=0.06)
            except asyncio.TimeoutError: pass
    async def spam_loop(stop_event):
        workers = [asyncio.create_task(_bot_spam_worker(b, stop_event)) for b in bots]
        try: await asyncio.gather(*workers, return_exceptions=True)
        finally:
            for w in workers:
                if not w.done(): w.cancel()
    await task_controller.start_task(chat_id, "spam", spam_loop)
    await update.message.reply_text(f"💬 𝐒𝐏𝐀𝐌 𝐀𝐂𝐓𝐈𝐕𝐄 ({len(bots)} bots)\nStop: /stopspam")

async def stopspam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await task_controller.stop_task(update.effective_chat.id, "spam"): await update.message.reply_text("🛑 𝐒𝐏𝐀𝐌 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")
    else: await update.message.reply_text("No spam running.")

async def autoreply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+autoreply", "💦autoreply", "/autoreply"), context)
    if not base:
        autoreply_chats.pop(update.effective_chat.id, None)
        return await update.message.reply_text("🔇 𝐀𝐔𝐓𝐎𝐑𝐄𝐏𝐋𝐘 𝐎𝐅𝐅")
    autoreply_chats[update.effective_chat.id] = base
    await update.message.reply_text(f"💬 𝐀𝐔𝐓𝐎𝐑𝐄𝐏𝐋𝐘 𝐎𝐍: {base[:30]}")

async def stopautoreply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    autoreply_chats.pop(update.effective_chat.id, None)
    await update.message.reply_text("🔇 𝐀𝐔𝐓𝐎𝐑𝐄𝐏𝐋𝐘 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")

async def targetreply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    raw = (update.message.text or "").strip()
    base = _extract_base(raw, ("+targetreply", "💦targetreply", "/targetreply"), context)
    u = update.message.reply_to_message.from_user if update.message.reply_to_message else None
    if not u or is_admin(u.id) or not base:
        targetreply_chats.pop(update.effective_chat.id, None)
        return await update.message.reply_text("Usage: reply to user with +targetreply <text>")
    targetreply_chats[update.effective_chat.id] = {"uid": u.id, "text": base}
    await update.message.reply_text(f"🎯 Target reply set for @{u.username or u.first_name}")

async def stoptargetreply_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    targetreply_chats.pop(update.effective_chat.id, None)
    await update.message.reply_text("🔇 𝐓𝐀𝐑𝐆𝐄𝐓𝐑𝐄𝐏𝐋𝐘 𝐒𝐓𝐎𝐏𝐏𝐄𝐃")

async def setmenuphoto_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    ref = update.message.reply_to_message or update.message
    if not ref.photo: return await update.message.reply_text("Reply to a photo.")
    _menu_media.clear()
    _menu_media["photo_id"] = ref.photo[-1].file_id
    save_menu_media(_menu_media)
    await update.message.reply_text("🖼 Menu photo set!")

async def setmenuvideo_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    ref = update.message.reply_to_message or update.message
    if not ref.video and not ref.animation: return await update.message.reply_text("Reply to a video.")
    _menu_media.clear()
    if ref.video: _menu_media["video_id"] = ref.video.file_id
    else: _menu_media["animation_id"] = ref.animation.file_id
    save_menu_media(_menu_media)
    await update.message.reply_text("🎥 Menu video set!")

async def clearmenu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    _menu_media.clear()
    save_menu_media(_menu_media)
    await update.message.reply_text("🗑 Menu media cleared.")

async def botname_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    name = " ".join(context.args or []).strip()
    if not name: return await update.message.reply_text("Usage: /botname <new name>")
    for b in all_bot_instances or [context.bot]:
        try: await b.set_my_name(name)
        except Exception: pass
    await update.message.reply_text(f"📛 Bot Name updated to: {name}")

async def globalstop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    total = 0
    for cid in list(known_chats):
        total += await task_controller.stop_all_for_chat(cid)
    await update.message.reply_text(f"🛑 𝐆𝐋𝐎𝐁𝐀𝐋 𝐒𝐓𝐎𝐏: Stopped tasks across all groups.")

async def globalannounce_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    text = " ".join(context.args or []).strip()
    if not text: return await update.message.reply_text("Usage: /globalannounce <message>")
    for cid in list(known_chats):
        try: await context.bot.send_message(cid, text); await asyncio.sleep(0.15)
        except Exception: pass
    await update.message.reply_text(f"📢 Announced to {len(known_chats)} groups.")

async def globalmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    mute_chats.update(known_chats)
    await update.message.reply_text("🔇 Global mute ON in all groups.")

async def globalunmute_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_user or not is_admin(update.effective_user.id): return
    mute_chats.clear()
    await update.message.reply_text("🔊 Global mute OFF in all groups.")

# ══════════════════════════════════════════════════════════════════
#  DISPATCHERS & EVENT LISTENERS
# ══════════════════════════════════════════════════════════════════
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user or not update.effective_chat: return
    chat_id = update.effective_chat.id
    known_chats.add(chat_id)
    uid = update.message.from_user.id
    msg = (update.message.text or "").strip()
    msg_lower = msg.lower()

    if chat_id in mute_chats and not is_admin(uid):
        try: await update.message.delete()
        except Exception: pass
        return

    if chat_id in autoreact_chats and update.message.message_id:
        style = autoreact_chats[chat_id]
        react_bots = get_bots_for_chat(chat_id, context.bot)
        asyncio.create_task(_do_react(react_bots, chat_id, update.message.message_id, style))

    # All GC NC (CRITICAL: MUST BE CHECKED BEFORE +allgc)
    if (msg_lower.startswith("+allgcnc") or msg_lower.startswith("💦allgcnc") or
        msg_lower.startswith("+globalnc") or msg_lower.startswith("💦globalnc") or
        msg_lower.startswith("/globalnc") or msg_lower.startswith("/allgcnc")):
        if is_admin(uid): await globalnc_cmd(update, context)
        return

    if msg_lower.startswith("/stopglobalnc") or msg_lower.startswith("+stopglobalnc") or msg_lower.startswith("💦stopglobalnc"):
        if is_admin(uid): await stopglobalnc_cmd(update, context)
        return

    # My GC List (STRICT CHECK: exact match or followed by space/newline)
    if (msg_lower == "+mygc" or msg_lower.startswith("+mygc ") or
        msg_lower == "💦mygc" or msg_lower.startswith("💦mygc ") or
        msg_lower == "+allgc" or msg_lower.startswith("+allgc ") or
        msg_lower == "+gclist" or msg_lower.startswith("+gclist ") or
        msg_lower == "/mygc" or msg_lower.startswith("/mygc ") or
        msg_lower == "/gclist" or msg_lower.startswith("/gclist ")):
        if is_admin(uid): await mygc_cmd(update, context)
        return

    # Add GC / Del GC manual management
    if msg_lower.startswith("+addgc") or msg_lower.startswith("/addgc"):
        if is_admin(uid):
            parts = msg.split()
            if len(parts) > 1:
                try:
                    target_id = int(parts[1])
                    known_chats.add(target_id)
                    save_groups(known_chats)
                    await update.message.reply_text(f"✅ Group `{target_id}` added to target list! Total: `{len(known_chats)}` GCs.", parse_mode="Markdown")
                except ValueError:
                    await update.message.reply_text("Usage: `+addgc <numeric_chat_id>`", parse_mode="Markdown")
            else:
                if update.effective_chat:
                    known_chats.add(update.effective_chat.id)
                    save_groups(known_chats)
                    await update.message.reply_text(f"✅ Current group `{update.effective_chat.id}` added! Total: `{len(known_chats)}` GCs.", parse_mode="Markdown")
        return

    if msg_lower.startswith("+delgc") or msg_lower.startswith("/delgc"):
        if is_admin(uid):
            parts = msg.split()
            if len(parts) > 1:
                try:
                    target_id = int(parts[1])
                    known_chats.discard(target_id)
                    save_groups(known_chats)
                    await update.message.reply_text(f"🗑️ Group `{target_id}` removed! Total: `{len(known_chats)}` GCs.", parse_mode="Markdown")
                except ValueError:
                    await update.message.reply_text("Usage: `+delgc <numeric_chat_id>`", parse_mode="Markdown")
        return

    # Zalgo & Gradient
    if msg_lower.startswith("+zalgonc") or msg_lower.startswith("💦zalgonc"):
        if is_admin(uid): await zalgonc_handler(update, context)
        return
    if msg_lower.startswith("+gradientnc") or msg_lower.startswith("💦gradientnc"):
        if is_admin(uid): await gradientnc_handler(update, context)
        return

    # Original Name changers
    if msg_lower.startswith("+horneync") or msg_lower.startswith("💦horneync"):
        if is_admin(uid): await horneync_handler(update, context)
        return
    if msg_lower.startswith("+ohyesnc") or msg_lower.startswith("💦ohyesnc"):
        if is_admin(uid): await ohyesnc_handler(update, context)
        return
    if msg_lower.startswith("+stealthnc") or msg_lower.startswith("💦stealthnc"):
        if is_admin(uid): await stealthnc_handler(update, context)
        return
    if msg_lower.startswith("+lunanc") or msg_lower.startswith("💦lunanc") or msg_lower.startswith("+lundnc") or msg_lower.startswith("💦lundnc"):
        if is_admin(uid): await lundnc_handler(update, context)
        return
    if msg_lower.startswith("+bhosdanc") or msg_lower.startswith("💦bhosdanc"):
        if is_admin(uid): await bhosdanc_handler(update, context)
        return
    if msg_lower.startswith("+areync") or msg_lower.startswith("💦areync"):
        if is_admin(uid): await areync_handler(update, context)
        return
    if msg_lower.startswith("+hatnc") or msg_lower.startswith("💦hatnc"):
        if is_admin(uid): await hatnc_handler(update, context)
        return
    if msg_lower.startswith("+crync") or msg_lower.startswith("💦crync") or msg_lower.startswith("+😭nc") or msg_lower.startswith("💦😭nc"):
        if is_admin(uid): await crync_handler(update, context)
        return
    if msg_lower.startswith("+mentalnc") or msg_lower.startswith("💦mentalnc") or msg_lower.startswith("+arnavnc") or msg_lower.startswith("💦arnavnc"):
        if is_admin(uid): await arnavnc_handler(update, context)
        return
    if msg_lower.startswith("+amritnc") or msg_lower.startswith("💦amritnc") or msg_lower.startswith("+kentonc") or msg_lower.startswith("💦kentonc"):
        if is_admin(uid): await kentonc_handler(update, context)
        return
    if msg_lower.startswith("+amritxnc") or msg_lower.startswith("💦amritxnc") or msg_lower.startswith("+cr7nc") or msg_lower.startswith("💦cr7nc"):
        if is_admin(uid): await cr7nc_handler(update, context)
        return
    if msg_lower.startswith("+tripnc") or msg_lower.startswith("💦tripnc"):
        if is_admin(uid): await tripnc_handler(update, context)
        return
    if msg_lower.startswith("+ultranc") or msg_lower.startswith("💦ultranc"):
        if is_admin(uid): await ultranc_handler(update, context)
        return
    if msg_lower.startswith("+pairnc") or msg_lower.startswith("💦pairnc"):
        if is_admin(uid): await pairnc_handler(update, context)
        return
    if msg_lower.startswith("+infernc") or msg_lower.startswith("💦infernc"):
        if is_admin(uid): await infernc_handler(update, context)
        return
    if msg_lower.startswith("+voidnc") or msg_lower.startswith("💦voidnc"):
        if is_admin(uid): await voidnc_handler(update, context)
        return
    if msg_lower.startswith("+stormnc") or msg_lower.startswith("💦stormnc"):
        if is_admin(uid): await stormnc_handler(update, context)
        return
    if msg_lower.startswith("+bloodnc") or msg_lower.startswith("💦bloodnc"):
        if is_admin(uid): await bloodnc_handler(update, context)
        return
    if msg_lower.startswith("+divinenc") or msg_lower.startswith("💦divinenc"):
        if is_admin(uid): await divinenc_handler(update, context)
        return

    # Font NCs
    if msg_lower.startswith("+boldnc") or msg_lower.startswith("💦boldnc"):
        if is_admin(uid): await boldnc_handler(update, context)
        return
    if msg_lower.startswith("+italicnc") or msg_lower.startswith("💦italicnc"):
        if is_admin(uid): await italicnc_handler(update, context)
        return
    if msg_lower.startswith("+cursivenc") or msg_lower.startswith("💦cursivenc"):
        if is_admin(uid): await cursivenc_handler(update, context)
        return
    if msg_lower.startswith("+bubblenc") or msg_lower.startswith("💦bubblenc"):
        if is_admin(uid): await bubblenc_handler(update, context)
        return
    if msg_lower.startswith("+smallcapsnc") or msg_lower.startswith("💦smallcapsnc"):
        if is_admin(uid): await smallcapsnc_handler(update, context)
        return
    if msg_lower.startswith("+flipnc") or msg_lower.startswith("💦flipnc"):
        if is_admin(uid): await flipnc_handler(update, context)
        return

    # Animations
    if msg_lower.startswith("+loading") or msg_lower.startswith("💦loading"):
        if is_admin(uid): await loading_cmd(update, context)
        return
    if msg_lower.startswith("+countdown") or msg_lower.startswith("💦countdown"):
        if is_admin(uid): await countdown_cmd(update, context)
        return
    if msg_lower.startswith("+typewrite") or msg_lower.startswith("💦typewrite"):
        if is_admin(uid): await typewrite_cmd(update, context)
        return
    if msg_lower.startswith("+spinner") or msg_lower.startswith("💦spinner"):
        if is_admin(uid): await spinner_cmd(update, context)
        return
    if msg_lower.startswith("+glitch") or msg_lower.startswith("💦glitch"):
        if is_admin(uid): await glitch_cmd(update, context)
        return
    if msg_lower.startswith("+matrix") or msg_lower.startswith("💦matrix"):
        if is_admin(uid): await matrixtroll_cmd(update, context)
        return

    # Mental 1-10
    for num, h in enumerate([mental1_handler, mental2_handler, mental3_handler, mental4_handler, mental5_handler, mental6_handler, mental7_handler, mental8_handler, mental9_handler, mental10_handler], 1):
        if msg_lower.startswith(f"+mental{num}") or msg_lower.startswith(f"💦mental{num}") or msg_lower.startswith(f"+amrit{num}") or msg_lower.startswith(f"💦amrit{num}"):
            if is_admin(uid): await h(update, context)
            return

    # GCPFP Global (+ prefix)
    if msg_lower.startswith("+gcpfp") or msg_lower.startswith("💦gcpfp") or msg_lower.startswith("+allgcpfp"):
        if is_admin(uid):
            parts = msg.split()
            context.args = parts[1:] if len(parts) > 1 else []
            await gcpfp_cmd(update, context)
        return
    if msg_lower.startswith("+stopgcpfp") or msg_lower.startswith("💦stopgcpfp") or msg_lower.startswith("+stopallgcpfp"):
        if is_admin(uid):
            await stopgcpfp_cmd(update, context)
        return

    # Dhasu Features (+ prefix)
    if msg_lower.startswith("+tempmail") or msg_lower.startswith("💦tempmail"):
        await tempmail_cmd(update, context)
        return
    if msg_lower.startswith("+rollcall") or msg_lower.startswith("💦rollcall"):
        if is_admin(uid): await rollcall_cmd(update, context)
        return
    if msg_lower.startswith("+bodyguard") or msg_lower.startswith("💦bodyguard"):
        if is_admin(uid):
            parts = msg.split()
            context.args = parts[1:] if len(parts) > 1 else []
            await bodyguard_cmd(update, context)
        return
    if msg_lower.startswith("+iq") or msg_lower.startswith("💦iq"):
        await iq_cmd(update, context)
        return
    if msg_lower.startswith("+roast") or msg_lower.startswith("💦roast"):
        await roast_cmd(update, context)
        return
    if msg_lower.startswith("+stealthlock") or msg_lower.startswith("💦stealthlock"):
        if is_admin(uid):
            parts = msg.split()
            context.args = parts[1:] if len(parts) > 1 else []
            await stealthlock_cmd(update, context)
        return

    # Bodyguard Active Shield Defense
    if chat_id in bodyguard_chats and not is_admin(uid):
        is_rep_owner = False
        if update.message.reply_to_message and update.message.reply_to_message.from_user:
            rep_uid = update.message.reply_to_message.from_user.id
            if _is_owner(rep_uid):
                is_rep_owner = True
        abusive_triggers = ["gali", "madarchod", "bhosdike", "chutiya", "lodu", "randi", "bhenchod", "kuta", "tera baap", "aukat", "bsdk", "mc", "bc"]
        has_abuse = any(w in msg_lower for w in abusive_triggers)
        if is_rep_owner or (has_abuse and "amrit" in msg_lower):
            bg_responses = [
                f"🛡️ <b>[SHIELD ALERT]</b> {update.message.from_user.mention_html()} Boss Amrit ke khilaaf bolne ki ghalti mat kar! Aukaat me reh.",
                f"⚠️ <b>[BODYGUARD PROTOCOL]</b> {update.message.from_user.mention_html()} Warning 1: Admin Amrit is protected by Nexus Fleet! Retreat now.",
                f"🐉 <b>[FLEET THREAT DETECTED]</b> {update.message.from_user.mention_html()} Mind your language in front of Primary Admin Amrit!",
            ]
            reply_txt = random.choice(bg_responses)
            b = random.choice(all_bot_instances) if all_bot_instances else context.bot
            try:
                await b.send_message(chat_id, reply_txt, parse_mode="HTML", reply_to_message_id=update.message.message_id)
                try: await b.set_message_reaction(chat_id, update.message.message_id, reaction=[ReactionTypeEmoji("💀")])
                except Exception: pass
            except Exception: pass

    # Media, Replies & Reacts
    if msg_lower.startswith("+aiimg") or msg_lower.startswith("💦aiimg"):
        if is_admin(uid): await aiimg_cmd(update, context)
        return
    if msg_lower.startswith("+song") or msg_lower.startswith("💦song"):
        if is_admin(uid): await song_cmd(update, context)
        return
    if msg_lower.startswith("+purenc") or msg_lower.startswith("💦purenc"):
        if is_admin(uid): await purenc_handler(update, context)
        return
    if msg_lower.startswith("+rnc") or msg_lower.startswith("💦rnc") or msg_lower.startswith("+randnc") or msg_lower.startswith("💦randnc"):
        if is_admin(uid): await randnc_handler(update, context)
        return
    if msg_lower.startswith("+flamenc") or msg_lower.startswith("💦flamenc") or msg_lower.startswith("+burnc") or msg_lower.startswith("💦burnc"):
        if is_admin(uid): await burnc_handler(update, context)
        return
    if msg_lower.startswith("+aahnc") or msg_lower.startswith("💦aahnc"):
        if is_admin(uid): await aahnc_handler(update, context)
        return
    if msg_lower.startswith("+ncwar") or msg_lower.startswith("💦ncwar"):
        if is_admin(uid): await ncwar_cmd(update, context)
        return
    if msg_lower.startswith("+autoreact") or msg_lower.startswith("💦autoreact"):
        if is_admin(uid): await autoreact_cmd(update, context)
        return
    if msg_lower.startswith("+heartreact") or msg_lower.startswith("💦heartreact"):
        if is_admin(uid): await heartreact_cmd(update, context)
        return
    if msg_lower.startswith("+boomreact") or msg_lower.startswith("💦boomreact"):
        if is_admin(uid): await boomreact_cmd(update, context)
        return
    if msg_lower.startswith("+customreact") or msg_lower.startswith("💦customreact"):
        if is_admin(uid): await customreact_cmd(update, context)
        return
    if msg_lower.startswith("+slidereply") or msg_lower.startswith("💦slidereply"):
        if is_admin(uid): await slidereply_cmd(update, context)
        return
    if msg_lower.startswith("+slide") and not msg_lower.startswith("+slidereply"):
        if is_admin(uid): await plus_slide(update, context)
        return
    if msg_lower.startswith("+spam") or msg_lower.startswith("💦spam"):
        if is_admin(uid): await spam_cmd(update, context)
        return
    if msg_lower.startswith("+autoreply") or msg_lower.startswith("💦autoreply"):
        if is_admin(uid): await autoreply_cmd(update, context)
        return
    if msg_lower.startswith("+targetreply") or msg_lower.startswith("💦targetreply"):
        if is_admin(uid): await targetreply_cmd(update, context)
        return

    # Auto Folder & Admin Commands
    if msg_lower.startswith("+allpromote") or msg_lower.startswith("+promoteall"):
        if is_admin(uid): await allpromote_cmd(update, context)
        return
    if msg_lower.startswith("+addbot") or msg_lower.startswith("+addandpromote"):
        if is_admin(uid): await addbot_cmd(update, context)
        return
    if msg_lower.startswith("+joingc") or msg_lower.startswith("💦joingc") or msg_lower.startswith("+addgc"):
        if is_admin(uid): await joingc_cmd(update, context)
        return
    if msg_lower.startswith("+folderjoin"):
        if is_admin(uid): await folderjoin_cmd(update, context)
        return

    # Auto text reply if active
    if chat_id in autoreply_chats and not is_admin(uid):
        rep = autoreply_chats[chat_id]
        b = all_bot_instances[0] if all_bot_instances else context.bot
        asyncio.create_task(b.send_message(chat_id, rep, reply_to_message_id=update.message.message_id))

    tr = targetreply_chats.get(chat_id)
    if tr and uid == tr["uid"] and not is_admin(uid):
        b = all_bot_instances[0] if all_bot_instances else context.bot
        asyncio.create_task(b.send_message(chat_id, tr["text"], reply_to_message_id=update.message.message_id))

    target_uid = slide_reply_targets.get(chat_id)
    if target_uid and uid == target_uid and not is_admin(uid):
        mid = update.message.message_id
        for b in (all_bot_instances or [context.bot]):
            asyncio.create_task(_slide_reply_burst(b, chat_id, mid, count=5))

async def title_change_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.effective_chat: return
    chat_id = update.effective_chat.id
    changer = update.message.from_user
    changer_id = changer.id if changer else 0
    our_bot_ids = {getattr(b, "id", 0) for b in all_bot_instances if b}
    if chat_id in ncdel_chats and changer_id not in our_bot_ids and not is_admin(changer_id):
        try: await update.message.delete()
        except Exception: pass
    if chat_id in ncwar_targets and _is_primary_bot(context) and changer_id not in our_bot_ids:
        name = _build_name(ncwar_targets[chat_id], [""])
        for b in (all_bot_instances or [context.bot]):
            try: await b.set_chat_title(chat_id, name)
            except Exception: pass

async def gcs_info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows all registered groups in the fleet's active radar."""
    if not update.effective_user or not is_admin(update.effective_user.id): return
    if update.effective_chat and update.effective_chat.type in ("group", "supergroup"):
        if update.effective_chat.id not in known_chats:
            known_chats.add(update.effective_chat.id)
            save_groups(known_chats)

    total = len(known_chats)
    lines = [
        "╔═━─ 𓆩🌐𓆪 ─━═╗",
        f"『 ⚡ 𝐅𝐋𝐄𝐄𝐓 𝐀𝐂𝐓𝐈𝐕𝐄 𝐆𝐑𝐎𝐔𝐏𝐒 ({total}) 』",
        "╚═━─ 𖤐👑𖤐 ─━═╝\n"
    ]
    if not known_chats:
        lines.append("❌ *Koi groups record nahi hain!*\n👉 Kisi bhi group me `/ping` bhejein ya bot ko add karein.")
    else:
        for idx, cid in enumerate(list(known_chats), 1):
            lines.append(f"✦ `{idx}.` 🆔 `{cid}`")
        lines.append("\n🚀 *+allgcnc <text>* saare groups me run hoga!")
        lines.append("➕ Naya GC add karne ke liye: `+addgc <id>`")

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")

async def chat_member_updated_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c_update = update.my_chat_member or update.chat_member
    if not c_update or not c_update.chat:
        return
    chat = c_update.chat
    new_status = c_update.new_chat_member.status if c_update.new_chat_member else ""
    if chat.type in ("group", "supergroup"):
        if new_status in ("administrator", "member", "creator"):
            if chat.id not in known_chats:
                known_chats.add(chat.id)
                save_groups(known_chats)
                print(f"🎯 [AUTO-DETECT GC] Bot added/promoted in: {chat.title or chat.id} ({chat.id}) - Total GCs: {len(known_chats)}")
            if context.bot:
                register_bot_in_chat(chat.id, context.bot)
        elif new_status in ("left", "kicked"):
            known_chats.discard(chat.id)
            save_groups(known_chats)
            print(f"🚪 [GC REMOVED] Bot left: {chat.id}")

async def _any_chat_tracker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat and update.effective_chat.type in ("group", "supergroup"):
        cid = update.effective_chat.id
        if cid not in known_chats:
            known_chats.add(cid)
            save_groups(known_chats)
            print(f"📡 [TRACKER DETECTED GC] {update.effective_chat.title or cid} ({cid}) - Total: {len(known_chats)}")
        if context.bot:
            register_bot_in_chat(cid, context.bot)

def _register_handlers(app):
    cmds = {
        "start": start_cmd, "help": help_cmd, "panel": panel_cmd, "stop": stop_cmd,
        "ping": ping_cmd, "status": ping_cmd, "globalnc": globalnc_cmd, "allgcnc": globalnc_cmd, "stopglobalnc": stopglobalnc_cmd,
        "gcs": gcs_info_cmd, "groups": gcs_info_cmd,
        "zalgonc": zalgonc_handler, "gradientnc": gradientnc_handler,
        "addsudo": addsudo_cmd, "removesudo": removesudo_cmd, "sudolist": sudolist_cmd, "bots": bots_info_cmd, "joingc": joingc_cmd, "addgc": joingc_cmd, "folderjoin": folderjoin_cmd, "allpromote": allpromote_cmd, "promoteall": allpromote_cmd, "addbot": addbot_cmd, "addandpromote": addbot_cmd,
        "leave": leave_cmd, "purge": purge_cmd, "mute": mute_cmd, "ncdel": ncdel_cmd, "ncwar": ncwar_cmd, "stopncwar": stopncwar_cmd, "gclist": gclist_cmd, "mygc": mygc_cmd, "allgc": mygc_cmd,
        "restrict": restrict_cmd, "unrestrict": unrestrict_cmd, "stopreact": stopreact_cmd, "setmenuphoto": setmenuphoto_cmd, "setmenuvideo": setmenuvideo_cmd, "clearmenu": clearmenu_cmd,
        "slidereply": slidereply_cmd, "stopslidereply": stopslidereply_cmd, "slide": plus_slide, "spam": spam_cmd, "stopspam": stopspam_cmd,
        "autoreply": autoreply_cmd, "stopautoreply": stopautoreply_cmd, "targetreply": targetreply_cmd, "stoptargetreply": stoptargetreply_cmd,
        "customreact": customreact_cmd, "song": song_cmd, "floodbypass": floodbypass_cmd,
        "gcpfp": gcpfp_cmd, "allgcpfp": gcpfp_cmd, "globalgcpfp": gcpfp_cmd, "stopallgcpfp": stopgcpfp_cmd, "gcpfpadd": gcpfpadd_cmd, "gcpfpset": gcpfpset_cmd, "gcpfpclear": gcpfpclear_cmd, "stopgcpfp": stopgcpfp_cmd, "gcpfpstatus": gcpfpstatus_cmd,
        "botname": botname_cmd, "globalstop": globalstop_cmd, "globalannounce": globalannounce_cmd, "globalmute": globalmute_cmd, "globalunmute": globalunmute_cmd,
        "pairnc": pairnc_handler, "fakeban": fakeban_cmd, "fakekick": fakekick_cmd, "fakewarn": fakewarn_cmd, "fakedm": fakedm_cmd,
        "rnc": randnc_handler, "flamenc": burnc_handler, "lunanc": lundnc_handler, "randnc": randnc_handler, "burnc": burnc_handler,
        "ohyesnc": ohyesnc_handler, "aahnc": aahnc_handler, "horneync": horneync_handler, "purenc": purenc_handler, "stealthnc": stealthnc_handler,
        "lundnc": lundnc_handler, "bhosdanc": bhosdanc_handler, "areync": areync_handler, "hatnc": hatnc_handler, "crync": crync_handler,
        "aiimg": aiimg_cmd, "arnavnc": arnavnc_handler, "mentalnc": arnavnc_handler, "amritnc": kentonc_handler, "amritxnc": cr7nc_handler,
        "tripnc": tripnc_handler, "ultranc": ultranc_handler,
        "infernc": infernc_handler, "voidnc": voidnc_handler, "stormnc": stormnc_handler, "bloodnc": bloodnc_handler, "divinenc": divinenc_handler,
        "mental1": mental1_handler, "mental2": mental2_handler, "mental3": mental3_handler, "mental4": mental4_handler, "mental5": mental5_handler,
        "mental6": mental6_handler, "mental7": mental7_handler, "mental8": mental8_handler, "mental9": mental9_handler,         "mental10": mental10_handler,
        "tempmail": tempmail_cmd, "tmail": tempmail_cmd, "checkmail": checkmail_cmd,
        "rollcall": rollcall_cmd, "fleet": rollcall_cmd,
        "bodyguard": bodyguard_cmd, "bg": bodyguard_cmd,
        "iq": iq_cmd,
        "roast": roast_cmd,
        "stealthlock": stealthlock_cmd, "slock": stealthlock_cmd,
    }
    for cmd, h in cmds.items():
        if callable(h): app.add_handler(CommandHandler(cmd, _dedup(h)))
    app.add_handler(CallbackQueryHandler(_dedup(panel_callback), pattern=r"^panel:"))
    app.add_handler(CallbackQueryHandler(_dedup(tempmail_callback), pattern=r"^tmail:"))
    app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_TITLE, title_change_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, _dedup(message_handler)))
    app.add_handler(ChatMemberHandler(chat_member_updated_handler, ChatMemberHandler.MY_CHAT_MEMBER))
    app.add_handler(ChatMemberHandler(chat_member_updated_handler, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL, _any_chat_tracker), group=-1)

async def run_bots():
    global all_bot_instances, all_apps
    all_tokens = get_base_tokens() + [t for t in extra_tokens if t not in get_base_tokens()]
    print(f"🚀 Starting {len(all_tokens)} bots... (AMRIT MENTAL UPGRADED FULL)")
    from telegram.request import HTTPXRequest
    req_cfg = HTTPXRequest(connection_pool_size=500, read_timeout=30, write_timeout=30)
    for token in all_tokens:
        if "YOUR_BOT" in token: continue
        try:
            app = Application.builder().token(token).request(req_cfg).build()
            _register_handlers(app)
            await app.initialize()
            await app.start()
            if app.updater:
                await app.updater.start_polling(drop_pending_updates=False, allowed_updates=Update.ALL_TYPES)
            all_apps.append(app)
            all_bot_instances.append(app.bot)
            try:
                me = await app.bot.get_me()
                print(f"✅ @{me.username} Ready")
            except Exception: print("✅ Bot online")
        except Exception as e: print(f"❌ Error token {token[:15]}...: {e}")

    print(f"🎯 Full Fleet online ({len(all_bot_instances)} bots). Uptime: {get_uptime()}")
    try: await asyncio.Event().wait()
    finally:
        for app in all_apps:
            try: await app.stop(); await app.shutdown()
            except Exception: pass

def _auto_install_modules():
    import subprocess, sys
    for pkg in ["python-telegram-bot[all]", "telethon"]:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--quiet", "--upgrade", "--break-system-packages", pkg], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception: pass

def _setup_userbot_on_startup():
    """Checks if Userbot is configured. If running in terminal and missing, guides 1-time login."""
    import sys
    global HAS_TELETHON, USERBOT_API_ID, USERBOT_API_HASH, USERBOT_SESSION
    try:
        from telethon.sync import TelegramClient
        from telethon.sessions import StringSession
        HAS_TELETHON = True
    except ImportError:
        _auto_install_modules()
        try:
            from telethon.sync import TelegramClient
            from telethon.sessions import StringSession
            HAS_TELETHON = True
        except ImportError:
            HAS_TELETHON = False
            return

    api_id = USERBOT_API_ID or int(os.environ.get("USERBOT_API_ID") or os.environ.get("TELEGRAM_API_ID") or "0")
    api_hash = USERBOT_API_HASH or os.environ.get("USERBOT_API_HASH") or os.environ.get("TELEGRAM_API_HASH") or ""
    session_str = USERBOT_SESSION or os.environ.get("USERBOT_SESSION") or os.environ.get("STRING_SESSION") or ""

    if (not api_id or not api_hash or not session_str) and os.path.exists("userbot_creds.json"):
        try:
            with open("userbot_creds.json", "r", encoding="utf-8") as f:
                d = json.load(f)
                if not api_id: api_id = int(d.get("api_id", 0))
                if not api_hash: api_hash = d.get("api_hash", "")
                if not session_str: session_str = d.get("string_session", "")
        except Exception: pass

    has_file = os.path.exists("amrit_userbot.session")
    if api_id and api_hash and (session_str or has_file):
        try:
            sess = StringSession(session_str) if session_str else "amrit_userbot"
            cl = TelegramClient(sess, api_id, api_hash)
            cl.connect()
            if cl.is_user_authorized():
                me = cl.get_me()
                print(f"⚡ [USERBOT ACTIVE] Logged in as: {me.first_name} (@{me.username or me.id})")
                print("⚡ [USERBOT ACTIVE] Zero-Touch Folder Join & Mass Auto-Admin Ready! 🚀")
                cl.disconnect()
                return
            cl.disconnect()
        except Exception as e:
            print(f"⚠️ Userbot check warning: {e}")

    # If running interactively in terminal (VPS / RDP / SSH) and not logged in yet:
    if sys.stdin and sys.stdin.isatty():
        print("\n" + "═"*65)
        print("  ⚡ AMRIT MENTAL - INTEGRATED USERBOT SETUP (1-TIME SETUP)")
        print("═"*65)
        print("📌 Userbot account login zaroori hai taaki Folder me bots Auto-Add")
        print("   aur sabhi GCs me Auto-Admin promote ho sakein!\n")
        try:
            ask_id = input(f"👉 Enter API_ID [{api_id or 'Press Enter to Skip'}]: ").strip()
            if ask_id: api_id = int(ask_id)
            if not api_id:
                print("⏩ Skipping Userbot setup (Running Bots Only)...\n")
                return

            ask_hash = input(f"👉 Enter API_HASH [{api_hash[:6] + '...' if api_hash else 'Required'}]: ").strip()
            if ask_hash: api_hash = ask_hash
            if not api_hash:
                print("⏩ Skipping Userbot setup (Running Bots Only)...\n")
                return

            string_sess = StringSession()
            cl = TelegramClient(string_sess, api_id, api_hash)
            print("\n📲 Telegram Phone Number & OTP verification starting...")
            cl.start()
            me = cl.get_me()
            saved_str = string_sess.save()

            with open("userbot_creds.json", "w", encoding="utf-8") as f:
                json.dump({
                    "api_id": api_id,
                    "api_hash": api_hash,
                    "string_session": saved_str,
                    "user_id": me.id
                }, f, indent=2)

            file_cl = TelegramClient("amrit_userbot", api_id, api_hash)
            file_cl.start()
            file_cl.disconnect()
            cl.disconnect()

            USERBOT_API_ID = api_id
            USERBOT_API_HASH = api_hash
            USERBOT_SESSION = saved_str

            print(f"\n🎉 USERBOT LOGIN SUCCESSFUL: {me.first_name} (@{me.username or me.id})")
            print("💾 Saved to userbot_creds.json & amrit_userbot.session!")
            print("🚀 Ab Main Bot aur Userbot dono ek saath host ho rahe hain!\n" + "═"*65 + "\n")
        except Exception as e:
            print(f"❌ Userbot setup error: {e}")
            print("⏩ Continuing with Bot Fleet...\n")

if __name__ == "__main__":
    _auto_install_modules()
    _setup_userbot_on_startup()
    try: asyncio.run(run_bots())
    except KeyboardInterrupt: pass
