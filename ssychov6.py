#ssychogawd_v6_bot_system
import asyncio
import json
import os
import random
import time
from datetime import datetime
from telegram import Update, InputSticker, Sticker
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
import logging
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import itertools

# ---------------------------
# CONFIG
# ---------------------------
TOKENS = [
    
]


OWNER_ID = 8773893167
SUDO_FILE = "8773893167"

# ---------------------------
# TEXTS (UNCHANGED)
# ---------------------------
RAID_TEXTS = [
"ᴛᴇʀᴀ ʙᴀᴀᴘ ꜱꜱʏᴄʜᴏ :♪🧃",
  "ʟᴀɴɢᴅᴇ ᴄʜᴜᴅ :♪🧃", 
"ᴄʜᴜᴅᴀʏɪ ᴋᴀ ʙᴀᴋʀᴀ :♪🧃", 
"ʙʜɴ ᴋᴇ ʙʜsᴅᴇ :♪🧃", 
"ᴄʜᴜᴛᴋᴀ :♪🧃", 
"ʀᴀɴᴅᴀʟ ᴘᴜᴛʀ :♪🧃", 
"ᴜᴛʜ ᴘɪʟʟᴇ :♪🧃", 
"ᴛᴇʀᴀ ʙᴀᴀᴘ ꜱꜱʏᴄʜᴏ :♪🧃",
"ᴄʜᴜᴅᴡᴀʟɪ ᴍᴀᴀ :♪🧃",
"ᴛᴍᴋᴄ :♪🧃",
"ᴋɪ ᴍᴏsɪ ᴄᴜᴅᴇ :♪🧃",
"ʀɴᴅʏᴋᴀ :♪🧃",
"ʟᴀɴɢᴅᴇ ᴄʜᴜᴅ :♪🧃", 
"ᴄʜᴜᴅᴀʏɪ ᴋᴀ ʙᴀᴋʀᴀ :♪🧃", 
"ʙʜɴ ᴋᴇ ʙʜsᴅᴇ :♪🧃", 
"ᴄʜᴜᴛᴋᴀ :♪🧃", 
"ᴛᴇʀᴀ ʙᴀᴀᴘ ꜱꜱʏᴄʜᴏ :♪🧃",
"ʀᴀɴᴅᴀʟ ᴘᴜᴛʀ :♪🧃", 
"ᴜᴛʜ ᴘɪʟʟᴇ :♪🧃", 
"ᴄʜᴜᴅᴡᴀʟɪ ᴍᴀᴀ :♪🧃",
"ᴛᴍᴋᴄ :♪🧃",
"ᴋɪ ᴍᴏsɪ ᴄᴜᴅᴇ :♪🧃",
"ʀɴᴅʏᴋᴀ :♪🧃",
"ᴛᴇʀᴀ ʙᴀᴀᴘ ꜱꜱʏᴄʜᴏ :♪🧃",
"ʟᴀɴɢᴅᴇ ᴄʜᴜᴅ :♪🧃", 
"ᴄʜᴜᴅᴀʏɪ ᴋᴀ ʙᴀᴋʀᴀ :♪🧃", 
"ʙʜɴ ᴋᴇ ʙʜsᴅᴇ :♪🧃", 
"ᴄʜᴜᴛᴋᴀ :♪🧃", 
"ʀᴀɴᴅᴀʟ ᴘᴜᴛʀ :♪🧃", 
"ᴜᴛʜ ᴘɪʟʟᴇ :♪🧃", 
"ᴄʜᴜᴅᴡᴀʟɪ ᴍᴀᴀ :♪🧃",
"ᴛᴍᴋᴄ :♪🧃",
"ᴛᴇʀᴀ ʙᴀᴀᴘ ꜱꜱʏᴄʜᴏ :♪🧃",
"ᴋɪ ᴍᴏsɪ ᴄᴜᴅᴇ :♪🧃",
"ʀɴᴅʏᴋᴀ :♪🧃",
]

