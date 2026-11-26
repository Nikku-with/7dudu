# ==============================================================================
# NETWORK V6 CLASSIC (LIGHT CORE · 𒐫~✖ WEAVE · TAGDI NC · FWD-SPAM · 24/7)
# CREDITS: @Nikkkwa (Nik)
# ==============================================================================
import asyncio
import gc
import io
import json
import os
import random
import resource
import sys
import time
import traceback
from collections import deque
from contextlib import suppress
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Set, Tuple
import re
from html import escape as _hesc

# Linux VPS / Panels par uvloop auto-enable (low RAM + ultra-high speed)
with suppress(ImportError):
    import uvloop
    uvloop.install()

gc.set_threshold(400, 5, 5)

from aiohttp import web
from aiogram import Bot, Dispatcher, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.exceptions import (
    TelegramBadRequest,
    TelegramForbiddenError,
    TelegramRetryAfter,
)
from aiogram.filters import Command, CommandObject, Filter
from aiogram.types import (
    BufferedInputFile,
    ChatPermissions,
    Message,
    ReactionTypeCustomEmoji,
    ReactionTypeEmoji,
)

# Aiogram 3.7+ InputProfilePhotoStatic import for fixing !botpfp and !gp
try:
    from aiogram.types import InputProfilePhotoStatic
except ImportError:
    InputProfilePhotoStatic = None

# ==============================================================================
# ✅ NIK CONFIG — SAB KUCH SCRIPT KE ANDAR HI  ·  powered by @Nikkkwa
# ------------------------------------------------------------------------------
#  1) OWNER_ID     : apni numeric Telegram ID (@userinfobot)
#  2) MAIN_TOKEN   : MAIN / hosting bot token (@BotFather) = slot #1, ALAG
#  3) EXTRA_TOKENS : 9 alag slots (#2..#10) — file me ek sath bhar do,
#                     YA bot se  !addtoken <token>  /  !remtoken <no>
#  4) PREFIX       : default "!" — HAMESHA chalega, chahe prefix badal jaye.
#                     Badalne ke liye:  ~prefix ~   (naya prefix ~)
#                     Prefix bhool gaye?  ! se har command chalti hi rahegi.
# ------------------------------------------------------------------------------
#  ⚠️  Yahan koi real token/ID hardcode NAHI — khali placeholders.
#      Env se bhi:  BOT_TOKEN=...  OWNER_ID=...  (CONFIG pehle padhta hai)
# ==============================================================================
CONFIG: Dict[str, Any] = {
    "OWNER_ID":   0,     # ← apni numeric ID
    "MAIN_TOKEN": "",    # ← MAIN/hosting token (#1 — alag, protected)
}

EXTRA_TOKENS: List[str] = [   # 9 alag slots  (#2 .. #10)
    "",  # 2
    "",  # 3
    "",  # 4
    "",  # 5
    "",  # 6
    "",  # 7
    "",  # 8
    "",  # 9
    "",  # 10
]

MAX_TOKENS = 10                       # 1 main + 9 extra
RUNTIME_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "nik_runtime.json")

def _clean_tok(t) -> str:
    return ("" if t is None else str(t)).strip()

def _default_rt() -> Dict[str, Any]:
    return {"prefix": "!", "overrides": [None] * 9}

