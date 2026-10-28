import asyncio
import time
import random
import re
from datetime import datetime
from collections import defaultdict
from telegram import Update
from telegram import ChatPermissions
from telegram.error import TelegramError
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from telegram.error import RetryAfter

# ========================= MULTI BOT CONFIG =========================
BOT_TOKENS = [
"8861351383:AAEadIJDimI-bgpOnOjFN8WgUBHH4g4XuMw",
"8254769423:AAFbtlzv-PTqu1l3r24WaJBSRMerhp5fm7s",
"8914858885:AAHDpam0rLxiRnlKfhB4d_6UtIRTHYEZG9Y",
"8895979369:AAEV0fh6kXz-VBxKZaaBJWRQBSD1CTfV5LI",
"8763351235:AAEpm6LkVBKSihUCDm5-ifs3xxcOLOGW0MY",
"8821337889:AAF1g6uwtnDh-cLx_P89ol66bRLUILuKUUE",
"8657236759:AAHiKy9o6GFrf3mHTTOLkxGojQdoZsxvM8w",
"8915124714:AAEHIiHhE04RJ4ofyxbD6nLWHsMkN49mTnc",
"8829668167:AAFFoTKRy_jdoXCmhY4znQ8H9UOmXpJrtuQ",
"8987982715:AAEDvevGPM1N3OurfHZmqXcn2vBWesZNeeY",
"8706290457:AAE0MvYGktazg3tf9BrebnUjQsG1W1Zebr0",
"8925375155:AAG3G6GvE-wGziOmurqjYjuyVZEtGN-iKlg",
]

OWNER_ID = 8921566069

# ====================== SUPER FAST CONFIG ======================
DELAYS = {
    'nc': 0,      # 1ms - ULTRA FAST!
    'spam': 0,    # 1ms
    'swipe': 0,   # 1ms
    'reply': 0,   # 1ms
}

# ====================== TEXT LISTS ======================
NC_TEXTS = {
    'snc': [
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(🌀)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(🔥)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(💀)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(⚡)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(😈)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(☠️)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(🌪️)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(👑)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(💥)",
        r"{target} 𝘔𝘈𝘋𝘈𝘙𝘊𝘏𝘖𝘋 𝘖𝘠𝘌𝘌𝘌𝘌𝘌𝘌.....,🥶🤍💢᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄᳄༺═──────────────═༻☟☜♻𓂃𓂃𓂃♻᳄᳄᳄᳄᳄᳄᳄༺═────(🚨)"
    ],
    'ssnc': [
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(🌀)",
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(🔥)",
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(💀)",
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(⚡)",
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(😈)",
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(☠️)",
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(🌪️)",
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(👑)",
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(💥)",
        r"{target}﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷﷽﷽🩷〘𝐂ʜʜᴀᴋᴀ ᴄᴜᴅᴀɪ ᴋʜᴀ〙(🚨)"
    ],
    'fnc': [
        r"˚⊱━━🍁━━⊰˚{target} Cʜᴜᴘ Cʜᴜᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━🔥━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━💀━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━⚡━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━😈━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━☠️━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━🌪️━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━👑━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━💥━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅",
        r"˚⊱━━🚨━━⊰˚{target} Cʜᴜᴘ Cʜᴀᴘ Cʜᴜᴅ Rɴᴅʏᴋ\n꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅꧅"
    ],
    'cnc': [
        r"˚⊱━━😛━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━🔥━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━💀━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━⚡━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━😈━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━☠️━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━🌪️━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━👑━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━💥━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨",
        r"˚⊱━━🚨━━⊰˚{target} chote bhag rndice 𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨✨𒐫✨✨✨𒐫✨✨✨𒐫𒐫✨✨𒐫✨✨✨𒐫✨✨𒐫𒐫✨✨✨𒐫𒐫𒐫𒐫𒐫𒐫𒐫✨✨𒐫𒐫𒐫✨𒐫✨✨𒐫𒐫✨✨𒐫✨✨𒐫𒐫𒐫✨🎀✨"
    ],
    'bnc': [
        r"✨ {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧💫",
        r"🌟 {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧✨",
        r"🌀 {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧💫",
        r"🔱 {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧✨",
        r"🌈 {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧💫",
        r"⭐ {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧✨",
        r"🫧 {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧💫",
        r"🪩 {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧✨",
        r"🪷 {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧💫",
        r"🌙 {target} ke maa ke periods 🩸🩸 💧🩸💧🩸💧🩸🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧🩸🩸💧✨"
    ],
    'sgcnc': [
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(💔)",
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(❤️)",
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(🧡)",
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(💛)",
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(💚)",
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(🩶)",
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(🤎)",
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(💜)",
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(💙)",
        r"{target} tmkc AKKU mare 💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤💤-----(🩵)"
    ]
}