SLIDE_TEXTS = [
   " 🥴ɴʜɪ sᴜɴᴜɢᴀ ᴛᴇʀɪ ᴍᴀʏᴀᴠɪ ᴠᴀɪʏsʜʏᴀ ᴋᴇ ᴸᴬᴰᴷᴱ😖",
    " 🤮ᴛᴜ ʟᴀᴅᴇɢᴀ ɢᴏʟ ɢᴀᴘᴘᴇʀ ᴡᴀʟᴇ ᴋᴇ ʟᴀᴅᴋᴇ😂",
    " 😂👏🏻ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴀᴅᴅɪ ᴄʜᴜʀᴀ ʟɪ😹",
    "🪱ᴛᴜ ʟᴀssɪ ᴮᴷᴸ🪱",
    " 🌚 ᴛᴇʀɪ ʙʜᴇɴ ᴋᴀ ʙʀᴀ sɪᴢᴇᴮᴬᵀᴬ ᴶᴸᴰᴵ🌚",
    " ♾️ᴛᴇʀᴇ ᵀᴼᵀᴬᴸ ᴮᴬᴬᴾ ᴳᴵᴺ ᴷᴱ ᴮᴬᵀᴬ♾️",
    " 🤣🫵🏻ᴛᴜ ʟᴜɴ ᴋɪ ᴛᴏᴘɪ ɴᴏᴡ sᴀʏ ssʏᴄʜᴏ ᴼᴾ❤️‍🔥",
    " 🧑🏿‍🦽‍➡️ʟᴀɴɢᴅᴇ ʙʜᴀᴀɢᴷᴱ ᴰᴵᴷᴴᴬ🏃🏿",
    " 💦ᴛᴇʀɪ ʙʜᴇɴ sᴘᴇʀᴍ ᶜᴼᴸᴸᴱᶜᵀᴼᴿ💦",
    " 🃏ᴄʜᴀᴘᴘᴀʟᶜᴴᴼᴿ🤡",
    " 🤭ᴛᴇʀɪ ʙᴜᴀ sᴇxᵂᴼᴿᴷᴱᴿ🤭",
    " 😖ᴛᴇʀᴀ ᴅᴀᴅᴀ ᴬᴺᴳᴿᴱᶻᴼ ᴋᴀ ɴᴏᴋᴀʀ👞",
]

nc2_TEXTS = [
   "💔", "😖", "🦋", "🤍", "🔥", "⁉️", "😞", "👾", "🤤", "😋", "😛", "👌", "☺️", "😝", "😕", "🙂", "🤛", "🤜", "🤚", "👋", "🫶", "🙌", "👐", "✍️", "🤟", "🤲", "🙏", "💅", "🩷", "🧡", "💛", "💚", "❤️", "🩹", "❣️", "💕", "💞", "💟", "💝", "💘", "💖", "💓", "💗", "💌", "💢", "💥", "💤", "💦", "💨", "❤️‍🔥", "☮️", "🗿", "👑", "🩵", "🔱", "🌷", "❤️‍🩹", "👞", "🤮", "🤣", "😭", "🥺", "😁", "👿", "🚀", "🥹", "😬", "🙄", "😎", "👽", "👾", "😈", "👹", "🤡", "🙀", "🐒", "🦁", "🐅", "🦓", "🐮", "🐉", "🦖", "🦕", "🐲", "🦎", "🐴","💔", "😖", "🦋", "🤍", "🔥", "⁉️", "😞", "👾", "🤤", "😋", "😛", "👌", "☺️", "😝", "😕", "🙂", "🤛", "🤜", "🤚", "👋", "🫶", "🙌", "👐", "✍️", "🤟", "🤲", "🙏", "💅", "🩷", "🧡",
]

nc3_EMOJIS = [
   "💔", "😖", "🦋", "🤍", "🔥", "⁉️", "😞", "👾", "🤤", "😋", "😛", "👌", "☺️", "😝", "😕", "🙂", "🤛", "🤜", "🤚", "👋", "🫶", "🙌", "👐", "✍️", "🤟", "🤲", "🙏", "💅", "🩷", "🧡", "💛", "💚", "❤️", "🩹", "❣️", "💕", "💞", "💟", "💝", "💘", "💖", "💓", "💗", "💌", "💢", "💥", "💤", "💦", "💨", "❤️‍🔥", "☮️", "🗿", "👑", "🩵", "🔱", "🌷", "❤️‍🩹", "👞", "🤮", "🤣", "😭", "🥺", "😁", "👿", "🚀", "🥹", "😬", "🙄", "😎", "👽", "👾", "😈", "👹", "🤡", "🙀", "🐒", "🦁", "🐅", "🦓", "🐮", "🐉", "🦖", "🦕", "🐲", "🦎", "🐴","💔", "😖", "🦋", "🤍", "🔥", "⁉️", "😞", "👾", "🤤", "😋", "😛", "👌", "☺️", "😝", "😕", "🙂", "🤛", "🤜", "🤚", "👋", "🫶", "🙌", "👐", "✍️", "🤟", "🤲", "🙏", "💅", "🩷", "🧡","💔", "😖", "🦋", "🤍", "🔥", "⁉️", "😞", "👾", "🤤", "😋", "😛", "👌", "☺️", "😝", "😕", "🙂", "🤛", "🤜", 
]

