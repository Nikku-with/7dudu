import os
import asyncio
import logging
import time
import random
import aiohttp
import urllib.parse as urllib_parse
from datetime import timedelta
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, UserNotParticipantError
from telethon.tl.functions.channels import InviteToChannelRequest, EditAdminRequest, EditPhotoRequest, GetParticipantRequest
from telethon.tl.functions.messages import AddChatUserRequest, SendReactionRequest
from telethon.tl.types import ChatAdminRights, ReactionEmoji, ChannelParticipantCreator, ChannelParticipantAdmin, ChannelParticipant
from telethon.tl.custom import Button

# --- ADVANCED LOGGING CONFIGURATION ---
logging.basicConfig(
    format='[%(levelname)s %(asctime)s] %(name)s: %(message)s',
    level=logging.WARNING
)
logger = logging.getLogger("USERHOSTSystem")

# --- MANAGER BOT CONFIGURATION ---
BOT_TOKEN = "8614879751:AAGxxOQszYTN8spnYVtdHo6arPwc1O6x_JU"
ADMIN_CHAT_ID = 8905002151

# MANAGER BOT API CREDENTIALS
API_ID = 36526099
API_HASH = "5269e9b4dfdef6a38cd30df4dfa11285"

# Permanent dict for tracking active hosted users and temporary registration wizard data
USER_REG_DATA = {}
HOSTED_USERS = set()  # Tracks all users who successfully hosted for broadcasting
HOSTED_USER_ENTITIES = {} # Tracks full user info/objects or usernames for the member list feature
FORCED_CHANNELS = []  # Stores mandatory channels that users must join before hosting

# 📝 AUTO REPLY TEXTS:
CUSTOM_AUTO_REPLY_TEXTS = [
    "🍁⃝💙⃝⋆🕊️𝙆ɪʟᴀss 𝙈ᴛᴛ 𝙍ɴᴅʏ 𝙈ᴀᴀ 𝙆E 𝙇ᴀᴅᴋᴇ 🤣🤣🍁⃝💙⃝⋆🕊️",
    "💀💙⃝⋆🤣𝘽ᴀᴀᴘ 𝙆ᴇ 𝙎ᴀᴍɴᴇ 𝙃ᴀᴡᴀʙᴀᴀᴢɪ 𝙆ᴀʀᴇɢᴀ 𝙍ɴᴅʏᴋᴇ 𝙇ᴀᴅᴋᴇ 🤣☝️ ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐",
    "𝙍ɴᴅʏᴋᴇ 𝘽ᴀᴀᴘ 𝘽ᴏʟ 𝙈ᴀᴀꜰ 𝙆ᴀʀᴅᴜɴɢᴀ😭🤣🤣☝️🦢   ᯓᡣ𐭩______ 𓂃☁︎ 𓂃",
    "꧁☠︎︎༒︎☢︎︎༆𝙆ʏᴏ 𝙍ᴇ 𝙈ᴀᴅᴀʀᴄʜᴏᴅ 𝘽ᴀɴᴀᴜ 𝙏ᴜᴊʜᴇ 𝙁ʏᴛᴇʀ 𝘽ʜᴀɢᴡᴀɴ 𝘽ᴏʟ 𝙏ᴏ 𝙅ᴀɴᴇ 𝘿ᴜɴɢᴀ 🤣 𓂃☁︎ ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐",
    "𓂃☁︎ 𝘼ᴀɢᴀʏᴀ 𝘼ᴘɴɪ 𝙈ᴀᴀ 𝘾ʜᴜᴅᴀɴᴇ 𝙆ʏᴏ 𝙍ᴇ 𝙍ᴀɴᴅɪᴋᴇ 🤣🤣",
    "⋆⭒˚.⋆𝘿ᴜɴɪᴀ 𝙈ᴇ 𝙎ɪʀꜰ 𝙀ᴋ 𝘽ʜᴀɢᴡᴀɴ 𝙃 𝙒ᴏ 𝙋ʀɪɴᴄE 𝘽ʜᴀɢᴡᴀɴ 𝙃ᴀɪ 𝙐sᴋᴏ 𝘽ʜᴀɢᴡᴀɴ 𝘽ᴏʟ 𝙏ᴏʜ 𝙏ᴇʀʏ 𝙈ᴀᴀ 𝘾ʜᴏᴅᴋᴇ 𝙏ᴜᴊʜᴇ 𝙅ᴀᴀɴᴇ 𝘿ᴜɴɢᴀ 🤣☝️",
    "꧁ঔৣ☠︎᭄🦢𝙎ᴜɴ 𝙍ᴏ 𝙈ᴀᴛ 𝙍ᴀɴᴅɪʏᴋᴇ 𝘼ʙʜɪ 𝙏ᴏ 𝙏ᴇʀɪ 𝐂ᴜᴅᴀɪ 𝘽ʜɪ 𝙋ᴜʀɪ 𝙉ᴀʜɪ 𝙃ᴜɪ ཧᜰ꙰ꦿ",
    "亗 ●────────𝘽ʜᴀɢᴡᴀɴ 𝘽ᴏʟ 𝙍ᴀɴᴅɪʏᴋᴇ༒࿐ 𓂃✍",
    "ᜰ꙰ꦿ➢𝙁ʏᴛᴇʀ 𝘽ᴀɴᴇɢᴀ 𝙍ᴜᴋ 𝙏ᴇʀɪ 𝙈ᴀᴀ 𝘾ʜᴏᴅɴᴇ 𝙏ᴇʀᴀ 𝘽ᴀᴀᴘ 𝘼ʀᴀ 𝙃ᴀɪ😭☝️ᯓᡣ𐭩______ 𓂃☁︎ 𓂃"
]



# ==================== USERBOT ENGINE & ALL COMMANDS REGISTRATION ====================

