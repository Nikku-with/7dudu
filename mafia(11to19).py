# ============================================================
# ʀᴇɴᴏx – Ultimate Telegram Bot (Full Version)
# Created by: ʀᴇɴᴏx
# All rights reserved.
# ============================================================

import asyncio
import os
import json
import random
import time
import uuid
import logging
import shutil
import sys
import io
from datetime import datetime
import pytz

# ===== HARDCODED TOKENS (ORIGINAL) =====
TOKENS = [
"8740442350:AAFEKkI9LaPplgUGHJAs0Nksx4FRvCXOodU",

"8914647610:AAFduVfGwZPy5m1hUtw71S1IlrrPKrnQJcQ",

"8986433154:AAFYe7pwy6HI9AFUGxGt9qzSL_oTp5X1Pqs",

"8480288422:AAGeJVW3ohZQW9OlvkZc5YF-9IV5k8RydW4",

"8969591492:AAE9AzSLzdv4EkgFUpj0DJ9BWkR7YklVPqk",

"8905655120:AAHInA-8_wJRpcVj2aQys_9P2UfJvjVxQJ8",

"8924392149:AAFshP15kZMO8SDcbXX8KHnY2txxF2E6RuQ",

"8701656148:AAEwzRJv9M2UFrGK1ux0qi7ZZLbf4EBH_9E",

"8916393293:AAHmzhDEqC5eMCW_51gmK7b0NvTih8YbCHY",

"8979446390:AAHDm9135ZgHll18DGaHDHwxzZWNZMBhoKM",
]

# Allow override via environment variable (optional)
env_tokens = os.environ.get("BOT_TOKENS", "").strip()
if env_tokens:
    TOKENS = [t.strip() for t in env_tokens.split(",") if t.strip()]

if not TOKENS:
    raise ValueError("No bot tokens available. Set BOT_TOKENS or hardcode tokens.")

# ===== HARDCODED OWNER ID (ORIGINAL) =====
OWNER_ID = 8398082978
env_owner = os.environ.get("OWNER_ID", "").strip()
if env_owner.isdigit():
    OWNER_ID = int(env_owner)

# ===== CORRECT IMPORTS =====
from telegram import Update, ChatPermissions, helpers
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, filters,
    ContextTypes
)
from telegram.error import TelegramError, RetryAfter as TelegramRetryAfter, Forbidden, BadRequest
from gtts import gTTS

# ============================================================
# CONFIGURATION
# ============================================================

SUDO_FILE = "sudo_users.json"
DB_FILE = "bot_data.json"

# Global state
SUDO_USERS = {OWNER_ID}
GLOBAL_ADMINS = set()
SPY_MODE = True
CURRENT_PREFIX = "!"

# Delays (milliseconds)
NC_DELAY_MS = 150
SPAM_DELAY_MS = 900
RSPAM_DELAY_MS = 900
PFP_DELAY_MS = 900
VOICE_DELAY_MS = 2500
PIC_DELAY_MS = 3500
STICKER_DELAY_MS = 3500

nc_delays = {}
spm_delays = {}
rspm_delays = {}
pfp_delays = {}

# Task dictionaries
group_tasks = {}
keng_tasks = {}
spmnc_tasks = {}
ghostnc_tasks = {}
slidespam_tasks = {}
spm_loop_tasks = {}
rspm_tasks = {}
sticker_spm_tasks = {}
gif_spm_tasks = {}
media_spm_tasks = {}
voice_spm_tasks = {}
pfp_tasks = {}
spam_tasks = {}
spam1_tasks = {}
rspam_tasks_kartik = {}
vns_tasks = {}
pic_tasks = {}
sticker_tasks_store = {}
pfp_tasks_store = {}

# ===== FIX: Define missing dictionaries =====
nc_tasks = {}          # (if used elsewhere)
tnc_tasks = {}         # (if used elsewhere)
rnc_tasks = {}         # (if used elsewhere)

# Targeting
target_users = {}
target_slide_data = {}
targetslide_targets = {}
reply_kartik_targets = set()
react_targets = {}
swipe_mode = {}
muted_users = set()
known_chats = set()
known_users = set()
username_to_id = {}
user_names = {}
spy_sent = set()
group_leaders = {}
active_bots = {}  # token -> {"app": app, "username": username}

