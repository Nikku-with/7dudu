# FREAKY_GAZE_BOT.py - WORKING VERSION
import asyncio
import json
import os
import sys
import getpass
import random
from telegram import Update
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes
import logging

# ---------------------------
# YOUR 10 BOT TOKENS
# ---------------------------
TOKENS = [ ]

# ---------------------------
# OWNER & SUDO CONFIG
# ---------------------------
OWNER_ID = 
SUDO_FILE = "sudo_users.json"

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
nc_tasks = {}
spam_tasks = {}
slider_tasks = {}
GLOBAL_DELAY = 0.05

# Custom Messages
NC_START_MSG = "✅ NC started"
NC_STOP_MSG = "🛑 NC stopped"
SPAM_START_MSG = "✅ Spam started"
SPAM_STOP_MSG = "🛑 Spam stopped"
SLIDER_START_MSG = "✅ Slider started"
SLIDER_STOP_MSG = "🛑 Slider stopped"
ADDSUDO_MSG = "✅ Added sudo user"
NON_SUDO_MSG = "𝐊𝐲𝐮 𝐫𝐞 𝐠𝐚𝐫𝐞𝐞𝐛 𝐚𝐠𝐲𝐚 𝐟𝐫𝐞𝐞 𝐤𝐚 𝐦𝐚𝐚𝐥 𝐮𝐬𝐞 𝐤𝐫𝐧𝐞 ~ 😂"
HI_MSG = "𝐇𝐧 𝐛𝐡𝐚𝐢 ! 🫶🏻"
LEAVE_MSG = "𝐒𝐚𝐲𝐨𝐧𝐚𝐫𝐚 ~ 🚶🏻"
PROMOTE_MSG = "𝐀ᴅᴍɪɴ ~ 😇"

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
        await update.message.reply_text(NON_SUDO_MSG)
    return wrapper

# ---------------------------
# NC PATTERNS
# ---------------------------
MOMNC_EMOJIS = ["🎨","🫟","🖌️","🖍️","🪡","🧵","🧶","🎹","🎷","🎺","🪊","🎸","🪕","🎻","🪉","🪘","🥁","🪇","🪈","🪗","🎤","🎧","🎙️","🎚️","🎛️","📼","📻","📺","📹","📽️","🎥","🎞️","🎭","🎫","🎟️"]

BAAPNC_EMOJIS = ["🦁","🐯","🐱","🐶","🐺","🐻","🐻‍❄️","🐨","🐼","🐹","🐭","🐰","🦊","🐮","🐷","🐽","🐗","🦄","🐴","🫎","🐲","🦎","🐉","🦖","🦕","🐢","🐊","🐍","🐸"]

DEADNC_EMOJIS = ["🤨","🧐","😒","🙄","😮‍💨","😤","😠","😡","🤬","😞","😓","😟","😥","😢","☹️","🙁","🫤","😕","😵","😵‍💫","🫨","🥴","🥵","🥶","🤢","🤮","🫩","😴","😪","🤧","🤒","🤕","😷","🤥","😈","👿","👻","💀","☠️","🤖","👹","👺","☃️","⛄","👽","👾","⚰️","🎪","💢","🕋","🪃","🥤"]

FSTYNC_EMOJIS = ["❤️","🧡","💛","💚","🩵","💙","💜","🤎","🖤","🩶","🤍","🩷","💘","💝","💖","💗","💓","💞","💕","💌","💟","♥️","❣️","❤️‍🩹","💔","❤️‍🔥"]

RUNCN_EMOJIS = ["🏇🏻","🏌🏻","🤹🏻","🤺","⛷️","🏂🏻","🪂","🏄🏻","🚣🏻","🏊🏻","🤽🏻","🧜🏻","🧚🏻","🧞","🧝🏻","🧙🏻","🧛🏻","🧟","🧌","🫈","🦸🏻","🦹🏻","🧑🏻‍🎄","🥷🏻","💂🏻","🫅🏻","🧑🏻‍🍳","🧑🏻‍🚒"]

