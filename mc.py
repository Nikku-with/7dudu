# Takashi_x_Rexxy.py
import asyncio
import json
import os
import random
import time
import logging
import sys
import io
import getpass
from typing import Dict, List
from datetime import datetime, timezone, timedelta
from telegram import Update
from telegram.ext import Application, PrefixHandler, ContextTypes
from telegram import error as telegram_error

# ============================================
# WINDOWS ASYNCIO FIX (Required for Windows RDP)
# ============================================
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# ---------------------------
# CONFIGURATION
# ---------------------------
TOKENS = [ "8999855202:AAH1okN9maoaMcH3yCTQ3BSrW0nuixb6xa4",
"8883957565:AAEfHNU7pmDFUqCqWCX6zfcP7F9mEwBHpPU",
"8455647760:AAG7n9_wG4kJ_ltWrslqmp1K90yU9S3XaMg",
"8976722801:AAG2Y_Qjbpb7c1pi5Hpt7e8sBq36HllSZuI",
"8933972948:AAEbGygsWVLyAzPbOxs2HOiH26kMkIxW7Wo",
]

OWNER_ID = 8955102809
SUDO_FILE = "sudo_json"
PASSWORD = "Takashi69"
start_time = time.time()
GLOBAL_DELAY = 0.05
shutdown_event = asyncio.Event()

# ---------------------------
# IMAGE URLs (Direct from Catbox.moe)
# ---------------------------
HELP_IMAGE_URL = "https://files.catbox.moe/zoqo2s.mp4"
STATUS_IMAGE_URL = "https://files.catbox.moe/zoqo2s.mp4"
OVER_IMAGE_URL = "https://files.catbox.moe/zoqo2s.mp4"

# ---------------------------
# GLOBAL STATE
# ---------------------------
apps = []
bots = []

# Task dictionaries
nc1_tasks: Dict[int, List[asyncio.Task]] = {}
nc2_tasks: Dict[int, List[asyncio.Task]] = {}
sf_nc_tasks: Dict[int, List[asyncio.Task]] = {}
spam1_tasks: Dict[int, List[asyncio.Task]] = {}
spam2_tasks: Dict[int, List[asyncio.Task]] = {}
spam3_tasks: Dict[int, List[asyncio.Task]] = {}
slide1_tasks: Dict[int, List[asyncio.Task]] = {}
slide2_tasks: Dict[int, List[asyncio.Task]] = {}
slide3_tasks: Dict[int, List[asyncio.Task]] = {}
photo_tasks: Dict[int, List[asyncio.Task]] = {}
chat_photos: Dict[int, List[str]] = {}

# Legacy state
nc_tasks: Dict[int, List[asyncio.Task]] = {}
nc_counters: Dict[int, int] = {}
nc_modes: Dict[int, str] = {}
group_tasks: Dict[int, Dict] = {}

# ---------------------------
# EMOJI LISTS & PATTERNS
# ---------------------------
HEART_EMOJIS = ["❤️","🧡","💛","💚","🩵","💙","💜","🤎","🖤","🩶","🤍","🩷","💘","💝","💖","💗","💓","💞","💕","💌","💟","♥️","❣️","❤️‍🩹","💔","❤️‍🔥"]
WEATHER_SPACE_EMOJIS = ["💠","🌊","🌬️","❄️","🌀","🌪️","⚡","☔","🌈","","🌒","🌓","🌔","🌕","🌖","🌗","🌘","✨","🌞","🌝","🌚","🌜","🌛","","⭐","🌟","✨","🪐"]
NATURE_FLAGS_EMOJIS = ["🌿","🌱","🍃","☘️","🌹","🥀","🌺","🌷","🪷","🌸","💮","🏵️","🪻","🌻","🌼","🍂","🍁","🫧","🪼","🕸️","🪽","🎏","🎐","🏁","🚩","🎌","🏴","🏳️","🏳️‍🌈","🏳️‍⚧️","🏴‍☠️","🇦🇨","🇦🇩","🇦🇪","🇦🇫","🇦🇬","🇦🇮","🇦🇱","🇦🇲","🇦🇴","🇦🇶","🇦🇷","🇦🇸","🇦🇹","🇦🇺","🇦🇼","🇦🇽","🇦🇿","🇧🇦","🇧🇧","🇧🇩","🇧🇪","🇧🇫","🇧🇬","🇧🇭","🇧🇮","🇧🇯","🇧🇱","🇧🇲","🇧🇳","🇧🇴","🇧🇶","🇧🇷","🇧🇸","🇧🇹","🇧🇻","🇧🇼","🇧🇾","🇧🇿","🇨🇦","🇨🇨","🇨🇩","🇨🇫","🇨🇬","🇨🇭","🇨🇮","🇨🇰","🇨🇱","🇨🇲","🇨🇳","🇨🇴","🇨🇵","🇨🇶","🇨🇷","🇨🇺","🇨🇻","🇨🇼","🇩🇰","🇨🇽","🇨🇾","🇨🇿","🇩🇬","🇩🇲","🇬🇧","🇬🇩","🇬🇫","🇬🇬","🇬🇭","🇭🇲","🇬🇺","🇮🇨","🇮🇲","🇮🇪","🇰🇪","🇰🇲","🇱🇧","🇰🇿","🇰🇬","🇰🇾","🇱🇷","🇲🇩","🇲🇶","🇱🇾","🇱🇰","🇰🇷","🇯🇵","🇿🇲","🇻🇮","🇺🇸","🇹🇻","🇹🇲","🇺🇲","🇻🇪"]

