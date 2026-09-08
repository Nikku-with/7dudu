#!/usr/bin/env python3
# Multi-bot GC / Slide / Swipe tool (updated TOKENS & OWNER)
# Install deps: pip install python-telegram-bot==20.0 edge-tts

import asyncio
import functools
import json
import os
import random
import time
import logging
from typing import Dict
import edge_tts
from telegram import Update, ChatPermissions
from telegram.error import RetryAfter, TimedOut, NetworkError
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ---------------------------
# CONFIG
# ---------------------------
TOKENS = [
"8999855202:AAH1okN9maoaMcH3yCTQ3BSrW0nuixb6xa4",
"8883957565:AAEfHNU7pmDFUqCqWCX6zfcP7F9mEwBHpPU",
"8455647760:AAG7n9_wG4kJ_ltWrslqmp1K90yU9S3XaMg",
"8976722801:AAG2Y_Qjbpb7c1pi5Hpt7e8sBq36HllSZuI",
"8933972948:AAEbGygsWVLyAzPbOxs2HOiH26kMkIxW7Wo",
]

OWNER_ID = 8955102809
SUDO_FILE = "8955102809"

# ---------------------------
# raidnc TEXTS & EMOJIS
# ---------------------------
raidnc_TEXTS = [
    " 🇰 🇦 🇱 🇮  🇨 🇭 🇺 🇹  🇼 🇦 🇱 🇦  ⳺⳻⳺⳻⳺⳻⳺⳻⳺⳻⳺⳻⳺⳻⳺⳺⳻",
    "Tᴇʀɪ Mᴀᴀ Cʜᴜᴅɪ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Sᴀʟᴀᴍ Tʜᴏᴋ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Cʜɪɴᴀᴀʀ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Mᴀᴢᴅᴏᴏʀ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Hᴀᴡᴀʙᴀᴢᴢ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "𝐑ᴜ𝐋ᴇ𝐑 अब्बू  ʙᴏʟ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Tᴍᴋʟ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "ᴋᴀᴍᴢᴏʀ Kᴜᴛɪʏᴀ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Bʜᴇᴇᴋ Mᴀɴɢ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "RɴᴅɪMᴏɴ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Cʜᴜᴅᴀɪ Kɪᴅᴅᴇ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Gʜᴀᴛɪʏᴀ Bᴇᴛᴀ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Tᴇʀᴀ Bᴀᴀᴘ 𝐑ᴜ𝐋ᴇ𝐑 ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "GAɴᴅ Mᴀʀᴀ ᴍᴜʟʟᴇ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Cʜᴜᴅᴇɢɪ TᴇʀɪMA ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "BɪᴛCʜ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "HɪᴊᴅᴜSᴏɴ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Nᴀʟɪ Sᴀғ Kᴀʀ ᴊAᴋᴇ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "GʜɪNᴏɴɪ Rɴᴅ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Cʜᴏᴛɪ Jᴀᴀᴛ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "TᴇRɪ Mᴀ Cʜɪɴᴀᴀʀ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Hɪᴊᴀʙ PᴇʜᴇN ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
    "Tᴍᴋᴄ Mᴀɪ Kᴏʏʟᴀ ⎯͢⎯⃝𓆩⚚𓆪⎯͢⎯⃝⚰️",
]

emonc_EMOJIS = [
   "🌫️ ♱",
"🌌 ♱",
"🌠 ♱",
"🎑 ♱",
"🫧 ♱",
"🪶 ♱",
"🧿 ♱",
"🪷 ♱",
"🍂 ♱",
"🍁 ♱",
"🌾 ♱",
"🌱 ♱",
"🌿 ♱",
"☘️ ♱",
"🍃 ♱",
"🪵 ♱",
"🏺 ♱",
"🕰️ ♱",
"⌛ ♱",
"⏳ ♱",
"📜 ♱",
"🪄 ♱",
"💎 ♱",
"🧊 ♱",
"🫙 ♱",
"🛸 ♱",
"🚬 ♱",
"🌡️ ♱",
"🎻 ♱",
"🎼 ♱",
"🎹 ♱",
"🥂 ♱",
"🍸 ♱",
"🍵 ♱",
"🧸 ♱",
"🛐 ♱",
"⚰️ ♱",
"🪦 ♱",
"🕸️ ♱",
"🦂 ♱",
"🐍 ♱",
"🦅 ♱",
"🐆 ♱",
"🦢 ♱",
"🐚 ♱",
"🌊 ♱",
"🏹 ♱",
"🪖 ♱",
"⚔️ ♱",
"🖤 ♱",
"🤍 ♱",
"💜 ♱",
"💙 ♱",
"🩶 ♱",
"🩵 ♱",
"🪩 ♱",
"🕯️ ♱",
"🪞 ♱",
"🦋 ♱",
"🕊️ ♱",
"🥀 ♱",
"🌹 ♱",
"🍷 ♱",
"🎭 ♱",
"🎧 ♱",
"📿 ♱",
"🔮 ♱",
"🪬 ♱",
"⚜️ ♱",
"♠️ ♱",
"♣️ ♱",
"♦️ ♱",
"🃏 ♱",
"🎐 ♱",
"🫀 ♱",
"🗝️ ♱",
"⛓️ ♱",
"🦇 ♱",
"☠️ ♱",
]

# Each pattern is a 6-line message block
EMOSPAM_PATTERNS = [
    (
        "✫: ̗̀➛「{target}」────────ꜱᴀᴍᴏꜱᴇ ᴡᴀʟᴇᴇ ᴋᴇᴇ ʟᴀᴅᴅᴋᴇ 「🦢」\n"
        "✫: ̗̀➛「{target}」────────ᴘᴀɴɪᴘᴜʀɪ ᴡᴀʟᴇ ᴋᴀ ʟᴀᴅᴋᴀ「⚜️」\n"
        "✫: ̗̀➛「{target}」────────ʀᴀɴᴅɪ ᴋᴀ ʟᴀᴅᴋᴀ 「🦢」\n"
        "✫: ̗̀➛「{target}」────────ᴄʜɪɴᴇꜱꜱ ᴡᴀʟᴇ ᴋᴀ ʟᴀᴅᴋᴀ  「⚜️」\n"
        "✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🦢」\n"
        "✫: ̗̀➛「{target}」────────ꜱᴀᴍᴏꜱᴇ ᴡᴀʟᴇ ᴋᴀ ʟᴀᴅᴋᴀᴀ  「⚜️」"
    )

]

SPAM_PATTERNS = ["[ text ] 🪐", "[ text ] 🫶", "[ text ] 🤡", "[ text ] ⚜️"]

gawdnc_TEXTS = [
    "⚜️ { target } • 𝐑ᴀɴᴅ ⚜️",
    "🖤{ target } • 𝐑ᴀɴᴅ 🖤",
    "🤎{ target } • 𝐑ᴀɴᴅ 🤎",
    "💜{ target } • 𝐑ᴀɴᴅ 💜",
    "💙{ target } • 𝐑ᴀɴᴅ 💙",
    "🩵{ target } • 𝐑ᴀɴᴅ 🩵",
    "💚{ target } • 𝐑ᴀɴᴅ 💚",
    "💛{ target } • 𝐑ᴀɴᴅ 💛",
    "🧡{ target } • 𝐑ᴀɴᴅ 🧡",
    "❤️{ target } • 𝐑ᴀɴᴅ ❤️",
]

