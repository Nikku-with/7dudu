#!/usr/bin/env python3
# Multi-bot GC / Slide / Swipe tool (updated TOKENS & OWNER)
# - Spawns one Application per token and registers command handlers on each.
# - Commands available (same as original): /gcnc, /ncemo, /stopgcnc, /stopall, /delay, /status,
#   /targetslide, /stopslide, /slidespam, /stopslidespam, /swipe, /stopswipe,
#   /addsudo, /delsudo, /listsudo, /myid, /ping, /help
#
# NOTE: #𝘈𝘳𝘤𝘢𝘥𝘦 × 𝘠𝘢𝘴𝘰𝘥 × 𝘛𝘦𝘳𝘮𝘪 × 𝘔𝘢𝘥𝘢𝘳𝘢 × 𝘋𝘦𝘷𝘪𝘭 × 𝘚𝘶𝘬𝘶𝘯𝘢 𝘊𝘩𝘶𝘥𝘢𝘪 𝘚𝘤𝘳𝘪𝘱𝘵

import subprocess
import sys


def _ensure_deps():
    required = {"python-telegram-bot": "telegram"}
    for pkg, module in required.items():
        try:
            __import__(module)
        except ImportError:
            print(f"[SETUP] Installing {pkg}...")
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", f"{pkg}[all]"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            print(f"[SETUP] {pkg} installed successfully.")


_ensure_deps()

import asyncio
import json
import os
import random
import time
import logging
from typing import Dict
from telegram import Update
from telegram.error import RetryAfter, TimedOut, NetworkError
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ---------------------------
# CONFIG (UPDATED)
# ---------------------------
TOKENS = [
"8452664352:AAFLr_yrhjiBYOsbaLd90dqEVe-Fb1jijoM", 
"8560230273:AAHvWcuxYhSL5wh9j4BjS8vjucrj2cOKsbY",
"8442896167:AAH0fN-l5AFcEO8eXaL2feB41WeH87bM8kc", 
"8252325923:AAHl9MKDD79UgMOinwmSGFdv-mWMjeQDhQc", 
"8467261414:AAFEIXZ3PJ8ELSZEyLdLNDEQuRXwA_2brG0", 
"8356273614:AAEGoxXSfPwqm9gq_5fLk2dxEntRWPvAGkE", 
"8278353006:AAE45O8--r8e2RahKJs2AsYjnvt86b5XryI", 
"8457661652:AAFPuCmejpyA5_x4mNEX0wB0RQLSjPry0b8", 
"8564666249:AAG1DYB1BGleFJGrG0X8Mz3w1oJ-YZXw-3Q", 
"8400838936:AAG9oth5UPw5w26dH5_aTOixeyNn_jOhIaU", 
"8067783203:AAFnIMm2i9tWit3WA8MZSzc-ILpAb-QlBvA", 
"8402996493:AAFSk3LDSg61GW_cadP7IsANAvT1I3n0CRQ", 
"8560390965:AAHn2qa8mTjssSq3r7PqcgJzCWWPt_7rVeA",
"8520649128:AAFR22Y5Zq6Jk2yifY6HA0lpKlerE0sPmos",
"8312358658:AAFWXrn9SG5b8SLvnXWIXEeG0E9myksQiqI",  
]

# Owner / initial sudo
OWNER_ID = 6552187447
SUDO_FILE = "sudo.json"

