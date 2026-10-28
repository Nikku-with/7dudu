#!/usr/bin/env python3
# VEGETA FIGHTER – ULTIMATE USERBOT (FIXED)
# Interactive Setup + All Features + Custom Spam + Menu
# Fix: client created before handlers, FloodWait recovery, command conflicts resolved

import asyncio
import os
import sys
import time
import random
import logging
import traceback
import json
import requests
from datetime import datetime
from collections import defaultdict
from pathlib import Path

from telethon import TelegramClient, events, functions, types
from telethon.tl.functions.channels import (
    EditAdminRequest, EditBannedRequest, EditTitleRequest, LeaveChannelRequest,
    JoinChannelRequest
)
from telethon.tl.functions.messages import (
    EditChatDefaultBannedRightsRequest, ImportChatInviteRequest,
    SendReactionRequest
)
from telethon.tl.functions.photos import UploadProfilePhotoRequest, DeletePhotosRequest
from telethon.tl.functions.account import UpdateProfileRequest, UpdateUsernameRequest
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import ChatBannedRights, ChatAdminRights, ReactionEmoji
from telethon.errors import FloodWaitError, MessageNotModifiedError
from telethon.utils import get_display_name

# ─── GLOBALS ───
API_ID = None
API_HASH = None
OWNER_ID = None
SESSION_NAME = None
PREFIX = "."
client = None

DATA_DIR = Path("vegeta_data")
DATA_DIR.mkdir(exist_ok=True)
CONFIG_FILE = DATA_DIR / "user_config.json"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.WARNING,
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("VEGETA")
logging.getLogger("telethon").setLevel(logging.CRITICAL)

# ─── CONFIG ───
def load_json(name, default=None):
    path = DATA_DIR / name
    if default is None:
        default = {}
    if path.exists():
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return default

def save_json(name, data):
    path = DATA_DIR / name
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception:
        pass

def load_user_config():
    if CONFIG_FILE.exists():
        return load_json("user_config.json", {})
    return {}

def setup_config():
    config = load_user_config()
    if config.get("api_id") and config.get("api_hash") and config.get("owner_id"):
        return config
    print("\n" + "=" * 50)
    print("  🔐 VEGETA FIGHTER – FIRST TIME SETUP")
    print("=" * 50)
    print("\n📌 API ID & Hash: https://my.telegram.org/apps")
    print("📌 OWNER_ID: @userinfobot se lo\n")
    api_id = input("API_ID: ").strip()
    api_hash = input("API_HASH: ").strip()
    owner_id = input("OWNER_ID (Your Telegram ID): ").strip()
    session_name = input("Session name (default: vegeta_bhagwan): ").strip() or "vegeta_bhagwan"
    try:
        config = {
            "api_id": int(api_id),
            "api_hash": api_hash,
            "owner_id": int(owner_id),
            "session_name": session_name
        }
        save_json("user_config.json", config)
        print("\n✅ Config saved!")
        print("🔄 Restarting...\n")
        time.sleep(1.5)
        os.execv(sys.executable, [sys.executable] + sys.argv)
    except ValueError:
        print("❌ Invalid input!\n")
        sys.exit(1)

# ─── STATE ───
START_TIME = time.time()
SUDO_USERS = set()
MUTED_USERS = set()
GMUTED_USERS = set()
FORCE_MUTED = set()
PASS_LOCK = {}
GHOST_MODE = False
AFK_MODE = False
AFK_REASON = ""
AFK_START = 0
AFK_LAST_REPLY = {}
CLONE_DATA = {}
FILTERS = {}
NOTES = {}
WELCOME_MSG = {}
WARN_COUNT = defaultdict(int)
SPAM_DELAY = 0.01
AUTO_REACT_EMOJI = None
SLIDE_RAID_DATA = {}
GBAN_USERS = set()
AUTO_REACT_ON = False
FIGHT_ACTIVE = False
FIGHT_TASKS = []

ABUSE_PACK = [
    "{t} teri maa ki chut madarchod",
    "{t} bhenchod randi ke bacche",
    "{t} lund lele gandu",
    "{t} teri behen ko chodu",
    "{t} teri maa ka bhosda",
    "{t} chutiye ke bacche",
    "{t} harami kutta",
    "{t} sale chutiye",
    "{t} madarchod sala",
    "{t} randi ki aulad",
    "{t} gandu lund",
    "{t} teri maa ki gaand",
    "{t} bhosdiwale",
    "{t} lavde ke bacche",
    "{t} teri behen ki chut",
    "{t} chutiya sala",
    "{t} haramzade",
    "{t} kamine",
    "{t} gand mara",
    "{t} bhadwe",
    "{t} randi",
    "{t} gandu sala",
    "{t} bhen ke lode",
    "{t} maa ka loda",
]
SLAP_PACK = [
    "{t} ko zor se thappad maara 👋",
    "{t} ke muh pe joota maara 👢",
    "{t} ko hawa mein udaya 💨",
    "{t} ki gaand mein laath maari 🦶",
    "{t} ko zameen pe pataka 💥",
]
BOMB_PACK = [
    "💣 BOOM {t} ud gaya!",
    "💥 {t} ka game over!",
    "🧨 {t} explode ho gaya!",
    "🔥 {t} jal ke raakh ho gaya!",
]
NC_TITLES = [
    "💥🔥{t}🔥💥",
    "☠️💀{t}💀☠️",
    "⚡🌀{t}🌀⚡",
    "🩸👊{t}👊🩸",
    "🔥💯{t}💯🔥",
    "🌪️⚡{t}⚡🌪️",
    "💢🔱{t}🔱💢",
    "🖕🤬{t}🤬🖕",
    "👑💀{t}💀👑",
    "🤡🔥{t}🔥🤡",
]
SLIDE_EMOJIS = ["🔥", "💀", "⚡", "👊", "🗡️", "💣", "😈", "☠️"]

def load_all():
    global SUDO_USERS, FILTERS, NOTES, WELCOME_MSG, WARN_COUNT, SPAM_DELAY, PREFIX
    global GBAN_USERS, AUTO_REACT_EMOJI, AUTO_REACT_ON
    SUDO_USERS = set(load_json("sudo.json", []))
    FILTERS = load_json("filters.json", {})
    NOTES = load_json("notes.json", {})
    WELCOME_MSG = load_json("welcome.json", {})
    WARN_COUNT = defaultdict(int, {int(k): v for k, v in load_json("warns.json", {}).items()})
    settings = load_json("settings.json", {})
    SPAM_DELAY = float(settings.get("delay", 0.01))
    PREFIX = str(settings.get("prefix", ".")) or "."
    GBAN_USERS = set(load_json("gban.json", []))
    auto = load_json("auto_react.json", {})
    AUTO_REACT_EMOJI = auto.get("emoji", None)
    AUTO_REACT_ON = auto.get("enabled", False)

def save_sudo():
    save_json("sudo.json", list(SUDO_USERS))

def save_filters():
    save_json("filters.json", FILTERS)

def save_notes():
    save_json("notes.json", NOTES)

def save_welcome():
    save_json("welcome.json", WELCOME_MSG)

def save_warns():
    save_json("warns.json", {str(k): v for k, v in WARN_COUNT.items()})

def save_settings():
    save_json("settings.json", {"delay": SPAM_DELAY, "prefix": PREFIX})

def save_gban():
    save_json("gban.json", list(GBAN_USERS))

def save_auto_react():
    save_json("auto_react.json", {"emoji": AUTO_REACT_EMOJI, "enabled": AUTO_REACT_ON})

def is_owner(uid):
    if OWNER_ID is None:
        return False
    return uid == OWNER_ID or uid in SUDO_USERS

