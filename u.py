# < ꪑᴇxxꪗ  ><   ꪜˣ  >
import asyncio
import os
import sys
import time
import json
import random
import logging
import traceback
import re
import math
import datetime
import urllib.parse
from typing import Dict, Set, Optional, Any, List, Union
from io import BytesIO
import glob as _glob

import requests
import qrcode
from gtts import gTTS
import yt_dlp

from telethon import TelegramClient, events, functions, types
from telethon.errors import FloodWaitError, RPCError
from telethon.tl.functions.channels import EditBannedRequest, CreateChannelRequest, InviteToChannelRequest, EditAdminRequest, EditTitleRequest, EditPhotoRequest
from telethon.tl.functions.messages import CreateChatRequest, AddChatUserRequest, EditChatAdminRequest, EditChatTitleRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights, InputUser

# ─────────────────────────────────────────────────────────────────
#  LOGGING
# ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("mexxybotV6")

# ─────────────────────────────────────────────────────────────────
#  PATH SETUP
# ─────────────────────────────────────────────────────────────────
BASE_DIR = os.getcwd()
DOWNLOAD_PATH = os.path.join(BASE_DIR, "downloads")
TEMP_PATH = os.path.join(BASE_DIR, "temp")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)
os.makedirs(TEMP_PATH, exist_ok=True)

# ─────────────────────────────────────────────────────────────────
#  CONFIG  (env vars preferred; hardcoded as fallback)
# ─────────────────────────────────────────────────────────────────
API_ID   = int(os.environ.get("TG_API_ID",   "API ID "))
API_HASH = os.environ.get("TG_API_HASH",     "API HASH")
OWNER_ID = int(os.environ.get("TG_OWNER_ID", "USER ID"))
SESSION  = os.environ.get("TG_SESSION",      "MEXXY.JSON")

# Optional YouTube auth for .music
YTDLP_COOKIES_FILE    = os.environ.get("YTDLP_COOKIES_FILE", "").strip()
YTDLP_COOKIES_BROWSER = os.environ.get("YTDLP_COOKIES_BROWSER", "").strip()

# Gemini is used by .ask. Create a free-tier key in Google AI Studio, then set
# GEMINI_API_KEY in the environment that starts this script. Never hard-code it.
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6IX-95BeDqO-eq01Ylybvo6p3yfLvYFHGf1VQe3DbWvNQ").strip()
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()

# Saved bot usernames
MAX_SAVED_BOTS = 10
DEFAULT_BOT_USERNAMES = [
   BOT USERNAME 
][:MAX_SAVED_BOTS]

bot = TelegramClient(
    SESSION, API_ID, API_HASH,
    auto_reconnect=True,
    connection_retries=10,
    retry_delay=3,
)

# ─────────────────────────────────────────────────────────────────
#  STORAGE FILES
# ─────────────────────────────────────────────────────────────────
ADMINS_FILE      = "admins.json"
NOTES_FILE       = "notes.json"
BANNER_FILE      = "banner_msg_id.txt"
MRAID_FILE       = "mraid_msg_id.txt"
MENU_VIDEOS_FILE = "menu_videos.json"
BOT_NAMES_FILE   = "bot_names.json"
WELCOME_FILE     = "welcome.json"
MUTED_FILE       = "muted_users.json"
GMUTED_FILE      = "global_muted.json"
TITLES_FILE      = "locked_titles.json"

# ─────────────────────────────────────────────────────────────────
#  DEFAULT VIDEO BANNERS FOR MENUS (High quality aesthetic MP4/GIFs)
# ─────────────────────────────────────────────────────────────────
DEFAULT_MENU_VIDEOS = {
    "0": "https://raw.githubusercontent.com/Telegram-Userbots/Media/main/menu_main.mp4",
    "1": "https://raw.githubusercontent.com/Telegram-Userbots/Media/main/menu_raid.mp4",
    "2": "https://raw.githubusercontent.com/Telegram-Userbots/Media/main/menu_admin.mp4",
    "3": "https://raw.githubusercontent.com/Telegram-Userbots/Media/main/menu_tools.mp4",
    "4": "https://raw.githubusercontent.com/Telegram-Userbots/Media/main/menu_extra.mp4",
}

# ─────────────────────────────────────────────────────────────────
#  RUNTIME STATE
# ─────────────────────────────────────────────────────────────────
admins:            Set[int]                       = set()
notes:             Dict[int, str]                 = {}
menu_banner_msg:   Optional[tuple]                = None   # (chat_id, msg_id)
menu_videos:       Dict[str, Any]                 = DEFAULT_MENU_VIDEOS.copy()
mraid_media_msg:   Optional[tuple]                = None   # (chat_id, msg_id)
auto_react_emoji:  Optional[str]                  = None
bot_usernames:     List[str]                      = DEFAULT_BOT_USERNAMES.copy()

# Mutes structure:
# local_mutes: {(chat_id, user_id): expiry_timestamp or None}
# global_mutes: {user_id: expiry_timestamp or None}
local_muted_store:  Dict[tuple[int, int], Optional[float]] = {}
global_muted_store: Dict[int, Optional[float]]            = {}

# Group Title Lock state. Automatic deletion of title/name-change notices is
# intentionally disabled; deletion now requires an explicit .delnc command.
del_title_enabled:  bool                          = False
locked_group_titles: Dict[int, str]                = {}

reply_users:       Set[int]                       = set()
rr_users:          Set[int]                       = set()
flag_users:        Set[int]                       = set()
hrr_users:         Set[int]                       = set()
replygod_users:    Set[int]                       = set()
replyvx_users:     Dict[int, Dict[str, Any]]      = {}
abuse_users:       Set[int]                       = set()
abuse2_users:      Set[int]                       = set()
slap_users:        Set[int]                       = set()
kick_users:        Set[int]                       = set()
spam_users:        Set[int]                       = set()
media_raid_users:  Set[int]                       = set()
bomb_users:        Set[int]                       = set()
slide_users:       Dict[int, Dict[str, Any]]      = {}
clone_reply_users: Set[int]                       = set()

SLIDE_EMOJIS: List[str] = ["🔥","💀","⚡","👊","🗡️","💣","😈","🖕","☠️","🤬","💢","🩸"]

spray_tasks:  Dict[int, asyncio.Task]            = {}
group_locks:  Set[int]                           = set()

START_TIME   = time.time()
SPRAY_DELAY  = 5

# Clone engine
CLONE_ACTIVE:  bool         = False
LAST_CLONE_ID: Optional[int] = None
CLONE_DATA: Dict[str, Any]  = {
    "name": None, "last": None,
    "username": None, "bio": None, "photo_bytes": None,
}
CLONE_RAID_TASK: Optional[asyncio.Task] = None

# FastGC engine
FASTGC_STATE: Dict[str, Any] = {
    "active": False, "template": None,
    "task": None, "chat_id": None,
}
GC_FAST_INTERVAL = 1
GC_FAST_EMOJIS = [
    "❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎",
    "🩷","🩵","🩶","💖","💘","💝","💗","💓","💞",
    "💕","💟","❣️","❤️‍🔥","❤️‍🩹",
]

# ─────────────────────────────────────────────────────────────────
#  FONT & TYPOGRAPHY ENGINES
# ─────────────────────────────────────────────────────────────────
_SC = {
    'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ','h':'ʜ','i':'ɪ',
    'j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ',
    's':'s','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ',
}

_BOLD_SANS = {
    'A':'𝐀','B':'𝐁','C':'𝐂','D':'𝐃','E':'𝐄','F':'𝐅','G':'𝐆','H':'𝐇','I':'𝐈',
    'J':'𝐉','K':'𝐊','L':'𝐋','M':'𝐌','N':'𝐍','O':'𝐎','P':'𝐏','Q':'𝐐','R':'𝐑',
    'S':'𝐒','T':'𝐓','U':'𝐔','V':'𝐕','W':'𝐖','X':'𝐗','Y':'𝐘','Z':'𝐙',
    'a':'𝐚','b':'𝐛','c':'𝐜','d':'𝐝','e':'𝐞','f':'𝐟','g':'𝐠','h':'𝐡','i':'𝐢',
    'j':'𝐣','k':'𝐤','l':'𝐥','m':'𝐦','n':'𝐧','o':'𝐨','p':'𝐩','q':'𝐪','r':'𝐫',
    's':'𝐬','t':'𝐭','u':'𝐮','v':'𝐯','w':'𝐰','x':'𝐱','y':'𝐲','z':'𝐳',
    '0':'𝟎','1':'𝟏','2':'𝟐','3':'𝟑','4':'𝟒','5':'𝟓','6':'𝟔','7':'𝟕','8':'𝟖','9':'𝟗'
}

def to_small_caps(text: str) -> str:
    """Convert text characters to small caps."""
    return "".join(_SC.get(c.lower(), c) for c in text)

def to_bold_sans(text: str) -> str:
    """Convert ASCII text to mathematical bold sans-serif."""
    return "".join(_BOLD_SANS.get(c, c) for c in text)

def to_authority_style(text: str) -> str:
    """AᴛʜᴏRɪᴛʏ style — styled caps & small-caps blend."""
    result = []
    for word in text.split(" "):
        idx = 0
        word_out = []
        for ch in word:
            if ch.isalpha():
                if idx % 4 == 0:
                    word_out.append(ch.upper())
                else:
                    word_out.append(_SC.get(ch.lower(), ch))
                idx += 1
            else:
                word_out.append(ch)
        result.append("".join(word_out))
    return " ".join(result)

def to_aesthetic_font(text: str) -> str:
    """
    Uniform aesthetic font transformer.
    Protects markdown links, backticks, emojis, and placeholders like {user}, {chat}, {time}, {date}.
    """
    if not text:
        return ""
    # Pattern to match protected blocks
    protected_pattern = r"(https?://\S+|\{[a-zA-Z0-9_]+\}|`[^`]+`|\@\w+|\[[^\]]+\]\([^\)]+\)|<[^>]+>)"
    tokens = re.split(protected_pattern, text)
    out = []
    for token in tokens:
        if not token:
            continue
        if re.match(protected_pattern, token):
            out.append(token)
        else:
            # Transform text chunk to small caps & bold accents
            out.append("".join(_SC.get(c.lower(), c) for c in token))
    return "".join(out)

BRAND       = "ꪑᴇxxꪗ 𝐀ᴜᴛʜᴏʀɪᴛʏ V6"
BRAND_SHORT = "ꪑᴇxxꪗ"

async def safe_edit(event, text: str):
    """Safely edit outgoing message or reply with styled font."""
    text = to_aesthetic_font(text)
    if not text: return None
    try:
        return await event.edit(text)
    except Exception:
        try:
            msg = await event.reply(text)
            if getattr(event, "out", False):
                try: await event.delete()
                except: pass
            return msg
        except: return None

# ─────────────────────────────────────────────────────────────────
#  JSON & PERSISTENCE HELPERS
# ─────────────────────────────────────────────────────────────────
def _load_json(path: str, default):
    try:
        if os.path.isfile(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"[JSON LOAD] {path}: {e}")
    return default

def _save_json(path: str, data):
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"[JSON SAVE] {path}: {e}")

def load_admins():
    global admins
    data = _load_json(ADMINS_FILE, [])
    admins = {int(x) for x in data if str(x).lstrip("-").isdigit()}

def save_admins():
    _save_json(ADMINS_FILE, sorted(admins))

def is_admin(uid: int) -> bool:
    return bool(uid) and (uid == OWNER_ID or uid in admins)

def load_notes():
    global notes
    raw = _load_json(NOTES_FILE, {})
    notes = {int(k): str(v) for k, v in raw.items()}

def save_notes():
    _save_json(NOTES_FILE, {str(k): v for k, v in notes.items()})

def load_menu_videos():
    global menu_videos
    data = _load_json(MENU_VIDEOS_FILE, {})
    if isinstance(data, dict):
        menu_videos.update(data)

def save_menu_videos():
    _save_json(MENU_VIDEOS_FILE, menu_videos)

def load_mutes():
    global local_muted_store, global_muted_store
    raw_local = _load_json(MUTED_FILE, {})
    local_muted_store.clear()
    for key, expiry in raw_local.items():
        if ":" in key:
            c, u = key.split(":", 1)
            local_muted_store[(int(c), int(u))] = expiry
    raw_global = _load_json(GMUTED_FILE, {})
    global_muted_store.clear()
    for u, expiry in raw_global.items():
        global_muted_store[int(u)] = expiry

def save_mutes():
    raw_local = {f"{c}:{u}": exp for (c, u), exp in local_muted_store.items()}
    _save_json(MUTED_FILE, raw_local)
    raw_global = {str(u): exp for u, exp in global_muted_store.items()}
    _save_json(GMUTED_FILE, raw_global)

def load_locked_titles():
    global locked_group_titles
    raw = _load_json(TITLES_FILE, {})
    locked_group_titles = {int(k): v for k, v in raw.items()}

def save_locked_titles():
    _save_json(TITLES_FILE, {str(k): v for k, v in locked_group_titles.items()})

def _normalise_bot_username(name: str) -> Optional[str]:
    name = (name or "").strip().strip(",")
    if not name: return None
    if name.startswith("https://t.me/"): name = name.rsplit("/", 1)[-1]
    if name.startswith("t.me/"): name = name.rsplit("/", 1)[-1]
    name = name.split("?", 1)[0].strip()
    if not name.startswith("@"): name = "@" + name
    if not re.fullmatch(r"@[A-Za-z0-9_]{5,32}", name): return None
    return name