# ---------------------------
# RAID TEXTS & EMOJIS
# ---------------------------
RAID_TEXTS = [
    "Gᴜʟᴀᴍɪ ᴋʀ ——➤(🎀)",
    "Tᴇʀɪ Mᴀᴀ Cʜᴜᴅɪ ——➤(🎀)",
    "Sᴀʟᴀᴍ Tʜᴏᴋ ——➤(🎀)",
    "Cʜɪɴᴀᴀʀ ——➤(🎀)",
    "Mᴀᴢᴅᴏᴏʀ ——➤(🎀)",
    "Hᴀᴡᴀʙᴀᴢᴢ ——➤(🎀)",
    "Kᴇɴᴛᴏ अब्बू  ʙᴏʟ——➤(🎀)",
    "Tᴍᴋʟ ——➤(🎀)",
    "ᴋᴀᴍᴢᴏʀ Kᴜᴛɪʏᴀ ——➤(🎀)",
    "Bʜᴇᴇᴋ Mᴀɴɢ ——➤(🎀)",
    "RɴᴅɪMᴏɴ ——➤(🎀)",
    "Cʜᴜᴅᴀɪ Kɪᴅᴅᴇ ——➤(🎀)",
    "Gʜᴀᴛɪʏᴀ Bᴇᴛᴀ ——➤(🎀)",
    "Tᴇʀᴀ Bᴀᴀᴘ x𝘒𝘦𝘯𝘵𝘰 ——➤(🎀)",
    "GAɴᴅ Mᴀʀᴀ ᴍᴜʟʟᴇ ——➤(🎀)",
    "Cʜᴜᴅᴇɢɪ TᴇʀɪMA ——➤(🎀)",
    "BɪᴛCʜ ——➤(🎀)",
    "HɪᴊᴅᴜSᴏɴ ——➤(🎀)",
    "Nᴀʟɪ Sᴀғ Kᴀʀ ᴊAᴋᴇ ——➤(🎀)",
    "GʜɪNᴏɴɪ Rɴᴅ ——➤(🎀)",
    "Cʜᴏᴛɪ Jᴀᴀᴛ ——➤(🎀)",
    "TᴇRɪ Mᴀ Tᴇʀᴍɪ ——➤(🎀)",
    "Hɪᴊᴀʙ PᴇʜᴇN ——➤(🎀)",
    "Tᴍᴋᴄ Mᴀɪ Kᴏʏʟᴀ ——➤(🎀)",
]

NCEMO_EMOJIS = [
    "🌑",
    "🌒",
    "🌔",
    "🌕",
    "🌖",
    "🌗",
    "🌘",
    "🪐",
    "🌍",
    "🌎",
    "🌙",
    "☄️",
    "🌑",
    "🌒",
    "🌔",
    "🌕",
    "🌖",
    "🌗",
    "🌘",
    "🪐",
    "🌍",
    "🌎",
    "🌙",
    "☄️",
    "🫧",
]

EMOSPAM_PATTERNS = [
    "[ target ] TᴇRɪ MᴀKᴏ Kᴜᴛᴛᴀ Cʜᴏᴅᴇ 🌙 " * 20,
    "[ target ] Tᴇʀɪ Bᴇʜᴇɴ Kᴀ Bᴀʟᴀᴛᴋᴀʀ Bʏ x𝘒𝘦𝘯𝘵𝘰 🤍" * 30,
    "[ target ] Tᴇʀᴀ Bᴀᴀᴘ Hɪᴊᴅᴜ Gɴɢ MᴇMʙᴇʀ 🤡" * 30,
    "[ target ] Tᴇʀɪ NᴀNɪ Wʜᴏʀᴇ Oғ Tʜᴇ Wᴏʀʟᴅ 🪐" * 20,
]

SPAM_PATTERNS = ["[ text ] 🪐", "[ text ] 🌙", "[ text ] 🤡", "[ text ] 🤍"]

ARCADECHOD_TEXTS = [
    "〘💎〙{ target } ¡! Tᴍʀ〘💎〙",
    "〘🧡〙{ target } !¡ Tᴍʀ 〘🧡〙",
    "〘😊〙{ target } !¡ Tᴍʀ 〘😊〙",
    "〘🌙〙{ target } ¡! Tᴍʀ 〘🌙〙",
    "〘🎧〙{ target } !¡ Tᴍʀ 〘🎧〙",
    "〘🤣〙{ target } !¡ Tᴍʀ 〘🤣〙",
    "〘🖤〙{ target } !¡ Tᴍʀ 〘🖤〙",
    "〘🌹〙{ target } !¡ Tᴍʀ 〘🌹〙",
    "〘🌸〙{ target } !¡ Tᴍʀ 〘🌸〙",
    "〘🌹〙{ target } !¡ Tᴍʀ 〘🌹〙",
]

CHUDARA_TEXTS = [
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🎋",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🎊",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🎉",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🎎",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🎍",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🪅",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🎃",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🎄",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🪄",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🎐",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🎏",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🪆",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🥋",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🥊",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🧩",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🪢",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🧮",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🧭",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//🌿",
    "亗 {target} 亗 🩷गुलाबी चूत वाला__//💮",
]