NCHU_WORDS = [
    "𝙏𝙈𝙆𝙁𝘽", "𝙍𝙉𝘿𝙔", "𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝙈𝘼𝙍 𝙂𝙔𝙄", "𝙏𝘽𝙆𝘾",
    "𝙏𝙈𝙆𝘾 𝙈𝙄𝙀 𝙈𝘼𝙂𝙂𝙄𝙀", "𝙏𝘽𝙆𝘽 𝙈𝙄𝙀 𝙇𝙉𝘿", "𝙏𝙀𝙍𝙄 𝙂𝙉𝘿 𝙈𝙄𝙀 𝙆𝙐𝙏𝙏𝘼",
    "𝙂𝙐𝙇𝘼‌𝙈𝙄 𝙆𝙍", "𝙆𝙀𝙀𝘿𝙀", "𝘼𝙐𝙆𝘼𝘼𝙏 𝘽𝙉𝘼", "𝙂𝘼𝙍𝙀𝙀𝘽", "𝘽𝙎𝘿𝙆", "𝘾𝙃𝙈𝙍"
]

SKYNC_SIGNS = ["⋆˚꩜｡",".✦ ݁˖","𝜗ৎ","݁ ˖Ი𐑼⋆","⊹ ࣪ ˖","⋆˚࿔","𑣲","˚˖𓍢ִ໋❀","♡","ᯓ★",".☘︎ ݁˖","⋆.𐙚   ","₊˚⊹ ᰔ",".⋆♱","𖦹"]

# ---------------------------
# SLIDER TEXTS
# ---------------------------
BULK_TEXTS = [
    "𝙏𝙈𝙆𝘾 𝙈𝙄𝙀 𝙆𝙐𝙏𝙏𝙀 𝙆𝘼 𝙇𝙉𝘿 💢",
    "𝙊𝙔𝙀 𝙏𝙐 𝙈𝘼𝙍𝘼 𝙆𝘼𝙄𝙎𝙀 𝙂𝘼𝙍𝙀𝙀𝘽 𝘾𝙑𝙍 𝙆𝙍🥤",
    "𝙊𝙔𝙀 𝙏𝙀𝙍𝙄 𝙈𝘼𝙐𝙎𝙄 𝙆𝙄 𝘾𝙃𝙐𝙏 𝙈𝘼𝘼𝙍 𝘿𝙐 𝙍𝙊𝙔𝙀𝙂𝘼 𝙏𝙊 𝙉𝘼‌𝙄 ?😏",
    "𝙏𝙈𝙆𝘾 𝙍𝙉𝘿𝙔 𝙆𝙀 𝙂𝙐𝙇𝘼𝙈𝙄 𝙆𝙍 𝘾𝙃𝙐𝙋 𝘾𝙃𝘼𝙋😡",
    "𝙊𝙔𝙀 𝘽𝙎𝘿𝙆 𝙃𝘼𝙒𝘼𝘽𝘼𝘼𝙕 𝙏𝘼𝙏𝙏𝙀 𝘽𝙃𝘼𝙂 𝙈𝙏😆"
]

GOOGLE_TEXTS = [
    "𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙐𝘾𝙆 𝙃𝙄𝙎 𝙈𝙊𝙈 𝙋𝙍𝙊𝙋𝙀𝙍𝙇𝙔",
    "𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝘼𝙎𝙆 𝙃𝙄𝙈 𝙏𝙊 𝘾𝙊𝙑𝙀𝙍 𝙃𝙄𝙎 𝙈𝙊𝙈'𝙎 𝘼𝙎𝙎",
    "𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙄𝙓 𝙈𝙔 𝘼‌𝙋𝙋𝙊𝙄𝙉𝙏𝙈𝙀𝙉𝙏 𝙒𝙄𝙏𝙃 𝙃𝙄𝙎 𝙎𝙄𝙎",
    "𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝙁𝙐𝘾𝙆 𝘼𝙉𝘿 𝙏𝙃𝙍𝙊𝙒 𝙏𝙃𝙄𝙎 𝙂𝘼𝙍𝙀𝙀𝘽 𝙎𝙊𝙉",
    "𝙃𝙀𝙔 𝙂𝙊𝙊𝙂𝙇𝙀 𝘿𝙊 𝙉𝙊𝙏 𝙎𝙏𝙊𝙋 𝙁𝙐𝘾𝙆𝙄𝙉𝙂 𝙈𝙔 𝙂𝙐𝙇𝘼‌𝙈"
]