def _parse_bot_usernames(raw: str) -> List[str]:
    parsed: List[str] = []
    seen = set()
    for part in re.split(r"[\s,;]+", raw or ""):
        username = _normalise_bot_username(part)
        if username and username.lower() not in seen:
            parsed.append(username)
            seen.add(username.lower())
        if len(parsed) >= MAX_SAVED_BOTS: break
    return parsed

def load_bot_usernames():
    global bot_usernames
    data = _load_json(BOT_NAMES_FILE, DEFAULT_BOT_USERNAMES)
    if isinstance(data, dict): data = data.get("bots", [])
    if isinstance(data, str): bot_usernames = _parse_bot_usernames(data)
    elif isinstance(data, list): bot_usernames = _parse_bot_usernames(" ".join(str(x) for x in data))
    else: bot_usernames = DEFAULT_BOT_USERNAMES.copy()
    bot_usernames = bot_usernames[:MAX_SAVED_BOTS]

def save_bot_usernames():
    _save_json(BOT_NAMES_FILE, bot_usernames[:MAX_SAVED_BOTS])

def _bots_from_arg_or_saved(arg: str) -> List[str]:
    bots = _parse_bot_usernames(arg)
    return bots or bot_usernames[:MAX_SAVED_BOTS]

def _load_msg_ref(path: str) -> Optional[tuple]:
    try:
        if os.path.isfile(path):
            raw = open(path).read().strip()
            if ":" in raw:
                c, m = raw.split(":", 1)
                return (int(c), int(m))
    except Exception as e:
        logger.error(f"[MSG REF LOAD] {path}: {e}")
    return None

def _save_msg_ref(path: str, ref: Optional[tuple]):
    try:
        if ref:
            with open(path, "w") as f: f.write(f"{ref[0]}:{ref[1]}")
        elif os.path.isfile(path):
            os.remove(path)
    except Exception as e:
        logger.error(f"[MSG REF SAVE] {path}: {e}")

def load_banner():
    global menu_banner_msg
    menu_banner_msg = _load_msg_ref(BANNER_FILE)

def save_banner():
    _save_msg_ref(BANNER_FILE, menu_banner_msg)

def load_mraid_media():
    global mraid_media_msg
    mraid_media_msg = _load_msg_ref(MRAID_FILE)

def save_mraid_media():
    _save_msg_ref(MRAID_FILE, mraid_media_msg)

# ─────────────────────────────────────────────────────────────────
#  UNIVERSAL TARGET & TIME RESOLVER
# ─────────────────────────────────────────────────────────────────
async def get_targets(event, arg: str = "") -> Set[int]:
    targets: Set[int] = set()
    if event.is_reply:
        try:
            r = await event.get_reply_message()
            if r and r.sender_id:
                targets.add(int(r.sender_id))
        except: pass
    for part in (arg or "").strip().split():
        if not part or part.startswith("-"): continue
        if part.isdigit():
            targets.add(int(part))
            continue
        try:
            ent = await bot.get_entity(part)
            if getattr(ent, "id", None):
                targets.add(int(ent.id))
        except: pass
    try:
        me = await bot.get_me()
        targets.discard(me.id)
    except: pass
    return targets

def parse_time_duration(time_str: str) -> Optional[float]:
    """Parse time string like 10s, 5m, 2h, 1d into seconds duration."""
    time_str = (time_str or "").strip().lower()
    if not time_str: return None
    match = re.match(r"^(\d+)\s*([smhd])?$", time_str)
    if not match: return None
    val = int(match.group(1))
    unit = match.group(2) or "s"
    mult = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    return float(val * mult[unit])

# ─────────────────────────────────────────────────────────────────
#  COMMAND DECORATOR  (Supports Owner & Added Bot Admins!)
# ─────────────────────────────────────────────────────────────────
def cmd(pattern: str, needs_reply: bool = False, group_only: bool = False, owner_only: bool = False):
    regex = rf"^\.{re.escape(pattern)}(?:\s+(.+))?$"

    def decorator(func):
        # Trigger on incoming and outgoing to allow added bot admins to execute commands!
        @bot.on(events.NewMessage(pattern=re.compile(regex, re.I | re.S)))
        async def _handler(event):
            sender_id = event.sender_id
            if not sender_id: return
            
            # Authorization check: Message must be outgoing from self OR sent by an authorized admin
            if not (event.out or is_admin(sender_id)):
                return
            
            if owner_only and sender_id != OWNER_ID:
                return await safe_edit(event, "❌ **𝐎𝐰𝐧𝐞𝐫 𝐎𝐧𝐥𝐲 𝐂𝐨𝐦𝐦𝐚𝐧𝐝!**")
                
            if group_only and not event.is_group:
                return await safe_edit(event, "❌ **𝐆𝐫𝐨𝐮𝐩 𝐎𝐧𝐥𝐲!**")
                
            if needs_reply and not event.is_reply:
                return await safe_edit(event, "❌ **𝐑𝐞𝐩𝐥𝐲 𝐭𝐨 𝐚 𝐦𝐞𝐬𝐬𝐚𝐠𝐞 𝐟𝐢𝐫𝐬𝐭!**")
                
            m = re.match(regex, event.raw_text, re.I | re.S)
            arg = (m.group(1) or "").strip() if m else ""
            try:
                await func(event, arg)
            except FloodWaitError as fw:
                await safe_edit(event, f"⏳ **𝐅𝐥𝐨𝐨𝐝 𝐖𝐚𝐢𝐭 → {fw.seconds}s**")
            except Exception as e:
                logger.error(traceback.format_exc())
                await safe_edit(event, f"❌ `{str(e)[:70]}`")
        return func
    return decorator

# ─────────────────────────────────────────────────────────────────
#  FASTGC ENGINE
# ─────────────────────────────────────────────────────────────────
async def _fast_title_edit(chat_id, title):
    title = (title or "").strip()[:255]
    if not title: return False
    try:
        await bot(EditTitleRequest(channel=chat_id, title=title))
        return True
    except:
        try:
            await bot(EditChatTitleRequest(chat_id=chat_id, title=title))
            return True
        except Exception as e:
            logger.warning(f"[FastGC] title edit failed: {e}")
            return False

async def _gc_fast_loop(chat_id):
    try:
        while FASTGC_STATE.get("active"):
            template = FASTGC_STATE.get("template")
            if not template: break
            emoji = random.choice(GC_FAST_EMOJIS)
            ok = await _fast_title_edit(chat_id, template.replace("{emoji}", emoji))
            await asyncio.sleep(max(1, GC_FAST_INTERVAL) if ok else 5)
    except asyncio.CancelledError:
        pass
    except Exception as e:
        logger.error(f"[FastGC Loop] {e}")

# ─────────────────────────────────────────────────────────────────
#  REPLY TEXTS LISTS
# ─────────────────────────────────────────────────────────────────
ABUSE_TEXTS = [
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🧊〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈❄️〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🥶〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈☃️〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🌨️〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🌬️〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🧋〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🐻‍❄️〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🍧〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🍨〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈🌀〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
    "{user} 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘾𝙃𝙊𝘿 𝘿𝘼𝙇𝙀𝙉𝙂𝙀 𝙍𝙀 𓂃𓂃𓂃𓂃〉〈💨〉〈𓂃𓂃𓂃𓂃𓂃𓂃..!¡",
]

ABUSE2_TEXTS = [
    "{user} ˚⋆‌﹒Tᴇʀɪ Mᴀ Kɪ Xʜᴜᴅᴀʏɪ Nᴀʜɪ Rᴜᴋᴜɴɢᴀ Pᴀɢʟᴇ ⋆‌´𓂃🩵",
    "{user} ˚⋆‌﹒Tᴇʀɪ Mᴀ Kɪ Xʜᴜᴅᴀʏɪ Nᴀʜɪ Rᴜᴋᴜɴɢᴀ Pᴀɢʟᴇ ⋆‌´𓂃💙",
    "{user} ˚⋆‌﹒Tᴇʀɪ Mᴀ Kɪ Xʜᴜᴅᴀʏɪ Nᴀʜɪ Rᴜᴋᴜɴɢᴀ Pᴀɢʟᴇ ⋆‌´𓂃💜",
    "{user} ˚⋆‌﹒Tᴇʀɪ Mᴀ Kɪ Xʜᴜᴅᴀʏɪ Nᴀʜɪ Rᴜᴋᴜɴɢᴀ Pᴀɢʟᴇ ⋆‌´𓂃🖤",
    "{user} ˚⋆‌﹒Tᴇʀɪ Mᴀ Kɪ Xʜᴜᴅᴀʏɪ Nᴀʜɪ Rᴜᴋᴜɴɢᴀ Pᴀɢʟᴇ ⋆‌´𓂃🤍",
    "{user} ˚⋆‌﹒Tᴇʀɪ Mᴀ Kɪ Xʜᴜᴅᴀʏɪ Nᴀʜɪ Rᴜᴋᴜɴɢᴀ Pᴀɢʟᴇ ⋆‌´𓂃❤️",
]

SLAP_TEXTS = [
    "ﾒ𓂃 👋🏻 *sʟᴀᴘs {user} ᴡɪᴛʜ ᴀ ʟᴀʀɢᴇ ᴛʀᴏᴜᴛ!*",
    "ﾒ𓂃 👋🏻 *ɢɪᴠᴇs {user} ᴀ ʜᴀʀᴅ sʟᴀᴘ ᴏɴ ᴛʜᴇ ᴄʜᴇᴇᴋ!*",
    "ﾒ𓂃 👋🏻 *sʟᴀᴘs {user} sᴏ ʜᴀʀᴅ ᴛʜᴇʏ sᴘɪɴ ᴀʀᴏᴜɴᴅ!*",
    "ﾒ𓂃 👋🏻 *ᴜsᴇs ᴀ ʙʀɪᴄᴋ ᴛᴏ sʟᴀᴘ {user}!*",
    "ﾒ𓂃 👋🏻 *sʟᴀᴘs {user} ɪɴᴛᴏ ᴛʜᴇ ɴᴇxᴛ ᴅɪᴍᴇɴsɪᴏɴ!*",
]

REPLY_TEXTS = [
    "{user} ɴʏ ɴʏ ᴍᴀ ᴋᴜᴄʜ ɴʏ sᴜɴᴜɴɢᴀ ᴄᴜᴅᴇɢɪ ᴛᴏʜ ᴛᴇʀʏ ᴍᴀᴀ ʜᴇ ᴠᴏ ʙʜɪ ᴀᴘɴᴀ ꪑᴇxxꪗ ʙᴀᴀᴘ sᴀʏ🙄🙏",
    "ᴄᴀʙᴀʀɪ {user} ᴡᴀʟᴇ ᴋᴇ ʟᴀʀᴄᴇ sᴡɪᴘᴇ ғᴀsᴛ ᴍʀɢʏᴀ ᴄʏᴀ",
    "ᴏʏᴇ {user} ʙɪʜᴀʀɪ ᴛᴇʀʏ ᴀᴍɪ sᴇ ғʀᴏɢ ʀᴀᴄᴇ ᴋʀᴡᴀᴜ🤔🔥",
    "{user} ᴋᴀʟᴡᴇ ᴛᴇʀʏ ᴀᴍɪ ᴋɪ ʙʜᴏsᴅɪ ᴍ ʟᴜɴᴅ ɢɪʀᴀ ᴅᴜ ᴄʏᴀ🤔",
    "ʜᴀʀ ɢʜᴀᴅɪ {user} ᴛʀʏ ᴍᴀ ᴄᴜᴅᴇɢɪ 🕖🕐🕔🕑🕖🕑🕜🕗",
]

GOD_TEXTS = [
    "Aaj me {user} teri maa codke India co azaad crudnga 🇮🇳🥳",
    "Abe o {user} rndyke ❌💙💚💜💙",
    "Shut up {user} कुट्टिया ce son 😡✌🏿",
    "{user} Bohot cringe ey tu 🤮🤮🤮",
]

FLAG_EMOJIS = ["🇨🇫","🇦🇿","🇧🇪","🇧🇻","🇨🇭","🇨🇨","🇧🇹","🇧🇶","🇧🇮","🇦🇽","🇦🇲"]