emospam_tasks: Dict[int, asyncio.Task] = {}
arcadechod_tasks: Dict[int, Dict[str, asyncio.Task]] = {}
chudara_tasks: Dict[int, Dict[str, asyncio.Task]] = {}

# ---------------------------
# AUTO-SPEED CONFIG
# ---------------------------
NORMAL_DELAY      = 0.2    # default speed between title changes
BOOST_DELAY       = 0.05   # turbo speed when interference is detected
BOOST_DURATION    = 20     # number of successful title sets before returning to normal speed
CHECK_INTERVAL    = 5      # check actual chat title every N iterations to detect interference

# per-chat boost state  {chat_id: remaining_boost_iterations}
_boost_state: Dict[int, int] = {}
# per-chat last title we set  {chat_id: str}
_last_set_title: Dict[int, str] = {}

# ---------------------------
# GLOBAL STATE
# ---------------------------
if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r", encoding="utf-8") as f:
            _loaded = json.load(f)
            SUDO_USERS = set(int(x) for x in _loaded)
    except Exception:
        SUDO_USERS = {OWNER_ID}
else:
    SUDO_USERS = {OWNER_ID}
with open(SUDO_FILE, "w", encoding="utf-8") as f:
    json.dump(list(SUDO_USERS), f)


def save_sudo():
    with open(SUDO_FILE, "w", encoding="utf-8") as f:
        json.dump(list(SUDO_USERS), f)


group_tasks: Dict[int, Dict[str, asyncio.Task]] = {}
spam_tasks: Dict[int, asyncio.Task] = {}
slide_targets = set()
slidespam_targets = set()
swipe_mode = {}
apps, bots = [], []
delay = NORMAL_DELAY

logging.basicConfig(level=logging.WARNING)

# ---------------------------
# FONT STYLIZER  (TᴀʀGᴇᴛ format)
# ---------------------------
_SMALL_CAPS = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ',
    'f': 'ғ', 'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ',
    'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ',
    'p': 'ᴘ', 'q': 'q', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ',
    'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 'y': 'ʏ',
    'z': 'ᴢ',
}

def stylize_name(text: str) -> str:
    """Convert text to TᴀʀGᴇᴛ style: pos%3==0 → uppercase, else → small caps."""
    result = []
    pos = 0
    for char in text:
        if char.isalpha():
            if pos % 3 == 0:
                result.append(char.upper())
            else:
                result.append(_SMALL_CAPS.get(char.lower(), char.lower()))
            pos += 1
        else:
            result.append(char)
    return "".join(result)


# ---------------------------
# DECORATORS
# ---------------------------
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid not in SUDO_USERS:
            return await update.message.reply_text(
                "Pᴇʜʟᴇ AʀᴄᴀᴅᴇCʜᴏᴅ Kᴀ Mᴇᴍʙᴇʀ Bᴀɴ Fᴇʀ Usᴇ Kʀɴᴀ 🤍🦋."
            )
        return await func(update, context)

    return wrapper


def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid != OWNER_ID:
            return await update.message.reply_text(
                "Nᴏ Rɪɢʜᴛs Yᴏᴜ Nɪɢɢᴀ Cᴀɴ'ᴛ Cᴏɴᴛʀᴏʟ Mᴇ ❌."
            )
        return await func(update, context)

    return wrapper


# ---------------------------
# SAFE TITLE SETTER with flood-wait handling
# ---------------------------
async def safe_set_title(bot, chat_id: int, text: str) -> bool:
    """Try to set chat title. Returns True on success, False on failure."""
    try:
        await asyncio.wait_for(bot.set_chat_title(chat_id, text), timeout=8)
        return True
    except RetryAfter as e:
        wait = e.retry_after + random.uniform(0.5, 2.0)
        print(f"[FLOOD] chat {chat_id} retry after {wait:.1f}s")
        await asyncio.sleep(wait)
        return False
    except (TimedOut, NetworkError):
        await asyncio.sleep(1.5)
        return False
    except asyncio.CancelledError:
        raise
    except Exception as e:
        err = str(e).lower()
        if "flood" in err or "too many" in err:
            await asyncio.sleep(5)
        return False