rulerncloop_TEXTS = [
" 🎐 {target} 🧿52×~🫗 ", " 🧨 {target} ⚱️17××🪞 ", " 🎭 {target} 🧬84×~📿 ", " 🧷 {target} 🪤33××🧃 ", " 💸 {target} 🧠91×~⚗️", " 🫓 {target} 🪆26××🧊 ", " 🚿 {target} 🛝75×~🪬 ", " 🕯️ {target} 📎48××🧯 ", " 🫑 {target} 🪶13××🧴 ", " 🪒 {target} 🛼57×~🪢 ", " 🧽 {target} 🧭88××⚖️ ", " 🪰 {target} 🧪31×~🧿 ", " 🪥 {target} 🪫96××🪅 ", " 🪲 {target} 📡44×~🫙 ", " 🫐 {target} ⚰️18××🧺 ", " 🪳 {target} 🧊63×~🪖 ", " 🫒 {target} 🪞80××🪠 ", " 🪱 {target} 🫗24×~🪭 ", " 🫖 {target} 🛁71××🧸 ", " 🪠 {target} 🧹50×~🃏 ", " 🫔 {target} 🚿12××🎐 ", " 🧸 {target} 🧼87×~🎎 ", " 🫓 {target} 🪑36××🧧 ", " 🧷 {target} 🪒95×~🎴 ", " 🫑 {target} 🧻42××♟️ ", " 🔦 {target} 🧽66×~🪆 ", " 💍 {target} 🛒21××🪻 ", " 🪲 {target} 🪥77×~🫐 ", " 🧬 {target} 🧯14××🫒 ", " 🪰 {target} 🧴89×~🪱 ", " 🖇️ {target} 🧠28××🪲 ", " 🪳 {target} ⚗️61×~🫖 ", " 🫔 {target} 📿19××🪺 ", " 🔧 {target} 🧬83×~🫑 ", " 🫓 {target} 🪤37××🪷 ", " 📣 {target} 🛎️74×~🫛 ", " 🫒 {target} 🪆46××🪰 ", " 🪱 {target} 🧭90×~🫜 ", " 🫖 {target} 🛼25××🪳 ", " 📯 {target} 🫧58×~🫚 ", " 🫐 {target} 🪶11××🪲 ", " 🛎️ {target} 📡97×~🫔 ", " 🫑 {target} 🪫39××🪹 ", " 📿 {target} ⚰️62×~🫓 ", " ⚰️ {target} 🧊15××🪼 ", " 🪰 {target} 🪞81×~🫒 ", " 🔐 {target} 🫗34××🪱 ", " 🪳 {target} 🛁73×~🫖 ", " 🔮 {target} 🧹49××🪺 " , " 🪬 {target} ⚗️17×~🫧 ", " 🧿 {target} 🪤44××📼 ", " 🗝️ {target} 🧫91×~🪶 ", " 🛎️ {target} ⚱️28××🧷 ", " ⚔️ {target} 🧪63×~🪢 ", " 📿 {target} 🛼12××🫀 ", " 🧬 {target} 🪜77×~📡 ", " 🪞 {target} 🧯35××🕯️ ", " 🧲 {target} 🫙88×~🧃 ", " 🪅 {target} 🪸49××🫗 ", " 🧊 {target} 🧠26×~📻 ", " 🪥 {target} ⚖️95××🪐 ", " 🧵 {target} 🛗14×~🪦 ", " 🗡️ {target} 🧿53××📎 ", " 🪣 {target} 🪩71×~🧼 ", " 🔐 {target} 🪬38××🧴 ", " ⚜️ {target} 📿82×~🪞 ", " ⚰️ {target} 🛎️19××🪅 ", " 🪤 {target} 🧬64×~⚱️ ", " 〽️ {target} 🚸47××🛼 ", " 🧫 {target} 🧲90×~🧯 ", " 🧪 {target} 🪥21××🪸 ", " 🛗 {target} 🧊56×~🫀 ", " 🪶 {target} 🪣73××📻 ", " ⚗️ {target} 🛐30×~🧿 ", " 🧠 {target} 🪫84××🧵 ", " 🫙 {target} ⚰️41×~🕶️ ", " 🪜 {target} 🪤67××📿 ", " 🛼 {target} 🫧25×~🧬 ", " 📡 {target} 🧫98××🪞 ", " 🧃 {target} 🧪46×~🪅 ", " 🪢 {target} 🛗11××🧊 ", " 🧴 {target} 🪶59×~🛎️ ", " ⚖️ {target} 🧠72××🪣 ", " 🧼 {target} 🧽18×~👞 ", " 🪸 {target} 🪜87××⚗️ ", " 🧯 {target} 📡32×~🛝 ", " 🪦 {target} 🧃60××🪭 ", " 📎 {target} 🪢15×~🧿 ", " 🕯️ {target} 🧴93××🧬 ", " 🪖 {target} 🧭51×~🪤 ", " 🧳 {target} 🕯️24××⚰️ ", " 🪑 {target} 🧪79×~🧸 ", " 🧺 {target} 🪩36××🧊 ", " 🛁 {target} 📿65×~🪞 ", " 🚿 {target} 🪶10××🧠 ", " 🪠 {target} 🧯97×~🛼 ", " 🚽 {target} ⚗️43××🪢 ", " 🧻 {target} 🚿70×~🪐", " 🪒 {target} 🪸16××🧬 ", " 🧹 {target} 🪫58×~🧿 ", " 🪣 {target} 🛎️27××🧴 ", " 🧼 {target} 🪤89×~🪖 ", " 🪥 {target} ⚱️34××🧺 ", " 🧽 {target} 🧭76×~🚿 ", " 🧯 {target} 🛝22××🪑 ", " 🛒 {target} 📎61×~🪠 ", " 🧸 {target} 🫗13××🧻 ", " 🪆 {target} 🧊94×~🧹 ", " 🎐 {target} 🪞48××🪒 ", " 🪅 {target} 🧠80×~🛁 ", " 🎎 {target} ⚖️29××🧼 ", " 🪭 {target} 🪢57×~🪆 ", " 🧧 {target} 🧬96××🎐 ", " 🎴 {target} 🫧40×~🪅 ", " 🃏 {target} 🛼68××🎎 ", " 🎲 {target} 📡20×~🧧 ", " ♟️ {target} 🪫85××🎴 ",
]

gulam_TEXTS = [
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙   Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target}  #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ × 🫶",
    "🌒 • {target} #𝑴𝒂𝒅𝑴𝒂𝒙 Kᴇ Gᴜʟᴀᴍ ×🫶",
]

shutupnc_TEXTS = [
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🌹",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🥀",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🌺",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🌷",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🪷",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🌸",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️💮",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🏵️",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🪻",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🌻",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🌼",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🍂",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🍁",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️💐",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🌹",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🪷",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️💮",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🌷",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🪻",
    "𓆩⚝𓆪 {target} 𓆩⚝𓆪 Shut up रंडीके 🖇️🌺",
]

emospam_tasks: Dict[int, asyncio.Task] = {}
gawdnc_tasks: Dict[int, Dict[str, asyncio.Task]] = {}
shutupnc_tasks: Dict[int, Dict[str, asyncio.Task]] = {}
rulerncloop_tasks: Dict[int, Dict[str, asyncio.Task]] = {}
gulam_tasks: Dict[int, Dict[str, asyncio.Task]] = {}

# ---------------------------
# AUTO-SPEED CONFIG
# ---------------------------
NORMAL_DELAY   = 0   # fast base speed
BOOST_DELAY    = 0   # turbo speed on interference
BOOST_DURATION = 400     # keep turbo for longer
CHECK_INTERVAL = 4      # check title every 4 iters

_boost_state: Dict[int, int] = {}
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
# FONT STYLIZER
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
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return

        uid = update.effective_user.id

        if uid not in SUDO_USERS:
            return await update.message.reply_text(
                "𝐏ᴀʜʟᴇ 𝐒ᴜᴅᴏ 𝐋ᴇ 𝐅ɪʀ 𝐂ᴏᴍᴍᴀɴᴅ 𝐔sᴇ 𝐊ᴀʀ #𝑴𝒂𝒅𝑴𝒂𝒙 𝐊ᴇ 𝐆ᴜʟᴀᴍ ⚜️"
            )

        return await func(update, context)

    return wrapper


def only_owner(func):
    @functools.wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return

        uid = update.effective_user.id

        if uid != OWNER_ID:
            return await update.message.reply_text(
                "𝐒ɪʀғ #𝑴𝒂𝒅𝑴𝒂𝒙 𝐏ᴀᴘᴀ 𝐇ᴇ 𝐔sᴇ 𝐊ᴀʀ 𝐒ᴀᴋᴛᴀ 𝐇ᴀɪ 𝐘ᴇ 𝐂ᴏᴍᴍᴀɴᴅ ⚜️"
            )

        return await func(update, context)

    return wrapper

# ---------------------------
# SAFE TITLE SETTER
# ---------------------------
async def safe_set_title(bot, chat_id: int, text: str) -> bool:
    try:
        await asyncio.wait_for(bot.set_chat_title(chat_id, text), timeout=6)
        return True
    except RetryAfter as e:
        # Cap at 15s max — don't over-sleep
        wait = min(e.retry_after, 15) + random.uniform(0.1, 0.5)
        await asyncio.sleep(wait)
        return False
    except (TimedOut, NetworkError):
        await asyncio.sleep(0.1)
        return False
    except asyncio.CancelledError:
        raise
    except Exception as e:
        err = str(e).lower()
        if "flood" in err or "too many" in err:
            await asyncio.sleep(0)
        elif "rights" in err or "not enough" in err or "forbidden" in err:
            await asyncio.sleep(0)
        else:
            await asyncio.sleep(0)
        return False


# ---------------------------
# AUTO-SPEED
# ---------------------------
def _current_delay(chat_id: int) -> float:
    if _boost_state.get(chat_id, 0) > 0:
        return BOOST_DELAY
    return delay


def _trigger_boost(chat_id: int):
    _boost_state[chat_id] = BOOST_DURATION
    print(f"[BOOST] Interference detected in {chat_id} — switching to turbo speed!")


def _tick_boost(chat_id: int):
    if _boost_state.get(chat_id, 0) > 0:
        _boost_state[chat_id] -= 1
        if _boost_state[chat_id] == 0:
            print(f"[BOOST] chat {chat_id} — returning to normal speed.")