# ─────────────────────────────────────────────────────────────────
#  INCOMING MESSAGE HANDLER  (Mutes, Raids, Anti-Title, Locks)
# ─────────────────────────────────────────────────────────────────
@bot.on(events.NewMessage(incoming=True))
async def _incoming_handler(event):
    sender_id = event.sender_id
    if not sender_id: return
    now = time.time()

    # ── Global mute check ──
    if sender_id in global_muted_store:
        exp = global_muted_store[sender_id]
        if exp is not None and now > exp:
            global_muted_store.pop(sender_id, None)
            save_mutes()
        else:
            try: await event.delete()
            except: pass
            return

    # ── Local mute check in chat ──
    if (event.chat_id, sender_id) in local_muted_store:
        exp = local_muted_store[(event.chat_id, sender_id)]
        if exp is not None and now > exp:
            local_muted_store.pop((event.chat_id, sender_id), None)
            save_mutes()
        else:
            try: await event.delete()
            except: pass
            return

    # ── Group lock (delete non-admin messages) ──
    if event.is_group and event.chat_id in group_locks:
        if not is_admin(sender_id):
            try: await event.delete()
            except: pass
            return

    # ── Auto-react ──
    if auto_react_emoji:
        try:
            await bot(functions.messages.SendReactionRequest(
                peer=event.peer_id,
                msg_id=event.id,
                reaction=[types.ReactionEmoji(emoticon=auto_react_emoji)],
            ))
        except: pass

    # ── Resolve sender name once for raids that use {user} ──
    _any_name_raid = (
        sender_id in abuse_users or sender_id in abuse2_users or
        sender_id in reply_users or sender_id in rr_users or
        sender_id in replygod_users or sender_id in slap_users or
        sender_id in bomb_users or sender_id in slide_users
    )
    _sender_name = "User"
    if _any_name_raid:
        try:
            _u = await bot.get_entity(sender_id)
            _sender_name = getattr(_u, "first_name", None) or getattr(_u, "username", None) or "User"
        except: pass

    # ── Media raid ──
    if sender_id in media_raid_users:
        try:
            if mraid_media_msg:
                await bot.forward_messages(event.chat_id, mraid_media_msg[1], mraid_media_msg[0])
            else:
                await event.reply(random.choice(REPLY_TEXTS).format(user=_sender_name))
        except: pass

    # ── Abuse raid ──
    if sender_id in abuse_users:
        try: await event.reply(random.choice(ABUSE_TEXTS).format(user=_sender_name))
        except: pass

    # ── Abuse2 raid ──
    if sender_id in abuse2_users:
        try: await event.reply(random.choice(ABUSE2_TEXTS).format(user=_sender_name))
        except: pass

    # ── Slap raid ──
    if sender_id in slap_users:
        try: await event.reply(random.choice(SLAP_TEXTS).format(user=_sender_name))
        except: pass

    # ── Kick raid ──
    if sender_id in kick_users:
        try:
            try:
                await bot(EditBannedRequest(
                    event.chat_id, sender_id,
                    ChatBannedRights(until_date=None, view_messages=True)
                ))
                await asyncio.sleep(0.3)
                await bot(EditBannedRequest(
                    event.chat_id, sender_id,
                    ChatBannedRights(until_date=None, view_messages=False)
                ))
            except Exception:
                try:
                    await bot.kick_participant(event.chat_id, sender_id)
                except Exception as ke:
                    if "admin" in str(ke).lower() or "rights" in str(ke).lower():
                        kick_users.discard(sender_id)
        except: pass

    # ── Reply raid ──
    if sender_id in reply_users:
        try: await event.reply(random.choice(REPLY_TEXTS).format(user=_sender_name))
        except: pass

    # ── RR raid ──
    if sender_id in rr_users:
        try:
            await event.reply(random.choice(REPLY_TEXTS).format(user=_sender_name))
            await bot(functions.messages.SendReactionRequest(
                peer=event.peer_id,
                msg_id=event.id,
                reaction=[types.ReactionEmoji(emoticon="🤣")],
            ))
        except: pass

    # ── Flag raid ──
    if sender_id in flag_users:
        try: await event.reply(random.choice(FLAG_EMOJIS) * random.randint(3, 8))
        except: pass

    # ── Heart raid ──
    if sender_id in hrr_users:
        try:
            await bot(functions.messages.SendReactionRequest(
                peer=event.peer_id,
                msg_id=event.id,
                reaction=[types.ReactionEmoji(emoticon=random.choice(["❤️","💖","💘","💝","🩷"]))],
            ))
        except: pass

    # ── God raid ──
    if sender_id in replygod_users:
        try: await event.reply(random.choice(GOD_TEXTS).format(user=_sender_name))
        except: pass

    # ── Bomb raid ──
    if sender_id in bomb_users:
        try:
            bomb = "".join(random.choices(
                ["💣","💥","🔥","⚡","😈","👹","☠️","🖕","🤡","💀","🧨","🌋"],
                k=random.randint(8, 15)
            ))
            await event.reply(f"{_sender_name} {bomb}")
        except: pass

    # ── Clone Reply ──
    if sender_id in clone_reply_users and event.raw_text:
        try: await event.reply(event.raw_text)
        except: pass

    # ── Slide Raid ──
    if sender_id in slide_users:
        data = slide_users[sender_id]
        try:
            emoji = data["emojis"][data["idx"] % len(data["emojis"])]
            data["idx"] += 1
            slide_text = data["text"].replace("{time}", str(random.randint(1, 12)))
            await event.reply(f"{emoji} {slide_text} {emoji}")
        except: pass

    # ── ReplyVX raid ──
    if sender_id in replyvx_users:
        data = replyvx_users[sender_id]
        if data["count"] > 0:
            try:
                await event.reply(data["text"])
                data["count"] -= 1
                if data["count"] <= 0:
                    del replyvx_users[sender_id]
            except: pass

# ─────────────────────────────────────────────────────────────────
#  GROUP TITLE CHANGE DELETER & ANTI-TITLE LOCK LISTENER
# ─────────────────────────────────────────────────────────────────
@bot.on(events.ChatAction())
async def _title_change_handler(event):
    if not event.is_group: return
    # Check if action is title change or title edited
    if getattr(event, "title_changed", False) or getattr(event, "new_title", None):
        # 1. Auto-delete title change service message ONLY if del_title_enabled is explicitly ON
        if del_title_enabled:
            try:
                await event.delete()
            except Exception as e:
                logger.warning(f"[DelTitle] Failed to delete service msg: {e}")

        # 2. Check title lock for this group
        chat_id = event.chat_id
        if chat_id in locked_group_titles:
            original_title = locked_group_titles[chat_id]
            actor = await event.get_user()
            if actor and not is_admin(actor.id):
                try:
                    await _fast_title_edit(chat_id, original_title)
                    logger.info(f"[TitleLock] Reverted group title in {chat_id} back to: {original_title}")
                except Exception as e:
                    logger.warning(f"[TitleLock] Failed to revert title: {e}")

# ─────────────────────────────────────────────────────────────────
#  HELPERS FOR MULTI-MENU WITH VIDEO/GIF BANNERS
# ─────────────────────────────────────────────────────────────────
async def send_menu_with_media(event, text: str, menu_id: str = "0"):
    """Send or edit menu text with media/video banner for specific menu page."""
    video_ref = menu_videos.get(str(menu_id))

    # ── 1. Try per-menu saved media ref (tuple = (chat_id, msg_id)) ──
    if isinstance(video_ref, (list, tuple)) and len(video_ref) == 2:
        try:
            msg = await bot.get_messages(int(video_ref[0]), ids=int(video_ref[1]))
            if msg and msg.media:
                await bot.send_file(event.chat_id, msg.media, caption=text)
                if event.out:
                    try: await event.delete()
                    except: pass
                return
        except Exception as e:
            logger.warning(f"[MenuMedia] Saved media fetch failed for menu {menu_id}: {e}")

    # ── 2. Try per-menu URL/file string banner ──
    if isinstance(video_ref, str) and video_ref:
        try:
            await bot.send_file(event.chat_id, video_ref, caption=text)
            if event.out:
                try: await event.delete()
                except: pass
            return
        except Exception as e:
            logger.warning(f"[MenuMedia] URL banner send failed for menu {menu_id}: {e}")

    # ── 3. Fallback: global banner (only used if no per-menu banner worked) ──
    if menu_banner_msg:
        try:
            msg = await bot.get_messages(menu_banner_msg[0], ids=menu_banner_msg[1])
            if msg and msg.media:
                await bot.send_file(event.chat_id, msg.media, caption=text)
                if event.out:
                    try: await event.delete()
                    except: pass
                return
        except: pass

    # ── 4. Plain text fallback ──
    await safe_edit(event, text)

# ─────────────────────────────────────────────────────────────────
#  ██████████  COMMANDS & MENUS  ██████████
# ─────────────────────────────────────────────────────────────────

# ── MASTER MENU (HUB) ─────────────────────────────────────────────
@cmd("menu")
@cmd("help")
async def _master_menu(event, _):
    text = (
        f"👁️‍🗨️ 『 **{BRAND} — MASTER HUB** 』 👁️‍🗨️\n"
        f"🌌 ━━━━━━━━━━━━━━━━━━━━ System Dashboard ━━━━━━━━━━━━━━━━━━━━ 🌌\n\n"
        f"🔮 **.menu1** / **.raidmenu**     ──  ⚡ `Cursed Raids & Attacks` (Abuse, Slap, Bomb, Slide)\n"
        f"⛩️ **.menu2** / **.adminmenu**    ──  👑 `Jujutsu Admin & Controls` (Mute, Lock, Ban, Title)\n"
        f"🧿 **.menu3** / **.utilitymenu**  ──  📡 `Cursed Tools & AI` (Music, Song, TTS, Ask AI, QR)\n"
        f"📜 **.menu4** / **.extramenu**    ──  🎭 `Sorcerer Profile & Auto` (Clone, Welcome, AFK, Target)\n\n"
        f"🌌 ━━━━━━━━━━━━━━━━━━━━ Quick Commands ━━━━━━━━━━━━━━━━━━━━ 🌌\n"
        f"⚡ **.ping**   • **.alive**   • **.status**   • **.stopall** (Emergency Stop All)\n"
        f"🖼️ **.setmenuvid <0-4>** ── Set video banner for any menu page!\n"
        f"✦ ─────────────────────────────────────────────────────── ✦"
    )
    await send_menu_with_media(event, text, "0")

# ── MENU 1: RAIDS & ATTACKS ─────────────────────────────────────────
@cmd("menu1")
@cmd("raidmenu")
async def _menu1(event, _):
    text = (
        f"🔮 『 **{BRAND} — CURSED ATTACKS (PAGE 1)** 』 🔮\n"
        f"🌌 ━━━━━━━━━━━━━━━━━━━━ Raid Arsenal ━━━━━━━━━━━━━━━━━━━━ 🌌\n\n"
        f"⚡ **.reply**   | **.sreply**   ── Continuous Reply Raid\n"
        f"⚡ **.abuse**   | **.sabuse**   ── Heavy Hindi Abuse Raid\n"
        f"⚡ **.abuse2**  | **.sabuse2**  ── Stylish Abuse Raid 2\n"
        f"⚡ **.slap**    | **.sslap**    ── Slap Raid Attack\n"
        f"⚡ **.bomb**    | **.sbomb**    ── Emoji Bomb Rapid Raid\n"
        f"⚡ **.mraid**   | **.smraid**   ── Media Raid (Forward saved media)\n"
        f"⚡ **.setmraid**| **.remmraid** ── Set/Remove Media for MRAID\n"
        f"⚡ **.replygod**| **.sgod**     ── God Level Reply Raid\n"
        f"⚡ **.rr**      | **.srr**      ── Reply + Laugh Reaction Raid\n"
        f"⚡ **.flag**    | **.sflag**    ── Flag Emoji Spam Raid\n"
        f"⚡ **.hrr**     | **.shrr**     ── Heart Reaction Raid\n"
        f"⚡ **.replyvx** | **.svx**      ── Custom Count Reply Raid (.replyvx <text> <cnt>)\n"
        f"⚡ **.spray**   | **.dspray**   ── Spray Message Loop (.spray <text>)\n"
        f"⚡ **.slideraid**| **.dslideraid** ── Cycling Emoji Text Raid (.slideraid <text>)\n"
        f"⚡ **.clonereply**| **.sclonereply** ── Mirror Target's Exact Text\n"
        f"🛑 **.stopall**                 ── Emergency Cancel All Active Raids!\n"
        f"✦ ─────────────────────────────────────────────────────── ✦"
    )
    await send_menu_with_media(event, text, "1")

# ── MENU 2: ADMIN & GROUP CONTROLS ──────────────────────────────────
@cmd("menu2")
@cmd("adminmenu")
async def _menu2(event, _):
    text = (
        f"⛩️ 『 **{BRAND} — ADMIN & GROUP CONTROL (PAGE 2)** 』 ⛩️\n"
        f"🌌 ━━━━━━━━━━━━━━━━━━━━ Authority Tools ━━━━━━━━━━━━━━━━━━━━ 🌌\n\n"
        f"👑 **.addadmin** | **.deladmin** | **.admins** ── Add/Remove Bot Admins\n"
        f"🔇 **.mute**     | **.unmute**                 ── Local Mute / Timed Mute (.mute 10m)\n"
        f"🌐 **.gmute**    | **.gunmute**                ── Global Mute (.gmute 1h)\n"
        f"📋 **.mutelist**                               ── Detailed Mute List & Time Remaining\n"
        f"🔒 **.lock**     | **.unlock**                 ── Lock/Unlock Chat Messages\n"
        f"🗑️ **.nc** | **.delnc**               ── Delete NC / Service messages on command (.nc on/off)\n"
        f"📌 **.locktitle**| **.unlocktitle**            ── Lock & Auto-Revert Group Name Changes\n"
        f"💥 **.purge**                                  ── Reply Purge / Count Purge (.purge 50)\n"
        f"🚫 **.ban**      | **.throw**                  ── Ban or Kick User from Chat\n"
        f"👞 **.kickraid** | **.skickraid**               ── Continuous Auto-Kick Target\n"
        f"⚡ **.fastgc**   | **.fastgc stop**            ── Rapid GC Title Changer (.fastgc set <title>)\n"
        f"🏗️ **.creategc** | **.createch**               ── Bulk Create Supergroups & Channels\n"
        f"🤖 **.addbot**   | **.promotebots**            ── Add & Promote Bot List with Full Admin Rights\n"
        f"🧹 **.removebots**                              ── Remove All Saved Bots from Chat\n"
        f"✦ ─────────────────────────────────────────────────────── ✦"
    )
    await send_menu_with_media(event, text, "2")