# ---------------------------
# AUTO-SPEED: detect interference and boost
# ---------------------------
def _current_delay(chat_id: int) -> float:
    """Return effective delay for this chat (boosted or normal)."""
    if _boost_state.get(chat_id, 0) > 0:
        return BOOST_DELAY
    return delay


def _trigger_boost(chat_id: int):
    """Activate turbo mode for this chat."""
    _boost_state[chat_id] = BOOST_DURATION
    print(f"[BOOST] Interference detected in {chat_id} — switching to turbo speed!")


def _tick_boost(chat_id: int):
    """Decrement boost counter after each successful title set."""
    if _boost_state.get(chat_id, 0) > 0:
        _boost_state[chat_id] -= 1
        if _boost_state[chat_id] == 0:
            print(f"[BOOST] chat {chat_id} — returning to normal speed.")


# ---------------------------
# BOT LOOP used by gcnc/ncemo — with auto-speed
# ---------------------------
async def bot_loop(bot, chat_id: int, base: str, mode: str):
    i = 0
    check_counter = 0
    while True:
        try:
            if mode == "raid":
                text = f"{base} {RAID_TEXTS[i % len(RAID_TEXTS)]}"
            else:
                text = f"{base} {NCEMO_EMOJIS[i % len(NCEMO_EMOJIS)]}"

            # Every CHECK_INTERVAL iterations, read the actual title to detect outsiders
            check_counter += 1
            if check_counter >= CHECK_INTERVAL:
                check_counter = 0
                try:
                    chat_info = await asyncio.wait_for(
                        bot.get_chat(chat_id), timeout=6
                    )
                    actual_title = chat_info.title or ""
                    expected = _last_set_title.get(chat_id, "")
                    # If title was changed by someone else and we were in control, boost
                    if expected and actual_title != expected:
                        _trigger_boost(chat_id)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass

            success = await safe_set_title(bot, chat_id, text)
            if success:
                _last_set_title[chat_id] = text
                _tick_boost(chat_id)
                i += 1

            await asyncio.sleep(_current_delay(chat_id))

        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[WARN] Bot loop error in chat {chat_id}: {e}")
            await asyncio.sleep(0.5)


async def spam_loop(bot, chat_id, text):
    while True:
        try:
            spam_pattern = random.choice(SPAM_PATTERNS)
            spam_text = (
                spam_pattern.replace("[ text ]", text)
                .replace("[ Text ]", text)
                .replace("[ any text ]", text)
            )
            await bot.send_message(chat_id=chat_id, text=spam_text)
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            raise
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
        except Exception as e:
            print(f"[WARN] Spam error in chat {chat_id}: {e}")
            await asyncio.sleep(1)


# ---------------------------
# COMMANDS
# ---------------------------
@only_owner
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌙<3 AʀᴄᴀᴅᴇCʜᴏᴅ Gʀᴀᴍ Sᴄʀɪᴘᴛ Is Aᴄᴛɪᴠᴇ Nᴏᴡ !\nUsᴇ /help Tᴏ Sᴇᴇ Aʟʟ Cᴏᴍᴍᴀɴᴅs🌙<3."
    )