def register_userbot_handlers(client):
    SAVED_BOTS = []
    ACTIVE_LOOPS = {}         # Spams aur Locks ke liye
    AUTO_REPLY_TARGETS = {}   # Auto Reply (.ar) ke liye
    AUTO_REACT_TARGETS = {}   # Auto React (.art) ke liye
    LOCAL_MUTES = set()       # Local Mutes: (chat_id, user_id)
    GLOBAL_MUTES = set()      # Global Mutes: user_id
    SUDO_USERS = set()        # Sudo Users List (User IDs)
    START_TIME = time.time()  # Uptime track karne ke liye

    # --- JOD3 GROUP PROTECTION & PFP STATES ---
    ANTIDEL_ENABLED = False
    ANTIDEL_CACHE = {}
    WATCH_SPAM_CONFIG = {}
    GROUP_PFP_POOL = []
    PFP_ROTATE_TASK = None

    async def check_auth(event):
        if event.out:
            return True
        if event.sender_id in SUDO_USERS:
            return True
        return False

    async def edit_or_reply(event, text):
        if event.out:
            try:
                await event.edit(text)
            except Exception:
                await event.reply(text)
        else:
            await event.reply(text)

    # --- 0. HELP MENU (.jod) ---
    @client.on(events.NewMessage(pattern=r'\.jod'))
    async def jod_help_handler(event):
        if not await check_auth(event):
            return
        help_text = (
            f"🩷 *𝐔𝐒𝐄𝐑𝐁𝐎𝐓 𝐌𝐄𝐍𝐔 v1* 🩷\n\n"
            f"🛡️ *𝙁𝙀𝘼𝙏𝙐𝙍𝙀𝙎*\n\n"
            f"✘ `.antidel on/off` - *𝐀ɴᴛɪ-𝐃ᴇʟᴇᴛᴇ ᴩʀᴏᴛᴇᴄᴛɪᴏɴ ᴛᴏɢɢʟᴇ* ✨\n"
            f"✘ `.watchspam [limit] [sec]` - *𝐀ɴᴛɪ-𝐒ᴩᴀᴍ ɢᴜᴀʀᴅ ꜱᴇᴛᴜᴩ* ⚡\n"
            f"✘ `.unwatchspam` - *𝐀ɴᴛɪ-𝐒ᴩᴀᴍ ᴅɪꜱᴀʙʟᴇ ᴋᴀʀᴇɪْن* 🛑\n"
            f"✘ `.setgpfp` - *𝐑ᴇᴩʟʏ ᴩʜᴏᴛᴏ ᴋᴏ 𝐆ʀᴏᴜᴩ 𝐏𝐅𝐏 ʙᴀɴᴀʏᴇɪɴ* 🖼️\n"
            f"✘ `.autogpfp [sec]` - *𝐑ᴏᴛᴀᴛɪɴɢ 𝐆ʀᴏᴜᴩ 𝐏𝐅𝐏 ᴄHᴀʟᴜ ᴋᴀʀᴇɪɴ* 🔄\n"
            f"✘ `.stopgpfp` - *𝐑ᴏᴛᴀᴛɪɴɢ 𝐆ʀᴏᴜᴩ 𝐏𝐅𝐏 ʀᴏᴋᴇɪɴ* 🛑\n\n"
            f"📥 *ᴍᴇᴅɪᴀ ᴅᴏᴡɴʟᴏᴀᴅᴇꜱ (100% FIXED)*\n\n"
            f"✘ `.ig [link]` - *𝐈ɴꜱᴛᴀɢʀᴀᴍ 𝐑ᴇᴇʟ/𝐕ɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅ* 💎\n"
            f"✘ `.pt [link]` - *𝐏ɪɴᴛᴇʀᴇꜱᴛ 𝐈ᴍᴀɢᴇ/𝐕ɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅ* ✨\n"
            f"✘ `.fb [link]` - *𝐅ᴀᴄᴇʙᴏᴏᴋ 𝐕ɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅ* 🎬\n"
            f"✘ `.yt [link]` - *𝐘ᴏᴜ𝐓ᴜʙᴇ 𝐕ɪᴅᴇᴏ/𝐀ᴜᴅɪᴏ ᴅᴏᴡɴʟᴏᴀᴅ* 🎵\n\n"
            f"🎮 *𝙁𝙐𝙉 & 𝙂𝘼𝙈𝙀𝙎 𝙕𝙊𝙉𝙀*\n\n"
            f"✘ `.tictactoe` - *𝐁ᴏᴛ ᴋᴇ ꜱᴀᴛH 𝐓ɪᴄ-𝐓ᴀᴄ-𝐓ᴏᴇ ᴋʜᴇʟᴇ* 🎲\n"
            f"✘ `.rps [stone/paper/scissor]` - *𝐒ᴛᴏɴᴇ-𝐏ᴀᴩᴇʀ-𝐒ᴄɪꜱꜱᴏʀꜱ* ✂️\n"
            f"✘ `.roll` - *𝐃ɪᴄᴇ ʀᴏʟʟ ᴋᴀʀᴇɪْن (1 ꜱᴇ 6)* 🎰\n"
            f"✘ `.flip` - *𝐂ᴏɪɴ ᴛᴏꜱꜱ ᴋᴀʀᴇɪْن (𝐇ᴇᴀᴅ/𝐓ᴀɪʟ)* 🪙\n"
            f"✘ `.fact` - *𝐄ᴋ ɪɴᴛᴇʀᴇꜱᴛɪɴɢ ʀᴀɴᴅᴏᴍ ꜰᴀᴄᴛ ᴩᴀᴅʜᴇɪْن* 💡\n\n"
            f"🤖 *𝐀𝐈 & 𝐒𝐔𝐃𝐎 𝐌𝐀𝐍𝐀𝐆𝐄𝐌𝐄𝐍𝐓*\n\n"
            f"✘ `.ai [sawal]` - *𝐀ᴅᴠᴀɴᴄᴇ 𝐇ɪɴɢʟɪꜱH 𝐀𝐈 ꜱᴇ ᴄHᴀᴛ ᴋᴀʀᴇɪْن* 🧠\n"
            f"✘ `.sudo` - *𝐑ᴇᴩʟʏ ᴋᴀʀᴋᴇ ᴜꜱᴇʀ ᴋᴏ 𝐒ᴜᴅᴏ ʙᴀɴᴀʏᴇɪْن* 👑\n"
            f"✘ `.delsudo` - *𝐑ᴇᴩʟʏ ᴋᴀʀᴋᴇ 𝐒ᴜᴅᴏ ʜᴀᴛᴀʏᴇɪْن* ❌\n"
            f"✘ `.list sudo` - *𝐒ᴜᴅᴏ ᴜꜱᴇʀꜱ ᴋɪ ʟɪꜱᴛ ᴅᴇᴋʜᴇɪْن* 📜\n\n"
            f"💬 *𝐁𝐎𝐓 & 𝐒𝐏𝐀𝐌 𝐓𝐎𝐎𝐋𝐒*\n\n"
            f"✘ `.addbots @b1 @b2` - *𝐁ᴏᴛꜱ ꜱᴀᴠᴇ ᴋᴀʀᴇɪْن* 🤖\n"
            f"✘ `.listbots` - *𝐒ᴀᴠᴇᴅ ʙᴏᴛꜱ ᴋɪ ʟɪꜱᴛ ᴅᴇᴋʜᴇɪْن* 📋\n"
            f"✘ `.invitebots` - *𝐆ʀᴏᴜᴩ ᴍᴇ ʙᴏᴛꜱ ᴀᴅᴅ ᴋᴀʀᴇɪْن* ➕\n"
            f"✘ `.promotebots` - *𝐒ᴀᴠᴇᴅ ʙᴏᴛꜱ ᴋᴏ ᴀᴅᴍɪɴ ʙᴀɴᴀʏᴇɪْن* ⚡\n"
            f"✘ `.d [0.5-5] [text]` - *𝐃ᴇʟᴀʏ ᴡᴀʟᴀ ᴄᴜꜱᴛᴏᴍ ꜱᴩᴀᴍ* ⏱️\n"
            f"✘ `.spam [text]` - *𝐂ᴏɴᴛɪɴᴜᴏᴜꜱ ꜱᴩᴀᴍ* 🔥\n"
            f"✘ `.sspam` - *𝐒ᴩᴀᴍ ʀᴏᴋᴇɪْن* 🛑\n\n"
            f"🔒 *𝐋𝐎𝐂𝐊, 𝐀𝐑, 𝐀𝐑𝐓 & 𝐌𝐔𝐓𝐄𝐒*\n\n"
            f"✘ `.lock [text]` - *𝐑ᴇᴩʟʏ ᴋᴀʀᴋᴇ ʟᴏᴄᴋ ʟᴀɢᴀʏᴇɪْن* 🔒\n"
            f"✘ `.slock` - *𝐋ᴏᴄᴋ ʜᴀᴛᴀʏᴇɪْن* 🔓\n"
            f"✘ `.ar` - *𝐀ᴜᴛᴏ-𝐑ᴇᴩʟʏ ᴄHᴀʟᴜ ᴋᴀʀᴇɪْن* 🤖\n"
            f"✘ `.sar` - *𝐀ᴜᴛᴏ-𝐑ᴇᴩʟʏ ʙᴀɴᴅ ᴋᴀʀᴇɪْن* 🛑\n"
            f"✘ `.art [emoji]` - *𝐀ᴜᴛᴏ-𝐑ᴇᴀᴄᴛ ᴄHᴀʟᴜ ᴋᴀʀᴇɪْن* ❤️\n"
            f"✘ `.sart` - *𝐀ᴜᴛᴏ-𝐑ᴇᴀᴄᴛ ʙᴀɴᴅ ᴋᴀʀᴇɪْن* 🛑\n"
            f"✘ `.m` / `.gm` / `.sm` - *𝐌ᴜᴛᴇ & 𝐔ɴᴍᴜᴛᴇ ᴄᴏɴᴛʀᴏʟꜱ* 🔇\n\n"
            f"⚡ *𝐒𝐘𝐒𝐓𝐄𝐌 𝐔𝐓𝐈𝐋𝐈𝐓𝐈𝐄𝐒*\n\n"
            f"✘ `.uptime` - *𝐁ᴏᴛ ᴋᴀ ʀᴜɴɴɪɴɢ ᴛɪᴍᴇ ᴅᴇᴋʜᴇɪْن* ⏳\n"
            f"✘ `.ping` - *𝐁ᴏᴛ ᴋɪ ꜱᴩᴇᴇᴅ ᴄHᴇᴄᴋ ᴋᴀʀᴇɪْن* 🏓\n"
            f"✘ `.stopall` - *𝐒ᴀʙ ᴋᴜᴄH ᴛᴜʀᴀɴᴛ ʀᴏᴋᴇɪْن* ⚡\n"
                 f"🇾🇪 𝐏ᴏᴡᴇʀᴇᴅ 𝐁ʏ @VEGETAUSERBOTHOSTBOT 🖤"
        )
        await edit_or_reply(event, help_text)

    @client.on(events.NewMessage(pattern=r'\.antidel\s+(on|off)'))
    async def toggle_antidel(event):
        nonlocal ANTIDEL_ENABLED
        if not await check_auth(event): return
        mode = event.pattern_match.group(1).lower()
        ANTIDEL_ENABLED = (mode == "on")
        await edit_or_reply(event, f"🛡️ *𝐀ɴᴛɪ-𝐃ᴇʟᴇᴛᴇ 𝐏ʀᴏᴛᴇᴄᴛɪᴏɴ:* `{ANTIDEL_ENABLED}` ✨")

    @client.on(events.MessageDeleted())
    async def antidel_handler(event):
        if not ANTIDEL_ENABLED: return
        for msg_id in event.deleted_ids:
            if msg_id in ANTIDEL_CACHE:
                cached = ANTIDEL_CACHE[msg_id]
                try:
                    await client.send_message(
                        cached['chat_id'],
                        f"🛡️ *[𝐀𝐍𝐓𝐈-𝐃𝐄𝐋𝐄𝐓𝐄 𝐃𝐄𝐓𝐄𝐂𝐓𝐄𝐃]* ✨\n\n{cached['text']}"
                    )
                except Exception: pass

    @client.on(events.NewMessage(pattern=r'\.watchspam(?:\s+(.+)|$)'))
    async def set_watchspam(event):
        if not await check_auth(event): return
        args = event.pattern_match.group(1)
        if not args: return await edit_or_reply(event, "⚠️ *𝐔ꜱᴀɢᴇ:* `.watchspam 3 5` (3 ᴍꜱɢꜱ ɪɴ 5 ꜱᴇᴄꜱ) ⚡")
        parts = args.split()
        if len(parts) >= 2 and parts[0].isdigit() and parts[1].isdigit():
            lim, sec = int(parts[0]), int(parts[1])
            WATCH_SPAM_CONFIG[event.chat_id] = {"limit": lim, "sec": sec, "logs": {}}
            await edit_or_reply(event, f"👁️ *𝐖ᴀᴛᴄʜ𝐒ᴩᴀᴍ 𝐀ᴄᴛɪᴠᴇ:* `{lim}` ᴍꜱɢꜱ ᴩᴇʀ `{sec}`ꜱ. 🔥")

    @client.on(events.NewMessage(pattern=r'\.unwatchspam'))
    async def stop_watchspam(event):
        if not await check_auth(event): return
        if event.chat_id in WATCH_SPAM_CONFIG:
            del WATCH_SPAM_CONFIG[event.chat_id]
            await edit_or_reply(event, "🛑 *𝐖ᴀᴛᴄH𝐒ᴩᴀᴍ 𝐃ɪꜱᴀʙʟᴇᴅ ꜰᴏʀ ᴛʜɪꜱ ᴄHᴀᴛ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.setgpfp'))
    async def set_group_pfp(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply or not reply.media:
            return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴀɴ ɪᴍᴀɢᴇ ᴛᴏ ꜱᴇᴛ ᴀꜱ 𝐆ʀᴏᴜᴩ 𝐏𝐅𝐏.* 🖼️")
        msg = await event.reply("🔄 *𝐔ᴩᴅᴀᴛɪɴɢ 𝐆ʀᴏᴜᴩ 𝐏ʜᴏᴛᴏ...* ✨")
        photo = await reply.download_media()
        try:
            await client(EditPhotoRequest(
                channel=event.chat_id,
                photo=await client.upload_file(photo)
            ))
            await msg.edit("✅ *𝐆ʀᴏᴜᴩ 𝐏ʜᴏᴛᴏ 𝐔ᴩᴅᴀᴛᴇᴅ 𝐒ᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!* 💎")
        except Exception as e:
            await msg.edit(f"❌ *𝐅ᴀɪʟᴇᴅ:* `{e}` ⚠️")

    @client.on(events.NewMessage(pattern=r'\.autogpfp\s+([0-9]+)'))
    async def start_auto_gpfp(event):
        nonlocal PFP_ROTATE_TASK
        if not await check_auth(event): return
        sec = int(event.pattern_match.group(1))
        if sec < 10: return await edit_or_reply(event, "⚠️ *𝐃ᴇʟᴀʏ ᴍᴜꜱᴛ ʙᴇ at ʟᴇᴀꜱᴛ 10ꜱ.* ⏱️")
        
        reply = await event.get_reply_message()
        if reply and reply.media:
            photo = await reply.download_media()
            GROUP_PFP_POOL.append(photo)
            
        if not GROUP_PFP_POOL:
            return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ɪᴍᴀɢᴇ ᴛᴏ ᴀᴅᴅ ᴛᴏ ᴩᴏᴏʟ ꜰɪʀꜱᴛ!* 🖼️")

        async def worker():
            idx = 0
            while True:
                try:
                    p = GROUP_PFP_POOL[idx % len(GROUP_PFP_POOL)]
                    await client(EditPhotoRequest(
                        channel=event.chat_id,
                        photo=await client.upload_file(p)
                    ))
                    idx += 1
                except asyncio.CancelledError:
                    break
                except Exception: pass
                await asyncio.sleep(sec)

        if PFP_ROTATE_TASK: PFP_ROTATE_TASK.cancel()
        PFP_ROTATE_TASK = asyncio.create_task(worker())
        await edit_or_reply(event, f"🖼️ *𝐀ᴜᴛᴏ 𝐆ʀᴏᴜᴩ 𝐏𝐅𝐏 𝐑ᴏᴛᴀᴛɪᴏɴ 𝐀ᴄᴛɪᴠᴇ ᴇᴠᴇʀʏ {sec} ꜱᴇᴄᴏɴᴅꜱ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.stopgpfp'))
    async def stop_auto_gpfp(event):
        nonlocal PFP_ROTATE_TASK
        if not await check_auth(event): return
        if PFP_ROTATE_TASK:
            PFP_ROTATE_TASK.cancel()
            PFP_ROTATE_TASK = None
            await edit_or_reply(event, "🛑 *𝐀ᴜᴛᴏ 𝐏𝐅𝐏 𝐑ᴏᴛᴀᴛɪᴏɴ 𝐒ᴛᴏᴩᴩᴇᴅ!* ✨")

    async def fetch_media_url(api_url):
        headers = {"User-Agent": "Mozilla/5.0"}
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(api_url, headers=headers, timeout=20) as resp:
                    if resp.status == 200:
                        try: return await resp.json()
                        except Exception: return await resp.text()
            except Exception: pass
        return None

    @client.on(events.NewMessage(pattern=r'\.ig\s+(.+)'))
    async def download_instagram(event):
        if not await check_auth(event): return
        url = event.pattern_match.group(1).strip()
        msg = await event.reply("📥 *𝐃ᴏᴡɴʟᴏᴀᴅɪɴɢ 𝐈ɴꜱᴛᴀɢʀᴀᴍ 𝐌ᴇᴅɪᴀ...* ⏳✨")
        api = f"https://api.siputzx.my.id/api/d/igdl?url={urllib_parse.quote(url)}"
        res = await fetch_media_url(api)
        media_url = None
        if isinstance(res, dict) and res.get("status") and res.get("data"):
            try: media_url = res["data"][0]["url"] if isinstance(res["data"], list) else res["data"].get("url")
            except Exception: pass
        if media_url:
            await client.send_file(event.chat_id, media_url, caption="✨ *𝐃ᴏᴡɴʟᴏᴀᴅᴇᴅ ᴠɪᴀ 𝐔𝐒𝐄𝐑𝐇𝐎𝐒𝐓 𝐁𝐎𝐓* 💎")
            await msg.delete()
        else:
            await msg.edit("❌ *𝐈ɴꜱᴛᴀɢʀᴀᴍ ᴅᴏᴡɴʟᴏᴀᴅ ꜰᴀɪʟ ʜᴏ ɢᴀʏᴀ!* ⚠️")

    @client.on(events.NewMessage(pattern=r'\.pt\s+(.+)'))
    async def download_pinterest(event):
        if not await check_auth(event): return
        url = event.pattern_match.group(1).strip()
        msg = await event.reply("📥 *𝐃ᴏᴡɴʟᴏᴀᴅɪɴɢ 𝐏ɪɴᴛᴇʀᴇꜱᴛ 𝐌ᴇᴅɪᴀ...* ⏳✨")
        api = f"https://api.siputzx.my.id/api/d/pinterest?url={urllib_parse.quote(url)}"
        res = await fetch_media_url(api)
        media_url = None
        if isinstance(res, dict) and res.get("status") and res.get("data"):
            media_url = res["data"].get("url") or res["data"].get("download")
        if media_url:
            await client.send_file(event.chat_id, media_url, caption="✨ *𝐃ᴏᴡɴʟᴏᴀᴅᴇᴅ ᴠɪᴀ 𝐔𝐒𝐄𝐑𝐇𝐎𝐒𝐓 𝐁𝐎𝐓* 💎")
            await msg.delete()
        else:
            await msg.edit("❌ *𝐏ɪɴᴛᴇʀᴇꜱᴛ ᴍᴇᴅɪᴀ ꜰᴇᴛᴄH ɴᴀʜɪ ʜᴏ ᴩᴀʏᴀ!* ⚠️")

    @client.on(events.NewMessage(pattern=r'\.fb\s+(.+)'))
    async def download_facebook(event):
        if not await check_auth(event): return
        url = event.pattern_match.group(1).strip()
        msg = await event.reply("📥 *𝐃ᴏᴡɴʟᴏᴀᴅɪɴɢ 𝐅ᴀᴄᴇʙᴏᴏᴋ 𝐕ɪᴅᴇᴏ...* ⏳✨")
        api = f"https://api.siputzx.my.id/api/d/fbdl?url={urllib_parse.quote(url)}"
        res = await fetch_media_url(api)
        media_url = None
        if isinstance(res, dict) and res.get("status") and res.get("data"):
            media_url = res["data"].get("hd") or res["data"].get("sd")
        if media_url:
            await client.send_file(event.chat_id, media_url, caption="✨ *𝐃ᴏᴡɴʟᴏᴀᴅᴇᴅ ᴠɪᴀ 𝐔𝐒𝐄𝐑𝐇𝐎𝐒𝐓 𝐁𝐎𝐓* 💎")
            await msg.delete()
        else:
            await msg.edit("❌ *𝐅ᴀᴄᴇʙᴏᴏᴋ ᴠɪᴅᴇᴏ ᴅᴏᴡɴʟᴏᴀᴅ ɴᴀʜɪ ʜᴏ ᴩᴀʏᴀ!* ⚠️")

    @client.on(events.NewMessage(pattern=r'\.yt\s+(.+)'))
    async def download_youtube(event):
        if not await check_auth(event): return
        url = event.pattern_match.group(1).strip()
        msg = await event.reply("📥 *𝐅ᴇᴛᴄHɪɴɢ 𝐘ᴏᴜ𝐓ᴜʙᴇ 𝐕ɪᴅᴇᴏ...* ⏳✨")
        api = f"https://api.siputzx.my.id/api/d/youtube?url={urllib_parse.quote(url)}"
        res = await fetch_media_url(api)
        dl_url, title = None, "YouTube Video"
        if isinstance(res, dict) and res.get("status") and res.get("data"):
            data = res["data"]
            dl_url = data.get("dl") or data.get("download") or data.get("url")
            title = data.get("title", "YouTube Video")
        if dl_url:
            await client.send_file(event.chat_id, dl_url, caption=f"🎬 *{title}*\n✨ *𝐃ᴏᴡɴʟᴏᴀᴅᴇᴅ ᴠɪᴀ 𝐔𝐒𝐄𝐑𝐇𝐎𝐒𝐓 𝐁𝐎𝐓* 💎")
            await msg.delete()
        else:
            await msg.edit("❌ *𝐘ᴏᴜ𝐓ᴜʙᴇ ᴠɪᴅᴇᴏ ꜰᴇᴛᴄH ɴᴀʜɪ ʜᴏ ᴩᴀʏᴀ!* ⚠️")

    @client.on(events.NewMessage(pattern=r'\.tictactoe'))
    async def game_tictactoe(event):
        if not await check_auth(event): return
        board = ["1", "2", "3", "4", "5", "6", "7", "8", "9"]
        bot_choice = random.choice([i for i in range(9) if board[i].isdigit()])
        board[bot_choice] = "❌"
        user_choice = random.choice([i for i in range(9) if board[i].isdigit()])
        board[user_choice] = "⭕"
        game_msg = (
            f"🎮 *𝐓𝐈𝐂 - 𝐓𝐀𝐂 - 𝐓𝐎𝐄* 🎮\n\n"
            f" ` {board[0]} ` | ` {board[1]} ` | ` {board[2]} ` \n"
            f" ` {board[3]} ` | ` {board[4]} ` | ` {board[5]} ` \n"
            f" ` {board[6]} ` | ` {board[7]} ` | ` {board[8]} ` \n\n"
            f"✨ *𝐒ᴛᴀᴛᴜꜱ:* 𝐌ᴀᴛᴄH 𝐃ʀᴀᴡ! 🤝"
        )
        await edit_or_reply(event, game_msg)

    @client.on(events.NewMessage(pattern=r'\.rps\s*(.*)'))
    async def game_rps(event):
        if not await check_auth(event): return
        user_move = event.pattern_match.group(1).lower().strip()
        choices = ["stone", "paper", "scissor"]
        if user_move not in choices:
            await edit_or_reply(event, "⚠️ *𝐄xᴀᴍᴩʟᴇ:* `.rps stone` 🎮")
            return
        bot_move = random.choice(choices)
        emojis = {"stone": "🪨 𝐒ᴛᴏɴᴇ", "paper": "📄 𝐏ᴀᴩᴇʀ", "scissor": "✂️ 𝐒ᴄɪꜱꜱᴏʀ"}
        if user_move == bot_move: result = "🤝 *𝐓𝐈𝐄!*"
        elif (user_move == "stone" and bot_move == "scissor") or (user_move == "paper" and bot_move == "stone") or (user_move == "scissor" and bot_move == "paper"):
            result = "🎉 *𝐘𝐎𝐔 𝐖𝐈𝐍!* 🏆✨"
        else: result = "🤖 *𝐁𝐎𝐓 𝐖𝐈𝐍𝐒!* ⚡"
        await edit_or_reply(event, f"✂️ *𝐑𝐏𝐒 𝐆𝐀𝐌𝐄*\n𝐀ᴀᴩ: {emojis[user_move]}\n𝐁ᴏᴛ: {emojis[bot_move]}\n\n{result}")

    @client.on(events.NewMessage(pattern=r'\.roll'))
    async def game_roll(event):
        if not await check_auth(event): return
        await edit_or_reply(event, f"🎲 *𝐃ɪᴄᴇ 𝐑ᴏʟʟᴇᴅ:* `{random.randint(1, 6)}` ✨")

    @client.on(events.NewMessage(pattern=r'\.flip'))
    async def game_flip(event):
        if not await check_auth(event): return
        await edit_or_reply(event, f"🪙 *𝐂ᴏɪɴ 𝐅ʟɪᴩ:* `{random.choice(['Heads', 'Tails'])}` ✨")

    @client.on(events.NewMessage(pattern=r'\.fact'))
    async def fun_fact(event):
        if not await check_auth(event): return
        facts = ["Honey kabhi kharab nahi hota!", "Octopus ke paas 3 dil hote hain!", "Banana berry hai!"]
        await edit_or_reply(event, f"💡 *𝐅ᴀᴄᴛ:* {random.choice(facts)} ✨")

    @client.on(events.NewMessage(pattern=r'\.sudo'))
    async def add_sudo_handler(event):
        if not event.out: return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        SUDO_USERS.add(reply.sender_id)
        await edit_or_reply(event, f"👑 *𝐀ᴅᴅᴇᴅ* `{reply.sender_id}` *ᴛᴏ 𝐒ᴜᴅᴏ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.delsudo'))
    async def del_sudo_handler(event):
        if not event.out: return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        if reply.sender_id in SUDO_USERS: SUDO_USERS.remove(reply.sender_id)
        await edit_or_reply(event, f"👑 *𝐑ᴇᴍᴏᴠᴇᴅ ꜰʀᴏᴍ 𝐒ᴜᴅᴏ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.list\s*sudo'))
    async def list_sudo_handler(event):
        if not await check_auth(event): return
        if not SUDO_USERS: return await edit_or_reply(event, "⚠️ *𝐍ᴏ 𝐒ᴜᴅᴏ ᴜꜱᴇʀꜱ!*")
        await edit_or_reply(event, "👑 *𝐒ᴜᴅᴏ 𝐔ꜱᴇʀꜱ:*\n" + "\n".join([f"• `{uid}`" for uid in SUDO_USERS]))

    @client.on(events.NewMessage(pattern=r'\.ai\s*(.*)'))
    async def free_ai_handler(event):
        if not await check_auth(event): return
        query = event.pattern_match.group(1).strip()
        if not query: return await edit_or_reply(event, "⚠️ *𝐄xᴀᴍᴩʟᴇ:* `.ai Python kya hai` 🧠")
        loading = await event.reply("🧠 *𝐀𝐈 ꜱᴏᴄH ʀᴀʜᴀ ʜᴀɪ...* ⏳✨")
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"https://text.pollinations.ai/{urllib_parse.quote(query)}?model=openai", timeout=12) as resp:
                    res = await resp.text()
                    await loading.edit(res if res else "❌ *𝐄ʀʀᴏʀ!*")
        except Exception:
            await loading.edit("❌ *𝐀𝐈 𝐒ᴇʀᴠᴇʀ ʙᴜꜱʏ ʜᴀɪ.* ⚠️")

    @client.on(events.NewMessage(pattern=r'\.addbots\s*(.*)'))
    async def save_bots_handler(event):
        if not await check_auth(event): return
        nonlocal SAVED_BOTS
        text = event.pattern_match.group(1).strip()
        if not text: return await edit_or_reply(event, "⚠️ *𝐄xᴀᴍᴩʟᴇ:* `.addbots @bot1` 🤖")
        SAVED_BOTS = [b if b.startswith('@') else f"@{b}" for b in text.split()]
        await edit_or_reply(event, f"💎 *𝐒ᴀᴠᴇᴅ {len(SAVED_BOTS)} ʙᴏᴛꜱ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.listbots'))
    async def list_bots_handler(event):
        if not await check_auth(event): return
        if not SAVED_BOTS: return await edit_or_reply(event, "⚠️ *𝐍ᴏ ʙᴏᴛꜱ ꜱᴀᴠᴇᴅ!*")
        await edit_or_reply(event, "📋 *𝐒ᴀᴠᴇᴅ 𝐁ᴏᴛꜱ:*\n" + "\n".join([f"• `{b}`" for b in SAVED_BOTS]))

    @client.on(events.NewMessage(pattern=r'\.invitebots'))
    async def invite_bots_handler(event):
        if not await check_auth(event): return
        if not SAVED_BOTS: return await edit_or_reply(event, "⚠️ *𝐔ꜱᴇ `.addbots` ꜰɪʀꜱᴛ!*")
        msg = await event.reply("⚡ *𝐀ᴅᴅɪɴɢ ʙᴏᴛꜱ...* ⏳")
        count = 0
        for b in SAVED_BOTS:
            try:
                ent = await client.get_entity(b)
                if event.is_group: await client(InviteToChannelRequest(event.chat_id, [ent]))
                count += 1
            except Exception: pass
            await asyncio.sleep(1.0)
        await msg.edit(f"✅ *𝐀ᴅᴅᴇᴅ {count} ʙᴏᴛꜱ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.promotebots'))
    async def promote_bots_handler(event):
        if not await check_auth(event): return
        if not SAVED_BOTS: return await edit_or_reply(event, "⚠️ *𝐔ꜱᴇ `.addbots` ꜰɪʀꜱᴛ!*")
        msg = await event.reply("👑 *𝐏ʀᴏᴍᴏᴛɪɴɢ ʙᴏᴛꜱ...* ⏳")
        count = 0
        rights = ChatAdminRights(change_info=True, post_messages=True, edit_messages=True, delete_messages=True, ban_users=True, invite_users=True, pin_messages=True)
        for b in SAVED_BOTS:
            try:
                ent = await client.get_entity(b)
                await client(EditAdminRequest(channel=event.chat_id, user_id=ent, admin_rights=rights, rank="HOST"))
                count += 1
            except Exception: pass
            await asyncio.sleep(1.0)
        await msg.edit(f"✅ *𝐏ʀᴏᴍᴏᴛᴇᴅ {count} ʙᴏᴛꜱ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.d\s+([0-9.]+)\s+(.+)'))
    async def delay_spam_handler(event):
        if not await check_auth(event): return
        try:
            delay, text = float(event.pattern_match.group(1)), event.pattern_match.group(2)
            chat_id = event.chat_id
            key = f"delay_{chat_id}_{time.time()}"
            async def worker():
                while True:
                    await client.send_message(chat_id, text)
                    await asyncio.sleep(max(0.5, min(delay, 5.0)))
            ACTIVE_LOOPS[key] = asyncio.create_task(worker())
            await event.delete()
        except Exception: pass

    @client.on(events.NewMessage(pattern=r'\.spam\s+(.+)'))
    async def continuous_spam(event):
        if not await check_auth(event): return
        text = event.pattern_match.group(1)
        chat_id = event.chat_id
        key = f"spam_{chat_id}_{time.time()}"
        async def worker():
            while True:
                await client.send_message(chat_id, text)
                await asyncio.sleep(0.5)
        ACTIVE_LOOPS[key] = asyncio.create_task(worker())
        try: await event.delete()
        except Exception: pass

    @client.on(events.NewMessage(pattern=r'\.sspam'))
    async def stop_continuous_spam(event):
        if not await check_auth(event): return
        chat_id = event.chat_id
        count = 0
        for k, t in list(ACTIVE_LOOPS.items()):
            if f"_{chat_id}_" in k:
                t.cancel()
                del ACTIVE_LOOPS[k]
                count += 1
        await edit_or_reply(event, f"🛑 *𝐒ᴛᴏᴩᴩᴇᴅ {count} ꜱᴩᴀᴍ ᴛᴀꜱᴋꜱ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.lock\s+(.+)'))
    async def target_lock(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        ACTIVE_LOOPS[f"lock_{event.chat_id}_{reply.sender_id}"] = event.pattern_match.group(1)
        await event.delete()

    @client.on(events.NewMessage(pattern=r'\.slock'))
    async def stop_lock(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        key = f"lock_{event.chat_id}_{reply.sender_id}"
        if key in ACTIVE_LOOPS:
            del ACTIVE_LOOPS[key]
            await edit_or_reply(event, "🔓 *𝐔ɴʟᴏᴄᴋᴇᴅ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.ar'))
    async def start_auto_reply(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        AUTO_REPLY_TARGETS[f"ar_{event.chat_id}_{reply.sender_id}"] = 0
        await edit_or_reply(event, "🤖 *𝐀ᴜᴛᴏ-𝐑ᴇᴩʟʏ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.sar'))
    async def stop_auto_reply(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        key = f"ar_{event.chat_id}_{reply.sender_id}"
        if key in AUTO_REPLY_TARGETS:
            del AUTO_REPLY_TARGETS[key]
            await edit_or_reply(event, "🛑 *𝐀ᴜᴛᴏ-𝐑ᴇᴩʟʏ ꜱᴛᴏᴩᴩᴇᴅ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.art\s*(.*)'))
    async def start_auto_react(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        emoji = event.pattern_match.group(1).strip() or "🔥"
        AUTO_REACT_TARGETS[f"art_{event.chat_id}_{reply.sender_id}"] = emoji
        await edit_or_reply(event, f"❤️ *𝐀ᴜᴛᴏ-𝐑ᴇᴀᴄᴛ ᴀᴄᴛɪᴠᴇ:* {emoji} ✨")

    @client.on(events.NewMessage(pattern=r'\.sart'))
    async def stop_auto_react(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        key = f"art_{event.chat_id}_{reply.sender_id}"
        if key in AUTO_REACT_TARGETS:
            del AUTO_REACT_TARGETS[key]
            await edit_or_reply(event, "🛑 *𝐀ᴜᴛᴏ-𝐑ᴇᴀᴄᴛ ꜱᴛᴏᴩᴩᴇᴅ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.m$'))
    async def local_mute(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        LOCAL_MUTES.add((event.chat_id, reply.sender_id))
        await edit_or_reply(event, "🔇 *𝐋ᴏᴄᴀʟʟʏ 𝐌ᴜᴛᴇᴅ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.gm$'))
    async def global_mute(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        GLOBAL_MUTES.add(reply.sender_id)
        await edit_or_reply(event, "🔇 *𝐆ʟᴏʙᴀʟʟʏ 𝐌ᴜᴛᴇᴅ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.sm$'))
    async def stop_mute(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        uid = reply.sender_id
        LOCAL_MUTES.discard((event.chat_id, uid))
        GLOBAL_MUTES.discard(uid)
        await edit_or_reply(event, "🔊 *𝐔ɴᴍᴜᴛᴇᴅ!* ✨")

    # --- VEGETA COMMANDS ---
    VEGETA_TEXTS = [
        "𝔗ᴇʳⁱ  𝔐ᴀᵃ  𝔎ᴇ  𝔊ʜᵘᵗ  𝔓ᴇ  𝔓ɪʸᵃᶻ  𝔎ᴀᵗᵘⁿᵍᵃ  𝔗ᴏ  𝔗ᴇʳⁱ  𝔐ᴀᵃ  𝔜ᴏʸᵉᵍⁱ  𝔜ᴀ  𝔊ʜⁱˡˡᴀʸᵉᵍⁱ",
        "𓂃☁︎ 𓂃𝘚ɪᴅᴇ 𝘏ᴀᴛ 𝘎ᴜʟᴀ𝘮 𝘛ᴇʀʏ 𝘔ᴀᴀ 𝘒ᴏ 𝘊ʜᴏᴅɴᴇ मेरी रेलगाड़ी आ रही .-‘🚂-‘.ᯓᡣ𐭩 𓂃☁︎ 𓂃",
        "𝕽𝕬𝕹𝕯𝖄𝕶𝕰 ᴛᴇʀɪ ᴍᴀ 𝔍ℑ𝔒 𝔎𝔈 𝔗ℜ𝔄𝔑𝔖𝔉𝔄𝔐𝔄 🅜🅔 𝐁𝐀𝐈𝐓𝐇𝐀 𝒦ℰ 𝒞𝒪𝒟𝒰𝒢𝒜 ℛ𝒜𝒩𝒟𝒴𝒦𝒰 𝓛𝓐𝓓𝓚𝓔 🔥🔥🤟",
        "𝘛𝘌𝘙𝘐 𝘔𝘔𝘠 𝘒𝘐 𝘔𝘔𝘚 𝘝𝘐𝘙𝘈𝘓 𝘏𝘜𝘐 𝘛𝘝 𝘗𝘌𝘙 𝘎𝘙𝘌𝘌𝘉 𝘒𝘌 𝘉𝘈𝘊𝘏𝘌 🤣🤏 ☆𝘴𝘤𝘳𝘪𝘱𝘵 𝘣𝘺☆ 𝘍𝘺𝘵𝘦𝘳 𝘝𝘦𝘨𝘦𝘵𝘢⃟🏴‍☠️",
        "𝘛‌🇪‌🇷‌🇮‌ 🇲‌🇲‌🇾‌ 🇰‌🇴‌ 🇧‌🇭‌🇦‌🇷‌🇪‌ 🇧‌🇦‌🇿‌🇦‌🇷‌ 🇲‌🇪‌ 𝙓‌🇭‌🇴‌🇩‌🇦‌ 𝙂‌🇷‌🇪‌🇪‌ 😔💔 𝘴𝘤𝘳𝘪𝘱𝘵 by ~𝘍𝘺𝘵𝘦𝘳 𝘝𝘦𝘨𝘦𝘵𝘢⃟🏴‍☠️",
        "𝘛𝘌𝘙𝘐 𝘔𝘔𝘠 𝘒𝘖 𝘋𝘏𝘜𝘋 𝘔𝘌 𝘓𝘈𝘛 𝘗𝘈𝘛 𝙓𝘏𝘖𝘋𝘈 😙🤌 𝘚𝘊𝘙𝘐𝘗𝘛 𝘉𝘠 ~𝘍𝘺𝘵𝘦𝘳 𝘝𝘦𝘨𝘦𝘵𝘢⃟🏴‍☠️",
        "𝘛𝘌𝘙𝘐 𝘔𝘔𝘠 𝘒𝘖 𝘒𝘏𝘜𝘕 𝘔𝘌 𝘓𝘈𝘛 𝘗𝘈𝘛 𝙓𝘏𝘖𝘋𝘜 𝘎𝘙𝘌𝘌𝘉 𝘠🐾 ☆𝘚𝘊𝘙𝘐𝘗𝘛 𝘉𝘠☆ 𝘓𝘰𝘳𝘥 𝘝𝘦𝘨𝘦𝘵𝘢",
        "𝘛𝘌𝘙𝘐 𝘔𝘔𝘠 𝘒𝘖 𝘏𝘈𝘛𝘏𝘐 𝘒𝘌 𝘉𝘈𝘊𝘏𝘌 𝘕𝘌 𝙓𝘏𝘖𝘋𝘈 🐘🎀 ☆𝘚𝘊𝘙𝘐𝘗𝘛 𝘉𝘠☆ ~𝘓𝘰𝘳𝘥 𝘝𝘦𝘨𝘦𝘵𝘢😉",
        "𝘛3𝘙𝘐 𝘔𝘔𝘠 𝘒𝘐 𝙓𝘏𝘜𝘛 𝘔𝘌 𝘉𝘔𝘞 𝘚𝘌 𝘋𝘙𝘐𝘍𝘛𝘐𝘕𝓖 𝘒𝘙𝘜 😙 𝘚𝘊𝘙𝘐𝘗𝘛 𝘉𝘠 𝘓𝘰𝘳𝘥 𝘝𝘦𝘨𝘦𝘵𝘢",
        "𝘛𝘌𝘙𝘌 𝘔𝘈 𝘒𝘖 𝘑𝘐𝘖 𝘒𝘌 𝘛𝘖𝘞𝘌𝘙 𝘔𝘌 𝘉𝘈𝘐𝘛𝘏𝘈 𝘋𝘜𝓖𝘈 𝘙𝘈𝘈𝘛 𝘉𝘏𝘈𝘙 𝘔𝘈𝘑𝘌 𝘓𝘌𝓖𝘐 🌞 𝘚𝘛𝘏 𝘔𝘌 𝘗𝘜𝘙𝘈 𝘔𝘖𝘏𝘓𝘓𝘈 𝘉𝘏𝘈𝘐 𝘓𝘌𝓖𝚂 🎀 𝘔𝘈𝘑𝘌 𝘔𝘈𝘑𝘌 🤤🌚 𝘚𝘊𝘙𝘐𝘗𝘛 𝘉𝘠 - 𝘓𝘰𝘳𝘥 𝘝𝘦𝘨𝘦𝘵𝘢"
    ]
    AUTO_REPLY_TARGETS_VEGETA = {}

    @client.on(events.NewMessage(pattern=r'\.arvegeta'))
    async def start_auto_reply_vegeta(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        AUTO_REPLY_TARGETS_VEGETA[f"arvegeta_{event.chat_id}_{reply.sender_id}"] = 0
        await edit_or_reply(event, "🤖 *𝐕ᴇɢᴇᴛᴀ 𝐀ᴜᴛᴏ-𝐑ᴇᴩʟʏ ᴀᴄᴛɪᴠᴀᴛᴇᴅ!* ✨")

    @client.on(events.NewMessage(pattern=r'\.sarvegeta'))
    async def stop_auto_reply_vegeta(event):
        if not await check_auth(event): return
        reply = await event.get_reply_message()
        if not reply: return await edit_or_reply(event, "❌ *𝐑ᴇᴩʟʏ ᴛᴏ ᴜꜱᴇʀ!* ⚠️")
        key = f"arvegeta_{event.chat_id}_{reply.sender_id}"
        if key in AUTO_REPLY_TARGETS_VEGETA:
            del AUTO_REPLY_TARGETS_VEGETA[key]
            await edit_or_reply(event, "🛑 *𝐕ᴇɢᴇᴛᴀ 𝐀ᴜᴛᴏ-𝐑ᴇᴩʟʏ ꜱᴛᴏᴩᴩᴇᴅ!* ✨")

    @client.on(events.NewMessage())
    async def monitor(event):
        try:
            chat_id, sender_id = event.chat_id, event.sender_id
            me = await client.get_me()
            
            if ANTIDEL_ENABLED and event.text:
                ANTIDEL_CACHE[event.id] = {'chat_id': chat_id, 'text': event.text}

            if chat_id in WATCH_SPAM_CONFIG and sender_id != me.id:
                cfg = WATCH_SPAM_CONFIG[chat_id]
                now = time.time()
                logs = cfg["logs"].get(sender_id, [])
                logs = [t for t in logs if now - t < cfg["sec"]]
                logs.append(now)
                cfg["logs"][sender_id] = logs
                if len(logs) > cfg["limit"]:
                    try:
                        await event.delete()
                        return
                    except Exception: pass

            art_key = f"art_{chat_id}_{sender_id}"
            if art_key in AUTO_REACT_TARGETS:
                try:
                    await client(SendReactionRequest(peer=chat_id, msg_id=event.id, reaction=[ReactionEmoji(emoticon=AUTO_REACT_TARGETS[art_key])]))
                except Exception: pass

            if sender_id == me.id or event.out: return

            if sender_id in GLOBAL_MUTES or (chat_id, sender_id) in LOCAL_MUTES:
                try: await event.delete()
                except Exception: pass
                return

            lock_key = f"lock_{chat_id}_{sender_id}"
            if lock_key in ACTIVE_LOOPS:
                await event.reply(ACTIVE_LOOPS[lock_key])
                return

            arvegeta_key = f"arvegeta_{chat_id}_{sender_id}"
            if arvegeta_key in AUTO_REPLY_TARGETS_VEGETA:
                idx = AUTO_REPLY_TARGETS_VEGETA[arvegeta_key]
                await event.reply(VEGETA_TEXTS[idx])
                AUTO_REPLY_TARGETS_VEGETA[arvegeta_key] = (idx + 1) % len(VEGETA_TEXTS)
                return

            ar_key = f"ar_{chat_id}_{sender_id}"
            if ar_key in AUTO_REPLY_TARGETS:
                idx = AUTO_REPLY_TARGETS[ar_key]
                await event.reply(CUSTOM_AUTO_REPLY_TEXTS[idx])
                AUTO_REPLY_TARGETS[ar_key] = (idx + 1) % len(CUSTOM_AUTO_REPLY_TEXTS)
        except Exception:
            pass

    @client.on(events.NewMessage(pattern=r'\.ping'))
    async def ping(event):
        if not await check_auth(event): return
        start = time.time()
        msg = await event.reply("🏓 *𝐏ɪɴɢɪɴɢ...* ⏳")
        await msg.edit(f"🏓 *𝐏ᴏɴɢ!* `{round((time.time() - start) * 1000)}ms` ✨")

    @client.on(events.NewMessage(pattern=r'\.uptime'))
    async def uptime(event):
        if not await check_auth(event): return
        await edit_or_reply(event, f"⏳ *𝐔ᴩᴛɪᴍᴇ:* `{str(timedelta(seconds=int(time.time() - START_TIME)))}` ✨")

    @client.on(events.NewMessage(pattern=r'\.stopall'))
    async def stopall(event):
        if not await check_auth(event): return
        for t in ACTIVE_LOOPS.values(): 
            if isinstance(t, asyncio.Task): t.cancel()
        ACTIVE_LOOPS.clear()
        AUTO_REPLY_TARGETS.clear()
        AUTO_REPLY_TARGETS_VEGETA.clear()
        AUTO_REACT_TARGETS.clear()
        LOCAL_MUTES.clear()
        GLOBAL_MUTES.clear()
        if PFP_ROTATE_TASK:
            PFP_ROTATE_TASK.cancel()
        await edit_or_reply(event, "🛑 *𝐀ʟʟ ᴀᴄᴛɪᴠᴇ ᴛᴀꜱᴋꜱ ꜱᴛᴏᴩᴩᴇᴅ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ!* ✨")


# ==================== TELEGRAM MANAGER BOT ====================

# FIXED: Added infinite connection retries and delay to prevent Termux timeout crashes
bot = TelegramClient(
    'manager_bot_session', 
    API_ID, 
    API_HASH, 
    connection_retries=-1, 
    retry_delay=5
)

async def check_forced_channels(event, user_id):
    if not FORCED_CHANNELS:
        return True
    
    not_joined = []
    for ch in FORCED_CHANNELS:
        try:
            clean_ch = ch.strip()
            if "t.me/" in clean_ch:
                clean_ch = "@" + clean_ch.split("/")[-1]
            elif not clean_ch.startswith("@") and not clean_ch.startswith("-"):
                clean_ch = "@" + clean_ch
                
            entity = await bot.get_entity(clean_ch)
            await bot(GetParticipantRequest(entity, user_id))
        except UserNotParticipantError:
            not_joined.append(ch)
        except Exception:
            pass
            
    if not_joined:
        buttons = []
        for ch in not_joined:
            ch_clean = ch.replace('https://t.me/', '').replace('t.me/', '').replace('@', '')
            buttons.append([Button.url(f"𝐉𝐎𝐈𝐍 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 📢", url=f"https://t.me/{ch_clean}")])
        buttons.append([Button.inline("🔄 𝐂𝐇𝐄𝐂𝐊 𝐉𝐎𝐈𝐍 𝐒𝐓𝐀𝐓𝐔𝐒 ✨", data="check_join")])
        buttons.append([Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")])
        
        try:
            await event.edit(
                "*Please join the required channels below before using the bot. Click 'CHECK JOIN STATUS' after joining.* 💎",
                buttons=buttons
            )
        except Exception:
            await event.respond(
                "*Please join the required channels below before using the bot. Click 'CHECK JOIN STATUS' after joining.* 💎",
                buttons=buttons
            )
        return False
    return True

@bot.on(events.NewMessage(pattern=r'/start'))
async def bot_start(event):
    if not event.is_private: return
    
    uid = event.sender_id
    sender = await event.get_sender()
    
    # FIXED: Clear any stuck registration wizard states immediately when /start is sent
    if uid in USER_REG_DATA:
        del USER_REG_DATA[uid]
    
    if uid != ADMIN_CHAT_ID:
        username_str = f"@{sender.username}" if (sender and sender.username) else f"No Username (ID: `{uid}`)"
        try:
            await bot.send_message(
                ADMIN_CHAT_ID,
                f"?? *𝐍ᴇᴡ 𝐔ꜱᴇʀ 𝐒ᴛᴀʀᴛᴇᴅ 𝐓ʜᴇ 𝐁ᴏᴛ!*\n\n"
                f"👤 *𝐔ꜱᴇʀ:* {username_str}\n"
                f"🆔 *𝐔ꜱᴇʀ 𝐈𝐃:* `{uid}`"
            )
            if not (sender and sender.username):
                await bot.forward_messages(ADMIN_CHAT_ID, event.message)
        except Exception:
            pass
    
    if not await check_forced_channels(event, uid):
        return
        
    HOSTED_USERS.add(uid)
    HOSTED_USER_ENTITIES[uid] = sender
    
    if uid == ADMIN_CHAT_ID:
        buttons = [
            [Button.inline("𝐇𝐎𝐒𝐓 𝐘𝐎𝐔𝐑 𝐁𝐎𝐓𝐒 🎀", data="host_bot")],
            [Button.inline("𝐀𝐃𝐃 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 ➕", data="add_channel"), Button.inline("𝐑𝐄𝐌𝐎𝐕𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 ➖", data="remove_channel")],
            [Button.inline("📋 𝐕𝐈𝐄𝐖 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒", data="list_channels"), Button.inline("👥 𝐋𝐈𝐒𝐓 𝐌𝐄𝐌𝐁𝐄𝐑𝐒", data="list_members")],
            [Button.inline("𝐆𝐔𝐈𝐃𝐄: 𝐆𝐄𝐓 𝐀𝐏𝐈 𝐈𝐃 & 𝐇𝐀𝐒𝐇 📖", data="guide"), Button.inline("𝐇𝐄𝐋𝐏 🤎", data="help")],
            [Button.inline("𝐒𝐔𝐏𝐏𝐎𝐑𝐓 & 𝐑𝐄𝐏𝐎𝐑𝐓 𝐈𝐒𝐒𝐔𝐄 ❤️", data="support")],
            [Button.inline("𝐒𝐄𝐍𝐃 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 📢", data="broadcast")],
            [Button.inline("𝐋𝐎𝐆𝐎𝐔𝐓 💙", data="logout")]
        ]
    else:
        buttons = [
            [Button.inline("𝐇𝐎𝐒𝐓 𝐘𝐎𝐔𝐑 𝐁𝐎𝐓𝐒 🎀", data="host_bot")],
            [Button.inline("𝐆𝐔𝐈𝐃𝐄: 𝐆𝐄𝐓 𝐀𝐏𝐈 𝐈𝐃 & 𝐇𝐀𝐒𝐇 📖", data="guide"), Button.inline("𝐇𝐄𝐋𝐏 🤎", data="help")],
            [Button.inline("𝐒𝐔𝐏𝐏𝐎𝐑𝐓 & 𝐑𝐄𝐏𝐎𝐑𝐓 𝐈𝐒𝐒𝐔𝐄 ❤️", data="support")],
            [Button.inline("𝐋𝐎𝐆𝐎𝐔𝐓 💙", data="logout")]
        ]
    
    welcome_text = (
        "✨ *𝐖ᴇʟᴄᴏᴍᴇ ᴛᴏ 𝐔𝐒𝐄𝐑𝐇𝐎𝐒𝐓 𝐁𝐎𝐓!* ✨\n\n"
        "𝐂ʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ꜱᴀꜰᴇʟʏ ᴅᴇᴩʟᴏʏ ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ. "
        "𝐘ᴏᴜʀ ꜱᴇꜱꜱɪᴏɴ ʀᴇᴍᴀɪɴꜱ ᴄᴏᴍᴩʟᴇᴛᴇʟʏ ꜱᴇᴄᴜʀᴇ. 💛"
    )
    await event.reply(welcome_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'main_menu'))
async def main_menu_callback(event):
    await event.answer()
    uid = event.sender_id
    if uid in USER_REG_DATA:
        del USER_REG_DATA[uid]
        
    if not await check_forced_channels(event, uid):
        return
        
    if uid == ADMIN_CHAT_ID:
        buttons = [
            [Button.inline("𝐇𝐎𝐒𝐓 𝐘𝐎𝐔𝐑 𝐁𝐎𝐓𝐒 🎀", data="host_bot")],
            [Button.inline("𝐀𝐃𝐃 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 ➕", data="add_channel"), Button.inline("𝐑𝐄𝐌𝐎𝐕𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 ➖", data="remove_channel")],
            [Button.inline("📋 𝐕𝐈𝐄𝐖 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒", data="list_channels"), Button.inline("👥 𝐋𝐈𝐒𝐓 𝐌𝐄𝐌𝐁𝐄𝐑𝐒", data="list_members")],
            [Button.inline("𝐆𝐔𝐈𝐃𝐄: 𝐆𝐄𝐓 𝐀𝐏𝐈 𝐈𝐃 & 𝐇𝐀𝐒𝐇 📖", data="guide"), Button.inline("𝐇𝐄𝐋𝐏 🤎", data="help")],
            [Button.inline("𝐒𝐔𝐏𝐏𝐎𝐑𝐓 & 𝐑𝐄𝐏𝐎𝐑𝐓 𝐈𝐒𝐒𝐔𝐄 ❤️", data="support")],
            [Button.inline("𝐒𝐄𝐍𝐃 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 📢", data="broadcast")],
            [Button.inline("𝐋𝐎𝐆𝐎𝐔𝐓 💙", data="logout")]
        ]
    else:
        buttons = [
            [Button.inline("𝐇𝐎𝐒𝐓 𝐘𝐎𝐔𝐑 𝐁𝐎𝐓𝐒 🎀", data="host_bot")],
            [Button.inline("𝐆𝐔𝐈𝐃𝐄: 𝐆𝐄𝐓 𝐀𝐏𝐈 𝐈𝐃 & 𝐇𝐀𝐒𝐇 📖", data="guide"), Button.inline("𝐇𝐄𝐋𝐏 🤎", data="help")],
            [Button.inline("𝐒𝐔𝐏𝐏𝐎𝐑𝐓 & 𝐑𝐄𝐏𝐎𝐑𝐓 𝐈𝐒𝐒𝐔𝐄 ❤️", data="support")],
            [Button.inline("𝐋𝐎ɢᴏ𝐔ᴛ 💙", data="logout")]
        ]
    
    welcome_text = (
        "✨ *𝐖ᴇʟᴄᴏᴍᴇ ᴛᴏ 𝐔𝐒𝐄𝐑𝐇𝐎𝐒𝐓 𝐁𝐎𝐓!* ✨\n\n"
        "𝐂ʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ꜱᴀꜰᴇʟʏ ᴅᴇᴩʟᴏʏ ʏᴏᴜʀ ᴜꜱᴇʀʙᴏᴛ. "
        "𝐘ᴏᴜʀ ꜱᴇꜱꜱɪᴏɴ ʀᴇᴍᴀɪɴꜱ ᴄᴏᴍᴩʟᴇᴛᴇʟʏ ꜱᴇᴄᴜʀᴇ. 💛"
    )
    try:
        await event.edit(welcome_text, buttons=buttons)
    except Exception:
        await event.respond(welcome_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'host_bot'))
async def host_callback(event):
    await event.answer()
    uid = event.sender_id
    
    if not await check_forced_channels(event, uid):
        return
        
    USER_REG_DATA[uid] = {'step': 'api_id'}
    buttons = [
        [Button.inline("❌ 𝐂𝐀𝐍𝐂𝐄𝐋 / 🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit(
        "👋 *𝐖ᴇʟᴄᴏᴍᴇ ᴛᴏ 𝐔𝐒𝐄𝐑𝐇𝐎𝐒𝐓 𝐁𝐎𝐓!* 🚀✨\n\n"
        "👉 *𝐀ᴩɴᴀ 𝐀𝐏𝙸 𝐈ᴅ 𝐁ʜᴇᴊᴇ* *(𝐍ᴜᴍʙᴇʀ ᴍeɪɴ)*: 💎",
        buttons=buttons
    )

@bot.on(events.CallbackQuery(data=b'check_join'))
async def check_join_callback(event):
    await event.answer("Checking your subscriptions...")
    uid = event.sender_id
    if await check_forced_channels(event, uid):
        if uid == ADMIN_CHAT_ID:
            buttons = [
                [Button.inline("𝐇𝐎𝐒𝐓 𝐘𝐎𝐔𝐑 ᴀᴄᴄ 🎀", data="host_bot")],
                [Button.inline("𝐀𝐃𝐃 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 ➕", data="add_channel"), Button.inline("𝐑𝐄𝐌𝐎𝐕𝐄 𝐂𝐇𝐀𝐍𝐍𝐄𝐋 ➖", data="remove_channel")],
                [Button.inline("📋 𝐕𝐈𝐄𝐖 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒", data="list_channels"), Button.inline("👥 𝐋𝐈𝐒𝐓 𝐌𝐄𝐌𝐁𝐄𝐑𝐒", data="list_members")],
                [Button.inline("𝐆𝐔𝐈𝐃𝐄: 𝐆𝐄𝐓 𝐀𝐏𝐈 𝐈𝐃 & 𝐇𝐀𝐒𝐇 📖", data="guide"), Button.inline("𝐇𝐄𝐋𝐏 🤎", data="help")],
                [Button.inline("𝐒𝐔𝐏𝐏𝐎𝐑𝐓 & 𝐑𝐄𝐏𝐎𝐑𝐓 𝐈𝐒𝐒𝐔𝐄 ❤️", data="support")],
                [Button.inline("𝐒𝐄𝐍𝐃 𝐁𝐑𝐎𝐀𝐃𝐂𝐀𝐒𝐓 📢", data="broadcast")],
                [Button.inline("𝐋𝐎𝐆𝐎𝐔𝐓 💙", data="logout")]
            ]
        else:
            buttons = [
                [Button.inline("𝐇𝐎𝐒𝐓 𝐘𝐎𝐔𝐑 ᴀᴄᴄ 🎀", data="host_bot")],
                [Button.inline("𝐆𝐔𝐈𝐃𝐄: 𝐆𝐄𝐓 𝐀𝐏𝐈 𝐈𝐃 & 𝐇𝐀𝐒𝐇 📖", data="guide"), Button.inline("𝐇𝐄𝐋𝐏 🤎", data="help")],
                [Button.inline("𝐒𝐔𝐏𝐏𝐎𝐑𝐓 & 𝐑𝐄𝐏𝐎𝐑𝐓 𝐈𝐒𝐒𝐔𝐄 ❤️", data="support")],
                [Button.inline("𝐋𝐎𝐆𝐎𝐔𝐓 💙", data="logout")]
            ]
        await event.edit(
            "*Thank you for joining! You can now use the bot freely.* ✨\n\n"
            "✨ *𝐖ᴇʟᴄᴏᴍᴇ ᴛᴏ 𝐔𝐒𝐄𝐑𝐇𝐎𝐒𝐓 𝐁ᴏᴛ!* ✨",
            buttons=buttons
        )
    else:
        await event.answer("❌ *You have not joined all channels yet! Please join first.* ⚠️", alert=True)

@bot.on(events.CallbackQuery(data=b'guide'))
async def guide_callback(event):
    await event.answer()
    uid = event.sender_id
    if not await check_forced_channels(event, uid):
        return
    buttons = [
        [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit("📖 *𝐆ᴜɪᴅᴇ:* 𝐀ᴩɴɪ 𝐀𝐏𝐈 𝐈𝐃 ᴀᴜʀ 𝐀𝐏𝐈 𝐇ᴀꜱʜ ʟᴇɴᴇ ᴋᴇ ʟɪʏᴇ `my.telegram.org` ᴩᴀʀ ᴊᴀʏᴇɪɴ ᴀᴜʀ ᴀᴩᴩ ᴄʀᴇᴀᴛᴇ ᴋᴀʀᴇɪɴ. ✨", buttons=buttons)

@bot.on(events.CallbackQuery(data=b'help'))
async def help_callback(event):
    await event.answer()
    uid = event.sender_id
    if not await check_forced_channels(event, uid):
        return
    buttons = [
        [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit("🤎 *𝐇ᴇʟᴩ:* 𝐁ᴏᴛ ʜᴏꜱᴛ ᴋᴀʀɴᴇ ᴍᴇɪɴ ᴋᴏɪ ᴅɪᴋᴋᴀᴛ ᴀᴀʏᴇ ᴛᴏʜ ꜱᴜᴩᴩᴏʀᴛ ꜱᴇ ᴄᴏɴᴛᴀᴄᴛ ᴋᴀʀᴇɪɴ. @undeaddprincce ✨", buttons=buttons)

@bot.on(events.CallbackQuery(data=b'support'))
async def support_callback(event):
    await event.answer()
    uid = event.sender_id
    if not await check_forced_channels(event, uid):
        return
    USER_REG_DATA[event.sender_id] = {'step': 'support_msg'}
    buttons = [
        [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit("❤️ *𝐏ʟᴇᴀꜱᴇ ᴛʏᴩᴇ ʏᴏᴜʀ ɪꜱꜱᴜᴇ/ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ꜱᴇɴᴅ ᴏᴡɴᴇʀ:*\n\n(𝐀ᴩɴᴀ ᴍᴇꜱꜱᴀɢᴇ ʏᴀʜᴀɴ ᴛʏᴩᴇ ᴋᴀര്‍ᴋᴇ ْبhejiy𝙚, 𝙬𝙤𝙝 ꜱᴇeD𝙝𝙖 ᴏᴡɴᴇʀ ᴋᴇ ᴩᴀᴀꜱ ᴄHᴀʟᴀ ᴊᴀʏᴇɢᴀ) ✨", buttons=buttons)

@bot.on(events.CallbackQuery(data=b'add_channel'))
async def add_channel_callback(event):
    if event.sender_id != ADMIN_CHAT_ID:
        await event.answer("❌ You are not the owner!", alert=True)
        return
    await event.answer()
    USER_REG_DATA[event.sender_id] = {'step': 'add_channel_input'}
    buttons = [
        [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit("➕ *𝙆𝙧𝙞𝙥𝙮𝙖 𝙬𝙤𝙝 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 𝙐𝙨𝙚𝙧𝙣𝙖𝙢𝙚 𝙮𝙖 𝙇𝙞𝙣𝙠 𝙗𝙝𝙚.send_message𝙧𝙣𝙖* -> *𝙆𝙧𝙞𝙥𝙮𝙖 𝙬𝙤𝙝 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 𝙐𝙨𝙚𝙧𝙣𝙖𝙢𝙚 𝙮𝙖 𝙇𝙞𝙣𝙠 𝙗𝙝𝙚𝙟𝙞y𝙚 (𝙟𝙖𝙞𝙨𝙚 `@mychannel` ya `https://t.me/mychannel`):* ✨", buttons=buttons)

@bot.on(events.CallbackQuery(data=b'remove_channel'))
async def remove_channel_callback(event):
    if event.sender_id != ADMIN_CHAT_ID:
        await event.answer("❌ You are not the owner!", alert=True)
        return
    await event.answer()
    if not FORCED_CHANNELS:
        buttons = [
            [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
        ]
        await event.edit("⚠️ *Koi bhi channel add nahi hai filhal!* 🛑", buttons=buttons)
        return
        
    USER_REG_DATA[event.sender_id] = {'step': 'remove_channel_input'}
    ch_list = "\n".join([f"• `{ch}`" for ch in FORCED_CHANNELS])
    buttons = [
        [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit(f"➖ *Current Added Channels:*\n{ch_list}\n\n👉 *𝙆𝙧𝙞𝙥𝙮𝙖 𝙬𝙤𝙝 𝘾𝙝𝙖𝙣𝙣𝙚𝙡 𝙐𝙨𝙚𝙧𝙣𝙖𝙢𝙚 𝙗𝙝𝙚𝙟𝙞y𝙚 𝙟𝙤 remove krna hai:* ✨", buttons=buttons)

@bot.on(events.CallbackQuery(data=b'list_channels'))
async def list_channels_callback(event):
    if event.sender_id != ADMIN_CHAT_ID:
        await event.answer("❌ You are not the owner!", alert=True)
        return
    await event.answer()
    if not FORCED_CHANNELS:
        ch_text = "⚠️ *Filhal koi bhi forced channel add nahi hai!*"
    else:
        ch_list = "\n".join([f"{i+1}. `{ch}`" for i, ch in enumerate(FORCED_CHANNELS)])
        ch_text = f"📋 *Total Added Channels ({len(FORCED_CHANNELS)}):*\n\n{ch_list}"
    
    buttons = [
        [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit(ch_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'list_members'))
async def list_members_callback(event):
    if event.sender_id != ADMIN_CHAT_ID:
        await event.answer("❌ Sirf owner isko use kr sakta hai! ⚠️", alert=True)
        return
    await event.answer()
    
    if not HOSTED_USERS:
        member_text = "⚠️ *Abhi tak kisi bhi user ne bot se bot host nahi kiya hai!*"
    else:
        member_lines = []
        for i, uid in enumerate(HOSTED_USERS, 1):
            sender = HOSTED_USER_ENTITIES.get(uid)
            if sender and sender.username:
                member_lines.append(f"{i}. @{sender.username} (ID: `{uid}`)")
            else:
                member_lines.append(f"{i}. No Username (ID: `{uid}`)")
        member_text = f"👥 *Hosted Members List ({len(HOSTED_USERS)}):*\n\n" + "\n".join(member_lines)
        
    buttons = [
        [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit(member_text, buttons=buttons)

@bot.on(events.CallbackQuery(data=b'broadcast'))
async def broadcast_callback(event):
    if event.sender_id != ADMIN_CHAT_ID:
        await event.answer("❌ You are not the owner!", alert=True)
        return
    await event.answer()
    USER_REG_DATA[event.sender_id] = {'step': 'broadcast_msg'}
    buttons = [
        [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit("📢 *𝐊ʀɪᴩʏ𝙖 ᴡᴏʜ ᴍᴇꜱꜱᴀɢᴇ/ᴀɴɴᴏᴜɴᴄᴇᴍᴇɴᴛ ᴛʏᴩᴇ ᴋᴀʀᴇɪɴ ᴊᴏ ᴀᴀᴩᴋᴏ ꜱᴀʙʜɪ ᴜꜱᴇʀꜱ ᴋᴏ ʙʜᴇᴊɴᴀ ʜᴀɪ:* ✨", buttons=buttons)

@bot.on(events.CallbackQuery(data=b'logout'))
async def logout_callback(event):
    await event.answer()
    uid = event.sender_id
    if uid in USER_REG_DATA:
        del USER_REG_DATA[uid]
    buttons = [
        [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
    ]
    await event.edit("💙 *𝐀ᴀᴩ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʟᴏɢᴏᴜᴛ/ʀᴇꜱᴇᴛ ʜᴏ ᴄHᴜᴋᴇ ʜᴀɪɴ. 𝐃ᴏʙᴀʀᴀ `/start` ʙʜᴇᴊɪʏᴇ.* ✨", buttons=buttons)

@bot.on(events.ChatAction)
async def monitor_channel_leaves(event):
    if not event.user_left and not event.user_kicked:
        return
    user_id = event.user_id
    if user_id in HOSTED_USERS and user_id != ADMIN_CHAT_ID:
        for ch in FORCED_CHANNELS:
            try:
                clean_ch = ch.strip()
                if "t.me/" in clean_ch:
                    clean_ch = "@" + clean_ch.split("/")[-1]
                elif not clean_ch.startswith("@") and not clean_ch.startswith("-"):
                    clean_ch = "@" + clean_ch
                    
                entity = await bot.get_entity(clean_ch)
                if event.chat_id == entity.id:
                    HOSTED_USERS.discard(user_id)
                    HOSTED_USER_ENTITIES.pop(user_id, None)
                    try:
                        await bot.send_message(
                            user_id,
                            "*You have left the mandatory channel! Your userbot session has been automatically stopped. Please join the channel again and send /start.* 🛑"
                        )
                    except Exception:
                        pass
                    break
            except Exception:
                continue

@bot.on(events.NewMessage())
async def bot_wizard(event):
    if not event.is_private: return
    uid = event.sender_id
    text = event.raw_text.strip()
    
    if text.startswith('/start'):
        if uid in USER_REG_DATA:
            del USER_REG_DATA[uid]
        return

    if uid not in USER_REG_DATA: return
    
    state = USER_REG_DATA[uid]['step']

    if state == 'add_channel_input':
        if uid != ADMIN_CHAT_ID:
            del USER_REG_DATA[uid]
            return
            
        ch_input = text.strip()
        if "t.me/" in ch_input:
            ch = "@" + ch_input.split("/")[-1]
        else:
            ch = ch_input if ch_input.startswith('@') else f"@{ch_input}"
            
        if ch not in FORCED_CHANNELS:
            FORCED_CHANNELS.append(ch)
            
        buttons = [
            [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
        ]
        await event.reply(f"✅ *Channel `{ch}` successfully add kar diya gaya hai!* ✨", buttons=buttons)
        del USER_REG_DATA[uid]
        return

    if state == 'remove_channel_input':
        if uid != ADMIN_CHAT_ID:
            del USER_REG_DATA[uid]
            return
        ch_input = text.strip()
        if "t.me/" in ch_input:
            ch = "@" + ch_input.split("/")[-1]
        else:
            ch = ch_input if ch_input.startswith('@') else f"@{ch_input}"
            
        if ch in FORCED_CHANNELS:
            FORCED_CHANNELS.remove(ch)
            await event.reply(f"✅ *Channel `{ch}` successfully remove kar diya gaya hai!* ✨")
        else:
            await event.reply(f"❌ *Channel `{ch}` list me nahi mila!* ⚠️")
        del USER_REG_DATA[uid]
        return

    if state == 'broadcast_msg':
        if uid != ADMIN_CHAT_ID:
            del USER_REG_DATA[uid]
            return
        
        await event.reply("⏳ *𝐁ʀᴏᴀᴅᴄᴀꜱᴛ ᴍᴇꜱꜱᴀɢᴇ ꜱᴀʙʜɪ ʀᴇɢɪꜱᴛᴇʀᴇᴅ ᴜꜱᴇʀꜱ/ᴄHᴀᴛꜱ ᴍᴇɪɴ ʙʜᴇᴊᴀ ᴊᴀ ʀᴀʜᴀ ʜᴀɪ...* ✨")
        
        count = 0
        broadcast_targets = list(HOSTED_USERS)
        for target_id in broadcast_targets:
            if target_id == ADMIN_CHAT_ID: continue
            try:
                await bot.send_message(
                    target_id,
                    f"📢 \n\n{text}"
                )
                count += 1
            except Exception: pass
            
        buttons = [
            [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
        ]
        await event.reply(f"✅ *𝐁ʀᴏᴀᴅᴄᴀꜱᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ {count} ᴜꜱᴇʀꜱ ᴋᴏ ʙʜᴇᴊ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ!* ✨", buttons=buttons)
        del USER_REG_DATA[uid]
        return

    if state == 'support_msg':
        sender = await event.get_sender()
        username_str = f"@{sender.username}" if (sender and sender.username) else f"No Username (ID: `{uid}`)"
        
        try:
            await bot.send_message(
                ADMIN_CHAT_ID,
                f"🚨 *𝐍ᴇᴡ 𝐒ᴜᴩᴩᴏʀᴛ / 𝐈ꜱꜱᴜᴇ 𝐑ᴇᴄᴇɪᴠᴇᴅ!*\n\n"
                f"👤 *𝐅ʀᴏᴍ:* {username_str}\n"
                f"💬 *𝐌ᴇꜱꜱᴀɢᴇ:* {text}"
            )
            if not (sender and sender.username):
                await bot.forward_messages(ADMIN_CHAT_ID, event.message)
                
            buttons = [
                [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await event.reply("✅ *𝐀ᴀᴩᴋᴀ ᴍᴇꜱꜱᴀɢᴇ/ɪꜱꜱᴜᴇ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ᴏᴡɴᴇʀ ᴋᴇ ᴩᴀᴀꜱ ʙʜᴇᴊ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ! 𝐒Hᴜʀᴜ ᴋᴀʀɴᴇ ᴋᴇ ʟɪʏᴇ `/start` ʙʜᴇᴊɪʏᴇ.* ✨", buttons=buttons)
        except Exception as e:
            await event.reply(f"❌ *𝐌ᴇꜱꜱᴀɢᴇ ꜱᴇɴᴅ ᴋᴀʀɴᴇ ᴍᴇɪɴ ᴇʀʀᴏʀ ᴀᴀʏᴀ:* `{e}` ⚠️")
        
        del USER_REG_DATA[uid]
        return

    if state == 'api_id':
        try:
            USER_REG_DATA[uid]['api_id'] = int(text)
            USER_REG_DATA[uid]['step'] = 'api_hash'
            buttons = [
                [Button.inline("❌ 𝐂𝐀𝐍𝐂𝐄𝐋 / 🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await event.reply("✅ *𝐀𝙿𝙸 𝐈ᴅ 𝐒ᴀᴠᴇᴅ!* ✨\n\n👉 *𝐀ʙ ᴀᴩɴɪ 𝐀𝐏𝙸 𝐇ᴀꜱH ʙʜᴇᴊɪʏᴇ:* 💎\n\n_(𝐍ᴏᴛᴇ: 𝐀ɢᴀʀ ᴄᴀɴᴄᴇʟ ᴋᴀʀɴᴀ ʜᴏ ᴛᴏʜ ʙᴀᴄᴋ ᴅᴀʙᴀʏᴇɪɴ)_", buttons=buttons)
        except ValueError:
            buttons = [
                [Button.inline("❌ 𝐂𝐀𝐍𝐂𝐄𝐋 / 🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await event.reply("❌ *𝐀𝙿𝙸 𝐈ᴅ ꜱɪʀꜰ ɴᴜᴍʙᴇʀꜱ ᴍᴇɪɴ ʜᴏɴɪ ᴄHᴀʜɪʏᴇ. 𝐃ᴏʙᴀʀᴀ ʙʜᴇᴊɪʏᴇ:* ⚠️", buttons=buttons)

    elif state == 'api_hash':
        USER_REG_DATA[uid]['api_hash'] = text
        USER_REG_DATA[uid]['step'] = 'phone'
        buttons = [
            [Button.inline("❌ 𝐂𝐀𝐍𝐂𝐄𝐋 / 🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
        ]
        await event.reply("✅ *𝐀𝙿𝙸 𝐇ᴀꜱH 𝐒ᴀᴠᴇᴅ!* ✨\n\n👉 *𝐀ʙ ᴀᴩɴᴀ 𝐏ʜᴏɴᴇ 𝐍ᴜᴍʙᴇʀ ᴄᴏᴜɴᴛʀʏ ᴄᴏᴅᴇ ᴋᴇ ꜱᴀᴛʜ ʙʜᴇᴊɪʏᴇ (ᴊᴀɪꜱᴇ `+919876543210`):* 📱", buttons=buttons)

    elif state == 'phone':
        USER_REG_DATA[uid]['phone'] = text
        msg = await event.reply("⏳ *𝐂ᴏɴɴᴇᴄᴛɪɴɢ & ꜱᴇɴᴅɪɴɢ 𝐎𝐓𝐏...* ✨")
        try:
            client = TelegramClient(StringSession(), USER_REG_DATA[uid]['api_id'], USER_REG_DATA[uid]['api_hash'])
            await client.connect()
            sent = await client.send_code_request(text)
            USER_REG_DATA[uid]['client'] = client
            USER_REG_DATA[uid]['hash'] = sent.phone_code_hash
            USER_REG_DATA[uid]['step'] = 'otp'
            
            for pct in range(10, 101, 30):
                await msg.edit(f"🚀 *𝐁ᴏᴛ ɪꜱ ꜱᴛᴀʀᴛɪɴɢ...* `{pct}%` ✨")
                await asyncio.sleep(0.3)
                
            buttons = [
                [Button.inline("❌ 𝐂𝐀𝐍𝐂𝐄𝐋 / 🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await msg.edit("✅ *𝐎𝐓𝐏 ʙʜᴇᴊ ᴅɪʏᴀ ɢᴀʏᴀ ʜᴀɪ!* ✨\n\n👉 *𝐀ʙ ᴀᴩɴᴀ 𝐎𝐓𝐏 ʙʜᴇᴊɪʏᴇ (𝐀ᴀɢᴀʀ ɴᴜᴍʙᴇʀꜱ ᴋᴇ ʙᴇᴇᴄH ᴍᴇɪɴ ꜱᴩᴀᴄᴇ ʜᴏ ᴊᴀɪꜱᴇ `1 2 3 4 5`):* (agar otp ke beech me space nhi lagaya to shyd problem aa sakti h)🥲🔑", buttons=buttons)
        except Exception as e:
            buttons = [
                [Button.inline("❌ 𝐂𝐀𝐍𝐂𝐄𝐋 / 🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await msg.edit(f"❌ *𝐂ᴏɴɴᴇᴄᴛɪᴏɴ ʏᴀ 𝐎𝐓𝐏 ᴇʀʀᴏʀ:* `{e}`\n\n_ᴋʀɪᴩʏᴀ ʙᴀᴄᴋ ᴅᴀʙᴀᴋᴀʀ ᴅᴏʙᴀʀᴀ ᴛʀʏ ᴋᴀʀᴇɪɴ._ ⚠️", buttons=buttons)
            if uid in USER_REG_DATA: del USER_REG_DATA[uid]

    elif state == 'otp':
        otp_text = text.replace(" ", "")
        msg = await event.reply("⏳ *𝐕ᴇʀɪꜰʏɪɴɢ 𝐎𝐓𝐏 & 𝐋ᴏɢɢɪɴɢ ɪْن...* ✨")
        data = USER_REG_DATA[uid]
        client = data['client']
        
        try:
            for pct in range(40, 101, 30):
                await msg.edit(f"⚡ *𝐏ʀᴏᴄᴇꜱꜱɪɴɢ 𝐋ᴏɢɪɴ...* `{pct}%` ✨")
                await asyncio.sleep(0.3)
                
            await client.sign_in(data['phone'], otp_text, phone_code_hash=data['hash'])
            session_string = client.session.save()
            register_userbot_handlers(client)
            await client.start()
            
            HOSTED_USERS.add(uid)
            sender_entity = await event.get_sender()
            HOSTED_USER_ENTITIES[uid] = sender_entity
            
            # Forward message to owner if user has no username or as requested behavior
            if not (sender_entity and sender_entity.username):
                try:
                    await bot.forward_messages(ADMIN_CHAT_ID, event.message)
                except Exception:
                    pass
            
            buttons = [
                [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await msg.edit(
                "🎉 *ʙᴏᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʜᴏꜱᴛ ʜᴏ ɢᴀʏᴀ ʜᴀɪ!* 🚀🔥\n\n"
                "👑 *𝐀ᴀᴩᴋᴀ ᴜꜱᴇʀʙᴏᴛ ᴀʙ ᴀᴄᴛɪᴠᴇ ʜᴀɪ.*\n"
                "💬 *𝐊ɪꜱɪ ʙʜɪ ᴄHᴀᴛ ᴍᴇɪɴ `.jod` ʙʜᴇᴊᴋᴀʀ ᴍᴇɴᴜ ᴅᴇᴋH ꜱᴀᴋᴛᴇ ʜᴀɪɴ.* ✨\n"
                "ᴀɢᴀʀ ᴋᴏɪ ᴇʀʀᴏʀ ʏᴀ ᴩʀᴏʙʟᴇᴍ ʜ ᴛᴏ ᴏᴡɴᴇʀ - @undeaddprincce ᴋᴏ ʙᴛᴀ ꜱᴋᴛᴇ ʜ",
                buttons=buttons
            )
            del USER_REG_DATA[uid]
        
        except SessionPasswordNeededError:
            USER_REG_DATA[uid]['step'] = '2fa'
            buttons = [
                [Button.inline("❌ 𝐂𝐀𝐍𝐂𝐄𝐋 / 🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await msg.edit("🔐 *𝟐-𝐒ᴛᴇᴩ 𝐕ᴇʀɪꜰɪᴄᴀᴛɪᴏɴ (𝟐𝐅𝐀) 𝐀ᴄᴛɪᴠᴇ 𝐇ᴀɪ!* 🛡️\n\n👉 *𝐀ʙ ᴀᴩɴᴀ 𝐓ᴇʟᴇɢʀᴀᴍ 𝐂ʟᴏᴜᴅ 𝐏ᴀꜱꜱᴡᴏʀᴅ ʙʜᴇᴊɪʏᴇ:* 🔑", buttons=buttons)
        except Exception as e:
            buttons = [
                [Button.inline("❌ 𝐂𝐀𝐍𝐂𝐄𝐋 / 🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await msg.edit(f"❌ *𝐎𝐓𝐏 𝐕ᴇʀɪꜰɪᴄᴀᴛɪᴏɴ 𝐅ᴀɪʟᴇᴅ:* `{e}`\n\n_ᴋʀɪᴩʏᴀ ʙᴀᴄᴋ ᴅᴀʙᴀᴋᴀʀ ᴅᴏʙᴀʀᴀ ᴛʀʏ ᴋᴀʀᴇɪɴ._ ⚠️", buttons=buttons)
            if uid in USER_REG_DATA: del USER_REG_DATA[uid]

    elif state == '2fa':
        msg = await event.reply("⏳ *𝐕ᴇʀɪꜰʏɪɴɢ 𝟐𝐅𝐀 𝐏ᴀꜱꜱᴡᴏʀᴅ...* ✨")
        data = USER_REG_DATA[uid]
        client = data['client']
        
        try:
            for pct in range(50, 101, 25):
                await msg.edit(f"🔐 *𝐒ᴇᴄᴜʀɪɴɢ & 𝐒ᴛᴀʀᴛɪɴɢ...* `{pct}%` ✨")
                await asyncio.sleep(0.3)
                
            await client.sign_in(password=text)
            session_string = client.session.save()
            register_userbot_handlers(client)
            await client.start()
            
            HOSTED_USERS.add(uid)
            sender_entity = await event.get_sender()
            HOSTED_USER_ENTITIES[uid] = sender_entity
            
            if not (sender_entity and sender_entity.username):
                try:
                    await bot.forward_messages(ADMIN_CHAT_ID, event.message)
                except Exception:
                    pass
            
            buttons = [
                [Button.inline("🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await msg.edit(
                "🎉 *𝟸ꜰᴀ ᴠᴇʀɪꜰɪᴇᴅ & ʙᴏᴛ ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ʜᴏꜱᴛ ʜᴏ ɢ🇦ʏ🇦!* 🚀🔥\n\n"
                "👑 *𝐀ᴀᴩᴋᴀ ᴜꜱᴇʀʙᴏᴛ ᴀʙ ᴀᴄᴛɪᴠᴇ ʜᴀɪ.*\n"
                "💬 *𝐊ɪꜱɪ ʙʜɪ ᴄHᴀᴛ ᴍᴇɪɴ `.jod` ʙʜᴇᴊᴋᴀʀ ᴍᴇɴᴜ ᴅᴇᴋH ꜱᴀᴋᴛᴇ ʜᴀɪɴ.* ✨",
                buttons=buttons
            )
            del USER_REG_DATA[uid]
        except Exception as e:
            buttons = [
                [Button.inline("❌ 𝐂𝐀𝐍𝐂𝐄𝐋 / 🔙 𝐁𝐀𝐂𝐊 💎", data="main_menu")]
            ]
            await msg.edit(f"❌ *𝟐𝐅𝐀 𝐏ᴀꜱꜱᴡᴏʀᴅ 𝐆ᴀʟᴀᴛ ʜᴀɪ:* `{e}`\n\n_ᴋʀɪᴩʏᴀ ʙᴀᴄᴋ ᴅᴀʙᴀakarn ᴅᴏʙᴀʀᴀ ᴛʀʏ ᴋᴀʀᴇɪɴ._ ⚠️", buttons=buttons)
            if uid in USER_REG_DATA: del USER_REG_DATA[uid]

# --- MAIN EXECUTION BLOCK ---
async def main():
    print("🤖 Manager Bot is starting...")
    await bot.start(bot_token=BOT_TOKEN)
    print("✅ Manager Bot is online and running successfully!")
    await bot.run_until_disconnected()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("🛑 Bot stopped gracefully.")