# ---------------------------
# GLOBAL STATE
# ---------------------------
if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r") as f:
            _loaded = json.load(f)
        SUDO_USERS = set(int(x) for x in _loaded)
    except Exception:
        SUDO_USERS = {OWNER_ID}
else:
    SUDO_USERS = {OWNER_ID}

def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)


group_tasks = {}  
nc_tasks = {}   
nc2_tasks = {} 
nc3_tasks = {}  
spam_tasks = {}
flood_tasks = {}
react_tasks = {}
slide_targets = set()
slidespam_targets = set()

apps, bots = [], []


delay = 0.005  
spam_delay = 0.25
flood_delay = 0.05
nc2_delay = 0.0025  
nc3_delay = 0.001    


executor = ThreadPoolExecutor(max_workers=100)
lock = Lock()

# Pre-computed iterators for maximum speed
nc3_cycle = itertools.cycle(nc3_EMOJIS)
nc2_cycle = itertools.cycle(nc2_TEXTS)
raid_cycle = itertools.cycle(RAID_TEXTS)

logging.basicConfig(level=logging.INFO)

# ---------------------------
# DECORATORS
# ---------------------------
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid not in SUDO_USERS:
            await update.message.reply_text("❌ You are not SUDO.")
            return
        return await func(update, context)
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        uid = update.effective_user.id
        if uid != OWNER_ID:
            await update.message.reply_text("❌ Only Owner can do this.")
            return
        return await func(update, context)
    return wrapper

# ---------------------------
# ULTRA-FAST LOOP FUNCTIONS
# ---------------------------
async def ultra_fast_nc(bot, chat_id, base):
    """Ultra-fast NC with pre-computed cycles"""
    i = 0
    while True:
        try:
            text = f"{base} {next(raid_cycle)}"
            await bot.set_chat_title(chat_id, text)
            i += 1
            await asyncio.sleep(delay)
        except Exception as e:
            await asyncio.sleep(0.001)

async def ultra_fast_nc2(bot, chat_id, base):
    """Ultra-fast NC2 with multiple patterns"""
    i = 0
    while True:
        try:
            patterns = [
                f"{base} {next(nc2_cycle)}",
                f"{next(nc2_cycle)} {base}",
                f"{base}{next(nc2_cycle)}",
                f"{next(nc2_cycle)} {base} {next(nc2_cycle)}",
            ]
            text = random.choice(patterns)
            await bot.set_chat_title(chat_id, text)
            i += 1
            await asyncio.sleep(nc2_delay)
        except Exception as e:
            await asyncio.sleep(0.0005)

async def ultra_fast_nc3(bot, chat_id, base):
    """Ultra-fast NC3 with maximum speed"""
    i = 0
    while True:
        try:
            patterns = [
                f"{base} {next(nc3_cycle)}",
                f"{next(nc3_cycle)} {base}",
                f"{base}{next(nc3_cycle)}",
                f"{next(nc3_cycle)} {base} {next(nc3_cycle)}",
                f"{base} {next(nc3_cycle)} {next(nc3_cycle)}",
                f"{next(nc3_cycle)}{next(nc3_cycle)}{base}",
            ]

            text = patterns[i % len(patterns)]
            await bot.set_chat_title(chat_id, text)

            i += 1
            await asyncio.sleep(nc3_delay)

        except Exception as e:
            print(f"NC3 Error: {e}")
            await asyncio.sleep(0.001)