@only_owner
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "╔══════════════════════╗\n"
        "║  🌸 ᴀʀᴄᴀᴅᴇᴄʜᴏᴅ ᴍᴇɴᴜ 🌸  ║\n"
        "╚══════════════════════╝\n"
        "\n"
        "━━━━━ 🎀 ɴᴀᴍᴇ ᴄʜᴀɴɢᴇʀ 🎀 ━━━━━\n"
        "✦ /nc1 ‹ɴᴀᴍᴇ› — ᴇᴍᴏᴊɪ ʟᴏᴏᴘ\n"
        "✦ /nc2 ‹ɴᴀᴍᴇ› — ʀᴀɪᴅ ʟᴏᴏᴘ\n"
        "✦ /arcadechod ‹ɴᴀᴍᴇ› — 〘💎〙ʟᴏᴏᴘ\n"
        "✦ /chudara ‹ɴᴀᴍᴇ› — 亗 ʟᴏᴏᴘ\n"
        "✦ /stopnc2 — sᴛᴏᴘ ɴᴄ ʟᴏᴏᴘ\n"
        "✦ /stoparcadechod — sᴛᴏᴘ 💎 ʟᴏᴏᴘ\n"
        "✦ /stopchudara — sᴛᴏᴘ 亗 ʟᴏᴏᴘ\n"
        "\n"
        "━━━━━ 💬 sᴘᴀᴍ ᴛᴏᴏʟs 💬 ━━━━━\n"
        "✦ /spamloop ‹ᴛᴇxᴛ› — ᴛᴇxᴛ ʟᴏᴏᴘ\n"
        "✦ /stopspam — sᴛᴏᴘ ᴛᴇxᴛ ʟᴏᴏᴘ\n"
        "✦ /emospam ‹ᴛᴇxᴛ› — ᴇᴍᴏᴊɪ sᴘᴀᴍ\n"
        "✦ /stopemospam — sᴛᴏᴘ ᴇᴍᴏ sᴘᴀᴍ\n"
        "\n"
        "━━━━━ 🎯 sʟɪᴅᴇ ᴍᴏᴅᴇ 🎯 ━━━━━\n"
        "✦ /targetslide — sʟɪᴅᴇ ᴛᴀʀɢᴇᴛ\n"
        "✦ /stopslide — sᴛᴏᴘ sʟɪᴅᴇ\n"
        "✦ /slidespam — sᴘᴀᴍ sʟɪᴅᴇ\n"
        "✦ /stopslidespam — sᴛᴏᴘ sᴘᴀᴍ sʟɪᴅᴇ\n"
        "✦ /swipe ‹ɴᴀᴍᴇ› — sᴡɪᴘᴇ ᴍᴏᴅᴇ\n"
        "✦ /stopswipe — sᴛᴏᴘ sᴡɪᴘᴇ\n"
        "\n"
        "━━━━━ 👑 ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ 👑 ━━━━━\n"
        "✦ /addsudo — ➕ ᴀᴅᴅ sᴜᴅᴏ\n"
        "✦ /delsudo — ➖ ʀᴇᴍᴏᴠᴇ sᴜᴅᴏ\n"
        "✦ /listsudo — 📋 ʟɪsᴛ sᴜᴅᴏ\n"
        "\n"
        "━━━━━ ⚙️ sᴇᴛᴛɪɴɢs ⚙️ ━━━━━\n"
        "✦ /stopall — ⏹ sᴛᴏᴘ ᴇᴠᴇʀʏᴛʜɪɴɢ\n"
        "✦ /status — 📊 ᴄʜᴇᴄᴋ ᴀᴄᴛɪᴠᴇ\n"
        "✦ /delay ‹sᴇᴄ› — ⏱ sᴇᴛ sᴘᴇᴇᴅ\n"
        "✦ /myid — 🆔 ʏᴏᴜʀ ɪᴅ\n"
        "✦ /ping — 🏓 ᴛᴇsᴛ sᴘᴇᴇᴅ\n"
        "\n"
        "╔══════════════════════╗\n"
        "║ ⚡ ᴀᴜᴛᴏ-ᴛᴜʀʙᴏ: ᴀᴄᴛɪᴠᴇ 🔥 ║\n"
        "╚══════════════════════╝"
    )


@only_owner
async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_time = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end_time = time.time()
    latency = int((end_time - start_time) * 1000)
    await msg.edit_text(f"🏓 Pong! ✅ {latency} ms")


@only_owner
async def myid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆔 Your ID: {update.effective_user.id}")


# --- GC Loops ---
@only_owner
async def gcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /nc2 <text>")
    base = stylize_name(" ".join(context.args))
    chat_id = update.message.chat_id
    group_tasks.setdefault(chat_id, {})
    for bot in bots:
        key = getattr(bot, "token", str(id(bot)))
        if key not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "raid"))
            group_tasks[chat_id][key] = task
    await update.message.reply_text("🔄चुदाई suru hua.")


@only_owner
async def ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /nc1 <text>")
    base = stylize_name(" ".join(context.args))
    chat_id = update.message.chat_id
    group_tasks.setdefault(chat_id, {})
    for bot in bots:
        key = getattr(bot, "token", str(id(bot)))
        if key not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "emoji"))
            group_tasks[chat_id][key] = task
    await update.message.reply_text("🔄 Emoji loop started with all bots.")