# ====================== TEXT COLLECTIONS ======================
RAID_TEXTS = ["2-3 ⱮƛӇƖƝЄ ӇƲЄ ƝƛӇƖ ӇƛƓƝЄ ԼƓЄ ", "ⱦєяє ɠɦαя кι αυятση кι вяα ƒαα∂ к αρηα кυятα ѕιℓωαυ яη∂ук ", "ƓƦƖƁ Ɱƛ Ƙ ƁƛƇӇƳ ƓӇƛƦ ⱮЄ ƛƬƬƛ ԼЄ ƛƛ ", "ƊӇƛƬ яη∂ιкєу ", "ƬЄƦƖ Ɱƛƛ Ƙƛ ƁӇƧƊƛ ", "Ƭєяι мα к вσѕ∂є м αιѕα ℓαт мαяυggα ηα gαтє ωαу σƒ ιη∂ια вαη נαєggα ", "ꪶ  ⱠƲƝ ƬЄ Ɣƛʝ ꪻ♡︎ ", "уααя αρηι мα мт ηυηgу кя ", "Ƭяу мσм кє ѕαтн вα∂ мαηηєяѕ кя∂υggα ", "ƬЄƦƖ Ɱƛ ƇӇƠƊƲƝ ", "ƬЄƦƖ Ɱƛ Ƙ ƁӇƠƧƊƛ ⱮƛƊƦƇӇƠƊ ", "ⱮƛƇƇӇƛƦ ƬⱮƘƇ ", "Ƭєяу мαα кσ qαвαя ηαѕєєв ηα нσ яη∂укє ", "ƲƬӇ яη∂к кυттє ", "ƤƛƦԼЄ Ɠ ƘӇƛЄƓƛ ƘƳƛ ƬƠⱮⱮƳ ", "ƁƖӇƛƦƖ ƓƛƝƓ ƬЄƦƖ Ɱƛ ƇӇƠƊƲƝ ", "ƬƲⱮ ƧƁ ƘƲƬƬƠ ƘƖ ʝӇƲƝƊ ƘƖ ⱮƘƁ ", "ƓƇ ԼЄƑƬ ԼЄ яη∂ιвαℓα ", "Ƭєяι мαα кι ƈнσтι ραкα∂ кє ∂єєωαя мє мααяυηgα ∂нαм ∂нαм кι αωααנ ααуєgι ", "ƁӇƛƓƝƛ ⱮƛƝƛ ӇƳ ƬⱮƘƁ ", "ƘƖ ⱮƘƁ ƳƦ ƁӇƛƓ ƘЄƧЄ ƦӇЄ ӇƠ ƓƛƦƖƁƠ ", "ƬⱮƘƇ ", "ƬⱮƘƁ ", "ƬƁƘƇ ", "ƦƝƊƘ ƁƛƇӇƳ ", "ƠƳЄ ƬƠⱮⱮƳ ƲƬӇ ƁӇƛƓƝƛ ƝƳ ӇƛƖ "]
NCEMO_EMOJIS = ["🎀", "👑", "😂", "🤪", "👻", "❤️", "🌺", "🧊", "✅", "😹", "😻", "💦", "🤍", "🖤", "🤎", "💜", "💙", "❤️", "🧡", "💛", "💚", "💦", "🧑🏻‍✈️", "👮🏻", "🧑🏻‍🎓", "🦋", "🐳", "🎚️", "💸", "🕯️", "❔", "❌", "⚕️", "➿", "✖️", "➰", "™️", "💠", "♻️", "🈲", "🈹", "🈵", "🈴", "㊗️", "‼️", "🍡", "🍧", "🍭", "🐙", "🍃", "🤸🏻", "🤷🏻", "😱", "🤣", "👾", "💤", "💢", "♥️", "💟", "❄️", "🐕", "🕸️", "🍥", "🚙", "🚗", "🚐", "🚚", "🚜", "🚌", "🔫", "🎛️", "🪙", "🖱️", "🪢"]
SWIPE_TEXTS = ["NAME ƘƠ ƤEʟƬE ӇƲE EƝƬƦƳ 🤣😎❤️‍🔥", "NAME ƬEƦƖ Ɱƛƛ ƘƖ ƇӇƲƬ ⱮE ʟƠƲƊƛ ⱮƛƊƛƦƇӇƠƊ 😂🩷🤚🏼", "NAME ƦEƤʟƳ ƘƛƦ ƓƛƦƖƁ ƊƛƦ ƘƳƲ ƦƛӇƛ Ӈ 😁🤙🏼🤍", "NAME ƇӇƛʟ ƬEƦƖ Ɱƛ ƇӇƠƊƲ ƤƛƬƛƘ ƤƛƬƛƘ ƘE 🤪👻🩶", "NAME ƇӇƲƊƘE ƧƤƛⱮ ƳƛӇƖ ƛƲƘƛƬ Ӈ ƬEƦƖ ƓƛƦƖƁ 😹🩵🙌🏼", "ƇƤ ƘƛƦ NAME ƓƛƦƖƁ ƁӇƛƛƓ ⱮƬ ƇӇƠƬEƳ 😂🩶🤚🏼", "NAME ƘƖ ⱮƲⱮⱮƳ ƘƠ ƦƝƊƖ ƁƛƝƛ ƊƲƝƓƛ ӇEӇEӇE 🤣💖✌🏼", "NAME ƘE ƁƛƛƤ ƊƛƦƘ ƳEӇ ӇƛƖ ƖƝƘƖ Ɱƛƛ ƘE ƳƛƛƦ 😆🩶🤚🏼", "ƘƛƁƛƊƖ ƔƛʟE NAME ƘƖ ⱮƘƁ 🤣👻💗", "ƛƦEƳ NAME ƘƖ ⱮƘƁ ƳƛƛƦ ƁӇƛƓ ƘƛƖƧE ƦӇE ӇƠ ƓƛƦƖƁƠ 😤👻💞", "ƛƦEƳ NAME ⱮƛƇƇӇƛƦ ƬⱮƘƇ 😂🩷✌🏾", "NAME ƬƲ ʟƛƊӇEƓƛ ӇƲⱮƧE ƬEƦƖ Ɱƛ ƇƠƊƘE ⱮƖƬƬƖ ⱮE ⱮƖʟƛƊEƝƓE ӇƲⱮ 😂🔥🤸🏻", "NAME ʟEƛƔE ʟE ƬƲ ƦƝƊƳƘE ƤƛƧƛƝƊ ƝƛƖ ƛƳƛ ⱮƦƘƠ 😏👋🏼", "NAME ƓƦƖƁ Ɱƛ Ƙ ƁƛƇӇƳ ƓӇƛƦ ⱮE ƛƬƬƛ ʟE ƛƛ 😂🥲", "NAME ƛƲƦƛƬƠ Ƙƛ ƘƛⱮ ƦƠƬƖ ƁƝƛƝƛ ӇƠƬƛ Ӈ ƬƠ NAME ƘƖ Ɱƛ ƳƛӇƛ ƘƳƲ ƇӇƲƊƦӇƖ 🤬🤣😭", "NAME ƬEƦƖ Ɱƛ ƘƠ ƧEƝƛƤƛƬƖ ƧE ƇӇƲƊƔƛƊEƝƓE 🪖🖲️🔥", "NAME ƬƦƳ ƓƝƊ ⱮE ƛEƧƛ ƁӇƛʟƛ ⱮƛƦƲƓƛ ƧƖƊӇƛ ⱮƠƲƝƬ EƔEƦEƧƬ ƤE ƦƲƘEƓƛ 💯🚀💔", "NAME ƬEƦƖ Ɱƛƛ ƬƛƘʟƖ ӇEӇEӇE 💖💛💚", "NAME ⱮƲJӇE ƝƲⱮƁEƦ ƘƖ ƘƳƛ ƵƛƦƲƦƛƬ\nⱮƛƖ ӇƲ EƘ ƤʟƲⱮƁEƦ 👨‍🔧\nJƛƁ ƇӇƠƊƝE Ƙƛ ⱮƛƝƝ ƘƦEƓƛ NAME ƘƖ Ɱƛƛ ƇƠƊ ƊƲƝƓƛ ƓӇƛƦ 😂🔧", "NAME ƬEƦƳ Ɱƛƛ ƘƠ ƘƛƁƛƦ ƝƛƧEEƁ Ɲƛ ӇƠ ƦƝƊƳƘE 😑🖕🏽💔", "NAME ʟƲƝ ƬE ƔƛJ 😂👏🏻✨", "NAME ƬEƦƳ ƝƛƝƖ ƇӇƲƊ ƓƳƖ ƊӇƛⱮ ƊӇƛⱮ ƊӇƛⱮ 🥁🔊😍"]
TARGET_SLIDE_TEXTS = ["𝙉𝙔 𝙉𝙔 𝙉𝙔 𝙈𝙀 𝙆𝙐𝘾𝙃 𝙉𝙔 𝙅𝙉𝙏𝘼 𝘽BS 𝙀𝙔 {name} 𝙆𝙄 𝙈𝘼 𝙍𝙉𝘿𝙔 𝙀𝙔 🤣🔥", "𝙊𝙔𝙔 𝙔𝙍𝙍 𝙔𝙀 {name} 𝙆𝙄 𝙈𝘼 𝙍𝙊𝙅 𝙍𝙊𝙅 𝙂𝙊𝘽𝘼𝙍 𝙆𝙃𝘼𝙆𝙍 𝘼𝙋𝙉𝘼 𝘽𝙐𝙉𝘿 𝘿𝙀𝙏𝙄 𝙀𝙔 😑🖕🏿🔥", "𝙊𝙔𝙔 {name} 𝙆𝙈𝙕𝙊𝙍 𝙏𝘼𝙏𝙏𝙀 𝙏𝙀𝙍𝙄 𝙈𝘼 𝙎𝘼𝘽𝙎𝙀 𝙎𝙀 𝘽𝙃𝙄𝙆 𝙌 𝙈𝘼𝙉𝙂𝙏𝙄 𝙀𝙔", "𝙊𝙔𝙔 {name} 𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝘼 𝘽𝙐𝙉𝘿 𝙆𝘼𝙇𝘼 𝙌 𝙀𝙔 😑🔥🤣🖕🏿🔥", "𝙀𝙑𝙀𝙍𝙔𝙏𝙃𝙄𝙉𝙂 𝙄𝙎 𝙊𝙆 𝘽𝙐𝙏 {name} 𝙆𝙄 𝙈𝘼 𝘾𝙐𝘿𝙉𝘼 𝙄𝙎 𝙋𝙀𝙍𝙈𝘼𝙉𝙀𝙉𝙏 🤣🔥", "{name} 𝙏𝘼𝙏𝙏𝙀 𝙏𝙀𝙍𝙄 𝙈𝘼 𝙆𝙈𝙕𝙊𝙍 𝙍𝙉𝘿𝙔 𝙀𝙔 𝙔𝘼𝙆𝙄𝙉 𝙉𝙔 𝙀𝙔 𝙏𝙊 𝘼𝙋𝙉𝙀 𝙎𝘼𝘽 𝘽𝘼𝘼𝙋 𝙎𝙀 𝙋𝙐𝘾𝙃𝙇𝙀 😑🔥", "𝘼𝙉𝘿𝙔 𝙈𝘼𝙉𝘿𝙔 𝙎𝘼𝙉𝘿𝙔 {name} 𝙏𝘼𝙏𝙏𝙀 𝙆𝙄 𝙆𝙈𝙕𝙊𝙍 𝙈𝘼 𝙎𝙏𝙍𝙊𝙉𝙂𝙀𝙎𝙏 𝙍𝙉𝘿𝙔 😑🖕🏿🔥🤣", "𝙊𝙔 𝙈𝙀 𝙆𝙐𝘾𝙃 𝙉𝙔 𝙎𝙐𝙉𝙐𝙉𝙂𝘼 𝘽𝙎 𝙔𝙀 {name} 𝙆𝙄 𝙈𝘼 𝙈𝙀𝙍𝙄 𝙋𝙑𝙏. 𝙍𝙉𝘿𝙔 𝙀𝙔 😑🔥", "𝘾𝙃𝙄 𝙔𝙍𝙍 𝙀𝙔 {name} 𝙆𝙄 𝙈𝘼 𝘿𝙐𝙎𝙏𝘽𝙄𝙉 𝙎𝙀 𝘿𝙄𝙇𝘿𝙊 𝙉𝙄𝙆𝘼𝙇 𝙆𝙍 𝘼𝙋𝙉𝙀 𝘽𝙐𝙉𝘿 𝙈𝙀 𝘿𝘼𝙇 𝙇𝙀𝙏𝙄 𝙀𝙔 😑🔥", "𝙊𝙔𝙔 {name} 𝙏𝘼𝙏𝙏𝙀 𝙈𝙐𝙅𝙀 𝘽𝘼𝘼𝙋 𝘽𝙉𝘼 𝙇𝙀 𝙉𝙔 𝙏𝙊 𝙏𝙀𝙍𝙄 𝙈𝘼 𝙍𝙉𝘿𝙔"]
KENG_TEMPLATES = [{"text":"NAME ⱮƎ ƬƎƦƖ ⱮƛƘƠ ƇӇƠƊƲƝƓƛ","emoji":"🥱"},{"text":"NAME ƇӇƲƤ ƦƝƊƳƘƎ","emoji":"😂"},{"text":"NAME ƲƬӇ ƦƝƊƖƘƎ ƁƛƇӇƎ","emoji":"🍌"},{"text":"NAME ƛƦE NAME JƛƖƧE ƘƲƬƬƠ ƘƠ ⱮƛƛƦ Ƙ HƲⱮ ƤƛƝƖ Ɣ ƝƛӇƖ ƤƲƇӇƬE ⱮƇ","emoji":"🩷"},{"text":"NAME Ƙƛ ƁƛƛƤ ƛƛƳƛ","emoji":"❔"},{"text":"NAME ƘƖ Ɱƛ Ƙƛ ƁƠƠƦ","emoji":"🤪"},{"text":"ƛƦE NAME ƁӇƛƓ ƘEƧE ƦӇE ӇƠ ƓƛƦEEƁƠ","emoji":"👻"},{"text":"NAME ƲƬӇƛƘ ƁƛƖƬӇƛƘ ʟƛƓƛ ⱮƇ","emoji":"😹"},{"text":"NAME ƵƠƦ ʟƛƓƛ ƝƇ ƇƔƦ ʟE ⱮƇ","emoji":"🤣"},{"text":"NAME ƇӇƛʟ JӇƲƘ ƦƝƊƘ","emoji":"😎"}]
SPMNC_LONG = ["NAME ƲƬӇ ƤƛƖƦ ƤƘƊ ӇƲⱮƛƦE\n\n\n\n\n\n"*40, "ƝƳ ƝƳ ⱮE ƘƲƇӇ ƝƳ JƛƝƬƛ ƁƧ NAME ƘƖ Ɱƛ ƦƝƊƳ EƳ\n\n\n\n\n\n"*40, "NAME ƲƬӇ ƘE ƁƛƖƬӇ ƦƝƊƘ\n\n\n\n\n\n"*40, "NAME ƬEƦƖ Ɱƛ ƘƖ ƇӇƲƬ ⱮE ƛƛƓ ʟƛƓƛ ƊƲƝƓƛ ⱮƇ\n\n\n\n\n\n"*40, "NAME ƬEƦƖ ⱮƠⱮ ƦƝƊƳ\n\n\n\n\n\n"*40, "NAME ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ\n\n\n\n\n\n"*40, "NAME JӇƛƬƲ ƧƛʟE ƁƛƛƤ ʟƠƓ ƧE ʟƛƊӇEƓƛ?\n\n\n\n\n\n"*40]
SPMNC_SMALL = ["NAME ƲƬӇ ƤƛƖƦ ƤƘƊ ӇƲⱮƛƦE","ƝƳ ƝƳ ⱮE ƘƲƇӇ ƝƳ JƛƝƬƛ ƁƧ NAME ƘƖ Ɱƛ ƦƝƊƳ EƳ","NAME ƲƬӇ ƘE ƁƛƖƬӇ ƦƝƊƘ","NAME ƬEƦƖ Ɱƛ ƘƖ ƇӇƲƬ ⱮE ƛƛƓ ʟƛƓƛ ƊƲƝƓƛ ⱮƇ","NAME ƬEƦƖ ⱮƠⱮ ƦƝƊƳ","NAME ƬEƦƖ Ɱƛ ƘƠ ƇӇƠƊƲƝ","NAME JӇƛƬƲ ƧƛʟE ƁƛƛƤ ʟƠƓ ƧE ʟƛƊӇEƓƛ?"]
REPLY_KARTIK_TEXTS = ["ƖƵƵƛƬ ƘƦƠ ƬƲⱮӇƛƦE ƁƛƛƤ ƊƛƦƘ ƘƖ 😑🙌🏾", "ƓƛƊƊӇƛ ƊƖƘӇƛ ƘӇƠƊ ƊƖƳƛ ƬEƦƖ Ɱƛƛ ƊƖƘӇƖ ƇӇƠƊ ƊƖƳƛ 🙊🤦🏾😂", "ƊƛƦƘ ƁƊⱮƠƧӇ ƧƤEƛƘƖƝƓ ƑƦƠⱮ ƬEƦƖ ⱮƘƁ🤦🏾☎️", "ƇƲƊƝƛ ⱮƝƛ ӇƛƖ 😩🤟🏻", "ƬEƦƖ Ɱƛƛ ƇƠƊ ƘE ⱮƛƦ ƊƲƝƓƛ 🤣🖕🏾", "ƬEƦƖ Ɱƛƛ ƇƲƊ ƦӇƖ ӇƛƖ ƝƛƇӇƠ 👻🕺", "ӇƳ ƇƠƬƲ 😉✌🏾", "ƇƳƛ", "ƑƛƧƬ ʟƖƘӇ", "𝙌 ❓🤨", "ƇƲƊ ƘE ⱮƦƓƳƛ ƘƳƛ 💀😹", "ӇʟƔ ƤƓʟ ƁӇƛƓ ⱮƬ 🏃‍♂️💨", "ƊƛƦƘ ƇӇƠƊ ƦӇƛ ӇƛƖ 👻🔥", "ƇƳƛ?", "ƬEƦƖ Ɱƛƛ ❓", "ƬEƦƖ ƁӇEƝ ⱮƛƦƊƲ ❓", "ӇEʟƤ ӇEʟƤ ⱮƬ ƘƦ ƇƠƬƲ 😩👍🏾", "ƤƲJƛ ƘƦ ƬEƦƛ ƁƛƛƤ ƊƛƦƘ ƘƖ 🙏🏾🔥", "ӇʟƔ ӇʟƔ ӇƛⱮʟƛ ӇƠƓƳƛ ƬEƦƖ ⱮƘƁ ⱮE 😱😂", "ƬEƦƖ ƁƘƇ ⱮE ƁƖƓƁƠƧƧ 📺😆", "ӇʟƔ ƦEƤʟƳ ƑƛƧƬ", "ƑƛƧƬ ƬƳƤE ƘƦ ƊƛƦ ⱮƬ 😤⌨️", "ӇEʟƤ ӇEʟƤ ƬEƦƖ Ɱƛƛ ƇӇƲƊ ƓƳƖ 😩", "ƊƛƦƘ ƛƁƁƲ ƤEʟ ƦӇE ӇƛƖ 👻💪", "ӇƳ ƬEƦƖ Ɱƛƛ ⱮƦ ƓƳƖ ƘƳƛ 😶💔", "ƛƔƔ ƬEƦƖ Ɱƛƛ ƘƠ ƤƠƠƘƖE ƁƝƛƘE ⱮƛƦƲƝƓƛ 🤣🎀", "ƘƳƛ ❓😑", "ƦƠ ⱮƬ 😂🤟🏻", "ƧƠƦƬ ƝӇƖ ƘƦƲƝƓƛ ƇƲƊ ƬƲ ƁƖƝƛ ƦƲƘE 😹🖕🏾", "ƬƛƘE ƳƠƲƦ ƬƖⱮE ƑƖƦ ƇƲƊ 😉✌🏾", "ӇʟƔ ƘƲƬƖƳƛ ƘE ʟƦƘE 🐶😆", "ӇʟƔ ӇʟƔ ⱮJƛ ƛƛƦӇƛ ƇƲƊƝE ⱮE 😜🔥", "ƊƛƦƘ ƓƝƊ ⱮƛƛƦ ƦӇE ӇƛƖ 👻", "ӇƳ ƇƠƬƲ ƁӇƓ ⱮƬ ƦƝƊƳ ƘE 🔥😑👍🏾", "ƁӇƛƓƝƛ ⱮƛƝƛ ӇƛƖ JƖ 🚫😎", "ƊƛƦƘ ƛƁƁƲ ƛƛƓƳE 🤣🩷🙌🏾", "ƬEƦƖ Ɱƛƛ ⱮƛƦƘE ⱮJƊƲƦƖ ƘӇƬⱮ 👍🏾", "ƘƳƛ ƊƛƦƘ ƬEƦƛ ƁƛƛƤ ӇƛƖ 👻❓", "ƘƳƛ ⱮƬʟƁ ƬEƦƖ Ɱƛƛ ƊƛƦƘ ƝE ƇƠƊƖ 😹🖕🏾", "ƬEƦƖ ƁӇEƝ ⱮƛƦƘE ƁӇƛƓ JƛƲƝƓƛ 🙋🏾🤪", "ƬEƦƖ ƁӇEƝ ⱮƛƦƘE ƊƛƦƘ ƁӇƛƓ ƓƳƛ 🤦🏾💔", "ƁӇƛƓ 𝙌 ƦӇƛ ӇƛƖ ❓", "ƬEƦƖ Ɱƛƛ ⱮƲⱮƁƛƖ ⱮE ƇƲƊEƓƖ 😌🩷🙌🏾", "ƬƳƤE ƘƦ Ɲƛ ƛƁ ƬEƦE ƁƛƛƤ ƘE ƧƛⱮƝE ⁉️", "ƘƦ ƬƳƤE ƬⱮƘƇ 😂🤟🏻", "JʟƊƖ ƇƲƊ 🤢", "ƁƖƝƛ ƦƲƘE ƬӇƲƘƛƖ ӇƠƓƖ ƬEƦƖ 😁😂", "ƁӇƛƓEƓƛ ƬƠ ƇƠƊ ƘE ⱮƛƦƊƲƝƓƛ 😑🙌🏾", "ƖƊӇƦ ƛJƛ ƇӇƠƬEƳ 👶🍼", "ƁӇƛƓ ⱮƬ ƘƲƬƬƖ ƘE 🙊😂", "ƬEƦƖ Ɱƛƛ ƘƠ ƁEƝ10 ⱮE ƇƠƊƲƝƓƛ 👽😱", "ƖƵƵƛƬ ƘƦEƓƛ ƛƛJƧE ƊƛƦƘ ƛƁƁƲ ƘƖ 😂🤟🏻", "ƬEƦƖ ƁӇEƝ ƘƖ ƤƠƠƘƖE ƓƔƝƊ ⱮE ʟƲƝ 🎀", "ƁӇƛƓ ⱮƬ ƁEƬE 😑🙌🏾", "ƖƊӇƦ ƛJƛ ʟƛƊʟE 😉❤️", "ƬEƦƖ ƓEƝƊ ⱮE 100 ӇƛƬӇ 💯🔥", "ƘƦ ƛƁ ӇƛƔƛƁƛƛƵƖ?", "ʟE ƛƛƓƳƛ ƬEƦƛ ƁƛƛƤ ƊƛƦƘ 👻👑", "ƁӇƛƓƝE ƧE ƘƲƇӇ ƝӇƖ ӇƠƓƛ 🐕❌", "ƁӇƛƓ ƁӇƛƓ ƬⱮƘƇ 😑😹", "ƁӇƛƓƛ ƁӇƛƓƛ ƘE ⱮƛƦƲƝƓƛ 🤣🩷🙌🏾", "ƁƝ ƛƁ ƑƳƬƦ 🤦🏾😎😂", "ƘƦ Ɲƛ ƑƳƬ 😁🔥", "ƁӇƛƓEƓƛ ❓", "ƁӇƛƓ JʟƊƖ 🐕🏳️‍🌈", "ӇʟƔ ƇƲƊƓƳƖ ƘƳƛ 💀😹", "ƊƛƦƘ ƛƛƓƳƛ 👻🔥", "ƬEƦE ƁƛƛƤ ƊƛƦƘ ƘƖ EƝƬƦƳ 👻😂", "ƦEⱮEⱮƁEƦ ƬӇE ƓƠƊ ƘEƝƓ ƊƛƦƘ 👻👑"]