AIHAI_TEXTS = [
    "𝙂𝙀𝙈𝙄𝙉𝙄 𝙎𝘼𝙄𝘿 {text} 𝙄𝙎 𝙍𝙉𝘿𝙔 𝙋𝙐𝙏𝙍𝘼",
    "𝙋𝙀𝙍𝙋𝙇𝙀𝙓𝙄𝙏𝙔 𝙎𝘼𝙄𝘿 {text} 𝙄𝙎 𝙂𝙐𝙇𝘼𝙈",
    "𝙂𝙍𝙊𝙆 𝘼𝙄 𝙎𝘼𝙄𝘿 {text} 𝙄𝙎 𝙂𝘼𝙍𝙀𝙀𝘽",
    "𝘽𝙊𝙏 𝙎𝘼‌𝙄𝘿 {text} 𝙄𝙎 𝘾𝙃𝙐𝘿𝘼𝙆𝘼𝘿",
    "𝙈𝙊𝘿𝙄 𝙎𝘼‌𝙄𝘿 {text} 𝙄𝙎 𝙋𝙊𝙇𝙀 𝘿𝘼𝙉𝘾𝙀𝙍",
    "𝙏𝙍𝙐𝙈𝙋 𝙎𝘼𝙄𝘿 {text} 𝙄𝙎 𝘽𝙇𝙊𝙊𝘿 𝙈𝙊𝙏𝙃𝙀𝙍𝙁*\"𝘾𝙆𝙀𝙍"
]

