# FREAKY_BOT.py - FINAL VERSION (Ready to Run)
import asyncio
import json
import os
import sys
import getpass
import random
from datetime import datetime, timezone, timedelta
from telegram import Update, ChatMemberUpdated, ChatMember
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, ChatMemberHandler
import logging

# ---------------------------
# YOUR 11 BOT TOKENS
# ---------------------------
TOKENS = [
    "8579699126:AAFGJbrUj2t9z3Purj0XD9_dftSu6_JA1AQ",
    "8490800570:AAF6Skyfg3lbj7TekYpD4KxMStZlccWVM7M",
    "8538748762:AAG8AshcSWypAvif3kMf06yP_MRMBv73u-c",
    "8524204591:AAEIzT8-ERBOkW2OW4as3NY4BcDQlWo3PWk",
    "8233558696:AAGLYQHR6U24DF6p_CYigDGqENvnfUcfQtM",
    "8740227053:AAG77kiqWLE0rua2sdPHAwIw_C4SSIbvt3Q",
    "8612597436:AAFD0dj0_CxKrIVnIYI4O6geGTt4fnhTLAo",
    "8590785273:AAEdvR6q_jsalqr8sblYzSn6n0-6Fs0Dwc4",
    "8593897924:AAEA-Gdg69u4OUIfizeTxH63_pPCYj1_Mi4",
    "8231693095:AAFgOjkzNN4Ij_aEZ8Ga7GIr95WS6b-qTxY",
    "8737134116:AAG5L-sCgaVv7IiU7KWfXULK9f0uwgKeMeU",
]

# ---------------------------
# OWNER & SUDO CONFIG
# ---------------------------
OWNER_ID = 7058385030
SUDO_FILE = "sudo_users.json"

# Load sudo users
if os.path.exists(SUDO_FILE):
    with open(SUDO_FILE) as f:
        SUDO_USERS = set(json.load(f))
else:
    SUDO_USERS = {OWNER_ID}

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)

# ---------------------------
# GLOBAL STATE
# ---------------------------
apps = []
bots = []
bots_info = []               # list of dicts: {'id': int, 'username': str, 'bot': bot_instance}
nc_tasks = {}                # chat_id -> list of NC tasks
spam_tasks = {}              # chat_id -> list of spam tasks
target_tasks = {}            # chat_id -> list of target slider tasks
mark_tasks = {}              # chat_id -> list of mark slider tasks
fcked_tasks = {}             # chat_id -> list of fcked slider tasks
GLOBAL_DELAY = 0.05          # default speed (can be changed with /delay)

STOP_MESSAGE = "𝑯𝒎...𝒓𝒖𝒌 𝒈𝒚𝒆 !!"

logging.basicConfig(level=logging.INFO)

# ---------------------------
# PERMISSION HELPERS
# ---------------------------
def is_owner_or_sudo(uid):
    return uid == OWNER_ID or uid in SUDO_USERS

def owner_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id == OWNER_ID:
            return await func(update, context)
        await update.message.reply_text("❌ Only owner can use this command!")
    return wrapper