# ====================== GHOSTNC TEXTS ======================
GHOST_TEXTS = [
"{TEXT} Gᴀɴᴅᴜ Bʜᴇɴᴄʜᴏᴅ ——➤(💩)",
"{TEXT} Mᴀᴅᴀʀᴄʜᴏᴅ Kᴀ Pɪʟʟᴀ ——➤(🐖)",
"{TEXT} Rᴀɴᴅɪ Kᴀ Bᴇᴛᴀ ——➤(🥴)",
"{TEXT} Hᴀʀᴀᴍᴋʜᴏʀ Sᴜᴀʀ ——➤(👿)",
"{TEXT} Bʜᴇɴᴋɪ Cʜᴜᴛ Lᴀᴜɴᴅᴀ ——➤(🔞)",
"{TEXT} Rᴀɴᴅɪᴋᴀ Pᴜᴛʀᴀ ——➤(🐕‍🦺)",
"{TEXT} Bʜᴏsᴅɪᴋᴇ Kᴀ Bᴀᴄᴄʜᴀ ——➤(🐸)",
"{TEXT} Lᴏᴅᴜ Kᴀ Bʜᴀɪ ——➤(🪣)",
"{TEXT} Kᴀᴍᴢᴏʀ Cʜᴜᴛɪʏᴀ ——➤(🥚)",
"{TEXT} Bʜɪᴋʜᴀʀɪ Kɪ Aᴜʟᴀᴅ ——➤(🪔)",
"{TEXT} Rᴀɴᴅɪ Kᴀ Pᴏʀᴀ ——➤(🤡)",
"{TEXT} Cʜᴜᴅᴀɪʟ Kɪ Sᴀʟᴀʜ ——➤(🪓)",
"{TEXT} Gʜᴀᴛɪʏᴀ Mᴀᴅᴀʀᴄʜᴏᴅ ——➤(🐷)",
"{TEXT} Tᴇʀᴀ Bᴀᴀᴘ X Mᴀᴅᴀʀᴄʜᴏᴅ ——➤(🐗)",
"{TEXT} Gᴀɴᴅ Mᴀʀᴀ Mᴜʟʟᴀ ——➤(🧟)",
"{TEXT} Cʜᴜᴅᴇɢɪ Tᴇʀɪ Bᴇʜᴇɴ ——➤(😈)",
"{TEXT} Bɪᴛᴄʜ Bᴏʏ Rᴀɴᴅɪᴋᴀ ——➤(🐺)",
"{TEXT} Hɪᴊʀᴀ Kɪ Oʟᴀᴅ ——➤(🧚)",
"{TEXT} Nᴀʟɪ Cʜᴀᴛɴᴇ Wᴀʟᴀ ——➤(🧽)",
"{TEXT} Gʜɪɴᴏɴɪ Mᴀᴋʜɪ Rᴀɴᴅ ——➤(🪰)",
"{TEXT} Cʜᴏᴛɪ Jᴀᴀᴛ Kᴀ Kᴜᴛᴛᴀ ——➤(🐕)",
"{TEXT} Tᴇʀɪ Mᴀ Aᴜʀ Rᴀɴᴅɪᴋᴀ ——➤(🌋)",
"{TEXT} Hɪᴊᴀʙ Pʜᴀᴅᴏ Bʜᴇɴᴄʜᴏᴅ ——➤(🧕)",
"{TEXT} Kɪ Mᴀᴀ Kɪ Cʜᴜᴛ Mᴀᴅᴀʀᴄʜᴏᴅ ——➤(🖕)",
"{TEXT} Cʜᴜᴛɪʏᴀ Nᴜᴍʙᴇʀᴅᴀʀ ——➤(🧠)",
"{TEXT} Bʜᴏsᴅɪᴋᴇ Kᴀ Pᴀᴘᴏʟᴀ ——➤(🍌)",
"{TEXT} Rᴀɴᴅ Kᴀ Bᴀᴅsʜᴀʜ ——➤(👑)",
"{TEXT} Mᴀᴅᴀʀᴄʜᴏᴅ Kᴀ Mᴀᴋʜɪ ——➤(🪳)",
"{TEXT} Bᴇʜᴇɴ Kᴀ Lᴀᴜɴᴅᴀ ——➤(🧦)",
"{TEXT} Gᴀɴᴅᴜ Gᴀᴜʀᴀᴠ Kᴀ Bʜᴀɪ ——➤(🐒)",
"{TEXT} Hᴀʀᴀᴍᴢᴀᴅᴀ Pɪʟʟᴀ ——➤(👹)",
"{TEXT} Cʜᴜᴅᴀɪʟ Kᴀ Cʜᴇʟᴀ ——➤(🧛)",
"{TEXT} Rᴀɴᴅɪ Kɪ Sᴀɴᴛᴀɴ ——➤(👶)",
"{TEXT} Lᴏᴅᴜ Rᴀᴍ Kᴀ Bᴀɴᴅᴀ ——➤(🐫)",
"{TEXT} Gʜᴀᴛɪʏᴀ Sʜᴇʀ ——➤(🦁)",
"{TEXT} Bʜɪᴋʜᴀʀɪ Kᴀ Rᴀᴊᴀ ——➤(🤴)",
"{TEXT} Mᴀᴋʜɪ Cʜᴏᴅ Kᴜᴛᴛᴀ ——➤(🪱)",
"{TEXT} Tᴇʀɪ Mᴀ Kɪ Jᴀʜᴀᴢ ——➤(🚢)",
"{TEXT} Gᴀɴᴅ Fᴀʀɪ Kᴇɴᴛᴏ ——➤(🧨)",
"{TEXT} Rᴀɴᴅɪᴋᴀ Mᴏɴsᴛᴇʀ ——➤(👾)",
"{TEXT} Tᴇʀɪ Mᴀ Kᴀ Bʜᴏsᴅᴀ Sᴀʟᴇ Mᴀᴅᴇʀᴄʜᴏᴅ Kɪ Aᴜʟᴀᴅ ——➤(🤬)",
"{TEXT} Gᴀɴᴅ Kɪ Dʜᴀᴀʀ Bʜᴏsᴅɪᴋᴇ Fᴀᴛᴇᴇ Hᴜᴇ Cᴏɴᴅᴏᴍ Kɪ Nᴀᴀᴊᴀɪs Pᴀɪᴅᴀɪsʜ ——➤(🧬)",
"{TEXT} Tᴇʀɪ Mᴀᴀ Kɪ Cʜᴏᴏᴛ Gᴀɴᴅ Kᴀʏ Tᴀᴛᴛᴏ Tᴇʀɪ Mᴀᴀ Kᴀ Bʜᴏsᴅᴀ Kᴀʀᴋᴇ Usᴋɪ Gᴀᴀɴᴅ Mᴀɪ Pɪɴɢ Pᴏɴɢ Kᴀʀ Dᴜɴɢᴀ ——➤(🏓)",
"{TEXT} Pʜᴀᴛᴇʟᴇ Nɪʀᴏᴅʜ Kᴇ Nᴀᴛɪᴊᴇ ——➤(🎈)",
"{TEXT} Tᴇʀɪ Gᴀᴀɴᴅ Mᴇɪɴ Kᴜᴛᴛᴇ Kᴀ Lᴜɴᴅ Tᴇʀɪ Jʜᴀᴀᴛᴇɪɴ Kᴀᴀᴛ Kᴀʀ Tᴇʀᴇ Mᴏᴏʜ Pᴀʀ Lᴀɢᴀ Kᴀʀ Uɴᴋɪ Fʀᴇɴᴄʜ Bᴇᴀʀᴅ Bᴀɴᴀ Dᴏᴏɴɢᴀ ——➤(🧔)",
"{TEXT} Cʜᴜᴛ Kᴀʏ Bᴀᴀʟ Nɪᴘᴘʟᴇ Kɪ Dʜᴀᴀʀ Tᴇʀɪ Gᴀᴀɴᴅ Mᴀɪ Rᴏᴀᴅ Rᴏʟʟᴇʀ Dᴇ Dᴜɴɢᴀ ——➤(🚜)",
"{TEXT} Cʜᴜʟʟᴜ Bʜᴀʀ Mᴜᴛʜ Mᴇɪɴ Dᴏᴏʙ Mᴀʀ Kᴀᴀʟɪ Cʜᴜᴛ Kᴇ Sᴀғᴇᴅ Jʜᴀᴀᴛ ——➤(💦)",
"{TEXT} Cʜᴜᴛɪʏᴇ Bᴇʜᴇɴᴄʜᴏᴅ Lᴀᴜᴅᴀ Mᴀᴅᴀʀᴄʜᴏᴅ Gᴀᴀɴᴅᴜ Bʜᴏsᴀᴅɪᴋᴇʏ ——➤(😤)",
"{TEXT} Gᴏᴛᴇ Kɪᴛɴᴇ Bʜɪ Bᴀᴅᴇʏ Hᴏ, Lᴜɴᴅ Kᴇ Nɪᴄʜᴇ Hɪ Rᴇʜᴛᴇɪɴ Hᴀɪɴ ——➤(🥜)",
"{TEXT} Cʜɪᴘᴋᴀʟɪ Kɪ Bʜɪɢɪ Cʜᴜᴛ Cʜᴏᴏᴛ Kᴀʏ Bᴀᴀʟ Cʜɪᴘᴋᴀʟɪ Kᴇ Jʜᴀᴀᴛ Kᴇ Pᴀsᴇᴇɴᴇ ——➤(🦎)",
"{TEXT} Mᴀᴅᴀʀ Cʜᴏᴅ Bʜᴏsᴅᴋᴇ Eꜱᴀ Lᴀɢᴛᴀ H Aᴘɴᴇ Hɪɪ Tᴀᴀᴀᴛᴇ Kᴀᴀᴛ Kᴇ Cʜɪᴘᴋᴀ Dɪʏᴀ Aᴘɴɪ Sʜᴀᴋᴀʟ Dᴇᴋʜ Lᴏᴅᴇᴇ Jᴇsᴇ Sʜᴀᴋᴀʟ Aᴜʀ Gᴀɴᴅ Mᴇ H Aᴀᴋᴀʟ ——➤(🧠)",
"{TEXT} Tᴇʀɪ Mᴀ Kɪ Gᴀɴᴅ Mᴇ Hᴀᴛʜɪ Kᴀ Lᴜɴᴅ Dᴀʟᴋᴇ Aꜱᴀ Cʜᴏᴅᴜɴɢᴀ Nᴀ Bᴀᴄʜᴀ Hᴏᴊᴀʏᴇɢᴀ Jᴏʜɴʏ Sɪɴs Kᴇ Lᴜɴᴅ Sᴇ Cʜᴜᴅᴡᴀᴜɴɢᴜ Bʜᴏsᴅɪᴋᴇ ——➤(🐘)",
"{TEXT} 14 Bᴀᴀᴘ Kɪ Nᴀᴊᴀɪs Oʟᴀᴅ Rᴀɴᴅɪ Kᴀʏ Bᴇᴇᴢ Cʜɪɴɴᴀʟᴇ ——➤(👨‍👩‍👧‍👦)",
"{TEXT} Gᴀɴᴅ Mᴀɪ Vɪᴍᴀʟ Kɪ Gᴏʟɪ Bɴᴀ Kᴀʀ Dᴇ Dᴜɴɢᴀ Bʜᴇɴᴄʜᴏ Tᴇʀɪ Gᴀᴀɴᴅ Mᴀɪ Rᴀɪʟᴡᴀʏ Sᴛᴀᴛɪᴏɴ Kᴀ Fᴀᴛᴀᴋ Dᴇ Dᴜɴɢᴀ ——➤(🚉)",
"{TEXT} Tᴇʀɪ Mᴀᴀ K Bʜᴏsᴅᴇ Mᴀɪ Mᴅʜ Cʜᴀɴᴀ Mᴀsᴀʟᴀ Dᴀᴀʟ Kᴀʀ Tᴇʀᴇ Bᴀᴀᴘ Kᴏ Vᴏ Sᴘɪᴄʏ Bʜᴏsᴅᴀ Kʜɪʟᴀ Dᴜɴɢᴀ ——➤(🌶️)",
"{TEXT} Sᴀʟᴀ Tᴀʀɪ Bʜᴀɴ Kᴏ Rᴏᴀᴅ Pᴀ Lᴀᴊᴀ Kᴀ Kᴀ Nᴀɴɢᴀ Kᴀʀ Kᴀ Bᴀᴀᴄʜᴏ Sᴀ Cʜᴜᴅ Vᴀᴜ ——➤(🚸)",
"{TEXT} Tᴇʀɪ Mᴀ Rᴀɴᴅɪ Tᴇʀᴀ Bᴀᴀᴘ Hɪᴢᴅᴀ Kᴀᴀʟɪ Gᴀᴀɴᴅ Kᴀʏ Kʜᴀᴅᴇ Bᴀᴀʟ Jʜᴀᴀᴛᴜ Rᴀɴᴅɪ Kᴀʏ Cʜᴏᴅᴜ ——➤(🕺)",
"{TEXT} Tᴇʀᴀ Bᴀᴀᴘ Jᴏʜɴʏ Sɪɴs Cɪʀᴄᴜs Kᴀʏ Bʜᴏsᴅᴇ Jᴏᴋᴇʀ Kɪ Cʜɪᴅᴀᴀs 14 Lᴜɴᴅ Kɪ Dʜᴀᴀʀ Tᴇʀɪ Mᴜᴍᴍʏ Kɪ Cʜᴜᴛ Mᴀɪ 200 Iɴᴄʜ Kᴀ Lᴜɴᴅ ——➤(🎪)",
"{TEXT} Mᴀᴀ K Lᴏᴅᴇ Tᴇʀᴇ Jᴇsᴇ Rᴀɴᴅɪ K Bᴀᴄᴄʜᴏ Kᴏ Bᴀᴄʜᴘᴀɴ Mᴀɪ Mᴀᴀʀ Dᴇɴᴀ Cʜɪʏᴇ ——➤(👶)",
"{TEXT} Mᴀᴅᴀʀᴄʜᴏᴅ Cʜᴜᴛᴍᴀʀᴋᴇ Tᴇʀɪ Tᴀᴛᴛɪ Jᴇsɪ Sʜᴀᴋʟ Pᴇ Pᴀᴅ Dᴜɴɢᴀ Bʜᴇɴ K Lᴏᴅᴇ Cʜᴜᴛɪʏᴇ ——➤(💢)",
"{TEXT} Bʜᴇɴᴄʜᴏᴅ Bᴀᴀᴘ Sᴇ Pᴀɴɢᴀ Mᴀᴛᴛ Lᴇ Wᴀʀɴᴀ Mᴀᴀ Cʜᴏᴅʜ Dɪ Jᴀʏᴇɢɪ ——➤(⚔️)"
]

# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def get_prefix():
    return CURRENT_PREFIX

def font(text: str) -> str:
    chars = {'a':'ᴀ','b':'ʙ','c':'ᴄ','d':'ᴅ','e':'ᴇ','f':'ғ','g':'ɢ','h':'ʜ','i':'ɪ','j':'ᴊ','k':'ᴋ','l':'ʟ','m':'ᴍ','n':'ɴ','o':'ᴏ','p':'ᴘ','q':'ǫ','r':'ʀ','s':'s','t':'ᴛ','u':'ᴜ','v':'ᴠ','w':'ᴡ','x':'x','y':'ʏ','z':'ᴢ','A':'ᴀ','B':'ʙ','C':'ᴄ','D':'ᴅ','E':'ᴇ','F':'ғ','G':'ɢ','H':'ʜ','I':'ɪ','J':'ᴊ','K':'ᴋ','L':'ʟ','M':'ᴍ','N':'ɴ','O':'ᴏ','P':'ᴘ','Q':'ǫ','R':'ʀ','S':'s','T':'ᴛ','U':'ᴜ','V':'ᴠ','W':'ᴡ','X':'x','Y':'ʏ','Z':'ᴢ'}
    return "".join(chars.get(c, c) for c in text)