# ---------------------------
# SPAM PATTERNS
# ---------------------------
ENTRY_PATTERN = "༺   {text} 🤭  ༻  𝐊𝐎 𝐗𝐎𝐃𝐓𝐄 𝐇𝐔𝐄 𝐄𝐍𝐓𝐑𝐘༒ =====================================================================================🖤༺"
GALAXY_PATTERN = "{text}         -चूदके/दफन-         𝐂 𝐇 𝐔 𝐓     𝗣 𝗛 𝗔 𝗗 𝗨    𝐓 𝐄 𝐑 𝐈  ✧･ﾟ: *･ﾟ:⋆✧･ﾟ:*⋆｡ﾟ｡✧⋆· ━━━━━━━━      𝐋 𝐍 𝟗   𝐋𝐄"
CVRIE_PATTERN = "ㅤ→ {text} KI माँ को चोद के फेकl KUTTE KE TARAH ༺♡༻🤍彡彡              彡                                  {text} CHUD KE  DAFAN  彡彡彡彡彡彡彡        _/𒀸💙 𓂃𓈒ㅤ"
YOURS_EMOJIS = ["🏝️","🏖️","🌊","🌬️","❄️","🌀","🌪️","⚡","☔","🌈","💧","☁️","🌨️","🌧️","🌩️","⛈️","🌦️","🌥️","⛅","🌤️","☀️","🌞","🌝","🌚","🌜","🌛","🌙","⭐","🌟","✨","🕳️","🪐","🌍","🌎","🌏","🌫️","🌠","🌌","☄️","🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]

REPEAT_COUNT = 10

# ---------------------------
# NC LOOP FUNCTIONS (FIXED)
# ---------------------------
async def momnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = MOMNC_EMOJIS[i % len(MOMNC_EMOJIS)]
            new_title = f"{text} 𝙈𝙊𝙏𝙃𝙀𝙍𝙁𝙐𝘾𝙆𝙀𝙍 ´ཀ` <{emoji}>"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def baapnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = BAAPNC_EMOJIS[i % len(BAAPNC_EMOJIS)]
            new_title = f"{text} 𝙍𝙉𝘿𝙔𝙆𝙀 𝘽𝘼𝘼𝙋 𝘽𝙊𝙇 <{emoji}ྀི>"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def deadnc_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = DEADNC_EMOJIS[i % len(DEADNC_EMOJIS)]
            new_title = f"{text} 𝙈𝘼𝙍 𝙂𝙔𝘼 𝙆𝙔𝘼 𝙍𝙉𝘿 ᯓ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def fstync_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = FSTYNC_EMOJIS[i % len(FSTYNC_EMOJIS)]
            new_title = f"{text} 𝘾𝙃𝙐𝘿𝘼𝙄 केन्द्र ^ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def runcn_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = RUNCN_EMOJIS[i % len(RUNCN_EMOJIS)]
            new_title = f"{text} 𝘽𝙃𝘼𝙂𝘼 𝙆𝘼𝙄𝙎𝙀 𝙋𝙄𝙇𝙇𝙀 𑁍ࠬܓ {emoji}"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def nchu_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            word = NCHU_WORDS[i % len(NCHU_WORDS)]
            new_title = f"{text} {word} ˚˖𓍢ִ໋❀"
            await bot.set_chat_title(chat_id, new_title)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

async def skync_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            sign = SKYNC_SIGNS[i % len(SKYNC_SIGNS)]
            new_title = f"{text} જ⁀➴ <{sign}>"
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
# NC COMMAND HANDLERS
# ---------------------------
@sudo_only
async def momnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /momnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(momnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(NC_START_MSG)

@sudo_only
async def baapnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /baapnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(baapnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(NC_START_MSG)

@sudo_only
async def deadnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /deadnc <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(deadnc_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(NC_START_MSG)

@sudo_only
async def fstync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /fstync <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(fstync_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(NC_START_MSG)

@sudo_only
async def runcn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /runcn <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(runcn_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(NC_START_MSG)

@sudo_only
async def nchu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /nchu <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(nchu_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(NC_START_MSG)

@sudo_only
async def skync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /skync <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(skync_loop(b, chat_id, text)) for b in bots]
    nc_tasks[chat_id] = tasks
    await update.message.reply_text(NC_START_MSG)

# ---------------------------
# SPAM COMMAND HANDLERS
# ---------------------------
async def entry_loop(bot, chat_id, text):
    message = (ENTRY_PATTERN.format(text=text) + "\n") * REPEAT_COUNT
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

@sudo_only
async def entry(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /entry <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(entry_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(SPAM_START_MSG)

async def galaxy_loop(bot, chat_id, text):
    message = (GALAXY_PATTERN.format(text=text) + "\n") * REPEAT_COUNT
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

@sudo_only
async def galaxy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /galaxy <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(galaxy_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(SPAM_START_MSG)

async def cvrle_loop(bot, chat_id, text):
    message = (CVRIE_PATTERN.format(text=text) + "\n") * REPEAT_COUNT
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

@sudo_only
async def cvrle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /cvrle <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(cvrle_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(SPAM_START_MSG)

async def yours_loop(bot, chat_id, text):
    i = 0
    while True:
        try:
            emoji = YOURS_EMOJIS[i % len(YOURS_EMOJIS)]
            message = f"{text} {emoji}"
            await bot.send_message(chat_id, message)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

@sudo_only
async def yours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /yours <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(yours_loop(b, chat_id, text)) for b in bots]
    spam_tasks[chat_id] = tasks
    await update.message.reply_text(SPAM_START_MSG)

# ---------------------------
# SLIDER COMMAND HANDLERS
# ---------------------------
async def bulk_loop(bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            await bot.send_message(chat_id, BULK_TEXTS[i % len(BULK_TEXTS)], reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

@sudo_only
async def bulk(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start bulk!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(bulk_loop(b, chat_id, target_msg_id)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text(SLIDER_START_MSG)

async def google_loop(bot, chat_id, target_msg_id):
    i = 0
    while True:
        try:
            await bot.send_message(chat_id, GOOGLE_TEXTS[i % len(GOOGLE_TEXTS)], reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)

@sudo_only
async def google(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start google!")
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(google_loop(b, chat_id, target_msg_id)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text(SLIDER_START_MSG)

async def aihai_loop(bot, chat_id, target_msg_id, text):
    i = 0
    while True:
        try:
            msg = AIHAI_TEXTS[i % len(AIHAI_TEXTS)].format(text=text)
            await bot.send_message(chat_id, msg, reply_to_message_id=target_msg_id)
            i += 1
            await asyncio.sleep(GLOBAL_DELAY)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except Exception:
            await asyncio.sleep(1)


@sudo_only
async def aihai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("❌ Usage: /aihai <text> (reply to a message)")
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a message to start aihai!")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    target_msg_id = update.message.reply_to_message.message_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
    tasks = [asyncio.create_task(aihai_loop(b, chat_id, target_msg_id, text)) for b in bots]
    slider_tasks[chat_id] = tasks
    await update.message.reply_text(SLIDER_START_MSG)

# ---------------------------
# CONTROL COMMANDS
# ---------------------------
@sudo_only
async def stopnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
        await update.message.reply_text(NC_STOP_MSG)
    else:
        await update.message.reply_text("❌ No NC running in this chat.")

@sudo_only
async def stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
        await update.message.reply_text(SPAM_STOP_MSG)
    else:
        await update.message.reply_text("❌ No spam running in this chat.")

@sudo_only
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
        del slider_tasks[chat_id]
        await update.message.reply_text(SLIDER_STOP_MSG)
    else:
        await update.message.reply_text("❌ No slider running in this chat.")

@sudo_only
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    if chat_id in slider_tasks:
        for task in slider_tasks[chat_id]:
            task.cancel()
        del slider_tasks[chat_id]
    await update.message.reply_text("🛑 All activities stopped.")

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
# FUN COMMANDS
# ---------------------------
@sudo_only
async def hi(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(HI_MSG)

# ---------------------------
# OWNER COMMANDS
# ---------------------------
@owner_only
async def addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("❌ Reply to a user's message")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(ADDSUDO_MSG)

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

@owner_only
async def promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    promoter_bot = context.bot
    promoter_id = promoter_bot.id
    other_bots = [b for b in bots if b.id != promoter_id]
    if not other_bots:
        await update.message.reply_text("No other bots to promote.")
        return
    permissions = {
        'can_change_info': True, 'can_post_messages': True, 'can_edit_messages': True,
        'can_delete_messages': True, 'can_invite_users': True, 'can_restrict_members': True,
        'can_pin_messages': True, 'can_promote_members': True, 'can_manage_video_chats': True,
        'can_manage_chat': True
    }
    promoted_count = 0
    for bot in other_bots:
        try:
            await promoter_bot.promote_chat_member(chat_id=chat_id, user_id=bot.id, **permissions)
            promoted_count += 1
        except Exception as e:
            logging.warning(f"Failed to promote bot {bot.id}: {e}")
    await update.message.reply_text(f"Promotion completed. {promoted_count} bots promoted.")

@owner_only
async def leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    await update.message.reply_text("👋 Bots are leaving...")
    for bot in bots:
        try:
            await bot.send_message(chat_id, LEAVE_MSG)
            await bot.leave_chat(chat_id)
        except Exception as e:
            logging.warning(f"Bot {bot.id} could not leave: {e}")

# ---------------------------
# HELP COMMAND
# ---------------------------
HELP_MENU = """
𝐓ʜᴇ  𝐅ʀᴇᴀᴋʏ  𝐆ᴀᴢᴇ ~ ✨
═══════════════════
𝐍ᴄ 𝐒ᴇᴄᴛɪᴏɴ -------
~ /momnc {text}
~ /baapnc {text}
~ /deadnc {text}
~ /fstync {text}
~ /runcn {text}
~ /nchu {text}
~ /skync {text}
═══════════════════
𝐑ᴇᴘʟʏ 𝐒ᴇᴄᴛɪᴏɴ ------
~ /bulk
~ /google
~ /aihai {text}
═══════════════════
𝐒ᴘᴀᴍ 𝐒ᴇᴄᴛɪᴏɴ -------
~ /entry {text}
~ /galaxy {text}
~ /cvrle {text}
~ /yours {text}
═══════════════════
𝐎ᴡɴᴇʀ 𝐎ɴʟʏ ------
~ /addsudo 
~ /delsudo 
~ /sudo 
~ /promote 
~ /leave
═══════════════════
𝐂ᴏɴᴛʀᴏʟs -------
~ /stopnc
~ /stopspam 
~ /stopslide 
~ /stopall 
~ /delay [0.05 - 0.005]
~ /hi
═══════════════════
𝐄ɴᴊᴏʏ ♡⸝⸝
"""

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_owner_or_sudo(update.effective_user.id):
        await update.message.reply_text(HELP_MENU)
    else:
        await update.message.reply_text(NON_SUDO_MSG)

# ---------------------------
# BOT SETUP
# ---------------------------
def build_app(token):
    app = Application.builder().token(token).build()
    # NC Commands
    app.add_handler(CommandHandler("momnc", momnc))
    app.add_handler(CommandHandler("baapnc", baapnc))
    app.add_handler(CommandHandler("deadnc", deadnc))
    app.add_handler(CommandHandler("fstync", fstync))
    app.add_handler(CommandHandler("runcn", runcn))
    app.add_handler(CommandHandler("nchu", nchu))
    app.add_handler(CommandHandler("skync", skync))
    # Spam Commands
    app.add_handler(CommandHandler("entry", entry))
    app.add_handler(CommandHandler("galaxy", galaxy))
    app.add_handler(CommandHandler("cvrle", cvrle))
    app.add_handler(CommandHandler("yours", yours))
    # Slider Commands
    app.add_handler(CommandHandler("bulk", bulk))
    app.add_handler(CommandHandler("google", google))
    app.add_handler(CommandHandler("aihai", aihai))
    # Control Commands
    app.add_handler(CommandHandler("stopnc", stopnc))
    app.add_handler(CommandHandler("stopspam", stopspam))
    app.add_handler(CommandHandler("stopslide", stopslide))
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("delay", delay))
    # Fun Commands
    app.add_handler(CommandHandler("hi", hi))
    # Owner Commands
    app.add_handler(CommandHandler("addsudo", addsudo))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("sudo", sudo))
    app.add_handler(CommandHandler("promote", promote))
    app.add_handler(CommandHandler("leave", leave))
    # Help
    app.add_handler(CommandHandler("help", help_cmd))
    return app

async def run_all_bots():
    for token in TOKENS:
        try:
            app = build_app(token)
            apps.append(app)
            bots.append(app.bot)
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            print(f"🚀 Bot started: {token[:10]}...")
        except Exception as e:
            print(f"❌ Failed to start bot: {e}")

    print(f"\n🎉 FREAKY GAZE BOT is running with {len(bots)} bots!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"⚡ Default speed: {GLOBAL_DELAY:.3f}s per action")
    print("="*40)
    await asyncio.Event().wait()

if __name__ == "__main__":
    print("\n" + "="*40)
    print("      FREAKY GAZE BOT - SYSTEM LOCK")
    print("="*40)
    try:
        pw = getpass.getpass("🔑 ENTER ACCESS PASSWORD: ")
    except:
        pw = input("🔑 ENTER ACCESS PASSWORD: ")

    if pw != "FREAKYGAZE.PY":
        print("\n❌ ACCESS DENIED")
        sys.exit(1)

    print("\n✅ ACCESS GRANTED! STARTING BOTS...\n")
    try:
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped by user.")
    except Exception as e:
        print(f"❌ Error: {e}")