# ── MENU 3: UTILITY & AI ────────────────────────────────────────────
@cmd("menu3")
@cmd("utilitymenu")
async def _menu3(event, _):
    text = (
        f"🧿 『 **{BRAND} — TOOLS & AI (PAGE 3)** 』 🧿\n"
        f"🌌 ━━━━━━━━━━━━━━━━━━━━ Sorcerer Tools ━━━━━━━━━━━━━━━━━━━━ 🌌\n\n"
        f"🎵 **.music <song>**   ── Download Music from YouTube (High Quality)\n"
        f"🎶 **.song <song>**    ── Fast Spotify/JioSaavn Audio Downloader\n"
        f"🤖 **.ask <prompt>**   ── Gemini AI (free-tier API key required)\n"
        f"🎨 **.imagine <prompt>**── Free AI Image Generator (Flux Engine)\n"
        f"🗣️ **.tts <lang> <text>** ── Text-To-Speech Voice Generator (.tts hi namaste)\n"
        f"📷 **.qrcode <text>**  ── Generate QR Code Image\n"
        f"🌐 **.translate <lang> <text>** ── Translate Text (.translate hi Hello)\n"
        f"🌤 **.weather <city>** ── Real-time Weather & Temperature Report\n"
        f"📡 **.ip <address>**   ── Full IP Address Lookup & Geolocation\n"
        f"🧮 **.calc <expr>**    ── Advanced Math Calculator\n"
        f"📖 **.ud <word>**      ── Urban Dictionary Definition Lookup\n"
        f"📚 **.wiki <query>**   ── Wikipedia Summary Search\n"
        f"🔗 **.short <url>**    ── Shorten Long URLs\n"
        f"📡 **.speedtest**      ── Internet Download/Upload Speedtest\n"
        f"✦ ─────────────────────────────────────────────────────── ✦"
    )
    await send_menu_with_media(event, text, "3")

# ── MENU 4: PROFILE & AUTOMATION ────────────────────────────────────
@cmd("menu4")
@cmd("extramenu")
async def _menu4(event, _):
    text = (
        f"📜 『 **{BRAND} — AUTOMATION & PROFILE (PAGE 4)** 』 📜\n"
        f"🌌 ━━━━━━━━━━━━━━━━━━━━ Profile & Stealth ━━━━━━━━━━━━━━━━━━━━ 🌌\n\n"
        f"🎭 **.copy** @user      ── Clone Target's Name, Bio & Profile Photo\n"
        f"💾 **.save**            ── Save Original Profile Before Cloning\n"
        f"🔄 **.normal**          ── Restore Original Profile & Delete Cloned Photo\n"
        f"🤡 **.cloneraid** @user ── Continuous Auto-Reclone Profile Loop\n"
        f"🎉 **.setwelcome <txt>** ── Customize Aesthetic Welcome Card\n"
        f"🧪 **.welctest**        ── Test Welcome Message & Banner Output\n"
        f"🔕 **.welcoff** | **.welcon** ── Toggle Auto Welcome Greetings\n"
        f"🤖 **.autorespond**     ── Auto-Reply Rule Creator (.autorespond hi hello)\n"
        f"😴 **.afk <reason>**    ── Enable AFK Mode with Auto DM Reply\n"
        f"🎯 **.target <text>**   ── DM Auto-Reply with Photo + Custom Text\n"
        f"🗑️ **.nc** | **.delnc** ── Delete NC / Service messages on command (.nc on/off)\n"
        f"🛡️ **.safe** @user      ── Protect Users from Auto-Delete/Purges\n"
        f"📌 **.pin** | **.unpin** ── Pin/Unpin Messages\n"
        f"📝 **.setname** | **.setbio** ── Update Profile Name or Bio\n"
        f"💬 **.id**              ── Display Telegram Chat & User IDs\n"
        f"🔄 **.restart**         ── Full Userbot System Restart\n"
        f"✦ ─────────────────────────────────────────────────────── ✦"
    )
    await send_menu_with_media(event, text, "4")

# ── VIDEO BANNER CONFIGURATION COMMANDS ──────────────────────────────
@cmd("setmenuvid")
async def _setmenuvid(event, arg):
    global menu_videos
    parts = arg.split(" ", 1) if arg else []
    menu_id = parts[0].strip() if parts else "0"
    if menu_id not in ("0", "1", "2", "3", "4"):
        return await safe_edit(event, "❌ **Usage:** `.setmenuvid <0|1|2|3|4> [URL]`\n↳ Or reply to a video/GIF/photo with `.setmenuvid <0-4>`")

    url = parts[1].strip() if len(parts) > 1 else ""
    reply = await event.get_reply_message()

    # ── Save replied media to Saved Messages and store (chat_id, msg_id) tuple ──
    if reply and reply.media:
        await safe_edit(event, f"⏳ **Saving media banner for Menu {menu_id}...**")
        try:
            # Try forward to Saved Messages first (fastest)
            saved = await reply.forward_to("me")
        except Exception:
            try:
                # Fallback: download and re-upload
                data = await reply.download_media(file=bytes)
                if not data:
                    return await safe_edit(event, "❌ **Could not download the media!**")
                buf = BytesIO(data)
                buf.name = f"menu_{menu_id}_banner.mp4"
                saved = await bot.send_file("me", buf)
            except Exception as e:
                return await safe_edit(event, f"❌ **Failed to save media:** `{str(e)[:80]}`")
        # Store as [chat_id, msg_id] list (JSON-serializable)
        menu_videos[menu_id] = [saved.chat_id, saved.id]
        save_menu_videos()
        return await safe_edit(event, f"✅ **Media Banner Set for Menu {menu_id}!**\n↳ Saved to your Saved Messages (ID: `{saved.id}`)")

    # ── Save URL directly ──
    if url:
        menu_videos[str(menu_id)] = url
        save_menu_videos()
        return await safe_edit(event, f"✅ **Video URL Banner set for Menu {menu_id}:**\n`{url[:80]}`")

    await safe_edit(event, "❌ **Reply to a video/GIF/photo OR provide a video URL!**\n↳ Example: `.setmenuvid 1 https://files.catbox.moe/xxx.mp4`")

@cmd("remmenuvid")
async def _remmenuvid(event, arg):
    menu_id = arg.strip() if arg else "0"
    if menu_id in menu_videos:
        menu_videos[menu_id] = DEFAULT_MENU_VIDEOS.get(menu_id, "")
        save_menu_videos()
        await safe_edit(event, f"🗑️ **Banner for Menu {menu_id} reset to default.**")
    else:
        await safe_edit(event, "⚠️ **Invalid menu page ID.**")

# ── PING / ALIVE / STATUS ─────────────────────────────────────────
@cmd("ping")
async def _ping(event, _):
    t = time.time()
    m = await safe_edit(event, "🏓 𝐏𝐢𝐧𝐠𝐢𝐧𝐠...")
    ms = round((time.time() - t) * 1000, 2)
    await safe_edit(m, f"🏓 **𝐏𝐨𝐧𝐠!**\n⚡ **𝐋𝐚𝐭𝐞𝐧𝐜𝐲:** `{ms} ms`")

@cmd("alive")
async def _alive(event, _):
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    await safe_edit(event,
        f"🌟 **{BRAND}** ɪs ᴀʟɪᴠᴇ!\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏳ **Uptime:** `{h}h {m}m {s}s`\n"
        f"👑 **Owner:** `{BRAND_SHORT}`\n"
        f"🔧 **Version:** `v6.0 Ultimate Authority`\n"
        f"⚡ **Status:** `Operational & Fully Loaded`"
    )

@cmd("status")
async def _status(event, _):
    up = int(time.time() - START_TIME)
    h, r = divmod(up, 3600)
    m, s = divmod(r, 60)
    active_raids = sum([
        len(reply_users), len(rr_users), len(flag_users),
        len(hrr_users), len(replygod_users), len(replyvx_users),
        len(media_raid_users), len(kick_users), len(abuse_users), len(slap_users), len(bomb_users),
    ])
    await safe_edit(event,
        f"📊 **System Status**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⏳ **Uptime:** `{h}h {m}m {s}s`\n"
        f"👮 **Admins:** `{len(admins)}`\n"
        f"🔇 **Muted:** `{len(local_muted_store)}` local | `{len(global_muted_store)}` global\n"
        f"⚔️ **Active Raids:** `{active_raids}`\n"
        f"🔒 **Locked Groups:** `{len(group_locks)}`\n"
        f"📌 **Locked Titles:** `{len(locked_group_titles)}` | **Anti-Title:** `{'On' if del_title_enabled else 'Off'}`\n"
        f"📝 **Notes:** `{len(notes)}`\n"
        f"⚡ **FastGC:** `{'Active' if FASTGC_STATE['active'] else 'Off'}`\n"
        f"🤖 **Auto React:** `{auto_react_emoji or 'Off'}`\n"
        f"🎥 **Menu Banners:** `{len(menu_videos)} configured`"
    )

# ── BANNER COMMANDS ───────────────────────────────────────────────
@cmd("banner", needs_reply=True)
async def _banner(event, _):
    global menu_banner_msg
    reply = await event.get_reply_message()
    if not reply: return await safe_edit(event, "❌ Reply to a message!")
    await safe_edit(event, "⚡ Saving banner...")
    try:
        saved = None
        if reply.media:
            try: saved = await reply.forward_to("me")
            except:
                data = await reply.download_media(file=bytes)
                if data:
                    buf = BytesIO(data); buf.name = "banner"
                    saved = await bot.send_file("me", buf)
        if not saved:
            sender = await reply.get_sender()
            if sender:
                photo_bytes = await bot.download_profile_photo(sender, file=bytes)
                if photo_bytes:
                    buf = BytesIO(photo_bytes); buf.name = "banner.jpg"
                    saved = await bot.send_file("me", buf)
        if not saved: return await safe_edit(event, "❌ No media or photo found!")
        menu_banner_msg = (saved.chat_id, saved.id)
        save_banner()
        await safe_edit(event, f"🖼️ **Banner Set!** ID: `{saved.id}`\nShown with `.menu` automatically.")
    except Exception as e:
        await safe_edit(event, f"❌ `{str(e)[:60]}`")

@cmd("rembanner")
async def _rembanner(event, _):
    global menu_banner_msg
    if not menu_banner_msg: return await safe_edit(event, "⚠️ No banner set!")
    try: await bot.delete_messages(menu_banner_msg[0], [menu_banner_msg[1]])
    except: pass
    menu_banner_msg = None
    save_banner()
    await safe_edit(event, "🗑️ **Banner Removed!**")

# ── MEDIA RAID MEDIA SETTER ───────────────────────────────────────
@cmd("setmraid", needs_reply=True)
async def _setmraid(event, _):
    global mraid_media_msg
    reply = await event.get_reply_message()
    if not reply or not reply.media:
        return await safe_edit(event, "❌ Reply to a photo/video/gif!")
    await safe_edit(event, "⚡ Saving media raid media...")
    try:
        try: saved = await reply.forward_to("me")
        except:
            data = await reply.download_media(file=bytes)
            buf = BytesIO(data); buf.name = "mraid_media"
            saved = await bot.send_file("me", buf)
        mraid_media_msg = (saved.chat_id, saved.id)
        save_mraid_media()
        await safe_edit(event, f"📸 **MRaid Media Set!** ID: `{saved.id}`")
    except Exception as e:
        await safe_edit(event, f"❌ {e}")

@cmd("remmraid")
async def _remmraid(event, _):
    global mraid_media_msg
    if not mraid_media_msg: return await safe_edit(event, "⚠️ No mraid media set!")
    mraid_media_msg = None
    save_mraid_media()
    await safe_edit(event, "🗑️ **MRaid Media Removed!**")

# ── ADMIN MANAGEMENT ─────────────────────────────────────────────
@cmd("admins")
async def _admins(event, _):
    if not admins:
        return await safe_edit(event, "👮 **Admins:** None added yet.")
    lines = [f"👮 **Bot Admins ({len(admins)}):**\n━━━━━━━━━━━━━━━"]
    for uid in sorted(admins):
        try:
            u = await bot.get_entity(uid)
            name = getattr(u, "first_name", str(uid)) or str(uid)
            uname = f"@{u.username}" if getattr(u, "username", None) else f"`{uid}`"
            lines.append(f"• {name} ({uname})")
        except:
            lines.append(f"• `{uid}`")
    await safe_edit(event, "\n".join(lines))

@cmd("addadmin", owner_only=True)
async def _addadmin(event, arg):
    targets = await get_targets(event, arg)
    if not targets: return await safe_edit(event, "❌ Reply or provide user ID / @username!")
    added = []
    for uid in targets:
        admins.add(uid)
        added.append(str(uid))
    save_admins()
    await safe_edit(event, f"✅ **Admins Added:** `{', '.join(added)}`\nThey can now execute bot commands!")

@cmd("deladmin", owner_only=True)
async def _deladmin(event, arg):
    targets = await get_targets(event, arg)
    if not targets: return await safe_edit(event, "❌ Reply or provide user ID / @username!")
    removed = []
    for uid in targets:
        if uid in admins:
            admins.discard(uid)
            removed.append(str(uid))
    save_admins()
    await safe_edit(event, f"🗑️ **Admins Removed:** `{', '.join(removed) or 'None'}`")