def sudo_only(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if is_owner_or_sudo(update.effective_user.id):
            return await func(update, context)
        await update.message.reply_text("❌ You don't have permission!")
    return wrapper

# ---------------------------
# NC LOOPS
# ---------------------------
SIGNS_LIST = [
    "⋆˚꩜｡", ".✦ ݁˖", "𝜗ৎ", "݁ ˖Ი𐑼⋆", "⊹ ࣪ ˖", "⋆˚࿔", "𑣲", "˚˖𓍢ִ໋❀",
    "♡", "ᯓ★", ".☘︎ ݁˖", "⋆.𐙚 ̊", "₊˚⊹ ᰔ", ".⋆♱", "𖦹"
]

FACENC_EMOJIS = [
    "😀", "😃", "😄", "😁", "😆", "😅", "😂", "🤣", "😉", "😗", "😙", "😚", "😘",
    "🥰", "😍", "😖", "😣", "😩", "😫", "😭"
]

FLAG_EMOJIS = [
    "🇦🇨", "🇦🇩", "🇦🇪", "🇦🇫", "🇦🇬", "🇦🇮", "🇦🇱", "🇦🇲", "🇦🇴", "🇦🇶", "🇦🇷", "🇦🇸", "🇦🇹", "🇦🇺", "🇦🇼", "🇦🇽", "🇦🇿",
    "🇧🇦", "🇧🇧", "🇧🇩", "🇧🇪", "🇧🇫", "🇧🇬", "🇧🇭", "🇧🇮", "🇧🇯", "🇧🇱", "🇧🇲", "🇧🇳", "🇧🇴", "🇧🇶", "🇧🇷", "🇧🇸", "🇧🇹", "🇧🇻", "🇧🇼", "🇧🇾", "🇧🇿",
    "🇨🇦", "🇨🇦", "🇨🇨", "🇨🇩", "🇨🇫", "🇨🇬", "🇨🇭", "🇨🇮", "🇨🇰", "🇨🇱", "🇨🇲", "🇨🇳", "🇨🇴", "🇨🇵", "🇨🇶", "🇨🇷", "🇨🇺", "🇨🇼",
    "🇮🇳", "🇮🇱", "🇯🇵", "🇰🇷", "🇱🇰", "🇱🇷", "🇱🇾", "🇿🇦",
    "🏴󠁧󠁢󠁷󠁬󠁳󠁿",  # Wales
    "🇾🇹", "🇻🇮", "🇻🇬", "🇺🇳", "🇺🇲"
]

EMOJINC_EMOJIS = [
    "🦁", "🐯", "🐶", "🐺", "🐻", "🐻‍❄️", "🐨", "🐼", "🐹", "🐭", "🐰", "🦊", "🐮", "🐷", "🦄", "🐗", "🐴", "🫎", "🐲", "🐉", "🦖", "🦕", "🐊", "🐄", "🐖", "🐎", "🐇", "🐁", "🐀", "🦥", "🦣", "🐘", "🦓", "🦘", "🐅", "🦦", "🦔", "🐓", "🕊️", "🦆", "🪿", "🦩", "🐋", "🐬", "🦈", "🦭", "🐧", "🐳", "🐟", "🐠", "🦚", "🐦‍🔥", "🦜", "🦉", "🕷️", "🐌", "🦋", "🪼", "🐙", "🦪", "🪸", "🦑"
]

WORDNC_WORDS = [
    "𝙏𝙈𝙆𝘾",
    "𝙍𝙉𝘿𝙔 𝙋𝙐𝙏𝙍𝘼",
    "𝙏𝙈𝙆𝘽",
    "𝙂𝘼̀𝙍𝙀𝙀𝘽",
    "𝙂𝙐𝙇𝘼̀𝙈",
    "𝘾𝙃𝘼𝙆𝙆𝙀",
    "𝘾𝙃𝙈𝙍",
    "𝘽𝙎𝘿𝙆",
    "𝙏𝘽𝙆𝘾",
    "𝙏𝙈𝙆𝙇",
    "𝙏𝘽𝙆𝙇",
    "𝙏𝘼𝙏𝙏𝙀"
]

CUSTOMNC_EMOJIS = [
    "🍓", "🍒", "🍎", "🍅", "🌶️", "🍉", "🍑", "🍊", "🥕", "🥭", "🍍", "🍌", "🌽", "🍋", "🍋‍🟩", "🍈", "🍐", "🫛", "🥬", "🫑",
    "🍏", "🥝", "🥑", "🫒", "🥦", "🥒", "🫐", "🍇", "🍆", "🍠", "🫜", "🥥", "🥔", "🍄‍🟫", "🧅", "🫚", "🧄", "🫘", "🌰", "🥜"
]

LOVE_EMOJIS = [
    "♥️", "💌", "💕", "💞", "💓", "💗", "💖", "💝", "💘", "🩷", "🤍", "🩶", "🖤", "🤎",
    "💜", "💙", "🩵", "💚", "💛", "🧡", "❤️", "❤️‍🩹", "❣️", "❤️‍🔥", "💔", "🫀"
]

MEOW_EMOJIS = [
    "😺", "😸", "😹", "😻", "😼", "😽", "🙀", "😿", "😾", "🐈", "🐈‍⬛", "🐱"
]

TRIAL_EMOJIS = [
    "🏔️", "🌋", "☃️", "🏝️", "🏖️", "🌊", "🌬️", "❄️", "🌀", "🌪️", "⚡", "☔", "💧", "☁️", "🌨️", "🌧️", "🌩️", "⛈️", "🌦️",
    "🌥️", "⛅", "🌤️", "☀️", "🌞", "🌝", "🌚", "🌜", "🌛", "🌙", "⭐", "🌟", "✨", "🪐", "🌍", "🌠", "🌌", "☄️", "🌑", "🌒",
    "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"
]

# ---------------------------
# SLIDER CONSTANTS
# ---------------------------
TARGET_MESSAGE = "𐙚࣪ 𝐓ᴇʀɪ ᴍᴀ 𝐆ᴜʟᴀᴍ 🎏"

MARK_MESSAGES = [
    "𝘾𝙝𝙡 𝙩𝙖𝙩𝙩𝙚 𝙗𝙝𝙚𝙚𝙠 𝙢𝙖𝙣𝙜 ☙",
    "𝙏𝙚𝙧𝙞 𝙢𝙠𝙘 𝙢𝙞𝙚 𝙢𝙖𝙜𝙜𝙞𝙚 𝙗𝙣𝙖𝙪𝙜𝙖",
    "𝙊𝙮𝙚 𝙘𝙝𝙪𝙥 𝙘𝙝𝙖𝙥 𝙜𝙪𝙡𝙖𝙢𝙞 𝙠𝙧 😡",
    "𝘼𝙧𝙚 𝙧𝙣𝙙𝙮 𝙧𝙤𝙣𝙖 𝙢𝙩 𝙠𝙧 𝙣𝙞𝙠𝙡 𝙞𝙙𝙝𝙧 𝙨𝙚 𝙜𝙖𝙧𝙚𝙚𝙗 𝙩𝙖𝙩𝙩𝙚 😆",
    "𝙏𝙚𝙧𝙞 𝙗𝙝𝙚𝙣 𝙠𝙚 𝙨𝙖𝙖𝙩𝙝 𝙡𝙪𝙙𝙤 𝙠𝙝𝙚𝙡𝙣𝙚 𝙟𝙖 𝙧𝙝𝙖 𝙝𝙪 𝙧𝙤 𝙢𝙩 😆"
]

FCKED_MESSAGES = [
    "𝙏𝙪 𝙩𝙤 𝙘𝙝𝙪𝙙 𝙜𝙮𝙖 𝙮𝙡𝙡 🥹",
    "𝙏𝙚𝙧𝙞 𝙢𝙖𝙖 𝙗𝙝𝙞 𝙘𝙝𝙪𝙙 𝙜𝙮𝙞 𝙮𝙡𝙡 🥹",
    "𝙏𝙚𝙧𝙞 𝙗𝙝𝙚𝙣 𝙗𝙝𝙞 𝙘𝙝𝙪𝙙 𝙜𝙮𝙞 𝙮𝙡𝙡 🥹",
    "𝙏𝙚𝙧𝙖 𝙗𝙖𝙖𝙥 𝙗𝙝𝙞 𝙘𝙝𝙪𝙙 𝙜𝙮𝙖 𝙮𝙡𝙡 🥹",
    "𝙏𝙚𝙧𝙞 𝙗𝙪𝙖𝙖 𝙗𝙝𝙞 𝙘𝙝𝙪𝙙 𝙜𝙮𝙞 𝙮𝙡𝙡 🥹",
    "𝙏𝙚𝙧𝙞 𝙢𝙖̀𝙪𝙨𝙞 𝙗𝙝𝙞 𝙘𝙝𝙪𝙙 𝙜𝙮𝙞 𝙮𝙡𝙡 🥹",
    "𝙏𝙚𝙧𝙞 𝙙𝙖𝙙𝙞 𝙗𝙝𝙞 𝙘𝙝𝙪𝙙 𝙜𝙮𝙞 𝙮𝙡𝙡 🥹",
    "𝙔𝙤𝙪 𝙖̀𝙧𝙚 𝙛𝙪𝙘𝙠𝙚𝙙 𝙪𝙥 𝙗𝙧𝙤 🥹"
]

GREETING_MESSAGE = "ꪑ꠸ꫀ ꪖᧁꪗꪖ 🫣"
ADMIN_MESSAGE = "𝑨𝒅𝒎𝒊𝒏 𝒉𝒖 ☄️"
BYE_MESSAGE = "ᥴꫝꪊᦔꪖ꠸ ꪮꪜꫀ᥅ ᥇ꪗ ᠻ᥅ꫀꪖᛕꪗ ᥇ꪗꫀ ᥇ꪗꫀ ~ִֶָ. ..𓂃 ࣪ ִֶָ🪽་༘࿐"

# ---------------------------
# SPAM CONSTANTS
# ---------------------------
COVER_MESSAGE = "{text} 𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐌𝐀𝐑 𝐆𝐘𝐈 ~ °‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡°‧ 𓆝 𓆟 𓆞 ·｡𝐂𝐇𝐔𝐃 𝐑𝐍𝐃𝐘 °‧ 𓆝 𓆟 𓆞 ·｡"

ARROW_BLOCK = """╰┈➤ 𝘾𝙝𝙪𝙙 𝙍𝙣𝙙𝙮
╰┈➤ 𝙏𝙈𝙆𝘾
╰┈➤ 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝙈𝘼𝙍 𝙂𝙔𝙄
╰┈➤ 𝙂𝘼𝙈𝙀 𝙊𝙑𝙀𝙍
"""
ARROW_REPEAT_COUNT = 6
ARROW_FULL = ARROW_BLOCK * ARROW_REPEAT_COUNT

MATRIX_LINE = "{text}  𝐊𝐈 𝐁𝐇𝐍 𝐊𝐈 𝐗𝐇𝐔𝐓 𝐗𝐇𝐔𝐃𝐀𝐈 𝐌𝐄 𝐀𝐀𝐏𝐊𝐀 𝐒𝐖𝐀𝐆𝐀𝐓 𝐇𝐀𝐈🤍☁️🌿 ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ~/"
MATRIX_REPEAT = 10

KAOMOJI_LIST = [
    "(◕‿◕)", "(✿◠‿◠)", "(◔‿◔)", "(◡‿◡✿)", "(◕‿◕✿)", "(ᵔ◡ᵔ)", "(◠‿◠✿)", "(◕ᴗ◕✿)",
    "(◡‿◡)", "(◠‿◠)", "(◕‿◕)", "(◡ω◡)", "(◕ω◕)", "(◠ω◠)", "(ᵔᴗᵔ)", "(◕ᴗ◕)",
    "(◡ᴗ◡)", "(◠ᴗ◠)", "(｡◕‿◕｡)", "(◕‿◕✿)", "≧◔◡◔≦", "◕‿◕", "◕ω◕",
    "ʘ‿ʘ", "◉‿◉", "≧◡≦", "≧ω≦", ">ᴗ<", ">ω<", "^_^", "^-^", ">_<", "._.",
    "(•‿•)", "(•ω•)", "(•̀ᴗ•́)و", "(◕‿◕✿)", "♥‿♥", "😊", "😄", "😁"
]

# ---------------------------
# NC LOOP FUNCTIONS
# ---------------------------
async def signsnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            sign = SIGNS_LIST[i % len(SIGNS_LIST)]
            new_title = f"{text} ᶠᶸᶜᵏᵧₒᵤ! ~ {sign}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def facenc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FACENC_EMOJIS[i % len(FACENC_EMOJIS)]
            new_title = f"{text} 𝙏𝙈𝙆𝘽 𑁍ࠬܓ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def timenc_loop(bot, chat_id, text):
    ist = timezone(timedelta(hours=5, minutes=30))
    while True:
        try:
            now = datetime.now(ist)
            time_str = now.strftime("%H:%M:%S")
            new_title = f"{text} 𝘾𝙃𝙐𝘿𝘼𝙆𝘼𝘿 ᥫ᭡.ִֶָ𓂃 {time_str} .ᐟ.ᐟ.ᐟ"
            await bot.set_chat_title(chat_id, new_title)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def flagnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            flag = FLAG_EMOJIS[i % len(FLAG_EMOJIS)]
            new_title = f"{text} 𝙍𝙉𝘿𝙔°‧ 𓆝 𓆟 𓆞 ·｡ {flag}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def emojinc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = EMOJINC_EMOJIS[i % len(EMOJINC_EMOJIS)]
            new_title = f"{text} 𝙏𝙈𝙆𝘾 𝙈𝙄𝙀⁀➴༯ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def wordnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            word = WORDNC_WORDS[i % len(WORDNC_WORDS)]
            new_title = f"{text} ִֶָ𓂃 ࣪ ִֶָ🦢་༘࿐ {word}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def customnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = CUSTOMNC_EMOJIS[i % len(CUSTOMNC_EMOJIS)]
            new_title = f"{text} ִֶָ── {emoji} ──"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def lovenc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = LOVE_EMOJIS[i % len(LOVE_EMOJIS)]
            new_title = f"{text} 𝘾𝙃𝙐𝘿 જ⁀➴ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def meownc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MEOW_EMOJIS[i % len(MEOW_EMOJIS)]
            new_title = f"{text} 𝙈𝙀𝙊𝙒𝘿𝘼𝙍𝘾𝙃𝙊𝘿 {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def trialnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = TRIAL_EMOJIS[i % len(TRIAL_EMOJIS)]
            new_title = f"{text} 𝙂𝙐𝙇𝘼𝙈𝙄 𝙆𝙍𓇢𓆸 {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

# ---------------------------
# SPAM LOOP FUNCTIONS
# ---------------------------
async def cover_spam_loop(bot, chat_id, text):
    message = COVER_MESSAGE.format(text=text)
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def arrow_spam_loop(bot, chat_id, text):
    message = f"{text}\n" + ARROW_FULL
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def matrix_spam_loop(bot, chat_id, text):
    lines = [MATRIX_LINE.format(text=text) for _ in range(MATRIX_REPEAT)]
    message = "\n".join(lines)
    while True:
        try:
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def custom_spam_loop(bot, chat_id, text):
    while True:
        try:
            kaomoji = random.choice(KAOMOJI_LIST)
            message = f"{text}  ⩇⩇:⩇⩇ {kaomoji}"
            await bot.send_message(chat_id, message)
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

# ---------------------------
# SLIDER LOOP FUNCTIONS
# ---------------------------
async def target_loop(bot, chat_id, target_msg_id):
    while True:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=TARGET_MESSAGE,
                reply_to_message_id=target_msg_id
            )
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def mark_loop(bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            msg = MARK_MESSAGES[i % len(MARK_MESSAGES)]
            await bot.send_message(
                chat_id=chat_id,
                text=msg,
                reply_to_message_id=target_msg_id
            )
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def fcked_loop(bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            msg = FCKED_MESSAGES[i % len(FCKED_MESSAGES)]
            await bot.send_message(
                chat_id=chat_id,
                text=msg,
                reply_to_message_id=target_msg_id
            )
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

# ---------------------------
# AUTO‑GREET AND ADMIN HANDLER
# ---------------------------
async def handle_my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result: ChatMemberUpdated = update.my_chat_member
    if result.chat.type not in ["group", "supergroup"]:
        return
    old = result.old_chat_member
    new = result.new_chat_member

    # Bot was added to the group
    if old.status in [ChatMember.LEFT, ChatMember.BANNED] and new.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR]:
        await context.bot.send_message(chat_id=result.chat.id, text=GREETING_MESSAGE)

    # Bot was promoted to administrator
    elif old.status == ChatMember.MEMBER and new.status == ChatMember.ADMINISTRATOR:
        await context.bot.send_message(chat_id=result.chat.id, text=ADMIN_MESSAGE)

# ---------------------------
# NC COMMAND HANDLERS
# ---------------------------
@sudo_only
async def signsnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /signsnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(signsnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ signsnc started for: {text}")

@sudo_only
async def facenc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /facenc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(facenc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ facenc started for: {text}")

@sudo_only
async def timenc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /timenc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(timenc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ timenc started for: {text}")

@sudo_only
async def flagnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /flagnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(flagnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ flagnc started for: {text}")

@sudo_only
async def emojinc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /emojinc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(emojinc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ emojinc started for: {text}")

@sudo_only
async def wordnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /wordnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(wordnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ wordnc started for: {text}")

@sudo_only
async def customnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /customnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(customnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ customnc started for: {text}")

@sudo_only
async def lovenc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /lovenc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(lovenc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ lovenc started for: {text}")

@sudo_only
async def meownc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /meownc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(meownc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ meownc started for: {text}")

@sudo_only
async def trialnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /trialnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]

    tasks = [asyncio.create_task(trialnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ trialnc started for: {text}")

# ---------------------------
# STOP NC COMMAND (sudo+owner)
# ---------------------------
@sudo_only
async def stopnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks and nc_tasks[chat_id]:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else:
        await update.message.reply_text("❌ No NC running in this chat.")

# ---------------------------
# SPAM COMMAND HANDLERS
# ---------------------------
@sudo_only
async def cover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /cover <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]

    tasks = [asyncio.create_task(cover_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ cover spam started for: {text}")

@sudo_only
async def arrow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /arrow <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]

    tasks = [asyncio.create_task(arrow_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ arrow spam started for: {text}")

@sudo_only
async def matrix(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /matrix <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]

    tasks = [asyncio.create_task(matrix_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ matrix spam started for: {text}")

@sudo_only
async def custom(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /custom <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id

    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]

    tasks = [asyncio.create_task(custom_spam_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(f"✅ custom spam started for: {text}")

# ---------------------------
# STOP SPAM COMMAND (sudo+owner)
# ---------------------------
@sudo_only
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks and spam_tasks[chat_id]:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
        await update.message.reply_text(STOP_MESSAGE)
    else:
        await update.message.reply_text("❌ No spam running in this chat.")

# ---------------------------
# SLIDER COMMAND HANDLERS
# ---------------------------
@sudo_only
async def target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start target!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in target_tasks:
        for task in target_tasks[chat_id]:
            task.cancel()
        del target_tasks[chat_id]
    tasks = [asyncio.create_task(target_loop(b, chat_id, target_msg_id)) for b in bots]
    target_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Target started on that message.")

@sudo_only
async def mark(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start mark!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in mark_tasks:
        for task in mark_tasks[chat_id]:
            task.cancel()
        del mark_tasks[chat_id]
    tasks = [asyncio.create_task(mark_loop(b, chat_id, target_msg_id)) for b in bots]
    mark_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Mark started on that message.")

@sudo_only
async def fcked(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start fcked!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in fcked_tasks:
        for task in fcked_tasks[chat_id]:
            task.cancel()
        del fcked_tasks[chat_id]
    tasks = [asyncio.create_task(fcked_loop(b, chat_id, target_msg_id)) for b in bots]
    fcked_tasks[chat_id] = tasks
    await update.message.reply_text("✅ Fcked started on that message.")

# ---------------------------
# STOPSLIDE COMMAND (unified, sudo+owner)
# ---------------------------
@sudo_only
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    stopped = False
    if chat_id in target_tasks and target_tasks[chat_id]:
        for task in target_tasks[chat_id]:
            task.cancel()
        del target_tasks[chat_id]
        stopped = True
    if chat_id in mark_tasks and mark_tasks[chat_id]:
        for task in mark_tasks[chat_id]:
            task.cancel()
        del mark_tasks[chat_id]
        stopped = True
    if chat_id in fcked_tasks and fcked_tasks[chat_id]:
        for task in fcked_tasks[chat_id]:
            task.cancel()
        del fcked_tasks[chat_id]
        stopped = True
    if stopped:
        await update.message.reply_text(STOP_MESSAGE)
    else:
        await update.message.reply_text("❌ No slider running in this chat.")

# ---------------------------
# STOPALL COMMAND (sudo+owner)
# ---------------------------
@sudo_only
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    # Stop NC tasks
    if chat_id in nc_tasks and nc_tasks[chat_id]:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    # Stop Spam tasks
    if chat_id in spam_tasks and spam_tasks[chat_id]:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    # Stop Slider tasks
    if chat_id in target_tasks and target_tasks[chat_id]:
        for task in target_tasks[chat_id]:
            task.cancel()
        del target_tasks[chat_id]
    if chat_id in mark_tasks and mark_tasks[chat_id]:
        for task in mark_tasks[chat_id]:
            task.cancel()
        del mark_tasks[chat_id]
    if chat_id in fcked_tasks and fcked_tasks[chat_id]:
        for task in fcked_tasks[chat_id]:
            task.cancel()
        del fcked_tasks[chat_id]
    await update.message.reply_text(STOP_MESSAGE)

# ---------------------------
# DELAY COMMAND (sudo+owner)
# ---------------------------
@sudo_only
async def delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global GLOBAL_DELAY
    if not context.args:
        await update.message.reply_text(f"⏱ Current delay: {GLOBAL_DELAY:.3f}s\nUsage: /delay <0.005-0.05>")
        return
    try:
        new_delay = float(context.args[0])
        if new_delay < 0.005 or new_delay > 0.05:
            await update.message.reply_text("❌ Delay must be between 0.005 and 0.05 seconds.")
            return
        GLOBAL_DELAY = new_delay
        await update.message.reply_text(f"✅ Delay set to {GLOBAL_DELAY:.3f}s")
    except ValueError:
        await update.message.reply_text("❌ Invalid number. Use /delay <0.005-0.05>")

# ---------------------------
# PROMOTE COMMAND (owner only)
# ---------------------------
@owner_only
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    promoter_bot = context.bot
    promoter_id = promoter_bot.id
    other_bots = [info for info in bots_info if info['id'] != promoter_id]
    if not other_bots:
        await update.message.reply_text("No other bots to promote.")
        return
    permissions = {
        'can_change_info': True,
        'can_post_messages': True,
        'can_edit_messages': True,
        'can_delete_messages': True,
        'can_invite_users': True,
        'can_restrict_members': True,
        'can_pin_messages': True,
        'can_promote_members': True,
        'can_manage_video_chats': True,
        'can_manage_chat': True
    }
    promoted_count = 0
    for bot_info in other_bots:
        try:
            await promoter_bot.promote_chat_member(
                chat_id=chat_id,
                user_id=bot_info['id'],
                **permissions
            )
            promoted_count += 1
        except Exception as e:
            logging.warning(f"Failed to promote bot {bot_info['id']}: {e}")
    await update.message.reply_text(f"Promotion process completed. {promoted_count} bots promoted (others may already be admin).")

# ---------------------------
# JOIN COMMAND (owner only)
# ---------------------------
@owner_only
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    admin_bot = context.bot
    admin_id = admin_bot.id
    other_bots = [info for info in bots_info if info['id'] != admin_id]
    if not other_bots:
        await update.message.reply_text("No other bots to add.")
        return
    added_count = 0
    for bot_info in other_bots:
        try:
            await admin_bot.add_chat_members(chat_id, [bot_info['id']])
            added_count += 1
        except Exception as e:
            logging.warning(f"Failed to add bot {bot_info['id']}: {e}")
    await update.message.reply_text(f"Join process completed. Attempted to add {len(other_bots)} bots. {added_count} successfully added (others may already be present).")

# ---------------------------
# BYE COMMAND (owner only)
# ---------------------------
@owner_only
async def bye(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text("👋 All bots are leaving...")
    for bot in bots:
        try:
            await bot.send_message(chat_id, BYE_MESSAGE)
            await bot.leave_chat(chat_id)
        except Exception as e:
            logging.warning(f"Bot {bot.id} could not leave: {e}")

# ---------------------------
# FUN COMMANDS
# ---------------------------
@sudo_only
async def freaky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("sneaky")

@sudo_only
async def zip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("zap")

@sudo_only
async def lytic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("logic")

# ---------------------------
# SUDO MANAGEMENT (owner only)
# ---------------------------
@owner_only
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"✅ Added sudo: {uid}")

@owner_only
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS and uid != OWNER_ID:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"✅ Removed sudo: {uid}")
    else:
        await update.message.reply_text("❌ Cannot remove owner or user not in sudo")

@owner_only
async def sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = [f"👑 {uid}" for uid in SUDO_USERS]
    await update.message.reply_text(f"**SUDO USERS:**\n" + "\n".join(lines) + f"\n\nTotal: {len(SUDO_USERS)}")

# ---------------------------
# HELP COMMAND
# ---------------------------
HELP_MENU = """
───𝐋𝐯𝐱 ~ 𝐅ꭈׁׅꫀꪖƙׁׅ֑ꪗ ˚˖𓍢ִ໋🦢˚───

﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌﹌
🎐 𝑻𝒓𝒚 𝒊𝒕 ┈┈┈┈┈┈┈┈

𓂃 𓈒 /freaky
𓂃 𓈒 /zip
𓂃 𓈒 /lytic
═══════════════════
🎐 𝑵𝒄'𝒔 ┈┈┈┈┈┈┈┈

𓂃 𓈒 /signsnc
𓂃 𓈒 /facenc
𓂃 𓈒 /timenc
𓂃 𓈒 /flagnc
𓂃 𓈒 /emojinc
𓂃 𓈒 /wordnc
═══════════════════
🎐 𝑺𝒑𝒂𝒎 ┈┈┈┈┈┈┈┈

𓂃 𓈒 /cover
𓂃 𓈒 /custom
𓂃 𓈒 /arrow
═══════════════════
🎐 𝑼𝒏𝒊𝒒𝒖𝒆 ┈┈┈┈┈┈┈┈

𓂃 𓈒 /customnc
𓂃 𓈒 /custom
𓂃 𓈒 /lovenc
𓂃 𓈒 /meownc
𓂃 𓈒 /trialnc
═══════════════════
🎐 𝑺𝒍𝒊𝒅𝒆 𝒓𝒆𝒑𝒍𝒚𝒔 ┈┈┈┈┈┈┈┈

𓂃 𓈒 /target
𓂃 𓈒 /mark
𓂃 𓈒 /fcked
═══════════════════
🎐 𝑶𝒘𝒏𝒆𝒓'𝒔 ┈┈┈┈┈┈┈┈

𓂃 𓈒 /join
𓂃 𓈒 /bye
𓂃 𓈒 /promote
𓂃 𓈒 /addsudo
𓂃 𓈒 /delsudo
𓂃 𓈒 /sudo
═══════════════════
🎐 𝑪𝒐𝒏𝒕𝒓𝒐𝒍𝒔 ┈┈┈┈┈┈┈┈

𓂃 𓈒 /stopnc
𓂃 𓈒 /stopspam
𓂃 𓈒 /stopslide
𓂃 𓈒 /stopall
𓂃 𓈒 /delay [0.05 ~ 0.005]

﹌﹌﹌﹌ꫀꪀ꠹ꪮꪗ 💗⃝🌕﹌﹌﹌﹌
"""

NON_SUDO_HELP = "𝐅ꭈׁׅꫀꪖƙׁׅ֑ꪗ ꯱ׁׅ֒ꫀׁׅܻ յׁׅɑׁׅ֮ ƙׁׅ֑ꭈׁׅ ꯱ׁׅ֒υׁׅժׁׅ݊ᨵׁׅ ᥣׁׅ֪ꫀׁׅܻ ℘hׁׅ֮ᥣׁׅ֪ꫀׁׅܻ ⨍ꪱׁׅꭈׁׅ ϐׁׅ֒ɑׁׅ֮ɑׁׅ֮tׁׅ ƙׁׅ֑ꭈׁׅ 𓏲 ๋࣭ ࣪ ˖🎐"

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner_or_sudo(update.effective_user.id):
        await update.message.reply_text(HELP_MENU)
    else:
        await update.message.reply_text(NON_SUDO_HELP)

# ---------------------------
# BOT SETUP
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    # Fun commands
    app.add_handler(CommandHandler("freaky", freaky))
    app.add_handler(CommandHandler("zip", zip))
    app.add_handler(CommandHandler("lytic", lytic))
    # NC commands
    app.add_handler(CommandHandler("signsnc", signsnc))
    app.add_handler(CommandHandler("facenc", facenc))
    app.add_handler(CommandHandler("timenc", timenc))
    app.add_handler(CommandHandler("flagnc", flagnc))
    app.add_handler(CommandHandler("emojinc", emojinc))
    app.add_handler(CommandHandler("wordnc", wordnc))
    app.add_handler(CommandHandler("customnc", customnc))
    app.add_handler(CommandHandler("lovenc", lovenc))
    app.add_handler(CommandHandler("meownc", meownc))
    app.add_handler(CommandHandler("trialnc", trialnc))
    app.add_handler(CommandHandler("stopnc", stopnc))
    # Spam commands
    app.add_handler(CommandHandler("cover", cover))
    app.add_handler(CommandHandler("arrow", arrow))
    app.add_handler(CommandHandler("matrix", matrix))
    app.add_handler(CommandHandler("custom", custom))
    app.add_handler(CommandHandler("stopspam", stopspam))
    # Slider commands
    app.add_handler(CommandHandler("target", target))
    app.add_handler(CommandHandler("mark", mark))
    app.add_handler(CommandHandler("fcked", fcked))
    app.add_handler(CommandHandler("stopslide", stopslide))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("delay", delay))
    # Join, Promote, Bye (owner only)
    app.add_handler(CommandHandler("join", join))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("bye", bye))
    # Sudo management (owner only)
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("sudo", sudo))
    # Help command
    app.add_handler(CommandHandler("help", help_cmd))
    # Auto‑greet and admin promotion handler
    app.add_handler(ChatMemberHandler(handle_my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    return app

async def run_all_bots():
    global bots_info
    for token in TOKENS:
        try:
            app = build_app(token)
            await app.initialize()
            # Get bot info
            bot = app.bot
            me = await bot.get_me()
            bots_info.append({
                'id': me.id,
                'username': me.username,
                'bot': bot
            })
            apps.append(app)
            bots.append(bot)
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Bot started: @{me.username} (ID: {me.id})")
        except Exception as e:
            print(f"❌ Failed to start bot with token {token[:10]}: {e}")

    print(f"\n🎉 FREAKY BOT is running with {len(bots)} bots!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"⚡ Default speed: {GLOBAL_DELAY:.3f}s per action")
    print("="*40)

    # Keep running forever
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("\n" + "="*40)
    print("      FREAKY BOT - SYSTEM LOCK")
    print("="*40)
    try:
        pw = getpass.getpass("🔑 ENTER ACCESS PASSWORD: ")
    except:
        pw = input("🔑 ENTER ACCESS PASSWORD: ")

    # 🔐 Password set to LVXFREAKY.PY
    if pw != "LVXFREAKY.PY":
        print("\n❌ ACCESS DENIED")
        sys.exit(1)

    print("\n✅ ACCESS GRANTED! STARTING BOTS...\n")
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")
    except Exception as e:
        print(f"❌ Error: {e}")
    