# ---------------------------
# BOT LOOP
# ---------------------------
async def bot_loop(bot, chat_id: int, base: str, mode: str):
    i = 0
    check_counter = 0
    while True:
        try:
            if mode == "raidnc":
                text = f"{base} {raidnc_TEXTS[i % len(raidnc_TEXTS)]}"
            else:
                text = f"{base} {emonc_EMOJIS[i % len(emonc_EMOJIS)]}"

            check_counter += 1
            if check_counter >= CHECK_INTERVAL:
                check_counter = 0
                try:
                    chat_info = await asyncio.wait_for(
                        bot.get_chat(chat_id), timeout=6
                    )
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
            print(f"[WARN] Bot loop error in chat {chat_id}: {e}")
            await asyncio.sleep(0.1)


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
            await asyncio.sleep(0.1)


# ---------------------------
# COMMANDS
# ---------------------------
@only_owner
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔮🫶🏻 • < Sᴄʀɪᴘᴛ Bʏ  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ > Is Aᴄᴛɪᴠᴇ Nᴏᴡ •~ \nUsᴇ /menu Tᴏ Sᴇᴇ Aʟʟ Cᴏᴍᴍᴀɴᴅs > • 🌒🦢."
    )


@only_owner
async def menu_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    menu = (
"╔══════════════════════════════╗\n"
"║          👑 #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 👑          ║\n"
"╚══════════════════════════════╝\n"
"\n"
"⚡ ✦ ʙᴏʀɴ ᴛᴏ ʀᴜʟᴇ ✦ ⚡\n"
"👑 ✦ ᴛʜᴇ ᴏɴᴇ ᴀʙᴏᴠᴇ ᴀʟʟ ✦ 👑\n"
"\n"
"╭━━━ 👑 ᴄᴏʀᴇ ━━━╮\n"
"│ ◈ /start\n"
"│ ◈ /menu\n"
"│ ◈ /ping\n"
"│ ◈ /status\n"
"│ ◈ /myid\n"
"╰──────────────╯\n"
"\n"
"┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
"┃ 😎 ɴᴀᴀᴍ ʏᴀᴀᴅ ʀᴀᴋʜɴᴀ 😎 ┃\n"
"┃      #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ       ┃\n"
"┗━━━━━━━━━━━━━━━━━━━━━━┛\n"
"\n"
"╭━━━ ⚡ sᴜᴅᴏ ━━━╮\n"
"│ ◈ /bheeklerandike\n"
"│ ◈ /bhagmdc\n"
"│ ◈ /bhikari\n"
"╰──────────────╯\n"
"\n"
"✦━━━━━━━━━━━━━━━━━━━━✦\n"
"👑 ʜᴜᴋᴜᴍ ɴᴀʜɪ...\n"
"👑 ᴘᴇʜᴄʜᴀᴀɴ ᴄʜᴀʟᴛɪ ʜᴀɪ\n"
"✦━━━━━━━━━━━━━━━━━━━━✦\n"
"\n"
"╭━━━ ☠️ ᴅᴏᴍɪɴᴀᴛɪᴏɴ ━━━╮\n"
"│ ◈ /emonc <name>\n"
"│ ◈ /raidnc <name>\n"
"│ ◈ /gawdnc <name>\n"
"│ ◈ /shutupnc <name>\n"
"│ ◈ /#𝑴𝒂𝒅𝑴𝒂𝒙ɢᴀᴡᴅ <name>\n"
"│ ◈ /gulam <name>\n"
"│ ◈ /moonnc <name>\n"
"│ ◈ /baapnc <name>\n"
"╰────────────────────╯\n"
"\n"
"╔══════════════════════╗\n"
"║ 👑 ɴᴀᴀᴍ ʜɪ ᴋᴀғɪ ʜᴀɪ 👑 ║\n"
"║      #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ       ║\n"
"╚══════════════════════╝\n"
"\n"
"╭━━━ 🌪️ sᴘᴀᴍ ━━━╮\n"
"│ ◈ /spamloop\n"
"│ ◈ /slidespam\n"
"│ ◈ /swipe\n"
"│ ◈ /emospam\n"
"│ ◈ /targetslide\n"
"│ ◈ /delay <sec>\n"
"╰──────────────╯\n"
"\n"
"⚔️━━━━━━━━━━━━━━━━━━━━⚔️\n"
"   ᴇɴᴛʀʏ ᴄʜᴏᴛɪ sᴀʜɪ,\n"
"   ɴᴀᴀᴍ ʙᴀᴅᴀ ʜᴏɴᴀ ᴄʜᴀʜɪʏᴇ\n"
"⚔️━━━━━━━━━━━━━━━━━━━━⚔️\n"
"\n"
"╭━━━ ⛓️ ᴄᴏɴᴛʀᴏʟ ━━━╮\n"
"│ ◈ /stopraidnc\n"
"│ ◈ /stopgawdnc\n"
"│ ◈ /stopshutupnc\n"
"│ ◈ /stoprulerncloop\n"
"│ ◈ /stopgulam\n"
"│ ◈ /stopmoonnc\n"
"│ ◈ /stopbaapnc\n"
"│ ◈ /stopspam\n"
"│ ◈ /stopslidespam\n"
"│ ◈ /stopswipe\n"
"│ ◈ /stopemospam\n"
"│ ◈ /stopslide\n"
"│ ◈ /stopall\n"
"╰────────────────────╯\n"
"\n"
"╔══════════════════════╗\n"
"║ 👑 #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 👑 ║\n"
"║ 🔥 ᴘᴇʜᴄʜᴀᴀɴ ʜɪ ᴘᴇʜᴄʜᴀᴀɴ ʜᴀɪ 🔥 ║\n"
"╚══════════════════════╝\n"
"\n"
"╭━━━ ⚔️ ᴍᴏᴅ ━━━╮\n"
"│ ◈ /adminall\n"
"│ ◈ /mute\n"
"│ ◈ /unmute\n"
"│ ◈ /safe\n"
"│ ◈ /unsafe\n"
"│ ◈ /gclock\n"
"│ ◈ /gcunlock\n"
"│ ◈ /left\n"
"╰──────────────╯\n"
"\n"
"╭━━━ 👑 #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ ━━━╮\n"
"│ ◈ /setphoto\n"
"│ ◈ /stopphoto\n"
"│ ◈ /tts <text>\n"
"│ ◈ /chud\n"
"│ ◈ /chudaistop\n"
"│ ◈ /react <emoji>\n"
"│ ◈ /stopreact\n"
"╰──────────────╯\n"
"\n"
"┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
"┃ 👑 ᴋɪɴɢs ᴅᴏɴ'ᴛ ғᴏʟʟᴏᴡ 👑 ┃\n"
"┃      ʀᴜʟᴇs...       ┃\n"
"┃    ᴛʜᴇʏ ᴍᴀᴋᴇ ᴛʜᴇᴍ   ┃\n"
"┗━━━━━━━━━━━━━━━━━━━━━━┛\n"
"\n"
"╔══════════════════════════════╗\n"
"║          👑 #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 👑          ║\n"
"╚══════════════════════════════╝\n"
"\n"
"⚡ ✦ ʟᴇɢᴇɴᴅs ɴᴇᴠᴇʀ ᴅɪᴇ ✦ ⚡\n"
"👑 ✦ ᴛʜᴇ ᴏɴᴇ ᴀʙᴏᴠᴇ ᴀʟʟ ✦ 👑\n"
"🔥 ✦ ɴᴀᴀᴍ ʜɪ ᴋᴀғɪ ʜᴀɪ ✦ 🔥\n"
    )
    try:
        with open("attached_assets/127974803081e0da9a6cd0ab55795087_1775547819582.jpg", "rb") as photo:
            await update.message.reply_photo(photo=photo, caption=menu)
    except Exception:
        await update.message.reply_text(menu)


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
async def raidnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /raidnc <text>")
    base = stylize_name(" ".join(context.args))
    chat_id = update.message.chat_id
    group_tasks.setdefault(chat_id, {})
    for bot in bots:
        key = getattr(bot, "token", str(id(bot)))
        if key not in group_tasks[chat_id]:
            task = asyncio.create_task(bot_loop(bot, chat_id, base, "raidnc"))
            group_tasks[chat_id][key] = task
    await update.message.reply_text("🔄चुदाई suru hua.")