# ── UPGRADED MUTE / UNMUTE SYSTEM ────────────────────────────────
@cmd("mute")
async def _mute(event, arg):
    parts = arg.split() if arg else []
    duration_str = None
    if parts and not parts[0].startswith("@") and not parts[0].isdigit():
        duration_str = parts[0]
        arg_clean = " ".join(parts[1:])
    else:
        arg_clean = arg
        if len(parts) >= 2 and (parts[-1].endswith(("s","m","h","d")) or parts[-1].isdigit()):
            duration_str = parts[-1]
            arg_clean = " ".join(parts[:-1])

    targets = await get_targets(event, arg_clean)
    if not targets: return await safe_edit(event, "❌ Reply or provide user ID / @username!")

    seconds = parse_time_duration(duration_str) if duration_str else None
    expiry = time.time() + seconds if seconds else None
    dur_text = f"for {duration_str}" if duration_str else "indefinitely"

    muted_list = []
    for uid in targets:
        local_muted_store[(event.chat_id, uid)] = expiry
        muted_list.append(str(uid))
        # Telegram permission mute if bot is admin
        try:
            until_date = datetime.datetime.fromtimestamp(expiry) if expiry else None
            await bot(EditBannedRequest(
                event.chat_id, uid,
                ChatBannedRights(until_date=until_date, send_messages=True)
            ))
        except: pass

    save_mutes()
    await safe_edit(event, f"🔇 **Muted:** `{', '.join(muted_list)}` in this chat {dur_text}.")

@cmd("unmute")
async def _unmute(event, arg):
    targets = await get_targets(event, arg)
    if not targets: return await safe_edit(event, "❌ Reply or provide user ID / @username!")
    unmuted_list = []
    for uid in targets:
        local_muted_store.pop((event.chat_id, uid), None)
        unmuted_list.append(str(uid))
        try:
            await bot(EditBannedRequest(
                event.chat_id, uid,
                ChatBannedRights(until_date=None, send_messages=False)
            ))
        except: pass
    save_mutes()
    await safe_edit(event, f"🔊 **Unmuted:** `{', '.join(unmuted_list)}` in this chat.")

@cmd("gmute")
async def _gmute(event, arg):
    parts = arg.split() if arg else []
    duration_str = parts[-1] if len(parts) >= 2 and parts[-1].endswith(("s","m","h","d")) else None
    arg_clean = " ".join(parts[:-1]) if duration_str else arg

    targets = await get_targets(event, arg_clean)
    if not targets: return await safe_edit(event, "❌ Reply or provide user ID / @username!")

    seconds = parse_time_duration(duration_str) if duration_str else None
    expiry = time.time() + seconds if seconds else None
    dur_text = f"for {duration_str}" if duration_str else "indefinitely"

    for uid in targets:
        global_muted_store[uid] = expiry
    save_mutes()
    await safe_edit(event, f"🌐🔇 **Global Muted:** `{', '.join(str(u) for u in targets)}` {dur_text}.")

@cmd("gunmute")
async def _gunmute(event, arg):
    targets = await get_targets(event, arg)
    if not targets: return await safe_edit(event, "❌ Reply or provide user ID / @username!")
    for uid in targets: global_muted_store.pop(uid, None)
    save_mutes()
    await safe_edit(event, f"🌐🔊 **Global Unmuted:** `{', '.join(str(u) for u in targets)}`.")

@cmd("mutelist")
async def _mutelist(event, _):
    now = time.time()
    lines = [f"📋 **MUTE LIST REPORT**\n━━━━━━━━━━━━━━━"]
    
    # Local Muted here
    local_here = []
    for (cid, uid), exp in list(local_muted_store.items()):
        if cid == event.chat_id:
            if exp and now > exp:
                local_muted_store.pop((cid, uid), None)
                continue
            rem = f"({int(exp - now)}s remaining)" if exp else "(permanent)"
            local_here.append(f"• `{uid}` {rem}")
            
    lines.append(f"🔇 **Local Muted (Here):** `{len(local_here)}`")
    if local_here: lines.extend(local_here)

    # Global Muted
    global_list = []
    for uid, exp in list(global_muted_store.items()):
        if exp and now > exp:
            global_muted_store.pop(uid, None)
            continue
        rem = f"({int(exp - now)}s remaining)" if exp else "(permanent)"
        global_list.append(f"• `{uid}` {rem}")

    lines.append(f"\n🌐🔇 **Global Muted:** `{len(global_list)}`")
    if global_list: lines.extend(global_list)

    save_mutes()
    await safe_edit(event, "\n".join(lines))

# ── GROUP NAME CHANGE DELETION & TITLE LOCK ───────────────────────
@cmd("deltitle")
async def _deltitle(event, arg):
    global del_title_enabled
    sub = (arg or "").strip().lower()
    if sub == "off":
        del_title_enabled = False
        await safe_edit(event, "🔕 **Auto-deletion of Group Title Changes Disabled.**")
    elif sub == "on":
        del_title_enabled = True
        await safe_edit(event, "🔔 **Auto-deletion of Group Title Changes Enabled!**")
    elif sub == "":
        return await _delete_named_message(event, arg)
    else:
        del_title_enabled = not del_title_enabled
        status = "Enabled" if del_title_enabled else "Disabled"
        await safe_edit(event, f"📌 **Group Title Change Deletion is now {status}.**")

@cmd("locktitle", group_only=True)
async def _locktitle(event, arg):
    chat_id = event.chat_id
    title_to_lock = arg.strip()
    if not title_to_lock:
        try:
            chat = await event.get_chat()
            title_to_lock = getattr(chat, "title", "")
        except: pass
    if not title_to_lock:
        return await safe_edit(event, "❌ Could not determine group title to lock!")
        
    locked_group_titles[chat_id] = title_to_lock
    save_locked_titles()
    await safe_edit(event, f"🔒 **Group Title Locked to:** `{title_to_lock}`\nAny unauthorized changes will be auto-reverted!")

@cmd("unlocktitle", group_only=True)
async def _unlocktitle(event, _):
    chat_id = event.chat_id
    if chat_id in locked_group_titles:
        locked_group_titles.pop(chat_id, None)
        save_locked_titles()
        await safe_edit(event, "🔓 **Group Title Unlocked.**")
    else:
        await safe_edit(event, "⚠️ **Group title was not locked.**")

# ── LOCK / UNLOCK ─────────────────────────────────────────────────
@cmd("lock", group_only=True)
async def _lock(event, _):
    chat = event.chat_id
    if chat in group_locks: return await safe_edit(event, "⚠️ Group already locked!")
    group_locks.add(chat)
    try:
        await bot(functions.messages.EditChatDefaultBannedRightsRequest(
            peer=chat,
            banned_rights=ChatBannedRights(until_date=None, send_messages=True),
        ))
    except: pass
    await safe_edit(event, "🔒 **Group Locked! Only admins can send messages.**")

@cmd("unlock", group_only=True)
async def _unlock(event, _):
    chat = event.chat_id
    group_locks.discard(chat)
    try:
        await bot(functions.messages.EditChatDefaultBannedRightsRequest(
            peer=chat,
            banned_rights=ChatBannedRights(until_date=None, send_messages=False),
        ))
    except: pass
    await safe_edit(event, "🔓 **Group Unlocked!**")

# ── PURGE ─────────────────────────────────────────────────────────
@cmd("purge")
async def _purge(event, arg):
    from_id = None
    if event.is_reply:
        try:
            reply = await event.get_reply_message()
            if reply: from_id = reply.id
        except: pass

    if from_id is not None:
        m = await safe_edit(event, "⚡ Purging from replied message...")
        deleted = 0
        ids_to_delete = []
        async for message in bot.iter_messages(event.chat_id, min_id=from_id - 1, max_id=event.id + 1):
            ids_to_delete.append(message.id)
        for i in range(0, len(ids_to_delete), 100):
            batch = ids_to_delete[i:i+100]
            try:
                await bot.delete_messages(event.chat_id, batch)
                deleted += len(batch)
            except: pass
        try: await m.delete()
        except: pass
        try:
            done = await event.respond(f"✅ **Purged {deleted} messages!**")
            await asyncio.sleep(3)
            await done.delete()
        except: pass
    else:
        count = min(int(arg), 500) if arg and arg.isdigit() else 100
        m = await safe_edit(event, f"⚡ Purging last {count} messages...")
        deleted = 0
        ids_to_delete = []
        async for message in bot.iter_messages(event.chat_id, limit=count):
            ids_to_delete.append(message.id)
        for i in range(0, len(ids_to_delete), 100):
            batch = ids_to_delete[i:i+100]
            try:
                await bot.delete_messages(event.chat_id, batch)
                deleted += len(batch)
            except: pass
        try: await m.delete()
        except: pass
        try:
            done = await event.respond(f"✅ **Purged {deleted} messages!**")
            await asyncio.sleep(3)
            await done.delete()
        except: pass

# ── THROW (KICK) & BAN ────────────────────────────────────────────
@cmd("nc")
@cmd("delnc")
@cmd("delmsg")
async def _delete_named_message(event, arg):
    """
    Delete Name Change / Service messages or specific messages on demand.

    Usage:
      .nc / .delnc                    -> Delete NC / Title Change service messages in group (or replied message)
      .nc on / .nc off                -> Toggle background auto-delete mode
      .nc <count>                     -> Delete up to <count> recent NC / service messages
      Reply with .nc / .delnc         -> Delete replied message immediately
      .delnc @username <message_id>   -> Delete verified user message by ID
    """
    global del_title_enabled
    arg = (arg or "").strip()
    sub_lower = arg.lower()

    if sub_lower == "off":
        del_title_enabled = False
        return await safe_edit(event, "🔕 **NC Auto-Delete Disabled (Runs on command only).**")
    elif sub_lower == "on":
        del_title_enabled = True
        return await safe_edit(event, "🔔 **NC Auto-Delete Enabled.**")

    # If replying to a message, delete that replied message
    if event.is_reply:
        try:
            reply_msg = await event.get_reply_message()
            if reply_msg:
                if arg and not arg.isdigit() and arg.startswith("@"):
                    try:
                        target = await bot.get_entity(arg)
                        if reply_msg.sender_id != target.id:
                            return await safe_edit(event, "❌ Sender verification failed.")
                    except Exception:
                        return await safe_edit(event, "❌ Target user not found.")
                
                await bot.delete_messages(event.chat_id, [reply_msg.id])
                try: await event.delete()
                except: pass
                return
        except Exception as e:
            return await safe_edit(event, f"❌ Failed to delete replied message: {e}")

    # Format: .delnc @username <message_id>
    parts = arg.split()
    if len(parts) == 2 and parts[1].isdigit() and int(parts[1]) > 0:
        target_ref, message_id = parts[0], int(parts[1])
        try:
            message = await bot.get_messages(event.chat_id, ids=message_id)
            if not message:
                return await safe_edit(event, "❌ Message not found in this chat.")
            if not getattr(message, "sender_id", None):
                return await safe_edit(event, "❌ That message has no user sender.")
            target = await bot.get_entity(target_ref)
            if message.sender_id != target.id:
                return await safe_edit(event, "❌ Sender verification failed.")
            await bot.delete_messages(event.chat_id, [message.id])
            return await safe_edit(event, f"✅ Deleted verified message {message.id} from user {target.id}.")
        except Exception as e:
            return await safe_edit(event, f"❌ Error deleting message: {e}")

    # On command in group without reply: delete recent NC / service messages
    if event.is_group:
        limit = 100
        delete_count = int(parts[0]) if parts and parts[0].isdigit() else 20
        service_ids = []

        try:
            async for msg in bot.iter_messages(event.chat_id, limit=limit):
                if msg.action:
                    service_ids.append(msg.id)
                    if len(service_ids) >= delete_count:
                        break

            if service_ids:
                deleted = 0
                for i in range(0, len(service_ids), 100):
                    batch = service_ids[i:i+100]
                    await bot.delete_messages(event.chat_id, batch)
                    deleted += len(batch)
                
                try: await event.delete()
                except: pass
                
                done = await event.respond(f"🧹 **NC Delete:** Deleted `{deleted}` Name Change / Service messages!")
                await asyncio.sleep(3)
                try: await done.delete()
                except: pass
                return
            else:
                return await safe_edit(event, "ℹ️ No NC / Title Change service messages found in recent history.")
        except Exception as e:
            return await safe_edit(event, f"❌ Error performing NC delete: {e}")

    await safe_edit(event, "❌ Usage: `.nc` (in group/reply) or `.nc on/off` or `.delnc @user <msg_id>`")

@cmd("throw", group_only=True)
async def _throw(event, arg):
    targets = await get_targets(event, arg)
    if not targets: return await safe_edit(event, "❌ Reply or provide user ID / @username!")
    kicked = []
    for uid in targets:
        try:
            await bot.kick_participant(event.chat_id, uid)
            kicked.append(str(uid))
        except Exception as e:
            logger.warning(f"Kick {uid}: {e}")
    await safe_edit(event, f"🦵 **Kicked:** `{', '.join(kicked) or 'Failed'}`")

@cmd("ban", group_only=True)
async def _ban(event, arg):
    targets = await get_targets(event, arg)
    if not targets: return await safe_edit(event, "❌ Reply or provide user ID / @username!")
    banned = []
    for uid in targets:
        try:
            await bot(EditBannedRequest(
                event.chat_id, uid,
                ChatBannedRights(until_date=None, view_messages=True)
            ))
            banned.append(str(uid))
        except Exception as e:
            logger.warning(f"Ban {uid}: {e}")
    await safe_edit(event, f"🚫 **Banned:** `{', '.join(banned) or 'Failed'}`")

# ── RAID COMMAND REGISTRATION ─────────────────────────────────────
def _raid_toggle_on(store: set, label: str):
    async def _handler(event, arg):
        targets = await get_targets(event, arg)
        if not targets: return await safe_edit(event, "❌ Reply or provide target @username!")
        added = [str(u) for u in targets if u not in store]
        store.update(targets)
        await safe_edit(event, f"⚡ **{label} ON** → `{', '.join(added) or 'Already active'}`")
    return _handler