SPAM_TEXTS = {
    'bspam': [
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🎀」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🤍」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🎀」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🤍」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🎀」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Kᴀʟᴡɪ 「🤍」",
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「✨」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「🩷」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「✨」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「🩷」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「✨」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Bᴀᴜɴɪ 「🩷」",
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「💫」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「🩵」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「💫」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「🩵」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「💫」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Hᴀᴋʟɪ 「🩵」",
        r"✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🌙」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🖤」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🌙」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🖤」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🌙」\n✫: ̗̀➛「{target}」────────Tᴇʀɪ Mᴀ Lᴀɴɢᴅɪ 「🖤」"
    ],
    'aspam': [
        r"🤍{target}  Ki Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ 🤍",
        r" 🖤{target}  Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ  🖤",
        r" 🤎{target}  Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ  🤎",
        r" 💜{target}  Ki Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ  💜",
        r" 💙{target}  Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ  💙",
        r" 🩵{target}  Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ  🩵",
        r" 💚{target}  Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ  💚",
        r" 💛{target}  Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ  💛",
        r" 🧡{target}  Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ  🧡",
        r" ❤️{target}  Kɪ Mᴀ Kɪ Sᴀᴛʀᴀɴɢɪ Cʜᴜᴛ  ❤️"
    ],
    'sspam': [
        r"{target}  CVR KR MC GAREEB 👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞 {target}  CVR KR MC GAREEB{target}  CVR KR MC GAREEB 👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞 {target}  CVR KR MC GAREEB {target}  CVR KR MC GAREEB 👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞👞 {target}  CVR KR MC GAREEB"
    ],
    'fspam': [
        r"💛 𓂃𓈒 {target} ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝙎𝘼𝙍𝙀 𝙆𝙃𝙀𝙏 𝙀𝙆 𝙎𝘼𝙏𝙃 𝙆𝙃𝙊𝘿 𝘿𝙐𝙉𝙂𝘼 𝙃𝘼𝙏𝙀𝙍 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝘿𝙄𝙆𝙃𝙏𝙀 𝙃𝙄 𝘾𝙃𝙊𝘿 𝘿𝙐𝙉𝙂𝘼___/>🤣𓂃𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ 𝙉𝘼 𝙂𝙊𝙍𝙊 𝙆𝙄 𝙉𝘼 𝙆𝘼𝙇𝙊 𝙆𝙄 𝙔𝙀 𝘿𝙐𝙉𝙄𝙔𝘼 𝙃 𝙏𝙀𝙍𝙀 𝘽𝘼𝘼𝙋 𝙅𝘼𝙎𝙀 𝘽𝙃OSDI𝙒𝘼𝙇𝙊 𝙆𝙄___/𒀸𓆩᭄ᬼ♥️𓆪💛 𓂃??𓂃𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ 𝗠𝗘𝗡𝗘 𝗦𝗨𝗡𝗔 𝗞𝗜 𝗧𝗨𝗠𝗛𝗔𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗝𝗔𝗪𝗔𝗡 𝗛𝗢 𝗚𝗬𝗜 𝗛𝗔𝗜 𝗥𝗢𝗝 𝗕𝗨𝗥 𝗠𝗘 𝗨𝗚𝗟𝗜 𝗞𝗥𝗧𝗘 𝗣𝗔𝗞𝗗𝗜 𝗝𝗔𝗧𝗜 𝗛𝗔𝗜 𓆩᭄ᬼ♥️𓆪💛 𓂃𓈒𓂃𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ 𝗛𝗔𝗧𝗘𝗥___/𒀸    𝗞𝗬𝗔 𝗥𝗘 𝗦𝗣𝗔𝗠𝗠𝗘𝗥 𝗕𝗔𝗡𝗘𝗚𝗔 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗘𝗡 𝗞𝗜 𝗦𝗘𝗘𝗟 𝗧𝗛𝗢𝗗𝗨 𝗠𝗔𝗗𝗥𝗖𝗛𝗢𝗗  _____/𒀸💙 𓂃𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ BHAI MANE SUNA H TERA BAAP HIZRA H M AJAU KYA ___/𒀸𓆩᭄ᬼ♥️𓆪💛𓂃𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤKYA RE TATTE MYZHE SIKHAYEGA FYTER AB SYARI SUN TU ___/𒀸𓆩᭄ᬼ♥️𓆪𓂃𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝙈 𝙆𝙃𝘼𝙐𝙉𝙂𝘼 𝘾𝙃𝙄𝙉𝙀𝙀𝙕 𝙁𝙊𝗢𝘿 𝙏𝙀𝙍𝙄 𝘽𝘼𝙃𝙄𝙉 𝙆I 𝙆𝘼𝙇𝙄 𝘾𝙃𝙐𝙏𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝙈 𝘽𝘼𝙉𝘼𝙐𝙉𝙂𝘼 𝙈𝘼𝙂𝙂𝙄𝙀 𝙏𝙀𝙍𝙄 𝘽𝘼𝙃𝙄𝙉 𝘾𝙃𝙐𝙏 𝙆𝙀 𝘽𝙃𝘼𝙂𝙄𓂃___/𒀸𓆩᭄ᬼ♥️𓆪💛𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝙈 𝙆𝙃𝘼𝙐𝙉𝙂𝘼 𝙆𝙃𝘼𝙉𝘼 𝙏𝙀𝙍𝙄 𝘽𝘼HIN 𝙆I 𝙎𝙀𝙀𝗟 𝗧𝗢𝗗𝙐𝗡𝗚𝘼 𝙒𝙄𝗧𝗛 𝙋𝘼𝙉𝘼𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝙋𝙃𝙐𝙇 𝙃 𝙂𝙐𝙇𝘼𝘽 𝙆𝘼 𝙎𝙐𝙆𝙃𝙉𝙀 𝙉𝘼𝙃𝙄 𝘿𝙐𝙉𝙂𝘼 𝘿𝙀𝙆𝙃 𝙆𝙔𝘼 𝙍𝘼𝙃𝘼 𝙃 𝙏𝗘𝙍𝗜 𝙆𝙃𝘼𝘿𝙀 𝙆𝙃𝘼𝘿𝙀 𝙇𝙐𝙉𝙂𝘼𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝙎𝙐𝙉𝘼 H 𝙈𝙀𝙍𝙀 𝙑𝙃𝘼I 𝙉𝙀 𝙎𝘼𝙍𝙀 𝙆𝙃𝙀𝙏 𝙆𝙃𝙊𝘿 𝘿𝙄𝙀 𝙏𝙀𝙍𝙄 𝙈𝘼𝘼 𝙋𝘼𝙉I 𝘿𝙀𝙉𝙀 𝘼𝙔I 𝙈𝙀𝙍𝙄 𝘽𝙃𝘼I 𝙉𝙀 𝓧𝙃𝘖𝘋 𝘿𝙄𝙔𝙀𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝗠 𝗞𝗛𝗔𝗡𝗘 𝗠 𝗞𝗛𝗔𝗧𝗔 𝗛𝗨 𝗙𝗢𝗢𝗗 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗜 𝗩𝗜𝗥𝗔𝗟 𝗞𝗔𝗥𝗨𝗡𝗚𝗔 𝗡𝗨𝗗𝗘𓂃___/𒀸𓆩᭄ᬼ♥️𓆪💛𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝗠 𝗞𝗛𝗔𝗨𝗡𝗚𝗔 4 𝗕𝗛𝗨𝗧𝗧𝗘 𝗧𝗘𝗥𝗘 𝗕𝗔𝗔𝗣 𝗞𝗘 𝗣𝗔𝗦 𝗛 8 𝗧𝗔𝗧𝗧𝗘𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝗠𝗔 𝗞𝗛𝗔𝗨𝗡𝗚𝗔 𝗞𝗛𝗘𝗘𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗠 𝗘𝗞 𝗦𝗔𝗧𝗛 𝗧𝗨 𝗢𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗟𝗔𝗡𝗗 𝗗𝗨𝗡𝗚𝗔 𝗖𝗛𝗘𝗘𝗥___/𒀸𓆩᭄ᬼ♥️𓆪💛𓂃𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝓣𝓔𝓡𝓘 𝓜𝓐𝓐 𝓚𝓞 𝓚𝓐𝓡 𝓓𝓤𝓝𝓖𝓐 𝓑𝓐𝓝𝗗 𝓣𝓔𝓡𝓘 𝓜𝓐𝓐 𝓚𝓔 𝓟𝓐𝓢 𝓗 𝓚𝓐𝓛𝓐 𝓛𝓐𝓝𝓓𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝓜𝓐 𝓑𝓞𝓛𝓤𝓝𝓖𝓐 𝓗𝓤𝓛𝓚 𝓣𝓔𝓡𝓘 𝓑𝓐𝓗𝓘𝓝 𝓚𝓐𝓡𝓣𝓘 𝓗 𝓑𝓤𝓛𝓚𓂃𓈒ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗖𝗛𝗨𝗧 𝗛 𝗧𝗜𝗚𝗛𝗧 𝗕𝗔𝗧𝗔 𝗢𝗥 𝗞𝗔𝗥 𝗗𝗨𝗡𝗚𝗔 𝗕𝗥𝗜𝗚𝗛𝗧𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝗠𝗘𝗥𝗘 𝗗𝗢𝗦𝗧 𝗞𝗢 𝗞𝗔𝗛𝗧𝗘 𝗛 𝗣𝗢𝗟𝗔𝗥 𝗕𝗘𝗔𝗥 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗔 𝗗𝗢𝗪𝗡𝗟𝗢𝗔𝗗 𝗞𝗔𝗥𝗨 𝗦𝗢𝗙𝗧𝗪𝗔𝗥𝗘𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗕𝗛𝗔𝗚𝗧𝗘 𝗛𝗨𝗜 𝗖𝗛𝗨𝗗𝗜 𝗔𝗕 𝗧𝗘𝗥𝗜 𝗕𝗔𝗛𝗜𝗡 𝗞𝗜 𝗙𝗔𝗗𝗨𝗡𝗚𝗔 𝗙𝗨𝗗𝗜𝗜𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛ㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤㅤ     ㅤㅤㅤ ㅤㅤ𝗧𝗨 𝗣𝗜𝗬𝗘𝗚 𝗣𝗔𝗡𝗜 𝗜𝗡 𝗕𝗢𝗪𝗟 𝗧𝗘𝗥𝗜 𝗠𝗔𝗔 𝗞𝗜 𝗦𝗘𝗘𝗟 𝗧𝗢𝗗𝗘𝗚𝗔 𝗥𝗔𝗛𝗨𝗟𓂃𓈒___/𒀸𓆩᭄ᬼ♥️𓆪💛ㅤ{target}  CVR KR MC GAREEB {target}"
    ],
    'gspam': [
        r"TERYYYYYYYYYYYY AMMMMIIII KIIIII BURRRR FADUUGAAAA MADHARXHODDDDD👀👀👀 RANDIKEEEEE PILLEEEE  RANDDDD TERYYYY BHENNNN KIIII SEALLLL TODUGAAAAA SAREYAMMMMM CHAURAHEEEEE PEEEEE🤣🤣🤣🤣🤣BHENNNN KEEEE TAKEEEE MADHARXHODDDDDDD🖕🖕TERYYYYY MAAAA KEEEE BHOSDEEEE MEEEE KHADAAA HATHIIII KAAAA LUNDDDD DALUGAAAA BHENNNN KEEE TAKKEEEEE MADHARXHODDDDD👀👀👀🤣🤣🤣 BHSDKKK BAAAPP KOOO FEELLL LEEE BHAGGG MATTTT MADHARXHODDDD BHSDKKKK TERYYY MAAA XHODNIIII HAIIII MEREEE KOOO AJAAA RANDIKEEEE OLADDD🤣🤣👅👅🙈🖕🩸\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n           𓆩𝐀ᴋᴋᴜ𓆪  PAPA\n     ⠀⣴⣾⣿⣿⣶\n⠀⠀⢸⣿⣿⣿⣿⣿⣿\n⠀⠀⠈⢿⣿⣿⣿⣿\\\n⠀⠀⠀⠀⠈\⣩⣀\\n⠀⠀⠀⠀\\⣿⣿⣿\\n⠀⠀⠀⠀⠀\\⠀\\⣿⣿⣿⣿⣿\\n⠀⢀\\⣿⣿⣿⣿⣿⣿\\. {target} TERY MAA\n⢠\\⣿⣿⠉⣿⣿⣿⣿⣿\\\⠀\\⣤⣤⣀\n⠀⠙⣿⣿\\⣿⣿⣿⣿⣿\\⢠⣿⣿⣿⣿⣿\\n⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿\\⠸⣿⣿⣿⣿⣿\\n⠀⠀⠀⠀\\⠿⢿⣿⣿⣿⣿\\⠻⠿⠿⠛⠁\n⠀⠀⠀⠀⠀⠀⠀⡟\\⢿⠀⠀\\⣶⣶\\\n⠀⠀⠀⠀⠀⠀⠀\\⣿\\\\⣿⣿⣿⣿\\\n⠀⠀⠀⠀⠀⠀⠀⣿⣿\\\\⣿\\⣿⣿⣿⣿⣿\\\n⠀⠀⠀⠀⠀⠀⠀⣿⣿⣿\\⠀⠀\\⠿\\⣿⣿⣿⣿\\\n⠀⠀⠀⠀⠀⠀\\⣿⣿⣿\\⠀⠀⠀⠀⠀\\⣿⣿⣿⣿⣿\\n⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⠀⠀⠀⠀⠀⠀\\⣿⣿⣿⣿\\n⠀⠀⠀⠀⠀⠀⢸⣿⣿\\⠀⠀⠀\\⣿⣿⣿⣿\\\⣀⣀\n\n\nFEEL KARRRRRR BAAAPPPPPP KOOOOO MADRXHODDDDDDD :)(●*∩_∩*●)"
    ],
    'rspam': [
        r"{target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴ🇩ʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙 {target}𝐑ᴀɴᴅʏ 𝐊ᴀ 𝐁ᴀᴄʜᴀ ˏˋ°•*⁀➷ 𝑳𝑼𝑵𝑫 𝑪𝑯𝑶𝑶𝑺 𝐀ᴋᴋᴜ 𝑲𝑨 कुतिया के 🥂🌙"
    ]
}