NC1_WORDS = [
    "𝙏𝙈𝙆𝘾 𝙈𝙄𝙀 𝙆𝙐𝙏𝙏𝙀 𝙆𝘼 𝙇𝙉𝘿",
    "𝙊𝙔𝙀 𝙏𝙐 𝙈𝘼𝙍𝘼 𝙆𝘼𝙄𝙎𝙀 𝙂𝘼𝙍𝙀𝙀𝘽 𝘾𝙑𝙍 𝙆𝙍",
    "𝙊𝙔𝙀 𝙏𝙀𝙍𝙄 𝙈𝘼𝙐𝙎𝙄 𝙆𝙄 𝘾𝙃𝙐𝙏 𝙈𝘼𝘼𝙍 𝘿𝙐 𝙍𝙊𝙔𝙀𝙂𝘼 𝙏𝙊 𝙉𝘼‌𝙄 ?",
    "𝙏𝙈𝙆𝘾 𝙍𝙉𝘿𝙔 𝙆𝙀 𝙂𝙐𝙇𝘼𝙈𝙄 𝙆𝙍 𝘾𝙃𝙐𝙋 𝘾𝙃𝘼𝙋",
    "𝙊𝙔𝙀 𝘽𝙎𝘿𝙆 𝙃𝘼𝙒𝘼𝘽𝘼𝘼𝙕 𝙏𝘼𝙏𝙏𝙀 𝘽𝙃𝘼𝙂 𝙈𝙏",
    "𝙏𝙈𝙆𝙁𝘽", "𝙍𝙉𝘿𝙔", "𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝙈𝘼𝙍 𝙂𝙔𝙄", "𝙏𝘽𝙆𝘾",
    "𝙏𝙈𝙆𝘾 𝙈𝙄𝙀 𝙈𝘼𝙂𝙂𝙄𝙀", "𝙏𝘽𝙆𝘽 𝙈𝙄𝙀 𝙇𝙉𝘿", "𝙏𝙀𝙍𝙄 𝙂𝙉𝘿 𝙈𝙄𝙀 𝙆𝙐𝙏𝙏𝘼",
    "𝙂𝙐𝙇𝘼‌𝙈𝙄 𝙆𝙍", "𝙆𝙀𝙀𝘿𝙀", "𝘼𝙐𝙆𝘼𝘼𝙏 𝘽𝙉𝘼", "𝙂𝘼𝙍𝙀𝙀𝘽", "𝘽𝙎𝘿𝙆",
    "𝘾𝙃𝙈𝙍",
    "𝐓ᴍᴋʙ 𝐑ɴᴅʏ ᴋᴇ 𝐋ᴀᴅᴋᴇ 😈🖕🏻😈🖕🏻😈",
    "𝐓ᴇʀɪ ᴍᴀᴀ ᴍᴀʀ ɢʏɪ ¿😆😆😆",
    "𝐀ᴀʀ ꜱᴀᴍᴀɴᴅᴀʀ ᴘᴀᴀʀ ꜱᴀᴍᴀɴᴅᴀʀ ʙᴇᴇᴄʜ ᴍɪᴇ ʜᴀɪ ɴᴀɪʏᴀ ᴘʜʟᴇ ᴛᴇʀɪ ʙʜᴇɴ चोदू ʙᴀᴀᴅ ᴍɪᴇ चोदू ᴍᴀɪʏᴀ ¡! 🥰🖕🏻🥰🖕🏻🥰🖕🏻",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ʜᴜᴍᴇꜱʜᴀ ᴍᴜᴊʜꜱᴇ ʜɪ ᴋʏᴜ चुडती है ¡! 😡🤬😡🤬😡",
    "𝐃ᴇᴋʜ ᴀᴀᴊ ᴛᴇʀɪ 𝐌ᴀᴀ ᴋᴀ ɴᴀɴɢᴀ ᴅᴀɴᴄᴇ ᴅɪᴋʜᴀᴜ ! 🩰🧑🏻‍🩰",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ɪ 𝐆ᴜʟᴀʙɪ 𝐂ʜᴜᴛ ᴍɪᴇ 𝐌ᴜᴛ ᴋʀ ʙʜᴀɢ ᴊᴀᴜɢᴀ 𝐁ꜱᴅᴋ ! 😆",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴄʜᴏᴅɴᴇ ᴀʀʜᴀ ʜᴜ ʀᴜᴋ ᴡʜɪ ɢᴜʟᴀᴍ ! 😾",
    "𝐓ᴇʀɪ ʙʜᴇɴ ᴋᴇ ʙᴏᴏʙɪᴇꜱ ᴋᴇ ʙᴇᴇᴄʜ ᴍɪᴇ ʟɴᴅ ꜰᴀꜱᴀ ᴋʀ ᴍᴜᴛʜ ᴍᴀᴀʀ ᴅᴜɢᴀ ʙꜱᴅᴋ 😆",
    "𝐓ᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍɪᴇ ᴍᴀɢɢɪᴇ ʙɴᴀ ᴋʀ ᴍᴜᴛʜ ʙʜᴀʀ ᴅᴜɢᴀ ! 😆",
    "𝐓ᴇʀɪ ᴍᴀᴀ ʙʜᴛ ʀᴏᴛɪ ᴇʏ ʙɪʟᴋᴜʟ 𝐓ᴇʀɪ ᴛʀʜ ᴅᴏɴᴏ ʀɴᴅʏ ʀᴏɴᴀ ᴋʀᴛᴇ ʜᴏ ᴇᴡᴡ ! 😆",
    "𝐓ᴇʀɪ ʙʜᴇɴ ᴋɪ ɢᴜʟᴀʙɪ ᴄʜᴛ ᴋᴀᴀᴛ ᴅᴜɢᴀ ɢᴜʟᴀᴍ ! 😆",
    "𝐂ʜʟ ɢᴜʟᴀᴍ ɢᴜʟᴀᴍɪ ᴋʀ ! 😾"
]

# Original Patterns
NC1_PATTERN = "{text} {word} . ݁₊ ⊹ . ݁  <{emoji}> . ݁₊ ⊹ . ݁"
NC2_PATTERN = "{text} 𓂃˖˳·˖ ִֶָ ⋆{emoji}⋆ ִֶָ˖·˳˖𓂃 ִֶָ"
SFNC_PATTERN = "˚⊱{emoji}⊰˚ {text} ˚⊱{emoji}⊰˚"

# Spam patterns
SPAM1_LINE_PATTERN = "⁺‧₊˚ ཐི {text} ཋྀ ˚₊‧⁺ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴏᴅ 𝐊ᴇ 𝐅ᴇᴋ 𝐃ᴜɴɢᴀ<{emoji}>"
SPAM2_LINE_PATTERN = "𓆩{text}𓆪 𝐈 #𝐌ᴀᴀ 𝐂ʜᴜᴅᴀ 𝐑ɴʏᴅᴄᴇ  ⃟🌷꙰⃟𓆩"

def generate_spam1_message(text: str, emoji: str) -> str:
    lines = []
    for _ in range(10):
        lines.append(SPAM1_LINE_PATTERN.format(text=text, emoji=emoji))
        lines.append("")
    return "\n".join(lines)