async def owner_only(event):
    if not event.sender_id or not is_owner(event.sender_id):
        await event.reply("❌ Owner / Sudo only!")
        return False
    return True

def get_args(event):
    text = event.raw_text or ""
    parts = text.split(maxsplit=1)
    return parts[1].strip() if len(parts) > 1 else ""

async def safe_reply(event, text, **kwargs):
    try:
        return await event.reply(str(text)[:4090], **kwargs)
    except Exception:
        try:
            return await event.respond(str(text)[:4090], **kwargs)
        except Exception:
            return None

async def safe_edit(msg, text, **kwargs):
    try:
        return await msg.edit(str(text)[:4090], **kwargs)
    except MessageNotModifiedError:
        return msg
    except Exception:
        return None

def format_uptime():
    sec = int(time.time() - START_TIME)
    h, rem = divmod(sec, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m}m {s}s"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"

async def flood_sleep(e):
    """Wait out FloodWait without killing the whole task."""
    wait = min(float(getattr(e, "seconds", 1) or 1), 30.0)
    await asyncio.sleep(wait + 0.2)

# ─── TASK MANAGER ───
class TaskManager:
    def __init__(self):
        self.tasks = defaultdict(list)

    def add(self, key, coro):
        task = asyncio.create_task(coro)
        self.tasks[key].append(task)
        task.add_done_callback(lambda t: self._cleanup(key, t))
        return task

    def _cleanup(self, key, task):
        if key in self.tasks and task in self.tasks[key]:
            try:
                self.tasks[key].remove(task)
            except Exception:
                pass

    async def stop(self, key):
        tasks = self.tasks.pop(key, [])
        for t in tasks:
            if not t.done():
                t.cancel()
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        return len(tasks)

    async def stop_all(self):
        total = 0
        for k in list(self.tasks.keys()):
            total += await self.stop(k)
        return total

    def running(self, key):
        return any(not t.done() for t in self.tasks.get(key, []))

tm = TaskManager()

# ─── FIGHT ENGINE ───
async def spam_task(chat, target, pack=None):
    if pack is None:
        pack = random.choice([ABUSE_PACK, SLAP_PACK, BOMB_PACK])
    while FIGHT_ACTIVE:
        try:
            msg = random.choice(pack).format(t=target)
            await client.send_message(chat, msg)
            await asyncio.sleep(SPAM_DELAY)
        except FloodWaitError as e:
            await flood_sleep(e)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.05)

async def nc_task(chat, target):
    while FIGHT_ACTIVE:
        try:
            title = random.choice(NC_TITLES).format(t=target)[:128]
            await client(EditTitleRequest(channel=chat, title=title))
            await asyncio.sleep(SPAM_DELAY)
        except FloodWaitError as e:
            await flood_sleep(e)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.05)

async def mention_task(chat):
    try:
        async for user in client.iter_participants(chat):
            if not FIGHT_ACTIVE:
                break
            try:
                mention = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
                await client.send_message(chat, mention)
                await asyncio.sleep(SPAM_DELAY)
            except FloodWaitError as e:
                await flood_sleep(e)
            except asyncio.CancelledError:
                return
            except Exception:
                pass
    except Exception:
        pass

async def slide_task(chat, target):
    data = SLIDE_RAID_DATA.get(target, {})
    emoji_list = data.get("emojis", SLIDE_EMOJIS)
    text = data.get("text", "SLIDE")
    idx = 0
    while FIGHT_ACTIVE:
        try:
            emoji = emoji_list[idx % len(emoji_list)]
            idx += 1
            await client.send_message(chat, f"{emoji} {text} {emoji}")
            await asyncio.sleep(SPAM_DELAY)
        except FloodWaitError as e:
            await flood_sleep(e)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.05)

async def custom_spam_task(chat, text, count=None):
    sent = 0
    while True:
        if count is not None and sent >= count:
            break
        try:
            await client.send_message(chat, text)
            sent += 1
            await asyncio.sleep(SPAM_DELAY)
        except FloodWaitError as e:
            await flood_sleep(e)
        except asyncio.CancelledError:
            return
        except Exception:
            await asyncio.sleep(0.05)

async def start_fight(chat, target):
    global FIGHT_ACTIVE, FIGHT_TASKS
    if FIGHT_ACTIVE:
        return "⚔️ Fight already active! Use `.stopfight` first."
    try:
        entity = await client.get_entity(chat)
        chat_id = entity.id
        target_name = getattr(entity, "title", None) or getattr(entity, "first_name", target)
    except Exception:
        chat_id = chat
        target_name = target
    FIGHT_ACTIVE = True
    tasks = [
        asyncio.create_task(spam_task(chat_id, target_name)),
        asyncio.create_task(nc_task(chat_id, target_name)),
        asyncio.create_task(mention_task(chat_id)),
    ]
    if target in SLIDE_RAID_DATA:
        tasks.append(asyncio.create_task(slide_task(chat_id, target)))
    FIGHT_TASKS = tasks
    tm.add("fight", asyncio.gather(*tasks, return_exceptions=True))
    return (
        f"⚔️ **FIGHT STARTED** on {target_name}\n"
        f"Speed: {SPAM_DELAY}s | Tasks: {len(tasks)}\n"
        f"Use `.stopfight` to stop"
    )

async def stop_fight():
    global FIGHT_ACTIVE, FIGHT_TASKS
    FIGHT_ACTIVE = False
    count = await tm.stop("fight")
    FIGHT_TASKS = []
    return f"🛑 **FIGHT STOPPED** – killed {count} tasks"


# ═══════════════════════════════════════════════════════════
# HANDLERS — registered AFTER client exists (in register_handlers)
# ═══════════════════════════════════════════════════════════