SWIPE_TEXTS = {
    'aswipe': [
        r"𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ Akku  𝐒ᴇ - 🦢💘",
        r"𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ Akku  ! 🌙",
        r"acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥",
        r"chudke bhaga kaise 😂💥🤣🤘🏻",
        r"ne toh Akku  ka lun muh me lelia 😂🙏🏻😂🙏🏻",
        r"try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
        r"mkl lun te vaj 😂✊🏻💦",
        r"𝗧ᴍᴋ𝗕 pe Akku  ka hamla 😂⚔🔥💥",
        r"𝐂ʜʟ 𝐇ᴀʀᴍzIndex 𝐊ᴇ लड़के 💛🤍🩵",
        r"oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
        r"chl rndyce chud ke dikha 😂💥🤣🔥",
        r"𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
        r"tera baap bass Akku  hai 😂🎀",
        r" try maa hagte hue paad mari -#😹🔥🥀",
        r"  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ Akku  𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜",
        r"𝐊ʏᴀ 𝐑ᴇ 𝐑ᴀɴᴅɪᴋᴇ 𝐂ᴏᴏʟ 𝐁ᴀɴᴇɢᴀ 𝐓ᴜ 𝐂ʜᴀʟ 𝐀ʙ 𝐂ʜᴜᴅ 𝐀ᴘɴᴇ 𝐁ᴀᴀᴘ Akku  𝐒ᴇ - 🦢💘",
        r"𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ 𝐘ᴀᴀʀ - 𝐉ᴀɪ Akku  ! 🌙",
        r"acha beta 😂🔥👊🏻 ? coi na me toh HATER codunga 😹💔🔥😆👊🏻💥"
    ],
    'fswipe': [
        r"chudke bhaga kaise 😂💥🤣🤘🏻",
        r"ne toh Akku  ka lun muh me lelia 😂🙏🏻😂🙏🏻",
        r"try maa सूर्य☀ nikalte hi pel du 😹🔥💔",
        r"mkl lun te vaj 😂✊🏻💦",
        r"𝗧ᴍᴋ𝗕 pe Akku  ka hamla 😂⚔🔥💥",
        r"𝐂ʜʟ 𝐇ᴀʀᴍᴢᴀᴅ𝐈 𝐊ᴇ लड़के 💛🤍🩵",
        r"oi 𝐓ᴇʀɪ 𝐌‌ᴀᴀ गुलाम ₰🖤",
        r"chl rndyce chud ke dikha 😂💥🤣🔥",
        r"𝐊ɪ 𝐌ᴀᴀ 𝐌ᴀʀʀ 𝐆ᴀʏɪ naacho 💃🏻💃🏻🕺🏻🎶😂😆💞🔥 !",
        r"tera baap bass Akku  hai 😂🎀",
        r" try maa hagte hue paad mari -#😹🔥🥀",
        r"  𝐓ᴇʀɪ 𝐌ᴜᴍᴍʏ 𝐂ʜᴏᴅ 𝐃ɪ Akku  𝐍ᴇ 𝐁ᴡᴀʜᴀʜᴀʜᴀ ⚜"
    ],
    'rrswipe': [
        r"𓂃˖˳·˖ ִֶָ ⋆❤️͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚❤️ ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆🧡͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🧡 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💛͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💛 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💚͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💚 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💙͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💙 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💜͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💜 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆🖤͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🖤 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆🤍͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🤍 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆🤎͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚🤎 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💖͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💖 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💗͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💗 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💓͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💓 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💞͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝑪𝑯𝑶𝑶𝑺 -/- ⋆˚💞 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💕͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💕 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💘͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💘 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💝͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💝 ݁˖⭑.ᐟ",
        r"𓂃˖˳·˖ ִֶָ ⋆💟͙⋆ ִֶָ˖·˳˖𓂃 ִֶָ⁀➴༯ sꪶꪖꪜꫀ ִֶָ. ..𓂃 ࣪ ִֶָ🌈་༘࿐ 𝗟𝗡𝗗 𝗖𝗛𝗢𝗢𝗦 -/- ⋆˚💟 ݁˖⭑.ᐟ"
    ],
    'cswipe': [
        r" 𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸 ⇝ ༼ 🍓༽ ",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍈༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫜༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍒༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍐༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥥༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍎༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫛༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥔༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍅༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥬༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🧅༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🌶️༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫑༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫚༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍉༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍏༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫘༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍑༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥝༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🌰༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍊༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥑༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥜༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍐༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫒༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍞༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥭༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥦༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫓༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍍༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥒༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥯༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍌༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🫐༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🧇༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍋༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍇༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍳༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🌽༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍆༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🥩༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍋‍🟩༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍠༽",
        r"𝐾𝐵𝐴𝐷𝐼 𝑊𝐴𝐿𝐸  ⇝ ༼ 🍟༽"
    ]
}