def generate_spam2_message(text: str) -> str:
    lines = []
    for _ in range(10):
        lines.append(SPAM2_LINE_PATTERN.format(text=text))
        lines.append("")
    return "\n".join(lines)

# Slide messages
SLIDE1_MESSAGES = [
    "𝐂ʜʟ ʜᴀᴛ ɢᴀᴡᴀʀ ᴋɪ ᴀᴜʟᴀᴀᴅ ᴊɪᴛɴᴀ ᴛᴜ ʙᴏʟᴇɢᴀ ᴜᴛɴɪ ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅᴇɢɪ ! 😆😆😆😆😆😆😆",
    "𝐓ᴇʀɪ ᴍᴀᴀ ꜱᴇ ᴘᴜᴄʜɴᴀ ᴛᴇʀᴀ ʀᴇᴀʟ ʙᴀᴀᴘ ᴋᴏɴ ʜᴀɪ ᴡᴏ ᴍᴇʀᴀ ɴᴀᴀᴍ ʟᴇɢɪ ¡ 😍😍😍😍😍😍😍",
    "𝐓ᴇʀɪ ᴍᴀᴀ ᴋᴀ ᴋʜᴀꜱᴀᴍ ᴋʜᴀᴀꜱ ʜᴜ 🥹🥹🥹🥹🥹🥹🥹🥹🥹",
    "𝐂ʜʟ ʜᴀᴛ ʟᴡᴅᴇ ɢᴀʀᴇᴇʙ ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅ ᴋʀ ᴅᴀꜰᴀɴ ᴇʏ ¡ 😉😉😉😉😉😉😉😉😉😉😉",
    "𝐂ʜᴜᴘ ʀɴᴅʏᴋᴇ ʟᴀᴅᴋᴇ ᴍꜱɢ ᴍᴛ ᴋʀ ᴡʀɴᴀ ᴛᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴇxᴛʀᴀ ᴄᴏᴅ ᴅᴜɢᴀ ¡ 🤥🤥🤥🤥🤥🤥🤥🤥🤥🤥🤥🤥🤥🤥🤥",
    "𝐓ᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍɪᴇ ᴜɴɢʟɪ ᴋʀ ʀʜᴀ 𝐔ᴄʜᴀᴋ ᴍᴛ ʟᴡᴅᴇ 🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻🖕🏻",
    "𝐀ᴀᴊ ᴛᴇʀɪ ᴍᴀᴀ ʙʜᴇɴ ᴍᴀᴜꜱɪ ꜱᴀꜱᴜ ᴍᴀᴀ ʙᴜᴀᴀ ꜰᴜꜰᴀ ꜱʙ ᴄʜᴜᴅᴇɢᴇ 😆😆😆😆😆😆😆😆😆😆",
    "𝐓ᴇʀɪ ᴍᴀᴀ ᴋᴏ ᴄʜᴏᴅ ᴋʀ ᴍᴀɪɴ ʀᴏᴀᴅ ᴘʀ ꜰᴇᴋ ᴅᴜɢᴀ ʟᴇɴᴇ ᴀᴊᴀɴᴀ ꜱʜᴀʀᴘ 7:00ᴘ.ᴍ. 😆😆😆😆🖕🏻🖕🏻🖕🏻😆😆🖕🏻🖕🏻🖕🏻🖕🏻😆😆🖕🏻🖕🏻😆😆"
]
SLIDE2_MESSAGES = [
    "𝐂ʜᴜᴘ ᴍɪᴇ ᴋᴜᴄʜ ɴᴀɪ ꜱᴜɴᴜɢᴀ ᴛᴇʀɪ ᴍᴀᴀ ᴍᴇʀɪ ʀᴀᴋʜᴇʟ ʙᴀᴀᴛ ᴋʜᴛᴍ ¡ 😆🖕🏻😆🖕🏻😆🖕🏻😆😆😆😆😆🖕🏻🖕🏻🖕🏻😆😆🖕🏻😆",
    "𝐂ʜᴜᴘ ᴍɪᴇ ᴋᴜᴄʜ ɴᴀɪ ꜱᴜɴᴜɢᴀ ᴀʙ ᴛᴇʀɪ ʙʜᴇɴ ᴋᴏ ᴄʜᴜᴅɴᴇ ʙʜᴇᴊ ꜰꜱᴛ ꜰꜱᴛ ! 😘😘😘😘😘😘😘😘😘",
    "𝐖ᴏ ᴅᴇᴋʜ ᴜᴘᴀʀ ᴀꜱᴍᴀɴ ᴍɪᴇ ᴅᴇᴋʜ !! 𝐊ʏ ᴅᴇᴋʜ ʀʜᴀ ᴇʏ ʙꜱᴅ ᴛᴇʀɪ ᴍᴀᴀ ᴄʜᴜᴅ ʀʜɪ ʜᴀɪ ᴜᴘᴀʀ ᴀꜱᴍᴀɴ ᴍɪᴇ ! 🤣🤣🤣🤣🤣🤣🤣🤣",
    "𝐋ᴇ ʏᴇ ᴅᴀɴᴅᴀ ᴘᴀᴋᴀᴅ ᴀᴜʀ ᴀᴘɴɪ ɢɴᴅ ᴍɪᴇ ᴅᴀᴀʟ ᴋʀ ᴍᴜʜ ꜱᴇ ɴɪᴋᴀʟ ᴋʀ ᴅɪᴋʜᴀ ! 😒😒😒😒😒😒😒"
]
SLIDE3_PATTERN = "{text} ִֶָ𓂃 ࣪ ִֶָ🦢་༘࿐"

# ---------------------------
# SUDO MANAGEMENT
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

def save_sudo():
    with open(SUDO_FILE, "w", encoding="utf-8") as f:
        json.dump(list(SUDO_USERS), f)

UNAUTHORIZED_MSG = "𝐆ᴀʀᴇᴇʙ 🕷️ ɢᴀᴡᴅ ᥊ 𝐇ᴇʟʟғɪ᥅ꫀ 🕷️ ꜱᴇ 𝐁ʜɪᴋʜ 𝐌ᴀɴɢ 😾🥀"

def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid != OWNER_ID and uid not in SUDO_USERS:
            await update.message.reply_text(UNAUTHORIZED_MSG)
            return
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return
        uid = update.effective_user.id
        if uid != OWNER_ID:
            await update.message.reply_text(UNAUTHORIZED_MSG)
            return
        return await func(update, context)
    return wrapper