@only_owner
async def stopgcnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in group_tasks:
        for task in group_tasks[chat_id].values():
            task.cancel()
        group_tasks[chat_id] = {}
        _boost_state.pop(chat_id, None)
        _last_set_title.pop(chat_id, None)
        await update.message.reply_text("⏹ Loop stopped in this GC.")
    else:
        await update.message.reply_text("⏹ No active loops in this GC.")


@only_owner
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    for chat_id in list(group_tasks.keys()):
        for task in group_tasks[chat_id].values():
            task.cancel()
    group_tasks.clear()

    for chat_id in list(arcadechod_tasks.keys()):
        for task in arcadechod_tasks[chat_id].values():
            task.cancel()
    arcadechod_tasks.clear()

    for chat_id in list(chudara_tasks.keys()):
        for task in chudara_tasks[chat_id].values():
            task.cancel()
    chudara_tasks.clear()

    for task in spam_tasks.values():
        task.cancel()
    spam_tasks.clear()

    for task in emospam_tasks.values():
        task.cancel()
    emospam_tasks.clear()

    _boost_state.clear()
    _last_set_title.clear()

    await update.message.reply_text("⏹ All loops stopped.")


@only_owner
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay
    if not context.args:
        return await update.message.reply_text(f"⏱ Current delay: {delay}s")
    try:
        delay = float(context.args[0])
        await update.message.reply_text(f"✅ Delay set to {delay}s")
    except Exception:
        await update.message.reply_text("⚠️ Invalid number.")


@only_owner
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = "📊 Active Loops:\n"
    for chat_id, tasks in group_tasks.items():
        boost = _boost_state.get(chat_id, 0)
        mode = f"⚡TURBO ({boost} left)" if boost > 0 else "🟢 Normal"
        msg += f"Chat {chat_id}: {len(tasks)} bots | Speed: {mode}\n"
    if not group_tasks:
        msg += "No active loops."
    await update.message.reply_text(msg)


# --- SUDO ---
@only_owner
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        SUDO_USERS.add(uid)
        save_sudo()
        await update.message.reply_text(f"✅ {uid} added as sudo.")
    else:
        await update.message.reply_text("⚠️ Reply to a user to add them as sudo.")


@only_owner
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        if uid in SUDO_USERS:
            SUDO_USERS.remove(uid)
            save_sudo()
            await update.message.reply_text(f"🗑 {uid} removed from sudo.")
        else:
            await update.message.reply_text("⚠️ User not in sudo list.")
    else:
        await update.message.reply_text("⚠️ Reply to a user to remove them from sudo.")


@only_owner
async def listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👑 SUDO USERS:\n" + "\n".join(map(str, SUDO_USERS))
    )


# --- Slide / Spam / Swipe ---
@only_owner
async def targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slide_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🎯 Target slide added.")
    else:
        await update.message.reply_text("⚠️ Reply to a user to target them.")


@only_owner
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        slide_targets.discard(uid)
        await update.message.reply_text("🛑 Target slide stopped.")
    else:
        await update.message.reply_text("⚠️ Reply to a user to stop targeting them.")


@only_owner
async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        slidespam_targets.add(update.message.reply_to_message.from_user.id)
        await update.message.reply_text("🎯 Slidespam target added.")
    else:
        await update.message.reply_text("⚠️ Reply to a user to target them.")


@only_owner
async def stopslidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        slidespam_targets.discard(uid)
        await update.message.reply_text("🛑 Slidespam stopped.")
    else:
        await update.message.reply_text("⚠️ Reply to a user to stop targeting them.")


@only_owner
async def swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /swipe <name>")
    name = " ".join(context.args)
    chat_id = update.message.chat_id
    swipe_mode[chat_id] = name
    await update.message.reply_text(f"✨ Swipe mode enabled for: {name}")


@only_owner
async def stopswipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in swipe_mode:
        del swipe_mode[chat_id]
        await update.message.reply_text("🛑 Swipe mode disabled.")
    else:
        await update.message.reply_text("⚠️ Swipe mode not active in this chat.")


@only_owner
async def spamloop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /spamloop <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    bot = context.bot
    if chat_id in spam_tasks:
        spam_tasks[chat_id].cancel()
    task = asyncio.create_task(spam_loop(bot, chat_id, text))
    spam_tasks[chat_id] = task
    await update.message.reply_text("🔄 Spam loop started.")