REPLY_TEXTS = {
    'rreply': [
        r"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद Akku  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
        r"नहीं नहीं तेरी मां को 𝐒ɪʀғ Akku  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        r"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        r"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
        r"सोच तेरी बहन को Akku  बाप का गुलाम चोद रहा 😎🔥",
        r"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
        r"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन Akku  /\~ 👑 बाप से सही chudi 🥵🔥"
    ],
    'breply': [
        r"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ Akku  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
        r"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐",
        r"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद Akku  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
        r"नहीं नहीं तेरी मां को 𝐒ɪʀғ Akku  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        r"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        r"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
        r"सोच तेरी बहन को Akku  बाप का गुलाम चोद रहा 😎🔥",
        r"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
        r"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन Akku  /\~ 👑 बाप से सही chudi 🥵🔥",
        r"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ Akku  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
        r"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐",
        r"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद Akku  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥"
    ],
    'creply': [
        r"नहीं नहीं तेरी मां को 𝐒ɪʀғ Akku  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        r"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        r"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥",
        r"सोच तेरी बहन को Akku  बाप का गुलाम चोद रहा 😎🔥",
        r"Hello hello?? Oxygen aarahi है? रण्डी पुत्र 🧘🏻",
        r"Shut up रंडीके वरना दुनिया यही बोलेगी तेरी बहन Akku  /\~ 👑 बाप से सही chudi 🥵🔥",
        r"ᴛᴜ ᴏʀ ᴛᴇʀɪ ᴍᴀᴀ ᴅᴏɴᴏ Akku  बाप के ʟɴᴅ sᴇ ᴋᴀʙʜɪ ᴜᴛʜ ɴʜɪ ᴘᴀʏᴇ 😂🔥",
        r"🇮🇳𝐵𝐻𝐴𝑅𝐴𝑇 𝐻𝐴𝑀𝐴𝑅𝐴 𝐷𝐸𝑆𝐻 𝐻 𝐴𝑈𝑅 𝑈𝑆 𝐷𝐸𝑆𝐻 𝑀𝐸 तेरी मां घर घर जाके MOAN करती है ! 🛐",
        r"⋆｡ﾟ☁︎｡𝐂ʏᴜ 𝐑ᴇ मदरचोद Akku  बाप के सामने 𝐅ʏᴛᴇʀ 𝐁ᴀɴᴇɢᴀ ⋆𓂃 ོ☼𓂃 😂🔥",
        r"नहीं नहीं तेरी मां को 𝐒ɪʀғ Akku  बाप चोद सकता है ִֶָ𓂃 ࣪ ִֶָ👑་༘࿐ sᴀᴍᴊʜᴀ ʀᴀɴᴅɪᴋᴇ ???",
        r"तेरी मां का 𝐒ᴛʏʟɪsʜ भोसड़ा 😱",
        r"𝑻𝒆𝒓𝒚 𝒎𝒂𝒂 𝒓𝒂𝒏𝒅𝒂𝒍 𝒉 𝒃𝒂𝒔 𝒃𝒂𝒂𝒕 𝒌𝒉𝒂𝒕𝒂𝒎 😡🔥"
    ]
}