# ============================================
# NC WORKERS
# ============================================
async def nc1_worker(bot, chat_id, base_text, counter_dict):
    heart_len = len(HEART_EMOJIS)
    word_len = len(NC1_WORDS)
    while True:
        try:
            emoji = HEART_EMOJIS[random.randint(0, heart_len - 1)]
            word = NC1_WORDS[random.randint(0, word_len - 1)]
            text = NC1_PATTERN.format(text=base_text, word=word, emoji=emoji)
            await bot.set_chat_title(chat_id, text)
            counter_dict[chat_id] = counter_dict.get(chat_id, 0) + 1
        except asyncio.CancelledError:
            break
        except telegram_error.Forbidden:
            break
        except:
            pass

async def nc2_worker(bot, chat_id, base_text, counter_dict):
    emoji_len = len(WEATHER_SPACE_EMOJIS)
    while True:
        try:
            emoji = WEATHER_SPACE_EMOJIS[random.randint(0, emoji_len - 1)]
            text = NC2_PATTERN.format(text=base_text, emoji=emoji)
            await bot.set_chat_title(chat_id, text)
            counter_dict[chat_id] = counter_dict.get(chat_id, 0) + 1
        except asyncio.CancelledError:
            break
        except telegram_error.Forbidden:
            break
        except:
            pass

async def nc3_worker(bot, chat_id, base_text, counter_dict):
    emoji_len = len(NATURE_FLAGS_EMOJIS)
    while True:
        try:
            emoji = NATURE_FLAGS_EMOJIS[random.randint(0, emoji_len - 1)]
            text = SFNC_PATTERN.format(text=base_text, emoji=emoji)
            await bot.set_chat_title(chat_id, text)
            counter_dict[chat_id] = counter_dict.get(chat_id, 0) + 1
        except asyncio.CancelledError:
            break
        except telegram_error.Forbidden:
            break
        except:
            pass

async def stagger_worker1(bot, chat_id, base, counter, idx):
    await asyncio.sleep(idx * 0.1)
    await nc1_worker(bot, chat_id, base, counter)

async def stagger_worker2(bot, chat_id, base, counter, idx):
    await asyncio.sleep(idx * 0.1)
    await nc2_worker(bot, chat_id, base, counter)

async def stagger_worker3(bot, chat_id, base, counter, idx):
    await asyncio.sleep(idx * 0.1)
    await nc3_worker(bot, chat_id, base, counter)

# ============================================
# NC COMMAND HANDLERS
# ============================================
@only_sudo
async def nc1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: ~nc1 <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc1_tasks:
        for task in nc1_tasks[chat_id]:
            task.cancel()
        del nc1_tasks[chat_id]
    tasks = [asyncio.create_task(stagger_worker1(bot, chat_id, base, nc_counters, idx)) for idx, bot in enumerate(bots)]
    nc1_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ NC1 started with {len(bots)} bots")

@only_sudo
async def nc2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: ~nc2 <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc2_tasks:
        for task in nc2_tasks[chat_id]:
            task.cancel()
        del nc2_tasks[chat_id]
    tasks = [asyncio.create_task(stagger_worker2(bot, chat_id, base, nc_counters, idx)) for idx, bot in enumerate(bots)]
    nc2_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ NC2 started with {len(bots)} bots")

@only_sudo
async def nc3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: ~nc3 <text>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in sf_nc_tasks:
        for task in sf_nc_tasks[chat_id]:
            task.cancel()
        del sf_nc_tasks[chat_id]
    tasks = [asyncio.create_task(stagger_worker3(bot, chat_id, base, nc_counters, idx)) for idx, bot in enumerate(bots)]
    sf_nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ NC3 started with {len(bots)} bots")

# ============================================
# SPAM WORKERS & HANDLERS
# ============================================
async def spam1_loop(bot, chat_id, text):
    idx = 0
    emoji_len = len(HEART_EMOJIS)
    while True:
        try:
            emoji = HEART_EMOJIS[idx % emoji_len]
            message = generate_spam1_message(text, emoji)
            await bot.send_message(chat_id, message)
            idx += 1
        except asyncio.CancelledError:
            break
        except telegram_error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            pass

@only_sudo
async def spam1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: ~spam1 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam1_tasks:
        for task in spam1_tasks[chat_id]:
            task.cancel()
        del spam1_tasks[chat_id]
    tasks = [asyncio.create_task(spam1_loop(bot, chat_id, text)) for bot in bots]
    spam1_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Spam1 started with {len(bots)} bots")

async def spam2_loop(bot, chat_id, text):
    message = generate_spam2_message(text)
    while True:
        try:
            await bot.send_message(chat_id, message)
        except asyncio.CancelledError:
            break
        except telegram_error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            pass

@only_sudo
async def spam2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: ~spam2 <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam2_tasks:
        for task in spam2_tasks[chat_id]:
            task.cancel()
        del spam2_tasks[chat_id]
    tasks = [asyncio.create_task(spam2_loop(bot, chat_id, text)) for bot in bots]
    spam2_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Spam2 started with {len(bots)} bots")

async def spam3_loop(bot, chat_id, text):
    while True:
        try:
            await bot.send_message(chat_id, text)
        except asyncio.CancelledError:
            break
        except telegram_error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            pass

@only_sudo
async def spam3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    msg_text = None
    if context.args:
        msg_text = " ".join(context.args)
    elif update.message.reply_to_message:
        msg_text = update.message.reply_to_message.text
        if not msg_text:
            return await update.message.reply_text("❌ Replied message has no text!")
    else:
        return await update.message.reply_text("❌ Usage: ~spam3 <text> OR reply to a message")
    if chat_id in spam3_tasks:
        for task in spam3_tasks[chat_id]:
            task.cancel()
        del spam3_tasks[chat_id]
    tasks = [asyncio.create_task(spam3_loop(bot, chat_id, msg_text)) for bot in bots]
    spam3_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Spam3 started with {len(bots)} bots")

# ============================================
# SLIDE WORKERS & HANDLERS
# ============================================
async def slide1_loop(bot, chat_id, target_msg_id):
    i = 0
    total = len(SLIDE1_MESSAGES)
    while True:
        try:
            msg = SLIDE1_MESSAGES[i % total]
            await bot.send_message(chat_id, msg, reply_to_message_id=target_msg_id)
            i += 1
        except asyncio.CancelledError:
            break
        except telegram_error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            pass