def get_indian_time():
    tz = pytz.timezone('Asia/Kolkata')
    now = datetime.now(tz)
    return now.strftime("%I:%M:%S %p"), now.strftime("%d/%m/%Y")

bot_start_time = time.time()
def get_uptime():
    uptime = int(time.time() - bot_start_time)
    h = uptime // 3600
    m = (uptime % 3600) // 60
    s = uptime % 60
    return f"{h}h {m}m {s}s"

def load_data():
    global SPY_MODE, CURRENT_PREFIX
    if os.path.exists(SUDO_FILE):
        try:
            with open(SUDO_FILE, 'r') as f:
                for uid in json.load(f):
                    SUDO_USERS.add(int(uid))
        except (OSError, ValueError, TypeError) as e:
            logging.error("Failed to load sudo file: %s", e)
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, 'r') as f:
                data = json.load(f)
                for u in data.get("muted", []): muted_users.add(u)
                for u in data.get("reply_kartik", []): reply_kartik_targets.add(u)
                for k,v in data.get("targetslide", {}).items(): targetslide_targets[int(k)] = v
                for k,v in data.get("user_names", {}).items(): user_names[int(k)] = v
                for k,v in data.get("react_targets", {}).items(): react_targets[int(k)] = v
                for u in data.get("global_admins", []): GLOBAL_ADMINS.add(int(u))
                SPY_MODE = data.get("spy_mode", True)
                CURRENT_PREFIX = data.get("prefix", "!")
        except (OSError, ValueError, TypeError) as e:
            logging.error("Failed to load DB file: %s", e)

def save_data():
    data = {
        "muted": list(muted_users),
        "reply_kartik": list(reply_kartik_targets),
        "targetslide": targetslide_targets,
        "user_names": user_names,
        "react_targets": react_targets,
        "global_admins": list(GLOBAL_ADMINS),
        "spy_mode": SPY_MODE,
        "prefix": CURRENT_PREFIX
    }
    try:
        with open(DB_FILE, 'w') as f:
            json.dump(data, f)
        with open(SUDO_FILE, 'w') as f:
            json.dump(list(SUDO_USERS), f)
    except OSError as e:
        logging.error("Failed to save data: %s", e)

load_data()

async def is_admin_or_sudo(update: Update):
    uid = update.effective_user.id
    if uid in SUDO_USERS or uid in GLOBAL_ADMINS:
        return True
    await update.message.reply_text("❌ You are not authorised.")
    return False

def stop_task_group(task_dict, key):
    if key in task_dict:
        task_dict[key].clear()
        del task_dict[key]
        return True
    return False

async def get_group_leader(chat_id):
    if chat_id in group_leaders:
        leader = group_leaders[chat_id]
        try:
            await leader.bot.get_chat_member(chat_id, leader.bot.id)
            return leader
        except:
            del group_leaders[chat_id]
    for app_data in active_bots.values():
        app = app_data["app"]
        try:
            await app.bot.get_chat_member(chat_id, app.bot.id)
            group_leaders[chat_id] = app
            return app
        except:
            continue
    return None

async def is_leader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    leader_app = await get_group_leader(chat_id)
    if leader_app is None:
        return False
    return context.bot.id == leader_app.bot.id

# ============================================================
# TASK WORKERS
# ============================================================

async def nc_loop_worker(bot, chat_id, name, task_id):
    while chat_id in group_tasks and group_tasks[chat_id].get(bot.id) == task_id:
        try:
            delay = nc_delays.get(chat_id, NC_DELAY_MS) / 1000.0
            base = f"{name} {random.choice(RAID_TEXTS)}"
            emoji = random.choice(NCEMO_EMOJIS)
            base_len = len(base)
            emoji_len = len(emoji)
            if base_len < 120:
                repeats = (125 - base_len - 2) // emoji_len
                frame = base + "  " + (emoji * max(1, repeats))
            else:
                frame = base
            await bot.set_chat_title(chat_id, frame[:125])
            await asyncio.sleep(delay)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.1)
        except Exception as e:
            logging.error("nc_loop_worker error: %s", e)
            await asyncio.sleep(1)

async def ncemo_loop_worker(bot, chat_id, base_text, task_id):
    while chat_id in group_tasks and group_tasks[chat_id].get(bot.id) == task_id:
        try:
            delay = nc_delays.get(chat_id, NC_DELAY_MS) / 1000.0
            emoji = random.choice(NCEMO_EMOJIS) + random.choice(NCEMO_EMOJIS)
            base_len = len(base_text)
            emoji_len = len(emoji)
            repeats = max(1, (125 - base_len) // emoji_len)
            gap = " " * random.randint(1,3)
            frame = base_text + gap + (emoji * repeats)
            await bot.set_chat_title(chat_id, frame[:125])
            await asyncio.sleep(delay)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.1)
        except Exception as e:
            logging.error("ncemo_loop_worker error: %s", e)
            await asyncio.sleep(1)

async def keng_loop_worker(bot, chat_id, name, task_id):
    while chat_id in keng_tasks and keng_tasks[chat_id].get(bot.id) == task_id:
        try:
            delay = nc_delays.get(chat_id, NC_DELAY_MS) / 1000.0
            template = random.choice(KENG_TEMPLATES)
            base = template["text"].replace("NAME", name)
            emoji = template["emoji"]
            base_len = len(base)
            emoji_len = len(emoji)
            repeats = max(1, (125 - base_len) // emoji_len)
            gap = " " * random.randint(1,3)
            frame = base + gap + (emoji * repeats)
            await bot.set_chat_title(chat_id, frame[:125])
            await asyncio.sleep(delay)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.1)
        except Exception as e:
            logging.error("keng_loop_worker error: %s", e)
            await asyncio.sleep(1)

async def spmnc_worker(bot, chat_id, name, task_id):
    last_msg_time = 0
    while chat_id in spmnc_tasks and spmnc_tasks[chat_id].get(bot.id) == task_id:
        try:
            delay = nc_delays.get(chat_id, NC_DELAY_MS) / 1000.0
            small = random.choice(SPMNC_SMALL).replace("NAME", name)
            emoji = random.choice(NCEMO_EMOJIS)
            title = f"{emoji} {small} {emoji}"
            await bot.set_chat_title(chat_id, title[:125])
            await asyncio.sleep(delay)
            if time.time() - last_msg_time > 7.0:
                long_msg = random.choice(SPMNC_LONG).replace("NAME", name)
                await bot.send_message(chat_id, long_msg)
                last_msg_time = time.time()
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.1)
        except Exception as e:
            logging.error("spmnc_worker error: %s", e)
            await asyncio.sleep(1)

async def ghostnc_loop_worker(bot, chat_id, name, task_id):
    while chat_id in ghostnc_tasks and ghostnc_tasks[chat_id].get(bot.id) == task_id:
        try:
            delay = nc_delays.get(chat_id, NC_DELAY_MS) / 1000.0
            raw = random.choice(GHOST_TEXTS)
            title = raw.replace("{TEXT}", name)
            if len(title) > 125:
                title = title[:125]
            await bot.set_chat_title(chat_id, title)
            await asyncio.sleep(delay)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.1)
        except Exception as e:
            logging.error("ghostnc_loop_worker error: %s", e)
            await asyncio.sleep(1)

async def spam_task(bot, chat_id, text, task_id, dict_ref):
    while task_id in dict_ref.get(chat_id, []):
        try:
            delay = spm_delays.get(chat_id, SPAM_DELAY_MS) / 1000.0
            await bot.send_message(chat_id, text)
            await asyncio.sleep(delay)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.5)
        except Forbidden as e:
            logging.error("Spam task forbidden in chat %s: %s", chat_id, e)
            break
        except Exception as e:
            logging.error("spam_task error: %s", e)
            await asyncio.sleep(1.5)

# FIX: pass the correct task dictionary
async def rspm_sender(bot, chat_id, name, task_id, dict_ref):
    while task_id in dict_ref.get(chat_id, []):
        try:
            delay = rspm_delays.get(chat_id, RSPAM_DELAY_MS) / 1000.0
            base = f"{name} {random.choice(RAID_TEXTS)}"
            emoji = random.choice(NCEMO_EMOJIS)
            chunk = f"{base} {emoji}\n\n\n\n\n\n\n\n\n\n"
            msg = ""
            while len(msg) + len(chunk) < 4000:
                msg += chunk
            await bot.send_message(chat_id, msg)
            await asyncio.sleep(delay)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.5)
        except Forbidden:
            break
        except Exception as e:
            logging.error("rspm_sender error: %s", e)
            await asyncio.sleep(1.5)

async def media_spm_sender(bot, chat_id, media_type, file_id, dict_ref, task_id):
    while task_id in dict_ref.get(chat_id, []):
        try:
            delay = spm_delays.get(chat_id, SPAM_DELAY_MS) / 1000.0
            if media_type == "sticker":
                await bot.send_sticker(chat_id, file_id)
            elif media_type == "gif":
                await bot.send_animation(chat_id, file_id)
            elif media_type == "photo":
                await bot.send_photo(chat_id, file_id)
            elif media_type == "video":
                await bot.send_video(chat_id, file_id)
            elif media_type == "voice":
                await bot.send_voice(chat_id, file_id)
            await asyncio.sleep(delay)
        except Exception as e:
            logging.error("media_spm_sender error: %s", e)
            await asyncio.sleep(3)

async def vns_task(bot, chat_id, message, task_id):
    while task_id in vns_tasks.get(chat_id, []):
        try:
            def make_tts():
                tts = gTTS(text=message, lang='hi', slow=False)
                audio_bytes = io.BytesIO()
                tts.write_to_fp(audio_bytes)
                return audio_bytes
            audio_bytes = await asyncio.to_thread(make_tts)
            audio_bytes.seek(0)
            await bot.send_voice(chat_id, voice=audio_bytes)
            await asyncio.sleep(VOICE_DELAY_MS / 1000.0)
        except Exception as e:
            logging.error("vns_task error: %s", e)
            await asyncio.sleep(2)

async def pfp_loop_worker(bot, chat_id, task_id):
    while task_id in pfp_tasks.get(chat_id, []):
        try:
            delay = pfp_delays.get(chat_id, PFP_DELAY_MS) / 1000.0
            folder = os.path.join(os.path.dirname(__file__), 'downloads', str(chat_id))
            if not os.path.exists(folder):
                await asyncio.sleep(5)
                continue
            files = [f for f in os.listdir(folder) if f.endswith('.jpg')]
            if not files:
                await asyncio.sleep(5)
                continue
            pic = random.choice(files)
            pic_path = os.path.join(folder, pic)
            with open(pic_path, 'rb') as f:
                await bot.set_chat_photo(chat_id, photo=f)
            await asyncio.sleep(delay)
        except TelegramRetryAfter as e:
            await asyncio.sleep(e.retry_after + 0.1)
        except Exception as e:
            logging.error("pfp_loop_worker error: %s", e)
            await asyncio.sleep(2)

# ============================================================
# HELPER FOR TARGET INFO
# ============================================================
async def get_target_info(update: Update, context: ContextTypes.DEFAULT_TYPE, arg=None):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
        return user.id, user.first_name
    if update.message.entities:
        for ent in update.message.entities:
            if ent.type == 'text_mention' and ent.user:
                return ent.user.id, ent.user.first_name
            if ent.type == 'mention' and update.message.text:
                # Use proper slicing with entity offsets
                text = update.message.text
                uname = text[ent.offset+1:ent.offset+ent.length].lower()
                if uname in username_to_id:
                    uid = username_to_id[uname]
                    return uid, user_names.get(uid, uname)
    if arg:
        if arg.isdigit():
            uid = int(arg)
            return uid, user_names.get(uid, "User")
        if arg.startswith('@'):
            uname = arg[1:].lower()
            if uname in username_to_id:
                uid = username_to_id[uname]
                return uid, user_names.get(uid, uname)
    return None, None

# ============================================================
# COMMAND HANDLERS
# ============================================================

# ---------- NAME CHANGE ----------
async def cmd_nc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}nc <name>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    name = " ".join(context.args)
    if chat_id not in group_tasks:
        group_tasks[chat_id] = {}
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        group_tasks[chat_id][app.bot.id] = task_id
        asyncio.create_task(nc_loop_worker(app.bot, chat_id, name, task_id))
    await update.message.reply_text(f"🔄 NC started with `{helpers.escape_markdown(name)}`", parse_mode='Markdown')

async def cmd_dnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(group_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 NC stopped.")
    else:
        await update.message.reply_text("No NC running.")

async def cmd_ncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}ncemo <text>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    base_text = " ".join(context.args)
    if chat_id not in group_tasks:
        group_tasks[chat_id] = {}
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        group_tasks[chat_id][app.bot.id] = task_id
        asyncio.create_task(ncemo_loop_worker(app.bot, chat_id, base_text, task_id))
    await update.message.reply_text("🔄 Emoji NC started.")

async def cmd_dncemo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(group_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 Emoji NC stopped.")

async def cmd_kengnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}kengnc <name>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    name = " ".join(context.args)
    if chat_id not in keng_tasks:
        keng_tasks[chat_id] = {}
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        keng_tasks[chat_id][app.bot.id] = task_id
        asyncio.create_task(keng_loop_worker(app.bot, chat_id, name, task_id))
    await update.message.reply_text(f"🔺 KENG NC started for `{helpers.escape_markdown(name)}`", parse_mode='Markdown')

async def cmd_dkengnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(keng_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 KENG NC stopped.")

async def cmd_spmnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}spmnc <name>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    name = " ".join(context.args)
    if chat_id not in spmnc_tasks:
        spmnc_tasks[chat_id] = {}
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        spmnc_tasks[chat_id][app.bot.id] = task_id
        asyncio.create_task(spmnc_worker(app.bot, chat_id, name, task_id))
    await update.message.reply_text(f"⚡ SPMNC started for `{helpers.escape_markdown(name)}`", parse_mode='Markdown')

async def cmd_dspmnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(spmnc_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 SPMNC stopped.")

async def cmd_ghostnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}ghostnc <name>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    name = " ".join(context.args)
    if chat_id not in ghostnc_tasks:
        ghostnc_tasks[chat_id] = {}
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        ghostnc_tasks[chat_id][app.bot.id] = task_id
        asyncio.create_task(ghostnc_loop_worker(app.bot, chat_id, name, task_id))
    await update.message.reply_text(f"👻 GhostNC started with `{helpers.escape_markdown(name)}`", parse_mode='Markdown')