def _load_rt() -> Dict[str, Any]:
    d = _default_rt()
    try:
        with open(RUNTIME_FILE, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            d["prefix"] = str(raw.get("prefix") or "!")[:4] or "!"
            ov = raw.get("overrides")
            if isinstance(ov, list):
                d["overrides"] = [x if isinstance(x, str) else None
                                  for x in (list(ov) + [None] * 9)[:9]]
    except Exception:
        pass
    return d

_RT = _load_rt()

def _save_rt() -> None:
    with suppress(Exception):
        with open(RUNTIME_FILE, "w", encoding="utf-8") as f:
            json.dump(_RT, f, indent=2)

PREFIX: str = _RT["prefix"]           # working prefix — runtime editable

def build_tokens() -> List[str]:
    """10 slots: [MAIN, #2..#10].  override: None=file / ""=cleared / "tok"=set"""
    slots = [_clean_tok(CONFIG["MAIN_TOKEN"] or os.environ.get("BOT_TOKEN", ""))]
    for i in range(9):
        ov = _RT["overrides"][i]
        slots.append(_clean_tok(EXTRA_TOKENS[i] if ov is None else ov))
    seen, out = set(), []
    for t in slots:
        if t and t in seen:
            out.append("")
        else:
            if t:
                seen.add(t)
            out.append(t)
    return out[:MAX_TOKENS]

TOKENS: List[str] = build_tokens()    # main() yahi 10-slot list padhta hai
MAIN_TOKEN: str = TOKENS[0] if TOKENS else ""
OWNER_ID: int = int(CONFIG["OWNER_ID"] or os.environ.get("OWNER_ID", 0) or 0)

# ── Dynamic command filter ───────────────────────────────────────────────────
#  "!" = immutable fallback · "~" = meta prefix · PREFIX = runtime prefix
def _cmd_prefixes(extra: str) -> set:
    return {PREFIX, "!", "~"} | set(extra or "")

class DCommand(Filter):
    """aiogram Command filter ka drop-in; prefix runtime me resolve hota hai."""
    def __init__(self, *commands: str, prefix: str = "", ignore_case: bool = True):
        self.names = {c.lower() for c in commands if c}
        self.extra = prefix or ""
        self.ignore_case = ignore_case

    async def __call__(self, message: Message):
        text = message.text or message.caption or ""
        parts = text.split(maxsplit=1)
        head = parts[0] if parts else ""
        if not head or not text.startswith(head):
            return False
        for p in sorted(_cmd_prefixes(self.extra), key=len, reverse=True):
            if not p or not head.startswith(p):
                continue
            body = head[len(p):]
            if not body:
                continue
            name = body.split("@", 1)[0]
            if self.ignore_case:
                name = name.lower()
            if name in self.names:
                mention = body.split("@", 1)[1] if "@" in body else None
                rest = text[len(head):]
                if rest[:1].isspace():
                    rest = rest[1:]
                args = rest or None
                return {"command": CommandObject(prefix=p, command=name,
                                                 mention=mention, args=args)}
        return False

def _is_command_text(text: str) -> bool:
    return bool(text) and text.startswith((PREFIX, "!", "~", "/"))

PORT: int = int(os.environ.get("SERVER_PORT", os.environ.get("PORT", 7860)))

# Indian Standard Time (IST = UTC+5:30)
IST_TZ = timezone(timedelta(hours=5, minutes=30))

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SUDO_FILE = os.path.join(BASE_DIR, "v4_sudo.json")
TEMPLATE_FILE = os.path.join(BASE_DIR, "templates.json")
SPAM_TEMPLATE_FILE = os.path.join(BASE_DIR, "spam_template.txt")
RUNTIME_STATE_FILE = os.path.join(BASE_DIR, "v4_runtime_state.json")
PFP_DISK_DIR = os.path.join(BASE_DIR, "pfp_cache_disk")
GAMEOVER_GIF_FILE = os.path.join(PFP_DISK_DIR, "gameover.mp4")

os.makedirs(PFP_DISK_DIR, exist_ok=True)

DEFAULT_GAMEOVER_GIF_URL = "https://media.giphy.com/media/eJ4j2VnYOZU8qJU3Py/giphy.gif"

MAX_LOG_ENTRIES = 200
MAX_TRACKED_USERS_PER_CHAT = 150
MAX_PFP_CACHE_PER_CHAT = 4
MAX_MEDIA_PER_CHAT = 15
MAX_FWD_QUEUE_PER_CHAT = 10

# ==============================================================================
# DATA ARRAYS & 15 DISTINCT NC WALL + TEXT DESIGNS
# ==============================================================================
RAID_TEXTS = (
    "Choti jaati ke pille msg slide mt kr 😂🥀", "Chup joker slide kese derha tu", "Dekh teri maa ke cudne ka tym hogya ⏰️",
    "Tri Ma Marjaye Ameen 🙏🤣😭😭🤣💔🤣🥀💔", "idhr a takle bhag kese rha he", "Chl chl tmkc me aag laga du 😂🔥",
    "Ny ny try maa rndi bat khtm 🗽", "Oy teri maa puri banner jaati se chude 😂🔥", "Oy haste haste tri maa chudjaye 😂😂😂",
    "Oy tri maa ke bhosde me statue of liberty 🗽", "Chup rndyk jaake apne baap ke sth naali saf krwa 🤢🤢🤢",
    "Teri maa ke marne ke bad tere baap ko bhi uske sath dafan krwa dunga!",
    "🔺पिल्लै Tᴜᴊʜᴇ ᴍᴀʀᴇɴɢᴇ ʏᴀʜɪ ᴅᴇʟʜɪ ᴍᴀʏᴜʀ ᴠɪʜᴀʀ ᴍᴇ ᴊᴀʙ ᴍᴀʀᴇɴɢᴇ ᴅᴇᴋʜ ʟᴇɴᴀ ",
    "😖ᴛᴇʀᴀ ᴅᴀᴅᴀ ᴬᴺᴳᴿᴱᶻᴼ ᴋᴀ ɴᴏᴋᴀʀ👞", "Aaj ki Raat Teri maa k Sath 🫡💔🫡💔🫡💔🫡💔🍒☝🏻☝🏻🤲🏻☝🏻",
    " chup ᴛᴇʀɪ ᴍᴀ ʀᴀɴᴅi🤪᭄", "Hindi me cudega??\nSunn fir शेर भी तु , bndar भी तु ,\nलण्ड मेरा चुस के पीता भी तु..",
    "Sorry sir no मां चुदाई allowed ✋🏿🚫", "dhek teri maa chodne ke taynat hai 🫡🫡🫡🫡🫡🫡🫡",
    "𝘾𝙃𝙐𝙋 𝙏ᴇʀɪ 𝙈𝘼 𝙍𝘼NDI👻", "*, ☞. 𝘾𝙃𝘼𝙇 ☮️ 𝙏ᴇʀI 🤞🏻 𝙈𝘼𝘼 🙈 𝙍𝘼NDI ❤",
    "DᴇᴋH mai tere ko ᧁꪖꪶﺃ dunga tu\nMere ko ek काम 𝙠𝙧𝙩𝙚 dono milke आपकी ma chodte h 💙❤️🩵💜🩶🤎🤍🩷",
    "कमजोर रण्डी तेरी मां 🩶᭪", "कमजोर रण्डी तेरी मां 🩵᭪", "कमजोर रण्डी तेरी मां 🩷᭪", "कमजोर रण्डी तेरी मां  🤍᭪",
    "कमजोर रण्डी तेरी मां 🤎᭪", "कमजोर रण्डी तेरी मां  🖤᭪", "कमजोर रण्डी तेरी मां 💜᭪", "कमजोर रण्डी तेरी मां 💙᭪",
    "कमजोर रण्डी तेरी मां  💛᭪", "कमजोर रण्डी तेरी मां  🧡᭪", "कमजोर रण्डी तेरी मां ❤᭪", "कमजोर रण्डी तेरी मां 💚᭪",
    "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛🩶₊⊹", "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛🩵₊⊹", "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛🩷₊⊹", "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛🤍₊⊹",
    "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛🖤₊⊹", "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛🤎₊⊹", "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛💜₊⊹", "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛💙₊⊹",
    "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛💚₊⊹", "𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄: ̗̀➛💛₊⊹",
)

DEFAULT_WALL_CHAR = "𒐫𒐫𒐫🤍"
GAP_100 = "\n" * 100
START_BANNER_TEXT = "𝐴𝑑𝑣𝑎𝑛𝑐𝑒 𝐵𝑜𝑡 𝐵𝑦 @Nikkkwa (Nik)"

PREFIX_EMOJIS = (
    "🐉", "🤩", "🌊", "🪼", "✨", "😹", "❄️", "🌀", "🍁", "⚡",
    "🔥", "🦋", "👑", "💎", "🌸", "🫧", "🦈", "🦁", "👻", "😈",
    "🎯", "🚀", "🌙", "⭐", "🍀",
)

EMOJIS = (
    "❄️", "🌀", "🍁", "🍢", "✉️", "🍬",
    "🍀", "🚀", "😂", "😭", "😡", "😈",
    "💧", "🫧", "☄️", "🦑", "🥀", "🧊",
)

DYNAMIC_NC_MAP = {
    "n1":  {"prefixes": ("🐙", "🫧", "🦈", "🐬", "🐋", "🐳", "🦑", "🪼", "🦀", "🦞"), "fmt": "〚 {base} 𝙈𝘼𝘼 𝙍𝘼𝙉𝘿𝙄 𝙏𝙀𝙍𝙄 〛", "wall": "𒐫🍣"},
    "n2":  {"prefixes": ("🌸", "🎀", "🎐", "✨", "🌷", "🌺", "🌻", "🌼", "🍀", "💮"), "fmt": "< {base}  𝘉𝘌𝘛𝘈 𝘉𝘖𝘓𝘖  Nik 𝘗𝘈𝘗𝘈?? >", "wall": "𒈙🐲"},
    "n3":  {"prefixes": ("⚔️", "🔥", "🎸", "🎭", "🎯", "🚀", "⚡", "💣", "🧨", "🛡️"), "fmt": " {base} 𝐶ℎ𝑢𝑝 𝑅𝑛𝑑𝑦𝑐𝑒", "wall": "⸻🍜"},
    "n4":  {"prefixes": ("🩵", "🧡", "🤍", "💛", "🩷", "💜", "🖤", "💙", "💚", "🤎"), "fmt": "{base} Cʜᴀʟ Tᴍᴋʙ", "wall": "𒁏"},
    "n5":  {"prefixes": ("💔", "🖤", "😈", "👿", "👹", "👺", "💀", "👻", "👽", "👾"), "fmt": " {base} 𝘚𝘭𝘢𝘷𝘦", "wall": "꫞🍥"},
    "n6":  {"prefixes": ("🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘", "🌙", "🪐"), "fmt": "【 {base} 𝑪𝒉𝒖𝒅𝒂𝒊 𝑲𝒉𝒂 】", "wall": "𒀰𒐫🍙"},
    "n7":  {"prefixes": ("🐉", "🦣", "🦕", "🦖", "🐊", "🦁", "🐯", "🦅", "🦉", "🐺"), "fmt": " {base} 𝘙𝘢𝘯𝘥𝘪 𝘊𝘩𝘪𝘭𝘥", "wall": "🩷🩵💙۞"},
    "n8":  {"prefixes": ("🍧", "🍯", "🍭", "🌮", "🍣", "🍱", "🍜", "🍔", "🍥", "🍡"), "fmt": " {base} 𝙏𝙐𝙈 𝙈𝘼𝘿𝘼𝙍𝘾𝙃⭕𝘿", "wall": "ᯓ★🤍"},
    "n9":  {"prefixes": ("🍁", "🌿", "🪷", "❄️", "🌀", "🌊", "🔥", "🌟", "💥", "☄️"), "fmt": "《  {base} 𝑇𝑒𝑟𝑖 𝑀𝑎𝑎 𝑇𝑎𝑘𝑙𝑖 》", "wall": "--{🍬}"},
    "n10": {"prefixes": ("👑", "💎", "🏆", "🥇", "⚜️", "🔱", "💍", "🌟", "✨", "⚡"), "fmt": "〘  {base}  𝐾𝐼 𝑀𝐴𝐴 𝐶𝐻𝑂𝐷𝑁𝐸 𝐴𝑌𝐸??〙", "wall": "꧅🍭"},
    "n11": {"prefixes": ("⛓️", "🗡️", "🩸", "⚰️", "🪦", "🕸️", "🕷️", "🦇", "🐦‍⬛", "🏴‍☠️"), "fmt": "⦗  {base} Lᴜɴᴅ Cʜᴜs ⦘", "wall": "𒈙⸻🐬"},
    "n12": {"prefixes": ("🧬", "☢️", "☣️", "⚠️", "⚡", "🔋", "💻", "🛰️", "🛸", "🧪"), "fmt": "⧼  {base} Sʟᴀᴠᴇ ⧽", "wall": "ဪဪဪ🩶"},
    "n13": {"prefixes": ("❄️", "🧊", "🌨️", "⛄", "🌬️", "🏔️", "💎", "🩵", "🫧", "🌊"), "fmt": "⟬ ❄️ {base} Cʜᴜᴘ ʀɴᴅʏᴄᴇ ʟᴀᴅᴋᴇ ❄️ ⟭", "wall": "﷽🍡"},
    "n14": {"prefixes": ("🌺", "🦋", "🦩", "🦚", "🦜", "🦢", "🌷", "🌹", "🥀", "💐"), "fmt": "⦑  {base} TMKC ⦒", "wall": "ﷺ🍵"},
    "n15": {"prefixes": ("👹", "🔥", "💢", "💥", "🩸", "☠️", "⚡", "🔱", "⚔️", "🛡️"), "fmt": "【 {base} Lᴏᴅᴇ ᴘᴇ Cʜᴅ 】", "wall": "𒀱🍢"},
}
STYLE_KEYS_TUPLE = tuple(DYNAMIC_NC_MAP.keys())

# ==============================================================================
# BIG-NC WALL FORGE  ·  photo wala "big type nc" (full-screen X-cross lattice)
# Har frame RUNTIME me banta hai — koi stored line-bank / text-stuffing nahi.
# Dense ✖⨯ mesh + heart/gem/fruit side columns + cuneiform glyph rows + counters.
# ==============================================================================
class BigWallForge:
    CROSSES = ("✖", "⨯", "╳", "✕", "❌", "✗", "⤫", "⤬")
    WEAVES = ("mesh", "diamond", "x", "storm", "gem", "heart")
    HEARTS = ("🤍", "🩵", "💙", "🩷", "💜", "❤", "💚", "🤎")
    GEMS = ("🔮", "💎", "🌌", "🦄", "✨", "🪐", "💠", "🔷")
    FRUIT = ("🍌", "🍆", "🥒", "🍉", "🥝", "🌙")
    CUNEI = ("𒐫", "𒈙", "𒀰", "𒁏", "𒐪", "𒀱")
    GLYPHS = ("⫷", "⌁", "⟁", "⟒", "⧗", "⨳", "✧", "✦", "❖", "⟡")

    def __init__(self, cols: int = 48, rows: int = 44):
        self.cols = cols
        self.rows = rows

    def weave_for(self, tick: int, variant: str = "auto") -> str:
        if variant and variant != "auto" and variant in self.WEAVES:
            return variant
        return self.WEAVES[(tick // 4) % len(self.WEAVES)]

    def _lattice(self, tick: int, r: int, weave: str) -> str:
        c = self.cols
        if weave == "diamond":
            row = ("◇◆" * (c // 2 + 1))[:c]
        elif weave == "mesh":
            row = ("⤫⤬" * (c // 2 + 1))[:c]
        elif weave == "storm":
            row = "".join(self.CROSSES[(tick + r + i) % len(self.CROSSES)] for i in range(c))
        elif weave == "gem":
            row = "".join(self.CROSSES[(r + 2 * i) % len(self.CROSSES)] for i in range(c))
        elif weave == "heart":
            row = "".join(
                self.HEARTS[(tick + r + i) % len(self.HEARTS)]
                if (i + r) % 6 == 0 else self.CROSSES[(tick + r) % 4]
                for i in range(c))
        else:
            row = self.CROSSES[(tick + r) % 4] * c
        if r % 2:
            row = row[1:] + row[:1]          # half-cell phase -> interlocking lattice
        return row

    def _side(self, tick: int, r: int, kind: str) -> str:
        pool = {"heart": self.HEARTS, "gem": self.GEMS,
                "fruit": self.FRUIT, "cunei": self.CUNEI}[kind]
        return pool[(tick + r) % len(pool)]

    def title(self, target: str, tick: int) -> str:
        tag = (target or "NIKK").strip()[:34]
        core = f"✖ {tag}  »  ɴɪᴋ  «  {tag} "
        fill = (self.CROSSES[tick % 4] * 128)[:max(0, 128 - len(core))]
        return (core + fill)[:128]

    def build(self, target: str, tick: int = 0, variant: str = "auto",
              counter: int = 0) -> str:
        weave = self.weave_for(tick, variant)
        tag = (target or "NIKK").strip()[:28]
        lines = [f"✖⨯ {tag}  »  {tag}  «  {tag} ⨯✖"]
        for r in range(self.rows):
            row = self._lattice(tick, r, weave)
            if r % 7 == 3:                   # dense glyph band
                g = self.GLYPHS[(tick + r) % len(self.GLYPHS)]
                pos = max(0, self.cols // 2 - 2)
                row = row[:pos] + (g * 4) + row[pos + 4:]
            left = self._side(tick, r, "gem" if r % 5 == 0 else "cunei")
            right = self._side(tick, r, "heart" if r % 3 else "fruit")
            lines.append(left + row + right)
        n = counter or (31000 + tick * 13)
        lines.append(f"⨯ {' '.join(self.HEARTS[:3])}  {n:,}  "
                     f"{' '.join(self.CROSSES[:3])}  @Nikkkwa")
        return "\n".join(lines)

BIGWALL = BigWallForge()

# ==============================================================================
# ULTRA-WALL FORGE · 10 RANDOM VERY-BIG WALLS + FULL PAGE-BLOCK
#   Har family RUNTIME me banti hai — koi stored line-bank / text-stuffing nahi.
#   Har frame: naya random emoji palette, naya phase, naya counter.
#   compose_page() poora page bhar deta hai → saamne wali ki NC scroll off ho jati hai.
# ==============================================================================
MEGA_EMOJIS = (
    "💎", "🔮", "🩵", "🤍", "🩷", "💜", "❤", "💚", "🧡", "💛", "🖤", "🤎", "✨", "⚡", "🔥",
    "🌸", "🌺", "🌷", "🪷", "🍀", "🌿", "🍁", "❄️", "🌀", "🌊", "🌙", "⭐", "🌟", "☄️", "🪐",
    "🍉", "🍌", "🍆", "🥝", "🍇", "🍓", "🍒", "🥑", "🍍", "🥥", "🍑", "🍋", "🫐", "🍎", "🍐",
    "👑", "🏆", "🥇", "⚜️", "🔱", "💍", "🗡️", "🛡️", "⛓️", "🩸", "💀", "👻", "👹", "👺", "😈",
    "🦋", "🦄", "🐉", "🦁", "🦈", "🐬", "🪼", "🦑", "🦚", "🦩", "🐺", "🦅", "🐯", "🐊", "🦖",
    "🎯", "🚀", "🎭", "🎸", "🧨", "💣", "🧬", "☢️", "☣️", "🛸", "🛰️", "🧪", "🔋", "🕸️", "🦇",
    "🫧", "🧊", "🌨️", "⛄", "🏔️", "🌌", "🔷", "🔶", "💠", "⟡", "❖", "✦", "✧", "⧗", "⨳",
    "🍧", "🍯", "🍭", "🍢", "🍬", "🍣", "🍱", "🍜", "🍔", "🍥", "🍡", "🍵", "🍶", "🥀", "💐",
)

PACK_DELAY = 0.15          # gap between the 10 walls of !wallpack (speed engine)
WALL_CACHE_TTL = 3.0       # same wall dobara build karne ki zarurat nahi
IDLE_SLEEP = 0.05          # worker ka idle wait (0.5s se 10x fast pickup)
# SPEED ENGINE: (per-bot title gap sec, per-chat page-block interval sec)
#   Pehle HAR tick pe 3,900-char page jata tha -> per-chat flood -> saare
#   bots cooldown me -> script slow/dead.  Ab titles fast, pages budgeted.
SPEED_MODES = {"safe": (0.92, 6.00), "max": (0.92, 3.00),
               "turbo": (0.55, 1.50), "off": (0.30, 0.75)}
PAGE_INTERVAL = 3.00       # live value (mode se update hota hai)
_PAGE_LAST: Dict[int, float] = {}



# ==============================================================================
# NEMO WALL ENGINE  ·  𒐫 𒐫 𒐫 heavy cuneiform gutters + neon sides
# Ek line = (2-3x 𒐫) + pattern-cell + (2-3x 𒐫) har cell pe  ->  harr row
# 500+ cuneiform, page 4,900 chars.  Sab kuch runtime, koi stored wall nahi.
# ==============================================================================
NEMO_HEAVY = 2.6                     # average 𒐫 per pattern cell
NEMO_HARD_LIMIT = 4900               # full-page hard cap (classic weave)




_WALL_CACHE: Dict[str, tuple] = {}


def compose_page(wall: str, limit: int = 3900) -> str:
    """Adaptive full page-block: repeat the giant wall + viewport gaps to <=limit.

    Agar wall badi ho to utni hi full rows bheji jati hain jitni jagah bache;
    aakhir me khaali lines ka bada block jod kar saamne wali NC screen se bahar
    dhakel di jati hai.  Kabhi bhi limit cross nahi hoti.

    SPEED: result TTL cache me rehta hai — ek hi wall ko baar baar compose
    karne me CPU cycles waste nahi hote (ultra worker har tick compose karta tha).
    """
    key = f"{limit}:{len(wall)}:{hash(wall) & 0xFFFFFFFF:x}"
    hit = _WALL_CACHE.get(key)
    if hit is not None:
        stamp, page = hit
        if (time.monotonic() - stamp) < WALL_CACHE_TTL:
            return page
    page = _compose_page_raw(wall, limit)
    if len(_WALL_CACHE) > 512:
        _WALL_CACHE.clear()
    _WALL_CACHE[key] = (time.monotonic(), page)
    return page


def _compose_page_raw(wall: str, limit: int = 3900) -> str:
    """Uncached composer body (compose_page ke neeche se call hota hai)."""
    wall = wall.rstrip("\n")
    if not wall:
        return ""
    if len(wall) >= limit:
        return wall[:limit]
    rows = wall.split("\n")
    gap = "\n" * 40
    chunks, used = [wall, gap], len(wall) + len(gap)
    while used < limit:
        room = limit - used
        if room >= len(wall):
            chunks.append(wall + gap)
            used += len(wall) + len(gap)
            continue
        picked, acc = [], 0
        for ln in rows:
            if acc + len(ln) + 1 > room:
                break
            picked.append(ln)
            acc += len(ln) + 1
        if picked:
            chunks.append("\n".join(picked))
            used += acc
        else:
            chunks.append("\n" * room)
            used += room
        break
    tail = min(len(GAP_100), max(0, limit - used))
    if tail > 0:
        chunks.append("\n" * tail)
    return ("".join(chunks))[:limit]



# ==============================================================================
# WALL FORGE · CLASSIC 𒐫~✖ WEAVE  (light core, 12 families)
#   Screenshot look: unit-repeat weave + side emoji column + TMKC header/footer.
#   Sab runtime — koi stored wall/line-bank nahi.
# ==============================================================================
class WallForge:
    """12 classic families. RECIPES[fam] = (unit, left_pool, right_pool, accent)."""

    UNITS = ("𒐫~✖", "𒐫~⨯", "𒐫~✧", "✖~𒐫", "𒀰~✖", "𒐫~❖",
             "⨯~𒐫", "𒁏~✖", "𒐫~⟡", "✖~⨯", "𒐪~✖", "𒐫~⫷")
    HEARTS = ("🤍", "🩵", "💙", "🩷", "💜", "❤", "💚", "🧡", "🖤", "🤎")
    GEMS = ("💎", "🔮", "🪐", "✨", "👑", "⚜️", "🌌", "🔷", "💠", "🦄")
    SPICE = ("💀", "🔥", "⚡", "☠️", "💥", "🌟", "🌀", "🧿", "🩸", "🗿")
    GLYPH = ("⫷", "⌁", "⟁", "⟒", "⧗", "⨳", "✧", "✦", "❖", "⟡", "𒑊", "𒀭")

    FAMILIES = ("xmesh", "diamond", "heartline", "gemrain", "cuneiwave",
                "runeline", "apex", "storm", "titan", "blood", "royal", "mega")
    # har unit me 𒐫 (U+1242B) compulsory — user ka reference look
    RECIPES = {
        "xmesh":     ("𒐫~✖", HEARTS, GEMS,   "💙"),
        "diamond":   ("𒐫~⨯", GEMS,   HEARTS, "💎"),
        "heartline": ("𒐫~✧", HEARTS, HEARTS, "💙"),
        "gemrain":   ("✖~𒐫", GEMS,   SPICE,  "💎"),
        "cuneiwave": ("𒐫~❖", SPICE,  HEARTS, "𒐫"),
        "runeline":  ("𒐫~⟡", GEMS,   GEMS,   "❖"),
        "apex":      ("⨯~𒐫", SPICE,  GEMS,   "🔥"),
        "storm":     ("𒐫~✦", SPICE,  SPICE,  "⚡"),
        "titan":     ("𒐫~⫷", GEMS,   HEARTS, "👑"),
        "blood":     ("𒐫✖~", SPICE,  HEARTS, "🩸"),
        "royal":     ("𒐫~⨯✖", GEMS,  GEMS,   "⚜️"),
        "mega":      ("𒐫𒐫✖", HEARTS, GEMS,   "💀"),
    }

    def __init__(self, cols: int = 30, rows: int = 46):
        self.cols = cols          # units per row  (30 x 3 = 90 chars)
        self.rows = rows
        self.builds = 0

    def title(self, target: str, tick: int = 0, seed=None) -> str:
        rng = random.Random(seed) if seed is not None else random
        tag = (target or "NIKK").strip()[:22]
        e1 = rng.choice(self.HEARTS + self.GEMS)
        e2 = rng.choice(self.SPICE)
        core = f"{e1} 𒐫~✖ {tag} » ᴛɪᴛᴀɴ « {tag} ✖~𒐫 {e2} "
        return (core + ("𒐫~✖" * 128))[:128]

    def palette(self, rng, k: int = 8):
        return rng.sample(self.SPICE + self.GEMS, min(k, len(self.SPICE + self.GEMS)))

    def build(self, target: str, tick: int = 0, family: str = "random",
              counter: int = 0, seed=None) -> str:
        rng = random.Random(seed) if seed is not None else random
        fam = family if family in self.RECIPES else rng.choice(self.FAMILIES)
        unit, left_pool, right_pool, accent = self.RECIPES[fam]
        pal = self.palette(rng, 6)
        tag = (target or "NIKK").strip()[:20]
        out = [f"{accent}  {tag}  »  ɴɪᴋ ᴛɪᴛᴀɴ  «  {tag}  {accent}"]
        for r in range(self.rows):
            line = unit * self.cols
            if r % 2:                                   # interlocking half-phase
                line = line[-2:] + line[:-2]
            if r % 6 == 3:                              # dense glyph band
                g = self.GLYPH[(tick + r) % len(self.GLYPH)]
                pos = len(line) // 2
                line = line[:pos] + (g * 3) + line[pos + 3:]
            if r % 5 == 0:                              # emoji sprinkle
                cells = list(line)
                for _ in range(3):
                    if cells:
                        cells[rng.randrange(len(cells))] = rng.choice(pal)
                line = "".join(cells)
            left = left_pool[(tick + r) % len(left_pool)]
            right = right_pool[(tick + r + 3) % len(right_pool)]
            out.append(left + line + right)
        n = counter or (52000 + tick * 11)
        out.append(f"{right_pool[0]}  {tag} TMKC  {accent}  {n:,}  "
                   f"@Nikkkwa (Nik)  {left_pool[0]}")
        self.builds += 1
        return "\n".join(out)

    def page_block(self, target: str, tick: int = 0, family: str = "random",
                   counter: int = 0, seed=None, limit: int = NEMO_HARD_LIMIT) -> str:
        return compose_page(self.build(target, tick, family, counter, seed), limit)

    def pack(self, target: str, counter: int = 0, seed=None):
        rng = random.Random(seed) if seed is not None else random
        fams = list(self.FAMILIES)
        rng.shuffle(fams)
        return [self.page_block(target, i, fam, counter + i,
                                seed=rng.randrange(1 << 30))
                for i, fam in enumerate(fams)]


WALL = WallForge()
# purane command handlers isi engine pe chalte hain (drop-in API)
ULTRA = WALL
NEMO = WALL

# ==============================================================================
# RAM TELEMETRY, IST CLOCK & BOUNDED LOG ENGINE
# ==============================================================================
LOG_BUFFER = deque(maxlen=MAX_LOG_ENTRIES)

def get_ist_now() -> datetime:
    return datetime.now(IST_TZ)

def get_ist_str() -> str:
    return get_ist_now().strftime("%d-%m-%Y | %I:%M:%S %p IST")

def get_ram_mb() -> float:
    with suppress(Exception):
        if os.path.exists("/proc/self/status"):
            with open("/proc/self/status", "r") as f:
                for line in f:
                    if line.startswith("VmRSS:"):
                        return int(line.split()[1]) / 1024.0
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return usage / (1024.0 * 1024.0) if sys.platform == "darwin" else usage / 1024.0
    return 0.0

def log_event(level: str, tag: str, message: str):
    timestamp = get_ist_now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] [{level.upper()}] [{tag}] {message}"
    LOG_BUFFER.append(entry)
    print(entry, flush=True)

# ==============================================================================
# ULTRA-FAST LRU + ZERO-DOMINO PIPELINED FLOOD BYPASS CONTROLLER
# ==============================================================================
class FloodBypassEngine:
    __slots__ = (
        "cooldowns", "bypass_active", "throttle_mode", "flood_history",
        "last_nc_call", "in_flight", "per_bot_nc_gap", "cluster_nc_tick",
        "total_nc_ok", "recent_ticks", "missing_until", "total_bots"
    )

    def __init__(self):
        self.cooldowns: Dict[int, float] = {}
        self.bypass_active: bool = True
        self.throttle_mode: str = "max"
        self.flood_history: Dict[int, int] = {}
        self.last_nc_call: Dict[int, float] = {}
        self.in_flight: Set[int] = set()
        self.missing_until: Dict[tuple, float] = {}

        # 0.92s per-bot gap + 0.10s cluster pipeline tick = 10 updates/sec with zero flood
        self.per_bot_nc_gap: float = 0.92
        self.cluster_nc_tick: float = 0.10
        self.total_bots: int = 1

        self.total_nc_ok: int = 0
        self.recent_ticks: deque = deque(maxlen=40)

    def recalculate_pacing(self, total_bots: int):
        """SPEED ENGINE — do alag budgets: titles (fast) + page-blocks (budgeted)."""
        global PAGE_INTERVAL
        n = max(1, total_bots)
        self.total_bots = n
        gap, page_iv = SPEED_MODES.get(self.throttle_mode, SPEED_MODES["max"])
        self.per_bot_nc_gap = gap
        PAGE_INTERVAL = page_iv
        self.cluster_nc_tick = round(min(1.0 / n, 0.10), 3)
        with suppress(Exception):
            STATE.delays["nc"] = self.cluster_nc_tick

    def set_mode(self, mode: str, total_bots: int):
        mode = mode.lower().strip()
        if mode in ("turbo", "insane", "gfaad"):
            self.throttle_mode = "turbo"
            self.bypass_active = True
        elif mode in ("max", "on", "fast"):
            self.throttle_mode = "max"
            self.bypass_active = True
        elif mode in ("safe", "stable", "balanced"):
            self.throttle_mode = "safe"
            self.bypass_active = True
        elif mode in ("off", "disable", "raw"):
            self.throttle_mode = "off"
            self.bypass_active = False
        self.recalculate_pacing(total_bots)

    def record_nc_success(self):
        self.recent_ticks.append(time.monotonic())
        self.total_nc_ok += 1

    def get_live_hz(self) -> float:
        if len(self.recent_ticks) < 2:
            return 0.0
        now = time.monotonic()
        span = now - self.recent_ticks[0]
        if span <= 0 or (now - self.recent_ticks[-1]) > 5.0:
            return 0.0
        return round((len(self.recent_ticks) - 1) / span, 2)

    def mark_bot_present(self, chat_id: int, bot_id: int):
        self.missing_until.pop((chat_id, bot_id), None)

    def mark_bot_missing_in_chat(self, chat_id: int, bot_id: int, duration: float = 25.0):
        self.missing_until[(chat_id, bot_id)] = time.monotonic() + duration

    def is_bot_usable_in_chat(self, chat_id: int, bot_id: int) -> bool:
        until = self.missing_until.get((chat_id, bot_id), 0.0)
        if time.monotonic() < until:
            return False
        if (chat_id, bot_id) in self.missing_until:
            del self.missing_until[(chat_id, bot_id)]
        return True

    def is_flooded(self, bot_id: int) -> bool:
        until = self.cooldowns.get(bot_id, 0.0)
        if time.monotonic() < until:
            return True
        if bot_id in self.cooldowns:
            del self.cooldowns[bot_id]
            log_event("info", "BYPASS", f"Bot {bot_id} cooldown expired. Rejoined 10-bot pipeline.")
        return False

    def is_ready_for_nc(self, bot_id: int, chat_id: Optional[int] = None) -> bool:
        if bot_id in self.in_flight or self.is_flooded(bot_id):
            return False
        if chat_id is not None and not self.is_bot_usable_in_chat(chat_id, bot_id):
            return False
        if not self.bypass_active:
            return True
        return (time.monotonic() - self.last_nc_call.get(bot_id, 0.0)) >= self.per_bot_nc_gap

    def pick_best_nc_bot(self, bots: List[Bot], chat_id: int) -> Optional[Bot]:
        """
        LRU (Least Recently Used) Selector:
        Always picks the ready bot that rested the longest.
        If all bots were marked missing in chat (e.g. temporary admin toggle), auto-clears missing flags so NC never stops.
        """
        best_bot = None
        oldest_call = float("inf")
        usable_any = False

        for b in bots:
            if self.is_bot_usable_in_chat(chat_id, b.id):
                usable_any = True
            if self.is_ready_for_nc(b.id, chat_id):
                last_t = self.last_nc_call.get(b.id, 0.0)
                if last_t < oldest_call:
                    oldest_call = last_t
                    best_bot = b

        # Self-healing guard: if every single bot got marked missing, reset missing flags so NC never halts
        if not usable_any and bots:
            for b in bots:
                self.missing_until.pop((chat_id, b.id), None)

        return best_bot

    def count_healthy_bots_in_chat(self, bots: List[Bot], chat_id: int) -> int:
        return sum(
            1 for b in bots
            if not self.is_flooded(b.id) and self.is_bot_usable_in_chat(chat_id, b.id)
        )

    def mark_started(self, bot_id: int):
        self.in_flight.add(bot_id)
        self.last_nc_call[bot_id] = time.monotonic()

    def mark_finished(self, bot_id: int):
        self.in_flight.discard(bot_id)

    def remaining_cooldown(self, bot_id: int) -> float:
        return max(0.0, self.cooldowns.get(bot_id, 0.0) - time.monotonic())

    def mark_flooded(self, bot_id: int, retry_after: float, chat_id: Optional[int] = None):
        wait_time = float(retry_after) + 0.25
        self.cooldowns[bot_id] = time.monotonic() + wait_time
        self.flood_history[bot_id] = self.flood_history.get(bot_id, 0) + 1
        log_event("warn", "FLOOD", f"Bot {bot_id} hit 429 ({retry_after}s). Resting for {wait_time:.1f}s while other bots continue.")

fbe = FloodBypassEngine()

class BotQueue:
    __slots__ = ("min_gap_sec", "_last")

    def __init__(self, min_gap_ms: int = 100):
        self.min_gap_sec = min_gap_ms / 1000.0
        self._last: Dict[int, float] = {}

    async def wait(self, bid: int):
        now = time.monotonic()
        last = self._last.get(bid, 0.0)
        gap = self.min_gap_sec - (now - last)
        if gap > 0:
            await asyncio.sleep(gap)
        self._last[bid] = time.monotonic()
        return True

bq = BotQueue(min_gap_ms=100)

# ==============================================================================
# STATE MANAGEMENT
# ==============================================================================
def load_sudo() -> Set[int]:
    if os.path.exists(SUDO_FILE):
        with suppress(Exception):
            with open(SUDO_FILE, "r") as f:
                return set(json.load(f))
    return {OWNER_ID}

class StateManager:
    __slots__ = (
        "sudo", "tasks", "persisted_tasks", "nc_target_names",
        "gameover_gif_bytes", "delays", "targets", "media",
        "fwd_queue", "pfp_cache", "muted", "tracked_users",
        "known_chats", "chat_bots", "global_nc_count",
        "chat_nc_counts", "unsaved_nc_hits", "start_time", "failed_bots"
    )

    def __init__(self):
        self.sudo: Set[int] = load_sudo()
        self.tasks: Dict[str, Dict[int, Set[asyncio.Task]]] = {
            "nc": {}, "spam": {}, "fwd": {}, "media": {}, "pfp": {}, "gpfp": {}, "slide": {}, "big": {}, "fspam": {}, "tagdi": {}
        }
        self.persisted_tasks: Dict[str, Dict[str, Dict[str, Any]]] = {
            "nc": {}, "spam": {}, "fwd": {}, "media": {}, "slide": {}, "pfp": {}, "gpfp": {}, "big": {}
        }
        self.nc_target_names: Dict[int, str] = {}
        self.gameover_gif_bytes: Optional[bytes] = None

        # Ultra-Fast Default Pacing: 0.10s (100ms) NC tick & 0.25s Spam/Slide/Fwd
        self.delays: Dict[str, float] = {
            "nc": 0.10, "spam": 0.25, "rspm": 0.25, "fwd": 0.25, "slide": 0.25, "media": 1.0, "pfp": 1.0, "gpfp": 2.0
        }
        self.targets: Dict[str, Dict[int, Any]] = {"reply": {}, "react": {}, "swipe": {}}
        self.media: Dict[str, Dict[int, deque]] = {
            "photo": {}, "gif": {}, "sticker": {}, "video": {}, "voice": {}
        }
        self.fwd_queue: Dict[int, deque] = {}
        self.pfp_cache: Dict[str, Dict[int, deque]] = {"pfp": {}, "gpfp": {}}
        self.muted: Dict[int, Set[int]] = {}
        self.tracked_users: Dict[int, Set[int]] = {}
        self.known_chats: Set[int] = set()
        self.chat_bots: Dict[int, Set[int]] = {}
        self.global_nc_count: int = 0
        self.chat_nc_counts: Dict[int, int] = {}
        self.unsaved_nc_hits: int = 0
        self.start_time = time.time()
        self.failed_bots: List[str] = []

    def record_nc_hit(self, cid: int):
        self.global_nc_count += 1
        self.chat_nc_counts[cid] = self.chat_nc_counts.get(cid, 0) + 1
        self.unsaved_nc_hits += 1

    def register_chat_bot(self, cid: int, bot_id: int, is_group: bool = True):
        if is_group:
            self.known_chats.add(cid)
        self.chat_bots.setdefault(cid, set()).add(bot_id)
        fbe.mark_bot_present(cid, bot_id)

    def get_all_known_groups(self, fallback_cid: Optional[int] = None) -> List[int]:
        groups = set(self.known_chats)
        for c in self.tracked_users.keys():
            if c < 0:
                groups.add(c)
        for cat_dict in self.persisted_tasks.values():
            for cid_str in cat_dict.keys():
                with suppress(Exception):
                    c = int(cid_str)
                    if c < 0:
                        groups.add(c)
        if fallback_cid and not groups:
            groups.add(fallback_cid)
        return list(groups)

    def save_sudo(self):
        with suppress(Exception):
            with open(SUDO_FILE, "w") as f:
                json.dump(list(self.sudo), f)

    def save_gameover_gif(self, raw_bytes: bytes):
        self.gameover_gif_bytes = raw_bytes
        with suppress(Exception):
            with open(GAMEOVER_GIF_FILE, "wb") as f:
                f.write(raw_bytes)

    def load_pfp_from_disk(self):
        with suppress(Exception):
            if os.path.exists(GAMEOVER_GIF_FILE):
                with open(GAMEOVER_GIF_FILE, "rb") as f:
                    self.gameover_gif_bytes = f.read()
            if not os.path.exists(PFP_DISK_DIR):
                return
            for folder in os.listdir(PFP_DISK_DIR):
                if "_" not in folder:
                    continue
                cat, cid_str = folder.split("_", 1)
                if cat not in self.pfp_cache:
                    continue
                cid = int(cid_str)
                chat_dir = os.path.join(PFP_DISK_DIR, folder)
                q = self.pfp_cache[cat].setdefault(cid, deque(maxlen=MAX_PFP_CACHE_PER_CHAT))
                for fname in sorted(os.listdir(chat_dir)):
                    if fname.endswith(".jpg"):
                        with open(os.path.join(chat_dir, fname), "rb") as f:
                            q.append(f.read())

    def save_pfp_to_disk(self, cat: str, cid: int):
        with suppress(Exception):
            chat_dir = os.path.join(PFP_DISK_DIR, f"{cat}_{cid}")
            os.makedirs(chat_dir, exist_ok=True)
            for idx, raw_bytes in enumerate(self.pfp_cache[cat].get(cid, [])):
                with open(os.path.join(chat_dir, f"{idx}.jpg"), "wb") as f:
                    f.write(raw_bytes)

    def save_runtime_state(self):
        with suppress(Exception):
            payload = {
                "throttle_mode": fbe.throttle_mode,
                "global_nc_count": self.global_nc_count,
                "chat_nc_counts": {str(cid): cnt for cid, cnt in self.chat_nc_counts.items()},
                "nc_target_names": {str(cid): name for cid, name in self.nc_target_names.items()},
                "persisted_tasks": self.persisted_tasks,
                "delays": self.delays,
                "known_chats": list(self.known_chats),
                "muted": {str(cid): list(uids) for cid, uids in self.muted.items() if uids},
                "targets": {
                    t_cat: {str(k): v for k, v in t_dict.items()}
                    for t_cat, t_dict in self.targets.items()
                },
                "media": {
                    m_cat: {str(cid): list(q) for cid, q in m_dict.items() if q}
                    for m_cat, m_dict in self.media.items()
                },
                "fwd_queue": {
                    str(cid): list(q) for cid, q in self.fwd_queue.items() if q
                },
            }
            tmp_file = RUNTIME_STATE_FILE + ".tmp"
            with open(tmp_file, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False)
            os.replace(tmp_file, RUNTIME_STATE_FILE)

    def load_runtime_state(self) -> Dict[str, Any]:
        self.load_pfp_from_disk()
        if not os.path.exists(RUNTIME_STATE_FILE):
            return {}
        try:
            with open(RUNTIME_STATE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data.get("throttle_mode"), str):
                fbe.set_mode(data["throttle_mode"], max(1, len(active_bots)))
            if isinstance(data.get("global_nc_count"), int):
                self.global_nc_count = data["global_nc_count"]
            if isinstance(data.get("chat_nc_counts"), dict):
                for cid_str, cnt in data["chat_nc_counts"].items():
                    with suppress(Exception):
                        self.chat_nc_counts[int(cid_str)] = int(cnt)
            if isinstance(data.get("nc_target_names"), dict):
                for cid_str, name in data["nc_target_names"].items():
                    with suppress(Exception):
                        self.nc_target_names[int(cid_str)] = str(name)
            if isinstance(data.get("known_chats"), list):
                for c in data["known_chats"]:
                    with suppress(Exception):
                        self.known_chats.add(int(c))
            if isinstance(data.get("delays"), dict):
                for k, v in data["delays"].items():
                    if k in self.delays and isinstance(v, (int, float)):
                        self.delays[k] = float(v)
            if isinstance(data.get("muted"), dict):
                for cid_str, uids in data["muted"].items():
                    self.muted[int(cid_str)] = set(uids)
            if isinstance(data.get("targets"), dict):
                for t_cat, t_dict in data["targets"].items():
                    if t_cat in self.targets and isinstance(t_dict, dict):
                        self.targets[t_cat] = {int(k): v for k, v in t_dict.items()}
            if isinstance(data.get("media"), dict):
                for m_cat, m_dict in data["media"].items():
                    if m_cat in self.media and isinstance(m_dict, dict):
                        for cid_str, fids in m_dict.items():
                            self.media[m_cat][int(cid_str)] = deque(fids, maxlen=MAX_MEDIA_PER_CHAT)
            if isinstance(data.get("fwd_queue"), dict):
                for cid_str, items in data["fwd_queue"].items():
                    if isinstance(items, list):
                        self.fwd_queue[int(cid_str)] = deque(items, maxlen=MAX_FWD_QUEUE_PER_CHAT)
            if isinstance(data.get("persisted_tasks"), dict):
                for cat, c_dict in data["persisted_tasks"].items():
                    if cat in self.persisted_tasks and isinstance(c_dict, dict):
                        self.persisted_tasks[cat] = c_dict
                        for cid_str in c_dict.keys():
                            with suppress(Exception):
                                self.known_chats.add(int(cid_str))
            return data
        except Exception as e:
            log_event("warn", "RESTORE", f"Could not load runtime state: {e}")
            return {}

    def add_task(self, cat: str, cid: int, task: asyncio.Task):
        self.tasks.setdefault(cat, {}).setdefault(cid, set()).add(task)
        task.add_done_callback(lambda t: self.tasks[cat].get(cid, set()).discard(t))

    def cancel(self, cat: str, cid: int, save: bool = True):
        for task in self.tasks.get(cat, {}).pop(cid, set()):
            task.cancel()
        if cat in self.persisted_tasks:
            self.persisted_tasks[cat].pop(str(cid), None)
        if save:
            self.save_runtime_state()

    def stop_all(self, cid: int = None, save: bool = True):
        if cid:
            for cat in self.tasks:
                self.cancel(cat, cid, save=False)
            self.fwd_queue.pop(cid, None)
            for target_cat in self.targets:
                self.targets[target_cat].pop(cid, None)
            log_event("info", "STOP", f"All tasks halted for Chat: {cid}")
        else:
            for cat in self.tasks:
                for c in list(self.tasks[cat].keys()):
                    self.cancel(cat, c, save=False)
            if save:
                for cat in self.persisted_tasks:
                    self.persisted_tasks[cat].clear()
                self.fwd_queue.clear()
                for target_cat in self.targets:
                    self.targets[target_cat].clear()
            log_event("warn", "STOP-ALL", "All background tasks terminated.")
        if save:
            self.save_runtime_state()
        gc.collect()

STATE = StateManager()
router = Router()
active_bots: List[Bot] = []
bot_usernames: Dict[int, str] = {}
LIVE_BOTS: Dict[str, Bot] = {}   # token -> booted Bot (live add/remove)

# ==============================================================================
# ZERO-DELAY MULTI-BOT COMMAND FAILOVER MIDDLEWARE
# ==============================================================================
PROCESSED_MESSAGES: deque = deque(maxlen=1000)

@router.message.outer_middleware()
async def multi_bot_failover_middleware(handler, event: Message, data: Dict[str, Any]):
    bot: Optional[Bot] = data.get("bot")
    cid = event.chat.id
    is_group = event.chat.type in ("group", "supergroup")

    if bot:
        STATE.register_chat_bot(cid, bot.id, is_group=is_group)

    # Ignore title/photo service updates immediately so they never waste CPU
    if event.new_chat_title or event.new_chat_photo or event.delete_chat_photo:
        return

    # Instant zero-delay deduplication: whichever bot receives the message first handles it
    msg_key = (cid, event.message_id)
    if msg_key in PROCESSED_MESSAGES:
        return
    PROCESSED_MESSAGES.append(msg_key)

    return await handler(event, data)

# ==============================================================================
# FIXED BOT PROFILE PHOTO HELPER (WORKS ON AIOGRAM 3.7+ & OLDER)
# ==============================================================================
async def set_bot_profile_photo_safe(bot: Bot, raw_bytes: bytes) -> bool:
    try:
        file_obj = BufferedInputFile(raw_bytes, filename="pfp.jpg")
        if InputProfilePhotoStatic is not None:
            photo_payload = InputProfilePhotoStatic(type="static", photo=file_obj)
            await bot.set_my_profile_photo(photo=photo_payload)
        else:
            await bot.set_my_profile_photo(photo=file_obj)
        return True
    except TelegramRetryAfter as e:
        fbe.mark_flooded(bot.id, e.retry_after)
        return False
    except Exception:
        with suppress(Exception):
            file_obj = BufferedInputFile(raw_bytes, filename="pfp.jpg")
            await bot.set_my_profile_photo(photo=file_obj)
            return True
    return False

# ==============================================================================
# OWNER NOTIFICATION & GC INVITE LINK HELPER
# ==============================================================================
async def get_gc_invite_and_title(cid: int) -> tuple[str, str]:
    chat_title = f"Chat {cid}"
    invite_link = "Unavailable (No Invite Admin Right)"

    for b in active_bots:
        if fbe.is_flooded(b.id) or not fbe.is_bot_usable_in_chat(cid, b.id):
            continue
        with suppress(Exception):
            chat_obj = await b.get_chat(cid)
            if chat_obj.title:
                chat_title = chat_obj.title
            if chat_obj.username:
                invite_link = f"https://t.me/{chat_obj.username}"
                break
        try:
            inv = await b.create_chat_invite_link(chat_id=cid, name="GameOver Report")
            if inv and inv.invite_link:
                invite_link = inv.invite_link
                break
        except Exception:
            with suppress(Exception):
                exp = await b.export_chat_invite_link(chat_id=cid)
                if exp:
                    invite_link = exp
                    break
    return chat_title, invite_link

async def notify_owner_dm(html_text: str):
    for b in active_bots:
        if fbe.is_flooded(b.id):
            continue
        try:
            await b.send_message(OWNER_ID, html_text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
            return True
        except Exception:
            continue
    return False

class IsOwner(Filter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.from_user and message.from_user.id == OWNER_ID)

class IsSudo(Filter):
    async def __call__(self, message: Message) -> bool:
        return bool(message.from_user and (message.from_user.id in STATE.sudo or message.from_user.id == OWNER_ID))

# ==============================================================================
# PUBLIC /START COMMAND
# ==============================================================================
@router.message(DCommand("start", prefix="/!"))
async def cmd_public_start(message: Message):
    await message.reply(START_BANNER_TEXT)

# ==============================================================================
# 🔧 NIK SYSTEM — PREFIX EDIT + 10-TOKEN CLUSTER COMMANDS
#    !  hamesha · ~prefix ~  ·  !addtoken  ·  !remtoken  ·  !tokens
# ==============================================================================
def _mask_tok(t: str) -> str:
    t = t or ""
    return (t[:8] + "..." + t[-4:]) if len(t) > 14 else (t or "—")

@router.message(DCommand("prefix", "setprefix"), IsOwner())
async def cmd_prefix(message: Message, command: CommandObject):
    global PREFIX
    arg = (command.args or "").strip()
    new = arg.split()[0] if arg else ""
    if not new:
        return await message.reply(
            f"⚙️ <b>Working prefix:</b> <code>{_hesc(PREFIX)}</code>\n"
            "🔒 <code>!</code> fallback hamesha chalega (kabhi band nahi).\n"
            "✏️ Badalne ke liye: <code>~prefix ~</code>  ya  <code>!prefix .</code>",
            parse_mode=ParseMode.HTML)
    if len(new) > 4 or any(c.isspace() for c in new):
        return await message.reply("⚠️ Prefix 1–4 chars ka, bina space.", parse_mode=ParseMode.HTML)
    PREFIX = new
    _RT["prefix"] = PREFIX
    _save_rt()
    await message.reply(
        f"✅ <b>New prefix:</b> <code>{_hesc(PREFIX)}</code>\n"
        "🔒 <code>!command</code> abhi bhi chalega — prefix bhool gaye toh bhi.\n"
        "↩️ Wapas <code>!</code>: <code>!prefix !</code>",
        parse_mode=ParseMode.HTML)

@router.message(DCommand("tokens", "listtokens", "listbots"), IsOwner())
async def cmd_tokens(message: Message):
    lines = [f"🤖 <b>NIK CLUSTER</b> • <code>{sum(1 for t in TOKENS if t)}/{MAX_TOKENS}</code> active",
             f"⚙️ <b>Prefix:</b> <code>{_hesc(PREFIX)}</code> • 🔒 <code>!</code> always-on", ""]
    for i, t in enumerate(TOKENS, 1):
        tag = "  👑 MAIN" if i == 1 else ""
        lines.append(f"<code>{i:2d}.</code> {_mask_tok(t)}{tag}")
    lines += ["", "➕ <code>!addtoken &lt;token&gt;</code>  •  🗑 <code>!remtoken &lt;no&gt;</code>",
              "🔒 #1 MAIN CONFIG me alag — bot se remove nahi hota."]
    await message.reply("\n".join(lines), parse_mode=ParseMode.HTML)

@router.message(DCommand("addtoken", "addtokens"), IsOwner())
async def cmd_addtoken(message: Message, command: CommandObject):
    raw = (command.args or "").strip()
    cands = re.findall(r"\d{6,12}:[A-Za-z0-9_-]{20,}", raw)
    if not cands:
        return await message.reply(
            "⚠️ <b>Usage:</b> <code>!addtoken &lt;token&gt;</code>\n"
            "Ek ya zyada tokens space/comma/newline se de do.\n"
            "🔒 MAIN (#1) CONFIG me alag — yahan 9 extra slots.",
            parse_mode=ParseMode.HTML)
    added, dup, full = 0, 0, 0
    for tok in cands:
        free = [i for i in range(1, MAX_TOKENS) if not TOKENS[i]]
        if not free:
            full += 1
            continue
        if tok in TOKENS or tok == MAIN_TOKEN:
            dup += 1
            continue
        slot = free[0]
        TOKENS[slot] = tok
        _RT["overrides"][slot - 1] = tok
        added += 1
        with suppress(Exception):
            b = await asyncio.wait_for(_init_single_bot(tok), timeout=10)
            if b is not None and b not in active_bots:
                active_bots.append(b)
    _RT["prefix"] = PREFIX
    _save_rt()
    with suppress(Exception):
        fbe.recalculate_pacing(max(1, len(active_bots)))
    await message.reply(
        f"✅ <b>Added:</b> <code>{added}</code> • <b>Skipped dup:</b> <code>{dup}</code> • "
        f"<b>Full:</b> <code>{full}</code>\n"
        f"📊 <b>Active slots:</b> <code>{sum(1 for t in TOKENS if t)}/{MAX_TOKENS}</code>\n"
        "💾 Saved in <code>nik_runtime.json</code> • restart par naye nodes bhi polling me.",
        parse_mode=ParseMode.HTML)

@router.message(DCommand("remtoken", "remtokens", "removetoken", "deltoken"), IsOwner())
async def cmd_remtoken(message: Message, command: CommandObject):
    raw = (command.args or "").strip()
    if not raw:
        return await message.reply(
            "⚠️ <b>Usage:</b> <code>!remtoken &lt;no&gt;</code> (ya pura token)\n"
            "Number <code>!tokens</code> se. <code>#1</code> = MAIN (protected).",
            parse_mode=ParseMode.HTML)
    slot = -1
    if raw.isdigit():
        n = int(raw)
        if n == 1:
            return await message.reply("🔒 MAIN hosting token (#1) remove nahi hota — CONFIG me edit karo.", parse_mode=ParseMode.HTML)
        if 2 <= n <= MAX_TOKENS:
            slot = n - 1
    else:
        m = re.findall(r"\d{6,12}:[A-Za-z0-9_-]{20,}", raw)
        tok = m[0] if m else raw
        if tok == MAIN_TOKEN:
            return await message.reply("🔒 MAIN hosting token remove nahi hota.", parse_mode=ParseMode.HTML)
        if tok in TOKENS:
            slot = TOKENS.index(tok)
    if slot < 1 or slot >= MAX_TOKENS or not TOKENS[slot]:
        return await message.reply("⚠️ Slot khaali / galat number — <code>!tokens</code> dekho.", parse_mode=ParseMode.HTML)
    removed = TOKENS[slot]
    TOKENS[slot] = ""
    _RT["overrides"][slot - 1] = ""      # in-file slot bhi mask ho jaye
    _RT["prefix"] = PREFIX
    _save_rt()
    b = LIVE_BOTS.pop(removed, None)
    if b is not None and b in active_bots:
        with suppress(Exception):
            active_bots.remove(b)
        with suppress(Exception):
            await b.session.close()
    with suppress(Exception):
        fbe.recalculate_pacing(max(1, len(active_bots)))
    await message.reply(
        f"🗑️ <b>Removed #{slot + 1}:</b> <code>{_mask_tok(removed)}</code>\n"
        f"📊 Ab <code>{sum(1 for t in TOKENS if t)}/{MAX_TOKENS}</code> active • 🔒 MAIN safe.",
        parse_mode=ParseMode.HTML)


# ==============================================================================
# 🧱 BIG-NC WALL + CLUSTER CONTROL  (photo wala "g faad" set)
#   ! fallback / ~ meta / PREFIX — sab yahan bhi DCommand se chalte hain
# ==============================================================================
_WEAVE_CMDS = {
    "bignc": "auto", "bigx": "auto", "xwall": "auto", "megan": "auto",
    "diamond": "diamond", "mesh": "mesh", "storm": "storm",
    "gemwall": "gem", "heartwall": "heart",
}

@router.message(DCommand(*_WEAVE_CMDS.keys()), IsSudo())
async def cmd_bignc(message: Message, command: CommandObject):
    variant = _WEAVE_CMDS.get(command.command, "auto")
    target = (command.args or "").strip()
    if not target and message.reply_to_message:
        target = (message.reply_to_message.text
                  or message.reply_to_message.caption or "")
    target = target.strip()[:120]
    if not target:
        return await message.reply(
            "⚠️ <b>Usage:</b> <code>!bignc &lt;text&gt;</code> — ya kisi msg pe reply karo.",
            parse_mode=ParseMode.HTML)
    spawn(message.chat.id, "big", big_nc_worker, target, variant)
    await message.reply(
        f"🧱 <b>BIG-NC ACTIVE</b> • <code>{BIGWALL.rows}</code> rows ✖ lattice\n"
        f"🎨 <b>Weave:</b> <code>{variant}</code> • 🎯 <code>{_hesc(target[:40])}</code>\n"
        "♻️ 24/7 persisted (restart pe auto-resume) • 🛑 <code>!dbignc</code>",
        parse_mode=ParseMode.HTML)

@router.message(DCommand("bigwall", "wall", "wallshot"), IsSudo())
async def cmd_bigwall(message: Message, command: CommandObject):
    target = (command.args or "").strip()
    if not target and message.reply_to_message:
        target = (message.reply_to_message.text
                  or message.reply_to_message.caption or "")
    target = (target or "NIKK").strip()[:60]
    wall = BIGWALL.build(target, int(time.time()) % 100000, "auto",
                         STATE.global_nc_count)
    bot = fbe.pick_best_nc_bot(active_bots, message.chat.id) if active_bots else None
    if bot is None and active_bots:
        bot = active_bots[0]
    if bot is None:
        return await message.reply("⚠️ Koi active node nahi hai.")
    asyncio.create_task(_fire_big_wall(bot, message.chat.id, wall))
    await message.reply(
        f"🧱 <b>Wall fired</b> • <code>{len(wall)}</code> chars • "
        f"<code>{BIGWALL.rows}</code> rows • weave <code>{BIGWALL.weave_for(0)}</code>",
        parse_mode=ParseMode.HTML)

@router.message(DCommand("dbignc", "dbig", "dwall", "stopbig",
                         "dultra", "dpnc", "dpack"), IsSudo())
async def cmd_dbignc(message: Message):
    STATE.cancel("big", message.chat.id, save=True)
    await message.reply("🛑 <b>BIG-NC wall stopped.</b>", parse_mode=ParseMode.HTML)

@router.message(DCommand("bigmenu", "newcmds", "bighelp"), IsSudo())
async def cmd_bigmenu(message: Message):
    await message.reply(
        "🧱 <b>BIG-NC &amp; CLUSTER ADD-ONS</b>\n"
        "◈ <code>!bignc &lt;txt&gt;</code> / <code>!bigx</code> / <code>!xwall</code> / <code>!megan</code> » 24/7 wall NC\n"
        "◈ <code>!diamond</code> <code>!mesh</code> <code>!storm</code> <code>!gemwall</code> <code>!heartwall</code> » weave lock\n"
        "◈ <code>!bigwall &lt;txt&gt;</code> » ek-shot full-screen wall · <code>!dbignc</code> » stop\n"
        "◈ <code>!leaveall</code> » sab bots sab GC se · <code>!gcs</code> » group list · <code>!nodes</code> » node table\n"
        "◈ <code>!addtoken</code> / <code>!remtoken</code> / <code>!tokens</code> / <code>~prefix ~</code> » config\n"
        "◈ <code>!ultra</code> / <code>!u1</code>-<code>!u10</code> / <code>!wallpack</code> / <code>!pblock</code> / <code>!ultranc</code>\n"
        "𒐫 <code>!nemo</code> / <code>!n1</code>-<code>!n10</code> / <code>!nemopack</code> / "
        "<code>!nemoblock</code> / <code>!nemoNC</code> / <code>!dnemo</code> » NEMO mega walls\n"
        "⚡ <code>!speed turbo</code> / <code>!whoop</code> » speed engine + double fire\n"
        "🔒 <code>!</code> hamesha chalega — prefix badalne ke baad bhi",
        parse_mode=ParseMode.HTML)


# ── 10 random very-big walls / full page-block ──────────────────────────────
_U_FAMILY = {}
for _i, _fam in enumerate(ULTRA.FAMILIES, 1):
    _U_FAMILY[f"u{_i}"] = _fam
    _U_FAMILY[f"ultra{_i}"] = _fam


@router.message(DCommand("ultra", "megawall", "u", "randomwall"), IsSudo())
async def cmd_ultra(message: Message, command: CommandObject):
    """Ek RANDOM very-big wall, har baar naye random emojis ke sath."""
    target = _ultra_target(message, command)
    bot = _pick_bot(message.chat.id)
    if bot is None:
        return await message.reply("⚠️ Koi active node nahi hai.")
    page = ULTRA.page_block(target, int(time.time()) % 100000, "random",
                            STATE.global_nc_count)
    asyncio.create_task(_fire_page(bot, message.chat.id, page))
    await message.reply(
        f"🧱 <b>CLASSIC WALL</b> • <code>{len(page):,}</code> chars page-block\n"
        f"🎲 {len(WALL.FAMILIES)} families · 𒐫~✖ weave · "
        f"🎯 <code>{_hesc(target[:40])}</code>\n"
        "📦 <code>!wallpack</code> » sab ek sath · 🛑 <code>!dbignc</code>",
        parse_mode=ParseMode.HTML)


@router.message(DCommand(*_U_FAMILY.keys()), IsSudo())
async def cmd_ufamily(message: Message, command: CommandObject):
    """!u1 .. !u10 / !ultra1 .. !ultra10 — apni pasand ki giant family lock karo."""
    fam = _U_FAMILY.get(command.command, "random")
    target = _ultra_target(message, command)
    bot = _pick_bot(message.chat.id)
    if bot is None:
        return await message.reply("⚠️ Koi active node nahi hai.")
    page = ULTRA.page_block(target, int(time.time()) % 100000, fam,
                            STATE.global_nc_count)
    asyncio.create_task(_fire_page(bot, message.chat.id, page))
    await message.reply(
        f"🧱 <b>{fam.upper()}</b> • <code>{len(page)}</code> chars • "
        f"<code>{ULTRA.RECIPES[fam][1]}</code> rows × "
        f"<code>{ULTRA.RECIPES[fam][0]}</code> cols",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("wallpack", "10wall", "tenwalls", "pack"), IsSudo())
async def cmd_wallpack(message: Message, command: CommandObject):
    """10 random very-big walls, ek ke baad ek, sab me alag random emojis."""
    target = _ultra_target(message, command)
    pages = ULTRA.pack(target, STATE.global_nc_count)
    cid = message.chat.id

    async def _run():
        for page in pages:
            bot = _pick_bot(cid)
            if bot is None:
                break
            await _fire_page(bot, cid, page)
            await asyncio.sleep(PACK_DELAY)

    asyncio.create_task(_run())
    await message.reply(
        f"📦 <b>WALL PACK</b> • <code>{len(pages)}</code> random very-big walls\n"
        f"📏 total <code>{sum(len(p) for p in pages):,}</code> chars • "
        f"🎯 <code>{_hesc(target[:40])}</code>\n"
        "🎲 har wall: alag family + alag random emoji palette",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("pblock", "pageblock", "fullnc", "dab"), IsSudo())
async def cmd_pblock(message: Message, command: CommandObject):
    """Pura page-block + title rename — kisi ki bhi NC dab jaye."""
    target = _ultra_target(message, command)
    tick = int(time.time()) % 100000
    bot = _pick_bot(message.chat.id)
    if bot is None:
        return await message.reply("⚠️ Koi active node nahi hai.")
    page = ULTRA.page_block(target, tick, "titan", STATE.global_nc_count)
    asyncio.create_task(_fire_page(bot, message.chat.id, page))
    asyncio.create_task(_fire_single_nc(bot, message.chat.id,
                                        ULTRA.title(target, tick)))
    await message.reply(
        f"📄 <b>FULL PAGE-BLOCK</b> • <code>{len(page)}</code> chars + 128-char title\n"
        "🫠 viewport bhar gaya → saamne wali NC scroll off\n"
        "♻️ 24/7 chahiye? <code>!ultranc &lt;txt&gt;</code>",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("ultranc", "pnc", "dabnc", "wallnc", "ultrawall"), IsSudo())
async def cmd_ultranc(message: Message, command: CommandObject):
    """24/7 ultra page-block NC (persisted, restart pe auto-resume)."""
    target = _ultra_target(message, command)
    if not target.strip():
        return await message.reply(
            "⚠️ <b>Usage:</b> <code>!ultranc &lt;text&gt;</code> — ya reply karo.",
            parse_mode=ParseMode.HTML)
    spawn(message.chat.id, "big", ultra_nc_worker, target, "ultra")
    await message.reply(
        "♾️ <b>ULTRA NC ACTIVE</b> • 24/7 title + random full page-block\n"
        f"🎲 10 families · random emojis · 🎯 <code>{_hesc(target[:40])}</code>\n"
        "🛑 <code>!dultra</code> / <code>!dbignc</code> • ♻️ restart pe auto-resume",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("whoop", "double", "wh"), IsSudo())
async def cmd_whoop(message: Message, command: CommandObject):
    """Ek shot: 2 bots se 2 classic mega page + title (instant screen wipe)."""
    target = _ultra_target(message, command)
    tick = int(time.time()) % 100000
    bots = [b for b in active_bots
            if fbe.is_ready_for_nc(b.id, message.chat.id)][:2]
    if len(bots) < 2:
        bots += [b for b in active_bots if b not in bots][:2 - len(bots)]
    if not bots:
        return await message.reply("⚠️ Koi active node nahi hai.")
    for i, b in enumerate(bots):
        asyncio.create_task(_fire_page(
            b, message.chat.id,
            WALL.page_block(target, tick + i, "random", STATE.global_nc_count)))
    asyncio.create_task(_fire_single_nc(bots[0], message.chat.id,
                                       WALL.title(target, tick)))
    await message.reply(
        f"💥 <b>WHOOP</b> • <code>{len(bots)}</code> bots × classic page + title\n"
        f"🎯 <code>{_hesc(target[:40])}</code>",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("speed", "turbo", "pace", "gati"), IsSudo())
async def cmd_speed(message: Message, command: CommandObject):
    """!speed turbo|max|safe|off — live pacing (page budget + flood bypass)."""
    mode = (command.args or "").strip().lower()
    fbe.set_mode(mode or "max", len(active_bots))
    fbe.recalculate_pacing(len(active_bots))
    STATE.delays["nc"] = fbe.cluster_nc_tick
    STATE.save_runtime_state()
    await message.reply(
        f"⚡ <b>SPEED → {fbe.throttle_mode.upper()}</b>\n"
        f"◈ tick <code>{_nc_delay(message.chat.id):.3f}s</code> · "
        f"page budget <code>{PAGE_INTERVAL}s</code>\n"
        f"◈ nodes <code>{len(active_bots)}</code> · "
        f"modes <code>turbo</code>/<code>max</code>/<code>safe</code>/<code>off</code>",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("fwdspam", "fspam", "fs", "fwdloop", "fsp"), IsSudo())


# ── FORWARD SPAM (phase-5) ─────────────────────────────────────────────────
@router.message(DCommand("fwdspam", "fspam", "fs", "fwdloop", "fsp"), IsSudo())
async def cmd_fwdspam(message: Message, command: CommandObject):
    """!fwdspam <text> — text loop | reply karke bhejo = us message ka forward loop.

    {n} likho to counter badhta jayega. Poora 10-bot cluster rotate hota hai.
    """
    rm = message.reply_to_message
    args = (command.args or "").strip()
    if rm is not None:
        kind = "copy" if command.command.lower() in ("fspam_copy",) else "forward"
        item = {"from_chat_id": rm.chat.id, "message_id": rm.message_id}
        spawn(message.chat.id, "fspam", forward_spam_worker, "",
              kind, item["from_chat_id"], item["message_id"], 0.30)
        return await message.reply(
            f"🔁 <b>FWD-SPAM LOOP</b> • replied {kind} har <code>0.12s</code>\n"
            f"🤖 <code>{len(active_bots)}</code> bots rotate · 🛑 <code>!dfspam</code>",
            parse_mode=ParseMode.HTML)
    if not args:
        return await message.reply(
            "⚠️ <b>Usage:</b> <code>!fwdspam &lt;text&gt;</code> ya kisi message pe "
            "reply karke <code>!fwdspam</code>\n"
            "<code>{n}</code> = auto counter (e.g. <code>!fwdspam NIK {n}</code>)",
            parse_mode=ParseMode.HTML)
    spawn(message.chat.id, "fspam", forward_spam_worker, args, "text", 0, 0, 0.12)
    await message.reply(
        f"💥 <b>FWD-SPAM ON</b> • <code>{len(active_bots)}</code> bots rotate\n"
        f"📝 <code>{_hesc(args[:44])}</code>\n"
        f"🛑 <code>!dfspam</code> / <code>!dfs</code>",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("dfspam", "dfsp", "dfs", "stopfspam"), IsSudo())
async def cmd_dfspam(message: Message):
    STATE.cancel("fspam", message.chat.id, save=True)
    await message.reply("🛑 <b>FWD-SPAM stopped.</b>", parse_mode=ParseMode.HTML)


# ── TAGDI NC (3 heavy styles, {target} + emoji + glyph) ────────────────────
@router.message(DCommand("tagdi", "tgd", "tagdiwall"), IsSudo())
async def cmd_tagdi(message: Message, command: CommandObject):
    """!tagdi <name> — 3 tagdi styles rotate, target naam hamesha screen pe."""
    target = _ultra_target(message, command, "")
    if not target.strip():
        return await message.reply(
            "⚠️ <b>Usage:</b> <code>!tagdi &lt;name&gt;</code> — ya reply karo.",
            parse_mode=ParseMode.HTML)
    spawn(message.chat.id, "nc", nc_cluster_worker, target, "tagdi", None, None)
    await message.reply(
        f"☠️ <b>TAGDI NC ACTIVE</b> • 3 heavy styles rotate\n"
        f"🎯 <code>{_hesc(target[:40])}</code> · emoji + glyph fill 128 chars\n"
        f"🔒 lock: <code>!tagdi1</code> <code>!tagdi2</code> <code>!tagdi3</code> · "
        f"🛑 <code>!dnc</code>",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("tagdi1", "tagdi2", "tagdi3", "tgd1", "tgd2", "tgd3"), IsSudo())
async def cmd_tagdi_lock(message: Message, command: CommandObject):
    key = re.sub(r"\D", "", command.command) or "1"
    target = _ultra_target(message, command, "")
    if not target.strip():
        return await message.reply("⚠️ <code>!tagdi1 &lt;name&gt;</code>", parse_mode=ParseMode.HTML)
    spawn(message.chat.id, "nc", nc_cluster_worker, target, "tagdi", f"tagdi{key}", None)
    sample = tagdi_title(target, int(time.time()), f"tagdi{key}")
    await message.reply(
        f"🔒 <b>TAGDI {key} LOCKED</b>\n<code>{_hesc(sample)}</code>\n"
        f"🛑 <code>!dnc</code>",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("tagdilist", "tgdlist"), IsSudo())
async def cmd_tagdilist(message: Message):
    body = "\n\n".join(
        f"<b>!tagdi{i}</b> → <code>{_hesc(tagdi_title('TARGET', i * 5, f'tagdi{i}'))}</code>"
        for i in (1, 2, 3))
    await message.reply(f"☠️ <b>3 TAGDI STYLES</b>\n\n{body}", parse_mode=ParseMode.HTML)


# ── classic wall aliases (naye registration) ───────────────────────────────
_W_FAMILY = {}
for _wi, _wf in enumerate(WALL.FAMILIES, 1):
    _W_FAMILY[f"w{_wi}"] = _wf
    _W_FAMILY[f"wall{_wi}"] = _wf


@router.message(DCommand(*_W_FAMILY.keys()), IsSudo())
async def cmd_wfamily(message: Message, command: CommandObject):
    fam = _W_FAMILY.get(command.command, "random")
    target = _ultra_target(message, command)
    bot = _pick_bot(message.chat.id)
    if bot is None:
        return await message.reply("⚠️ Koi active node nahi hai.")
    page = WALL.page_block(target, int(time.time()) % 100000, fam,
                           STATE.global_nc_count)
    asyncio.create_task(_fire_page(bot, message.chat.id, page))
    await message.reply(
        f"🧱 <b>{fam.upper()}</b> • <code>{len(page):,}</code> chars · "
        f"<code>{page.count(chr(10))}</code> rows · 𒐫~✖ classic weave",
        parse_mode=ParseMode.HTML)


@router.message(DCommand("wallmenu", "wmenu", "families"), IsSudo())
async def cmd_wallmenu(message: Message):
    lines = ["🧱 <b>12 CLASSIC WALL FAMILIES</b>", ""]
    for i, fam in enumerate(WALL.FAMILIES, 1):
        unit = WALL.RECIPES[fam][0]
        lines.append(f"<code>!w{i}</code> {fam.upper()} · unit <code>{unit}</code>")
    lines += ["", "🎲 <code>!wall</code> random · 📦 <code>!wallpack</code> 9 ek sath · "
              "📄 <code>!pblock</code> full page"]
    await message.reply("\n".join(lines), parse_mode=ParseMode.HTML)

# ── cluster control: leaveall / gcs / nodes ─────────────────────────────────
@router.message(DCommand("gcs", "groups", "chatlist"), IsSudo())
async def cmd_gcs(message: Message, command: CommandObject):
    chats = sorted(STATE.get_all_known_groups(None))
    if (command.args or "").strip().lower() == "raw":
        body = "\n".join(f"<code>{c}</code>" for c in chats) or "—"
    else:
        body = "\n".join(
            f"• <code>{c}</code> • {len(STATE.chat_bots.get(c, set()))} bots"
            for c in chats) or "—"
    await message.reply(
        f"🌍 <b>KNOWN GROUPS:</b> <code>{len(chats)}</code>\n\n{body}",
        parse_mode=ParseMode.HTML)

@router.message(DCommand("nodes", "botsall", "cluster"), IsSudo())
async def cmd_nodes(message: Message):
    lines = [f"🤖 <b>CLUSTER</b> • <code>{len(active_bots)}</code> nodes • "
             f"<code>{len(STATE.get_all_known_groups(None))}</code> GCs", ""]
    for i, b in enumerate(active_bots, 1):
        un = bot_usernames.get(b.id, "")
        cd = fbe.remaining_cooldown(b.id)
        state = f"⚠️ {cd:.1f}s" if cd > 0 else "✅ ok"
        lines.append(f"<code>{i:2d}.</code> @{un or b.id} • {state}")
    if not active_bots:
        lines.append("— koi node nahi (CONFIG me token daalo) —")
    await message.reply("\n".join(lines), parse_mode=ParseMode.HTML)

@router.message(DCommand("leaveall", "leaveallgc", "byeall"), IsSudo())
async def cmd_leaveall(message: Message, command: CommandObject):
    arg = (command.args or "").strip().lower()
    chats = sorted(STATE.get_all_known_groups(None))
    if arg in ("list", "dry", "preview"):
        return await message.reply(
            f"🔎 <b>leaveall preview:</b> <code>{len(chats)}</code> groups × "
            f"<code>{len(active_bots)}</code> bots.\n"
            "Confirm karne ke liye <code>!leaveall</code> bhejo.",
            parse_mode=ParseMode.HTML)
    if not chats:
        return await message.reply("ℹ️ Koi known group nahi hai.")
    msg = await message.reply(
        f"🚪 <b>leaveall</b> • {len(chats)} GC × {len(active_bots)} bots …",
        parse_mode=ParseMode.HTML)

    async def _run():
        STATE.stop_all(None, save=True)
        left = 0
        for cid in chats:
            for b in list(active_bots):
                with suppress(Exception):
                    await b.leave_chat(cid)
                    left += 1
                await asyncio.sleep(0.05)
            STATE.known_chats.discard(cid)
            STATE.chat_bots.pop(cid, None)
        STATE.save_runtime_state()
        with suppress(Exception):
            await msg.edit_text(
                f"✅ <b>leaveall done</b> • <code>{left}</code> leave calls • "
                f"<code>{len(chats)}</code> groups cleared.\n"
                "🔒 MAIN token safe — <code>!addtoken</code> se wapas manage karo.",
                parse_mode=ParseMode.HTML)

    asyncio.create_task(_run())

# ==============================================================================
# PRE-BUILT TUPLE RAM TITLE POOL GENERATOR (ZERO-OVERHEAD IN LOOP)
# ==============================================================================
def read_template() -> str:
    tmpl = "{base}"
    if not os.path.exists(TEMPLATE_FILE):
        with suppress(Exception):
            with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
                f.write(tmpl)
        return tmpl
    try:
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content:
            return tmpl
        try:
            data = json.loads(content)
            if isinstance(data, dict):
                return data.get("format", data.get("template", data.get("text", tmpl)))
            elif isinstance(data, list) and len(data) > 0:
                return str(data[0])
        except Exception:
            pass
        return content
    except Exception:
        return tmpl


# ==============================================================================
# TAGDI NC · 3 heavy styles (emoji + glyph + {target})  ->  !tagdi <name>
# ==============================================================================
TAGDI_EMOJI = ("💀", "👑", "🔥", "⚡", "☠️", "🩸", "💥", "🌟", "🌀", "🦾",
               "🖤", "💙", "🩵", "🧿", "🗿", "⚔️", "🪬", "🧨", "💎", "🔮")
TAGDI_GLYPH = ("𒐫", "𒈙", "𒀰", "𒁏", "✖", "⨯", "⤫", "⤬", "⫷", "⟡", "❖", "✦")


def tagdi_title(target: str, tick: int = 0, style_key: str = None) -> str:
    """3 tagdi styles — target naam har baar, emoji + glyph random."""
    t = (target or "NIKK").strip()[:18]
    pick = tick % 3 if not style_key else (int(style_key[-1]) - 1 if style_key[-1:].isdigit() else 0)
    pick = max(0, min(2, pick))
    e1 = TAGDI_EMOJI[tick % len(TAGDI_EMOJI)]
    e2 = TAGDI_EMOJI[(tick * 3 + 7) % len(TAGDI_EMOJI)]
    g1 = TAGDI_GLYPH[(tick + 2) % len(TAGDI_GLYPH)]
    g2 = TAGDI_GLYPH[(tick + 6) % len(TAGDI_GLYPH)]
    if pick == 0:
        core = f"{e1} {g1}~✖ {t} » ᴛɢᴅɪ « {t} ✖~{g2} {e2} "
        fill = (f"{g1}~✖" * 60)
    elif pick == 1:
        core = f"{e1} ✖ {t} ▓ ɴɪᴋ ▓ {t} ✖ {e2} "
        fill = (f"{g2}~✖" * 60)
    else:
        core = f"{e1} {g1} {t} » ɢғᴀᴀᴅ « {t} {g2} {e2} "
        fill = (f"{g1}{g2}✖" * 60)
    return (core + fill)[:128]

def generate_single_title(base: str, mode: str, tick_idx: int, style_key: str = None, tmpl_format: str = None):
    if mode == "tagdi":
        return tagdi_title(base, tick_idx, style_key)
    if mode == "mix":
        slot = tick_idx % 17
        if slot < 15:
            sk = STYLE_KEYS_TUPLE[slot]
            cfg = DYNAMIC_NC_MAP[sk]
            prefixes = cfg["prefixes"]
            front_emo = prefixes[(tick_idx // 17 + slot) % len(prefixes)]
            styled_text = cfg["fmt"].replace("{base}", base)
            wall_char = cfg["wall"]
            core = f"{front_emo} {styled_text} "
        elif slot == 15:
            emo_a = PREFIX_EMOJIS[tick_idx % len(PREFIX_EMOJIS)]
            core = f"{emo_a} ༺ {base} ༻ "
            wall_char = DEFAULT_WALL_CHAR
        else:
            emo_a = PREFIX_EMOJIS[tick_idx % len(PREFIX_EMOJIS)]
            emo_b = PREFIX_EMOJIS[(tick_idx + 7) % len(PREFIX_EMOJIS)]
            core = f"{emo_a} {base} {emo_b} "
            wall_char = DEFAULT_WALL_CHAR

        fill_len = max(0, 128 - len(core))
        return (core + (wall_char * fill_len))[:128]

    if mode == "style" and style_key in DYNAMIC_NC_MAP:
        cfg = DYNAMIC_NC_MAP[style_key]
        prefixes = cfg["prefixes"]
        front_emo = prefixes[tick_idx % len(prefixes)]
        styled_text = cfg["fmt"].replace("{base}", base)
        wall_char = cfg["wall"]
        core = f"{front_emo} {styled_text} "
    else:
        front_emo = PREFIX_EMOJIS[tick_idx % len(PREFIX_EMOJIS)]
        wall_char = DEFAULT_WALL_CHAR
        if mode == "nken":
            core = f"{front_emo} ༺ {base} ༻ "
        elif mode == "nemo":
            back_emo = PREFIX_EMOJIS[(tick_idx + 3) % len(PREFIX_EMOJIS)]
            core = f"{front_emo} {base} {back_emo} "
        elif mode == "template" and tmpl_format:
            clean_base = tmpl_format.replace("{base}", base).strip()
            core = f"{front_emo} {clean_base} "
        else:
            core = f"{front_emo} {base} "

    fill_len = max(0, 128 - len(core))
    return (core + (wall_char * fill_len))[:128]

def build_title_pool(base: str, mode: str, style_key: str = None, tmpl_format: str = None) -> Tuple[str, ...]:
    if mode == "tagdi":
        return tuple(tagdi_title(base, i, style_key) for i in range(60))
    pool_size = 170 if mode == "mix" else 100
    return tuple(generate_single_title(base, mode, i, style_key, tmpl_format) for i in range(pool_size))

# ==============================================================================
# HELPER TO EXTRACT BACKUP PAYLOAD FOR FORWARD LOOP
# ==============================================================================
def extract_message_backup(msg: Message) -> Dict[str, Any]:
    backup: Dict[str, Any] = {
        "text": msg.html_text if msg.text else None,
        "caption": msg.html_text if msg.caption else None,
        "type": "text",
        "file_id": None,
    }
    if msg.photo:
        backup["type"] = "photo"
        backup["file_id"] = msg.photo[-1].file_id
    elif msg.sticker:
        backup["type"] = "sticker"
        backup["file_id"] = msg.sticker.file_id
    elif msg.animation:
        backup["type"] = "gif"
        backup["file_id"] = msg.animation.file_id
    elif msg.video:
        backup["type"] = "video"
        backup["file_id"] = msg.video.file_id
    elif msg.voice:
        backup["type"] = "voice"
        backup["file_id"] = msg.voice.file_id
    elif msg.audio:
        backup["type"] = "audio"
        backup["file_id"] = msg.audio.file_id
    elif msg.document:
        backup["type"] = "document"
        backup["file_id"] = msg.document.file_id
    return backup

async def send_backup_snapshot(bot: Bot, chat_id: int, backup: Dict[str, Any]):
    btype = backup.get("type", "text")
    fid = backup.get("file_id")
    cap = backup.get("caption")
    txt = backup.get("text")

    if btype == "text" and txt:
        await bot.send_message(chat_id, txt, parse_mode=ParseMode.HTML)
    elif btype == "photo" and fid:
        await bot.send_photo(chat_id, fid, caption=cap, parse_mode=ParseMode.HTML)
    elif btype == "sticker" and fid:
        await bot.send_sticker(chat_id, fid)
    elif btype == "gif" and fid:
        await bot.send_animation(chat_id, fid, caption=cap, parse_mode=ParseMode.HTML)
    elif btype == "video" and fid:
        await bot.send_video(chat_id, fid, caption=cap, parse_mode=ParseMode.HTML)
    elif btype == "voice" and fid:
        await bot.send_voice(chat_id, fid, caption=cap, parse_mode=ParseMode.HTML)
    elif btype == "audio" and fid:
        await bot.send_audio(chat_id, fid, caption=cap, parse_mode=ParseMode.HTML)
    elif btype == "document" and fid:
        await bot.send_document(chat_id, fid, caption=cap, parse_mode=ParseMode.HTML)
    elif txt or cap:
        await bot.send_message(chat_id, txt or cap, parse_mode=ParseMode.HTML)

# ==============================================================================
# WORKERS (NON-STOP 24/7 PIPELINED NC & PRE-BOUND SPAM/FWD WORKERS)
# ==============================================================================
async def _fire_single_nc(bot: Bot, chat_id: int, title: str):
    """Non-blocking single title update task so network RTT never stalls the 10-bot pipeline."""
    bid = bot.id
    fbe.mark_started(bid)
    try:
        await bot.set_chat_title(chat_id, title)
        fbe.record_nc_success()
        STATE.record_nc_hit(chat_id)
    except TelegramRetryAfter as e:
        fbe.mark_flooded(bid, e.retry_after, chat_id=chat_id)
    except TelegramForbiddenError:
        fbe.mark_bot_missing_in_chat(chat_id, bid, duration=25.0)
    except TelegramBadRequest as e:
        err_msg = str(e).lower()
        if any(w in err_msg for w in ("chat not found", "not a member", "not enough rights", "have no rights", "chat_admin_required")):
            fbe.mark_bot_missing_in_chat(chat_id, bid, duration=25.0)
    except Exception:
        pass
    finally:
        fbe.mark_finished(bid)

async def nc_cluster_worker(chat_id: int, base: str, mode: str, style_key: str = None, tmpl_format: str = None):
    """
    Non-Stop 24/7 Zero-Drift 10-Bot LRU Pipelined Dispatcher:
    Runs infinitely regardless of opponent activity until manually stopped.
    """
    title_pool = build_title_pool(base, mode, style_key, tmpl_format)
    pool_len = len(title_pool)
    title_idx = 0
    create_task = asyncio.create_task
    sleep = asyncio.sleep
    monotonic = time.monotonic

    while True:
        try:
            total = len(active_bots)
            if total == 0:
                await sleep(0.5)
                continue

            selected_bot = fbe.pick_best_nc_bot(active_bots, chat_id)

            if selected_bot is not None:
                t0 = monotonic()
                new_title = title_pool[title_idx % pool_len]
                title_idx += 1
                create_task(_fire_single_nc(selected_bot, chat_id, new_title))

                if fbe.bypass_active:
                    healthy = max(1, fbe.count_healthy_bots_in_chat(active_bots, chat_id))
                    dynamic_tick = fbe.per_bot_nc_gap / healthy
                    base_tick = STATE.delays["nc"] if STATE.delays["nc"] > 0 else fbe.cluster_nc_tick
                    tick = max(base_tick, dynamic_tick)
                else:
                    tick = STATE.delays["nc"] if STATE.delays["nc"] > 0 else 0.08

                elapsed = monotonic() - t0
                rem_sleep = tick - elapsed
                if rem_sleep > 0:
                    await sleep(rem_sleep)
            else:
                await sleep(0.008)

        except asyncio.CancelledError:
            break
        except Exception:
            await sleep(0.02)


# ------------------------------------------------------------------------------
# BIG-NC DISPATCH: fast taunt-title rotation + periodic full-screen lattice wall
# ------------------------------------------------------------------------------
async def _fire_big_wall(bot: Bot, chat_id: int, wall: str):
    """Ek full-screen wall bhejo (GAP_100 viewport bhar deta hai)."""
    try:
        await bot.send_message(chat_id, compose_page(wall))
        STATE.record_nc_hit(chat_id)
    except TelegramRetryAfter as e:
        fbe.mark_flooded(bot.id, e.retry_after, chat_id=chat_id)
    except TelegramForbiddenError:
        fbe.mark_bot_missing_in_chat(chat_id, bot.id, duration=25.0)
    except Exception:
        pass


async def _fire_page(bot: Bot, chat_id: int, page: str):
    """Pehle se composed page-block bhejo (double-compose na ho)."""
    try:
        await bot.send_message(chat_id, page[:4000])
        STATE.record_nc_hit(chat_id)
    except TelegramRetryAfter as e:
        fbe.mark_flooded(bot.id, e.retry_after, chat_id=chat_id)
    except TelegramForbiddenError:
        fbe.mark_bot_missing_in_chat(chat_id, bot.id, duration=25.0)
    except Exception:
        pass


def _pick_bot(chat_id: int):
    bot = fbe.pick_best_nc_bot(active_bots, chat_id) if active_bots else None
    if bot is None and active_bots:
        bot = active_bots[0]
    return bot


def _ultra_target(message, command, default: str = "NIKK") -> str:
    txt = (command.args or "").strip() if command else ""
    if not txt and getattr(message, "reply_to_message", None):
        r = message.reply_to_message
        txt = (getattr(r, "text", None) or getattr(r, "caption", None) or "")
    return (txt.strip() or default)[:60]

def _nc_delay(chat_id: int) -> float:
    """SPEED: do clear modes.

    bypass ON  -> adaptive (per-bot gap / healthy nodes) : flood-safe, balanced
    bypass OFF -> RAW 0.03s flat : saamne wale ki NC ke against maximum pressure
    Page-blocks alag budget se chalte hain (_page_gate), isliye RAW pe bhi
    chat flood nahi hoti.
    """
    if not fbe.bypass_active:
        return 0.03                       # !fb off  = raw speed
    healthy = max(1, fbe.count_healthy_bots_in_chat(active_bots, chat_id))
    dyn = fbe.per_bot_nc_gap / healthy
    base = STATE.delays["nc"] if STATE.delays["nc"] > 0 else 0.10
    return max(0.02, max(base, dyn))


def _page_gate(chat_id: int) -> bool:
    """Per-chat page-block budget — yahi 429 flood ka asli ilaaj hai.

    Ek chat me har PAGE_INTERVAL sec me sirf ek heavy page (4,900 chars).
    Titles alag chalti hain, isliye NC dheemi nahi lagti par flood nahi hota.
    One-shot commands (!nemo / !nemopack / !whoop) is gate ko bypass karte hain.
    """
    now = time.monotonic()
    iv = PAGE_INTERVAL if fbe.bypass_active else min(PAGE_INTERVAL, 1.20)
    if (now - _PAGE_LAST.get(chat_id, 0.0)) < iv:
        return False
    _PAGE_LAST[chat_id] = now
    return True


async def big_nc_worker(chat_id: int, target: str, variant: str = "auto",
                        wall_every: int = 8):
    """24/7 BIG-NC: title har tick, giant lattice wall har N tick."""
    tick = 0
    create_task = asyncio.create_task
    sleep = asyncio.sleep
    while True:
        try:
            if not active_bots:
                await sleep(0.5)
                continue
            bot = fbe.pick_best_nc_bot(active_bots, chat_id)
            if bot is None:
                await sleep(0.008)
                continue
            create_task(_fire_single_nc(bot, chat_id, BIGWALL.title(target, tick)))
            if wall_every and tick % wall_every == 0:
                if variant in BIGWALL.WEAVES:
                    wall = BIGWALL.build(target, tick, variant, STATE.global_nc_count)
                elif variant in NEMO.RECIPES:
                    if _page_gate(chat_id):
                        create_task(_fire_page(bot, chat_id,
                                               NEMO.page_block(target, tick, variant,
                                                               STATE.global_nc_count)))
                    wall = None
                else:
                    wall = ULTRA.build(target, tick, variant, STATE.global_nc_count)
                if wall and _page_gate(chat_id):
                    create_task(_fire_big_wall(bot, chat_id, wall))
            tick += 1
            await sleep(_nc_delay(chat_id))
        except asyncio.CancelledError:
            break
        except Exception:
            await sleep(0.02)


async def nemo_nc_worker(chat_id: int, target: str, variant: str = "nemo",
                         wall_every: int = 1):
    """24/7 NEMO 𒐫 NC: har tick naya title + nemo/ultra alternating page-block."""
    tick = 0
    create_task = asyncio.create_task
    sleep = asyncio.sleep
    while True:
        try:
            if not active_bots:
                await sleep(IDLE_SLEEP * 10)
                continue
            bot = fbe.pick_best_nc_bot(active_bots, chat_id)
            if bot is None:
                await sleep(0.008)
                continue
            create_task(_fire_single_nc(bot, chat_id, NEMO.title(target, tick)))
            if wall_every and tick % wall_every == 0:
                fam = variant if variant in NEMO.RECIPES else "random"
                if _page_gate(chat_id):
                    if fam == "random" and tick % 2:
                        page = ULTRA.page_block(target, tick, "random",
                                                STATE.global_nc_count)
                    else:
                        page = NEMO.page_block(target, tick, fam,
                                               STATE.global_nc_count)
                    create_task(_fire_page(bot, chat_id, page))
                if tick % 8 == 0 and _page_gate(chat_id):
                    bot2 = fbe.pick_best_nc_bot(active_bots, chat_id)
                    if bot2 is not None and bot2.id != bot.id:
                        create_task(_fire_page(bot2, chat_id,
                                               NEMO.page_block(target, tick + 1,
                                                               "random",
                                                               STATE.global_nc_count)))
            tick += 1
            await sleep(_nc_delay(chat_id))
        except asyncio.CancelledError:
            break
        except Exception:
            await sleep(0.02)


async def ultra_nc_worker(chat_id: int, target: str, variant: str = "ultra",
                          wall_every: int = 1):
    """24/7 ULTRA: har tick naya 128-char title + naya random full page-block.

    Title + giant wall ek sath chalte hain, isliye saamne wala kitna bhi NC
    badle, uski rename card screen pe tikti hi nahi.
    """
    tick = 0
    create_task = asyncio.create_task
    sleep = asyncio.sleep
    while True:
        try:
            if not active_bots:
                await sleep(IDLE_SLEEP)
                continue
            bot = fbe.pick_best_nc_bot(active_bots, chat_id)
            if bot is None:
                await sleep(0.008)
                continue
            create_task(_fire_single_nc(bot, chat_id, ULTRA.title(target, tick)))
            if wall_every and tick % wall_every == 0 and _page_gate(chat_id):
                page = ULTRA.page_block(target, tick, "random",
                                        STATE.global_nc_count)
                create_task(_fire_page(bot, chat_id, page))
            tick += 1
            await sleep(_nc_delay(chat_id))
        except asyncio.CancelledError:
            break
        except Exception:
            await sleep(0.02)


async def _fire_single_forward(bot: Bot, chat_id: int, item: Dict[str, Any]):
    bid = bot.id
    from_cid = int(item["from_chat_id"])
    msg_id = int(item["message_id"])
    use_copy = bool(item.get("copy", False))
    backup = item.get("backup")

    try:
        if use_copy:
            await bot.copy_message(chat_id=chat_id, from_chat_id=from_cid, message_id=msg_id)
        else:
            await bot.forward_message(chat_id=chat_id, from_chat_id=from_cid, message_id=msg_id)
    except TelegramRetryAfter as e:
        fbe.mark_flooded(bid, e.retry_after, chat_id=chat_id)
    except TelegramForbiddenError:
        fbe.mark_bot_missing_in_chat(chat_id, bid, duration=25.0)
    except TelegramBadRequest as e:
        err_msg = str(e).lower()
        if any(w in err_msg for w in ("chat not found", "not a member", "have no rights", "not enough rights")):
            fbe.mark_bot_missing_in_chat(chat_id, bid, duration=25.0)
        elif backup:
            with suppress(Exception):
                await send_backup_snapshot(bot, chat_id, backup)
    except Exception:
        pass


# ------------------------------------------------------------------------------
# FORWARD SPAM (text ya replied message ka repeat loop, har bot rotate)
# ------------------------------------------------------------------------------
async def forward_spam_worker(chat_id: int, text: str, kind: str = "text",
                              from_chat: int = 0, msg_id: int = 0,
                              delay: float = 0.15):
    """Har tick ek bot se text-spam ya forward/copy — poora cluster use hota hai."""
    idx = 0
    sleep = asyncio.sleep
    while True:
        try:
            if not active_bots:
                await sleep(IDLE_SLEEP * 10)
                continue
            bot = fbe.pick_best_nc_bot(active_bots, chat_id)
            if bot is None:
                await sleep(0.02)
                continue
            if kind == "forward" and from_chat and msg_id:
                asyncio.create_task(_fire_single_forward(bot, chat_id, {
                    "from_chat_id": from_chat, "message_id": msg_id,
                    "copy": False, "backup": None,
                }))
            elif kind == "copy" and from_chat and msg_id:
                asyncio.create_task(_fire_single_forward(bot, chat_id, {
                    "from_chat_id": from_chat, "message_id": msg_id,
                    "copy": True, "backup": None,
                }))
            else:
                idx += 1
                asyncio.create_task(_fire_fspam_text(bot, chat_id, text, idx))
            await sleep(max(0.08, delay))
        except asyncio.CancelledError:
            break
        except Exception:
            await sleep(0.05)


async def _fire_fspam_text(bot: Bot, chat_id: int, text: str, n: int):
    body = text
    if "{n}" in body:
        body = body.replace("{n}", str(n))
    try:
        await bot.send_message(chat_id, body[:4000])
        STATE.record_nc_hit(chat_id)
    except TelegramRetryAfter as e:
        fbe.mark_flooded(bot.id, e.retry_after, chat_id=chat_id)
    except TelegramForbiddenError:
        fbe.mark_bot_missing_in_chat(chat_id, bot.id, duration=25.0)
    except Exception:
        pass

async def fwd_cluster_worker(chat_id: int):
    item_idx = 0
    bot_idx = 0
    create_task = asyncio.create_task
    sleep = asyncio.sleep

    while True:
        try:
            items = STATE.fwd_queue.get(chat_id)
            total = len(active_bots)
            if not items or total == 0:
                await sleep(0.4)
                continue

            selected_bot = None
            for _ in range(total):
                candidate = active_bots[bot_idx % total]
                bot_idx += 1
                if not fbe.is_flooded(candidate.id) and fbe.is_bot_usable_in_chat(chat_id, candidate.id):
                    selected_bot = candidate
                    break

            if selected_bot is not None:
                await bq.wait(selected_bot.id)
                item = items[item_idx % len(items)]
                item_idx += 1
                create_task(_fire_single_forward(selected_bot, chat_id, item))
                await sleep(max(0.08, STATE.delays["fwd"]))
            else:
                await sleep(0.02)

        except asyncio.CancelledError:
            break
        except Exception:
            await sleep(0.05)

async def spam_worker(bot: Bot, chat_id: int, text: str, mode: str, tmpl_format=None, initial_delay_ms: int = 0):
    if initial_delay_ms > 0:
        await asyncio.sleep(initial_delay_ms / 1000.0)
    bid = bot.id
    delay_key = "rspm" if mode in ["rs", "ns"] else "spam"
    send_msg = bot.send_message
    html_mode = ParseMode.HTML
    sleep = asyncio.sleep
    choice = random.choice
    raid_tuple = RAID_TEXTS
    is_raid = mode in ["rs", "ns"]
    is_tmpl = (mode == "template" and bool(tmpl_format))
    static_msg = f"<b>{text}{GAP_100}{text}</b>"

    while True:
        try:
            await bq.wait(bid)
            if fbe.is_flooded(bid) or not fbe.is_bot_usable_in_chat(chat_id, bid):
                await sleep(0.3)
                continue

            if is_tmpl:
                chosen_tmpl = choice(tmpl_format) if isinstance(tmpl_format, list) else tmpl_format
                base_msg = chosen_tmpl.replace("{base}", text)
                msg = f"<b>{base_msg}{GAP_100}{base_msg}</b>"
            elif is_raid:
                base_msg = f"{text} {choice(raid_tuple)}"
                msg = f"<b>{base_msg}{GAP_100}{base_msg}</b>"
            else:
                msg = static_msg

            await send_msg(chat_id, msg, parse_mode=html_mode)

            dly = STATE.delays[delay_key]
            if dly > 0:
                await sleep(dly)

        except TelegramRetryAfter as e:
            fbe.mark_flooded(bid, e.retry_after, chat_id=chat_id)
            await sleep(0.1)
        except (TelegramForbiddenError, TelegramBadRequest) as e:
            if any(w in str(e).lower() for w in ("chat not found", "not a member", "forbidden", "have no rights")):
                fbe.mark_bot_missing_in_chat(chat_id, bid, duration=25.0)
            await sleep(0.4)
        except asyncio.CancelledError:
            break
        except Exception as e:
            log_event("error", f"SPAM-{bid}", str(e))
            await sleep(0.4)

async def pfp_worker(bot: Bot, chat_id: int, is_global: bool = False, initial_delay_ms: int = 0):
    if initial_delay_ms > 0:
        await asyncio.sleep(initial_delay_ms / 1000.0)
    bid = bot.id
    idx = 0
    m_cat = "gpfp" if is_global else "pfp"

    while True:
        try:
            if fbe.is_flooded(bid) or (not is_global and not fbe.is_bot_usable_in_chat(chat_id, bid)):
                await asyncio.sleep(0.8)
                continue

            items = STATE.pfp_cache[m_cat].get(chat_id)
            if not items:
                await asyncio.sleep(1.5)
                continue

            raw_bytes = items[idx % len(items)]
            if is_global:
                await set_bot_profile_photo_safe(bot, raw_bytes)
            else:
                photo_input = BufferedInputFile(raw_bytes, "pfp.jpg")
                await bot.set_chat_photo(chat_id, photo=photo_input)

            await asyncio.sleep(STATE.delays[m_cat])
            idx += 1

        except TelegramRetryAfter as e:
            fbe.mark_flooded(bid, e.retry_after, chat_id=None if is_global else chat_id)
            await asyncio.sleep(0.4)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.8)

async def media_worker(bot: Bot, chat_id: int, mtype: str, initial_delay_ms: int = 0):
    if initial_delay_ms > 0:
        await asyncio.sleep(initial_delay_ms / 1000.0)
    bid = bot.id
    idx = 0
    while True:
        try:
            if fbe.is_flooded(bid) or not fbe.is_bot_usable_in_chat(chat_id, bid):
                await asyncio.sleep(0.4)
                continue

            items = STATE.media[mtype].get(chat_id)
            if not items:
                await asyncio.sleep(1.5)
                continue

            await bq.wait(bid)
            fid = items[idx % len(items)]
            if mtype == "sticker":
                await bot.send_sticker(chat_id, fid)
            elif mtype == "gif":
                await bot.send_animation(chat_id, fid)
            elif mtype == "photo":
                await bot.send_photo(chat_id, fid)
            elif mtype == "voice":
                await bot.send_voice(chat_id, fid)

            await asyncio.sleep(STATE.delays["media"])
            idx += 1

        except TelegramRetryAfter as e:
            fbe.mark_flooded(bid, e.retry_after, chat_id=chat_id)
            await asyncio.sleep(0.15)
        except asyncio.CancelledError:
            break
        except Exception:
            await asyncio.sleep(0.4)

async def slide_worker(bot: Bot, chat_id: int, uid: int, name: str, text: str = None, initial_delay_ms: int = 0):
    if initial_delay_ms > 0:
        await asyncio.sleep(initial_delay_ms / 1000.0)
    bid = bot.id
    mention = f'<a href="tg://user?id={uid}">{name}</a>'
    send_msg = bot.send_message
    html_mode = ParseMode.HTML
    sleep = asyncio.sleep
    choice = random.choice
    raid_tuple = RAID_TEXTS
    emo_tuple = EMOJIS

    while True:
        try:
            if fbe.is_flooded(bid) or not fbe.is_bot_usable_in_chat(chat_id, bid):
                await sleep(0.3)
                continue

            await bq.wait(bid)
            base_msg = f"{mention} {text if text else choice(raid_tuple)} {choice(emo_tuple)}"
            msg = f"{base_msg}{GAP_100}{base_msg}"

            await send_msg(chat_id, msg, parse_mode=html_mode)
            dly = STATE.delays["slide"]
            if dly > 0:
                await sleep(dly)

        except TelegramRetryAfter as e:
            fbe.mark_flooded(bid, e.retry_after, chat_id=chat_id)
            await sleep(0.15)
        except asyncio.CancelledError:
            break
        except Exception:
            await sleep(0.4)

def spawn(cid: int, cat: str, func, *args, save: bool = True):
    STATE.cancel(cat, cid, save=False)
    if cid < 0:
        STATE.known_chats.add(cid)

    cid_str = str(cid)
    if cat == "nc":
        base = args[0] if len(args) > 0 else ""
        mode = args[1] if len(args) > 1 else "n"
        style_key = args[2] if len(args) > 2 else None
        tmpl_format = args[3] if len(args) > 3 else None
        if base:
            STATE.nc_target_names[cid] = base
        STATE.persisted_tasks["nc"][cid_str] = {
            "base": base, "mode": mode, "style_key": style_key, "tmpl_format": tmpl_format
        }
    elif cat == "big":
        target = args[0] if len(args) > 0 else ""
        variant = args[1] if len(args) > 1 else "auto"
        if target:
            STATE.nc_target_names[cid] = target
        STATE.persisted_tasks["big"][cid_str] = {
            "target": target, "variant": variant
        }
    elif cat == "spam":
        text = args[0] if len(args) > 0 else ""
        mode = args[1] if len(args) > 1 else "s"
        tmpl_format = args[2] if len(args) > 2 else None
        if text and cid not in STATE.nc_target_names:
            STATE.nc_target_names[cid] = text
        STATE.persisted_tasks["spam"][cid_str] = {
            "text": text, "mode": mode, "tmpl_format": tmpl_format
        }
    elif cat == "fwd":
        STATE.persisted_tasks["fwd"][cid_str] = {
            "active": True,
            "count": len(STATE.fwd_queue.get(cid, []))
        }
    elif cat == "fspam":
        STATE.persisted_tasks.setdefault("fspam", {})[cid_str] = {
            "text": args[0] if len(args) > 0 else "",
            "kind": args[1] if len(args) > 1 else "text",
            "from_chat": args[2] if len(args) > 2 else 0,
            "msg_id": args[3] if len(args) > 3 else 0,
            "delay": args[4] if len(args) > 4 else 0.15,
        }
    elif cat == "slide":
        uid = args[0] if len(args) > 0 else 0
        name = args[1] if len(args) > 1 else "User"
        text = args[2] if len(args) > 2 else None
        STATE.persisted_tasks["slide"][cid_str] = {
            "uid": uid, "name": name, "text": text
        }
    elif cat == "media":
        mtype = args[0] if len(args) > 0 else "sticker"
        STATE.persisted_tasks["media"][cid_str] = {"mtype": mtype}
    elif cat in ("pfp", "gpfp"):
        is_glob = args[0] if len(args) > 0 else (cat == "gpfp")
        STATE.persisted_tasks[cat][cid_str] = {"is_global": is_glob}

    if save:
        STATE.save_runtime_state()

    if cat == "nc":
        STATE.add_task(cat, cid, asyncio.create_task(nc_cluster_worker(cid, *args)))
        log_event("info", "SPAWN", f"10-BOT PIPELINED MEGA-NC deployed via {len(active_bots)} nodes on {cid}")
        return

    if cat == "big":
        STATE.add_task(cat, cid, asyncio.create_task((func or big_nc_worker)(cid, *args)))
        log_event("info", "SPAWN", f"BIG-NC WALL deployed on {cid} ({len(active_bots)} nodes)")
        return

    if cat == "fwd":
        STATE.add_task(cat, cid, asyncio.create_task(fwd_cluster_worker(cid)))
        log_event("info", "SPAWN", f"Repeat-Forward Loop deployed on Chat {cid}")
        return

    if cat == "fspam":
        STATE.add_task(cat, cid, asyncio.create_task(forward_spam_worker(cid, *args)))
        log_event("info", "SPAWN", f"FWD-SPAM loop deployed on Chat {cid}")
        return

    for idx, b in enumerate(active_bots):
        initial_delay = idx * 80
        STATE.add_task(cat, cid, asyncio.create_task(func(b, cid, *args, initial_delay_ms=initial_delay)))

# ==============================================================================
# MANUAL !GAMEOVER EXECUTION
# ==============================================================================
async def send_gameover_media_to_gc(cid: int, caption_html: str):
    for b in active_bots:
        if fbe.is_flooded(b.id) or not fbe.is_bot_usable_in_chat(cid, b.id):
            continue
        try:
            if STATE.gameover_gif_bytes:
                gif_input = BufferedInputFile(STATE.gameover_gif_bytes, "gameover.mp4")
                await b.send_animation(cid, animation=gif_input, caption=caption_html, parse_mode=ParseMode.HTML)
            else:
                await b.send_animation(cid, animation=DEFAULT_GAMEOVER_GIF_URL, caption=caption_html, parse_mode=ParseMode.HTML)
            return True
        except Exception:
            with suppress(Exception):
                await b.send_message(cid, caption_html, parse_mode=ParseMode.HTML)
                return True
    return False

async def execute_gameover(cid: int, custom_target: Optional[str] = None):
    cid_str = str(cid)
    nc_info = STATE.persisted_tasks.get("nc", {}).get(cid_str)
    spm_info = STATE.persisted_tasks.get("spam", {}).get(cid_str)

    target_name = (
        custom_target
        or (nc_info.get("base") if nc_info else None)
        or STATE.nc_target_names.get(cid)
        or (spm_info.get("text") if spm_info else None)
        or "OPPONENT"
    )
    STATE.nc_target_names[cid] = target_name

    for cat in ("nc", "spam", "fwd", "slide", "media"):
        STATE.cancel(cat, cid, save=False)
    STATE.save_runtime_state()

    now_ist = get_ist_now()
    date_str = now_ist.strftime("%d/%m/%Y")
    time_str = now_ist.strftime("%I:%M:%S %p IST")

    gameover_line = f"{target_name} Gameover by @Nikkkwa (Nik)"
    caption_html = (
        f"╭━━━〘 🏁 <b>ＧＡＭＥ ＯＶＥＲ</b> 🏁 〙━━━╮\n"
        f"┃ 🏆 <b>{gameover_line}</b>\n"
        f"┃ 📅 <b>Date (IST):</b> <code>{date_str}</code>\n"
        f"┃ ⏰ <b>Time (IST):</b> <code>{time_str}</code>\n"
        f"╰━━━〘 👑 <b>@Nikkkwa (Nik)</b> 〙━━━╯"
    )

    await send_gameover_media_to_gc(cid, caption_html)

    final_core = f"🏆 {gameover_line} "
    fill_len = max(0, 128 - len(final_core))
    final_title = (final_core + (DEFAULT_WALL_CHAR * fill_len))[:128]
    for b in active_bots:
        if not fbe.is_flooded(b.id) and fbe.is_bot_usable_in_chat(cid, b.id):
            with suppress(Exception):
                await b.set_chat_title(cid, final_title)
                break

    chat_title, invite_link = await get_gc_invite_and_title(cid)
    owner_report = (
        f"🏁 <b>GAME OVER REPORT (IST)</b> 🏁\n\n"
        f"🎯 <b>Result:</b> <code>{gameover_line}</code>\n"
        f"🏷️ <b>Group:</b> <b>{chat_title}</b> (<code>{cid}</code>)\n"
        f"🔗 <b>GC Link:</b> {invite_link}\n"
        f"📅 <b>Date & Time:</b> <code>{date_str} | {time_str}</code>"
    )
    await notify_owner_dm(owner_report)
    log_event("info", "GAMEOVER", f"{gameover_line} in {cid}")

async def restore_persisted_tasks():
    restored_count = 0

    for cid_str, info in list(STATE.persisted_tasks.get("big", {}).items()):
        cid = int(cid_str)
        _variant = info.get("variant", "auto")
        if _variant == "ultra" or _variant == "whoop":
            worker = ultra_nc_worker
        elif _variant in NEMO.RECIPES or _variant in ("nemo", "nemoNC"):
            worker = nemo_nc_worker
        else:
            worker = big_nc_worker
        spawn(cid, "big", worker,
              info.get("target", ""), info.get("variant", "auto"),
              save=False)
        restored_count += 1

    for cid_str, info in list(STATE.persisted_tasks.get("nc", {}).items()):
        cid = int(cid_str)
        spawn(
            cid, "nc", nc_cluster_worker,
            info.get("base", ""), info.get("mode", "n"),
            info.get("style_key"), info.get("tmpl_format"),
            save=False
        )
        restored_count += 1

    for cid_str, info in list(STATE.persisted_tasks.get("fspam", {}).items()):
        cid = int(cid_str)
        spawn(cid, "fspam", forward_spam_worker,
              info.get("text", ""), info.get("kind", "text"),
              info.get("from_chat", 0), info.get("msg_id", 0),
              info.get("delay", 0.15), save=False)
        restored_count += 1

    for cid_str, info in list(STATE.persisted_tasks.get("spam", {}).items()):
        cid = int(cid_str)
        spawn(
            cid, "spam", spam_worker,
            info.get("text", ""), info.get("mode", "s"),
            info.get("tmpl_format"),
            save=False
        )
        restored_count += 1

    for cid_str, info in list(STATE.persisted_tasks.get("fwd", {}).items()):
        cid = int(cid_str)
        if STATE.fwd_queue.get(cid):
            spawn(cid, "fwd", fwd_cluster_worker, save=False)
            restored_count += 1

    for cid_str, info in list(STATE.persisted_tasks.get("slide", {}).items()):
        cid = int(cid_str)
        spawn(
            cid, "slide", slide_worker,
            info.get("uid", 0), info.get("name", "User"),
            info.get("text"),
            save=False
        )
        restored_count += 1

    for cid_str, info in list(STATE.persisted_tasks.get("media", {}).items()):
        cid = int(cid_str)
        mtype = info.get("mtype", "sticker")
        if STATE.media.get(mtype, {}).get(cid):
            spawn(cid, "media", media_worker, mtype, save=False)
            restored_count += 1

    for cat in ("pfp", "gpfp"):
        for cid_str, info in list(STATE.persisted_tasks.get(cat, {}).items()):
            cid = int(cid_str)
            if STATE.pfp_cache.get(cat, {}).get(cid):
                spawn(cid, cat, pfp_worker, info.get("is_global", cat == "gpfp"), save=False)
                restored_count += 1

    if restored_count > 0:
        log_event("info", "AUTO-RESUME", f"Resumed {restored_count} GC task(s) automatically after boot!")

async def task_watchdog_daemon():
    while True:
        await asyncio.sleep(3)
        with suppress(Exception):
            if not active_bots:
                continue
            for cid_str, info in list(STATE.persisted_tasks.get("nc", {}).items()):
                cid = int(cid_str)
                active_set = STATE.tasks.get("nc", {}).get(cid, set())
                if not any(not t.done() for t in active_set):
                    log_event("warn", "WATCHDOG", f"NC task in {cid} died. Respawning immediately!")
                    spawn(
                        cid, "nc", nc_cluster_worker,
                        info.get("base", ""), info.get("mode", "n"),
                        info.get("style_key"), info.get("tmpl_format"),
                        save=False
                    )
            for cid_str, info in list(STATE.persisted_tasks.get("spam", {}).items()):
                cid = int(cid_str)
                active_set = STATE.tasks.get("spam", {}).get(cid, set())
                if not any(not t.done() for t in active_set):
                    log_event("warn", "WATCHDOG", f"Spam task in {cid} died. Respawning immediately!")
                    spawn(
                        cid, "spam", spam_worker,
                        info.get("text", ""), info.get("mode", "s"),
                        info.get("tmpl_format"),
                        save=False
                    )
            for cid_str in list(STATE.persisted_tasks.get("fwd", {}).keys()):
                cid = int(cid_str)
                if STATE.fwd_queue.get(cid):
                    active_set = STATE.tasks.get("fwd", {}).get(cid, set())
                    if not any(not t.done() for t in active_set):
                        log_event("warn", "WATCHDOG", f"Forward task in {cid} died. Respawning immediately!")
                        spawn(cid, "fwd", fwd_cluster_worker, save=False)

# ==============================================================================
# HELPER FUNCTIONS FOR FIXED PROMOTE & MUTE
# ==============================================================================
async def smart_promote(chat_id: int, target_user_id: int) -> bool:
    for promoter_bot in active_bots:
        if fbe.is_flooded(promoter_bot.id) or not fbe.is_bot_usable_in_chat(chat_id, promoter_bot.id):
            continue
        try:
            await promoter_bot.promote_chat_member(
                chat_id=chat_id,
                user_id=target_user_id,
                can_manage_chat=True,
                can_delete_messages=True,
                can_manage_video_chats=True,
                can_restrict_members=True,
                can_promote_members=True,
                can_change_info=True,
                can_invite_users=True,
                can_pin_messages=True,
                can_manage_topics=True,
            )
            return True
        except TelegramRetryAfter as e:
            fbe.mark_flooded(promoter_bot.id, e.retry_after)
            continue
        except TelegramBadRequest:
            try:
                await promoter_bot.promote_chat_member(
                    chat_id=chat_id,
                    user_id=target_user_id,
                    can_manage_chat=True,
                    can_delete_messages=True,
                    can_manage_video_chats=True,
                    can_restrict_members=True,
                    can_change_info=True,
                    can_invite_users=True,
                    can_pin_messages=True,
                )
                return True
            except Exception:
                continue
        except Exception:
            continue
    return False

async def smart_restrict(chat_id: int, target_user_id: int, mute: bool) -> bool:
    perms = ChatPermissions(
        can_send_messages=not mute,
        can_send_audios=not mute,
        can_send_documents=not mute,
        can_send_photos=not mute,
        can_send_videos=not mute,
        can_send_video_notes=not mute,
        can_send_voice_notes=not mute,
        can_send_polls=not mute,
        can_send_other_messages=not mute,
        can_add_web_page_previews=not mute,
    )
    for b in active_bots:
        if fbe.is_flooded(b.id) or not fbe.is_bot_usable_in_chat(chat_id, b.id):
            continue
        try:
            await b.restrict_chat_member(
                chat_id=chat_id,
                user_id=target_user_id,
                permissions=perms,
                use_independent_chat_permissions=True
            )
            return True
        except TelegramBadRequest as e:
            if mute and ("administrator" in str(e).lower() or "right" in str(e).lower()):
                with suppress(Exception):
                    await b.promote_chat_member(
                        chat_id=chat_id,
                        user_id=target_user_id,
                        can_manage_chat=False,
                        can_delete_messages=False,
                        can_manage_video_chats=False,
                        can_restrict_members=False,
                        can_promote_members=False,
                        can_change_info=False,
                        can_invite_users=False,
                        can_pin_messages=False,
                    )
                    await b.restrict_chat_member(
                        chat_id=chat_id,
                        user_id=target_user_id,
                        permissions=perms,
                        use_independent_chat_permissions=True
                    )
                    return True
        except TelegramRetryAfter as e:
            fbe.mark_flooded(b.id, e.retry_after)
        except Exception:
            continue
    return False

# ==============================================================================
# MULTI-CATEGORY SMALL CAPS MENU (!menu / !help)
# ==============================================================================
@router.message(DCommand("menu", "help", prefix="!"), IsSudo())
async def cmd_menu(message: Message):
    up = len(active_bots)
    menu_text = (
        f"👑 <b>ɴɪᴋ ᴛɪᴛᴀɴ · ᴄʟᴀssɪᴄ ᴇᴅɪᴛɪᴏɴ</b> 👑\n"
        f"<i>@Nikkkwa (Nik) · 𒐫~✖ weave · runtime walls</i>\n"
        f"📊 nodes <code>{up}/10</code> · tick <code>{_nc_delay(message.chat.id):.2f}s</code> · "
        f"page <code>{PAGE_INTERVAL:.1f}s</code> · Hz <code>{fbe.get_live_hz()}</code>\n\n"
        f"𝟏 ⚡ <b>NC — target ke against</b>\n"
        f"◈ <code>!nc &lt;name&gt;</code> » full NC · <code>!umix &lt;name&gt;</code> » 15-style mix\n"
        f"◈ <code>!tagdi &lt;name&gt;</code> » 3 tagdi styles (emoji+glyph) · "
        f"<code>!tagdi1..3</code> lock · <code>!tagdilist</code>\n"
        f"◈ <code>!dnc</code> » stop\n\n"
        f"𝟐 🧱 <b>WALLS — classic 𒐫~✖ (very big)</b>\n"
        f"◈ <code>!wall &lt;name&gt;</code> / <code>!bigwall</code> » ek giant wall\n"
        f"◈ <code>!w1</code>-<code>!w12</code> » family lock · <code>!wallmenu</code> » list\n"
        f"◈ <code>!wallpack</code> » 9 walls ek sath · <code>!pblock</code> » full page + title\n"
        f"◈ <code>!wallnc &lt;name&gt;</code> » 24/7 wall+title NC · <code>!dwallnc</code>\n"
        f"◈ <code>!whoop</code> » 2 bots double fire\n\n"
        f"𝟑 💥 <b>SPAM &amp; FORWARD</b>\n"
        f"◈ <code>!s &lt;txt&gt;</code> / <code>!rs</code> / <code>!ts</code> / <code>!c</code>\n"
        f"◈ <code>!fwdspam &lt;txt&gt;</code> » text loop ({{n}} = counter)\n"
        f"◈ reply + <code>!fwdspam</code> » us message ka forward loop\n"
        f"◈ <code>!fwd</code> / <code>!f</code> / <code>!cfwd</code> · "
        f"<code>!gfwd</code> global\n"
        f"◈ stop: <code>!ds</code> · <code>!dfspam</code> · <code>!dfwd</code>\n\n"
        f"𝟒 ⚙️ <b>SPEED / FLOOD</b>\n"
        f"◈ <code>!speed turbo|max|safe|off</code> · <code>!fb on|off</code>\n"
        f"◈ <code>!fb off</code> » RAW 0.03s tick (max pressure, flood-safe pages)\n"
        f"◈ <code>!throttle 0.08</code> · <code>!count</code> · <code>!tasks</code>\n\n"
        f"𝟓 🛡️ <b>ADMIN / CLUSTER</b>\n"
        f"◈ <code>!prombots</code> » auto-admin (2-pass + reason) · <code>!prom</code> reply\n"
        f"◈ <code>!m</code> / <code>!um</code> / <code>!mlist</code> · <code>!sudo</code>\n"
        f"◈ <code>!gcs</code> · <code>!nodes</code> · <code>!leaveall list</code> · "
        f"<code>!leaveall</code>\n\n"
        f"𝟔 🔐 <b>TOKENS / PREFIX</b>\n"
        f"◈ <code>!tokens</code> · <code>!addtoken &lt;tok&gt;</code> · "
        f"<code>!remtoken &lt;no&gt;</code>\n"
        f"◈ <code>!prefix .</code> · <code>~prefix ~</code> · 🔒 <code>!</code> hamesha\n\n"
        f"𝟕 🖼️ <b>PFP / MEDIA / MISC</b>\n"
        f"◈ <code>!botpfp</code> / <code>!p</code> / <code>!gp</code> / <code>!stk</code>\n"
        f"◈ <code>!stat</code> · <code>!ping</code> · <code>!logs</code> · "
        f"<code>!stopall</code> · <code>!bc &lt;txt&gt;</code>"
    )
    await message.reply(menu_text, parse_mode=ParseMode.HTML)

# ==============================================================================
# !GAMEOVER & !SETGO COMMANDS (MANUAL ONLY)
# ==============================================================================
@router.message(DCommand("setgo", "setgameover", prefix="!"), IsSudo())
async def cmd_set_gameover_gif(message: Message):
    rm = message.reply_to_message
    if not rm or not (rm.animation or rm.video):
        return await message.reply("⚠️ <b>Reply to a GIF or short MP4 video with</b> <code>!setgo</code> <b>to save it as the Game Over GIF!</b>", parse_mode=ParseMode.HTML)

    fid = rm.animation.file_id if rm.animation else rm.video.file_id
    file = await message.bot.get_file(fid)
    bio = io.BytesIO()
    try:
        await message.bot.download_file(file.file_path, destination=bio)
        raw_bytes = bio.getvalue()
    finally:
        bio.close()

    STATE.save_gameover_gif(raw_bytes)
    await message.reply("✅ <b>Custom Game Over GIF saved to disk!</b>", parse_mode=ParseMode.HTML)

@router.message(DCommand("gameover", "go", prefix="!"), IsSudo())
async def cmd_gameover(message: Message, command: CommandObject):
    rm = message.reply_to_message
    if rm and (rm.animation or rm.video):
        with suppress(Exception):
            fid = rm.animation.file_id if rm.animation else rm.video.file_id
            file = await message.bot.get_file(fid)
            bio = io.BytesIO()
            await message.bot.download_file(file.file_path, destination=bio)
            STATE.save_gameover_gif(bio.getvalue())
            bio.close()

    custom_target = command.args.strip() if command.args else None
    await execute_gameover(message.chat.id, custom_target=custom_target)

# ==============================================================================
# REPEAT FORWARD COMMANDS (!fwd, !f, !cfwd, !cf, !nfwd, !fnmix, !gfwd, !gf, !dfwd)
# ==============================================================================
@router.message(DCommand("fwd", "f", "cfwd", "cf", "nfwd", "fnmix", prefix="!"), IsSudo())
async def cmd_forward_loop(message: Message, command: CommandObject):
    rm = message.reply_to_message
    if not rm:
        return await message.reply(
            f"⚠️ <b>Reply to any message (text, photo, sticker, video, voice) with</b> <code>!{command.command}</code> <b>to repeat-forward it!</b>",
            parse_mode=ParseMode.HTML
        )

    cmd = command.command.lower()
    use_copy = cmd in ("cfwd", "cf")
    item = {
        "from_chat_id": rm.chat.id,
        "message_id": rm.message_id,
        "copy": use_copy,
        "backup": extract_message_backup(rm),
    }

    q = STATE.fwd_queue.setdefault(message.chat.id, deque(maxlen=MAX_FWD_QUEUE_PER_CHAT))
    if command.args and command.args.strip().lower() == "new":
        q.clear()
    q.append(item)

    spawn(message.chat.id, "fwd", fwd_cluster_worker)

    if cmd in ("nfwd", "fnmix"):
        nc_text = (command.args or "").strip() or (rm.text or rm.caption or "V4 ULTIMATE")[:25]
        spawn(message.chat.id, "nc", nc_cluster_worker, nc_text, "mix")
        return await message.reply(
            f"🌪️ <b>COMBO ACTIVATED: 15-STYLE MIX NC + REPEAT FORWARD!</b>\n"
            f"🔁 <b>Queued Messages:</b> <code>{len(q)}/{MAX_FWD_QUEUE_PER_CHAT}</code>\n"
            f"🎨 <b>NC Target:</b> <code>{nc_text}</code>\n"
            f"🚀 <b>Speed:</b> <code>100ms Pipelined (Non-Stop 24/7)</code>",
            parse_mode=ParseMode.HTML
        )

    mode_label = "COPY-REPEAT" if use_copy else "FORWARD-REPEAT"
    await message.reply(
        f"🔁 <b>{mode_label} LOOP ACTIVATED!</b>\n"
        f"📦 <b>Messages in Rotation:</b> <code>{len(q)}/{MAX_FWD_QUEUE_PER_CHAT}</code>\n"
        f"🛑 <i>Use <code>!dfwd</code> or <code>!df</code> to stop.</i>",
        parse_mode=ParseMode.HTML
    )

@router.message(DCommand("gfwd", "gf", "gcfwd", prefix="!"), IsSudo())
async def cmd_global_forward_loop(message: Message, command: CommandObject):
    rm = message.reply_to_message
    if not rm:
        return await message.reply(
            f"⚠️ <b>Reply to any message with</b> <code>!{command.command}</code> <b>to repeat-forward it across ALL GCs!</b>",
            parse_mode=ParseMode.HTML
        )

    use_copy = command.command.lower() == "gcfwd"
    item = {
        "from_chat_id": rm.chat.id,
        "message_id": rm.message_id,
        "copy": use_copy,
        "backup": extract_message_backup(rm),
    }

    target_chats = STATE.get_all_known_groups(message.chat.id)
    for cid in target_chats:
        q = STATE.fwd_queue.setdefault(cid, deque(maxlen=MAX_FWD_QUEUE_PER_CHAT))
        q.append(item)
        spawn(cid, "fwd", fwd_cluster_worker, save=False)

    STATE.save_runtime_state()
    await message.reply(
        f"🌍 <b>GLOBAL REPEAT-FORWARD DEPLOYED ACROSS {len(target_chats)} GC(s)!</b>\n"
        f"🛑 <i>Use <code>!dgfwd</code> to stop across all GCs.</i>",
        parse_mode=ParseMode.HTML
    )

@router.message(DCommand("dfwd", "df", "dcfwd", "dnfwd", prefix="!"), IsSudo())
async def cmd_stop_forward(message: Message, command: CommandObject):
    STATE.cancel("fwd", message.chat.id, save=False)
    STATE.fwd_queue.pop(message.chat.id, None)
    if command.command.lower() == "dnfwd":
        STATE.cancel("nc", message.chat.id, save=False)
    STATE.save_runtime_state()
    await message.reply("🛑 <b>Repeat-Forward Loop Stopped & Queue Cleared for this GC.</b>", parse_mode=ParseMode.HTML)

@router.message(DCommand("dgfwd", "dgf", prefix="!"), IsSudo())
async def cmd_stop_global_forward(message: Message):
    all_fwd_cids = [int(c) for c in list(STATE.persisted_tasks["fwd"].keys())]
    for cid in set(all_fwd_cids + list(STATE.tasks["fwd"].keys()) + list(STATE.fwd_queue.keys())):
        STATE.cancel("fwd", cid, save=False)
        STATE.fwd_queue.pop(cid, None)
    STATE.save_runtime_state()
    await message.reply("🛑 <b>Global Repeat-Forward Loop Stopped across ALL GCs!</b>", parse_mode=ParseMode.HTML)

# ==============================================================================
# NC COUNTER COMMAND (!count / !nccount / !counts)
# ==============================================================================
@router.message(DCommand("count", "nccount", "counts", prefix="!"), IsSudo())
async def cmd_nc_counts(message: Message):
    gc_hits = STATE.chat_nc_counts.get(message.chat.id, 0)
    global_hits = STATE.global_nc_count
    live_hz = fbe.get_live_hz()

    top_chats = sorted(STATE.chat_nc_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    leaderboard = "\n".join(
        [f"  {idx}. Chat <code>{cid}</code> ➔ <b>{cnt:,}</b> changes" for idx, (cid, cnt) in enumerate(top_chats, 1)]
    ) or "  <i>No group changes recorded yet.</i>"

    await message.reply(
        f"╭━━━〘 🔥 <b>ＮＣ ＣＯＵＮＴＥＲ ＴＥＬＥＭＥＴＲＹ</b> 🔥 〙━━━╮\n"
        f"┃ 📍 <b>This GC Changes:</b> <code>{gc_hits:,}</code>\n"
        f"┃ 🌍 <b>Global Total Changes:</b> <code>{global_hits:,}</code>\n"
        f"┃ ⚡ <b>Current Speed:</b> <code>{live_hz} changes/sec</code>\n"
        f"┣━━━〘 🏆 <b>ＴＯＰ ５ ＧＣｓ</b> 〙━━━┫\n"
        f"{leaderboard}\n"
        f"╰━━━〘 👑 <b>@Nikkkwa (Nik)</b> 〙━━━╯",
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# !THROTTLE ENGINE COMMAND (ULTRA PIPELINED SPEED)
# ==============================================================================
@router.message(DCommand("throttle", prefix="!"), IsSudo())
async def cmd_throttle(message: Message, command: CommandObject):
    arg = (command.args or "").strip().lower()

    if not arg or arg in ("max", "turbo", "on", "fast"):
        fbe.set_mode("max", len(active_bots))
        STATE.delays["nc"] = round(1.0 / max(1, len(active_bots)), 3)
        STATE.delays["spam"] = 0.25
        STATE.delays["rspm"] = 0.25
        STATE.delays["fwd"] = 0.25
        STATE.save_runtime_state()
        return await message.reply(
            f"⚡ <b>ULTRA PIPELINED TURBO ENGINE:</b> <code>ENABLED</code>\n"
            f"🚀 <b>NC Tick:</b> <code>{STATE.delays['nc']}s</code> | <b>Per-Bot Gap:</b> <code>{fbe.per_bot_nc_gap}s</code>\n"
            f"💥 <b>Spam/Fwd Delay:</b> <code>0.25s</code> (100ms BotQueue)",
            parse_mode=ParseMode.HTML
        )

    if arg in ("safe", "stable", "balanced"):
        fbe.set_mode("safe", len(active_bots))
        STATE.delays["nc"] = 0.12
        STATE.save_runtime_state()
        return await message.reply(
            f"🛡️ <b>THROTTLE ENGINE:</b> <code>SAFE BALANCED MODE</code>\n"
            f"⏱️ <b>NC Tick:</b> <code>{STATE.delays['nc']}s</code> | <b>Per-Bot Gap:</b> <code>{fbe.per_bot_nc_gap}s</code>",
            parse_mode=ParseMode.HTML
        )

    if arg in ("off", "disable", "raw"):
        fbe.set_mode("off", len(active_bots))
        STATE.save_runtime_state()
        return await message.reply(
            "🛑 <b>THROTTLE ENGINE:</b> <code>OFF (Uncapped Raw Dispatch)</code>",
            parse_mode=ParseMode.HTML
        )

    total_floods = sum(fbe.flood_history.values())
    healthy_here = fbe.count_healthy_bots_in_chat(active_bots, message.chat.id)
    await message.reply(
        f"📊 <b>PIPELINED ENGINE TELEMETRY:</b>\n\n"
        f"⚙️ <b>Active Profile:</b> <code>{fbe.throttle_mode.upper()}</code>\n"
        f"⚡ <b>Live Throughput:</b> <code>{fbe.get_live_hz()} updates/sec</code>\n"
        f"⏱️ <b>Per-Bot Gap:</b> <code>{fbe.per_bot_nc_gap:.2f}s</code> | <b>Tick:</b> <code>{STATE.delays['nc']}s</code>\n"
        f"🛡️ <b>Total OK:</b> <code>{fbe.total_nc_ok}</code> | <b>Total 429s:</b> <code>{total_floods}</code>\n"
        f"🤖 <b>Healthy Bots in GC:</b> <code>{healthy_here}/{len(active_bots)}</code>",
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# GLOBAL NC COMMANDS (ALL GCs AT PIPELINED SPEED)
# ==============================================================================
@router.message(
    DCommand(
        "gnc", "gmix", "gnmix", "gns", "gnsmix",
        "gn1", "gn2", "gn3", "gn4", "gn5", "gn6", "gn7", "gn8",
        "gn9", "gn10", "gn11", "gn12", "gn13", "gn14", "gn15",
        prefix="!"
    ),
    IsSudo()
)
async def cmd_global_nc(message: Message, command: CommandObject):
    if not command.args:
        return await message.reply(f"⚠️ Usage: <code>!{command.command} &lt;text&gt;</code>", parse_mode=ParseMode.HTML)

    target_chats = STATE.get_all_known_groups(message.chat.id)
    cmd = command.command.lower()
    text = command.args

    for cid in target_chats:
        if cmd in ("gmix", "gnmix", "gnsmix"):
            spawn(cid, "nc", nc_cluster_worker, text, "mix", save=False)
        elif cmd in ("gnc", "gns"):
            spawn(cid, "nc", nc_cluster_worker, text, "n", save=False)
        elif cmd.startswith("gn") and cmd[1:] in DYNAMIC_NC_MAP:
            style_key = cmd[1:]
            spawn(cid, "nc", nc_cluster_worker, text, "style", style_key, save=False)

        if cmd in ("gns", "gnsmix"):
            spawn(cid, "spam", spam_worker, text, "ns", save=False)

    STATE.save_runtime_state()
    await message.reply(
        f"🌍 <b>GLOBAL {cmd.upper()} DEPLOYED ACROSS {len(target_chats)} GC(s)!</b>\n"
        f"🎯 <b>Target Name:</b> <code>{text}</code>\n"
        f"🚀 <b>Speed:</b> <code>100ms Pipelined (Non-Stop 24/7)</code>",
        parse_mode=ParseMode.HTML
    )

@router.message(DCommand("dgnc", "dgmix", "dgnmix", "dgns", "dgnsmix", prefix="!"), IsSudo())
async def cmd_stop_global_nc(message: Message, command: CommandObject):
    all_nc_cids = [int(c) for c in list(STATE.persisted_tasks["nc"].keys())]
    for cid in set(all_nc_cids + list(STATE.tasks["nc"].keys())):
        STATE.cancel("nc", cid, save=False)
        if "s" in command.command:
            STATE.cancel("spam", cid, save=False)
    STATE.save_runtime_state()
    await message.reply("🛑 <b>Global NC Stopped across all GCs!</b>", parse_mode=ParseMode.HTML)

# ==============================================================================
# SINGLE-GC NAME CHANGE COMMANDS (!nmix, !mix, !nsmix, !n1-!n15, !n, !nemo, !nken, !tn)
# ==============================================================================
@router.message(DCommand("nmix", "mix", "nsmix", prefix="!"), IsSudo())
async def cmd_mix_nc(message: Message, command: CommandObject):
    if not command.args:
        return await message.reply(f"⚠️ Usage: !{command.command} <text>")
    spawn(message.chat.id, "nc", nc_cluster_worker, command.args, "mix")
    if command.command == "nsmix":
        spawn(message.chat.id, "spam", spam_worker, command.args, "ns")
        return await message.reply(
            f"🌪️ <b>MEGA MIX-NC + RAID SPAM ACTIVATED!</b>\n"
            f"🎯 <b>Target:</b> <code>{command.args}</code>\n"
            f"🚀 <b>Speed:</b> <code>100ms Pipelined (Non-Stop 24/7)</code>",
            parse_mode=ParseMode.HTML
        )
    await message.reply(
        f"🌪️ <b>ULTIMATE 15-STYLE MIX NC ACTIVATED!</b>\n"
        f"🎯 <b>Target:</b> <code>{command.args}</code>\n"
        f"🚀 <b>Speed:</b> <code>100ms Pipelined ({STATE.delays['nc']}s tick • Non-Stop 24/7)</code>",
        parse_mode=ParseMode.HTML
    )

@router.message(DCommand("n", "nemo", "nken", "ns", prefix="!"), IsSudo())
async def cmd_nc(message: Message, command: CommandObject):
    if not command.args:
        return await message.reply(f"⚠️ Usage: !{command.command} <text>")
    if command.command == "ns":
        spawn(message.chat.id, "nc", nc_cluster_worker, command.args, "n")
        spawn(message.chat.id, "spam", spam_worker, command.args, "ns")
        await message.reply(f"🌩 SPMNC (Spam + 7-Line Mega NC) Activated for '{command.args}'!")
    else:
        spawn(message.chat.id, "nc", nc_cluster_worker, command.args, command.command)
        await message.reply(f"🔥 {command.command.upper()} 7-Line Mega NC Activated for '{command.args}'!")

@router.message(
    DCommand("n1", "n2", "n3", "n4", "n5", "n6", "n7", "n8", "n9", "n10", "n11", "n12", "n13", "n14", "n15", prefix="!"),
    IsSudo()
)
async def cmd_new_styles_nc(message: Message, command: CommandObject):
    if not command.args:
        return await message.reply(f"⚠️ Usage: !{command.command} <text>")
    cfg = DYNAMIC_NC_MAP[command.command]
    spawn(message.chat.id, "nc", nc_cluster_worker, command.args, "style", command.command)
    sample_txt = cfg["fmt"].replace("{base}", command.args)
    await message.reply(
        f"🚀 <b>{command.command.upper()} 100ms Pipelined NC Activated!</b>\n"
        f"🎨 <b>Text Style:</b> <code>{sample_txt}</code>\n"
        f"🧱 <b>Wall Design:</b> <code>{cfg['wall'] * 8}</code>",
        parse_mode=ParseMode.HTML
    )

@router.message(DCommand("tn", prefix="!"), IsSudo())
async def cmd_template_nc(message: Message, command: CommandObject):
    if not command.args:
        return await message.reply("⚠ Usage: !tn <target>")
    tmpl = read_template()
    spawn(message.chat.id, "nc", nc_cluster_worker, command.args, "template", None, tmpl)
    await message.reply(f"🚀 TEMPLATE 7-Line Mega NC Activated with target '{command.args}'!")

@router.message(DCommand("dn", "dnemo", "dnken", "dns", "dnmix", "dmix", prefix="!"), IsSudo())
async def cmd_dnc(message: Message, command: CommandObject):
    STATE.cancel("nc", message.chat.id)
    if command.command in ["dns", "dnmix"]:
        STATE.cancel("spam", message.chat.id)
    STATE.save_runtime_state()
    await message.reply("🛑 NC Engine Stopped.")

# ==============================================================================
# DELAY CONTROLS (!dlyn, !dlyp, !dlys, !dlyrs, !dlyf)
# ==============================================================================
@router.message(DCommand("dlyn", "dlyp", "dlys", "dlyrs", "dlyf", prefix="!"), IsSudo())
async def cmd_delays(message: Message, command: CommandObject):
    if not command.args or not command.args.replace('.', '', 1).isdigit():
        return await message.reply(f"⚠ Enter delay in ms (e.g., !{command.command} 100).")

    ms = float(command.args) / 1000.0
    key_map = {"dlyn": "nc", "dlyp": "pfp", "dlys": "spam", "dlyrs": "rspm", "dlyf": "fwd"}
    STATE.delays[key_map[command.command]] = max(0.0, ms)
    STATE.save_runtime_state()
    await message.reply(f"⏱️ Delay for {key_map[command.command]} set to {ms:.3f}s.")

# ==============================================================================
# MEDIA & PFP COMMANDS (FIXED !botpfp & !gp + DISK/RAM CACHE)
# ==============================================================================
@router.message(DCommand("sv", "gsv", prefix="!"), IsSudo())
async def cmd_save_pfp(message: Message, command: CommandObject):
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply("⚠️ Reply to a photo.")
    fid = message.reply_to_message.photo[-1].file_id
    cat = "gpfp" if command.command == "gsv" else "pfp"

    file = await message.bot.get_file(fid)
    bio = io.BytesIO()
    try:
        await message.bot.download_file(file.file_path, destination=bio)
        raw_bytes = bio.getvalue()
    finally:
        bio.close()

    q = STATE.pfp_cache[cat].setdefault(message.chat.id, deque(maxlen=MAX_PFP_CACHE_PER_CHAT))
    q.append(raw_bytes)
    STATE.save_pfp_to_disk(cat, message.chat.id)
    await message.reply(f"📸 Saved to {cat.upper()} Disk+RAM Cache. Total cached: {len(q)}/{MAX_PFP_CACHE_PER_CHAT}")

@router.message(DCommand("rm", prefix="!"), IsSudo())
async def cmd_del_pfp(message: Message):
    STATE.pfp_cache["pfp"].pop(message.chat.id, None)
    gc.collect()
    await message.reply("🗑️ Chat PFP cache cleared.")

@router.message(DCommand("rmall", prefix="!"), IsSudo())
async def cmd_del_all_media(message: Message):
    for k in STATE.media:
        STATE.media[k].pop(message.chat.id, None)
    for k in STATE.pfp_cache:
        STATE.pfp_cache[k].pop(message.chat.id, None)
    STATE.save_runtime_state()
    gc.collect()
    await message.reply("🧹 All saved media & PFP caches cleared.")

@router.message(DCommand("p", "gp", prefix="!"), IsSudo())
async def cmd_start_pfp(message: Message, command: CommandObject):
    cat = "gpfp" if command.command == "gp" else "pfp"
    is_glob = (cat == "gpfp")
    if not STATE.pfp_cache[cat].get(message.chat.id):
        return await message.reply(f"⚠ Use !{'gsv' if is_glob else 'sv'} first.")
    spawn(message.chat.id, cat, pfp_worker, is_glob)
    await message.reply(f"🔄 {cat.upper()} Rotation Started!")

@router.message(DCommand("dp", prefix="!"), IsSudo())
async def cmd_stop_pfp(message: Message):
    STATE.cancel("pfp", message.chat.id)
    STATE.cancel("gpfp", message.chat.id)
    await message.reply("🛑 PFP Rotation Stopped.")

def register_media(cmd: str, mtype: str, attr: str):
    @router.message(DCommand(cmd, prefix="!"), IsSudo())
    async def hndlr(msg: Message):
        rm = msg.reply_to_message
        if not rm or not getattr(rm, attr, None):
            return await msg.reply(f"⚠️ Reply to {attr}.")
        fid = getattr(rm, attr).file_id if attr != "photo" else rm.photo[-1].file_id
        q = STATE.media[mtype].setdefault(msg.chat.id, deque(maxlen=MAX_MEDIA_PER_CHAT))
        q.append(fid)
        if not STATE.tasks["media"].get(msg.chat.id):
            spawn(msg.chat.id, "media", media_worker, mtype)
            await msg.reply(f"🎬 {mtype.upper()} Spam Started!")
        else:
            STATE.save_runtime_state()
            await msg.reply(f"➕ Added to {mtype} spam ({len(q)}/{MAX_MEDIA_PER_CHAT}).")

register_media("stk", "sticker", "sticker")
register_media("gif", "gif", "animation")
register_media("pic", "photo", "photo")
register_media("vc", "voice", "voice")

@router.message(DCommand("dstk", "dgif", "dpic", "dvc", prefix="!"), IsSudo())
async def cmd_stop_media(message: Message):
    STATE.cancel("media", message.chat.id)
    await message.reply("🛑 Media Spam Stopped.")

# ==============================================================================
# COPY TEMPLATE COMMAND (!c)
# ==============================================================================
@router.message(DCommand("c", prefix="!"), IsSudo())
async def cmd_copy_text(message: Message, command: CommandObject):
    text_to_save = command.args
    if not text_to_save and message.reply_to_message:
        text_to_save = message.reply_to_message.text or message.reply_to_message.caption

    if not text_to_save:
        return await message.reply("⚠️ Provide text or reply to a message containing text to copy.")

    templates = []
    if os.path.exists(SPAM_TEMPLATE_FILE):
        try:
            with open(SPAM_TEMPLATE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content.startswith("["):
                    templates = json.loads(content)
                elif content:
                    templates = [content]
        except Exception:
            pass

    templates.append(text_to_save)
    templates = templates[-30:]
    with open(SPAM_TEMPLATE_FILE, "w", encoding="utf-8") as f:
        json.dump(templates, f, ensure_ascii=False, indent=2)

    await message.reply(f"✅ Template added! (Total: {len(templates)})\nUse `!ts <target>` to start random template spam.")

# ==============================================================================
# SPAM & SLIDE COMMANDS
# ==============================================================================
@router.message(DCommand("s", "rs", prefix="!"), IsSudo())
async def cmd_spam(message: Message, command: CommandObject):
    if not command.args:
        return await message.reply(f"⚠️ Usage: !{command.command} <text>")
    spawn(message.chat.id, "spam", spam_worker, command.args, command.command)
    await message.reply(f"🔥 {command.command.upper()} Started with 100-line Gap!")

@router.message(DCommand("ts", prefix="!"), IsSudo())
async def cmd_template_spam(message: Message, command: CommandObject):
    if not command.args:
        return await message.reply("⚠️ Usage: !ts <target>")

    tmpls = ["{base} Tᴇʀɪ Mᴀᴀ"]
    if os.path.exists(SPAM_TEMPLATE_FILE):
        try:
            with open(SPAM_TEMPLATE_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content.startswith("["):
                    data = json.loads(content)
                    if isinstance(data, list) and len(data) > 0:
                        tmpls = data
                elif content:
                    tmpls = [content]
        except Exception:
            pass

    spawn(message.chat.id, "spam", spam_worker, command.args, "template", tmpls)
    await message.reply(f"🚀 RANDOM TEMPLATE SPAM Activated for '{command.args}' ({len(tmpls)} templates)!")

@router.message(DCommand("tsl", "sls", prefix="!"), IsSudo())
async def cmd_slide(message: Message, command: CommandObject):
    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply("⚠️ Reply to a user.")
    uid = message.reply_to_message.from_user.id
    name = command.args if command.command == "tsl" and command.args else message.reply_to_message.from_user.first_name
    text = command.args if command.command == "sls" else None

    spawn(message.chat.id, "slide", slide_worker, uid, name, text)
    await message.reply(f"🎯 Target Locked on {name}!")

@router.message(DCommand("ds", "drs", "dts", "dalls", "dtsl", "dsls", prefix="!"), IsSudo())
async def cmd_stop_spams(message: Message, command: CommandObject):
    if "sl" in command.command:
        STATE.cancel("slide", message.chat.id)
    else:
        STATE.cancel("spam", message.chat.id)
    await message.reply("🛑 Task Stopped.")

# ==============================================================================
# TARGET INTERCEPTORS
# ==============================================================================
@router.message(DCommand("rnorv", "rct", "swp", prefix="!"), IsSudo())
async def cmd_interceptors(message: Message, command: CommandObject):
    cmd = command.command
    if cmd == "swp":
        if not command.args:
            return await message.reply("⚠️ Usage: !swp <text>")
        STATE.targets["swipe"][message.chat.id] = command.args
        STATE.save_runtime_state()
        return await message.reply("⚡ Auto-Intercept Swipe Active.")

    if not message.reply_to_message or not message.reply_to_message.from_user:
        return await message.reply("⚠ Reply to a user.")
    uid = message.reply_to_message.from_user.id

    if cmd == "rnorv":
        STATE.targets["reply"][uid] = True
        STATE.save_runtime_state()
        await message.reply("🗣️ Auto-Insult Active.")
    elif cmd == "rct":
        if not command.args:
            return await message.reply("⚠️ Provide an emoji.")
        STATE.targets["react"][uid] = command.args.strip()
        STATE.save_runtime_state()
        await message.reply("✅ Auto-React Active.")

@router.message(DCommand("drnorv", "drct", "dswp", prefix="!"), IsSudo())
async def cmd_stop_interceptors(message: Message, command: CommandObject):
    target_key = ""
    if command.command == "drnorv":
        target_key = "reply"
    elif command.command == "drct":
        target_key = "react"
    elif command.command == "dswp":
        target_key = "swipe"

    if target_key == "swipe":
        STATE.targets["swipe"].pop(message.chat.id, None)
    elif message.reply_to_message and message.reply_to_message.from_user:
        STATE.targets[target_key].pop(message.reply_to_message.from_user.id, None)
    else:
        STATE.targets[target_key].clear()

    STATE.save_runtime_state()
    await message.reply(f"🛑 {target_key.upper()} deactivated.")

# ==============================================================================
# LOGS, ACTIVE TASKS & FLOOD BYPASS COMMANDS
# ==============================================================================
@router.message(DCommand("tasks", "running", prefix="!"), IsSudo())
async def cmd_tasks(message: Message):
    lines = ["🔄 <b>ACTIVE PERSISTED TASKS:</b>\n"]
    found = False
    for cat, c_dict in STATE.persisted_tasks.items():
        if c_dict:
            found = True
            lines.append(f"📂 <b>{cat.upper()} ({len(c_dict)} GCs):</b>")
            for cid_str, info in c_dict.items():
                cid_int = int(cid_str)
                usable = fbe.count_healthy_bots_in_chat(active_bots, cid_int)
                hits = STATE.chat_nc_counts.get(cid_int, 0)
                label = info.get("style_key") or info.get("mode") or info.get("mtype") or info.get("name") or f"{len(STATE.fwd_queue.get(cid_int, []))} msg(s)"
                arg_txt = info.get("base") or info.get("text") or ""
                lines.append(f"  • Chat <code>{cid_str}</code> ➔ <code>{label}</code> ({arg_txt[:15]}) | 🤖 <code>{usable}</code> | 🔥 <code>{hits:,}</code>")

    if not found:
        lines.append("<i>No active tasks running right now.</i>")
    await message.reply("\n".join(lines), parse_mode=ParseMode.HTML)

@router.message(DCommand("logs", "log", prefix="!"), IsSudo())
async def cmd_logs(message: Message, command: CommandObject):
    args = (command.args or "").strip().lower()

    if not LOG_BUFFER:
        return await message.reply("📝 <b>Logs Buffer:</b> Empty.", parse_mode=ParseMode.HTML)

    if args == "file":
        full_log_data = "\n".join(LOG_BUFFER).encode("utf-8")
        doc = BufferedInputFile(full_log_data, filename="cluster_logs.txt")
        return await message.reply_document(document=doc, caption="📁 <b>Cluster Telemetry Logs</b>", parse_mode=ParseMode.HTML)

    recent_entries = list(LOG_BUFFER)[-15:]
    formatted_logs = "\n".join(recent_entries)

    text = (
        "📋 <b>RECENT CLUSTER LOGS (Last 15):</b>\n\n"
        f"<code>{formatted_logs}</code>\n\n"
        "💡 <i>Use <code>!logs file</code> or <code>!clearlogs</code></i>"
    )
    await message.reply(text, parse_mode=ParseMode.HTML)

@router.message(DCommand("clearlogs", prefix="!"), IsSudo())
async def cmd_clear_logs(message: Message):
    LOG_BUFFER.clear()
    gc.collect()
    await message.reply("🧹 <b>Telemetry Log Buffer Cleared.</b>", parse_mode=ParseMode.HTML)

@router.message(DCommand("fb", "bypass", prefix="!"), IsSudo())
async def cmd_flood_bypass(message: Message, command: CommandObject):
    args = (command.args or "").strip().lower()

    if args in ["on", "enable", "1"]:
        fbe.set_mode("max", len(active_bots))
        STATE.save_runtime_state()
        return await message.reply(
            f"⚡ <b>Flood Bypass System:</b> <code>ENABLED</code> (10-Bot LRU Pipelined Pacing)\n"
            f"🤖 <b>Tick:</b> <code>{STATE.delays['nc']}s</code> | <b>Per-Bot Gap:</b> <code>{fbe.per_bot_nc_gap}s</code>",
            parse_mode=ParseMode.HTML
        )
    elif args in ["off", "disable", "0"]:
        fbe.set_mode("off", len(active_bots))
        STATE.save_runtime_state()
        return await message.reply("🛑 <b>Flood Bypass System:</b> <code>DISABLED</code> (Uncapped rate).", parse_mode=ParseMode.HTML)

    status_lines = [
        f"⚡ <b>FLOOD BYPASS ENGINE:</b> <code>{'ENABLED' if fbe.bypass_active else 'DISABLED'}</code>",
        f"🤖 <b>Total Nodes:</b> <code>{len(active_bots)}</code>",
        f"🚀 <b>Live Throughput:</b> <code>{fbe.get_live_hz()} Hz</code> (Gap: <code>{fbe.per_bot_nc_gap:.2f}s</code>)",
        ""
    ]

    flooded_count = 0
    for idx, b in enumerate(active_bots, start=1):
        rem = fbe.remaining_cooldown(b.id)
        hits = fbe.flood_history.get(b.id, 0)
        if rem > 0:
            flooded_count += 1
            status_lines.append(f"• <b>Bot {idx}</b> (<code>{b.id}</code>): ⚠️ Cooling down (<code>{rem:.1f}s</code> left | Hits: {hits})")
        else:
            status_lines.append(f"• <b>Bot {idx}</b> (<code>{b.id}</code>): 🟢 Ready (Hits: {hits})")

    status_lines.append(f"\n📊 <b>Healthy Nodes Available:</b> <code>{len(active_bots) - flooded_count}/{len(active_bots)}</code>")
    await message.reply("\n".join(status_lines), parse_mode=ParseMode.HTML)

# ==============================================================================
# BROADCAST SYSTEM (ANTI-FLOOD)
# ==============================================================================
@router.message(DCommand("bc", "broadcast", prefix="!"), IsSudo())
async def cmd_broadcast(message: Message, command: CommandObject):
    text = command.args
    if not text and message.reply_to_message:
        text = message.reply_to_message.text or message.reply_to_message.caption

    if not text:
        return await message.reply("⚠️ Usage: <code>!bc &lt;text&gt;</code> or reply to a message with <code>!bc</code>", parse_mode=ParseMode.HTML)

    chats = STATE.get_all_known_groups(message.chat.id)
    msg = await message.reply(f"🚀 Starting anti-flood broadcast to {len(chats)} chats...")

    async def run_broadcast():
        success, failed = 0, 0
        for chat_id in chats:
            sent = False
            for b in active_bots:
                if fbe.is_flooded(b.id) or not fbe.is_bot_usable_in_chat(chat_id, b.id):
                    continue
                try:
                    await b.send_message(chat_id, text, parse_mode=ParseMode.HTML)
                    success += 1
                    sent = True
                    break
                except TelegramRetryAfter as e:
                    fbe.mark_flooded(b.id, e.retry_after)
                except Exception:
                    continue
            if not sent:
                failed += 1
            await asyncio.sleep(0.8)

        with suppress(Exception):
            await msg.edit_text(
                f"✅ <b>Broadcast Complete!</b>\n🎯 Success: <code>{success}</code>\n❌ Failed: <code>{failed}</code>",
                parse_mode=ParseMode.HTML
            )

    asyncio.create_task(run_broadcast())

# ==============================================================================
# FIXED MUTE, PROMO & BOTPFP COMMANDS
# ==============================================================================
def extract_target_uid(message: Message, command: CommandObject) -> Optional[int]:
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user.id
    if command.args and command.args.strip().lstrip("-").isdigit():
        return int(command.args.strip())
    return None

@router.message(DCommand("m", "mute", prefix="!"), IsSudo())
async def cmd_mute(message: Message, command: CommandObject):
    uid = extract_target_uid(message, command)
    if not uid:
        return await message.reply("⚠️ Reply to a user or provide their User ID: <code>!m &lt;user_id&gt;</code>", parse_mode=ParseMode.HTML)
    if uid == OWNER_ID or uid in STATE.sudo:
        return await message.reply("❌ Cannot mute Owner or Sudo users.")

    STATE.muted.setdefault(message.chat.id, set()).add(uid)
    STATE.save_runtime_state()
    await smart_restrict(message.chat.id, uid, mute=True)
    await message.reply(f"🤫 User <code>{uid}</code> Permanently Muted.", parse_mode=ParseMode.HTML)

@router.message(DCommand("um", "unmute", prefix="!"), IsSudo())
async def cmd_unmute(message: Message, command: CommandObject):
    uid = extract_target_uid(message, command)
    if not uid:
        return await message.reply("⚠️ Reply to a user or provide their User ID: <code>!um &lt;user_id&gt;</code>", parse_mode=ParseMode.HTML)

    if message.chat.id in STATE.muted:
        STATE.muted[message.chat.id].discard(uid)
    STATE.save_runtime_state()

    await smart_restrict(message.chat.id, uid, mute=False)
    await message.reply(f"🔊 User <code>{uid}</code> unmuted.", parse_mode=ParseMode.HTML)

@router.message(DCommand("mlist", prefix="!"), IsSudo())
async def cmd_mutelist(message: Message):
    users = STATE.muted.get(message.chat.id, set())
    if not users:
        return await message.reply("🔊 No muted users in this chat.")
    text = "🤫 <b>Muted Users:</b>\n" + "\n".join([f"• <code>{u}</code>" for u in users])
    await message.reply(text, parse_mode=ParseMode.HTML)

@router.message(DCommand("prombots", "promall", prefix="!"), IsSudo())
async def cmd_promotebots(message: Message):
    """Auto-admin: har bot ko promote karo — 2 pass (full rights -> minimal).

    Fail hone par asli wajah batata hai (admin rights / bot not admin / etc),
    isliye pehle "kharab" lagta tha: silent except ke andar error gayab ho jata tha.
    """
    cid = message.chat.id
    if not active_bots:
        return await message.reply("⚠️ Koi active node nahi hai.")
    msg = await message.reply(
        f"🔄 <b>Auto-admin</b> • <code>{len(active_bots)}</code> bots…",
        parse_mode=ParseMode.HTML)
    ok_ids, fails = [], []
    for b in active_bots:
        done = False
        for rights in ("full", "minimal"):
            try:
                if rights == "full":
                    await b.promote_chat_member(
                        chat_id=cid, user_id=b.id,
                        can_manage_chat=True, can_delete_messages=True,
                        can_manage_video_chats=True, can_restrict_members=True,
                        can_promote_members=True, can_change_info=True,
                        can_invite_users=True, can_pin_messages=True,
                        can_manage_topics=True)
                else:
                    await b.promote_chat_member(
                        chat_id=cid, user_id=b.id, can_manage_chat=True)
                done = True
                break
            except TelegramRetryAfter as e:
                fbe.mark_flooded(b.id, e.retry_after, chat_id=cid)
                await asyncio.sleep(min(3.0, float(e.retry_after or 1)))
            except Exception as e:
                reason = str(e).lower()
                if rights == "minimal":
                    if "not enough rights" in reason or "have no rights" in reason:
                        fails.append((b.id, "promoter admin nahi"))
                    elif "chat_admin_required" in reason or "not an administrator" in reason:
                        fails.append((b.id, "bot khud admin nahi"))
                    elif "user is an administrator" in reason:
                        done = True
                        break
                    else:
                        fails.append((b.id, reason[:38] or "unknown"))
                continue
        if done:
            ok_ids.append(b.id)
        await asyncio.sleep(0.25)
    body = (f"🛡️ <b>AUTO-ADMIN</b>\n"
            f"✅ promoted <code>{len(ok_ids)}/{len(active_bots)}</code>\n")
    if fails:
        body += "⚠️ <b>Failed:</b>\n" + "\n".join(
            f"• <code>{bid}</code> — {why}" for bid, why in fails[:6])
        body += ("\n\n💡 Bot ko pehle <b>admin</b> banao (Add New Admins right) "
                 "warna wo khud ko promote nahi kar sakta.")
    await msg.edit_text(body, parse_mode=ParseMode.HTML)

@router.message(DCommand("prom", "promote", prefix="!"), IsSudo())
async def cmd_promoteall(message: Message, command: CommandObject):
    uid = extract_target_uid(message, command)
    if uid:
        users = {uid}
    else:
        bot_ids = {b.id for b in active_bots}
        users = {u for u in STATE.tracked_users.get(message.chat.id, set()) if u not in bot_ids}

    if not users:
        return await message.reply("⚠️ Reply to a user, pass a User ID (<code>!prom 123456</code>), or wait for users to chat.", parse_mode=ParseMode.HTML)

    msg = await message.reply(f"🔄 Promoting {len(users)} user(s)...")
    count = 0
    for u in users:
        if await smart_promote(message.chat.id, u):
            count += 1
        await asyncio.sleep(0.12)
    await msg.edit_text(f"✅ Successfully promoted <code>{count}/{len(users)}</code> user(s).", parse_mode=ParseMode.HTML)

@router.message(DCommand("sudo", "dsudo", prefix="!"), IsOwner())
async def cmd_sudo(message: Message, command: CommandObject):
    uid = extract_target_uid(message, command)
    if not uid:
        return await message.reply("⚠️ Reply to a user or provide a User ID.")
    if command.command == "sudo":
        STATE.sudo.add(uid)
        await message.reply(f"✅ <code>{uid}</code> is now Sudo.", parse_mode=ParseMode.HTML)
    else:
        if uid == OWNER_ID:
            return await message.reply("❌ Cannot remove Owner.")
        STATE.sudo.discard(uid)
        await message.reply(f"🗑️ <code>{uid}</code> removed from Sudo.", parse_mode=ParseMode.HTML)
    STATE.save_sudo()

@router.message(DCommand("sudolist", prefix="!"), IsSudo())
async def cmd_listsudo(message: Message):
    text = "👑 <b>SUDO USERS:</b>\n" + "\n".join([f"• <code>{u}</code>" for u in STATE.sudo])
    await message.reply(text, parse_mode=ParseMode.HTML)

@router.message(DCommand("botpfp", prefix="!"), IsSudo())
async def cmd_botpfp(message: Message):
    rm = message.reply_to_message
    if not rm or not (rm.photo or (rm.document and rm.document.mime_type and rm.document.mime_type.startswith("image/"))):
        return await message.reply("⚠️ <b>Reply to a photo with</b> <code>!botpfp</code> <b>to update all cluster bots' profile pictures!</b>", parse_mode=ParseMode.HTML)

    msg = await message.reply("🔄 <b>Updating profile pictures across all cluster bots...</b>", parse_mode=ParseMode.HTML)
    fid = rm.photo[-1].file_id if rm.photo else rm.document.file_id
    file = await message.bot.get_file(fid)
    bio = io.BytesIO()
    try:
        await message.bot.download_file(file.file_path, destination=bio)
        raw_bytes = bio.getvalue()
    finally:
        bio.close()

    results = await asyncio.gather(*(set_bot_profile_photo_safe(b, raw_bytes) for b in active_bots), return_exceptions=True)
    updated_count = sum(1 for r in results if r is True)

    await msg.edit_text(
        f"✅ <b>Bot Profile Photos Updated:</b> <code>{updated_count}/{len(active_bots)}</code> bots!",
        parse_mode=ParseMode.HTML
    )

# ==============================================================================
# MISC, RAM OPTIMIZER & STATS
# ==============================================================================
@router.message(DCommand("stopall", prefix="!"), IsSudo())
async def cmd_dall(message: Message, command: CommandObject):
    if command.args and command.args.strip().lower() == "global":
        STATE.stop_all(None, save=True)
        return await message.reply("🛑 ALL TASKS HALTED GLOBALLY ACROSS ALL CHATS.")
    STATE.stop_all(message.chat.id, save=True)
    await message.reply("🛑 ALL TASKS HALTED IN THIS CHAT.\n💡 <i>Use <code>!stopall global</code> to clear all chats.</i>", parse_mode=ParseMode.HTML)

@router.message(DCommand("leave", prefix="!"), IsSudo())
async def cmd_leave(message: Message):
    STATE.stop_all(message.chat.id, save=True)
    STATE.known_chats.discard(message.chat.id)
    STATE.save_runtime_state()
    await message.reply("👋 Abandoning Chat...")
    for b in active_bots:
        with suppress(Exception):
            await b.leave_chat(message.chat.id)

@router.message(DCommand("o", prefix="!"), IsSudo())
async def cmd_optimize(message: Message):
    before_mb = get_ram_mb()
    STATE.tracked_users.clear()
    LOG_BUFFER.clear()
    gc.collect()
    after_mb = get_ram_mb()
    await message.reply(
        f"🧹 <b>RAM Purged!</b>\n"
        f"📉 <b>Before:</b> <code>{before_mb:.1f} MB</code> ➔ <b>Now:</b> <code>{after_mb:.1f} MB</code>",
        parse_mode=ParseMode.HTML
    )

@router.message(DCommand("bots", "mbots", prefix="!"), IsSudo())
async def cmd_bots(message: Message, command: CommandObject):
    if command.command == "bots":
        in_this_gc = len(STATE.chat_bots.get(message.chat.id, set()))
        await message.reply(
            f"🤖 <b>Active Cluster Nodes:</b> <code>{len(active_bots)}</code>\n"
            f"📍 <b>Detected in this GC:</b> <code>{in_this_gc}</code> (All-Bot Failover Active)",
            parse_mode=ParseMode.HTML
        )
    else:
        text = "❌ <b>Failed Nodes:</b>\n" + "\n".join([f"• <code>{t[:15]}...</code>" for t in STATE.failed_bots]) if STATE.failed_bots else "✅ No missing bots."
        await message.reply(text, parse_mode=ParseMode.HTML)

@router.message(DCommand("link", "links", prefix="!"), IsSudo())
async def cmd_links(message: Message):
    msg = await message.reply("🔍 Extracting all cluster and chat links...")

    bot_links = []
    for idx, b in enumerate(active_bots, start=1):
        uname = bot_usernames.get(b.id)
        if uname:
            add_url = f"https://t.me/{uname}?startgroup=true"
            bot_links.append(f"• <b>Bot {idx}</b> (@{uname}): <a href='{add_url}'>Add to Chat</a>")
        else:
            bot_links.append(f"• <b>Bot {idx}</b> (ID: <code>{b.id}</code>): No username")

    _, chat_invite = await get_gc_invite_and_title(message.chat.id)

    lines = [f"🤖 <b>ACTIVE CLUSTER NODES ({len(active_bots)} TOTAL):</b>", ""]
    lines.extend(bot_links)

    if message.chat.type in ["group", "supergroup"]:
        lines.append("")
        lines.append(f"🔗 <b>Current Group Invite Link:</b>\n{chat_invite}")

    await msg.edit_text("\n".join(lines), parse_mode=ParseMode.HTML, disable_web_page_preview=True)

@router.message(DCommand("stat", "up", "on", "ping", prefix="!"), IsSudo())
async def cmd_stats(message: Message, command: CommandObject):
    ram_mb = get_ram_mb()
    gc_hits = STATE.chat_nc_counts.get(message.chat.id, 0)
    global_hits = STATE.global_nc_count

    if command.command in ["ping", "on"]:
        t1 = time.perf_counter()
        m = await message.reply("📡 Pinging...")
        await m.edit_text(
            f"🚀 <b>PONG!</b> <code>{(time.perf_counter() - t1)*1000:.1f}ms</code>\n"
            f"🤖 <b>Answered By:</b> @{bot_usernames.get(message.bot.id, message.bot.id)}\n"
            f"⚡ <b>Speed:</b> <code>{fbe.get_live_hz()} Hz</code> (Tick: <code>{STATE.delays['nc']}s</code>)\n"
            f"🔥 <b>NC Count:</b> <code>{gc_hits:,} GC</code> | <code>{global_hits:,} Global</code>\n"
            f"💾 <b>RAM:</b> <code>{ram_mb:.1f} MB</code>",
            parse_mode=ParseMode.HTML
        )
    else:
        uptime = int(time.time() - STATE.start_time)
        hrs, rem = divmod(uptime, 3600)
        mins, secs = divmod(rem, 60)
        nc_gcs = len(STATE.persisted_tasks["nc"])
        spm_gcs = len(STATE.persisted_tasks["spam"])
        fwd_gcs = len(STATE.persisted_tasks["fwd"])
        known_gcs = len(STATE.get_all_known_groups(message.chat.id))
        await message.reply(
            f"╭━━━〘 📊 <b>ＣＬＵＳＴＥＲ ＴＥＬＥＭＥＴＲＹ</b> 📊 〙━━━╮\n"
            f"┃ ⏱️ <b>Uptime:</b> <code>{hrs}h {mins}m {secs}s</code>\n"
            f"┃ 🤖 <b>Bots Online:</b> <code>{len(active_bots)}</code> (All-Bot Failover)\n"
            f"┃ ⚡ <b>Speed:</b> <code>100ms Pipelined</code> (<code>{fbe.get_live_hz()} Hz</code>)\n"
            f"┃ 🔥 <b>This GC NC Count:</b> <code>{gc_hits:,}</code>\n"
            f"┃ 🌐 <b>Global NC Count:</b> <code>{global_hits:,}</code>\n"
            f"┃ 🌍 <b>Known GCs:</b> <code>{known_gcs}</code>\n"
            f"┃ 🔄 <b>Active GCs:</b> <code>{nc_gcs} NC | {spm_gcs} Spm | {fwd_gcs} Fwd</code>\n"
            f"┃ 💾 <b>RAM Usage:</b> <code>{ram_mb:.1f} MB</code>\n"
            f"╰━━━〘 👑 <b>@Nikkkwa (Nik)</b> 〙━━━╯",
            parse_mode=ParseMode.HTML
        )

# ==============================================================================
# GLOBAL MESSAGE INTERCEPTOR (CONCURRENT MULTI-BOT DISPATCH)
# ==============================================================================
async def _safe_react(bot: Bot, cid: int, mid: int, react_obj):
    with suppress(Exception):
        await bot.set_message_reaction(cid, mid, reaction=[react_obj])

async def _safe_reply(bot: Bot, cid: int, mid: int, text: str):
    with suppress(Exception):
        await bot.send_message(cid, text, reply_to_message_id=mid)

@router.message()
async def interceptor(message: Message, bot: Bot):
    if not message.from_user:
        return
    uid = message.from_user.id
    cid = message.chat.id

    if message.chat.type in ("group", "supergroup"):
        STATE.known_chats.add(cid)

    tracked = STATE.tracked_users.setdefault(cid, set())
    if len(tracked) < MAX_TRACKED_USERS_PER_CHAT:
        tracked.add(uid)

    if cid in STATE.muted and uid in STATE.muted[cid]:
        with suppress(Exception):
            await message.delete()
        return

    if message.text and _is_command_text(message.text):
        return

    mid = message.message_id
    create_task = asyncio.create_task

    if uid in STATE.targets["react"]:
        emo = STATE.targets["react"][uid]
        react = ReactionTypeCustomEmoji(type="custom_emoji", custom_emoji_id=emo) if len(emo) > 10 else ReactionTypeEmoji(type="emoji", emoji=emo)
        for b in active_bots:
            if not fbe.is_flooded(b.id):
                create_task(_safe_react(b, cid, mid, react))

    if cid in STATE.targets["swipe"]:
        swipe_text = f"{STATE.targets['swipe'][cid]} 𝘓𝘶𝘯𝘥 𝘤𝘩𝘶𝘴𝘴𝘭𝘦 𝘴𝘢𝘵𝘩 𝘮𝘦 मां 𝘣𝘩𝘦 𝘤𝘩𝘶𝘥𝘸𝘢 𝘭𝘦 Okna? 😵‍💫🔥 {random.choice(EMOJIS)}"
        for b in active_bots:
            if not fbe.is_flooded(b.id):
                create_task(_safe_reply(b, cid, mid, swipe_text))

    if uid in STATE.targets["reply"]:
        for b in active_bots:
            if not fbe.is_flooded(b.id):
                create_task(_safe_reply(b, cid, mid, random.choice(RAID_TEXTS)))

# ==============================================================================
# AUTO RAM-GUARD DAEMON & OPTIONAL KEEP-ALIVE WEB SERVER
# ==============================================================================
async def auto_ram_guard():
    while True:
        await asyncio.sleep(60)
        with suppress(Exception):
            if STATE.unsaved_nc_hits > 0:
                STATE.unsaved_nc_hits = 0
                STATE.save_runtime_state()
            for cid in list(STATE.tracked_users.keys()):
                if len(STATE.tracked_users[cid]) > MAX_TRACKED_USERS_PER_CHAT:
                    STATE.tracked_users[cid].clear()
            gc.collect()
            ram = get_ram_mb()
            if ram > 380.0:
                STATE.tracked_users.clear()
                LOG_BUFFER.clear()
                gc.collect()
                log_event("warn", "RAM-GUARD", f"High RAM ({ram:.1f}MB) auto-purged.")

async def handle_health(request):
    return web.json_response({
        "status": "online",
        "banner": START_BANNER_TEXT,
        "dev": "@Nikkkwa (Nik)",
        "ist_time": get_ist_str(),
        "active_bots": len(active_bots),
        "live_hz": fbe.get_live_hz(),
        "global_nc_count": STATE.global_nc_count,
        "ram_mb": round(get_ram_mb(), 2),
        "known_gcs": len(STATE.known_chats),
        "persisted_nc_chats": len(STATE.persisted_tasks["nc"]),
        "persisted_big_chats": len(STATE.persisted_tasks["big"]),
        "ultra_families": len(ULTRA.FAMILIES),
        "mega_emojis": len(MEGA_EMOJIS),
    })

async def start_panel_or_hf_webserver():
    try:
        app = web.Application()
        app.router.add_get("/", handle_health)
        app.router.add_get("/health", handle_health)
        runner = web.AppRunner(app, access_log=None)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", PORT)
        await site.start()
        log_event("info", "WEB", f"Keep-Alive Server bound to 0.0.0.0:{PORT}")
    except Exception as e:
        log_event("info", "VPS", f"Port {PORT} bind skipped ({e}). Running in pure VPS/Panel mode.")

# ==============================================================================
# MAIN LIFECYCLE (PARALLEL FAST BOOT + ALL-BOT FAILOVER POLLING + 24/7 PIPELINE)
# ==============================================================================
async def _init_single_bot(t: str) -> Optional[Bot]:
    try:
        session = AiohttpSession(limit=100)
        b = Bot(token=t, session=session, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
        me = await b.get_me()
        await b.delete_webhook(drop_pending_updates=True)
        bot_usernames[b.id] = me.username or ""
        LIVE_BOTS[t] = b
        return b
    except Exception as e:
        STATE.failed_bots.append(t)
        log_event("warn", "BOOT", f"Token {t[:12]}... failed: {e}")
        return None

async def main():
    global active_bots
    active_bots.clear()
    await start_panel_or_hf_webserver()
    asyncio.create_task(auto_ram_guard())

    dp = Dispatcher()
    dp.include_router(router)

    valid_tokens = [t.strip() for t in TOKENS if t.strip() and not t.startswith("YOUR_BOT")]
    log_event("info", "BOOT", f"Parallel-initializing 10-Bot Pipelined Cluster ({len(valid_tokens)} tokens)...")

    booted = await asyncio.gather(*(_init_single_bot(t) for t in valid_tokens))
    active_bots.extend([b for b in booted if b is not None])

    gc.collect()
    if not active_bots:
        log_event("error", "BOOT", "No valid bots loaded. Retrying in 10s...")
        await asyncio.sleep(10)
        return

    fbe.recalculate_pacing(len(active_bots))
    STATE.load_runtime_state()
    STATE.delays["nc"] = fbe.cluster_nc_tick   # SPEED: json ki purani value override

    await restore_persisted_tasks()

    # SPEED: pehla wall turant taiyar — boot pe hi 2 pages prewarm
    try:
        _warm = "NIKK"
        compose_page(NEMO.build(_warm, 0, "nemox", 0), NEMO_HARD_LIMIT)
        compose_page(ULTRA.build(_warm, 0, "titan", 0), 3900)
    except Exception:
        pass

    asyncio.create_task(task_watchdog_daemon())

    log_event("info", "BOOT", f"{len(active_bots)} Nodes Online | All-Bot Failover Active | Pipelined NC Tick: {STATE.delays['nc']}s")

    while True:
        try:
            await dp.start_polling(
                *active_bots,
                allowed_updates=dp.resolve_used_update_types(),
                polling_timeout=25,
                handle_signals=False,
            )
        except asyncio.CancelledError:
            break
        except Exception as e:
            log_event("error", "SYSTEM", f"Polling interrupted: {str(e)}. Reconnecting in 2s...")
            gc.collect()
            await asyncio.sleep(2)

    STATE.stop_all(save=False)
    for b in active_bots:
        with suppress(Exception):
            await b.session.close()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() in ("--check", "-c"):
        print("=== NIK SYSTEM / CONFIG CHECK ===")
        print(f"  OWNER_ID    : {OWNER_ID or 0}")
        print("  MAIN_TOKEN  : " + ("set" if MAIN_TOKEN else "EMPTY -> CONFIG[MAIN_TOKEN] bharo"))
        print(f"  extra slots : {sum(1 for t in TOKENS[1:] if t)}/9 filled")
        print(f"  total       : {sum(1 for t in TOKENS if t)}/{MAX_TOKENS}")
        print(f"  PREFIX      : {PREFIX}  (! fallback ALWAYS on)")
        print("  commands    : !addtoken / !remtoken / !tokens / ~prefix ~")
        print("  big-nc      : bignc / bigwall / dbignc / bigmenu / leaveall / gcs / nodes")
        print(f"  ultra-wall  : {len(ULTRA.FAMILIES)} random giant families + {len(MEGA_EMOJIS)} emojis")
        print("  ultra-cmds  : ultra / u1-u10 / wallpack / pblock / ultranc / dultra")
        print(f"  wall-classic: {len(WALL.FAMILIES)} families 𒐫~✖ · "
              f"{NEMO_HARD_LIMIT}-char pages · !wall/!w1-!w12/!wallpack/!pblock")
        print("  tagdi-nc    : 3 heavy styles · !tagdi/!tagdi1-!tagdi3/!tagdilist")
        print("  fwd-spam    : !fwdspam <txt> | reply+!fwdspam | !dfspam")
        print(f"  speed       : PACK_DELAY={PACK_DELAY}s · cache TTL={WALL_CACHE_TTL}s · "
              f"per-bot gap={fbe.per_bot_nc_gap}s · !speed turbo")
        sys.exit(0)
    while True:
        try:
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            STATE.save_runtime_state()
            print("🛑 MANUAL SHUTDOWN. State & NC counts preserved in v4_runtime_state.json.")
            break
        except Exception as fatal_err:
            STATE.save_runtime_state()
            print(f"⚠️ FATAL CRASH DETECTED: {fatal_err}\n{traceback.format_exc()}", flush=True)
            print("🔄 Auto-restarting script in 2 seconds and resuming all GC tasks...", flush=True)
            time.sleep(2)