@only_sudo
async def slide1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a message to start slide1!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slide1_tasks:
        for task in slide1_tasks[chat_id]:
            task.cancel()
        del slide1_tasks[chat_id]
    tasks = [asyncio.create_task(slide1_loop(bot, chat_id, target_msg_id)) for bot in bots]
    slide1_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Slide1 started, targeting {update.message.reply_to_message.from_user.first_name}")

async def slide2_loop(bot, chat_id, target_msg_id):
    i = 0
    total = len(SLIDE2_MESSAGES)
    while True:
        try:
            msg = SLIDE2_MESSAGES[i % total]
            await bot.send_message(chat_id, msg, reply_to_message_id=target_msg_id)
            i += 1
        except asyncio.CancelledError:
            break
        except telegram_error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            pass

@only_sudo
async def slide2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a message to start slide2!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slide2_tasks:
        for task in slide2_tasks[chat_id]:
            task.cancel()
        del slide2_tasks[chat_id]
    tasks = [asyncio.create_task(slide2_loop(bot, chat_id, target_msg_id)) for bot in bots]
    slide2_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Slide2 started, targeting {update.message.reply_to_message.from_user.first_name}")

async def slide3_loop(bot, chat_id, target_msg_id, text):
    message = SLIDE3_PATTERN.format(text=text)
    while True:
        try:
            await bot.send_message(chat_id, message, reply_to_message_id=target_msg_id)
        except asyncio.CancelledError:
            break
        except telegram_error.RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            pass

@only_sudo
async def slide3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: ~slide3 <text> (reply to a message)")
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start slide3!")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slide3_tasks:
        for task in slide3_tasks[chat_id]:
            task.cancel()
        del slide3_tasks[chat_id]
    tasks = [asyncio.create_task(slide3_loop(bot, chat_id, target_msg_id, text)) for bot in bots]
    slide3_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ Slide3 started, targeting {update.message.reply_to_message.from_user.first_name}\n📝 Text: {text}")

# ============================================
# PHOTO LOOP & COMMANDS (FIXED)
# ============================================

async def photo_loop(bot, chat_id):
    while True:
        try:
            if chat_id not in chat_photos or not chat_photos[chat_id]:
                await asyncio.sleep(5.0)
                continue
            photos_list = chat_photos[chat_id]
            file_id = random.choice(photos_list)
            photo_file = await bot.get_file(file_id)
            buf = io.BytesIO()
            await photo_file.download_to_memory(buf)
            buf.seek(0)
            await bot.set_chat_photo(chat_id=chat_id, photo=buf)
            await asyncio.sleep(0.5)
        except telegram_error.RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logging.error(f"Photo change error: {e}")
            await asyncio.sleep(5.0)

@only_sudo
async def savephoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ Reply to a photo to save it!")
    chat_id = update.message.chat_id
    file_id = update.message.reply_to_message.photo[-1].file_id
    chat_photos.setdefault(chat_id, []).append(file_id)
    await update.message.reply_text(f"✅ Photo saved! Total: {len(chat_photos[chat_id])}")

@only_sudo
async def startphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in chat_photos or len(chat_photos[chat_id]) < 1:
        return await update.message.reply_text("⚠️ Save at least 1 photo first using ~savephoto")
    if chat_id in photo_tasks:
        for task in photo_tasks[chat_id]:
            task.cancel()
        del photo_tasks[chat_id]
    tasks = [asyncio.create_task(photo_loop(bot, chat_id)) for bot in bots]
    photo_tasks[chat_id] = tasks
    await update.message.reply_text(f"🔄 Photo loop started for {len(bots)} bots")

@only_sudo
async def stopphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in photo_tasks:
        for task in photo_tasks[chat_id]:
            task.cancel()
        del photo_tasks[chat_id]
        await update.message.reply_text("⏹ Photo loop stopped!")
    else:
        await update.message.reply_text("❌ No active photo loop")

@only_sudo
async def clearphotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in chat_photos:
        del chat_photos[chat_id]
        await update.message.reply_text("🗑 Saved photos cleared!")
    else:
        await update.message.reply_text("❌ No saved photos")

@only_sudo
async def listphotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    count = len(chat_photos.get(chat_id, []))
    await update.message.reply_text(f"📸 Total saved photos: {count}")

# ============================================
# STOP COMMANDS
# ============================================
STOP_REPLY = " 🕷️ ɢᴀᴡᴅ ᥊ 𝐇ᴇʟʟғɪ᥅ꫀ 🕷️𝐂ʜᴜᴅᴀᴊ 𝐑ᴏᴋ 𝐃ɪ"

@only_sudo
async def stop1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc1_tasks:
        for task in nc1_tasks[chat_id]:
            task.cancel()
        del nc1_tasks[chat_id]
    if chat_id in spam1_tasks:
        for task in spam1_tasks[chat_id]:
            task.cancel()
        del spam1_tasks[chat_id]
    if chat_id in slide1_tasks:
        for task in slide1_tasks[chat_id]:
            task.cancel()
        del slide1_tasks[chat_id]
    await update.message.reply_text(STOP_REPLY)

@only_sudo
async def stop2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc2_tasks:
        for task in nc2_tasks[chat_id]:
            task.cancel()
        del nc2_tasks[chat_id]
    if chat_id in spam2_tasks:
        for task in spam2_tasks[chat_id]:
            task.cancel()
        del spam2_tasks[chat_id]
    if chat_id in slide2_tasks:
        for task in slide2_tasks[chat_id]:
            task.cancel()
        del slide2_tasks[chat_id]
    await update.message.reply_text(STOP_REPLY)

@only_sudo
async def stop3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in sf_nc_tasks:
        for task in sf_nc_tasks[chat_id]:
            task.cancel()
        del sf_nc_tasks[chat_id]
    if chat_id in spam3_tasks:
        for task in spam3_tasks[chat_id]:
            task.cancel()
        del spam3_tasks[chat_id]
    if chat_id in slide3_tasks:
        for task in slide3_tasks[chat_id]:
            task.cancel()
        del slide3_tasks[chat_id]
    await update.message.reply_text(STOP_REPLY)