# ---------------------------
# CORE COMMANDS (UNCHANGED)
# ---------------------------
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🌙 ꜱꜱʏᴄʜᴏ ʙᴀᴀᴘ ᴠ6  \nUse /help")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """  ꜱꜱʏᴄʜᴏ ʙᴀᴀᴘ ᴠ6 👑
════════════
[NAME]
/nc <name>
/nc2 <name>
/nc3 <name>
/stopall = nc nc2 nc3
────────────
[SPAM]
/spam <text>
/unspam
────────────
[SLIDE]
/targetslide
/slidespam
/stopslide
/stopslidespam
────────────
[SUDO]
/listsudo
/addson
/delsudo
────────────
[SYSTEM]
/delay <sec>
/stopall
/ping
/admin
/remove
/status
════════════
ꜱꜱʏᴄʜᴏ ʙᴀᴀᴘ ʜᴀɪ 🤍  """
    await update.message.reply_text(help_text)

async def ping_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start = time.time()
    msg = await update.message.reply_text("🏓 Pinging...")
    end = time.time()
    await msg.edit_text(f"🏓 Pong! {int((end-start)*1000)}ms")

# ---------------------------
# ENHANCED NAME CHANGER COMMANDS
# ---------------------------
@only_sudo
async def nc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /nc <name>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Initialize task storage for this chat if not exists
    if chat_id not in nc_tasks:
        nc_tasks[chat_id] = []
    
    # Cancel existing NC tasks for this chat
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
    
    # Start new NC tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(ultra_fast_nc(bot, chat_id, base))
        tasks.append(task)
    
    nc_tasks[chat_id] = tasks
    await update.message.reply_text("ɴᴄ 1 ꜱᴛᴀʀᴛꜱ")

@only_sudo
async def nc2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /nc2 <name>")
    base = " ".join(context.args)
    chat_id = update.message.chat_id
    
    # Initialize task storage for this chat if not exists
    if chat_id not in nc2_tasks:
        nc2_tasks[chat_id] = []
    
    # Cancel existing NC2 tasks for this chat
    if chat_id in nc2_tasks:
        for task in nc2_tasks[chat_id]:
            task.cancel()
    
    # Start new NC2 tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(ultra_fast_nc2(bot, chat_id, base))
        tasks.append(task)
    
    nc2_tasks[chat_id] = tasks
    await update.message.reply_text("ɴᴄ 2 ꜱᴛᴀʀᴛꜱ")

@only_sudo
async def nc3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /nc3 <name>")

    base = " ".join(context.args)
    chat_id = update.message.chat_id

    # Cancel old tasks
    if chat_id in nc3_tasks:
        for task in nc3_tasks[chat_id]:
            task.cancel()

    # Start new tasks
    tasks = []
    for bot in bots:
        task = asyncio.create_task(
            ultra_fast_nc3(bot, chat_id, base)
        )
        tasks.append(task)

    nc3_tasks[chat_id] = tasks

    await update.message.reply_text("ɴᴄ 3 ꜱᴛᴀʀᴛꜱ")

@only_sudo
async def stopnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
        await update.message.reply_text("👑 𝙎𝙎𝙔𝘾𝙃𝙊 𝘽𝘼𝘼𝙋 𝙃𝘼𝙄 👑")
    else:
        await update.message.reply_text("𝙉𝙊 𝙉𝘾 𝙄𝙎 𝙃𝙀𝙍𝙀 ")

@only_sudo
async def stopnc2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc2_tasks:
        for task in nc2_tasks[chat_id]:
            task.cancel()
        del nc2_tasks[chat_id]
        await update.message.reply_text("👑 𝙎𝙎𝙔𝘾𝙃𝙊 𝘽𝘼𝘼𝙋 𝙃𝘼𝙄 👑")
    else:
        await update.message.reply_text("𝙉𝙊 𝙉𝘾 2 𝙄𝙎 𝙃𝙀𝙍𝙀 ")

@only_sudo
async def stopnc3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in nc3_tasks:
        for task in nc3_tasks[chat_id]:
            task.cancel()
        del nc3_tasks[chat_id]
        await update.message.reply_text("👑 𝙎𝙎𝙔𝘾𝙃𝙊 𝘽𝘼𝘼𝙋 𝙃𝘼𝙄 👑")
    else:
        await update.message.reply_text("𝙉𝙊 𝙉𝘾 3 𝙄𝙎 𝙃𝙀𝙍𝙀 ")

# ---------------------------
# SPAM COMMANDS (UNCHANGED)
# ---------------------------
@only_sudo
async def spam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /spam <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
    tasks = []
    for bot in bots:
        task = asyncio.create_task(spam_loop(bot, chat_id, text))
        tasks.append(task)
    spam_tasks[chat_id] = tasks
    await update.message.reply_text("💥 SPAM STARTED!")

@only_sudo
async def unspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
        await update.message.reply_text("🛑 Spam Stopped!")
    else:
        await update.message.reply_text("❌ No active spam")

@only_sudo
async def flood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /flood <text>")
    text = " ".join(context.args)
    chat_id = update.message.chat_id
    if chat_id in flood_tasks:
        for task in flood_tasks[chat_id]:
            task.cancel()
    tasks = []
    for bot in bots:
        task = asyncio.create_task(flood_loop(bot, chat_id, text))
        tasks.append(task)
    flood_tasks[chat_id] = tasks
    await update.message.reply_text("🌊 FLOOD STARTED!")

@only_sudo
async def stopflood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in flood_tasks:
        for task in flood_tasks[chat_id]:
            task.cancel()
        del flood_tasks[chat_id]
        await update.message.reply_text("🛑 Flood Stopped!")
    else:
        await update.message.reply_text("❌ No active flood")

# ---------------------------
# SLIDE COMMANDS (UNCHANGED)
# ---------------------------
@only_sudo
async def targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slide_targets.add(target_id)
    await update.message.reply_text(f"🎯 Target slide added: {target_id}")
    # Start immediate slide spam
    chat_id = update.message.chat_id
    message_id = update.message.reply_to_message.message_id
    for bot in bots:
        try:
            for text in SLIDE_TEXTS[:3]:
                await bot.send_message(
                    chat_id, text, reply_to_message_id=message_id
                )
                await asyncio.sleep(0.1)
        except:
            pass

@only_sudo
async def stopslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slide_targets.discard(target_id)
    await update.message.reply_text(f"🛑 Slide stopped: {target_id}")

@only_sudo
async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slidespam_targets.add(target_id)
    await update.message.reply_text(f"💥 Slide spam started: {target_id}")
    # Start immediate slide spam
    chat_id = update.message.chat_id
    message_id = update.message.reply_to_message.message_id
    for bot in bots:
        try:
            for text in SLIDE_TEXTS:
                await bot.send_message(
                    chat_id, text, reply_to_message_id=message_id
                )
                await asyncio.sleep(0.05)
        except:
            pass

@only_sudo
async def stopslidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slidespam_targets.discard(target_id)
    await update.message.reply_text(f"🛑 Slide spam stopped: {target_id}")

# ---------------------------
# SUDO MANAGEMENT (UNCHANGED)
# ---------------------------
@only_owner
async def addson(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user")
    uid = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    save_sudo()
    await update.message.reply_text(f"SSYCHO Baap added there Son: {uid}")

@only_owner
async def delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user")
    uid = update.message.reply_to_message.from_user.id
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_sudo()
        await update.message.reply_text(f"NIKAL MADARCHOD: {uid}")
    else:
        await update.message.reply_text("AUKAT ME REH LE BSDK ")

@only_sudo
async def listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sudo_list = []
    for uid in SUDO_USERS:
        if uid == OWNER_ID:
            sudo_list.append(f"👑SSYCHO: {uid}")
        else:
            sudo_list.append(f"SONs: {uid}")
    await update.message.reply_text("👑 SUDO Users:\n" + "\n".join(sudo_list))

# ---------------------------
# ENHANCED CONTROL COMMANDS
# ---------------------------
@only_sudo
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    
    # Stop NC
    if chat_id in nc_tasks:
        for task in nc_tasks[chat_id]:
            task.cancel()
        del nc_tasks[chat_id]
    
    # Stop NC2
    if chat_id in nc2_tasks:
        for task in nc2_tasks[chat_id]:
            task.cancel()
        del nc2_tasks[chat_id]
    
    # Stop NC3
    if chat_id in nc3_tasks:
        for task in nc3_tasks[chat_id]:
            task.cancel()
        del nc3_tasks[chat_id]
    
    # Stop Spam
    if chat_id in spam_tasks:
        for task in spam_tasks[chat_id]:
            task.cancel()
        del spam_tasks[chat_id]
    
    # Stop Flood
    if chat_id in flood_tasks:
        for task in flood_tasks[chat_id]:
            task.cancel()
        del flood_tasks[chat_id]
    
    await update.message.reply_text("👑 𝙎𝙎𝙔𝘾𝙃𝙊 𝘽𝘼𝘼𝙋 𝙃𝘼𝙄 👑",)

@only_sudo
async def delay_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global delay, spam_delay, flood_delay, nc2_delay, nc3_delay
    if not context.args:
        return await update.message.reply_text(
            f"⏱ Current delays:\n"
            f"NC: {delay}s\n"
            f"NC2: {nc2_delay}s\n"
            f"NC3: {nc3_delay}s\n"
            f"Spam: {spam_delay}s\n"
            f"Flood: {flood_delay}s"
        )
    try:
        delay_val = max(0.001, float(context.args[0]))
        delay = delay_val
        nc2_delay = delay_val / 2
        nc3_delay = delay_val / 5
        spam_delay = delay_val * 5
        flood_delay = delay_val * 10
        await update.message.reply_text(
            f"✅ Delays updated:\n"
            f"NC: {delay}s\n"
            f"NC2: {nc2_delay}s\n"
            f"NC3: {nc3_delay}s\n"
            f"Spam: {spam_delay}s\n"
            f"Flood: {flood_delay}s"
        )
    except:
        await update.message.reply_text("❌ Invalid number")

@only_sudo
async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    promoted_count = 0
    already_admin_count = 0
    failed_count = 0
    
    # Use the first bot as controller to check and promote all bots
    if not bots:
        await update.message.reply_text("❌ No bots available")
        return
    
    controller_bot = bots[0]
    for bot in bots:
        try:
            # Check bot status using controller
            member = await controller_bot.get_chat_member(chat_id, bot.id)
            if member.status in ['administrator', 'creator']:
                already_admin_count += 1
                continue
            
            # Promote bot using controller
            await controller_bot.promote_chat_member(
                chat_id, bot.id,
                can_change_info=True,
                can_delete_messages=True,
                can_invite_users=True,
                can_restrict_members=True,
                can_pin_messages=True,
                can_manage_chat=True
            )
            promoted_count += 1
        except Exception as e:
            failed_count += 1
            print(f"Failed to promote bot {bot.id}: {e}")
    
    await update.message.reply_text(
        f"👑 Admin Promotion Results:\n"
        f"✅ Promoted: {promoted_count} bots\n"
        f"ℹ️ Already Admin: {already_admin_count} bots\n"
        f"❌ Failed: {failed_count} bots"
    )

@only_sudo
async def remove_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    for bot in bots:
        try:
            await bot.leave_chat(chat_id)
        except:
            pass
    await update.message.reply_text("👋 All bots leaving chat!")

@only_sudo
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    status_text = f""" SSYCHOGAWD STATUS
════════════════════