async def cmd_dghostnc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(ghostnc_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 GhostNC stopped.")
    else:
        await update.message.reply_text("No GhostNC running.")

async def cmd_delaync(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}delaync <ms>`", parse_mode='Markdown')
        return
    try:
        val = int(context.args[0])
        nc_delays[update.effective_chat.id] = max(10, val)
        await update.message.reply_text(f"✅ NC delay set to {val}ms for this group.")
    except ValueError:
        await update.message.reply_text("❌ Invalid number.")

# ---------- SPAM ----------
async def cmd_spm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}spm <text>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    text = " ".join(context.args)
    if chat_id not in spm_loop_tasks:
        spm_loop_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        spm_loop_tasks[chat_id].append(task_id)
        asyncio.create_task(spam_task(app.bot, chat_id, text, task_id, spm_loop_tasks))
    await update.message.reply_text("💬 SPM started.")

async def cmd_dspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(spm_loop_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 SPM stopped.")

async def cmd_rspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}rspm <name>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    name = " ".join(context.args)
    if chat_id not in rspm_tasks:
        rspm_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        rspm_tasks[chat_id].append(task_id)
        asyncio.create_task(rspm_sender(app.bot, chat_id, name, task_id, rspm_tasks))
    await update.message.reply_text(f"🔥 RSPM started for `{helpers.escape_markdown(name)}`", parse_mode='Markdown')

async def cmd_drspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(rspm_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 RSPM stopped.")

async def cmd_delaygcspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}delaygcspm <ms>`", parse_mode='Markdown')
        return
    try:
        val = int(context.args[0])
        spm_delays[update.effective_chat.id] = max(10, val)
        await update.message.reply_text(f"✅ SPM delay set to {val}ms.")
    except ValueError:
        await update.message.reply_text("❌ Invalid number.")

async def cmd_delayrspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}delayrspm <ms>`", parse_mode='Markdown')
        return
    try:
        val = int(context.args[0])
        rspm_delays[update.effective_chat.id] = max(10, val)
        await update.message.reply_text(f"✅ RSPM delay set to {val}ms.")
    except ValueError:
        await update.message.reply_text("❌ Invalid number.")

# ---------- KARTIK STYLE SPAM ----------
async def cmd_spam_kartik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}spam <text>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    text = " ".join(context.args)
    if chat_id not in spam_tasks:
        spam_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        spam_tasks[chat_id].append(task_id)
        asyncio.create_task(spam_task(app.bot, chat_id, text, task_id, spam_tasks))
    await update.message.reply_text("💬 Spam (Kartik style) started.")

async def cmd_stopspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(spam_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 Spam stopped.")

async def cmd_spam1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}spam1 <name>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    name = " ".join(context.args)
    if chat_id not in spam1_tasks:
        spam1_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        text = f"{name} {random.choice(RAID_TEXTS)}"
        spam1_tasks[chat_id].append(task_id)
        asyncio.create_task(spam_task(app.bot, chat_id, text, task_id, spam1_tasks))
    await update.message.reply_text(f"🎀 spam1 started for `{helpers.escape_markdown(name)}`", parse_mode='Markdown')

async def cmd_stopspam1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(spam1_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 spam1 stopped.")

async def cmd_rspam_kartik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}rspam <name>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    name = " ".join(context.args)
    if chat_id not in rspam_tasks_kartik:
        rspam_tasks_kartik[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        rspam_tasks_kartik[chat_id].append(task_id)
        asyncio.create_task(rspm_sender(app.bot, chat_id, name, task_id, rspam_tasks_kartik))
    await update.message.reply_text(f"🎲 Random spam started for `{helpers.escape_markdown(name)}`", parse_mode='Markdown')

async def cmd_stoprspam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(rspam_tasks_kartik, update.effective_chat.id):
        await update.message.reply_text("🛑 Random spam stopped.")

# ---------- MEDIA ----------
async def cmd_pic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text(f"Reply to a photo with `{helpers.escape_markdown(get_prefix())}pic`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    file_id = update.message.reply_to_message.photo[-1].file_id
    if chat_id not in pic_tasks:
        pic_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        pic_tasks[chat_id].append(task_id)
        asyncio.create_task(media_spm_sender(app.bot, chat_id, "photo", file_id, pic_tasks, task_id))
    await update.message.reply_text("🖼️ Pic spam started.")

async def cmd_stoppic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(pic_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 Pic spam stopped.")

async def cmd_sticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text(f"Reply to a sticker with `{helpers.escape_markdown(get_prefix())}sticker`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    file_id = update.message.reply_to_message.sticker.file_id
    if chat_id not in sticker_tasks_store:
        sticker_tasks_store[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        sticker_tasks_store[chat_id].append(task_id)
        asyncio.create_task(media_spm_sender(app.bot, chat_id, "sticker", file_id, sticker_tasks_store, task_id))
    await update.message.reply_text("🎭 Sticker spam started.")

async def cmd_stopsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(sticker_tasks_store, update.effective_chat.id):
        await update.message.reply_text("🛑 Sticker spam stopped.")

async def cmd_vns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}vns <text>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    text = " ".join(context.args)
    if chat_id not in vns_tasks:
        vns_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        vns_tasks[chat_id].append(task_id)
        asyncio.create_task(vns_task(app.bot, chat_id, text, task_id))
    await update.message.reply_text("🎤 Voice spam started.")

async def cmd_stopvns(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(vns_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 Voice spam stopped.")

# ---------- FAST MEDIA ----------
async def cmd_stickerspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not update.message.reply_to_message.sticker:
        await update.message.reply_text("Reply to a sticker with `!stickerspm`")
        return
    chat_id = update.effective_chat.id
    file_id = update.message.reply_to_message.sticker.file_id
    if chat_id not in sticker_spm_tasks:
        sticker_spm_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        sticker_spm_tasks[chat_id].append(task_id)
        asyncio.create_task(media_spm_sender(app.bot, chat_id, "sticker", file_id, sticker_spm_tasks, task_id))
    await update.message.reply_text("🎭 Sticker SPM started (fast).")

async def cmd_dstickerspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(sticker_spm_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 Sticker SPM stopped.")

async def cmd_gifspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not update.message.reply_to_message.animation:
        await update.message.reply_text("Reply to a GIF with `!gifspm`")
        return
    chat_id = update.effective_chat.id
    file_id = update.message.reply_to_message.animation.file_id
    if chat_id not in gif_spm_tasks:
        gif_spm_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        gif_spm_tasks[chat_id].append(task_id)
        asyncio.create_task(media_spm_sender(app.bot, chat_id, "gif", file_id, gif_spm_tasks, task_id))
    await update.message.reply_text("🎥 GIF SPM started.")

async def cmd_dgifspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(gif_spm_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 GIF SPM stopped.")

async def cmd_mediaspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    rm = update.message.reply_to_message
    if not rm or not (rm.photo or rm.video):
        await update.message.reply_text("Reply to a photo or video with `!mediaspm`")
        return
    chat_id = update.effective_chat.id
    file_id = rm.photo[-1].file_id if rm.photo else rm.video.file_id
    media_type = "photo" if rm.photo else "video"
    if chat_id not in media_spm_tasks:
        media_spm_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        media_spm_tasks[chat_id].append(task_id)
        asyncio.create_task(media_spm_sender(app.bot, chat_id, media_type, file_id, media_spm_tasks, task_id))
    await update.message.reply_text("🖼️ Media SPM started.")

async def cmd_dmediaspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(media_spm_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 Media SPM stopped.")

async def cmd_voicespm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not update.message.reply_to_message.voice:
        await update.message.reply_text("Reply to a voice note with `!voicespm`")
        return
    chat_id = update.effective_chat.id
    file_id = update.message.reply_to_message.voice.file_id
    if chat_id not in voice_spm_tasks:
        voice_spm_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        voice_spm_tasks[chat_id].append(task_id)
        asyncio.create_task(media_spm_sender(app.bot, chat_id, "voice", file_id, voice_spm_tasks, task_id))
    await update.message.reply_text("🎤 Voice SPM started.")

async def cmd_dvoicespm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(voice_spm_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 Voice SPM stopped.")

# ---------- PFP ----------
async def cmd_save(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("Reply to a photo with `!save`")
        return
    chat_id = update.effective_chat.id
    photo = update.message.reply_to_message.photo[-1]
    folder = os.path.join(os.path.dirname(__file__), 'downloads', str(chat_id))
    os.makedirs(folder, exist_ok=True)
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive(os.path.join(folder, f"{photo.file_unique_id}.jpg"))
    await update.message.reply_text("📸 Photo saved for this group.")

async def cmd_del(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("Reply to a saved photo with `!del`")
        return
    uid = update.message.reply_to_message.photo[-1].file_unique_id
    target = os.path.join(os.path.dirname(__file__), 'downloads', str(update.effective_chat.id), f"{uid}.jpg")
    if os.path.exists(target):
        os.remove(target)
        await update.message.reply_text("🗑️ Photo deleted.")
    else:
        await update.message.reply_text("⚠️ Photo not found in storage.")

async def cmd_gsave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("Reply to a photo with `!gsave`")
        return
    photo = update.message.reply_to_message.photo[-1]
    folder = os.path.join(os.path.dirname(__file__), 'downloads', 'global')
    os.makedirs(folder, exist_ok=True)
    file = await context.bot.get_file(photo.file_id)
    await file.download_to_drive(os.path.join(folder, f"{photo.file_unique_id}.jpg"))
    await update.message.reply_text("🌍 Photo saved to GLOBAL storage.")

async def cmd_delgpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        await update.message.reply_text("Reply to a saved photo with `!delgpfp`")
        return
    uid = update.message.reply_to_message.photo[-1].file_unique_id
    target = os.path.join(os.path.dirname(__file__), 'downloads', 'global', f"{uid}.jpg")
    if os.path.exists(target):
        os.remove(target)
        await update.message.reply_text("🗑️ Global photo deleted.")
    else:
        await update.message.reply_text("⚠️ Not found in global storage.")

async def cmd_delallmedia(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Only owner can do this.")
        return
    if not await is_leader(update, context): return
    dldir = os.path.join(os.path.dirname(__file__), 'downloads')
    if os.path.exists(dldir):
        shutil.rmtree(dldir)
        os.makedirs(os.path.join(dldir, 'global'), exist_ok=True)
        await update.message.reply_text("💥 All media deleted.")
    else:
        await update.message.reply_text("No media folder.")

async def cmd_gpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    folder = os.path.join(os.path.dirname(__file__), 'downloads', 'global')
    if not os.path.exists(folder):
        await update.message.reply_text("No global photos.")
        return
    files = [f for f in os.listdir(folder) if f.endswith('.jpg')]
    if not files:
        await update.message.reply_text("No global photos.")
        return
    success = 0
    for cid in known_chats:
        if cid > 0: continue
        pic = random.choice(files)
        pic_path = os.path.join(folder, pic)
        with open(pic_path, 'rb') as f:
            for app_data in active_bots.values():
                app = app_data["app"]
                try:
                    await app.bot.set_chat_photo(cid, photo=f)
                    success += 1
                    break
                except Exception as e:
                    logging.error("Failed to set photo in chat %s: %s", cid, e)
                    continue
    await update.message.reply_text(f"✅ Global PFP updated in {success} groups.")

async def cmd_pfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    folder = os.path.join(os.path.dirname(__file__), 'downloads', str(chat_id))
    if not os.path.exists(folder) or not [f for f in os.listdir(folder) if f.endswith('.jpg')]:
        await update.message.reply_text("No photos saved for this group. Use `!save` first.")
        return
    if chat_id not in pfp_tasks:
        pfp_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        pfp_tasks[chat_id].append(task_id)
        asyncio.create_task(pfp_loop_worker(app.bot, chat_id, task_id))
    await update.message.reply_text("🪄 PFP cycling started.")

async def cmd_dpfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if stop_task_group(pfp_tasks, update.effective_chat.id):
        await update.message.reply_text("🛑 PFP cycling stopped.")

async def cmd_delaypfp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text("Usage: `!delaypfp <ms>`", parse_mode='Markdown')
        return
    try:
        val = int(context.args[0])
        pfp_delays[update.effective_chat.id] = max(10, val)
        await update.message.reply_text(f"✅ PFP delay set to {val}ms.")
    except ValueError:
        await update.message.reply_text("❌ Invalid number.")

# ---------- TARGETING ----------
async def cmd_target(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text(f"Reply to a user's message with `{helpers.escape_markdown(get_prefix())}target`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    target_id = update.message.reply_to_message.from_user.id
    if chat_id not in target_users:
        target_users[chat_id] = set()
    target_users[chat_id].add(target_id)
    await update.message.reply_text("🎯 Target locked.")

async def cmd_stoptarget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    if chat_id in target_users:
        target_users[chat_id].clear()
        await update.message.reply_text("🛑 Target removed.")

async def cmd_targetcp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not context.args:
        await update.message.reply_text(f"Usage: Reply to user with `{helpers.escape_markdown(get_prefix())}targetcp <message>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    target_id = update.message.reply_to_message.from_user.id
    msg = " ".join(context.args)
    key = f"{chat_id}_{target_id}"
    target_slide_data[key] = msg
    await update.message.reply_text(f"🌀 Custom slide set: {msg}")

async def cmd_stoptargetcp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    keys = [k for k in target_slide_data if k.startswith(f"{chat_id}_")]
    for k in keys:
        del target_slide_data[k]
    await update.message.reply_text("🛑 Custom slide stopped.")

async def cmd_targetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    uid, name = await get_target_info(update, context, context.args[0] if context.args else None)
    if not uid:
        await update.message.reply_text("⚠️ Reply to a user or tag them.")
        return
    targetslide_targets[uid] = name
    save_data()
    await update.message.reply_text(f"🎯 Target slide locked on {name}.")

async def cmd_dtargetslide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    uid, _ = await get_target_info(update, context, context.args[0] if context.args else None)
    if not uid:
        await update.message.reply_text("⚠️ Reply to a user or tag them.")
        return
    if uid in targetslide_targets:
        del targetslide_targets[uid]
        save_data()
        await update.message.reply_text("🛑 Target slide stopped.")