def _raid_toggle_off(store: set, label: str):
    async def _handler(event, arg):
        targets = await get_targets(event, arg)
        if targets:
            stopped = [str(u) for u in targets if u in store]
            for u in targets: store.discard(u)
            await safe_edit(event, f"🛑 **{label} OFF** → `{', '.join(stopped) or 'Not active'}`")
        else:
            store.clear()
            await safe_edit(event, f"🛑 **{label} OFF** → All targets")
    return _handler

cmd("reply")(_raid_toggle_on(reply_users,    "Reply Raid"))
cmd("sreply")(_raid_toggle_off(reply_users,  "Reply Raid"))
cmd("rr")(_raid_toggle_on(rr_users,          "RR Raid"))
cmd("srr")(_raid_toggle_off(rr_users,        "RR Raid"))
cmd("flag")(_raid_toggle_on(flag_users,      "Flag Raid"))
cmd("sflag")(_raid_toggle_off(flag_users,    "Flag Raid"))
cmd("hrr")(_raid_toggle_on(hrr_users,        "Heart Raid"))
cmd("shrr")(_raid_toggle_off(hrr_users,      "Heart Raid"))
cmd("replygod")(_raid_toggle_on(replygod_users, "God Raid"))
cmd("sgod")(_raid_toggle_off(replygod_users, "God Raid"))
cmd("bomb")(_raid_toggle_on(bomb_users,       "Bomb Raid"))
cmd("sbomb")(_raid_toggle_off(bomb_users,     "Bomb Raid"))
cmd("clonereply")(_raid_toggle_on(clone_reply_users,  "Clone Reply"))
cmd("sclonereply")(_raid_toggle_off(clone_reply_users,"Clone Reply"))

@cmd("replyvx")
async def _replyvx(event, arg):
    parts = arg.rsplit(" ", 1) if arg else []
    if len(parts) < 2 or not parts[1].isdigit():
        return await safe_edit(event, "❌ **Usage:** `.replyvx <text> <count>`")
    text, count = parts[0], min(int(parts[1]), 100)
    targets = await get_targets(event, "")
    if not targets: return await safe_edit(event, "❌ Reply to target message!")
    for uid in targets: replyvx_users[uid] = {"text": text, "count": count}
    await safe_edit(event, f"☄️ **ReplyVX ON** → `{', '.join(str(u) for u in targets)}` × `{count}`")

@cmd("svx")
async def _svx(event, arg):
    targets = await get_targets(event, arg)
    if targets:
        for uid in targets: replyvx_users.pop(uid, None)
        await safe_edit(event, f"🛑 **ReplyVX OFF** → `{', '.join(str(u) for u in targets)}`")
    else:
        replyvx_users.clear()
        await safe_edit(event, "🛑 **ReplyVX OFF** → All targets")

@cmd("mraid")
async def _mraid(event, arg):
    targets = await get_targets(event, arg)
    if not targets: return await safe_edit(event, "❌ Reply or provide @username!")
    for uid in targets: media_raid_users.add(uid)
    tip = "" if mraid_media_msg else "\n⚠️ Use `.setmraid` to save photo/video media first!"
    await safe_edit(event, f"🖼️ **Media Raid Started on {len(targets)} user(s)**{tip}")

@cmd("smraid")
async def _smraid(event, arg):
    targets = await get_targets(event, arg)
    if targets:
        for uid in targets: media_raid_users.discard(uid)
        await safe_edit(event, f"🛑 **MRaid OFF** → `{', '.join(str(u) for u in targets)}`")
    else:
        media_raid_users.clear()
        await safe_edit(event, "🛑 **MRaid OFF** → All targets")

@cmd("abuse")
async def _abuse(event, arg):
    targets = await get_targets(event, arg)
    for uid in targets: abuse_users.add(uid)
    await safe_edit(event, f"⚔️ **Abuse Raid Started on {len(targets)} user(s)**")

@cmd("sabuse")
async def _sabuse(event, arg):
    targets = await get_targets(event, arg)
    if targets:
        for uid in targets: abuse_users.discard(uid)
        await safe_edit(event, f"🛑 **Abuse Raid OFF** → `{', '.join(str(u) for u in targets)}`")
    else:
        abuse_users.clear()
        await safe_edit(event, "🛑 **Abuse Raid OFF** → All targets")

@cmd("abuse2")
async def _abuse2(event, arg):
    targets = await get_targets(event, arg)
    for uid in targets: abuse2_users.add(uid)
    await safe_edit(event, f"💀 **Abuse2 Raid Started on {len(targets)} user(s)**")

@cmd("sabuse2")
async def _sabuse2(event, arg):
    targets = await get_targets(event, arg)
    if targets:
        for uid in targets: abuse2_users.discard(uid)
        await safe_edit(event, f"🛑 **Abuse2 Raid OFF** → `{', '.join(str(u) for u in targets)}`")
    else:
        abuse2_users.clear()
        await safe_edit(event, "🛑 **Abuse2 Raid OFF** → All targets")

@cmd("slap")
async def _slap(event, arg):
    targets = await get_targets(event, arg)
    for uid in targets: slap_users.add(uid)
    await safe_edit(event, f"👋🏻 **Slap Raid Started on {len(targets)} user(s)**")

@cmd("sslap")
async def _sslap(event, arg):
    targets = await get_targets(event, arg)
    if targets:
        for uid in targets: slap_users.discard(uid)
        await safe_edit(event, f"🛑 **Slap Raid OFF** → `{', '.join(str(u) for u in targets)}`")
    else:
        slap_users.clear()
        await safe_edit(event, "🛑 **Slap Raid OFF** → All targets")

@cmd("kickraid")
async def _kickraid(event, arg):
    targets = await get_targets(event, arg)
    if not targets: return await safe_edit(event, "❌ Reply or provide @username!")
    for uid in targets: kick_users.add(uid)
    await safe_edit(event, f"👞 **Kick Raid Started on {len(targets)} user(s)**")

@cmd("skickraid")
async def _skickraid(event, arg):
    targets = await get_targets(event, arg)
    if targets:
        for uid in targets: kick_users.discard(uid)
        await safe_edit(event, f"🛑 **Kick Raid OFF** → `{', '.join(str(u) for u in targets)}`")
    else:
        kick_users.clear()
        await safe_edit(event, "🛑 **Kick Raid OFF** → All targets")

@cmd("stopall")
async def _stopall(event, _):
    reply_users.clear(); rr_users.clear(); flag_users.clear(); hrr_users.clear()
    abuse_users.clear(); abuse2_users.clear(); slap_users.clear(); kick_users.clear()
    media_raid_users.clear(); replygod_users.clear(); replyvx_users.clear()
    bomb_users.clear(); clone_reply_users.clear(); slide_users.clear()
    for task in spray_tasks.values():
        if not task.done(): task.cancel()
    spray_tasks.clear()
    FASTGC_STATE["active"] = False
    if FASTGC_STATE.get("task") and not FASTGC_STATE["task"].done():
        FASTGC_STATE["task"].cancel()
    FASTGC_STATE["task"] = None
    global CLONE_RAID_TASK
    if CLONE_RAID_TASK and not CLONE_RAID_TASK.done():
        CLONE_RAID_TASK.cancel()
        CLONE_RAID_TASK = None
    await safe_edit(event, "🛑 **ALL RAIDS, SPRAY & SLIDE RAIDS STOPPED!**")