NAME CHANGERS
NC     : {len(nc_tasks.get(chat_id, []))}
NC2   : {len(nc3_tasks.get(chat_id, []))}
NC3    : {len(nc3_tasks.get(chat_id, []))}

SPAM
SPAM     : {len(spam_tasks.get(chat_id, []))}
FLOOD    : {len(flood_tasks.get(chat_id, []))}

SLIDE
TARGETS  : {len(slide_targets)}
SPAM     : {len(slidespam_targets)}

SPEED
NC     : {delay}s
NC2   : {nc2_delay}s
NC3   : {nc3_delay}s

SYSTEM
BOTS     : {len(bots)}
SUDO     : {len(SUDO_USERS)}

════════════════════
SSYCHOGAWD """
    await update.message.reply_text(status_text)

# ---------------------------
# ENHANCED AUTO REPLY HANDLER
# ---------------------------
async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):  # FIXED: Added ContextTypes.
    uid = update.message.from_user.id
    chat_id = update.message.chat_id
    message_id = update.message.message_id
    
    # Handle slide targets - reply to user's message
    if uid in slide_targets:
        # Create tasks for all bots to run concurrently
        tasks = []
        for bot in bots:
            task = asyncio.create_task(
                rapid_slide_reply(bot, chat_id, message_id)
            )
            tasks.append(task)
        # Wait for all to complete with timeout
        try:
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=1.0)
        except asyncio.TimeoutError:
            pass
    
    # Handle slidespam targets - reply to user's message
    if uid in slidespam_targets:
        # Create tasks for all bots to run concurrently
        tasks = []
        for bot in bots:
            task = asyncio.create_task(
                rapid_slidespam_reply(bot, chat_id, message_id)
            )
            tasks.append(task)
        # Wait for all to complete with timeout
        try:
            await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=0.5)
        except asyncio.TimeoutError:
            pass

async def rapid_slide_reply(bot, chat_id, message_id):
    """Rapid slide reply with minimal delay"""
    try:
        for text in SLIDE_TEXTS[:3]:
            await bot.send_message(
                chat_id, text, reply_to_message_id=message_id
            )
            await asyncio.sleep(0.01)  # Reduced from 0.1
    except Exception as e:
        print(f"Slide reply error: {e}")

async def rapid_slidespam_reply(bot, chat_id, message_id):
    """Rapid slidespam reply with minimal delay"""
    try:
        for text in SLIDE_TEXTS:
            await bot.send_message(
                chat_id, text, reply_to_message_id=message_id
            )
            await asyncio.sleep(0.005)  # Reduced from 0.05
    except Exception as e:
        print(f"Slidespam reply error: {e}")

# ---------------------------
# ENHANCED BOT SETUP WITH RETRY
# ---------------------------
async def run_all_bots():
    global apps, bots
    successful_bots = []
    failed_tokens = []
    
    for token in TOKENS:
        if token.strip():
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    app = build_app(token)
                    await app.initialize()
                    await app.start()
                    await app.updater.start_polling(drop_pending_updates=True)
                    
                    apps.append(app)
                    bots.append(app.bot)
                    successful_bots.append(token[:10] + "...")
                    print(f"✅ Bot initialized: {token[:10]}... (Attempt {attempt + 1})")
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        failed_tokens.append(token[:10] + "...")
                        print(f"❌ Failed building app after {max_retries} attempts: {e}")
                    else:
                        print(f"⚠️ Retry {attempt + 1}/{max_retries} for bot {token[:10]}...")
                        await asyncio.sleep(2)  # Wait before retry
    
    print(f"\n SSYCHO BAAP Status:")
    print(f"✅ Active Bots: {len(bots)}/{len(TOKENS)}")
    print(f"❌ Failed Bots: {len(failed_tokens)}")
    
    if failed_tokens:
        print(f"Failed tokens: {', '.join(failed_tokens)}")
    
    print(f"\n🤖 Active Bots: {len(bots)}")
    print("🫅🏻 Name Changers: READY (All 3 types can run simultaneously)")
    print("😹 Spam Functions: READY")
    print("🌊 Flood Mode: READY")
    print("🪼 Slide System: OPTIMIZED")
    print("👑 SUDO System: ACTIVE")
    print("⚡ Ultra-Fast Mode: ACTIVATED ")
    print("🚀 Performance: MAXIMUM - 24/7 RUNNING")
    
    # Bot health check
    await asyncio.sleep(5)  # Wait for bots to stabilize
    await bot_health_check()
    
    # Keep running
    await asyncio.Event().wait()

async def bot_health_check():
    """Check bot health and reconnect if needed"""
    print("\n🔍 Performing bot health check...")
    healthy_bots = []
    
    for i, bot in enumerate(bots):
        try:
            # Test bot connectivity
            await bot.get_me()
            healthy_bots.append(i)
            print(f"✅ Bot {i+1}: Healthy")
        except Exception as e:
            print(f"❌ Bot {i+1}: Unhealthy - {e}")
            # Try to restart unhealthy bot
            try:
                await apps[i].stop()
                await apps[i].initialize()
                await apps[i].start()
                await apps[i].updater.start_polling(drop_pending_updates=True)
                healthy_bots.append(i)
                print(f"🔄 Bot {i+1}: Restarted successfully")
            except:
                print(f"💀 Bot {i+1}: Failed to restart")
    
    print(f"\n📊 Health Check Result: {len(healthy_bots)}/{len(bots)} bots healthy")

# ---------------------------
# ENHANCED SLIDE COMMANDS
# ---------------------------
@only_sudo
async def targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):  # FIXED: Added ContextTypes.
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slide_targets.add(target_id)
    await update.message.reply_text(f"🎯 Target slide added: {target_id}")
    
    # Start immediate slide spam with all bots
    chat_id = update.message.chat_id
    message_id = update.message.reply_to_message.message_id
    
    # Create concurrent tasks for all bots
    tasks = []
    for bot in bots:
        task = asyncio.create_task(
            rapid_slide_reply(bot, chat_id, message_id)
        )
        tasks.append(task)
    
    # Execute with timeout
    try:
        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=2.0)
    except asyncio.TimeoutError:
        await update.message.reply_text("⚡ Slide initiated (some bots may be delayed)")

@only_sudo
async def slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):  # FIXED: Added ContextTypes.
    if not update.message.reply_to_message:
        return await update.message.reply_text("⚠️ Reply to a user's message")
    target_id = update.message.reply_to_message.from_user.id
    slidespam_targets.add(target_id)
    await update.message.reply_text(f"💥 Slide spam started: {target_id}")
    
    # Start immediate slide spam with all bots
    chat_id = update.message.chat_id
    message_id = update.message.reply_to_message.message_id
    
    # Create concurrent tasks for all bots
    tasks = []
    for bot in bots:
        task = asyncio.create_task(
            rapid_slidespam_reply(bot, chat_id, message_id)
        )
        tasks.append(task)
    
    # Execute with timeout
    try:
        await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=1.0)
    except asyncio.TimeoutError:
        await update.message.reply_text("⚡ Slide spam initiated (some bots may be delayed)")

# ---------------------------
# ADDITIONAL UTILITY COMMANDS
# ---------------------------
@only_sudo
async def restart_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):  # FIXED: Added ContextTypes.
    """Restart all bots"""
    await update.message.reply_text("🔄 Restarting all bots...")
    
    for i, app in enumerate(apps):
        try:
            await app.stop()
            await asyncio.sleep(0.5)
            await app.initialize()
            await app.start()
            await app.updater.start_polling(drop_pending_updates=True)
            print(f"✅ Bot {i+1} restarted")
        except Exception as e:
            print(f"❌ Failed to restart bot {i+1}: {e}")
    
    await update.message.reply_text("✅ Bot restart completed")

@only_sudo
async def check_bots(update: Update, context: ContextTypes.DEFAULT_TYPE):  # FIXED: Added ContextTypes.
    """Check bot status"""
    status_text = "🤖 Bot Status:\n"
    
    for i, bot in enumerate(bots):
        try:
            await bot.get_me()
            status_text += f"✅ Bot {i+1}: Online\n"
        except:
            status_text += f"❌ Bot {i+1}: Offline\n"
    
    await update.message.reply_text(status_text)

# Add these new commands to build_app():
def build_app(token):
    app = Application.builder().token(token).build()
    
    # Core commands
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("ping", ping_cmd))
    app.add_handler(CommandHandler("status", status_cmd))
    
    # Name changer commands
    app.add_handler(CommandHandler("nc", nc))
    app.add_handler(CommandHandler("nc2", nc2))
    app.add_handler(CommandHandler("nc3", nc3))

    app.add_handler(CommandHandler("stopnc", stopnc))
    app.add_handler(CommandHandler("stopnc2", stopnc))   # agar alag function nahi hai toh same use kar
    app.add_handler(CommandHandler("stopnc3", stopnc))
    
    # Spam commands
    app.add_handler(CommandHandler("spam", spam))
    app.add_handler(CommandHandler("unspam", unspam))
    app.add_handler(CommandHandler("flood", flood))
    app.add_handler(CommandHandler("stopflood", stopflood))
    
    # Slide commands
    app.add_handler(CommandHandler("targetslide", targetslide))
    app.add_handler(CommandHandler("stopslide", stopslide))
    app.add_handler(CommandHandler("slidespam", slidespam))
    app.add_handler(CommandHandler("stopslidespam", stopslidespam))
    
    # SUDO management
    app.add_handler(CommandHandler("addson", addson))
    app.add_handler(CommandHandler("delsudo", delsudo))
    app.add_handler(CommandHandler("listsudo", listsudo))
    
    # Control commands
    app.add_handler(CommandHandler("stopall", stopall))
    app.add_handler(CommandHandler("delay", delay_cmd))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("remove", remove_cmd))
    
    # Utility commands
    app.add_handler(CommandHandler("restartbots", restart_bots))
    app.add_handler(CommandHandler("checkbots", check_bots))
    
    # Auto replies
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, auto_replies))
    
    return app

# ---------------------------
# MAIN EXECUTION
# ---------------------------
if __name__ == "__main__":
    try:
        print(" Starting SSYCHO BAAP BOT...")
        asyncio.run(run_all_bots())
    except KeyboardInterrupt:
        print("\n Shutting down gracefully...")
        # Cleanup all tasks
        for chat_id in list(nc_tasks.keys()):
            for task in nc_tasks[chat_id]:
                task.cancel()
        for chat_id in list(nc2_tasks.keys()):
            for task in nc2_tasks[chat_id]:
                task.cancel()
        for chat_id in list(nc3_tasks.keys()):
            for task in nc3_tasks[chat_id]:
                task.cancel()
        print("✅ All tasks cancelled. Shutdown complete.")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()