@only_sudo
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    for d in (nc1_tasks, nc2_tasks, sf_nc_tasks, spam1_tasks, spam2_tasks, spam3_tasks, slide1_tasks, slide2_tasks, slide3_tasks, photo_tasks):
        if chat_id in d:
            for task in d[chat_id]:
                task.cancel()
            del d[chat_id]
    await update.message.reply_text(STOP_REPLY)

# ============================================
# OWNER & SUDO COMMANDS
# ============================================
@only_owner
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ Added sudo user: {uid}")

@only_owner
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    if uid == OWNER_ID:
        return await update.message.reply_text("❌ Cannot remove owner")
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"✅ Removed sudo user: {uid}")
    else:
        await update.message.reply_text("❌ User not in sudo list")

@only_sudo
async def sudos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not SUDO_USERS:
        return await update.message.reply_text("No sudo users")
    lines = []
    for uid in SUDO_USERS:
        if uid == OWNER_ID:
            lines.append(f"👑 **{uid}** (Owner)")
        else:
            lines.append(f"🛡️ `{uid}`")
    await update.message.reply_text("**📋 SUDO USERS LIST**\n\n" + "\n".join(lines) + f"\n\n**Total:** {len(SUDO_USERS)}", parse_mode="Markdown")

@only_sudo
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    promoter = context.bot
    other_bots = [b for b in bots if b.id != promoter.id]
    if not other_bots:
        return await update.message.reply_text("❌ No other bots found")
    perms = {
        'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True,
        'can_delete_messages': True, 'can_invite_users': True, 'can_restrict_members': True,
        'can_pin_messages': True, 'can_promote_members': True, 'can_manage_video_chats': True,
        'can_manage_chat': True
    }
    status = await update.message.reply_text("🔄 Promoting bots...")
    promoted = 0
    for bot in other_bots:
        try:
            await promoter.promote_chat_member(chat_id, bot.id, **perms)
            promoted += 1
            await asyncio.sleep(0.5)
        except:
            pass
    await status.edit_text(f"✅ Promoted {promoted}/{len(other_bots)} bots")

@only_sudo
async def bye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    try:
        await update.message.delete()
    except:
        pass
    for bot in bots:
        try:
            await bot.leave_chat(chat_id)
        except:
            pass

# ============================================
# STATUS, HELP, OVER, DELAY COMMANDS
# ============================================
@only_sudo
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uptime = int(time.time() - start_time)
    is_active = False
    chat_id = update.message.chat_id
    if chat_id in spam1_tasks or chat_id in slide1_tasks or chat_id in nc1_tasks:
        is_active = True
    
    status_details = f"""
📊 𝐒𝐘𝐒𝐓𝐄𝐌 𝐒𝐓𝐀𝐓𝐔𝐒 (𝐄𝐗𝐓𝐑𝐄𝐌𝐄 𝐑𝐔𝐒𝐇 𝐌𝐎𝐃𝐄)

🤖 𝐁𝐨𝐭𝐬: {len(bots)}
⚙️ 𝐀𝐜𝐭𝐢𝐯𝐞 𝐂𝐡𝐚𝐭𝐬: {len(nc1_tasks) + len(nc2_tasks) + len(sf_nc_tasks) + len(spam1_tasks) + len(spam2_tasks) + len(spam3_tasks) + len(slide1_tasks) + len(slide2_tasks) + len(slide3_tasks)}
⏳ 𝐔𝐩𝐭𝐢𝐦𝐞: {uptime}s
🌎 𝐆𝐥𝐨𝐛𝐚𝐥 𝐑𝐞𝐚𝐜𝐭: 𝐎𝐅𝐅
🗑️ 𝐏𝐮𝐫𝐠𝐞 𝐀𝐜𝐭𝐢𝐯𝐞: {"𝐎𝐍" if is_active else "𝐎𝐅𝐅"}

🚀 𝐂𝐨𝐧𝐟𝐢𝐠𝐮𝐫𝐚𝐭𝐢𝐨𝐧:
• 𝐁𝐮𝐫𝐬𝐭 𝐋𝐢𝐦𝐢𝐭: 10 𝐦𝐬𝐠𝐬 (𝐎𝐯𝐞𝐫𝐥𝐚𝐩 𝐄𝐧𝐚𝐛𝐥𝐞𝐝)
• 𝐁𝐮𝐫𝐬𝐭 𝐃𝐞𝐥𝐚𝐲: {GLOBAL_DELAY}s
• 𝐒𝐰𝐢𝐭𝐜𝐡 𝐃𝐞𝐥𝐚𝐲: {GLOBAL_DELAY}s
• 𝐒𝐩𝐚𝐦 𝐃𝐞𝐥𝐚𝐲: {GLOBAL_DELAY}s
"""
    await update.message.reply_photo(photo=STATUS_IMAGE_URL, caption=f"𝐀ʟʟ ʙᴏᴛꜱ ᴀʀᴇ 𝐎ɴ ᴀɴᴅ 𝐑ᴇᴀᴅʏ ᴛᴏ ʀᴜɴ ¡ 𝐖ᴀɪᴛɪɴɢ ꜰᴏʀ ʏᴏᴜʀ ᴄᴏᴍᴍᴀɴᴅ !! 🩵\n\n{status_details}", parse_mode="HTML")