@only_owner
async def emonc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /emonc <text>")
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

    for chat_id in list(gawdnc_tasks.keys()):
        for task in gawdnc_tasks[chat_id].values():
            task.cancel()
    gawdnc_tasks.clear()

    for chat_id in list(shutupnc_tasks.keys()):
        for task in shutupnc_tasks[chat_id].values():
            task.cancel()
    shutupnc_tasks.clear()

    for chat_id in list(rulerncloop_tasks.keys()):
        for task in rulerncloop_tasks[chat_id].values():
            task.cancel()
    rulerncloop_tasks.clear()

    for chat_id in list(gulam_tasks.keys()):
        for task in gulam_tasks[chat_id].values():
            task.cancel()
    gulam_tasks.clear()

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
async def bheeklerandike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        uid = update.message.reply_to_message.from_user.id
        SUDO_USERS.add(uid)
        save_sudo()
        await update.message.reply_text(f"✅ {uid} added as sudo.")
    else:
        await update.message.reply_text("⚠️ Reply to a user to add them as sudo.")


@only_owner
async def bhagmdc(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
async def bhikari(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        await update.message.reply_text("🛑 chudiye stop stopped.")
    else:
        await update.message.reply_text("⚠️ No spam loop active in this chat.")


async def gawdnc_loop(bot, chat_id: int, target: str):
    i = 0
    check_counter = 0
    while True:
        try:
            pattern = gawdnc_TEXTS[i % len(gawdnc_TEXTS)]
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
            print(f"[WARN] gawdnc loop error in chat {chat_id}: {e}")
            await asyncio.sleep(0.1)


async def emospam_loop(bot, chat_id, text):
    # Small stagger so multiple bots don't all hit at same time
    await asyncio.sleep(random.uniform(0, 0.3))
    while True:
        try:
            pattern = random.choice(EMOSPAM_PATTERNS)
            spam_text = pattern.replace("{target}", text)
            await bot.send_message(chat_id=chat_id, text=spam_text)
            await asyncio.sleep(delay)
        except asyncio.CancelledError:
            raise
        except RetryAfter as e:
            wait = max(e.retry_after, 1) + random.uniform(0.1, 0.5)
            await asyncio.sleep(wait)
        except (TimedOut, NetworkError):
            await asyncio.sleep(0.1)
        except Exception as e:
            print(f"[WARN] Emospam error in chat {chat_id}: {e}")
            await asyncio.sleep(0.1)


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
async def gawdnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /gawdnc <target name>")
    target = stylize_name(" ".join(context.args))
    chat_id = update.message.chat_id
    gawdnc_tasks.setdefault(chat_id, {})
    for bot in bots:
        key = getattr(bot, "token", str(id(bot)))
        if key not in gawdnc_tasks[chat_id]:
            task = asyncio.create_task(gawdnc_loop(bot, chat_id, target))
            gawdnc_tasks[chat_id][key] = task
    await update.message.reply_text(f"🎯 gawdnc loop started for: {target}")


@only_owner
async def stopgawdnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in gawdnc_tasks:
        for task in gawdnc_tasks[chat_id].values():
            task.cancel()
        del gawdnc_tasks[chat_id]
        _boost_state.pop(chat_id, None)
        _last_set_title.pop(chat_id, None)
        await update.message.reply_text("⏹ gawdnc loop stopped.")
    else:
        await update.message.reply_text("⚠️ No gawdnc loop active in this chat.")


async def shutupnc_loop(bot, chat_id: int, target: str):
    i = 0
    check_counter = 0
    while True:
        try:
            pattern = shutupnc_TEXTS[i % len(shutupnc_TEXTS)]
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
            print(f"[WARN] shutupnc loop error in chat {chat_id}: {e}")
            await asyncio.sleep(0.1)


@only_owner
async def shutupnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /shutupnc <target name>")
    target = stylize_name(" ".join(context.args))
    chat_id = update.message.chat_id
    shutupnc_tasks.setdefault(chat_id, {})
    for bot in bots:
        key = getattr(bot, "token", str(id(bot)))
        if key not in shutupnc_tasks[chat_id]:
            task = asyncio.create_task(shutupnc_loop(bot, chat_id, target))
            shutupnc_tasks[chat_id][key] = task
    await update.message.reply_text(f"🎋 shutupnc loop started for: {target}")


@only_owner
async def stopshutupnc_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in shutupnc_tasks:
        for task in shutupnc_tasks[chat_id].values():
            task.cancel()
        del shutupnc_tasks[chat_id]
        _boost_state.pop(chat_id, None)
        _last_set_title.pop(chat_id, None)
        await update.message.reply_text("⏹ shutupnc loop stopped.")
    else:
        await update.message.reply_text("⚠️ No shutupnc loop active in this chat.")


# ---------------------------
# rulerncloop LOOP
# ---------------------------
async def rulerncloop_loop(bot, chat_id: int, target: str, bot_index: int):
    await asyncio.sleep(bot_index * 0.1)
    i = bot_index
    check_counter = 0
    while True:
        try:
            pattern = rulerncloop_TEXTS[i % len(rulerncloop_TEXTS)]
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
            print(f"[WARN] rulerncloop loop error in chat {chat_id}: {e}")
            await asyncio.sleep(0.1)


@only_owner
async def rulerncloop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    target = stylize_name(" ".join(context.args)) if context.args else "Target"
    if chat_id in rulerncloop_tasks:
        for task in rulerncloop_tasks[chat_id].values():
            task.cancel()
    loop = asyncio.get_running_loop()
    tasks = {}
    for i, bot in enumerate(bots):
        task = loop.create_task(rulerncloop_loop(bot, chat_id, target, i))
        tasks[f"bot_{i}"] = task
    rulerncloop_tasks[chat_id] = tasks
    await update.message.reply_text(f"▶️ rulerncloop loop started for: {target}")


@only_owner
async def stoprulerncloop_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in rulerncloop_tasks:
        for task in rulerncloop_tasks[chat_id].values():
            task.cancel()
        del rulerncloop_tasks[chat_id]
        _boost_state.pop(chat_id, None)
        _last_set_title.pop(chat_id, None)
        await update.message.reply_text("⏹ rulerncloop loop stopped.")
    else:
        await update.message.reply_text("⚠️ No rulerncloop loop active in this chat.")


# ---------------------------
# gulam LOOP
# ---------------------------
async def gulam_loop(bot, chat_id: int, target: str, bot_index: int):
    await asyncio.sleep(bot_index * 0.1)
    i = bot_index
    check_counter = 0
    while True:
        try:
            pattern = gulam_TEXTS[i % len(gulam_TEXTS)]
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
            print(f"[WARN] gulam loop error in chat {chat_id}: {e}")
            await asyncio.sleep(0.1)


@only_owner
async def gulam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if not context.args:
        return await update.message.reply_text("⚠️ Usage: /gulam <target name>")
    target = stylize_name(" ".join(context.args))
    if chat_id in gulam_tasks:
        for task in gulam_tasks[chat_id].values():
            task.cancel()
    loop = asyncio.get_running_loop()
    tasks = {}
    for i, bot in enumerate(bots):
        task = loop.create_task(gulam_loop(bot, chat_id, target, i))
        tasks[f"bot_{i}"] = task
    gulam_tasks[chat_id] = tasks
    await update.message.reply_text(f"🫶 gulam loop started for: {target}")


@only_owner
async def stopgulam_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in gulam_tasks:
        for task in gulam_tasks[chat_id].values():
            task.cancel()
        del gulam_tasks[chat_id]
        _boost_state.pop(chat_id, None)
        _last_set_title.pop(chat_id, None)
        await update.message.reply_text("⏹ gulam loop stopped.")
    else:
        await update.message.reply_text("⚠️ No gulam loop active in this chat.")
        

    # ===========================
# ADMIN ALL FEATURE
# ===========================

@only_owner
async def adminall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    success = 0
    failed = 0

    for bot in bots:
        try:
            me = await bot.get_me()

            await bot.promote_chat_member(
                chat_id=chat_id,
                user_id=me.id,
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_topics=True
            )

            success += 1

        except Exception as e:
            print(f"Admin error: {e}")
            failed += 1

    await update.message.reply_text(
        f"""
"╔═══━━━── • ──━━━═══╗\n"
"      👑  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 👑\n"
"╚═══━━━── • ──━━━═══╝\n"
"\n"
"🔥 ᴀᴅᴍɪɴ ᴘᴏᴡᴇʀ ᴅʀᴏᴘᴘᴇᴅ 🔥\n"
"\n"
"✦ sᴜᴄᴄᴇss ➜ {success}\n"
"✦ ғᴀɪʟᴇᴅ ➜ {failed}\n"
"\n"
"⚔️ ᴇᴠᴇʀʏ ʙᴏᴛ ɴᴏᴡ ᴀɴsᴡᴇʀs\n"
"ᴛᴏ ᴛʜᴇ ɴᴀᴍᴇ ᴏғ #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 👑\n"
"\n"
"👑 ᴛʜᴇ ᴛʜʀᴏɴᴇ ᴏғ ᴛʜɪs ɢᴄ\n"
"ɴᴏᴡ ʙᴇʟᴏɴɢs ᴛᴏ #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ ⚜️\n"
"\n"
"🔥 ɴᴀᴀᴍ ʜɪ ᴋᴀғɪ ʜᴀɪ 🔥\n"
"👑 #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ ɴᴇᴠᴇʀ ᴍɪssᴇs 👑\n"
"""
    )
    
    # ===========================
# MUTE FEATURE
# ===========================

muted_users = {}

@only_owner
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "⚠️ 𝐑ᴇᴘʟʏ ᴋᴀʀ ᴋɪsɪ ᴜsᴇʀ ᴘᴇ /mute ᴜsᴇ ᴋʀ ⚜️"
        )

    chat_id = update.effective_chat.id
    user = update.message.reply_to_message.from_user

    muted_users.setdefault(chat_id, set()).add(user.id)

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user.id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
            )
        )
    except Exception as e:
        print(f"[MUTE ERROR] {e}")

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
      ⚜️ 𝐌ᴜᴛᴇᴅ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 👤 𝐔sᴇʀ » {user.first_name}