# ====================== STATE ======================
active_tasks = {}
sudo_users = {OWNER_ID}
sudo_list = [OWNER_ID]
start_time = time.time()

def is_sudo(user_id: int) -> bool:
    return user_id in sudo_users or user_id == OWNER_ID

async def replace_target(text: str, target: str = "") -> str:
    if target:
        text = text.replace("{target}", target).replace("<target>", target).replace("<TARGET>", target.upper())
    return text

# ====================== SUPER FAST LOOPS ======================
async def nc_loop(context, bot_id, chat_id, loop_type, target):
    key = f"{bot_id}_{chat_id}_{loop_type}"
    texts = NC_TEXTS.get(loop_type, NC_TEXTS['snc'])
    i = 0
    
    while key in active_tasks:
        try:
            title = await replace_target(texts[i % len(texts)], target)
            await context.bot.set_chat_title(chat_id, title)
            i += 1
            await asyncio.sleep(DELAYS['nc'])
        except Exception as e:
            if "FloodWait" in str(e):
                wait_match = re.search(r'retry after (\d+)', str(e), re.IGNORECASE)
                wait_time = int(wait_match.group(1)) if wait_match else 1
                await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(0.1)

async def spam_loop(context, bot_id, chat_id, loop_type, target):
    key = f"{bot_id}_{chat_id}_{loop_type}"
    texts = SPAM_TEXTS.get(loop_type, SPAM_TEXTS['bspam'])
    i = 0
    
    while key in active_tasks:
        try:
            msg = await replace_target(texts[i % len(texts)], target)
            await context.bot.send_message(chat_id, msg)
            i += 1
            await asyncio.sleep(DELAYS['spam'])
        except Exception as e:
            if "FloodWait" in str(e):
                wait_match = re.search(r'retry after (\d+)', str(e), re.IGNORECASE)
                wait_time = int(wait_match.group(1)) if wait_match else 1
                await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(0.1)

async def swipe_loop(context, bot_id, chat_id, reply_to, loop_type, target, is_reply=False):
    key = f"{bot_id}_{chat_id}_{reply_to}_{loop_type}"
    texts = SWIPE_TEXTS.get(loop_type) if not is_reply else REPLY_TEXTS.get(loop_type)
    if not texts:
        return
    i = 0
    
    while key in active_tasks:
        try:
            text = await replace_target(texts[i % len(texts)], target)
            await context.bot.send_message(chat_id, text, reply_to_message_id=reply_to)
            i += 1
            delay = DELAYS['swipe' if not is_reply else 'reply']
            await asyncio.sleep(delay)
        except Exception as e:
            if "FloodWait" in str(e):
                wait_match = re.search(r'retry after (\d+)', str(e), re.IGNORECASE)
                wait_time = int(wait_match.group(1)) if wait_match else 1
                await asyncio.sleep(wait_time)
            else:
                await asyncio.sleep(0.1)