@only_sudo
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    HELP_MENU = """╭━━━〔 🕷️ ɢᴀᴡᴅ ᥊ 𝐇ᴇʟʟғɪ᥅ꫀ 🕷️〕━━━╮

          ⚡ 𝐃ᴇᴀᴛʜ 𝐂ᴏʀᴇ 𝐒ʏꜱᴛᴇᴍ ⚡
          🕷️ 𝐌ᴜʟᴛɪ 𝐁ᴏᴛ 𝐄ɴɢɪɴᴇ 🕷️

╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯

⌬ 𝐏ʀᴇꜰɪx → !
⌬ 𝐒ᴛᴀᴛᴜꜱ → 𝐀ʟᴡᴀʏs 𝐀ᴄᴛɪᴠᴇ
⌬ 𝐏ɪɴɢ → ⚡ 𝐒ᴛᴀʙʟᴇ
⌬ 𝐌ᴏᴅᴇ → 🌑 𝐂ʜᴀᴏꜱ

━━━━━━━━━━━━━━━━━━━━

〔 🕸️ 𝐑ᴇɴᴀᴍᴇ 𝐄ɴɢɪɴᴇ 🕸️ 〕

⟡ ɴᴄ𝟷
⟡ ɴᴄ𝟸
⟡ ɴᴄ𝟹

━━━━━━━━━━━━━━━━━━━━

〔 ☄️ 𝐅ʟᴏᴏᴅ 𝐄ɴɢɪɴᴇ ☄️ 〕

⟡ ꜱᴘᴀᴍ𝟷
⟡ ꜱᴘᴀᴍ𝟸
⟡ ꜱᴘᴀᴍ𝟹

━━━━━━━━━━━━━━━━━━━━

〔 🌊 𝐒ʟɪᴅᴇ 𝐄ɴɢɪɴᴇ 🌊 〕

⟡ ꜱʟɪᴅᴇ𝟷
⟡ ꜱʟɪᴅᴇ𝟸
⟡ ꜱʟɪᴅᴇ𝟹

━━━━━━━━━━━━━━━━━━━━

〔 🎮 𝐆ᴀᴍᴇ 𝐙ᴏɴᴇ 🎮 〕

⟡ ᴅɪᴄᴇ
⟡ Qᴜɪᴢ
⟡ ᴀɴꜱᴡᴇʀ
⟡ ᴛᴛᴛ
⟡ ᴍᴏᴠᴇ

━━━━━━━━━━━━━━━━━━━━

〔 📸 𝐏ʜᴏᴛᴏ 𝐂ᴏɴᴛʀᴏʟ 📸 〕

⟡ ꜱᴀᴠᴇᴘʜᴏᴛᴏ
⟡ ꜱᴛᴀʀᴛᴘʜᴏᴛᴏ
⟡ ʟɪꜱᴛᴘʜᴏᴛᴏꜱ
⟡ ꜱᴛᴏᴘᴘʜᴏᴛᴏ

━━━━━━━━━━━━━━━━━━━━

〔 ⚙️ 𝐒ʏꜱᴛᴇᴍ 𝐂ᴏɴᴛʀᴏʟ ⚙️ 〕

⟡ ᴘɪɴɢ
⟡ ᴛɪᴍᴇ
⟡ ᴅᴇʟᴀʏ
⟡ ꜱᴛᴀᴛᴜꜱ
⟡ ᴏᴠᴇʀ
⟡ ꜱᴛᴏᴘᴀʟʟ

━━━━━━━━━━━━━━━━━━━━

〔 👑 𝐎ᴡɴᴇʀ 𝐏ᴀɴᴇʟ 👑 〕

⟡ ᴀᴅᴅꜱᴜᴅᴏ
⟡ ᴅᴇʟꜱᴜᴅᴏ
⟡ ꜱᴜᴅᴏꜱ
⟡ ᴀᴅᴍɪɴ
⟡ ʙʏᴇ

━━━━━━━━━━━━━━━━━━━━

🌧️ 𝐒ᴏᴍᴇ 𝐒ᴄʀɪᴘᴛꜱ 𝐑ᴜɴ
☄️ 𝐓ʜɪꜱ 𝐎ɴᴇ 𝐑ᴜʟᴇꜱ

╰━━━〔 🕷️ ɢᴀᴡᴅ ᥊ 𝐇ᴇʟʟғɪ᥅ꫀ 🕷️ 〕━━━╯"""
    await update.message.reply_photo(photo=HELP_IMAGE_URL, caption=HELP_MENU, parse_mode="HTML")

@only_sudo
async def over_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ist = timezone(timedelta(hours=5, minutes=30))
    now = datetime.now(ist)

    current_time = now.strftime("%I:%M:%S %p")
    current_day = now.strftime("%A")
    current_date = now.strftime("%B %d, %Y")

    over_message = f"""
  🕷️ ɢᴀᴡᴅ ᥊ 𝐇ᴇʟʟғɪ᥅ꫀ 🕷️ᴋɪ ɢᴜʟᴀᴍɪ ᴋʀ ᴋᴇᴇᴅᴇ !! 🤍

𝐓ɪᴍᴇ : {current_time}
𝐃ᴀʏ : {current_day}
𝐃ᴀᴛᴇ : {current_date}
"""

    await update.message.reply_photo(
        photo=OVER_IMAGE_URL,
        caption=over_message,
        parse_mode="HTML"
    )


@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_DELAY

    if not context.args:
        await update.message.reply_text(
            f"⏱ Current delay: {GLOBAL_DELAY}s\nUsage: !delay 0.05"
        )
        return

    try:
        new_delay = float(context.args[0])

        if new_delay < 0.05 or new_delay > 1.0:
            await update.message.reply_text(
                "❌ Delay must be between 0.05 and 1.0 seconds."
            )
            return

        GLOBAL_DELAY = new_delay

        await update.message.reply_text(
            f"✅ Delay set to {GLOBAL_DELAY}s"
        )

    except:
        await update.message.reply_text("❌ Invalid number")


@only_sudo
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚡ Pong!")


@only_sudo
async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = random.randint(1, 6)
    await update.message.reply_text(f"🎲 Dice → {value}")


@only_sudo
async def time_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%I:%M:%S %p")
    await update.message.reply_text(f"🕒 Time → {now}")


QUIZ_QUESTIONS = [
    {
        "question": "👑 Who is strongest in com?",
        "answer": "Aayan"
    },
    {
        "question": "🌍 Capital of Japan?",
        "answer": "tokyo"
    },
    {
        "question": "⚡ 5 + 7 = ?",
        "answer": "12"
    },
    {
        "question": "🎮 Creator of Minecraft?",
        "answer": "notch"
    },
    {
        "question": "🕷️ Which planet is called Red Planet?",
        "answer": "mars"
    }
]

current_quiz = {}
ttt_games = {}


@only_sudo
async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = random.choice(QUIZ_QUESTIONS)

    current_quiz[update.effective_chat.id] = q["answer"]

    await update.message.reply_text(
        f"❓ 𝐐ᴜɪᴢ 𝐓ɪᴍᴇ ❓\n\n{q['question']}"
    )