async def cmd_slidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not context.args:
        await update.message.reply_text(f"Reply to a message with `{helpers.escape_markdown(get_prefix())}slidespam <text>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    msg = " ".join(context.args)
    if chat_id not in slidespam_tasks:
        slidespam_tasks[chat_id] = []
    for app_data in active_bots.values():
        app = app_data["app"]
        task_id = str(uuid.uuid4())
        slidespam_tasks[chat_id].append(task_id)
        asyncio.create_task(spam_task(app.bot, chat_id, msg, task_id, slidespam_tasks))
    await update.message.reply_text("💥 Slidespam started.")

async def cmd_dslidespam(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    if chat_id in slidespam_tasks:
        del slidespam_tasks[chat_id]
        await update.message.reply_text("🛑 Slidespam stopped.")
    else:
        await update.message.reply_text("No slidespam running in this chat.")

async def cmd_replykartik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    uid, name = await get_target_info(update, context, context.args[0] if context.args else None)
    if not uid:
        await update.message.reply_text("⚠️ Reply to a user or tag them.")
        return
    reply_kartik_targets.add(uid)
    save_data()
    await update.message.reply_text("💬 ReplyKartik enabled for this user.")

async def cmd_dreplykartik(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    uid, _ = await get_target_info(update, context, context.args[0] if context.args else None)
    if not uid:
        await update.message.reply_text("⚠️ Reply to a user or tag them.")
        return
    if uid in reply_kartik_targets:
        reply_kartik_targets.remove(uid)
        save_data()
        await update.message.reply_text("🛑 ReplyKartik stopped.")

async def cmd_react(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message or not context.args:
        await update.message.reply_text("Reply to a user and provide emoji: `!react <emoji>`")
        return
    uid = update.message.reply_to_message.from_user.id
    emoji = context.args[0]
    if emoji not in ["🤣","😭","🔥","🤪","❤️"]:
        await update.message.reply_text("Allowed emojis: 🤣 😭 🔥 🤪 ❤️")
        return
    react_targets[uid] = emoji
    save_data()
    await update.message.reply_text(f"✅ Auto‑react set for user with {emoji}.")

async def cmd_dreact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to the user.")
        return
    uid = update.message.reply_to_message.from_user.id
    if uid in react_targets:
        del react_targets[uid]
        save_data()
        await update.message.reply_text("🛑 Auto‑react stopped.")

async def cmd_swipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}swipe <name>`", parse_mode='Markdown')
        return
    chat_id = update.effective_chat.id
    swipe_mode[chat_id] = " ".join(context.args)
    await update.message.reply_text("⚡ Swipe mode ON.")

async def cmd_dswipe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    if chat_id in swipe_mode:
        del swipe_mode[chat_id]
        await update.message.reply_text("🛑 Swipe mode OFF.")

# ---------- ADMIN ----------
async def cmd_addsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can add sudo.")
        return
    if not await is_leader(update, context): return
    uid, name = await get_target_info(update, context, context.args[0] if context.args else None)
    if uid:
        SUDO_USERS.add(uid)
        save_data()
        await update.message.reply_text(f"👑 {name} added as SUDO.")
    else:
        await update.message.reply_text("Reply to a user or provide ID.")

async def cmd_delsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can remove sudo.")
        return
    if not await is_leader(update, context): return
    uid, name = await get_target_info(update, context, context.args[0] if context.args else None)
    if uid and uid in SUDO_USERS:
        SUDO_USERS.remove(uid)
        save_data()
        await update.message.reply_text(f"🗑️ {name} removed from SUDO.")
    else:
        await update.message.reply_text("User not found or not sudo.")

async def cmd_listsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    sudo_list = []
    for u in SUDO_USERS:
        name = user_names.get(u, "Unknown")
        sudo_list.append(f"• {name} (`{u}`)")
    await update.message.reply_text("👑 SUDO Users:\n" + "\n".join(sudo_list), parse_mode='Markdown')

async def cmd_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can add global admins.")
        return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user.")
        return
    uid = update.message.reply_to_message.from_user.id
    GLOBAL_ADMINS.add(uid)
    save_data()
    await update.message.reply_text(f"⭐ Global admin added: `{uid}`", parse_mode='Markdown')

async def cmd_radmin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can remove global admins.")
        return
    if not await is_leader(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user.")
        return
    uid = update.message.reply_to_message.from_user.id
    if uid in GLOBAL_ADMINS:
        GLOBAL_ADMINS.remove(uid)
        save_data()
        await update.message.reply_text(f"❌ Global admin removed: `{uid}`", parse_mode='Markdown')

async def cmd_adminlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    admins = [f"`{u}`" for u in GLOBAL_ADMINS]
    text = "📜 Global Admins:\n" + "\n".join(admins) if admins else "No global admins."
    await update.message.reply_text(text, parse_mode='Markdown')

async def cmd_mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    uid, name = await get_target_info(update, context, context.args[0] if context.args else None)
    if uid:
        muted_users.add(uid)
        save_data()
        await update.message.reply_text(f"🔇 {name} muted.")
    else:
        await update.message.reply_text("Reply to a user or tag them.")

async def cmd_unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    uid, name = await get_target_info(update, context, context.args[0] if context.args else None)
    if uid and uid in muted_users:
        muted_users.remove(uid)
        save_data()
        await update.message.reply_text(f"🔊 {name} unmuted.")
    else:
        await update.message.reply_text("User not muted.")

async def cmd_mutelist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not muted_users:
        await update.message.reply_text("No muted users.")
        return
    lines = []
    for u in muted_users:
        name = user_names.get(u, "Unknown")
        lines.append(f"• {name} (`{u}`)")
    await update.message.reply_text("🔇 Muted Users:\n" + "\n".join(lines), parse_mode='Markdown')

async def promote_user(bot, chat_id, uid, full=True):
    return await bot.promote_chat_member(
        chat_id=chat_id, user_id=uid, is_anonymous=False,
        can_change_info=full, can_delete_messages=full,
        can_invite_users=full, can_restrict_members=full,
        can_pin_messages=full, can_promote_members=full,
        can_manage_chat=full, can_manage_video_chats=full
    )

async def cmd_promote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    uid, name = await get_target_info(update, context, context.args[0] if context.args else None)
    if not uid:
        await update.message.reply_text("Reply to a user.")
        return
    try:
        await promote_user(context.bot, update.effective_chat.id, uid, True)
        await update.message.reply_text(f"✅ {name} promoted.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def cmd_demote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    uid, name = await get_target_info(update, context, context.args[0] if context.args else None)
    if not uid:
        await update.message.reply_text("Reply to a user.")
        return
    try:
        await promote_user(context.bot, update.effective_chat.id, uid, False)
        await update.message.reply_text(f"🛑 {name} demoted.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def cmd_promoteallbots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    success = 0
    for app_data in active_bots.values():
        app = app_data["app"]
        try:
            await promote_user(app.bot, chat_id, app.bot.id, True)
            success += 1
        except:
            pass
    await update.message.reply_text(f"✅ Promoted {success} bots.")

async def cmd_promoteall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    success = 0
    for uid in known_users:
        try:
            await promote_user(context.bot, chat_id, uid, True)
            success += 1
        except:
            pass
    await update.message.reply_text(f"✅ Promoted {success} users.")

async def cmd_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    for app_data in active_bots.values():
        app = app_data["app"]
        try:
            await app.bot.leave_chat(chat_id)
        except:
            pass
    await update.message.reply_text("👋 All bots left.")

async def cmd_spy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}spy on/off`", parse_mode='Markdown')
        return
    global SPY_MODE
    mode = context.args[0].lower()
    if mode == "on":
        SPY_MODE = True
        save_data()
        await update.message.reply_text("👀 Spy mode ON.")
    elif mode == "off":
        SPY_MODE = False
        save_data()
        await update.message.reply_text("🚫 Spy mode OFF.")
    else:
        await update.message.reply_text("Use on or off.")

async def cmd_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}cmd <newprefix>`", parse_mode='Markdown')
        return
    global CURRENT_PREFIX
    new = context.args[0].strip()
    if not new:
        await update.message.reply_text("Prefix cannot be empty.")
        return
    if len(new) > 5:
        await update.message.reply_text("Prefix too long (max 5).")
        return
    old = CURRENT_PREFIX
    CURRENT_PREFIX = new
    save_data()
    await update.message.reply_text(f"✅ Prefix changed from `{helpers.escape_markdown(old)}` to `{helpers.escape_markdown(new)}`.", parse_mode='Markdown')

# ---------- MENU COMMANDS ----------
async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_leader(update, context): return
    prefix = get_prefix()
    owner_mention = f"[Owner](tg://user?id={OWNER_ID})"
    main_text = f"""
╔════════════════════════════════════
║╭━━━『 🤖 𝐑ᴇɴᴏx • 𝐌ᴀɪɴ 𝐌ᴇɴᴜ 』━━━╮
┃
┃ 👑 𝐂ʀᴇᴀᴛᴇᴅ ʙʏ ➜ {owner_mention}
┃ ⚡ 𝐏ʀᴇғɪx ➜ "{helpers.escape_markdown(prefix)}"
┃ ⏱️ 𝐔ᴘᴛɪᴍᴇ ➜ {get_uptime()}
┃ 🤖 𝐀ᴄᴛɪᴠᴇ 𝐁ᴏᴛs ➜ {len(active_bots)}
┃
╰━━━━━━━━━━━━━━━━━━━━━━━━━━╯║

🪐 Type the following commands to see details:

• `{prefix}𝐌ᴇɴᴜ1` – 𝐍ᴄ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs
• `{prefix}𝐌ᴇɴᴜ2` – 𝐒ᴘᴍ ᴀʟʟ ᴄᴏᴍᴍᴀɴᴅs
• `{prefix}𝐌ᴇɴᴜ3` – 𝐌ᴇᴅɪᴀ ᴏʀ sᴘᴀᴍ ᴄᴏᴍᴍᴀɴᴅs
• `{prefix}𝐌ᴇɴᴜ4` – 𝐓ᴀʀɢᴇᴛ & 𝐑ᴇᴀᴄᴛ
• `{prefix}𝐌ᴇɴᴜ5` – 𝐀ᴅᴍɪɴ & 𝐂ᴏɴᴛʀᴏʟ
• `{prefix}𝐌ᴇɴᴜ6` – 𝐌ᴜsɪᴄ & 𝐔ᴛɪʟɪᴛɪᴇs

Use `{prefix}menu<number>` to explore.
"""
    await update.message.reply_text(main_text, parse_mode='Markdown')

async def cmd_menu1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_leader(update, context): return
    prefix = get_prefix()
    text = f"""
💫 𝐌ᴇɴᴜ 1 – 𝐍ᴀᴍᴇ 𝐂ʜᴀɴɢᴇʀ
{prefix}𝐍ᴄ <name>       – RAID text + emoji (fast)
{prefix}𝐍ᴄᴇᴍᴏ <text>    – Emoji‑suffix
{prefix}𝐊ᴇɴɢɴᴄ <name>   – KENG templates
{prefix}𝐒ᴘᴍɴᴄ <name>    – Title + long msg
{prefix}𝐆ʜᴏsᴛɴᴄ <name>  – GhostNC (abusive texts with {{TEXT}} placeholder)
{prefix}𝐃ɴᴄ / 𝐃ɴᴄᴇᴍᴏ / 𝐃ᴋᴇɴɢɴᴄ / 𝐃sᴘᴍɴᴄ / 𝐃ɢʜᴏsᴛɴᴄ – 𝐒ᴛᴏᴘ
{prefix}𝐃ᴇʟᴀʏɴᴄ <ms>    – 𝐒ᴇᴛ 𝐃ᴇʟᴀʏ

➡️ Type `{prefix}help` to go back to Main Menu.
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def cmd_menu2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_leader(update, context): return
    prefix = get_prefix()
    text = f"""
🎯 𝐌ᴇɴᴜ 2 – 𝐒ᴘᴀᴍ
{prefix}𝐒ᴘᴍ <text>      – normal spam
{prefix}𝐑sᴘᴍ <name>     – heavy RAID spam
{prefix}𝐒ᴘᴀᴍ <text>     – Kartik style
{prefix}𝐒ᴘᴀᴍ1 <name>    – template spam
{prefix}𝐑sᴘᴀᴍ <name>    – random spam
{prefix}𝐃sᴘᴍ / 𝐃ʀsᴘᴍ / 𝐒ᴛᴏᴘsᴘᴀᴍ / 𝐒ᴛᴏᴘsᴘᴀᴍ1 / 𝐒ᴛᴏᴘʀsᴘᴀᴍ – 𝐒ᴛᴏᴘ
{prefix}𝐃ᴇʟᴀʏɢᴄsᴘᴍ <ms> / 𝐃ᴇʟᴀʏʀsᴘᴍ <ms>

➡️ Type `{prefix}help` to go back to Main Menu.
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def cmd_menu3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_leader(update, context): return
    prefix = get_prefix()
    text = f"""
🎀 𝐌ᴇɴᴜ 3 – 𝐌ᴇᴅɪᴀ 𝐒ᴘᴀᴍ
{prefix}𝐏ɪᴄ (reply)     – 𝐏ʜᴏᴛᴏ 𝐒ᴘᴀᴍ
{prefix} (reply) – 𝐒ᴛɪᴄᴋᴇʀ 𝐒ᴘᴀᴍ
{prefix}𝐕ɴs <text>      – 𝐓ᴛs 𝐕ᴏɪᴄᴇ
{prefix}𝐒ᴛɪᴄᴋᴇʀ𝐒ᴘᴍ (reply) – 𝐒ᴛɪᴄᴋᴇʀ 𝐒ᴘᴀᴍ (fast)
{prefix}𝐆ɪғsᴘᴍ (reply)  – 𝐆ɪғ 𝐒ᴘᴀᴍ
{prefix}𝐌ᴇᴅɪᴀ𝐒ᴘᴍ (reply)– 𝐏ʜᴏᴛᴏ/𝐕ɪᴅᴇᴏ
{prefix}𝐕ᴏɪᴄᴇ𝐒ᴘᴍ (reply)– 𝐕ᴏɪᴄᴇ 𝐍ᴏᴛᴇ
{prefix}𝐒ᴛᴏᴘ𝐏ɪᴄ / 𝐒ᴛᴏᴘ𝐒ᴛɪᴄᴋᴇʀ / 𝐒ᴛᴏᴘ𝐕ɴs / 𝐃𝐒ᴛɪᴄᴋᴇʀspm / 𝐃ɢɪғ𝐒ᴘᴍ / 𝐃ᴍᴇᴅɪᴀ𝐒ᴘᴍ / 𝐃ᴠᴏɪᴄᴇ𝐒ᴘᴍ

➡️ Type `{prefix}help` to go back to Main Menu.
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def cmd_menu4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_leader(update, context): return
    prefix = get_prefix()
    text = f"""
💮 𝐌ᴇɴᴜ 4 – 𝐓ᴀʀɢᴇᴛ & 𝐑ᴇᴀᴄᴛ
{prefix}𝐓ᴀʀɢᴇᴛ (reply)  – 𝐋ᴏᴄᴋ 𝐔sᴇʀ (slide)
{prefix}𝐒ᴛᴏᴘ𝐓ᴀʀɢᴇᴛ
{prefix}𝐓ᴀʀɢᴇᴛᴄᴘ <msg> (reply) – custom slide
{prefix}𝐒ᴛᴏᴘᴛᴀʀɢᴇᴛᴄᴘ
{prefix}𝐓ᴀʀɢᴇᴛ𝐒ʟɪᴅᴇ <name> – slide on user talk
{prefix}𝐃ᴛᴀʀɢᴇᴛ𝐒ʟɪᴅᴇ
{prefix}𝐒ʟɪᴅᴇ𝐒ᴘᴀᴍ <text> (reply) – 𝐊ɪsɪ 𝐊ᴇ 𝐌sɢ 𝐏ᴇ 𝐑ᴇᴘʟʏ 𝐊ʀᴏ
{prefix}𝐃sʟɪᴅᴇ𝐒ᴘᴀᴍ
{prefix}𝐑ᴇᴘʟʏ𝐊ᴀʀᴛɪᴋ (reply) – auto‑insult
{prefix}𝐃ʀᴇᴘʟʏ𝐊ᴀʀᴛɪᴋ
{prefix}𝐑ᴇᴀᴄᴛ <emoji> (reply) – auto‑react
{prefix}𝐃ʀᴇᴀᴄᴛ
{prefix}𝐒ᴡɪᴘᴇ <name> – swipe mode
{prefix}𝐃sᴡɪᴘᴇ

➡️ Type `{prefix}help` to go back to Main Menu.
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def cmd_menu5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_leader(update, context): return
    prefix = get_prefix()
    text = f"""
💥 𝗠𝗘𝗡𝗨 5 – ADMIN & CONTROL
{prefix}𝐀ᴅᴅsᴜᴅᴏ (reply)  – add sudo (owner)
{prefix}𝐃ᴇʟsᴜᴅᴏ (reply)  – remove sudo
{prefix}𝐋ɪsᴛ𝐒ᴜᴅᴏ
{prefix}𝐀ᴅᴍɪɴ (reply)    – add global admin
{prefix}𝐑ᴀᴅᴍɪɴ (reply)   – remove global admin
{prefix}𝐀ᴅᴍɪɴ𝐋ɪsᴛ
{prefix}𝐌ᴜᴛᴇ (reply/tag)
{prefix}𝐔ɴᴍᴜᴛᴇ
{prefix}𝐌ᴜᴛᴇ𝐋ɪsᴛ
{prefix}𝐏ʀᴏᴍᴏᴛᴇ (reply/tag)
{prefix}𝐃ᴇᴍᴏᴛᴇ
{prefix}𝐏ʀᴏᴍᴏᴛᴇᴀʟʟʙᴏᴛs
{prefix}𝐏ʀᴏᴍᴏᴛᴇᴀʟʟ
{prefix}𝐋ᴇᴀᴠᴇ
{prefix}𝐒ᴘʏ on/off
{prefix}𝐂ᴍᴅ <newprefix

➡️ Type `{prefix}help` to go back to Main Menu.
"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def cmd_menu6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_leader(update, context): return
    prefix = get_prefix()
    text = f"""
♨️ 𝐌ᴇɴᴜ 6 – MISC & UTILITIES
{prefix}𝐏ɪɴɢ
{prefix}𝐔ᴘᴛɪᴍᴇ
{prefix}𝐒ᴛᴀᴛᴜs
{prefix}𝐀ᴄᴛɪᴠᴇ𝐁ᴏᴛs
{prefix}𝐌ɪssɪɴɢ𝐁ᴏᴛs
{prefix}ᴏ                  – optimize
{prefix}𝐂ʟᴇᴀɴ              – clear data (owner)
{prefix}𝐑ᴇғʀᴇsʜ            – restart (owner)
{prefix}𝐃ᴀʟʟ               – stop all tasks (owner)
{prefix}𝐃ᴀʟʟsᴘᴍ            – stop all spam
{prefix}𝐁ʀᴏᴀᴅᴄᴀsᴛ <text>   – send to all groups (sudo)
{prefix}𝐆ᴇᴛᴀʟʟᴀᴄᴛɪᴠᴇʟɪɴᴋs
{prefix}𝐆ᴇᴛʟɪɴᴋ <chat_id>
{prefix}𝐆ᴀᴍᴇᴏᴠᴇʀ <name>
{prefix}𝐒ʜᴏᴡᴅᴇʟᴀʏ
{prefix}𝐃ᴇʟᴀʏ <type> <sec>

➡️ Type `{prefix}help` to go back to Main Menu.
"""
    await update.message.reply_text(text, parse_mode='Markdown')

# ---------- MISC ----------
async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_leader(update, context): return
    await update.message.reply_text(f"🏓 Pong! `{random.randint(30,90)} ms`", parse_mode='Markdown')

async def cmd_uptime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    await update.message.reply_text(f"⏱️ Uptime: {get_uptime()}")

async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    active = []
    for d in [group_tasks, keng_tasks, spmnc_tasks, ghostnc_tasks, spm_loop_tasks, rspm_tasks, pfp_tasks, sticker_spm_tasks, gif_spm_tasks, media_spm_tasks, voice_spm_tasks, nc_tasks, tnc_tasks, rnc_tasks, spam_tasks, spam1_tasks, rspam_tasks_kartik, vns_tasks, pic_tasks, sticker_tasks_store, pfp_tasks_store]:
        active.extend(d.keys())
    active = list(set(active))
    txt = f"📊 **Bot Status**\n⏱️ Uptime: {get_uptime()}\n🤖 Bots: {len(active_bots)}\n🔥 Active Groups: {len(active)}\n"
    for cid in active:
        txt += f"• `{cid}`\n"
    await update.message.reply_text(txt, parse_mode='Markdown')

async def cmd_activebots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    names = []
    for app_data in active_bots.values():
        if app_data.get("username"):
            names.append(f"• @{app_data['username']}")
        else:
            names.append("• unknown")
    text = "🤖 **Active Bots**\n" + "\n".join(names) + f"\n\n✅ Total: {len(active_bots)}"
    await update.message.reply_text(text, parse_mode='Markdown')

async def cmd_missingbots(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    missing = []
    for app_data in active_bots.values():
        app = app_data["app"]
        try:
            await app.bot.get_chat_member(chat_id, app.bot.id)
        except:
            missing.append(app_data.get("username") or app.bot.username)
    if missing:
        await update.message.reply_text("🕵️ **Missing Bots**\n" + "\n".join(f"• @{u}" for u in missing), parse_mode='Markdown')
    else:
        await update.message.reply_text("✅ All bots are in the group.")

async def cmd_optimize(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    save_data()
    await update.message.reply_text("✨ Optimized and DB saved.")

async def cmd_clean(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can clean.")
        return
    if not await is_leader(update, context): return
    # Clear all task dicts and data
    for d in [group_tasks, keng_tasks, spmnc_tasks, ghostnc_tasks, spm_loop_tasks, rspm_tasks, pfp_tasks, sticker_spm_tasks, gif_spm_tasks, media_spm_tasks, voice_spm_tasks, nc_tasks, tnc_tasks, rnc_tasks, spam_tasks, spam1_tasks, rspam_tasks_kartik, vns_tasks, pic_tasks, sticker_tasks_store, pfp_tasks_store]:
        d.clear()
    target_users.clear()
    target_slide_data.clear()
    swipe_mode.clear()
    targetslide_targets.clear()
    react_targets.clear()
    reply_kartik_targets.clear()
    muted_users.clear()
    known_chats.clear()
    known_users.clear()
    user_names.clear()
    username_to_id.clear()
    spy_sent.clear()
    GLOBAL_ADMINS.clear()
    SUDO_USERS.clear()
    SUDO_USERS.add(OWNER_ID)  # keep owner as sudo
    nc_delays.clear()
    spm_delays.clear()
    rspm_delays.clear()
    pfp_delays.clear()
    # Reset prefix and spy mode to defaults
    global CURRENT_PREFIX, SPY_MODE
    CURRENT_PREFIX = "!"
    SPY_MODE = True
    dldir = os.path.join(os.path.dirname(__file__), 'downloads')
    if os.path.exists(dldir):
        shutil.rmtree(dldir)
    save_data()
    await update.message.reply_text("🧹 All data cleared and tasks stopped. Prefix reset to '!', Spy mode ON.")

async def cmd_refresh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can refresh.")
        return
    if not await is_leader(update, context): return
    await update.message.reply_text("🔄 Restarting bot...")
    python = sys.executable
    os.execl(python, python, *sys.argv)

async def cmd_dall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("Only owner can stop all.")
        return
    if not await is_leader(update, context): return
    for d in [group_tasks, keng_tasks, spmnc_tasks, ghostnc_tasks, spm_loop_tasks, rspm_tasks, pfp_tasks, sticker_spm_tasks, gif_spm_tasks, media_spm_tasks, voice_spm_tasks, nc_tasks, tnc_tasks, rnc_tasks, spam_tasks, spam1_tasks, rspam_tasks_kartik, vns_tasks, pic_tasks, sticker_tasks_store, pfp_tasks_store]:
        d.clear()
    target_users.clear()
    target_slide_data.clear()
    swipe_mode.clear()
    targetslide_targets.clear()
    react_targets.clear()
    reply_kartik_targets.clear()
    await update.message.reply_text("🛑 All tasks stopped globally.")

async def cmd_dallspm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    spm_loop_tasks.clear()
    rspm_tasks.clear()
    spam_tasks.clear()
    spam1_tasks.clear()
    rspam_tasks_kartik.clear()
    await update.message.reply_text("🛑 All spam loops stopped.")

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args and not update.message.reply_to_message:
        await update.message.reply_text("Usage: `!broadcast <text>` or reply to a message.")
        return
    if update.message.reply_to_message:
        target = update.message.reply_to_message
        is_copy = True
    else:
        is_copy = False
        text = " ".join(context.args)
    count = 0
    for cid in known_chats:
        if cid > 0: continue
        try:
            if is_copy:
                await context.bot.copy_message(cid, target.chat.id, target.message_id)
            else:
                await context.bot.send_message(cid, text)
            count += 1
        except:
            pass
    await update.message.reply_text(f"📣 Broadcast sent to {count}/{len(known_chats)} groups.")

async def cmd_getlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text("Usage: `!getlink <chat_id>`")
        return
    try:
        cid = int(context.args[0])
        link = await context.bot.export_chat_invite_link(cid)
        await update.message.reply_text(f"🔗 Invite link:\n{link}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def cmd_getallactivelinks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not known_chats:
        await update.message.reply_text("No known chats.")
        return
    links = []
    for cid in known_chats:
        if cid > 0: continue
        try:
            link = await context.bot.export_chat_invite_link(cid)
            links.append(f"• {cid}: {link}")
        except:
            pass
    if links:
        await update.message.reply_text("🔗 **Active Group Links**\n" + "\n".join(links), parse_mode='Markdown')
    else:
        await update.message.reply_text("No links could be generated.")

async def cmd_gameover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if not context.args:
        await update.message.reply_text(f"Usage: `{helpers.escape_markdown(get_prefix())}gameover <name>`", parse_mode='Markdown')
        return
    target = " ".join(context.args)
    current_time, current_date = get_indian_time()
    msg = f"""🪻🕊️ 𝗚𝗔𝗠𝗘 𝗢𝗩𝗘𝗥 🕊️🪻
🪼🌸 {target} 𝗣𝗜𝗟𝗟𝗘 𝗖𝗛𝗨𝗗𝗞𝗘 𝗗𝗔𝗙𝗔𝗡 🌸🪼 
𝐓𝐈𝐌𝐄 : {current_time}
𝐃𝐀𝐓𝐄 : {current_date}
𝐑ᴇɴᴏx 🥤
🪼 Pᴏᴡᴇʀᴇᴅ Bʏ Rᴇɴᴏx 🪼"""
    over_path = "over.jpg"
    if os.path.exists(over_path):
        with open(over_path, 'rb') as f:
            await update.message.reply_photo(photo=f, caption=msg)
    else:
        await update.message.reply_text(msg)

async def cmd_showdelay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    chat_id = update.effective_chat.id
    text = f"""📊 **Current Delays**
• NC: {nc_delays.get(chat_id, NC_DELAY_MS)} ms
• Spam: {spm_delays.get(chat_id, SPAM_DELAY_MS)} ms
• RSpam: {rspm_delays.get(chat_id, RSPAM_DELAY_MS)} ms
• PFP: {pfp_delays.get(chat_id, PFP_DELAY_MS)} ms
• Voice: {VOICE_DELAY_MS} ms
• Pic: {PIC_DELAY_MS} ms
• Sticker: {STICKER_DELAY_MS} ms"""
    await update.message.reply_text(text, parse_mode='Markdown')

async def cmd_delay(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_admin_or_sudo(update): return
    if not await is_leader(update, context): return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: `!delay <type> <sec>` where type = nc, spam, voice, pic, pfp, sticker", parse_mode='Markdown')
        return
    typ = context.args[0].lower()
    try:
        sec = float(context.args[1])
        if typ == "nc":
            nc_delays[update.effective_chat.id] = int(sec * 1000)
        elif typ == "spam":
            spm_delays[update.effective_chat.id] = int(sec * 1000)
        elif typ == "voice":
            global VOICE_DELAY_MS
            VOICE_DELAY_MS = int(sec * 1000)
        elif typ == "pic":
            global PIC_DELAY_MS
            PIC_DELAY_MS = int(sec * 1000)
        elif typ == "pfp":
            pfp_delays[update.effective_chat.id] = int(sec * 1000)
        elif typ == "sticker":
            global STICKER_DELAY_MS
            STICKER_DELAY_MS = int(sec * 1000)
        else:
            await update.message.reply_text("Invalid type.")
            return
        await update.message.reply_text(f"✅ {typ} delay set to {sec}s.")
    except ValueError:
        await update.message.reply_text("Invalid number.")

# ============================================================
# MESSAGE HANDLER – also handles custom prefix commands
# ============================================================
command_map = {
    "help": cmd_help,
    "menu1": cmd_menu1,
    "menu2": cmd_menu2,
    "menu3": cmd_menu3,
    "menu4": cmd_menu4,
    "menu5": cmd_menu5,
    "menu6": cmd_menu6,
    "nc": cmd_nc,
    "dnc": cmd_dnc,
    "ncemo": cmd_ncemo,
    "dncemo": cmd_dncemo,
    "kengnc": cmd_kengnc,
    "dkengnc": cmd_dkengnc,
    "spmnc": cmd_spmnc,
    "dspmnc": cmd_dspmnc,
    "ghostnc": cmd_ghostnc,
    "dghostnc": cmd_dghostnc,
    "delaync": cmd_delaync,
    "spm": cmd_spm,
    "dspm": cmd_dspm,
    "rspm": cmd_rspm,
    "drspm": cmd_drspm,
    "spam": cmd_spam_kartik,
    "stopspam": cmd_stopspam,
    "spam1": cmd_spam1,
    "stopspam1": cmd_stopspam1,
    "rspam": cmd_rspam_kartik,
    "stoprspam": cmd_stoprspam,
    "delaygcspm": cmd_delaygcspm,
    "delayrspm": cmd_delayrspm,
    "pic": cmd_pic,
    "stoppic": cmd_stoppic,
    "sticker": cmd_sticker,
    "stopsticker": cmd_stopsticker,
    "vns": cmd_vns,
    "stopvns": cmd_stopvns,
    "stickerspm": cmd_stickerspm,
    "dstickerspm": cmd_dstickerspm,
    "gifspm": cmd_gifspm,
    "dgifspm": cmd_dgifspm,
    "mediaspm": cmd_mediaspm,
    "dmediaspm": cmd_dmediaspm,
    "voicespm": cmd_voicespm,
    "dvoicespm": cmd_dvoicespm,
    "save": cmd_save,
    "del": cmd_del,
    "gsave": cmd_gsave,
    "delgpfp": cmd_delgpfp,
    "delallmedia": cmd_delallmedia,
    "gpfp": cmd_gpfp,
    "pfp": cmd_pfp,
    "dpfp": cmd_dpfp,
    "delaypfp": cmd_delaypfp,
    "target": cmd_target,
    "stoptarget": cmd_stoptarget,
    "targetcp": cmd_targetcp,
    "stoptargetcp": cmd_stoptargetcp,
    "targetslide": cmd_targetslide,
    "dtargetslide": cmd_dtargetslide,
    "slidespam": cmd_slidespam,
    "dslidespam": cmd_dslidespam,
    "replykartik": cmd_replykartik,
    "dreplykartik": cmd_dreplykartik,
    "react": cmd_react,
    "dreact": cmd_dreact,
    "swipe": cmd_swipe,
    "dswipe": cmd_dswipe,
    "addsudo": cmd_addsudo,
    "delsudo": cmd_delsudo,
    "listsudo": cmd_listsudo,
    "admin": cmd_admin,
    "radmin": cmd_radmin,
    "adminlist": cmd_adminlist,
    "mute": cmd_mute,
    "unmute": cmd_unmute,
    "mutelist": cmd_mutelist,
    "promote": cmd_promote,
    "demote": cmd_demote,
    "promoteallbots": cmd_promoteallbots,
    "promoteall": cmd_promoteall,
    "leave": cmd_leave,
    "spy": cmd_spy,
    "cmd": cmd_cmd,
    "ping": cmd_ping,
    "uptime": cmd_uptime,
    "status": cmd_status,
    "activebots": cmd_activebots,
    "missingbots": cmd_missingbots,
    "o": cmd_optimize,
    "clean": cmd_clean,
    "refresh": cmd_refresh,
    "dall": cmd_dall,
    "dallspm": cmd_dallspm,
    "broadcast": cmd_broadcast,
    "getlink": cmd_getlink,
    "getallactivelinks": cmd_getallactivelinks,
    "gameover": cmd_gameover,
    "showdelay": cmd_showdelay,
    "delay": cmd_delay,
}

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.from_user:
        return
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_name = update.effective_user.first_name or ""

    known_chats.add(chat_id)
    known_users.add(user_id)
    user_names[user_id] = user_name
    if update.message.from_user.username:
        username_to_id[update.message.from_user.username.lower()] = user_id

    # ----- Handle custom prefix commands -----
    text = update.message.text
    if text and text.startswith(CURRENT_PREFIX):
        cmd_text = text[len(CURRENT_PREFIX):].strip()
        if not cmd_text:
            return
        parts = cmd_text.split()
        cmd_name = parts[0].lower()
        args = parts[1:]
        old_args = context.args
        context.args = args
        if cmd_name in command_map:
            try:
                await command_map[cmd_name](update, context)
            except Exception as e:
                logging.error(f"Error in prefix command {cmd_name}: {e}")
            finally:
                context.args = old_args
        return

    # React
    if user_id in react_targets:
        try:
            await context.bot.set_message_reaction(
                chat_id=chat_id,
                message_id=update.message.message_id,
                reaction=[{"type": "emoji", "emoji": react_targets[user_id]}]
            )
        except:
            pass

    if not await is_leader(update, context):
        return

    # Target slide
    if chat_id in target_users and user_id in target_users[chat_id]:
        try:
            text = random.choice(SWIPE_TEXTS).replace("NAME", user_name)
            await update.message.reply_text(text)
        except:
            pass

    key = f"{chat_id}_{user_id}"
    if key in target_slide_data:
        try:
            await update.message.reply_text(target_slide_data[key])
        except:
            pass

    if user_id in targetslide_targets:
        name = targetslide_targets[user_id]
        mention = f"[{name}](tg://user?id={user_id})"
        text = random.choice(TARGET_SLIDE_TEXTS).replace("{name}", mention)
        try:
            await update.message.reply_text(text, parse_mode='Markdown')
        except:
            pass

    if user_id in reply_kartik_targets:
        try:
            await update.message.reply_text(random.choice(REPLY_KARTIK_TEXTS))
        except:
            pass

    if chat_id in swipe_mode:
        name_arg = swipe_mode[chat_id]
        template = random.choice(SWIPE_TEXTS).replace("NAME", name_arg)
        try:
            await update.message.reply_text(template)
        except:
            pass

# ============================================================
# USER LEFT HANDLER
# ============================================================
async def on_user_left(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.left_chat_member:
        return
    if not SPY_MODE:
        return
    left_user = update.message.left_chat_member
    chat_id = update.effective_chat.id
    if left_user.is_bot:
        return
    user_display = f"@{left_user.username}" if left_user.username else left_user.first_name or str(left_user.id)
    current_time, current_date = get_indian_time()
    msg = f"""╔═══════✦✧✦═══════╗
               🪼 Pᴏᴡᴇʀᴇᴅ Bʏ 𝐑ᴇɴᴏx 🪼
╚═══════✦✧✦═══════╝

👤 User: {user_display}
📅 Date: {current_date}
⏰ Time: {current_time}

━━━━━━━━━━━━━━━
💔 𝑳𝒆𝒇𝒕 𝒕𝒉𝒆 𝑮𝒓𝒐𝒖𝒑...
━━━━━━━━━━━━━━━
💬 He/She has officially left the chat...
━━━━━━━━━━━━━━━"""
    key = f"{chat_id}_{left_user.id}"
    if key in spy_sent:
        return
    spy_sent.add(key)
    if len(spy_sent) > 100:
        spy_sent.clear()
    for app_data in active_bots.values():
        app = app_data["app"]
        try:
            await app.bot.send_message(chat_id, msg)
            break
        except:
            pass

# ============================================================
# BOT INITIALIZATION
# ============================================================
async def start_bot_instance(token):
    try:
        app = ApplicationBuilder().token(token).build()
        # Register all command handlers for '/' commands
        app.add_handler(CommandHandler("help", cmd_help))
        app.add_handler(CommandHandler("menu1", cmd_menu1))
        app.add_handler(CommandHandler("menu2", cmd_menu2))
        app.add_handler(CommandHandler("menu3", cmd_menu3))
        app.add_handler(CommandHandler("menu4", cmd_menu4))
        app.add_handler(CommandHandler("menu5", cmd_menu5))
        app.add_handler(CommandHandler("menu6", cmd_menu6))
        app.add_handler(CommandHandler("nc", cmd_nc))
        app.add_handler(CommandHandler("dnc", cmd_dnc))
        app.add_handler(CommandHandler("ncemo", cmd_ncemo))
        app.add_handler(CommandHandler("dncemo", cmd_dncemo))
        app.add_handler(CommandHandler("kengnc", cmd_kengnc))
        app.add_handler(CommandHandler("dkengnc", cmd_dkengnc))
        app.add_handler(CommandHandler("spmnc", cmd_spmnc))
        app.add_handler(CommandHandler("dspmnc", cmd_dspmnc))
        app.add_handler(CommandHandler("ghostnc", cmd_ghostnc))
        app.add_handler(CommandHandler("dghostnc", cmd_dghostnc))
        app.add_handler(CommandHandler("delaync", cmd_delaync))
        app.add_handler(CommandHandler("spm", cmd_spm))
        app.add_handler(CommandHandler("dspm", cmd_dspm))
        app.add_handler(CommandHandler("rspm", cmd_rspm))
        app.add_handler(CommandHandler("drspm", cmd_drspm))
        app.add_handler(CommandHandler("spam", cmd_spam_kartik))
        app.add_handler(CommandHandler("stopspam", cmd_stopspam))
        app.add_handler(CommandHandler("spam1", cmd_spam1))
        app.add_handler(CommandHandler("stopspam1", cmd_stopspam1))
        app.add_handler(CommandHandler("rspam", cmd_rspam_kartik))
        app.add_handler(CommandHandler("stoprspam", cmd_stoprspam))
        app.add_handler(CommandHandler("delaygcspm", cmd_delaygcspm))
        app.add_handler(CommandHandler("delayrspm", cmd_delayrspm))
        app.add_handler(CommandHandler("pic", cmd_pic))
        app.add_handler(CommandHandler("stoppic", cmd_stoppic))
        app.add_handler(CommandHandler("sticker", cmd_sticker))
        app.add_handler(CommandHandler("stopsticker", cmd_stopsticker))
        app.add_handler(CommandHandler("vns", cmd_vns))
        app.add_handler(CommandHandler("stopvns", cmd_stopvns))
        app.add_handler(CommandHandler("stickerspm", cmd_stickerspm))
        app.add_handler(CommandHandler("dstickerspm", cmd_dstickerspm))
        app.add_handler(CommandHandler("gifspm", cmd_gifspm))
        app.add_handler(CommandHandler("dgifspm", cmd_dgifspm))
        app.add_handler(CommandHandler("mediaspm", cmd_mediaspm))
        app.add_handler(CommandHandler("dmediaspm", cmd_dmediaspm))
        app.add_handler(CommandHandler("voicespm", cmd_voicespm))
        app.add_handler(CommandHandler("dvoicespm", cmd_dvoicespm))
        app.add_handler(CommandHandler("save", cmd_save))
        app.add_handler(CommandHandler("del", cmd_del))
        app.add_handler(CommandHandler("gsave", cmd_gsave))
        app.add_handler(CommandHandler("delgpfp", cmd_delgpfp))
        app.add_handler(CommandHandler("delallmedia", cmd_delallmedia))
        app.add_handler(CommandHandler("gpfp", cmd_gpfp))
        app.add_handler(CommandHandler("pfp", cmd_pfp))
        app.add_handler(CommandHandler("dpfp", cmd_dpfp))
        app.add_handler(CommandHandler("delaypfp", cmd_delaypfp))
        app.add_handler(CommandHandler("target", cmd_target))
        app.add_handler(CommandHandler("stoptarget", cmd_stoptarget))
        app.add_handler(CommandHandler("targetcp", cmd_targetcp))
        app.add_handler(CommandHandler("stoptargetcp", cmd_stoptargetcp))
        app.add_handler(CommandHandler("targetslide", cmd_targetslide))
        app.add_handler(CommandHandler("dtargetslide", cmd_dtargetslide))
        app.add_handler(CommandHandler("slidespam", cmd_slidespam))
        app.add_handler(CommandHandler("dslidespam", cmd_dslidespam))
        app.add_handler(CommandHandler("replykartik", cmd_replykartik))
        app.add_handler(CommandHandler("dreplykartik", cmd_dreplykartik))
        app.add_handler(CommandHandler("react", cmd_react))
        app.add_handler(CommandHandler("dreact", cmd_dreact))
        app.add_handler(CommandHandler("swipe", cmd_swipe))
        app.add_handler(CommandHandler("dswipe", cmd_dswipe))
        app.add_handler(CommandHandler("addsudo", cmd_addsudo))
        app.add_handler(CommandHandler("delsudo", cmd_delsudo))
        app.add_handler(CommandHandler("listsudo", cmd_listsudo))
        app.add_handler(CommandHandler("admin", cmd_admin))
        app.add_handler(CommandHandler("radmin", cmd_radmin))
        app.add_handler(CommandHandler("adminlist", cmd_adminlist))
        app.add_handler(CommandHandler("mute", cmd_mute))
        app.add_handler(CommandHandler("unmute", cmd_unmute))
        app.add_handler(CommandHandler("mutelist", cmd_mutelist))
        app.add_handler(CommandHandler("promote", cmd_promote))
        app.add_handler(CommandHandler("demote", cmd_demote))
        app.add_handler(CommandHandler("promoteallbots", cmd_promoteallbots))
        app.add_handler(CommandHandler("promoteall", cmd_promoteall))
        app.add_handler(CommandHandler("leave", cmd_leave))
        app.add_handler(CommandHandler("spy", cmd_spy))
        app.add_handler(CommandHandler("cmd", cmd_cmd))
        app.add_handler(CommandHandler("ping", cmd_ping))
        app.add_handler(CommandHandler("uptime", cmd_uptime))
        app.add_handler(CommandHandler("status", cmd_status))
        app.add_handler(CommandHandler("activebots", cmd_activebots))
        app.add_handler(CommandHandler("missingbots", cmd_missingbots))
        app.add_handler(CommandHandler("o", cmd_optimize))
        app.add_handler(CommandHandler("clean", cmd_clean))
        app.add_handler(CommandHandler("refresh", cmd_refresh))
        app.add_handler(CommandHandler("dall", cmd_dall))
        app.add_handler(CommandHandler("dallspm", cmd_dallspm))
        app.add_handler(CommandHandler("broadcast", cmd_broadcast))
        app.add_handler(CommandHandler("getlink", cmd_getlink))
        app.add_handler(CommandHandler("getallactivelinks", cmd_getallactivelinks))
        app.add_handler(CommandHandler("gameover", cmd_gameover))
        app.add_handler(CommandHandler("showdelay", cmd_showdelay))
        app.add_handler(CommandHandler("delay", cmd_delay))

        # Message handlers
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages), group=1)
        app.add_handler(MessageHandler(filters.StatusUpdate.LEFT_CHAT_MEMBER, on_user_left), group=2)

        await app.initialize()
        await app.start()
        await app.updater.start_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
        me = await app.bot.get_me()
        active_bots[token] = {"app": app, "username": me.username}
        logging.info(f"✅ Bot started: @{me.username}")
        return True
    except Exception as e:
        logging.error(f"Failed to start bot: {e}")
        return False

# ============================================================
# MAIN
# ============================================================
async def main():
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    tasks = [start_bot_instance(token) for token in TOKENS if token.strip()]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success_count = sum(1 for r in results if r is True)
    logging.info(f"🚀 Started {success_count} out of {len(TOKENS)} bots. Owner: {OWNER_ID}")
    if success_count == 0:
        logging.error("No bots started. Exiting.")
        return
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        save_data()
        print("🛑 Bot stopped.")