@cmd("spray")
async def _spray(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.spray <text>`")
    chat = event.chat_id
    if chat in spray_tasks and not spray_tasks[chat].done():
        return await safe_edit(event, "⚠️ Spray already active here!")
    text = arg[:4000]
    await safe_edit(event, "⚡ Spray started!")
    async def _loop():
        try:
            while True:
                await bot.send_message(chat, text)
                await asyncio.sleep(SPRAY_DELAY)
        except asyncio.CancelledError: pass
        except Exception as e: logger.error(f"[Spray] {e}")
    spray_tasks[chat] = asyncio.ensure_future(_loop())

@cmd("dspray")
async def _dspray(event, _):
    chat = event.chat_id
    task = spray_tasks.get(chat)
    if task and not task.done():
        task.cancel()
        del spray_tasks[chat]
        await safe_edit(event, "🛑 **Spray Stopped!**")
    else:
        await safe_edit(event, "⚠️ No active spray here!")

@cmd("slideraid")
async def _slideraid(event, arg):
    if not arg:
        return await safe_edit(event, "❌ **Usage:** Reply to target -> `.slideraid <text>`")
    targets = await get_targets(event, "")
    if not targets: return await safe_edit(event, "❌ Reply to target message to start!")
    text, emojis = arg[:3000], list(SLIDE_EMOJIS)
    added = []
    for uid in targets:
        slide_users[uid] = {"text": text, "idx": 0, "emojis": emojis}
        added.append(str(uid))
    await safe_edit(event, f"🎭 **SLIDE RAID ON** → `{', '.join(added)}`")

@cmd("dslideraid")
async def _dslideraid(event, arg):
    targets = await get_targets(event, arg)
    if targets:
        for u in targets: slide_users.pop(u, None)
        await safe_edit(event, "🛑 **Slide Raid OFF** for specified target(s).")
    else:
        slide_users.clear()
        await safe_edit(event, "🛑 **Slide Raid Stopped — All users!**")

@cmd("fastgc")
async def _fastgc(event, arg):
    if not arg: return await safe_edit(event, "❌ **Usage:** `.fastgc set <template>` or `.fastgc stop`")
    sub = arg.split(" ", 1)
    action = sub[0].lower()
    if action == "stop":
        FASTGC_STATE["active"] = False
        if FASTGC_STATE.get("task") and not FASTGC_STATE["task"].done():
            FASTGC_STATE["task"].cancel()
        FASTGC_STATE["task"] = None
        return await safe_edit(event, "🛑 **FastGC Stopped!**")
    if action == "set":
        if len(sub) < 2: return await safe_edit(event, "❌ Provide a title template!")
        template = sub[1]
        FASTGC_STATE["active"] = True
        FASTGC_STATE["template"] = template
        FASTGC_STATE["chat_id"] = event.chat_id
        if FASTGC_STATE.get("task") and not FASTGC_STATE["task"].done():
            FASTGC_STATE["task"].cancel()
        FASTGC_STATE["task"] = asyncio.ensure_future(_gc_fast_loop(event.chat_id))
        return await safe_edit(event, f"⚡ **FastGC Started!** Template: `{template}`")
    await safe_edit(event, "❌ Use `set` or `stop`")

# ── PROFILE CLONE & RESTORE ───────────────────────────────────────
@cmd("save")
async def _save_profile(event, _):
    try:
        me = await bot.get_me()
        full = await bot(functions.users.GetFullUserRequest(me.id))
        CLONE_DATA["name"] = me.first_name
        CLONE_DATA["last"] = me.last_name
        CLONE_DATA["bio"] = full.full_user.about
        CLONE_DATA["username"] = getattr(me, "username", None) or ""
        photos = await bot.get_profile_photos(me.id, limit=1)
        if photos:
            CLONE_DATA["photo_bytes"] = await bot.download_media(photos[0], file=bytes)
        await safe_edit(event, f"💾 **Profile State Saved!** Use `.normal` to restore.")
    except Exception as e:
        await safe_edit(event, f"❌ Save failed: `{e}`")

@cmd("copy")
async def _copy(event, arg):
    global CLONE_DATA, CLONE_ACTIVE, LAST_CLONE_ID
    reply = await event.get_reply_message() if event.is_reply else None
    target = None
    if reply:
        try: target = await bot.get_entity(reply.sender_id)
        except: pass
    if not target and arg:
        try: target = await bot.get_entity(arg.strip())
        except: pass
    if not target: return await safe_edit(event, "❌ Reply or provide @username/ID")
    me = await bot.get_me()
    if target.id == me.id: return await safe_edit(event, "⚠️ Cannot clone yourself!")
    await safe_edit(event, "⚡ Cloning profile...")
    if not CLONE_ACTIVE:
        try:
            full = await bot(functions.users.GetFullUserRequest(me.id))
            CLONE_DATA["name"] = me.first_name
            CLONE_DATA["last"] = me.last_name
            CLONE_DATA["bio"] = full.full_user.about
            CLONE_DATA["username"] = getattr(me, "username", None) or ""
            photos = await bot.get_profile_photos(me.id, limit=1)
            if photos:
                CLONE_DATA["photo_bytes"] = await bot.download_media(photos[0], file=bytes)
        except: pass
    try:
        new_name = getattr(target, "first_name", None) or "User"
        new_last = getattr(target, "last_name", None) or ""
        new_bio = ""
        try:
            full_t = await bot(functions.users.GetFullUserRequest(target.id))
            new_bio = full_t.full_user.about or ""
        except: pass
        await bot(functions.account.UpdateProfileRequest(
            first_name=new_name, last_name=new_last, about=new_bio
        ))
        photos = await bot.get_profile_photos(target.id, limit=1)
        if photos:
            photo_bytes = await bot.download_media(photos[0], file=bytes)
            buf = BytesIO(photo_bytes); buf.name = "photo.jpg"
            await bot(functions.photos.UploadProfilePhotoRequest(
                file=await bot.upload_file(buf)
            ))
        CLONE_ACTIVE = True
        LAST_CLONE_ID = target.id
        await safe_edit(event, f"✅ **Cloned `{new_name}`'s profile!** (use `.normal` to revert)")
    except Exception as e:
        await safe_edit(event, f"❌ Clone failed: `{e}`")

@cmd("normal")
async def _normal(event, _):
    global CLONE_ACTIVE, LAST_CLONE_ID
    if not CLONE_ACTIVE and not CLONE_DATA.get("name"):
        return await safe_edit(event, "⚠️ No active clone state saved!")
    await safe_edit(event, "⚡ Restoring profile...")
    try:
        try:
            my_photos = await bot.get_profile_photos("me", limit=1)
            if my_photos:
                p = my_photos[0]
                await bot(functions.photos.DeletePhotosRequest(
                    id=[types.InputPhoto(id=p.id, access_hash=p.access_hash, file_reference=p.file_reference)]
                ))
        except: pass

        if CLONE_DATA.get("photo_bytes"):
            try:
                buf = BytesIO(CLONE_DATA["photo_bytes"]); buf.name = "photo.jpg"
                await bot(functions.photos.UploadProfilePhotoRequest(file=await bot.upload_file(buf)))
            except: pass

        await bot(functions.account.UpdateProfileRequest(
            first_name=CLONE_DATA.get("name") or "",
            last_name=CLONE_DATA.get("last") or "",
            about=CLONE_DATA.get("bio") or "",
        ))

        CLONE_ACTIVE = False
        LAST_CLONE_ID = None
        await safe_edit(event, "✅ **Profile Restored! Original photo and bio are back.**")
    except Exception as e:
        await safe_edit(event, f"❌ Restore failed: `{e}`")

# ── MUSIC & SONG DOWNLOADERS ──────────────────────────────────────
@cmd("music")
async def _music(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.music <song name or URL>`")
    m = await safe_edit(event, f"🎵 Searching YouTube for `{arg}`...")
    base_tmpl = os.path.join(DOWNLOAD_PATH, "music_%(id)s.%(ext)s")
    query = arg if arg.startswith(("http://", "https://")) else f"ytsearch1:{arg}"
    info, out_path, video_id = None, None, None

    try:
        opts = {
            "format": "bestaudio/best",
            "outtmpl": base_tmpl,
            "quiet": True,
            "noplaylist": True,
            "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, query, True)
            if info and "entries" in info: info = next((x for x in info["entries"] if x), None)
        if info: video_id = info.get("id")
        matches = _glob.glob(os.path.join(DOWNLOAD_PATH, f"music_{video_id}.*")) if video_id else []
        if matches: out_path = matches[0]
    except Exception as e1:
        logger.warning(f"[music] {e1}")

    if not info or not out_path:
        return await safe_edit(m, "❌ Audio download failed or music not found.")

    title, duration = info.get("title", "Unknown"), int(info.get("duration") or 0)
    mins, secs = divmod(duration, 60)
    await safe_edit(m, f"⬆️ Uploading `{title}`...")
    try:
        await bot.send_file(
            event.chat_id, out_path,
            caption=f"🎵 **{title}**\n⏱️ `{mins}:{secs:02d}`",
            attributes=[types.DocumentAttributeAudio(duration=duration, title=title, performer="YouTube")]
        )
        try: os.remove(out_path)
        except: pass
        await m.delete()
    except Exception as e:
        await safe_edit(m, f"❌ Upload error: `{e}`")

@cmd("song")
async def _song(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.song <song name>`")
    m = await safe_edit(event, f"🔍 Searching Spotify/JioSaavn for `{arg}`...")
    try:
        encoded = urllib.parse.quote(arg, safe="")
        resp = await asyncio.to_thread(
            lambda: requests.get(f"https://saavnapi-nine.vercel.app/result/?query={encoded}", timeout=25).json()
        )
        songs = resp.get('results', []) if isinstance(resp, dict) else (resp if isinstance(resp, list) else [])
        valid_songs = [s for s in songs if isinstance(s, dict) and s.get('media_url')]
        if not valid_songs:
            return await safe_edit(m, f"❌ No downloadable songs found for `{arg}`.")

        song = valid_songs[0]
        song_name = song.get('song') or song.get('title') or arg
        media_url = song.get('media_url')

        await safe_edit(m, f"⏳ Downloading `{song_name}`...")
        audio_data = await asyncio.to_thread(lambda: requests.get(media_url, timeout=40).content)

        path = os.path.join(TEMP_PATH, f"song_{event.id}.mp3")
        with open(path, "wb") as f: f.write(audio_data)

        await safe_edit(m, f"⬆️ Uploading `{song_name}`...")
        await bot.send_file(
            event.chat_id, path,
            caption=f"🎵 **{song_name}** | {BRAND_SHORT}",
            attributes=[types.DocumentAttributeAudio(duration=0, title=song_name, performer="Spotify/JioSaavn")]
        )
        os.remove(path)
        await m.delete()
    except Exception as e:
        await safe_edit(m, f"❌ Song error: `{str(e)[:60]}`")

# ── AI: ASK & IMAGINE ─────────────────────────────────────────────
@cmd("ask")
async def _ask(event, arg):
    if not arg:
        return await safe_edit(event, "Usage: .ask <your question>")
    if len(arg) > 12000:
        return await safe_edit(event, "Please keep the question under 12,000 characters.")

    # Read these at request time so a restarted process can use updated env vars.
    api_key = os.environ.get("GEMINI_API_KEY", GEMINI_API_KEY).strip()
    model = os.environ.get("GEMINI_MODEL", GEMINI_MODEL).strip()
    if not api_key:
        return await safe_edit(
            event,
            "AI is not configured. Set GEMINI_API_KEY, restart the userbot, then try .ask again."
        )
    if not model:
        return await safe_edit(event, "GEMINI_MODEL is empty. Use gemini-3.5-flash-lite.")

    await safe_edit(event, "AI is thinking...")
    endpoint = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{urllib.parse.quote(model, safe='-._')}:generateContent"
    )
    payload = {
        "contents": [{"role": "user", "parts": [{"text": arg}]}],
        "generationConfig": {"maxOutputTokens": 1024},
    }
    try:
        response = await asyncio.to_thread(
            requests.post,
            endpoint,
            headers={"x-goog-api-key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=45,
        )
        try:
            data = response.json()
        except ValueError:
            data = {}
        if not response.ok:
            detail = data.get("error", {}).get("message") or response.text[:160]
            raise RuntimeError(f"Gemini request failed (HTTP {response.status_code}): {detail}")

        candidates = data.get("candidates") or []
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []
        answer = "\n".join(
            str(part.get("text", "")).strip()
            for part in parts
            if isinstance(part, dict) and part.get("text")
        ).strip()
        if not answer:
            finish_reason = candidates[0].get("finishReason", "no response") if candidates else "no response"
            raise RuntimeError(f"Gemini returned no text ({finish_reason}).")
    except requests.RequestException as exc:
        return await safe_edit(event, f"AI network error: {str(exc)[:160]}")
    except Exception as exc:
        return await safe_edit(event, f"AI error: {str(exc)[:220]}")

    return await safe_edit(event, f"AI ({model})\n\n{answer[:3600]}")

    if not arg: return await safe_edit(event, "❌ Usage: `.ask <your question>`")
    await safe_edit(event, "🤖 **AI is thinking...**")
    try:
        encoded = urllib.parse.quote(arg, safe="")
        resp = await asyncio.to_thread(
            lambda: requests.get(f"https://text.pollinations.ai/{encoded}", timeout=35, headers={"User-Agent": "mexxyV6/1.0"})
        )
        answer = resp.text.strip()[:3800]
        await safe_edit(event, f"🤖 **{BRAND_SHORT} AI**\n━━━━━━━━━━━━━━━\n❓ `{arg[:80]}`\n━━━━━━━━━━━━━━━\n{answer}")
    except Exception as e:
        await safe_edit(event, f"❌ AI error: `{e}`")

@cmd("imagine")
async def _imagine(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.imagine <prompt>`")
    await safe_edit(event, f"🎨 **Generating AI Image for `{arg[:40]}`...**")
    try:
        encoded = urllib.parse.quote(arg, safe="")
        seed = random.randint(1, 999999)
        url = f"https://image.pollinations.ai/prompt/{encoded}?width=1024&height=1024&nologo=true&seed={seed}&model=flux"
        img_bytes = await asyncio.to_thread(
            lambda: requests.get(url, timeout=50, headers={"User-Agent": "mexxyV6/1.0"}).content
        )
        buf = BytesIO(img_bytes); buf.name = "ai.jpg"
        await bot.send_file(event.chat_id, buf, caption=f"🎨 **AI Image:** `{arg[:100]}`")
        await event.delete()
    except Exception as e:
        await safe_edit(event, f"❌ Imagine error: `{e}`")

# ── TTS & QR CODE ─────────────────────────────────────────────────
@cmd("tts")
async def _tts(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.tts [lang] <text>`")
    parts = arg.split(" ", 1)
    lang, text = (parts[0], parts[1]) if len(parts) > 1 and len(parts[0]) == 2 else ("en", arg)
    await safe_edit(event, "⚡ Generating voice...")
    try:
        tts = gTTS(text=text[:500], lang=lang)
        path = os.path.join(TEMP_PATH, f"tts_{event.id}.mp3")
        tts.save(path)
        await bot.send_file(event.chat_id, path, voice_note=True, caption=f"🔊 `{text[:50]}`")
        os.remove(path)
        await event.delete()
    except Exception as e:
        await safe_edit(event, f"❌ TTS failed: `{e}`")

@cmd("qrcode")
async def _qrcode(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.qrcode <text>`")
    await safe_edit(event, "⚡ Generating QR Code...")
    try:
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(arg); qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        path = os.path.join(TEMP_PATH, f"qr_{event.id}.png")
        img.save(path)
        await bot.send_file(event.chat_id, path, caption=f"📷 QR Code for: `{arg[:60]}`")
        os.remove(path)
        await event.delete()
    except Exception as e:
        await safe_edit(event, f"❌ QR Code failed: `{e}`")

# ── UTILITIES (TRANSLATE, WEATHER, IP, CALC, WIKI, SPEEDTEST) ─────
@cmd("translate")
async def _translate(event, arg):
    if not arg or " " not in arg: return await safe_edit(event, "❌ Usage: `.translate <lang> <text>`")
    lang, text = arg.split(" ", 1)
    await safe_edit(event, "⚡ Translating...")
    try:
        resp = requests.get(
            "https://api.mymemory.translated.net/get",
            params={"q": text[:500], "langpair": f"en|{lang.upper()}"},
            timeout=10
        ).json()
        translated = resp.get("responseData", {}).get("translatedText", "")
        await safe_edit(event, f"🌐 **Translated ({lang.upper()}):**\n`{translated}`")
    except Exception as e:
        await safe_edit(event, f"❌ Translation error: `{e}`")

@cmd("weather")
async def _weather(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.weather <city>`")
    await safe_edit(event, "⚡ Fetching weather...")
    try:
        geo = requests.get(f"https://geocoding-api.open-meteo.com/v1/search?name={arg}&count=1", timeout=8).json()
        if not geo.get("results"): return await safe_edit(event, "❌ City not found!")
        r = geo["results"][0]
        w = requests.get(f"https://api.open-meteo.com/v1/forecast?latitude={r['latitude']}&longitude={r['longitude']}&current_weather=true", timeout=8).json()
        cw = w.get("current_weather", {})
        await safe_edit(event,
            f"🌦️ **Weather in {r['name']}, {r.get('country_code','')}**\n"
            f"🌡️ Temp: `{cw.get('temperature')}°C` | 💨 Wind: `{cw.get('windspeed')} km/h`"
        )
    except Exception as e:
        await safe_edit(event, f"❌ Weather error: `{e}`")

@cmd("ip")
async def _ip(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.ip <address>`")
    await safe_edit(event, "⚡ Looking up IP...")
    try:
        data = requests.get(f"http://ip-api.com/json/{arg}", timeout=8).json()
        if data.get("status") != "success": return await safe_edit(event, "❌ Invalid IP!")
        await safe_edit(event,
            f"📡 **IP Info:** `{data.get('query')}`\n"
            f"🌐 Country: `{data.get('country')}` | City: `{data.get('city')}`\n"
            f"📍 ISP: `{data.get('isp')}`"
        )
    except Exception as e:
        await safe_edit(event, f"❌ IP error: `{e}`")

@cmd("calc")
async def _calc(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.calc <expr>`")
    expr = arg.strip()
    if any(c not in "0123456789+-*/().% " for c in expr):
        return await safe_edit(event, "❌ Invalid characters!")
    try:
        res = eval(expr, {"__builtins__": None}, {"abs": abs, "round": round, "sqrt": math.sqrt})
        await safe_edit(event, f"🧮 `{expr}` = `{res}`")
    except:
        await safe_edit(event, "❌ Expression error!")

@cmd("wiki")
async def _wiki(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.wiki <query>`")
    await safe_edit(event, f"🔍 Searching Wiki for `{arg}`...")
    try:
        search = requests.get("https://en.wikipedia.org/w/api.php", params={"action":"query","list":"search","srsearch":arg,"format":"json","srlimit":1}, timeout=8).json()
        results = search.get("query", {}).get("search", [])
        if not results: return await safe_edit(event, "❌ No Wiki results found!")
        title = results[0]["title"]
        summary = requests.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(title)}", timeout=8).json()
        await safe_edit(event, f"📚 **{title}**\n{summary.get('extract','')[:500]}")
    except Exception as e:
        await safe_edit(event, f"❌ Wiki error: `{e}`")

@cmd("speedtest")
async def _speedtest(event, _):
    await safe_edit(event, "📡 Running speedtest... (may take ~20s)")
    try:
        import speedtest as _st
        def _run():
            s = _st.Speedtest(); s.get_best_server()
            return s.download()/1e6, s.upload()/1e6, s.results.ping
        dl, ul, ping = await asyncio.to_thread(_run)
        await safe_edit(event, f"📡 **Speedtest:**\n⬇️ Down: `{dl:.2f} Mbps` | ⬆️ Up: `{ul:.2f} Mbps` | ⏱️ Ping: `{ping:.0f} ms`")
    except Exception as e:
        await safe_edit(event, f"❌ Speedtest error: `{e}`")

@cmd("restart", owner_only=True)
async def _restart(event, _):
    await safe_edit(event, "🔄 **Restarting userbot...**")
    await bot.disconnect()
    os.execv(sys.executable, [sys.executable] + sys.argv)

# ─────────────────────────────────────────────────────────────────
#  NEW AESTHETIC WELCOME SYSTEM
# ─────────────────────────────────────────────────────────────────
_welcome_cfg: Dict[str, Any] = {
    "enabled": True,
    "text": (
        "✦ ───────── ❨ ꪑᴇxxꪗ 𝐖𝐄𝐋𝐂𝐎𝐌𝐄 ❩ ───────── ✦\n"
        "👑 **𝐇𝐞𝐥𝐥𝐨** {mention}!\n"
        "✨ **𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐭𝐨** {chat}\n"
        "🆔 **𝐔𝐬𝐞𝐫 𝐈𝐃:** `{id}`\n"
        "⏰ **𝐉𝐨𝐢𝐧𝐞𝐝 𝐀𝐭:** `{time}` | `{date}`\n"
        "✦ ───────────────────────────────── ✦"
    ),
    "send_banner": True,
}

def _load_welcome():
    global _welcome_cfg
    data = _load_json(WELCOME_FILE, {})
    _welcome_cfg.update(data)

def _save_welcome():
    _save_json(WELCOME_FILE, _welcome_cfg)

@cmd("setwelcome")
async def _setwelcome(event, arg):
    if not arg:
        return await safe_edit(
            event,
            "❌ **Usage:** `.setwelcome <text>`\n"
            "Variables: `{mention}` `{name}` `{chat}` `{id}` `{time}` `{date}`"
        )
    _welcome_cfg["text"] = arg.strip()
    _welcome_cfg["enabled"] = True
    _save_welcome()
    await safe_edit(event, f"✅ **Welcome message updated & enabled!**\n\n{_welcome_cfg['text']}")

@cmd("welctest")
async def _welctest(event, _):
    if not _welcome_cfg.get("text"):
        return await safe_edit(event, "❌ No welcome message set.")
    me = await bot.get_me()
    chat = await event.get_chat()
    mention = f"[{me.first_name}](tg://user?id={me.id})"
    chat_name = getattr(chat, "title", "this group")
    now = datetime.datetime.now()
    preview = _welcome_cfg["text"].format(
        mention=mention, name=me.first_name or "user",
        chat=chat_name, id=me.id,
        time=now.strftime("%I:%M %p"), date=now.strftime("%d %b %Y"),
    )
    await safe_edit(event, f"🎉 **Welcome Card Test Output:**\n\n{preview}")

@cmd("delwelcome")
async def _delwelcome(event, _):
    _welcome_cfg["text"] = ""
    _welcome_cfg["enabled"] = False
    _save_welcome()
    await safe_edit(event, "🗑️ **Welcome message deleted.**")

@cmd("welcoff")
async def _welcoff(event, _):
    _welcome_cfg["enabled"] = False
    _save_welcome()
    await safe_edit(event, "🔕 **Auto welcome disabled.**")

@cmd("welcon")
async def _welcon(event, _):
    _welcome_cfg["enabled"] = True
    _save_welcome()
    await safe_edit(event, "✅ **Auto welcome enabled.**")

@bot.on(events.ChatAction())
async def _welcome_handler(event):
    if not _welcome_cfg.get("enabled"): return
    if not (event.user_joined or event.user_added): return
    try:
        user = await event.get_user()
        if not user or user.bot: return
        chat = await event.get_chat()
        mention = f"[{user.first_name}](tg://user?id={user.id})"
        chat_name = getattr(chat, "title", "this group")
        now = datetime.datetime.now()
        text = _welcome_cfg["text"].format(
            mention=mention, name=user.first_name or "user",
            chat=chat_name, id=user.id,
            time=now.strftime("%I:%M %p"), date=now.strftime("%d %b %Y"),
        )
        await bot.send_message(event.chat_id, text, parse_mode="md")
    except Exception as e:
        logger.warning(f"[Welcome handler] {e}")

# ─────────────────────────────────────────────────────────────────
#  ADDITIONAL AUTOMATION & EXTRA FEATURES
# ─────────────────────────────────────────────────────────────────
_autorespond_store: dict = {}
_afk_store: dict         = {}
_delall_store: dict      = {}
_target_store: dict      = {}

@cmd("autorespond")
async def _autorespond_cmd(event, arg):
    if not arg or " " not in arg: return await safe_edit(event, "❌ Usage: `.autorespond <trigger> <reply>`")
    trigger, response = arg.split(" ", 1)
    _autorespond_store.setdefault(event.chat_id, {})[trigger.lower()] = response
    await safe_edit(event, f"✅ Auto-respond set: `{trigger}` → `{response}`")

@cmd("stopautorespond")
async def _stopautorespond(event, _):
    _autorespond_store.pop(event.chat_id, None)
    await safe_edit(event, "✅ Auto-respond disabled for this chat.")

@bot.on(events.NewMessage(incoming=True))
async def _autorespond_handler(event):
    if not event.message or not event.message.text: return
    rules = _autorespond_store.get(event.chat_id)
    if not rules: return
    text = event.message.text.lower()
    for trigger, response in rules.items():
        if trigger in text:
            await event.reply(response)
            break

@cmd("afk")
async def _afk_cmd(event, arg):
    me = await bot.get_me()
    if arg and arg.lower() == "off":
        _afk_store.pop(me.id, None)
        return await safe_edit(event, "✅ AFK Mode OFF")
    reason = arg or "I am currently away."
    _afk_store[me.id] = reason
    await safe_edit(event, f"😴 **AFK Mode ON**\nReason: `{reason}`")

@cmd("killafk")
async def _killafk(event, _):
    me = await bot.get_me()
    _afk_store.pop(me.id, None)
    await safe_edit(event, "✅ AFK Mode Disabled.")

@bot.on(events.NewMessage(incoming=True))
async def _afk_reply_handler(event):
    if not event.is_private: return
    me = await bot.get_me()
    if me.id in _afk_store:
        try: await event.reply(f"😴 I am AFK right now.\nReason: `{_afk_store[me.id]}`")
        except: pass

@cmd("delall")
async def _delall_cmd(event, arg):
    return await safe_edit(
        event,
        "Automatic deletion is disabled. Use .nc or .delnc on command or reply to delete messages."
    )
    arg = (arg or "").strip().lower()
    if arg == "off":
        _delall_store.pop(event.chat_id, None)
        return await safe_edit(event, "✅ Delete-All Mode OFF")
    _delall_store[event.chat_id] = True
    await safe_edit(event, "⚠️ **Delete-All Mode ON — Incoming messages will be auto-deleted.**")

@bot.on(events.NewMessage(incoming=True))
async def _delall_handler(event):
    if False:  # Automatic delete mode is disabled; use .delnc for one message.
        try: await event.delete()
        except: pass

@cmd("target")
async def _target_cmd(event, arg):
    if not event.is_private: return await safe_edit(event, "❌ Use in DM only.")
    if not event.is_reply: return await safe_edit(event, "❌ Reply to a photo with `.target <text>`")
    reply = await event.get_reply_message()
    if not reply.photo: return await safe_edit(event, "❌ Reply to a photo!")
    path = os.path.join(TEMP_PATH, f"target_{event.chat_id}.jpg")
    await bot.download_media(reply.photo, path)
    _target_store[event.chat_id] = (path, arg or "")
    await safe_edit(event, "✅ **Target DM Auto-Reply Set!**")

@cmd("untarget")
async def _untarget(event, _):
    data = _target_store.pop(event.chat_id, None)
    if data and os.path.exists(data[0]):
        try: os.remove(data[0])
        except: pass
    await safe_edit(event, "✅ Target DM removed.")

@bot.on(events.NewMessage(incoming=True))
async def _target_handler(event):
    if not event.is_private: return
    target = _target_store.get(event.sender_id)
    if target and os.path.exists(target[0]):
        try: await bot.send_file(event.sender_id, target[0], caption=target[1])
        except: pass

# ── CREATEGGC, CREATECH, ADDBOT, PROMOTEBOTS, REMOVEBOTS ──────────
@cmd("setbots", owner_only=True)
async def _setbots(event, arg):
    global bot_usernames
    bots = _parse_bot_usernames(arg)
    if not bots: return await safe_edit(event, "❌ Usage: `.setbots @bot1 @bot2`")
    bot_usernames = bots[:MAX_SAVED_BOTS]
    save_bot_usernames()
    await safe_edit(event, f"✅ **Saved {len(bot_usernames)} Bots:** `{', '.join(bot_usernames)}`")

@cmd("bots")
async def _bots(event, _):
    if not bot_usernames: return await safe_edit(event, "🤖 No saved bots. Use `.setbots @bot1`.")
    lines = "\n".join(f"{i}. `{b}`" for i, b in enumerate(bot_usernames, 1))
    await safe_edit(event, f"🤖 **Saved Bots List ({len(bot_usernames)}):**\n{lines}")

@cmd("creategc")
async def _creategc(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.creategc <group_name>`")
    await safe_edit(event, f"⚡ Creating supergroup `{arg}`...")
    try:
        res = await bot(CreateChannelRequest(title=arg[:128], about=f"Created by {BRAND}", megagroup=True))
        created_chat = res.chats[0]
        full_id = f"-100{created_chat.id}"
        await safe_edit(event, f"✅ **Group Created!**\n📌 Name: `{arg}`\n🆔 ID: `{full_id}`")
    except Exception as e:
        await safe_edit(event, f"❌ Group creation error: `{e}`")

@cmd("createch")
async def _createch(event, arg):
    if not arg: return await safe_edit(event, "❌ Usage: `.createch <channel_name>`")
    await safe_edit(event, f"⚡ Creating channel `{arg}`...")
    try:
        res = await bot(CreateChannelRequest(title=arg[:128], about=f"Created by {BRAND}", megagroup=False))
        chat_id = res.chats[0].id
        await safe_edit(event, f"✅ **Channel Created!**\n📌 Name: `{arg}`\n🆔 ID: `-100{chat_id}`")
    except Exception as e:
        await safe_edit(event, f"❌ Channel creation error: `{e}`")

@cmd("addbot")
async def _addbot(event, arg):
    bots = _bots_from_arg_or_saved(arg)
    if not bots: return await safe_edit(event, "❌ Usage: `.addbot @bot1`")
    await safe_edit(event, f"⚡ Adding {len(bots)} bot(s)...")
    added = []
    for b in bots:
        try:
            user = await bot.get_input_entity(b)
            await bot(InviteToChannelRequest(event.chat_id, [user]))
            added.append(b)
        except: pass
    await safe_edit(event, f"✅ **Bots Added:** `{', '.join(added) or 'None'}`")

@cmd("promotebots")
async def _promotebots(event, arg):
    bots = _bots_from_arg_or_saved(arg)
    if not bots: return await safe_edit(event, "❌ Usage: `.promotebots @bot1`")
    await safe_edit(event, f"⚡ Promoting {len(bots)} bot(s)...")
    promoted = []
    rights = ChatAdminRights(change_info=True, delete_messages=True, ban_users=True, invite_users=True, pin_messages=True)
    for b in bots:
        try:
            user = await bot.get_input_entity(b)
            await bot(EditAdminRequest(event.chat_id, user, rights, rank="Bot"))
            promoted.append(b)
        except: pass
    await safe_edit(event, f"✅ **Bots Promoted:** `{', '.join(promoted) or 'None'}`")

@cmd("removebots", group_only=True)
async def _removebots(event, _):
    await safe_edit(event, "⚡ Removing bots...")
    removed = 0
    for b in bot_usernames:
        try:
            user = await bot.get_entity(b)
            await bot.kick_participant(event.chat_id, user)
            removed += 1
        except: pass
    await safe_edit(event, f"✅ Removed `{removed}` bot(s).")

# ─────────────────────────────────────────────────────────────────
#  STARTUP & INITIALIZATION
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info(f"🚀 Starting {BRAND} V6 Ultimate...")
    load_admins()
    load_notes()
    load_banner()
    load_mraid_media()
    load_bot_usernames()
    load_menu_videos()
    load_mutes()
    load_locked_titles()
    _load_welcome()

    bot.start()
    me = bot.loop.run_until_complete(bot.get_me())
    logger.info(f"✅ Logged in as: {me.first_name} (@{me.username}) | ID: {me.id}")
    logger.info(f"🤖 Saved bot usernames: {', '.join(bot_usernames) or 'none'}")
    logger.info(f"🎥 Video Banners Configured: {len(menu_videos)}")
    logger.info(f"🎉 Welcome Greeting: {'enabled' if _welcome_cfg['enabled'] else 'disabled'}")
    logger.info(f"🌟 {BRAND} V6 is running! Type .menu to launch Master Hub.")
    bot.run_until_disconnected()