│ 🔇 𝐒ᴛᴀᴛᴜs » 𝐌ᴜᴛᴇᴅ
│ ⚔️ 𝐌ᴏᴅᴇ » 𝐈ɴsᴛᴀɴᴛ 𝐃ᴇʟᴇᴛᴇ
╰─────────────❖

🪬 𝐍ᴏᴡ 𝐄ᴠᴇʀʏ 𝐌ᴇssᴀɢᴇ 𝐖ɪʟʟ 𝐕 ♱
⚜️ MADMAX gawd 𝐇ᴏʟᴅs 𝐓ʜᴇ 𝐏ᴏᴡᴇʀ ⚔️
"""
    )


@only_owner
async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "⚠️ 𝐑ᴇᴘʟʏ ᴋᴀʀ ᴋɪsɪ ᴜsᴇʀ ᴘᴇ /unmute ᴜsᴇ ᴋʀ ⚜️"
        )

    chat_id = update.effective_chat.id
    user = update.message.reply_to_message.from_user

    if chat_id in muted_users:
        muted_users[chat_id].discard(user.id)

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user.id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
            )
        )
    except Exception as e:
        print(f"[UNMUTE ERROR] {e}")

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
     ⚜️ 𝐔ɴᴍᴜᴛᴇᴅ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 👤 𝐔sᴇʀ » {user.first_name}
│ 🔊 𝐒ᴛᴀᴛᴜs » 𝐔ɴᴍᴜᴛᴇᴅ
│ 🌒 𝐌ᴏᴅᴇ » 𝐅ʀᴇᴇᴅ
╰─────────────❖

🪬 𝐓ʜᴇ 𝐒ɪʟᴇɴᴄᴇ 𝐇ᴀs 𝐄ɴᴅᴇᴅ ♱
⚜️ #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝐒ᴘᴀʀᴇᴅ 𝐓ʜᴇᴍ ⚔️
"""
    )