# ====================== GAME OVER ======================
async def gameover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_sudo(user.id):
        await update.message.reply_text("Akku se Sudo leke aa pehle rndice Bache 🌀🌀")
        return

    text = update.message.text or ""
    parts = text.split(" ", 1)
    target = parts[1].strip() if len(parts) > 1 else "Bhai"

    now = datetime.now()

    game_msg = f"""
==========================
  GAME OVER BY AKKU GAWD 🌀 
==========================
{target} Teri cudai done by akku 
Date :- {now.strftime("%d %b %Y")}
Time :- {now.strftime("%H:%M:%S")}
Day :- {now.strftime("%A")}
==========================
AB NO BHAW ROTA REH RNDICE 
==========================
""".strip()

    await update.message.reply_text(game_msg)

# ====================== PIN COMMANDS ======================
async def pin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐀ᴋᴋᴜ papa se Sudo Maang pehle 🌀🌀")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a message to pin it!\nExample: Reply to a message and type !pin")
        return
    
    try:
        await update.message.reply_to_message.pin()
        await update.message.reply_text("📌 Message pinned successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\nMake sure bot has admin rights!")

async def unpin_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐀ᴋᴋᴜ papa se Sudo Maang pehle 🌀🌀")
        return
    
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ Reply to a message to unpin it!\nExample: Reply to a message and type !unpin")
        return
    
    try:
        await update.message.reply_to_message.unpin()
        await update.message.reply_text("📌 Message unpinned successfully!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\nMake sure bot has admin rights!")

async def unpin_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐀ᴋᴋᴜ papa se Sudo Maang pehle 🌀🌀")
        return
    
    chat = update.effective_chat
    
    try:
        await chat.unpin_all_messages()
        await update.message.reply_text("📌 All pinned messages removed!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}\nMake sure bot has admin rights!")

# ====================== MUTE/UNMUTE COMMANDS ======================
async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐀ᴋᴋᴜ papa se Sudo Maang pehle 🌀🌀")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to user message.")
        return

    chat_id = update.effective_chat.id
    user_id = update.message.reply_to_message.from_user.id

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=False,
                can_send_media_messages=False,
                can_send_polls=False,
                can_send_other_messages=False,
                can_add_web_page_previews=False,
                can_change_info=False,
                can_invite_users=False,
                can_pin_messages=False
            )
        )
        await update.message.reply_text("✅ MUTED")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐀ᴋᴋᴜ papa se Sudo Maang pehle 🌀🌀")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to user message.")
        return

    chat_id = update.effective_chat.id
    user_id = update.message.reply_to_message.from_user.id

    try:
        await context.bot.restrict_chat_member(
            chat_id=chat_id,
            user_id=user_id,
            permissions=ChatPermissions(
                can_send_messages=True,
                can_send_media_messages=True,
                can_send_polls=True,
                can_send_other_messages=True,
                can_add_web_page_previews=True,
                can_change_info=False,
                can_invite_users=True,
                can_pin_messages=False
            )
        )
        await update.message.reply_text("✅ UNMUTED")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")

async def gcmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("No access")
        return

    chat_id = update.effective_chat.id
    perms = ChatPermissions(
        can_send_messages=False,
        can_send_polls=False,
        can_send_other_messages=False,
        can_add_web_page_previews=False,
        can_change_info=False,
        can_invite_users=False,
        can_pin_messages=False
    )
    await context.bot.set_chat_permissions(chat_id=chat_id, permissions=perms)
    await update.message.reply_text("🔇 GC MUTED")

async def gcunmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("No access")
        return

    chat_id = update.effective_chat.id
    perms = ChatPermissions(
        can_send_messages=True,
        can_send_polls=True,
        can_send_other_messages=True,
        can_add_web_page_previews=True,
        can_change_info=False,
        can_invite_users=True,
        can_pin_messages=False
    )
    await context.bot.set_chat_permissions(chat_id=chat_id, permissions=perms)
    await update.message.reply_text("🔊 GC UNMUTED")

# ====================== OTHER COMMANDS ======================
async def stopall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐀ᴋᴋᴜ papa se Sudo Maang pehle 🌀🌀")
        return
    chat_id = update.effective_chat.id
    removed = 0
    for key in list(active_tasks.keys()):
        if str(chat_id) in key:
            task = active_tasks.pop(key, None)
            if task and not task.done():
                task.cancel()
                removed += 1
    await update.message.reply_text(f"✅ All Tasks Stopped! ({removed} loops)")

async def add_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("Only Owner can give sudo!")

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            user_id = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("❌ Invalid ID!")
    else:
        return await update.message.reply_text("Usage:\n• !sudo <user_id>\n• Reply to a user's message with !sudo")

    if user_id in sudo_users:
        return await update.message.reply_text("Already sudo!")

    sudo_users.add(user_id)
    if user_id not in sudo_list:
        sudo_list.append(user_id)

    await update.message.reply_text(f"✅ Sudo added: `{user_id}`", parse_mode="Markdown")

async def remove_sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if update.message.reply_to_message:
        user_id = update.message.reply_to_message.from_user.id
    elif context.args:
        try:
            user_id = int(context.args[0])
        except ValueError:
            return await update.message.reply_text("❌ Invalid ID!")
    else:
        return await update.message.reply_text("Usage:\n• !dsudo <user_id>\n• Reply to a sudo user's message with !dsudo")

    sudo_users.discard(user_id)
    if user_id in sudo_list:
        sudo_list.remove(user_id)

    await update.message.reply_text(f"❌ Sudo removed: `{user_id}`", parse_mode="Markdown")

