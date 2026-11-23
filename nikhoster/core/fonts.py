"""
NIK HOSTER v1 — clean typography.

Rule: gaali-mixed math-bold unicode nahi. Sirf 3 style:
  sc()   -> small caps  (headers, labels, buttons)
  HTML   -> <b>, <i>, <code>, <blockquote>  (Telegram ka apna clean font)
  plain  -> numbers / paths inside <code> so they align in monospace
"""
from __future__ import annotations

import time

SMALL_CAPS = {
    "a": "ᴀ", "b": "ʙ", "c": "ᴄ", "d": "ᴅ", "e": "ᴇ", "f": "ꜰ", "g": "ɢ",
    "h": "ʜ", "i": "ɪ", "j": "ᴊ", "k": "ᴋ", "l": "ʟ", "m": "ᴍ", "n": "ɴ",
    "o": "ᴏ", "p": "ᴘ", "q": "ǫ", "r": "ʀ", "s": "ꜱ", "t": "ᴛ", "u": "ᴜ",
    "v": "ᴠ", "w": "ᴡ", "x": "x", "y": "ʏ", "z": "ᴢ",
}

LINE = "─" * 16


def sc(text: str) -> str:
    """small caps — clean, halka, har device pe same dikhta hai."""
    return "".join(SMALL_CAPS.get(ch.lower(), ch) if ch.isalpha() else ch for ch in str(text))


def esc(text: str) -> str:
    """HTML parse mode ke liye escape (user names safe rahen)."""
    return (str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def bold(text: str) -> str:
    return f"<b>{esc(text)}</b>"


def mono(text: str) -> str:
    return f"<code>{esc(text)}</code>"


def quote(text: str) -> str:
    return f"<blockquote>{text}</blockquote>"


def link(text: str, url: str) -> str:
    return f'<a href="{esc(url)}">{esc(text)}</a>'


def human_bytes(num: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(num) < 1024.0 or unit == "TB":
            return f"{num:.0f} {unit}" if unit == "B" else f"{num:.1f} {unit}"
        num /= 1024.0
    return f"{num:.1f} TB"


def human_dur(seconds: float) -> str:
    seconds = max(0, int(seconds))
    d, rem = divmod(seconds, 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    if d:
        return f"{d}d {h}h"
    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"


def ago(ts: float) -> str:
    if not ts:
        return "—"
    return human_dur(time.time() - ts) + " ago"


def bar(pct: float, width: int = 10) -> str:
    pct = max(0.0, min(100.0, float(pct or 0)))
    filled = int(round(pct / 100 * width))
    return "█" * filled + "░" * (width - filled)


STATUS_DOT = {
    "running": "🟢",
    "starting": "🟡",
    "stopped": "⚪️",
    "crashed": "🔴",
    "autofixing": "🛠",
    "queued": "🕓",
    "stopping": "🟠",
    "banned": "⛔️",
}

STATUS_LABEL = {
    "running": "ᴏɴʟɪɴᴇ",
    "starting": "ꜱᴛᴀʀᴛɪɴɢ",
    "stopped": "ꜱᴛᴏᴘᴘᴇᴅ",
    "crashed": "ᴄʀᴀꜱʜᴇᴅ",
    "autofixing": "ᴀᴜᴛᴏ-ꜰɪxɪɴɢ",
    "queued": "Qᴜᴇᴜᴇᴅ",
    "stopping": "ꜱᴛᴏᴘᴘɪɴɢ",
}


def status_chip(status: str) -> str:
    return f"{STATUS_DOT.get(status, '⚪️')} {sc(STATUS_LABEL.get(status, status))}"


def header(title: str, sub: str | None = None, icon: str = "⚡") -> str:
    out = f"{icon} <b>{sc(title)}</b>"
    if sub:
        out += f"  <i>{sub}</i>"
    return out


def kv(key: str, value: str, bullet: str = "├") -> str:
    return f"{bullet} {sc(key)}  {value}"


def clamp(text: str, limit: int = 3900) -> str:
    if len(text) <= limit:
        return text
    return text[: limit - 24].rstrip() + "\n<i>… truncated</i>"