@only_owner
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        spam_tasks[chat_id].cancel()
        del spam_tasks[chat_id]
        await update.message.reply_text("🛑 Spam loop stopped.")
    else:
        await update.message.reply_text("⚠️ No spam loop active in this chat.")


async def arcadechod_loop(bot, chat_id: int, target: str):
    i = 0
    check_counter = 0
    while True:
        try:
            pattern = ARCADECHOD_TEXTS[i % len(ARCADECHOD_TEXTS)]
            text = pattern.replace("{ target }", target)

            check_counter += 1
            if check_counter >= CHECK_INTERVAL:
                check_counter = 0
                try:
                    chat_info = await asyncio.wait_for(bot.get_chat(chat_id), timeout=6)
                    actual_title = chat_info.title or ""
                    expected = _last_set_title.get(chat_id, "")
                    if expected and actual_title != expected:
                        _trigger_boost(chat_id)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass

            success = await safe_set_title(bot, chat_id, text)
            if success:
                _last_set_title[chat_id] = text
                _tick_boost(chat_id)
                i += 1

            await asyncio.sleep(_current_delay(chat_id))
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[WARN] ArcadeChod loop error in chat {chat_id}: {e}")
            await asyncio.sleep(0.5)


async def emospam_loop(bot, chat_id, text):
    while True:
        try:
            pattern = random.choice(EMOSPAM_PATTERNS)
            spam_text = pattern.replace("[ target ]", text)
            await bot.send_message(chat_id=chat_id, text=spam_text)
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            raise
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
        except Exception as e:
            print(f"[WARN] Emospam error in chat {chat_id}: {e}")
            await asyncio.sleep(1)


@only_owner
async def emospam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /emospam <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    bot = context.bot
    if chat_id in emospam_tasks:
        emospam_tasks[chat_id].cancel()
    task = asyncio.create_task(emospam_loop(bot, chat_id, text))
    emospam_tasks[chat_id] = task
    await update.message.reply_text("🔄 Emoji spam started.")


@only_owner
async def stopemospam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in emospam_tasks:
        emospam_tasks[chat_id].cancel()
        del emospam_tasks[chat_id]
        await update.message.reply_text("🛑 Emoji spam stopped.")
    else:
        await update.message.reply_text("⚠️ No emoji spam active in this chat.")


@only_owner
async def arcadechod_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /arcadechod <target name>")
    target = stylize_name(" ".join(context.args))
    chat_id = update.message.chat_id
    arcadechod_tasks.setdefault(chat_id, {})
    for bot in bots:
        key = getattr(bot, "token", str(id(bot)))
        if key not in arcadechod_tasks[chat_id]:
            task = asyncio.create_task(arcadechod_loop(bot, chat_id, target))
            arcadechod_tasks[chat_id][key] = task
    await update.message.reply_text(f"🎯 ArcadeChod loop started for: {target}")


@only_owner
async def stoparcadechod_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in arcadechod_tasks:
        for task in arcadechod_tasks[chat_id].values():
            task.cancel()
        del arcadechod_tasks[chat_id]
        _boost_state.pop(chat_id, None)
        _last_set_title.pop(chat_id, None)
        await update.message.reply_text("⏹ ArcadeChod loop stopped.")
    else:
        await update.message.reply_text("⚠️ No ArcadeChod loop active in this chat.")


async def chudara_loop(bot, chat_id: int, target: str):
    i = 0
    check_counter = 0
    while True:
        try:
            pattern = CHUDARA_TEXTS[i % len(CHUDARA_TEXTS)]
            text = pattern.replace("{target}", target)

            check_counter += 1
            if check_counter >= CHECK_INTERVAL:
                check_counter = 0
                try:
                    chat_info = await asyncio.wait_for(bot.get_chat(chat_id), timeout=6)
                    actual_title = chat_info.title or ""
                    expected = _last_set_title.get(chat_id, "")
                    if expected and actual_title != expected:
                        _trigger_boost(chat_id)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    pass

            success = await safe_set_title(bot, chat_id, text)
            if success:
                _last_set_title[chat_id] = text
                _tick_boost(chat_id)
                i += 1

            await asyncio.sleep(_current_delay(chat_id))
        except asyncio.CancelledError:
            raise
        except Exception as e:
            print(f"[WARN] Chudara loop error in chat {chat_id}: {e}")
            await asyncio.sleep(0.5)