async def mute_watcher(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id in muted_users and user_id in muted_users[chat_id]:
        try:
            await update.message.delete()
        except:
            pass
    
    # ===========================
# SUDO ACCESS FIX
# ===========================

def sudo_access(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.effective_user:
            return

        uid = update.effective_user.id

        # OWNER + SUDO dono allowed
        if uid != OWNER_ID and uid not in SUDO_USERS:
            return await update.message.reply_text(
                "⚜️ Pᴇʜʟᴇ  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ Kᴀ Sᴜᴅᴏ Bᴀɴ Rᴀɴᴅɪ Kᴇ Fɪʀ Cᴍᴅ Usᴇ Kʀ ⚜️"
            )

        return await func(update, context)

    return wrapper
    
    # ===========================
# FAST LEFT FEATURE
# ===========================

@only_owner
async def left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id

    left_count = 0
    failed_count = 0

    async def leave_bot(bot):
        nonlocal left_count, failed_count

        try:
            await bot.leave_chat(chat_id)
            left_count += 1
        except Exception as e:
            print(f"[LEFT ERROR] {e}")
            failed_count += 1

    # FAST PARALLEL LEAVE
    await asyncio.gather(*[leave_bot(bot) for bot in bots])

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
    💬 ɢᴀᴍᴇ ᴏᴠᴇʀ ʙʏ #𝑴𝒂𝒅𝑴𝒂𝒙⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 🤖 𝐁ᴏᴛs 𝐋ᴇғᴛ » {left_count}
│ ❌ 𝐅ᴀɪʟᴇᴅ » {failed_count}
│ 🌒 𝐒ᴛᴀᴛᴜs » 𝐄sᴄᴀᴘᴇ 𝐂ᴏᴍᴘʟᴇᴛᴇ
╰─────────────❖

🪬 𝐀ʟʟ 𝐁ᴏᴛs 𝐕ᴀɴɪsʜᴇᴅ 𝐈ɴᴛᴏ 𝐃ᴀʀᴋɴᴇss ♱
⚔️ #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝐍ᴇᴠᴇʀ 𝐋ᴏsᴇs ⚜️
"""
    )
    
    
  # ===========================
# GC LOCK + SAFE/UNSAFE
# ===========================

gc_locked = False
SAFE_USERS = {OWNER_ID}


@only_owner
async def safe(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "⚠️ 𝐑ᴇᴘʟʏ ᴋᴀʀ ᴋɪsɪ ᴜsᴇʀ ᴘᴇ /safe ᴜsᴇ ᴋʀ ⚜️"
        )

    user = update.message.reply_to_message.from_user
    SAFE_USERS.add(user.id)

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
      ⚜️ 𝐒ᴀғᴇᴅ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 👤 𝐔sᴇʀ » {user.first_name}
│ 🪬 𝐒ᴛᴀᴛᴜs » 𝐒ᴀғᴇ 𝐔sᴇʀ
│ 👑 𝐀ᴄᴄᴇss » 𝐀ʟʟᴏᴡᴇᴅ
╰─────────────❖

⚜️ 𝐓ʜɪs 𝐒ᴏᴜʟ 𝐍ᴏᴡ 𝐒ᴘᴇᴀᴋs 𝐅ʀᴇᴇʟʏ ♱
"""
    )
    
    # ===========================
# FAST TTS FEATURE
# ===========================

@only_owner
async def tts(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if len(context.args) == 0:
        return await update.message.reply_text(
            "⚠️ 𝐔sᴇ » /tts <text> ⚜️"
        )

    text = " ".join(context.args)

    file_name = f"tts_{update.effective_user.id}.mp3"

    try:

        communicate = edge_tts.Communicate(
            text=text,
            voice="en-US-GuyNeural"
        )

        await communicate.save(file_name)

        await update.message.reply_voice(
            voice=open(file_name, "rb"),
            caption=f"""
╔═══━━━── • ──━━━═══╗
        ⚜️ 𝐓𝐓𝐒 ⚜️
╚═══━━━── • ──━━━═══╝

🪬 𝐕ᴏɪᴄᴇ 𝐒ᴜᴍᴍᴏɴᴇᴅ 𝐅ʀᴏᴍ 𝐓ʜᴇ #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ ♱
⚔️ 𝐓ᴇxᴛ » {text[:40]}
"""
        )

        os.remove(file_name)

    except Exception as e:
        print(f"[FAST TTS ERROR] {e}")

        await update.message.reply_text(
            "⚠️ 𝐓𝐓𝐒 𝐅ᴀɪʟᴇᴅ ⚜️"
        )


@only_owner
async def unsafe(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "⚠️ 𝐑ᴇᴘʟʏ ᴋᴀʀ ᴋɪsɪ ᴜsᴇʀ ᴘᴇ /unsafe ᴜsᴇ ᴋʀ ⚜️"
        )

    user = update.message.reply_to_message.from_user

    if user.id == OWNER_ID:
        return await update.message.reply_text(
            "⚠️ 𝐎ᴡɴᴇʀ 𝐊ᴏ 𝐔ɴsᴀғᴇ 𝐍ʜɪ 𝐊ʀ Sᴀᴋᴛᴇ ⚜️"
        )

    SAFE_USERS.discard(user.id)

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
     ⚜️ 𝐔ɴsᴀғᴇᴅ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 👤 𝐔sᴇʀ » {user.first_name}
│ ☠️ 𝐒ᴛᴀᴛᴜs » 𝐑ᴇᴍᴏᴠᴇᴅ
│ 🔒 𝐀ᴄᴄᴇss » 𝐃ᴇɴɪᴇᴅ
╰─────────────❖

🪬 𝐓ʜᴇ 𝐏ʀᴏᴛᴇᴄᴛɪᴏɴ 𝐇ᴀs 𝐁ᴇᴇɴ 𝐓ᴀᴋᴇɴ ♱
"""
    )


@only_owner
async def gclock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global gc_locked

    gc_locked = True

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
     ⚜️ 𝐆𝐂 𝐋ᴏᴄᴋᴇᴅ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 🔒 𝐌ᴏᴅᴇ » 𝐀ᴄᴛɪᴠᴇ
│ 👑 𝐎ɴʟʏ » 𝐎ᴡɴᴇʀ + 𝐒ᴀғᴇ 𝐔sᴇʀs
│ ⚔️ 𝐀ᴄᴛɪᴏɴ » 𝐈ɴsᴛᴀɴᴛ 𝐃ᴇʟᴇᴛᴇ
╰─────────────❖

🪬 𝐓ʜɪs 𝐆𝐂 𝐇ᴀs 𝐅ᴀʟʟᴇɴ 𝐈ɴᴛᴏ 𝐒ɪʟᴇɴᴄᴇ ♱
⚜️ 𝐎ɴʟʏ 𝐓ʜᴇ 𝐂ʜᴏsᴇɴ 𝐌ᴀʏ 𝐒ᴘᴇᴀᴋ ⚔️
"""
    )


@only_owner
async def gcunlock(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global gc_locked

    gc_locked = False

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
    ⚜️ 𝐆𝐂 𝐔ɴʟᴏᴄᴋᴇᴅ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 🔓 𝐌ᴏᴅᴇ » 𝐃ɪsᴀʙʟᴇᴅ
│ 🌒 𝐒ᴛᴀᴛᴜs » 𝐅ʀᴇᴇ 𝐂ʜᴀᴛ
╰─────────────❖

🪬 𝐓ʜᴇ 𝐒ɪʟᴇɴᴄᴇ 𝐇ᴀs 𝐁ᴇᴇɴ 𝐁ʀᴏᴋᴇɴ ♱
"""
    )


async def gclock_watcher(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global gc_locked

    if not gc_locked:
        return

    if not update.message:
        return

    user_id = update.effective_user.id

    if user_id in SAFE_USERS:
        return

    try:
        await update.message.delete()
    except:
        pass
        
        # ===========================
# AUTO REPLY FEATURE
# ===========================

reply_users = {}

# ===========================
# CUSTOM REPLY TEXTS
# ===========================
# FORMAT:
# "your text here",
#
# EXAMPLE:
# "⚜️ Welcome Back ♱",
# "🖤 The Void Is Watching ⚔️",
# ===========================

REPLY_TEXTS = [
    "𝘾𝙔𝙐 𝙍𝙀 𝙍𝙉𝘿𝙔𝙆𝙀 𝘽𝘼𝘼𝙋 𝙎𝙀 𝘽𝙃𝙄𝘿𝙉𝙀 𝘼𝘼 𝙂𝙔𝘼?", "𝘾𝙃𝙇 𝘾𝙃𝙐𝘿 𝘼𝘽 𝙍𝙉𝘿 𝙆𝙀 𝙋𝙄𝙇𝙀𝙀",
    "𝙏𝙍𝙔 𝙈𝘼 𝙆𝙊   #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝘼𝘽𝘽𝙐 𝙋𝙀𝙇𝙀", "𝘾𝙃𝙐𝘿𝙂𝙀𝙂𝘼 𝙎𝘼𝘼𝙇 𝘽𝙃𝙍 𝙏𝙐𝙏𝙊 𝘽𝙀𝙏𝘼 🍑",
    "𝙔𝙀𝙃 𝙂𝙍𝙀𝙀𝙑 𝙁𝙔𝙏𝙀𝙍 𝙄𝙎𝙆𝙄 𝙈𝙆𝘽", "𝙃𝙑𝘼𝘽𝘼𝘼𝙕 𝘽𝘼𝙉𝙀𝙂𝘼 𝙏𝙈𝙍",
    "𝙅𝙇𝘿𝙄 𝙅𝙇𝘿𝙄 𝘾𝙃𝙐𝘿  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝘼𝘽𝘽𝙐 𝘽𝙐𝙎𝙎𝙔 𝙃𝘼𝙄", "𝘾𝙑𝙍 𝙆𝙍 𝙈𝘼𝙅𝘽𝙐𝙍𝙄𝙔𝘼 𝙉𝘼 𝙎𝙐𝙉𝘼",
    "𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝘼 𝙋𝘼𝙏𝙄  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝙃𝘼𝙄", "𝘽𝙃𝘼𝘼𝙂 𝙈𝘼𝙏 𝙋𝙄𝙇𝙇𝙀 𝙊𝙔𝙀",
    "𝘼𝘽𝙀 𝙇𝙊𝘿𝙐 𝙏𝙀𝙍𝙄 𝙂𝘼𝙉𝘿 𝙈𝙀 𝘿𝘼𝙉𝘿𝘼", " #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝙊𝙉 𝙏𝙊𝙋 𝘽𝘼𝘽𝙔",
    "𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝙄 𝘾𝙃𝙐𝙏 𝙈𝙀 𝘽𝙊𝙏 𝙆𝘼 𝙇𝙐𝙉𝘿", "𝘽𝙃𝘼𝂂 𝘽𝙃𝙊𝙎𝘿𝙄𝙆𝙀 𝘽𝙃𝘼𝂂",
    "𝘼𝙋𝙉𝙄 𝘼𝙈𝙈𝙄 𝙆𝙊 𝘽𝙃𝙀𝙅 𝙋𝘼𝙉𝙄 𝙉𝙄𝙆𝘼𝙇𝙉𝘼 𝙃", "𝙏𝙀𝙍𝘼 𝙆𝙃𝘼𝙉𝘿𝘼𝙉 𝙆𝙃𝘼𝙏𝘼𝙈",
    " #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝙆𝙄 𝘿𝙀𝙃𝙎𝙃𝘼𝙏", "𝘽𝘼𝘼𝙋 𝙎𝙀 𝘽𝘼𝙆𝘾𝙃𝙊𝘿𝙄 𝙉𝙃𝙄",
    "𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝙊 𝘾𝙃𝙊𝘿 𝘿𝙐𝙉𝙂𝘼", "𝙍𝘼𝙉𝘿𝙄 𝙆𝙀 𝘽𝘼𝘾𝘾𝙃𝙀",
    "𝘼𝐐𝘼𝙏 𝙈𝙀 𝙍𝙀𝙃 𝙇𝙊𝘿𝙀", "𝙏𝙀𝙍𝘼 𝘽𝘼𝘼𝙋 𝙃𝙐 𝙈𝘼𝙄",
    "𝘾𝙃𝘼𝙇 𝙉𝙄𝙆𝘼𝙇 𝘽𝙃𝙊𝙎𝘿𝙄𝙆𝙀", "𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝘼 𝘽𝙃𝙊𝙎𝘿𝘼",
    " #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝙄𝙎 𝙂𝙊𝘿", 
    "𝙏𝙀𝙍𝙄 𝙂𝘼𝘼𝙉𝘿 𝙁𝘼𝘼𝘿 𝘿𝙐𝙉𝙂𝘼", "𝙈𝘼𝘼 𝘾𝙃𝙐𝘿𝘼 𝘼𝙋𝙉𝙄",
    "     𝐊ʏᴜ 𝐑ᴇ 𝐑ᴀɴᴅɪ 𝐌𝐀 ᴋᴇ 𝐋ᴀᴅᴄᴏ  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ   𝐊ᴏ 𝐃ʙᴀ. ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ??🤬",
    "     𝐊ʏᴜ 𝐑ᴇ 𝐑ᴀɴᴅɪ 𝐌𝐀 ᴋᴇ 𝐋ᴀᴅᴄᴏ  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝐊ᴏ 𝐃ʙᴀ. ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ??😡",
    "     𝐊ʏᴜ 𝐑ᴇ 𝐑ᴀɴᴅɪ 𝐌𝐀 ᴋᴇ 𝐋ᴀᴅᴄᴏ  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝐊ᴏ 𝐃ʙᴀ. ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ??🤨",
    "     𝐊ʏᴜ 𝐑ᴇ 𝐑ᴀɴᴅɪ 𝐌𝐀 ᴋᴇ 𝐋ᴀᴅᴄᴏ   #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝐊ᴏ 𝐃ʙᴀ. ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ??😱",
    "     𝐊ʏᴜ 𝐑ᴇ 𝐑ᴀɴᴅɪ 𝐌𝐀 ᴋᴇ 𝐋ᴀᴅᴄᴏ  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝐊ᴏ 𝐃ʙᴀ. ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ??😮‍💨",
    "     𝐊ʏᴜ 𝐑ᴇ 𝐑ᴀɴᴅɪ 𝐌𝐀 ᴋᴇ 𝐋ᴀᴅᴄᴏ  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝐊ᴏ 𝐃ʙᴀ. ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ??😨",
    "     𝐊ʏᴜ 𝐑ᴇ 𝐑ᴀɴᴅɪ 𝐌𝐀 ᴋᴇ 𝐋ᴀᴅᴄᴏ  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝐊ᴏ 𝐃ʙᴀ. ɴʜɪ 𝐏ᴀʀᴇ ᴄʏᴀ??😟",
    "तू छोटा था तब तेरी मां का स्तन पान करता था मैं, उसके दूध में 60% क्रीम होता था, तू रोते हुए आता था और मैं तुझे लात मारके भागता था बोलता था हट साले मेरे लन्ड से निकले हुए मैल",
    "This message cannot be seen because you are randy",
    "GRIB MA K BACHAY GHAR ME ATTA LE AA HATER कामज़ोर KA BAAP  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ सरकार",
    "घिनौनी रंडी के बच्चे तु बात बात पर अपनी माँ क्यूँ चुदवाता है मादरचोद",
    "Chup kali maa ke रण्डी बच्चे",
    "Chl Harmzadi Ke लड़के",
    "Trymaa ki chut mein labubu",
    "khadi ho ब्राह्मण guru दक्षिणा me mera lund pakad",
    "Teri माँ के भोसड़े पर इतने बल्ले मारूंगा की IPL जीत जायेगी",
    "Dar mat pagli bas piche se karenge",
    "काले Doraemon रोता reh",
    "NEKAL MADARCHOD",
    "Yar apni ma mt nungy kr",
    "randycy तेरी माँ ke बुर me न्युक phod dunga",
    "end portal bn gya ab try ma iske andar chudegi",
    "Teri takli maa ke sar pr per rkhkr bolunga jutte saaf kr rndy",
    "jhutt bolke bachega tmkc Rndyke",
    "क्या रे Chai Wale Ke Ladke बनाऊ तुझे Fyter",
    "Teri mummy or papa kal accident me mar MADMAXe",
    "जब मैं तेरी माँ को जम कर चोदूंगा तो तेरी माँ रहम की भीख मांगेगी Samjha",
    "oye rndi ke ldke भगा to teri maa चमार जाति ki राँड",
    "सुबह शाम Teri माँ नंगी होगी",
    "क्या सोचा है तेरे जैसे MajDuR के लिए अपना TiMe wAsTe करुंगा Eww निकाल MaDaRchOd के धुर",
    "CHUP RNDIKE",
    "100% TERI MAA KA GULABHI BOSHDA HACK KARLIYA",
    "तुझ जैसे लोगो की Maa Ki Chut Mein अम्बुजा Cement से majboot ghar bna dena chahiye",
    "tri ma रंग बिरंगी रंडी",
    "चुप तेरी नानी का भोसड़ा",
    "तेरी माँ की चुत में ok"
]


@only_owner
async def chud(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "⚠️ 𝐑ᴇᴘʟʏ ᴋᴀʀ ᴜsᴇʀ ᴘᴇ /chud ᴜsᴇ ᴋʀ ⚜️"
        )

    user = update.message.reply_to_message.from_user
    chat_id = update.effective_chat.id

    reply_users[chat_id] = user.id

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
    ⚜️ 𝐑ᴇᴘʟʏ 𝐌ᴏᴅᴇ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 👤 𝐓ᴀʀɢᴇᴛ » {user.first_name}
│ 💬 𝐌ᴏᴅᴇ » 𝐀ᴄᴛɪᴠᴇ
│ 🪬 𝐑ᴇᴘʟʏ » 𝐄ɴᴀʙʟᴇᴅ
╰─────────────❖
"""
    )


@only_owner
async def chudaistop(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.effective_chat.id

    if chat_id in reply_users:
        del reply_users[chat_id]

    await update.message.reply_text(
"""
╔═══━━━── • ──━━━═══╗
   ⚜️ 𝐑ᴇᴘʟʏ 𝐒ᴛᴏᴘᴘᴇᴅ ⚜️
╚═══━━━── • ──━━━═══╝

🪬 𝐓ʜᴇ 𝐕ᴏɪᴄᴇs 𝐇ᴀᴠᴇ 𝐅ᴀʟʟᴇɴ 𝐒ɪʟᴇɴᴛ ♱
"""
    )


async def auto_reply_watcher(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message:
        return

    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in reply_users:
        return

    if user_id != reply_users[chat_id]:
        return

    try:
        await update.message.reply_text(
            random.choice(REPLY_TEXTS)
        )
    except Exception:
        pass
        
        # ===========================
# SET PHOTO FEATURE
# ===========================

PHOTO_LOOP = False


@only_owner
async def setphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global PHOTO_LOOP

    if not update.message.reply_to_message:
        return await update.message.reply_text(
            "⚠️ 𝐑ᴇᴘʟʏ ᴋᴀʀ ᴘʜᴏᴛᴏ ᴘᴇ /setphoto ᴜsᴇ ᴋʀ ⚜️"
        )

    photo = update.message.reply_to_message.photo

    if not photo:
        return await update.message.reply_text(
            "⚠️ 𝐏ʜᴏᴛᴏ 𝐑ᴇᴘʟʏ 𝐊ʀ ⚜️"
        )

    PHOTO_LOOP = True

    chat_id = update.effective_chat.id

    file = await context.bot.get_file(photo[-1].file_id)
    photo_bytes = await file.download_as_bytearray()

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
    ⚜️ 𝐏ʜᴏᴛᴏ 𝐋ᴏᴏᴘ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 🖼️ 𝐌ᴏᴅᴇ » 𝐀ᴄᴛɪᴠᴇ
│ 🤖 𝐁ᴏᴛs » 𝐒ᴡɪᴛᴄʜɪɴɢ
│ ⚔️ 𝐒ᴘᴇᴇᴅ » 𝐅ᴀsᴛ
╰─────────────❖

🪬 𝐓ʜᴇ 𝐓ʜʀᴏɴᴇ 𝐈s 𝐒ʜɪғᴛɪɴɢ ♱
"""
    )

    async def _photo_loop():
        while PHOTO_LOOP:
            for bot in bots:
                try:
                    await bot.set_chat_photo(
                        chat_id=chat_id,
                        photo=photo_bytes
                    )
                    await asyncio.sleep(0.05)
                except Exception as e:
                    print(f"[PHOTO LOOP ERROR] {e}")
                    await asyncio.sleep(0.1)

    asyncio.create_task(_photo_loop())


@only_owner
async def stopphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global PHOTO_LOOP

    PHOTO_LOOP = False

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
   ⚜️ 𝐏ʜᴏᴛᴏ 𝐒ᴛᴏᴘᴘᴇᴅ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 🌒 𝐌ᴏᴅᴇ » 𝐃ɪsᴀʙʟᴇᴅ
│ 🖼️ 𝐒ᴛᴀᴛᴜs » 𝐅ɪɴɪsʜᴇᴅ
╰─────────────❖

🪬 𝐓ʜᴇ 𝐓ʜʀᴏɴᴇ 𝐇ᴀs 𝐒ᴛᴏᴘᴘᴇᴅ 𝐒ʜɪғᴛɪɴɢ ♱
"""
    )

# ===========================
# MOON NC LOOP
# ===========================

moon_task = None

@only_owner
async def moonnc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global moon_task

    if not context.args:
        return await update.message.reply_text(
            "⚠️ 𝐔sᴇ » /moonnc <ɴᴀᴍᴇ> ⚜️"
        )

    target = " ".join(context.args)

    moon_emojis = [
    "🌙", "🌌", "🌒", "🌑", "🖤", "✨", "💫", "☄️",
    "🪬", "⚜️", "♱", "🌃", "🌠", "🌜", "🌛", "🫧",
    "🔮", "☁️", "🦢", "🌘", "🌗", "🌖", "⭐", "🌟",
    "🕯️", "🥀", "🩶", "🐺", "🌊", "🕊️", "🪐", "🦋",
    "🎭", "🎑", "🌚", "🌝", "🕸️", "🧿", "🫀", "🪽"
]

    async def moon_loop():

        while True:
            try:
                for emoji in moon_emojis:

                    name = f"{emoji} {target} 🌙"

                    for bot in bots:
                        try:
                            await bot.set_chat_title(
                                chat_id=update.effective_chat.id,
                                title=name
                            )
                        except:
                            pass

                    await asyncio.sleep(0)

            except:
                pass

    moon_task = asyncio.create_task(moon_loop())

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
      🌙 𝐌ᴏᴏɴ 𝐍𝐂 🌙
╚═══━━━── • ──━━━═══╝

🪬  #𝑴𝒂𝒅𝑴𝒂𝒙 ɢᴀᴡᴅ 𝐀ᴄᴛɪᴠᴀᴛᴇᴅ ♱
⚜️ 𝐓ᴀʀɢᴇᴛ » {target}
"""
    )


@only_owner
async def stopmoonnc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global moon_task

    if moon_task:
        moon_task.cancel()
        moon_task = None

    await update.message.reply_text(
"""
⚜️ 🌙 𝐌ᴏᴏɴ 𝐍𝐂 𝐒ᴛᴏᴘᴘᴇᴅ ♱
"""
    )
    # ===========================
# BAAP NC LOOP
# ===========================

baap_task = None

@only_owner
async def baapnc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global baap_task

    if not context.args:
        return await update.message.reply_text(
            "⚠️ 𝐔sᴇ » /baapnc <ɴᴀᴍᴇ> ⚜️"
        )

    target = " ".join(context.args)

    baap_emojis = [
    "👑", "⚜️", "🔥", "😈", "☠️", "💀", "🩸", "⚔️",
    "🖤", "🪬", "♱", "🦅", "🐉", "🦁", "🔱", "🗿",
    "🥷", "🦂", "🕶️", "🚬", "🩶", "🥀", "💣", "🛡️",
    "🧨", "👿", "🌪️", "🦇", "🐺", "🩻", "🕸️", "🔮",
    "⛓️", "🪦", "⚡", "🌑", "🌘", "🩸", "🎭", "🗡️"
]

    async def baap_loop():

        while True:
            try:
                for emoji in baap_emojis:

                    name = f"{emoji} {target} 𝐁𝐀𝐀𝐏"

                    for bot in bots:
                        try:
                            await bot.set_chat_title(
                                chat_id=update.effective_chat.id,
                                title=name
                            )
                        except:
                            pass

                    await asyncio.sleep(0)

            except:
                pass

    baap_task = asyncio.create_task(baap_loop())

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
      👑 𝐁𝐀𝐀𝐏 𝐍𝐂 👑
╚═══━━━── • ──━━━═══╝

⚔️ 𝐓ʜᴇ 𝐓ʜʀᴏɴᴇ 𝐇ᴀs 𝐀ᴡᴀᴋᴇɴᴇᴅ ♱
⚜️ 𝐓ᴀʀɢᴇᴛ » {target}
"""
    )


@only_owner
async def stopbaapnc(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global baap_task

    if baap_task:
        baap_task.cancel()
        baap_task = None

    await update.message.reply_text(
"""
⚜️ 👑 𝐁𝐀𝐀𝐏 𝐍𝐂 𝐒ᴛᴏᴘᴘᴇᴅ ♱
"""
    )
# ===========================
# REACT MODE FEATURE
# ===========================

REACT_MODE = False
REACT_EMOJI = "🤍"


@only_owner
async def react(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global REACT_MODE
    global REACT_EMOJI

    if len(context.args) == 0:
        return await update.message.reply_text(
            "⚠️ 𝐔sᴇ » /react 😭 ⚜️"
        )

    REACT_EMOJI = context.args[0]
    REACT_MODE = True

    await update.message.reply_text(
f"""
╔═══━━━── • ──━━━═══╗
      ⚜️ 𝐑ᴇᴀᴄᴛ ⚜️
╚═══━━━── • ──━━━═══╝

╭─❖
│ 😭 𝐄ᴍᴏᴊɪ » {REACT_EMOJI}
│ ⚔️ 𝐌ᴏᴅᴇ » 𝐀ᴄᴛɪᴠᴇ
│ 👑 𝐓ᴀʀɢᴇᴛ » 𝐎ᴡɴᴇʀ + 𝐒ᴜᴅᴏ
╰─────────────❖

🪬 𝐓ʜᴇ 𝐄ᴍᴏᴊɪ 𝐇ᴀs 𝐁ᴇᴇɴ 𝐒ᴜᴍᴍᴏɴᴇᴅ ♱
"""
    )


@only_owner
async def stopreact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global REACT_MODE

    REACT_MODE = False

    await update.message.reply_text(
"""
╔═══━━━── • ──━━━═══╗
   ⚜️ 𝐑ᴇᴀᴄᴛ 𝐒ᴛᴏᴘᴘᴇᴅ ⚜️
╚═══━━━── • ──━━━═══╝

🪬 𝐓ʜᴇ 𝐑ᴇᴀᴄᴛɪᴏɴs 𝐇ᴀᴠᴇ 𝐅ᴀʟʟᴇɴ 𝐒ɪʟᴇɴᴛ ♱
"""
    )


async def react_watcher(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global REACT_MODE
    global REACT_EMOJI

    if not REACT_MODE:
        return

    if not update.message:
        return

    user_id = update.effective_user.id

    # OWNER + SUDO USERS ONLY
    if user_id != OWNER_ID and user_id not in SUDO_USERS:
        return

    try:
        await update.message.reply_text(
            f"{REACT_EMOJI}"
        )

    except:
        pass
        

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

            # CORE
            app.add_handler(CommandHandler("start", start_cmd))
            app.add_handler(CommandHandler("menu", menu_cmd))
            app.add_handler(CommandHandler("ping", ping_cmd))
            app.add_handler(CommandHandler("status", status_cmd))
            app.add_handler(CommandHandler("myid", myid))

            # SUDO
            app.add_handler(CommandHandler("bheeklerandike", bheeklerandike))
            app.add_handler(CommandHandler("bhagmdc", bhagmdc))
            app.add_handler(CommandHandler("bhikari", bhikari))

            # NC COMMANDS
            app.add_handler(CommandHandler("emonc", emonc))
            app.add_handler(CommandHandler("raidnc", raidnc))
            app.add_handler(CommandHandler("gawdnc", gawdnc_cmd))
            app.add_handler(CommandHandler("shutupnc", shutupnc_cmd))
            app.add_handler(CommandHandler("rulerncloop", rulerncloop_cmd))
            app.add_handler(CommandHandler("gulam", gulam_cmd))
            app.add_handler(CommandHandler("moonnc", moonnc))
            app.add_handler(CommandHandler("baapnc", baapnc))

            # STOP COMMANDS
            app.add_handler(CommandHandler("stopgcnc", stopgcnc))
            app.add_handler(CommandHandler("stopgawdnc", stopgawdnc_cmd))
            app.add_handler(CommandHandler("stopshutupnc", stopshutupnc_cmd))
            app.add_handler(CommandHandler("stoprulerncloop", stoprulerncloop_cmd))
            app.add_handler(CommandHandler("stopgulam", stopgulam_cmd))
            app.add_handler(CommandHandler("stopmoonnc", stopmoonnc))
            app.add_handler(CommandHandler("stopbaapnc", stopbaapnc))
            app.add_handler(CommandHandler("stopall", stopall))

            # SPAM / SLIDE
            app.add_handler(CommandHandler("spamloop", spamloop))
            app.add_handler(CommandHandler("stopspam", stopspam))
            app.add_handler(CommandHandler("slidespam", slidespam))
            app.add_handler(CommandHandler("stopslidespam", stopslidespam))
            app.add_handler(CommandHandler("swipe", swipe))
            app.add_handler(CommandHandler("stopswipe", stopswipe))
            app.add_handler(CommandHandler("targetslide", targetslide))
            app.add_handler(CommandHandler("stopslide", stopslide))
            app.add_handler(CommandHandler("emospam", emospam))
            app.add_handler(CommandHandler("stopemospam", stopemospam))
            app.add_handler(CommandHandler("delay", delay_cmd))

            # ADMIN / MOD
            app.add_handler(CommandHandler("adminall", adminall))
            app.add_handler(CommandHandler("mute", mute))
            app.add_handler(CommandHandler("unmute", unmute))
            app.add_handler(CommandHandler("safe", safe))
            app.add_handler(CommandHandler("unsafe", unsafe))
            app.add_handler(CommandHandler("gclock", gclock))
            app.add_handler(CommandHandler("gcunlock", gcunlock))
            app.add_handler(CommandHandler("left", left))

            # EXTRA
            app.add_handler(CommandHandler("setphoto", setphoto))
            app.add_handler(CommandHandler("stopphoto", stopphoto))
            app.add_handler(CommandHandler("tts", tts))
            app.add_handler(CommandHandler("chud", chud))
            app.add_handler(CommandHandler("chudaistop", chudaistop))
            app.add_handler(CommandHandler("react", react))
            app.add_handler(CommandHandler("stopreact", stopreact))

            # MESSAGE WATCHERS (registered once per app)
            app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, mute_watcher), group=1)
            app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, gclock_watcher), group=2)
            app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, auto_reply_watcher), group=3)
            app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, react_watcher), group=4)

            apps.append(app)
            bots.append(app.bot)

            print(f"[OK] Bot added: {token[:20]}...")

        except Exception as e:
            print(f"[ERROR] Failed to add bot: {e}")

    if not apps:
        print("[FATAL] No bots loaded. Exiting.")
        return

    print(f"[INFO] Starting {len(apps)} bot(s)...")

    await asyncio.gather(*[app.initialize() for app in apps])
    await asyncio.gather(*[app.start() for app in apps])
    await asyncio.gather(
        *[app.updater.start_polling(drop_pending_updates=True) for app in apps]
    )

    print("[INFO] All bots running successfully ✅")

    try:
        await asyncio.Event().wait()

    except KeyboardInterrupt:
        print("[INFO] Stopping bots...")

    finally:
        for app in apps:
            try:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            except Exception as e:
                print(f"[WARN] Shutdown error: {e}")


if __name__ == "__main__":
    asyncio.run(main())