@only_sudo
async def answer(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    if chat_id not in current_quiz:
        return await update.message.reply_text(
            "❌ No active quiz!"
        )

    user_answer = " ".join(context.args).lower()

    if user_answer == current_quiz[chat_id]:
        await update.message.reply_text("✅ 7 crore ⚡")
    else:
        await update.message.reply_text("❌ dimag lga lwde 💀")

    del current_quiz[chat_id]


WIN_PATTERNS = [
    [0,1,2],
    [3,4,5],
    [6,7,8],
    [0,3,6],
    [1,4,7],
    [2,5,8],
    [0,4,8],
    [2,4,6]
]


def render_board(board):
    return f'''
{board[0]} | {board[1]} | {board[2]}
---------
{board[3]} | {board[4]} | {board[5]}
---------
{board[6]} | {board[7]} | {board[8]}
'''


def check_win(board, symbol):

    for pattern in WIN_PATTERNS:
        if all(board[i] == symbol for i in pattern):
            return True

    return False


@only_sudo
async def ttt(update: Update, context: ContextTypes.DEFAULT_TYPE):

    board = ["1","2","3","4","5","6","7","8","9"]

    ttt_games[update.effective_chat.id] = {
        "board": board,
        "turn": "X"
    }

    await update.message.reply_text(
        "🎮 TicTacToe Started!\n\n"
        + render_board(board)
        + "\n\nUse: !move <position>"
    )


@only_sudo
async def move(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    if chat_id not in ttt_games:
        return await update.message.reply_text(
            "❌ No active game!"
        )

    if not context.args:
        return await update.message.reply_text(
            "Usage: !move 1-9"
        )

    game = ttt_games[chat_id]

    board = game["board"]
    turn = game["turn"]

    try:
        pos = int(context.args[0]) - 1

    except:
        return await update.message.reply_text(
            "❌ Invalid number!"
        )

    if pos < 0 or pos > 8:
        return await update.message.reply_text(
            "❌ Choose 1-9"
        )

    if board[pos] in ["X", "O"]:
        return await update.message.reply_text(
            "❌ Already used!"
        )

    board[pos] = turn

    if check_win(board, turn):

        await update.message.reply_text(
            render_board(board)
            + f"\n\n🏆 {turn} Wins!"
        )

        del ttt_games[chat_id]
        return

    if all(x in ["X", "O"] for x in board):

        await update.message.reply_text(
            render_board(board)
            + "\n\n🤝 Draw!"
        )

        del ttt_games[chat_id]
        return

    game["turn"] = "O" if turn == "X" else "X"

    await update.message.reply_text(
        render_board(board)
        + f"\n\n🎯 Turn: {game['turn']}"
    )

# ============================================
# BOT STARTUP
# ============================================
async def run_all_bots():
    global start_time
    start_time = time.time()

    if not TOKENS:
        print("❌ No bot tokens provided!")
        return

    MAIN_BOT_TOKEN = TOKENS[0]

    for token in TOKENS:
        try:
            app = Application.builder().token(token).build()
            
            # NC Commands
            app.add_handler(PrefixHandler("!", "nc1", nc1))
            app.add_handler(PrefixHandler("!", "nc2", nc2))
            app.add_handler(PrefixHandler("!", "nc3", nc3))
            
            # Spam Commands
            app.add_handler(PrefixHandler("!", "spam1", spam1))
            app.add_handler(PrefixHandler("!", "spam2", spam2))
            app.add_handler(PrefixHandler("!", "spam3", spam3))
            
            # Slide Commands
            app.add_handler(PrefixHandler("!", "slide1", slide1))
            app.add_handler(PrefixHandler("!", "slide2", slide2))
            app.add_handler(PrefixHandler("!", "slide3", slide3))
            
            # Photo Commands
            app.add_handler(PrefixHandler("!", "savephoto", savephoto))
            app.add_handler(PrefixHandler("!", "startphoto", startphoto))
            app.add_handler(PrefixHandler("!", "stopphoto", stopphoto))
            app.add_handler(PrefixHandler("!", "clearphotos", clearphotos))
            app.add_handler(PrefixHandler("!", "listphotos", listphotos))
            
            # Stop Commands
            app.add_handler(PrefixHandler("!", "stop1", stop1))
            app.add_handler(PrefixHandler("!", "stop2", stop2))
            app.add_handler(PrefixHandler("!", "stop3", stop3))
            app.add_handler(PrefixHandler("!", "stopall", stopall))
            
            # Owner/Sudo Commands
            app.add_handler(PrefixHandler("!", "addsudo", addsudo))
            app.add_handler(PrefixHandler("!", "delsudo", delsudo))
            app.add_handler(PrefixHandler("!", "sudos", sudos))
            app.add_handler(PrefixHandler("!", "admin", admin))
            app.add_handler(PrefixHandler("!", "bye", bye))
            
                       # Main Bot Commands Only
            if token == MAIN_BOT_TOKEN:

                app.add_handler(PrefixHandler("!", "status", status_cmd))
                app.add_handler(PrefixHandler("!", "help", help_cmd))
                app.add_handler(PrefixHandler("!", "over", over_cmd))
                app.add_handler(PrefixHandler("!", "delay", delay_cmd))

                app.add_handler(PrefixHandler("!", "ping", ping))
                app.add_handler(PrefixHandler("!", "dice", dice))
                app.add_handler(PrefixHandler("!", "time", time_cmd))

                app.add_handler(PrefixHandler("!", "quiz", quiz))
                app.add_handler(PrefixHandler("!", "answer", answer))

                app.add_handler(PrefixHandler("!", "ttt", ttt))
                app.add_handler(PrefixHandler("!", "move", move))
            
            apps.append(app)
            bots.append(app.bot)
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Bot started: {token[:10]}...")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")
    
    print(f"\n 🪐 𝐓ᴀᴋᴀꜱʜɪ 𝐱 𝐑ᴇxxʏ  𝐁ʜᴀɢᴡᴀɴ 🕷️")
    print(f"🤖 Total bots online: {len(bots)}")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"⚙️ Prefix: !")
    await asyncio.Event().wait()

# ============================================
# MAIN EXECUTION
# ============================================
if __name__ == "__main__":
    print("\n" + "="*50)
    print("      AAYAN BHAGWAN MULTI-BOT SYSTEM")
    print("="*50)
    try:
        pw = getpass.getpass("🔑 ENTER ACCESS PASSWORD: ")
    except:
        pw = input("🔑 ENTER ACCESS PASSWORD: ")
    
    if pw != PASSWORD:
        print("\n❌ ACCESS DENIED")
        sys.exit(1)
    
    print("\n✅ ACCESS GRANTED! INITIALIZING BOTS...\n")
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("\n🛑 Bots stopped.")
    except Exception as e:
        print(f"❌ Error: {e}")