@only_owner
async def chudara_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /chudara <target name>")
    target = stylize_name(" ".join(context.args))
    chat_id = update.message.chat_id
    chudara_tasks.setdefault(chat_id, {})
    for bot in bots:
        key = getattr(bot, "token", str(id(bot)))
        if key not in chudara_tasks[chat_id]:
            task = asyncio.create_task(chudara_loop(bot, chat_id, target))
            chudara_tasks[chat_id][key] = task
    await update.message.reply_text(f"🎋 Chudara loop started for: {target}")


@only_owner
async def stopchudara_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in chudara_tasks:
        for task in chudara_tasks[chat_id].values():
            task.cancel()
        del chudara_tasks[chat_id]
        _boost_state.pop(chat_id, None)
        _last_set_title.pop(chat_id, None)
        await update.message.reply_text("⏹ Chudara loop stopped.")
    else:
        await update.message.reply_text("⚠️ No Chudara loop active in this chat.")


# ---------------------------
# MAIN
# ---------------------------
async def main():
    global apps, bots

    seen_tokens = set()
    for token in TOKENS:
        if token in seen_tokens:
            print(f"[SKIP] Duplicate token skipped: {token[:20]}...")
            continue
        seen_tokens.add(token)
        try:
            app = Application.builder().token(token).build()

            app.add_handler(CommandHandler("start", start_cmd))
            app.add_handler(CommandHandler("help", help_cmd))
            app.add_handler(CommandHandler("ping", ping_cmd))
            app.add_handler(CommandHandler("myid", myid))
            app.add_handler(CommandHandler("nc2", gcnc))
            app.add_handler(CommandHandler("nc1", ncemo))
            app.add_handler(CommandHandler("stopnc2", stopgcnc))
            app.add_handler(CommandHandler("stopall", stopall))
            app.add_handler(CommandHandler("delay", delay_cmd))
            app.add_handler(CommandHandler("status", status_cmd))
            app.add_handler(CommandHandler("addsudo", addsudo))
            app.add_handler(CommandHandler("delsudo", delsudo))
            app.add_handler(CommandHandler("listsudo", listsudo))
            app.add_handler(CommandHandler("targetslide", targetslide))
            app.add_handler(CommandHandler("stopslide", stopslide))
            app.add_handler(CommandHandler("slidespam", slidespam))
            app.add_handler(CommandHandler("stopslidespam", stopslidespam))
            app.add_handler(CommandHandler("swipe", swipe))
            app.add_handler(CommandHandler("stopswipe", stopswipe))
            app.add_handler(CommandHandler("spamloop", spamloop))
            app.add_handler(CommandHandler("stopspam", stopspam))
            app.add_handler(CommandHandler("emospam", emospam))
            app.add_handler(CommandHandler("stopemospam", stopemospam))
            app.add_handler(CommandHandler("arcadechod", arcadechod_cmd))
            app.add_handler(CommandHandler("stoparcadechod", stoparcadechod_cmd))
            app.add_handler(CommandHandler("chudara", chudara_cmd))
            app.add_handler(CommandHandler("stopchudara", stopchudara_cmd))

            apps.append(app)
            bots.append(app.bot)
            print(f"[OK] Bot added: {token[:20]}...")
        except Exception as e:
            print(f"[ERR] Failed to add bot {token[:20]}...: {e}")

    if not apps:
        print("[FATAL] No bots loaded. Exiting.")
        return

    print(f"[INFO] Starting {len(apps)} bot(s)...")

    await asyncio.gather(*[app.initialize() for app in apps])
    await asyncio.gather(*[app.start() for app in apps])
    await asyncio.gather(
        *[app.updater.start_polling(drop_pending_updates=True) for app in apps]
    )

    print("[INFO] All bots are running. Press Ctrl+C to stop.")
    print(f"[INFO] Normal delay: {NORMAL_DELAY}s | Boost delay: {BOOST_DELAY}s | Auto-speed: ENABLED")

    try:
        await asyncio.Event().wait()
    except asyncio.CancelledError:
        pass
    finally:
        print("[INFO] Shutting down...")
        for app in apps:
            try:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            except Exception as e:
                print(f"[WARN] Shutdown error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