def register_handlers(c: TelegramClient):
    """Bind all event handlers to the live client instance."""

    def pfx(cmd: str) -> str:
        # Escape special regex chars in prefix
        import re
        esc = re.escape(PREFIX)
        return rf"^{esc}{cmd}(?:\s|$)"

    # ─── MENU ───
    @c.on(events.NewMessage(pattern=pfx("help"), outgoing=True))
    @c.on(events.NewMessage(pattern=pfx("menu"), outgoing=True))
    async def cmd_menu(event):
        if not await owner_only(event):
            return
        p = PREFIX
        menu_text = f"""𓆩𓆩VEGETA BHAGWAN𓆪  🤍

🌷 ꜱᴘᴀᴍ
 · {p}vegeta 🦋  ꜱᴘᴀᴍ ꜱᴏᴍᴇᴏɴᴇ
 · {p}reply 🌸  ᴀᴜᴛᴏ ʀᴇᴘʟʏ
 · {p}stop 🍂   ꜱᴛᴏᴘ ᴇᴠᴇʀʏᴛʜɪɴɢ

🌷 ᴍᴇᴅɪᴀ
 · {p}song 🎵   ꜱᴇɴᴅ ᴀ ꜱᴏɴɢ

🌷 ᴄʜᴀᴛ
 · {p}mute 🤫   ᴍᴜᴛᴇ ᴀ ᴜꜱᴇʀ
 · {p}sp 🗑     ᴅᴇʟᴇᴛᴇ ɪɴᴄᴏᴍɪɴɢ
 · {p}react 💫  ᴀᴜᴛᴏ ʀᴇᴀᴄᴛ
 · {p}forward 🔗 ʟɪᴠᴇ ꜰᴏʀᴡᴀʀᴅ

🌷 ᴀᴅᴍɪɴ
 · {p}admin 👑  ɢɪᴠᴇ ᴀᴅᴍɪɴ
 · {p}take 🚫   ʀᴇᴍᴏᴠᴇ ᴀᴅᴍɪɴ
 · {p}kick 👢   ᴋɪᴄᴋ ᴜꜱᴇʀ
 · {p}add 🤖    ᴀᴅᴅ ʙᴏᴛꜱ

🌷 ᴘʀᴏꜰɪʟᴇ
 · {p}clonejutsu 🌙 ᴄʟᴏɴᴇ ᴘʀᴏꜰɪʟᴇ
 · {p}back 🌿   ʀᴇꜱᴛᴏʀᴇ ᴘʀᴏꜰɪʟᴇ

🌷 ᴀᴄᴄᴇꜱꜱ
 · {p}sub 🤍    ɢɪᴠᴇ ᴀᴄᴄᴇꜱꜱ
 · {p}antisub 🖤 ʀᴇᴠᴏᴋᴇ ᴀᴄᴄᴇꜱꜱ

🌷 ꜱᴀꜰᴇ
 · {p}safe 🛡   ᴘʀᴏᴛᴇᴄᴛ ᴀ ᴜꜱᴇʀ'ꜱ ᴍꜱɢꜱ
 · {p}unsafe 🌸 ʀᴇᴍᴏᴠᴇ ᴘʀᴏᴛᴇᴄᴛɪᴏɴ

ᴍᴀᴅᴇ ᴡɪᴛʜ 🤍 ʙʏ #vegeta"""
        await safe_reply(event, menu_text)

    # ─── CUSTOM SPAM ───
    @c.on(events.NewMessage(pattern=pfx("cspam"), outgoing=True))
    async def cmd_customspam(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args:
            await safe_reply(event, f"Usage: `{PREFIX}cspam <text>` or `{PREFIX}cspam <count> <text>`")
            return
        parts = args.split(maxsplit=1)
        count = None
        text = args
        if parts[0].isdigit():
            count = int(parts[0])
            if len(parts) < 2:
                await safe_reply(event, "❌ Provide text after count")
                return
            text = parts[1]
        chat = event.chat_id
        tm.add("cspam", custom_spam_task(chat, text, count))
        if count:
            await safe_reply(event, f"✅ Custom spam: `{count}` times")
        else:
            await safe_reply(event, f"✅ Custom spam loop\n`.stop` to stop")

    @c.on(events.NewMessage(pattern=pfx("cspamstop"), outgoing=True))
    async def cmd_cspamstop(event):
        if not await owner_only(event):
            return
        n = await tm.stop("cspam")
        await safe_reply(event, f"🛑 Custom spam stopped – `{n}`")

    # ─── FIGHT ───
    @c.on(events.NewMessage(pattern=pfx("fight"), outgoing=True))
    async def cmd_fight(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args:
            chat = event.chat_id
            target = str(event.chat_id)
        else:
            try:
                entity = await c.get_entity(args)
                chat = entity.id
                target = args
            except Exception:
                await safe_reply(event, "❌ Invalid target")
                return
        msg = await start_fight(chat, target)
        await safe_reply(event, msg)

    @c.on(events.NewMessage(pattern=pfx("stopfight"), outgoing=True))
    async def cmd_stopfight(event):
        if not await owner_only(event):
            return
        await safe_reply(event, await stop_fight())

    @c.on(events.NewMessage(pattern=pfx("slideraid"), outgoing=True))
    async def cmd_slideraid(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args or " " not in args:
            await safe_reply(event, f"Usage: `{PREFIX}slideraid @user <text>`")
            return
        parts = args.split(maxsplit=1)
        SLIDE_RAID_DATA[parts[0]] = {"text": parts[1], "emojis": SLIDE_EMOJIS}
        await safe_reply(event, f"🌀 SlideRaid set for {parts[0]}\nUse `{PREFIX}fight`")

    # ─── CORE ───
    @c.on(events.NewMessage(pattern=pfx("ping"), outgoing=True))
    async def cmd_ping(event):
        if not await owner_only(event):
            return
        t0 = time.time()
        msg = await safe_reply(event, "⚡")
        ms = int((time.time() - t0) * 1000)
        await safe_edit(msg, f"⚡ **Pong!** `{ms}ms`\n⏱ Uptime: `{format_uptime()}`")

    @c.on(events.NewMessage(pattern=pfx("alive"), outgoing=True))
    async def cmd_alive(event):
        if not await owner_only(event):
            return
        me = await c.get_me()
        running = sum(len(v) for v in tm.tasks.values())
        await safe_reply(
            event,
            f"**VEGETA FIGHTER**\n\n"
            f"👤 `{get_display_name(me)}`\n"
            f"⏱ Uptime: `{format_uptime()}`\n"
            f"⚙️ Tasks: `{running}`\n"
            f"🐌 Delay: `{SPAM_DELAY}s`\n"
            f"👑 Owner: `{OWNER_ID}`"
        )

    @c.on(events.NewMessage(pattern=pfx("id"), outgoing=True))
    async def cmd_id(event):
        if not await owner_only(event):
            return
        if event.is_reply:
            r = await event.get_reply_message()
            u = await r.get_sender()
            await safe_reply(event, f"**User ID:** `{u.id}`\n**Chat ID:** `{event.chat_id}`")
        else:
            await safe_reply(event, f"**Your ID:** `{event.sender_id}`\n**Chat ID:** `{event.chat_id}`")

    @c.on(events.NewMessage(pattern=pfx("info"), outgoing=True))
    async def cmd_info(event):
        if not await owner_only(event):
            return
        if event.is_reply:
            r = await event.get_reply_message()
            u = await r.get_sender()
        else:
            u = await event.get_sender()
        await safe_reply(
            event,
            f"**User Info**\nName: `{get_display_name(u)}`\n"
            f"ID: `{u.id}`\nUsername: @{getattr(u, 'username', None) or 'None'}\n"
            f"Bot: `{getattr(u, 'bot', False)}`"
        )

    @c.on(events.NewMessage(pattern=pfx("stats"), outgoing=True))
    async def cmd_stats(event):
        if not await owner_only(event):
            return
        running = sum(len(v) for v in tm.tasks.values())
        await safe_reply(
            event,
            f"**Stats**\n⏱ `{format_uptime()}`\n👥 Sudo: `{len(SUDO_USERS)}`\n"
            f"⚙️ Tasks: `{running}`\n🐌 Delay: `{SPAM_DELAY}s`"
        )

    @c.on(events.NewMessage(pattern=pfx("delay"), outgoing=True))
    async def cmd_delay(event):
        global SPAM_DELAY
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args:
            await safe_reply(event, f"Current delay: `{SPAM_DELAY}s`\nUsage: `{PREFIX}delay 0.005`")
            return
        try:
            val = float(args)
            if val < 0.001 or val > 10:
                await safe_reply(event, "Delay 0.001 – 10.0")
                return
            SPAM_DELAY = val
            save_settings()
            await safe_reply(event, f"✅ Delay set to `{val}s`")
        except ValueError:
            await safe_reply(event, "Invalid number")

    @c.on(events.NewMessage(pattern=pfx("stop"), outgoing=True))
    @c.on(events.NewMessage(pattern=pfx("stopall"), outgoing=True))
    async def cmd_stop(event):
        global FIGHT_ACTIVE
        if not await owner_only(event):
            return
        FIGHT_ACTIVE = False
        count = await tm.stop_all()
        await safe_reply(event, f"🛑 Stopped – killed `{count}` tasks")

    # ─── RAID / ABUSE ───
    async def _pack_loop(cid, target, pack):
        while True:
            try:
                msg = random.choice(pack).format(t=target)
                await c.send_message(cid, msg)
                await asyncio.sleep(SPAM_DELAY)
            except FloodWaitError as e:
                await flood_sleep(e)
            except asyncio.CancelledError:
                return
            except Exception:
                await asyncio.sleep(0.05)

    @c.on(events.NewMessage(pattern=pfx("raid"), outgoing=True))
    @c.on(events.NewMessage(pattern=pfx("abuse"), outgoing=True))
    async def cmd_raid(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        target = args
        if event.is_reply and not target:
            r = await event.get_reply_message()
            u = await r.get_sender()
            target = get_display_name(u) or str(u.id)
        if not target:
            await safe_reply(event, f"Usage: `{PREFIX}raid <name>` or reply")
            return
        tm.add(event.chat_id, _pack_loop(event.chat_id, target, ABUSE_PACK))
        await safe_reply(event, f"⚔️ Abuse raid on **{target}** | `{SPAM_DELAY}s`\n`.stop`")

    @c.on(events.NewMessage(pattern=pfx("slap"), outgoing=True))
    async def cmd_slap(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        target = args
        if event.is_reply and not target:
            r = await event.get_reply_message()
            u = await r.get_sender()
            target = get_display_name(u) or str(u.id)
        if not target:
            await safe_reply(event, f"Usage: `{PREFIX}slap <name>` or reply")
            return
        tm.add(event.chat_id, _pack_loop(event.chat_id, target, SLAP_PACK))
        await safe_reply(event, f"👋 Slap on **{target}**\n`.stop`")

    @c.on(events.NewMessage(pattern=pfx("bomb"), outgoing=True))
    async def cmd_bomb(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        target = args
        if event.is_reply and not target:
            r = await event.get_reply_message()
            u = await r.get_sender()
            target = get_display_name(u) or str(u.id)
        if not target:
            await safe_reply(event, f"Usage: `{PREFIX}bomb <name>` or reply")
            return
        tm.add(event.chat_id, _pack_loop(event.chat_id, target, BOMB_PACK))
        await safe_reply(event, f"💣 Bomb on **{target}**\n`.stop`")

    @c.on(events.NewMessage(pattern=pfx("replyraid"), outgoing=True))
    async def cmd_replyraid(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to a message")
            return
        r = await event.get_reply_message()
        target_id = r.id
        text = get_args(event) or "⚡ VEGETA"
        cid = event.chat_id

        async def loop():
            while True:
                try:
                    await c.send_message(cid, text, reply_to=target_id)
                    await asyncio.sleep(SPAM_DELAY)
                except FloodWaitError as e:
                    await flood_sleep(e)
                except asyncio.CancelledError:
                    return
                except Exception:
                    await asyncio.sleep(0.05)

        tm.add(cid, loop())
        await safe_reply(event, "🔁 ReplyRaid started — `.stop`")

    @c.on(events.NewMessage(pattern=pfx("spam"), outgoing=True))
    async def cmd_spam_count(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args or " " not in args:
            await safe_reply(event, f"Usage: `{PREFIX}spam <count> <text>`")
            return
        parts = args.split(maxsplit=1)
        try:
            count = min(int(parts[0]), 500)
        except ValueError:
            await safe_reply(event, "Invalid count")
            return
        text = parts[1]
        cid = event.chat_id
        for _ in range(count):
            try:
                await c.send_message(cid, text)
                await asyncio.sleep(SPAM_DELAY)
            except FloodWaitError as e:
                await flood_sleep(e)
            except Exception:
                await asyncio.sleep(0.05)
        await safe_reply(event, f"✅ Spam done: {count}")

    @c.on(events.NewMessage(pattern=pfx("vegeta"), outgoing=True))
    async def cmd_vegeta(event):
        args = get_args(event)
        if not args:
            await safe_reply(event, f"Usage: `{PREFIX}vegeta <text>`")
            return
        cid = event.chat_id
        for _ in range(10):
            try:
                await c.send_message(cid, args)
                await asyncio.sleep(SPAM_DELAY)
            except FloodWaitError as e:
                await flood_sleep(e)
            except Exception:
                await asyncio.sleep(0.05)
        await safe_reply(event, "✅ Vegeta spam done")

    @c.on(events.NewMessage(pattern=pfx("fasternc"), outgoing=True))
    async def cmd_fasternc(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args:
            await safe_reply(event, f"Usage: `{PREFIX}fasternc <text>`")
            return
        cid = event.chat_id
        words = ["LUND", "TBKC", "TMR", "CHUD", "RANDI", "GULAM"]

        async def loop():
            idx = 0
            while True:
                try:
                    word = words[idx % len(words)]
                    title = f"{args} 💥🔥{word}🔥💥"[:128]
                    await c(EditTitleRequest(channel=cid, title=title))
                    idx += 1
                    await asyncio.sleep(SPAM_DELAY)
                except FloodWaitError as e:
                    await flood_sleep(e)
                except asyncio.CancelledError:
                    return
                except Exception:
                    await asyncio.sleep(0.05)

        tm.add("nc", loop())
        await safe_reply(event, f"⚡ FasterNC for `{args}`\n`.stop`")

    @c.on(events.NewMessage(pattern=pfx("multinc"), outgoing=True))
    async def cmd_multinc(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args:
            await safe_reply(event, f"Usage: `{PREFIX}multinc <text>`")
            return
        cid = event.chat_id
        styles = [
            lambda t: f"꧁{t}꧂🔥",
            lambda t: f"⚡{t}⚡💀",
            lambda t: f"💥{t}💥👑",
            lambda t: f"🌟{t}🌟",
            lambda t: f"💀{t}💀",
            lambda t: f"🔥🔥{t}🔥🔥",
            lambda t: f"卍{t}卍",
            lambda t: f"☠️{t}☠️",
            lambda t: f"༒{t}༒",
            lambda t: f"꧁{t}꧂☄️",
        ]

        async def loop():
            idx = 0
            while True:
                try:
                    title = styles[idx % len(styles)](args)[:128]
                    await c(EditTitleRequest(channel=cid, title=title))
                    idx += 1
                    await asyncio.sleep(SPAM_DELAY)
                except FloodWaitError as e:
                    await flood_sleep(e)
                except asyncio.CancelledError:
                    return
                except Exception:
                    await asyncio.sleep(0.05)

        tm.add("multinc", loop())
        await safe_reply(event, f"🌀 MultiNC for `{args}`\n`.stop`")

    # ─── REACT ───
    @c.on(events.NewMessage(pattern=pfx("autoreact"), outgoing=True))
    async def cmd_autoreact(event):
        global AUTO_REACT_ON
        if not await owner_only(event):
            return
        args = get_args(event).lower()
        if args == "on":
            AUTO_REACT_ON = True
            save_auto_react()
            await safe_reply(event, "✅ Auto-react ON")
        elif args == "off":
            AUTO_REACT_ON = False
            save_auto_react()
            await safe_reply(event, "❌ Auto-react OFF")
        else:
            await safe_reply(event, f"Usage: `{PREFIX}autoreact on/off`")

    @c.on(events.NewMessage(pattern=pfx("setreact"), outgoing=True))
    async def cmd_setreact(event):
        global AUTO_REACT_EMOJI
        if not await owner_only(event):
            return
        emoji = get_args(event)
        if not emoji:
            await safe_reply(event, f"Usage: `{PREFIX}setreact 🔥`")
            return
        AUTO_REACT_EMOJI = emoji[0] if len(emoji) > 1 else emoji
        save_auto_react()
        await safe_reply(event, f"✅ Auto-react: `{AUTO_REACT_EMOJI}`")

    @c.on(events.NewMessage(pattern=pfx("react"), outgoing=True))
    async def cmd_react_toggle(event):
        await cmd_autoreact(event)

    @c.on(events.NewMessage(pattern=pfx("reactall"), outgoing=True))
    async def cmd_reactall(event):
        if not await owner_only(event):
            return
        emoji = get_args(event)
        if not emoji:
            await safe_reply(event, f"Usage: `{PREFIX}reactall 🔥`")
            return
        emoji = emoji[0]
        cid = event.chat_id
        count = 0
        async for msg in c.iter_messages(cid, limit=100):
            try:
                await c(SendReactionRequest(
                    peer=cid, msg_id=msg.id,
                    reaction=[ReactionEmoji(emoticon=emoji)]
                ))
                count += 1
                await asyncio.sleep(0.05)
            except Exception:
                pass
        await safe_reply(event, f"✅ Reacted `{count}` msgs with `{emoji}`")

    # ─── GBAN ───
    @c.on(events.NewMessage(pattern=pfx("gban"), outgoing=True))
    async def cmd_gban(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        uid = r.sender_id
        GBAN_USERS.add(uid)
        save_gban()
        try:
            await c(EditBannedRequest(
                event.chat_id, uid,
                ChatBannedRights(until_date=None, view_messages=True)
            ))
        except Exception:
            pass
        await safe_reply(event, f"🌐 GBanned `{uid}`")

    @c.on(events.NewMessage(pattern=pfx("ungban"), outgoing=True))
    async def cmd_ungban(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        uid = r.sender_id
        GBAN_USERS.discard(uid)
        save_gban()
        await safe_reply(event, f"✅ Ungban `{uid}`")

    @c.on(events.NewMessage(pattern=pfx("gbanlist"), outgoing=True))
    async def cmd_gbanlist(event):
        if not await owner_only(event):
            return
        if not GBAN_USERS:
            await safe_reply(event, "No gban users")
            return
        await safe_reply(event, "🌐 **GBan:**\n" + "\n".join(f"• `{u}`" for u in GBAN_USERS))

    # ─── MASS ───
    @c.on(events.NewMessage(pattern=pfx("massdm"), outgoing=True))
    async def cmd_massdm(event):
        if not await owner_only(event):
            return
        text = get_args(event)
        if not text:
            await safe_reply(event, f"Usage: `{PREFIX}massdm <text>`")
            return
        count = 0
        async for dialog in c.iter_dialogs():
            if dialog.is_user and not getattr(dialog.entity, "bot", False):
                try:
                    await c.send_message(dialog.id, text)
                    count += 1
                    await asyncio.sleep(0.5)
                except Exception:
                    pass
        await safe_reply(event, f"✅ Mass DM: `{count}`")

    @c.on(events.NewMessage(pattern=pfx("broadcast"), outgoing=True))
    async def cmd_broadcast(event):
        if not await owner_only(event):
            return
        text = get_args(event)
        if not text:
            await safe_reply(event, f"Usage: `{PREFIX}broadcast <text>`")
            return
        count = 0
        async for dialog in c.iter_dialogs():
            if dialog.is_group:
                try:
                    await c.send_message(dialog.id, f"📢 {text}")
                    count += 1
                    await asyncio.sleep(0.5)
                except Exception:
                    pass
        await safe_reply(event, f"✅ Broadcast: `{count}` groups")

    # ─── UTILS ───
    @c.on(events.NewMessage(pattern=pfx("weather"), outgoing=True))
    async def cmd_weather(event):
        if not await owner_only(event):
            return
        city = get_args(event)
        if not city:
            await safe_reply(event, f"Usage: `{PREFIX}weather <city>`")
            return
        try:
            resp = requests.get(f"https://wttr.in/{city}?format=%C+%t+%w+%h", timeout=10)
            if resp.status_code == 200:
                await safe_reply(event, f"🌤 **{city}:**\n{resp.text.strip()}")
            else:
                await safe_reply(event, "❌ City not found")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("wiki"), outgoing=True))
    async def cmd_wiki(event):
        if not await owner_only(event):
            return
        query = get_args(event)
        if not query:
            await safe_reply(event, f"Usage: `{PREFIX}wiki <query>`")
            return
        try:
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query.replace(' ', '_')}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                await safe_reply(event, f"📚 **{data.get('title', query)}**\n{data.get('extract', '')[:800]}")
            else:
                await safe_reply(event, "❌ Not found")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("translate"), outgoing=True))
    async def cmd_translate(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args or " " not in args:
            await safe_reply(event, f"Usage: `{PREFIX}translate hi Hello`")
            return
        lang, text = args.split(maxsplit=1)
        try:
            url = f"https://api.mymemory.translated.net/get?q={text}&langpair=en|{lang}"
            resp = requests.get(url, timeout=10)
            if resp.status_code == 200:
                t = resp.json().get("responseData", {}).get("translatedText", "Error")
                await safe_reply(event, f"🌐 **{lang}:**\n{t}")
            else:
                await safe_reply(event, "❌ Failed")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("speedtest"), outgoing=True))
    async def cmd_speedtest(event):
        if not await owner_only(event):
            return
        await safe_reply(event, "📡 Speedtest... (20s)")
        try:
            import speedtest
            st = speedtest.Speedtest()
            st.get_best_server()
            down = st.download() / 1e6
            up = st.upload() / 1e6
            ping = st.results.ping
            await safe_reply(
                event,
                f"📡 **Speedtest**\n⬇️ `{down:.2f} Mbps`\n⬆️ `{up:.2f} Mbps`\n⏱ `{ping:.0f} ms`"
            )
        except ImportError:
            await safe_reply(event, "❌ pip install speedtest-cli")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("calc"), outgoing=True))
    async def cmd_calc(event):
        if not await owner_only(event):
            return
        expr = get_args(event)
        if not expr:
            await safe_reply(event, f"Usage: `{PREFIX}calc 2+2`")
            return
        if not all(ch in "0123456789+-*/().% " for ch in expr):
            await safe_reply(event, "❌ Only basic math")
            return
        try:
            result = eval(expr, {"__builtins__": {}}, {})
            await safe_reply(event, f"`{expr} = {result}`")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    # ─── ADMIN ───
    @c.on(events.NewMessage(pattern=pfx("ban"), outgoing=True))
    async def cmd_ban(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        try:
            await c(EditBannedRequest(
                event.chat_id, r.sender_id,
                ChatBannedRights(until_date=None, view_messages=True)
            ))
            await safe_reply(event, f"🚫 Banned `{r.sender_id}`")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("unban"), outgoing=True))
    async def cmd_unban(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        try:
            await c(EditBannedRequest(event.chat_id, r.sender_id, ChatBannedRights(until_date=None)))
            await safe_reply(event, f"✅ Unbanned `{r.sender_id}`")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("kick"), outgoing=True))
    async def cmd_kick(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        try:
            await c.kick_participant(event.chat_id, r.sender_id)
            await safe_reply(event, f"👢 Kicked `{r.sender_id}`")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("mute"), outgoing=True))
    async def cmd_mute(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        uid = r.sender_id
        msg = f"🔇 Muted `{uid}`"
        try:
            await c(EditBannedRequest(
                event.chat_id, uid,
                ChatBannedRights(until_date=None, send_messages=True)
            ))
            MUTED_USERS.add(uid)
        except Exception:
            msg += "\n⚠️ Restrict failed — Force Mute ON"
        FORCE_MUTED.add(uid)
        await safe_reply(event, msg)

    @c.on(events.NewMessage(pattern=pfx("unmute"), outgoing=True))
    async def cmd_unmute(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        uid = r.sender_id
        MUTED_USERS.discard(uid)
        FORCE_MUTED.discard(uid)
        try:
            await c(EditBannedRequest(event.chat_id, uid, ChatBannedRights(until_date=None)))
        except Exception:
            pass
        await safe_reply(event, f"🔊 Unmuted `{uid}`")

    @c.on(events.NewMessage(pattern=pfx("gmute"), outgoing=True))
    async def cmd_gmute(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        uid = r.sender_id
        GMUTED_USERS.add(uid)
        FORCE_MUTED.add(uid)
        await safe_reply(event, f"🌐 GMuted `{uid}`")

    @c.on(events.NewMessage(pattern=pfx("ungmute"), outgoing=True))
    async def cmd_ungmute(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        uid = r.sender_id
        GMUTED_USERS.discard(uid)
        FORCE_MUTED.discard(uid)
        await safe_reply(event, f"✅ UnGMute `{uid}`")

    @c.on(events.NewMessage(pattern=pfx("promote"), outgoing=True))
    @c.on(events.NewMessage(pattern=pfx("admin"), outgoing=True))
    async def cmd_promote(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        rights = ChatAdminRights(
            change_info=True, delete_messages=True, ban_users=True,
            invite_users=True, pin_messages=True, manage_call=True
        )
        try:
            await c(EditAdminRequest(event.chat_id, r.sender_id, rights, "Admin"))
            await safe_reply(event, f"✅ Promoted `{r.sender_id}`")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("demote"), outgoing=True))
    @c.on(events.NewMessage(pattern=pfx("take"), outgoing=True))
    async def cmd_demote(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        try:
            await c(EditAdminRequest(event.chat_id, r.sender_id, ChatAdminRights(), ""))
            await safe_reply(event, f"✅ Demoted `{r.sender_id}`")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("purge"), outgoing=True))
    async def cmd_purge(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to starting message")
            return
        r = await event.get_reply_message()
        msgs = [m.id async for m in c.iter_messages(event.chat_id, min_id=r.id - 1, max_id=event.id)]
        try:
            await c.delete_messages(event.chat_id, msgs)
            await safe_reply(event, f"🧹 Purged `{len(msgs)}`")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("del"), outgoing=True))
    async def cmd_del(event):
        if not await owner_only(event):
            return
        if event.is_reply:
            try:
                await (await event.get_reply_message()).delete()
                await event.delete()
            except Exception:
                pass

    @c.on(events.NewMessage(pattern=pfx("pin"), outgoing=True))
    async def cmd_pin(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to message")
            return
        try:
            await c.pin_message(event.chat_id, (await event.get_reply_message()).id)
            await safe_reply(event, "📌 Pinned")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("unpin"), outgoing=True))
    async def cmd_unpin(event):
        if not await owner_only(event):
            return
        try:
            await c.unpin_message(event.chat_id)
            await safe_reply(event, "📌 Unpinned")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("lock"), outgoing=True))
    async def cmd_lock(event):
        if not await owner_only(event):
            return
        try:
            rights = ChatBannedRights(
                until_date=None,
                send_messages=True, send_media=True, send_stickers=True,
                send_gifs=True, send_games=True, send_inline=True, send_polls=True,
                change_info=True, invite_users=True, pin_messages=True
            )
            await c(EditChatDefaultBannedRightsRequest(event.chat_id, rights))
            await safe_reply(event, "🔒 Locked")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("unlock"), outgoing=True))
    async def cmd_unlock(event):
        if not await owner_only(event):
            return
        try:
            await c(EditChatDefaultBannedRightsRequest(event.chat_id, ChatBannedRights(until_date=None)))
            await safe_reply(event, "🔓 Unlocked")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    # ─── WARN ───
    @c.on(events.NewMessage(pattern=pfx("warn"), outgoing=True))
    async def cmd_warn(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        uid = r.sender_id
        WARN_COUNT[uid] += 1
        save_warns()
        count = WARN_COUNT[uid]
        await safe_reply(event, f"⚠️ Warned `{uid}` — **{count}**")
        if count >= 3:
            try:
                await c(EditBannedRequest(
                    event.chat_id, uid,
                    ChatBannedRights(until_date=None, view_messages=True)
                ))
                await safe_reply(event, f"🚫 Auto-ban `{uid}` (3 warns)")
            except Exception:
                pass

    @c.on(events.NewMessage(pattern=pfx("warns"), outgoing=True))
    async def cmd_warns(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        await safe_reply(event, f"⚠️ `{r.sender_id}` has **{WARN_COUNT.get(r.sender_id, 0)}** warns")

    @c.on(events.NewMessage(pattern=pfx("resetwarns"), outgoing=True))
    async def cmd_resetwarns(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        WARN_COUNT[r.sender_id] = 0
        save_warns()
        await safe_reply(event, f"✅ Warns reset `{r.sender_id}`")

    # ─── CLONE / PFP ───
    @c.on(events.NewMessage(pattern=pfx("clone"), outgoing=True))
    @c.on(events.NewMessage(pattern=pfx("fullclone"), outgoing=True))
    @c.on(events.NewMessage(pattern=pfx("clonejutsu"), outgoing=True))
    async def cmd_fullclone(event):
        if not await owner_only(event):
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to target user → `.clonejutsu`")
            return
        r = await event.get_reply_message()
        u = await r.get_sender()
        me = await c.get_me()
        status = []
        try:
            # Save YOUR original profile for .back
            full_me = await c(GetFullUserRequest(me.id))
            CLONE_DATA["first"] = me.first_name or ""
            CLONE_DATA["last"] = me.last_name or ""
            CLONE_DATA["bio"] = full_me.full_user.about or ""
            CLONE_DATA["username"] = me.username or ""
            # Save original PFP to disk
            orig_pfp = DATA_DIR / "original_pfp.jpg"
            try:
                saved = await c.download_profile_photo("me", file=str(orig_pfp))
                CLONE_DATA["pfp_saved"] = bool(saved)
            except Exception:
                CLONE_DATA["pfp_saved"] = False

            # Target profile
            first = u.first_name or " "
            last = u.last_name or ""
            try:
                target_full = await c(GetFullUserRequest(u.id))
                bio = target_full.full_user.about or ""
            except Exception:
                bio = ""

            await c(UpdateProfileRequest(
                first_name=first[:64],
                last_name=last[:64],
                about=(bio or "")[:70]
            ))
            status.append(f"✅ Name: {first} {last}".strip())
            status.append(f"✅ Bio: {(bio or '—')[:40]}")

            if u.username:
                try:
                    await c(UpdateUsernameRequest(username=u.username))
                    status.append(f"✅ Username: @{u.username}")
                except Exception:
                    status.append("⚠️ Username taken / failed (Telegram limit)")
            else:
                status.append("⚠️ Target has no username")

            # Target PFP
            pfp_path = None
            try:
                pfp_path = await c.download_profile_photo(u, file=str(DATA_DIR / "clone_pfp.jpg"))
                if pfp_path:
                    uploaded = await c.upload_file(pfp_path)
                    await c(UploadProfilePhotoRequest(file=uploaded))
                    status.append("✅ Profile photo")
                else:
                    status.append("⚠️ No profile photo")
            except Exception as pe:
                status.append(f"⚠️ Photo: {pe}")
            finally:
                if pfp_path:
                    try:
                        os.remove(pfp_path)
                    except Exception:
                        pass

            await safe_reply(
                event,
                f"✅ **CLONED {get_display_name(u)}'S PROFILE!**\n\n"
                + "\n".join(status)
                + f"\n\n`{PREFIX}back` se wapas normal ho jaoge"
            )
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("revert"), outgoing=True))
    @c.on(events.NewMessage(pattern=pfx("back"), outgoing=True))
    async def cmd_revert(event):
        if not await owner_only(event):
            return
        if not CLONE_DATA:
            await safe_reply(event, "❌ Pehle koi clone nahi hua")
            return
        status = []
        try:
            await c(UpdateProfileRequest(
                first_name=CLONE_DATA.get("first", "User") or "User",
                last_name=CLONE_DATA.get("last", "") or "",
                about=CLONE_DATA.get("bio", "") or ""
            ))
            status.append("✅ Name + Bio restored")

            old_user = CLONE_DATA.get("username", "") or ""
            if old_user:
                try:
                    await c(UpdateUsernameRequest(username=old_user))
                    status.append(f"✅ Username @{old_user}")
                except Exception:
                    status.append("⚠️ Username restore failed")
            else:
                try:
                    await c(UpdateUsernameRequest(username=""))
                    status.append("✅ Username cleared")
                except Exception:
                    pass

            # Restore original PFP
            orig_pfp = DATA_DIR / "original_pfp.jpg"
            if CLONE_DATA.get("pfp_saved") and orig_pfp.exists():
                try:
                    uploaded = await c.upload_file(str(orig_pfp))
                    await c(UploadProfilePhotoRequest(file=uploaded))
                    status.append("✅ Profile photo restored")
                except Exception as pe:
                    status.append(f"⚠️ Photo restore: {pe}")
            else:
                status.append("⚠️ Original photo not saved")

            await safe_reply(event, "🌿 **BACK TO NORMAL**\n\n" + "\n".join(status))
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("setpfp"), outgoing=True))
    async def cmd_setpfp(event):
        if not await owner_only(event):
            return
        if not event.is_reply or not (await event.get_reply_message()).photo:
            await safe_reply(event, "Reply to a photo")
            return
        try:
            path = await c.download_media((await event.get_reply_message()).photo)
            if not path:
                await safe_reply(event, "❌ Download failed")
                return
            uploaded = await c.upload_file(path)
            await c(UploadProfilePhotoRequest(file=uploaded))
            await safe_reply(event, "✅ Profile photo set")
            try:
                os.remove(path)
            except Exception:
                pass
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("delpfp"), outgoing=True))
    async def cmd_delpfp(event):
        if not await owner_only(event):
            return
        try:
            photos = await c.get_profile_photos("me")
            if photos:
                await c(DeletePhotosRequest(id=photos[:1]))
                await safe_reply(event, "✅ Removed")
            else:
                await safe_reply(event, "No photo")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    # ─── JOIN / LEAVE ───
    @c.on(events.NewMessage(pattern=pfx("join"), outgoing=True))
    async def cmd_join(event):
        if not await owner_only(event):
            return
        link = get_args(event)
        if not link:
            await safe_reply(event, f"Usage: `{PREFIX}join <link>`")
            return
        try:
            if "+" in link or "joinchat" in link:
                h = link.split("+")[-1].split("/")[-1].split("?")[0]
                await c(ImportChatInviteRequest(h))
            else:
                await c(JoinChannelRequest(link))
            await safe_reply(event, "✅ Joined")
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    @c.on(events.NewMessage(pattern=pfx("leave"), outgoing=True))
    async def cmd_leave(event):
        if not await owner_only(event):
            return
        try:
            await c(LeaveChannelRequest(event.chat_id))
        except Exception as e:
            await safe_reply(event, f"❌ {e}")

    # ─── AFK (unafk only — no conflict with revert) ───
    @c.on(events.NewMessage(pattern=pfx("afk"), outgoing=True))
    async def cmd_afk(event):
        global AFK_MODE, AFK_REASON, AFK_START
        if not await owner_only(event):
            return
        AFK_MODE = True
        AFK_REASON = get_args(event) or "AFK"
        AFK_START = time.time()
        await safe_reply(event, f"💤 AFK: `{AFK_REASON}`")

    @c.on(events.NewMessage(pattern=pfx("unafk"), outgoing=True))
    async def cmd_unafk(event):
        global AFK_MODE
        if not await owner_only(event):
            return
        AFK_MODE = False
        await safe_reply(event, "✅ Back (AFK off)")

    @c.on(events.NewMessage(pattern=pfx("ghost"), outgoing=True))
    async def cmd_ghost(event):
        global GHOST_MODE
        if not await owner_only(event):
            return
        GHOST_MODE = not GHOST_MODE
        await safe_reply(event, f"👻 Ghost: **{'ON' if GHOST_MODE else 'OFF'}**")

    # ─── FILTERS / NOTES ───
    @c.on(events.NewMessage(pattern=pfx("filter"), outgoing=True))
    async def cmd_filter(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args or " " not in args:
            await safe_reply(event, f"Usage: `{PREFIX}filter <trigger> <reply>`")
            return
        trig, resp = args.split(" ", 1)
        FILTERS[trig.lower()] = resp
        save_filters()
        await safe_reply(event, f"✅ Filter `{trig}`")

    @c.on(events.NewMessage(pattern=pfx("filters"), outgoing=True))
    async def cmd_filters(event):
        if not await owner_only(event):
            return
        if not FILTERS:
            await safe_reply(event, "No filters")
            return
        await safe_reply(event, "**Filters:**\n" + "\n".join(f"• `{k}`" for k in FILTERS))

    @c.on(events.NewMessage(pattern=pfx("stopfilter"), outgoing=True))
    async def cmd_stopfilter(event):
        if not await owner_only(event):
            return
        trig = get_args(event).lower()
        if trig in FILTERS:
            del FILTERS[trig]
            save_filters()
            await safe_reply(event, f"🗑️ Removed `{trig}`")
        else:
            await safe_reply(event, "Not found")

    @c.on(events.NewMessage(pattern=pfx("note"), outgoing=True))
    async def cmd_note(event):
        if not await owner_only(event):
            return
        args = get_args(event)
        if not args or " " not in args:
            await safe_reply(event, f"Usage: `{PREFIX}note <name> <text>`")
            return
        name, content = args.split(" ", 1)
        NOTES[name.lower()] = content
        save_notes()
        await safe_reply(event, f"✅ Note `{name}`")

    @c.on(events.NewMessage(pattern=pfx("getnote"), outgoing=True))
    async def cmd_getnote(event):
        if not await owner_only(event):
            return
        name = get_args(event).lower()
        if name in NOTES:
            await safe_reply(event, NOTES[name])
        else:
            await safe_reply(event, "Not found")

    @c.on(events.NewMessage(pattern=pfx("notes"), outgoing=True))
    async def cmd_notes(event):
        if not await owner_only(event):
            return
        if not NOTES:
            await safe_reply(event, "No notes")
            return
        await safe_reply(event, "**Notes:**\n" + "\n".join(f"• `{k}`" for k in NOTES))

    @c.on(events.NewMessage(pattern=pfx("setwelcome"), outgoing=True))
    async def cmd_setwelcome(event):
        if not await owner_only(event):
            return
        text = get_args(event)
        if not text:
            await safe_reply(event, f"Usage: `{PREFIX}setwelcome Welcome {{name}}`")
            return
        WELCOME_MSG[str(event.chat_id)] = text
        save_welcome()
        await safe_reply(event, "✅ Welcome set")

    # ─── SUDO ───
    @c.on(events.NewMessage(pattern=pfx("sudo"), outgoing=True))
    @c.on(events.NewMessage(pattern=pfx("sub"), outgoing=True))
    async def cmd_sudo(event):
        if event.sender_id != OWNER_ID:
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        uid = r.sender_id
        SUDO_USERS.add(uid)
        save_sudo()
        await safe_reply(event, f"🤍 Access given `{uid}`")

    @c.on(events.NewMessage(pattern=pfx("antisub"), outgoing=True))
    async def cmd_antisub(event):
        if event.sender_id != OWNER_ID:
            return
        if not event.is_reply:
            await safe_reply(event, "Reply to user")
            return
        r = await event.get_reply_message()
        uid = r.sender_id
        SUDO_USERS.discard(uid)
        save_sudo()
        await safe_reply(event, f"🖤 Access revoked `{uid}`")

    @c.on(events.NewMessage(pattern=pfx("sudolist"), outgoing=True))
    async def cmd_sudolist(event):
        if not await owner_only(event):
            return
        if not SUDO_USERS:
            await safe_reply(event, "No sudo")
            return
        await safe_reply(event, "**Sudo:**\n" + "\n".join(f"• `{u}`" for u in SUDO_USERS))

    # ─── PREFIX ───
    @c.on(events.NewMessage(pattern=r"(?i)^[.!/\-]setprefix(?:\s|$)", outgoing=True))
    async def cmd_setprefix(event):
        global PREFIX
        if event.sender_id != OWNER_ID:
            return
        text = (event.raw_text or "").strip()
        parts = text.split(maxsplit=1)
        if len(parts) < 2 or not parts[1].strip():
            await safe_reply(event, f"Current: `{PREFIX}`\nUsage: `{PREFIX}setprefix <new>`")
            return
        new_p = parts[1].strip()
        if len(new_p) > 10:
            await safe_reply(event, "Max 10 chars")
            return
        old = PREFIX
        PREFIX = new_p
        save_settings()
        await safe_reply(event, f"✅ Prefix `{old}` → `{PREFIX}`\n**Restart** script to apply handlers.")

    # ─── PASS LOCK ───
    @c.on(events.NewMessage(pattern=pfx("passlock"), outgoing=True))
    async def cmd_passlock(event):
        if not await owner_only(event):
            return
        pwd = get_args(event)
        if not pwd:
            await safe_reply(event, f"Usage: `{PREFIX}passlock <password>`")
            return
        cid = event.chat_id
        PASS_LOCK[cid] = {"password": pwd, "allowed": set()}
        try:
            rights = ChatBannedRights(
                until_date=None,
                send_messages=True, send_media=True, send_stickers=True,
                send_gifs=True, send_games=True, send_inline=True, send_polls=True
            )
            await c(EditChatDefaultBannedRightsRequest(cid, rights))
        except Exception:
            pass
        await safe_reply(event, f"🔒 PassLock ON: `{pwd}`\n`{PREFIX}passunlock` to off")

    @c.on(events.NewMessage(pattern=pfx("passunlock"), outgoing=True))
    async def cmd_passunlock(event):
        if not await owner_only(event):
            return
        cid = event.chat_id
        PASS_LOCK.pop(cid, None)
        try:
            await c(EditChatDefaultBannedRightsRequest(cid, ChatBannedRights(until_date=None)))
        except Exception:
            pass
        await safe_reply(event, "🔓 PassLock OFF")

    @c.on(events.NewMessage(pattern=pfx("passstatus"), outgoing=True))
    async def cmd_passstatus(event):
        if not await owner_only(event):
            return
        cid = event.chat_id
        if cid not in PASS_LOCK:
            await safe_reply(event, "🔐 PassLock: OFF")
            return
        data = PASS_LOCK[cid]
        await safe_reply(
            event,
            f"🔐 ON | pwd: `{data['password']}` | verified: `{len(data.get('allowed', set()))}`"
        )

    # ─── RESTART (auto re-run after 5s — no manual start) ───
    @c.on(events.NewMessage(pattern=pfx("restart"), outgoing=True))
    async def cmd_restart(event):
        if event.sender_id != OWNER_ID:
            return
        await safe_reply(event, "🔄 Restarting in 5 seconds...\nScript khud start ho jayegi.")
        await tm.stop_all()
        try:
            flag = DATA_DIR / ".restart_flag"
            flag.write_text("1")
        except Exception:
            pass
        try:
            await c.disconnect()
        except Exception:
            pass
        # Prefer in-process relaunch after delay
        await asyncio.sleep(5)
        try:
            os.execv(sys.executable, [sys.executable] + sys.argv)
        except Exception:
            # Fallback: exit with special code → outer watchdog restarts
            sys.exit(42)

    # ─── INCOMING ───
    @c.on(events.NewMessage(incoming=True))
    async def incoming_handlers(event):
        if event.out:
            return
        uid = event.sender_id
        cid = event.chat_id

        if uid in GBAN_USERS:
            try:
                await event.delete()
                await c(EditBannedRequest(
                    cid, uid, ChatBannedRights(until_date=None, view_messages=True)
                ))
            except Exception:
                pass
            return

        if uid in FORCE_MUTED or uid in GMUTED_USERS:
            try:
                await event.delete()
            except Exception:
                pass
            return

        if cid in PASS_LOCK:
            if is_owner(uid):
                return
            data = PASS_LOCK[cid]
            allowed = data.get("allowed", set())
            pwd = data.get("password", "")
            text = (event.raw_text or "").strip()
            if text == pwd:
                allowed.add(uid)
                data["allowed"] = allowed
                try:
                    await event.delete()
                    await event.respond("✅ Access granted!")
                except Exception:
                    pass
                return
            if uid not in allowed:
                try:
                    await event.delete()
                except Exception:
                    pass
            return

        if AFK_MODE and (event.is_private or event.mentioned):
            now = time.time()
            if now - AFK_LAST_REPLY.get(uid, 0) > 30:
                AFK_LAST_REPLY[uid] = now
                try:
                    elapsed = int(now - AFK_START)
                    await event.reply(f"💤 AFK: `{AFK_REASON}`\n({elapsed}s)")
                except Exception:
                    pass

        if AUTO_REACT_ON and AUTO_REACT_EMOJI:
            try:
                await c(SendReactionRequest(
                    peer=cid, msg_id=event.id,
                    reaction=[ReactionEmoji(emoticon=AUTO_REACT_EMOJI)]
                ))
            except Exception:
                pass

        text = (event.raw_text or "").lower()
        for t, r in FILTERS.items():
            if t in text:
                try:
                    await event.reply(r)
                except Exception:
                    pass
                break

    @c.on(events.ChatAction)
    async def welcome_handler(event):
        if not event.user_joined and not event.user_added:
            return
        msg = WELCOME_MSG.get(str(event.chat_id))
        if not msg:
            return
        try:
            user = await event.get_user()
            name = get_display_name(user) if user else "User"
            await event.reply(msg.replace("{name}", name))
        except Exception:
            pass


# ─── MAIN ───
async def main():
    global API_ID, API_HASH, OWNER_ID, SESSION_NAME, client, START_TIME

    config = setup_config()
    API_ID = config["api_id"]
    API_HASH = config["api_hash"]
    OWNER_ID = config["owner_id"]
    SESSION_NAME = config["session_name"]
    START_TIME = time.time()

    print("=" * 50)
    print("  VEGETA FIGHTER – ULTIMATE USERBOT (FIXED)")
    print("=" * 50)

    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)
    globals()["client"] = client

    load_all()
    register_handlers(client)

    await client.start()
    me = await client.get_me()
    print(f"✅ Logged in: {get_display_name(me)}")
    print(f"👑 Owner: {OWNER_ID} | Prefix: [{PREFIX}]")
    print(f"🐌 Delay: {SPAM_DELAY}s | FloodWait = sleep & continue")
    print("=" * 50)
    await client.run_until_disconnected()


if __name__ == "__main__":
    # Watchdog: .restart → 5s wait → auto start (no manual run)
    while True:
        try:
            flag = DATA_DIR / ".restart_flag"
            if flag.exists():
                try:
                    flag.unlink()
                except Exception:
                    pass
                print("🔄 Restart flag found — starting in 5 seconds...")
                time.sleep(5)
            asyncio.run(main())
            break
        except KeyboardInterrupt:
            print("\n🛑 Stopped")
            break
        except SystemExit as e:
            if getattr(e, "code", None) == 42:
                print("🔄 Exit 42 — auto-restart in 5s...")
                time.sleep(5)
                continue
            break
        except Exception as e:
            print(f"❌ {e}")
            traceback.print_exc()
            print("🔄 Crash — retry in 5s... (Ctrl+C to stop)")
            try:
                time.sleep(5)
            except KeyboardInterrupt:
                break