async def ban_unban(update: Update, context: ContextTypes.DEFAULT_TYPE, ban_action: bool = True):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐀ᴋᴋᴜ papa se Sudo Maang pehle 🌀🌀")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message!")
        return
    user = update.message.reply_to_message.from_user
    chat = update.effective_chat
    try:
        if ban_action:
            await chat.ban_member(user.id)
            await update.message.reply_text(f"✅ {user.first_name} BANNED!")
        else:
            await chat.unban_member(user.id)
            await update.message.reply_text(f"✅ {user.first_name} UNBANNED!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ban_unban(update, context, True)

async def unban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await ban_unban(update, context, False)

async def delmsg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        await update.message.reply_text("𝐀ᴋᴋᴜ papa se Sudo Maang pehle 🌀🌀")
        return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message!")
        return
    try:
        await update.message.reply_to_message.delete()
        await update.message.reply_text("✅ Message deleted!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def sudolist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    if sudo_users:
        await update.message.reply_text(f"**Sudo List** ({len(sudo_users)})\n" + "\n".join(map(str, sudo_users)))
    else:
        await update.message.reply_text("No sudo users.")

async def adminlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    try:
        admins = await update.effective_chat.get_administrators()
        admin_names = [f"{admin.user.first_name} (ID: {admin.user.id})" for admin in admins]
        await update.message.reply_text(f"**Admin List**\n" + "\n".join(admin_names))
    except Exception as e:
        await update.message.reply_text(f"Cannot fetch: {str(e)}")

async def banlist_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    await update.message.reply_text("**Ban List** - Check manually.")

async def refreshsudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    global sudo_users, sudo_list
    sudo_users = {OWNER_ID}
    sudo_list = [OWNER_ID]
    await update.message.reply_text("✅ Sudo refreshed! Only Owner is sudo now.")

async def refresh_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id):
        return
    global active_tasks, sudo_users, sudo_list, start_time
    for key, task in list(active_tasks.items()):
        if not task.done():
            task.cancel()
    active_tasks.clear()
    sudo_users = {OWNER_ID}
    sudo_list = [OWNER_ID]
    start_time = time.time()
    await update.message.reply_text("✅ Bot refreshed! All tasks stopped.")

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    nc = sum(1 for k in active_tasks if "nc_" in k)
    spam = sum(1 for k in active_tasks if "spam_" in k)
    swipe = sum(1 for k in active_tasks if "swipe_" in k)
    reply = sum(1 for k in active_tasks if any(x in k for x in ['rreply', 'breply', 'creply']))
    
    await update.message.reply_text(
        f"**📊 BOT STATUS**\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🔹 NC: {nc}\n"
        f"🔹 Spam: {spam}\n"
        f"🔹 Swipe: {swipe}\n"
        f"🔹 Reply: {reply}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📌 Total: {len(active_tasks)}"
    )

# ====================== MENU ======================
MENU_TEXT = """
<<<<<<<<<<<<<>>>>>>>>>>>>>
       📃 NC CONTROLS 📃
<<<<<<<<<<<<<>>>>>>>>>>>>> 
 
         !snc <target> / !dnc
         !ssnc <target> / !dssnc
         !fnc <target> / !dfnc 
         !cnc <target> / !dcnc
         !bnc <target> / !dbnc
         !sgcnc <target> / !dgcnc 
         
              !dallnc
      
<<<<<<<<<<<<<>>>>>>>>>>>>>
     🔥  SPAM CONTROLS 🔥     
<<<<<<<<<<<<<>>>>>>>>>>>>>
         
         !bspam <target> / !dbspam
         !aspam <target> / !daspam
         !sspam <target> / !dsspam
         !fspam <target> / !dfspam 
         !gspam <target> / !dgspam
         !rspam <target> / !drspam
       
             !dallspam
  
<<<<<<<<<<<<<>>>>>>>>>>>>>
      🌀 SWIPE CONTROLS 🌀
<<<<<<<<<<<<<>>>>>>>>>>>>>

         !aswipe / !daswipe
         !fswipe / !dfswipe 
         !rrswipe / !drrswipe
         !cswipe / !dcswipe 
        
             !dallswipe    
    
<<<<<<<<<<<<<>>>>>>>>>>>>>
     ✨ REPLY CONTROLS ✨
<<<<<<<<<<<<<>>>>>>>>>>>>>
    
         !rreply / !drreply
         !breply / !dbreply
         !creply / !dcreply
         
             !dallreply
   
<<<<<<<<<<<<<>>>>>>>>>>>>> 
     ⏩ DELAY CONTROLS ⏩
<<<<<<<<<<<<<>>>>>>>>>>>>>
         
         !setdelaync <sec>
         !setdelayspam <sec>
         !setdelayswipe <sec> 
         !setdelayreply <sec>
         
<<<<<<<<<<<<<>>>>>>>>>>>>>
          🛠️ TOOLS 🛠️
<<<<<<<<<<<<<>>>>>>>>>>>>>
    
          !ping  
          !status
          !uptime
          !refresh 
          !pin
          !unpin
          !revpin
               
<<<<<<<<<<<<<>>>>>>>>>>>>>
     🛡️ ADMINISTRATOR 🛡️
<<<<<<<<<<<<<>>>>>>>>>>>>>
         
          !ban / !unban
          !sudo / !dsudo
          !delmsg
          !mute / !unmute
          !gcmute / !gcunmute
          !sudolist
          !refreshsudo
          !adminlist
          !banlist  
          !gameover <target>
          !stopall
<<<<<<<<<<<<<>>>>>>>>>>>>>
      🌀 MADE BY AKKU GAWD🌀
<<<<<<<<<<<<<>>>>>>>>>>>>>
"""

# ====================== MAIN HANDLER ======================
async def make_handler(bot_id: str):
    async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return
        
        text = update.message.text
        if not text.startswith('!'):
            return

        msg = update.message
        cmd_parts = text.lower().strip().split()
        cmd = cmd_parts[0][1:] if cmd_parts else ""
        args = cmd_parts[1:] if len(cmd_parts) > 1 else []

        if cmd == "menu":
            return await msg.reply_text(MENU_TEXT)
        
        if cmd == "ping":
            start = time.time()
            await msg.reply_text("🏓 Pong!")
            end = time.time()
            await msg.reply_text(f"⚡ Response: {round((end-start)*1000)}ms")
            return
        
        if cmd == "uptime":
            up = int(time.time() - start_time)
            hours = up // 3600
            minutes = (up % 3600) // 60
            seconds = up % 60
            await msg.reply_text(f"⏱️ Uptime: {hours}h {minutes}m {seconds}s")
            return

        if not is_sudo(update.effective_user.id):
            return await msg.reply_text("𝐀ᴋᴋᴜ papa se Sudo Maang pehle 🌀🌀")

        chat_id = msg.chat.id

        if cmd == "gameover":
            return await gameover(update, context)
        
        if cmd == "stopall":
            return await stopall(update, context)
        
        if cmd == "pin":
            return await pin_message(update, context)
        
        if cmd == "unpin":
            return await unpin_message(update, context)
        
        if cmd == "revpin":
            return await unpin_all_messages(update, context)

        if cmd in NC_TEXTS or cmd in SPAM_TEXTS or cmd in SWIPE_TEXTS or cmd in REPLY_TEXTS:
            target = " ".join(args) if args else msg.from_user.first_name
            is_swipe = cmd in SWIPE_TEXTS
            is_reply = cmd in REPLY_TEXTS
            
            if is_swipe or is_reply:
                if not msg.reply_to_message:
                    return await msg.reply_text("Reply to a message!")
                reply_to = msg.reply_to_message.message_id
                target_name = msg.reply_to_message.from_user.first_name if msg.reply_to_message.from_user else target
                key = f"{bot_id}_{chat_id}_{reply_to}_{cmd}"
                if key in active_tasks:
                    return await msg.reply_text("⚠️ Already Running!")
                task = asyncio.create_task(swipe_loop(context, bot_id, chat_id, reply_to, cmd, target_name, is_reply))
            elif cmd in SPAM_TEXTS:
                key = f"{bot_id}_{chat_id}_{cmd}"
                if key in active_tasks:
                    return await msg.reply_text("⚠️ Already Running!")
                task = asyncio.create_task(spam_loop(context, bot_id, chat_id, cmd, target))
            else:
                key = f"{bot_id}_{chat_id}_{cmd}"
                if key in active_tasks:
                    return await msg.reply_text("⚠️ Already Running!")
                task = asyncio.create_task(nc_loop(context, bot_id, chat_id, cmd, target))
            
            active_tasks[key] = task
            await msg.reply_text(f"✅ {cmd.upper()} Started!")

        elif cmd.startswith('d'):
            removed = 0
            base_cmd = cmd.replace('d', '', 1)
            
            if cmd in ['dallnc', 'dallspam', 'dallswipe', 'dallreply']:
                category = cmd.replace('dall', '')
                for key in list(active_tasks.keys()):
                    if category in key and str(chat_id) in key:
                        task = active_tasks.pop(key, None)
                        if task and not task.done():
                            task.cancel()
                            removed += 1
            else:
                for key in list(active_tasks.keys()):
                    if key.endswith(f"_{base_cmd}") and str(chat_id) in key:
                        task = active_tasks.pop(key, None)
                        if task and not task.done():
                            task.cancel()
                            removed += 1
            
            await msg.reply_text(f"✅ Stopped {removed} loop(s)!")

        elif cmd.startswith("setdelay"):
            try:
                if not args:
                    return await msg.reply_text("Usage: !setdelaync 0.001")
                sec = float(args[0])
                if sec < 0:
                    sec = 1
                dtype = cmd.replace("setdelay", "")
                if dtype in DELAYS:
                    DELAYS[dtype] = sec
                    await msg.reply_text(f"✅ {dtype.upper()} Delay = {sec}s")
                else:
                    await msg.reply_text(f"❌ Invalid! Use: nc, spam, swipe, reply")
            except Exception:
                await msg.reply_text("❌ Invalid number!")

        elif cmd == "sudo":
            await add_sudo(update, context)
        elif cmd == "dsudo":
            await remove_sudo(update, context)
        elif cmd == "sudolist":
            await sudolist_cmd(update, context)
        elif cmd == "refreshsudo":
            await refreshsudo(update, context)
        elif cmd == "ban":
            await ban(update, context)
        elif cmd == "unban":
            await unban(update, context)
        elif cmd == "mute":
            await mute(update, context)
        elif cmd == "unmute":
            await unmute(update, context)
        elif cmd == "gcmute":
            await gcmute(update, context)
        elif cmd == "gcunmute":
            await gcunmute(update, context)
        elif cmd == "delmsg":
            await delmsg(update, context)
        elif cmd == "adminlist":
            await adminlist_cmd(update, context)
        elif cmd == "banlist":
            await banlist_cmd(update, context)
        elif cmd == "status":
            await status_cmd(update, context)
        elif cmd == "refresh":
            await refresh_cmd(update, context)

    return handler

# ====================== RUN MULTI BOT =========================
async def run_multibot():
    applications = []
    
    for i, token in enumerate(BOT_TOKENS):
        if not token or "YOUR_BOT_TOKEN" in token:
            continue
        
        try:
            app = Application.builder().token(token).build()
            handler = await make_handler(str(i))
            app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS & filters.Regex(r'^!'), handler))
            
            await app.initialize()
            await app.start()
            await app.updater.start_polling()
            
            applications.append(app)
            print(f"🚀 Bot {i+1} Started - {token[-8:]}")
            
        except Exception as e:
            print(f"❌ Bot {i+1} failed: {e}")

    if applications:
        print("\n✅ Bot is running! Press Ctrl+C to stop.\n")
        try:
            while True:
                await asyncio.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping...")
            for app in applications:
                await app.updater.stop()
                await app.stop()
                await app.shutdown()
            print("✅ Stopped!")
    else:
        print("❌ No bots started!")

if __name__ == '__main__':
    print("🔥 AKKU GAWD SUPER FAST BOT")
    print("⚡ SPEED: 0.001s")
    print("="*50)
    
    try:
        asyncio.run(run_multibot())
    except KeyboardInterrupt:
        print("\n👋 Stopped!")
    except Exception as e:
        print(f"❌ Error: {e}")