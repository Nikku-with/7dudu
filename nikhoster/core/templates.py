"""
NIK HOSTER v1 — starter userbot runner.

Session-string deploy pe yahi file generate hoti hai. Minimal + fast:
sirf zaroori commands, koi extra import nahi, boot ~1 second.
"""
from __future__ import annotations

SESSION_RUNNER = r'''
# ─────────────────────────────────────────────────────────────
#  NIK HOSTER v1 · starter userbot  (auto-generated, edit freely)
# ─────────────────────────────────────────────────────────────
import asyncio
import os
import time

from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["NK_API_ID"])
API_HASH = os.environ["NK_API_HASH"]
SESSION = os.environ["NK_SESSION"]
PREFIX = os.environ.get("NK_PREFIX", ".")
SUDO = {int(x) for x in os.environ.get("NK_SUDO", "").replace(",", " ").split() if x.lstrip("-").isdigit()}
START = time.time()

client = TelegramClient(StringSession(SESSION), API_ID, API_HASH,
                        device_model="NIK-HOST", system_version="v1",
                        app_version="1.0", lang_code="en")


def auth(event):
    return event.out or event.sender_id in SUDO


def up(seconds):
    seconds = int(seconds)
    d, r = divmod(seconds, 86400)
    h, r = divmod(r, 3600)
    m, s = divmod(r, 60)
    return f"{d}d {h}h {m}m {s}s" if d else (f"{h}h {m}m {s}s" if h else f"{m}m {s}s")


@client.on(events.NewMessage(pattern=rf"\{PREFIX}ping$"))
async def ping(event):
    t0 = time.perf_counter()
    msg = await event.reply("🏓 ᴘᴏɴɢ")
    dt = (time.perf_counter() - t0) * 1000
    await msg.edit(f"🏓 <b>ᴘᴏɴɢ</b> <code>{dt:.0f} ms</code>\n"
                   f"├ ᴜᴘᴛɪᴍe <code>{up(time.time() - START)}</code>\n"
                   f"└ ʜᴏsᴛ <code>ɴɪᴋ ʜᴏsᴛᴇʀ</code>", parse_mode="html")


@client.on(events.NewMessage(pattern=rf"\{PREFIX}alive$"))
async def alive(event):
    me = await client.get_me()
    await event.reply(f"⚡ <b>ᴀʟɪᴠᴇ</b>\n"
                      f"├ ᴀᴄᴄᴏᴜɴᴛ <code>{me.first_name or ''}</code>\n"
                      f"├ ᴜsᴇʀɴᴀᴍᴇ <code>@{me.username or '—'}</code>\n"
                      f"└ ᴜᴘᴛɪᴍᴇ <code>{up(time.time() - START)}</code>", parse_mode="html")


@client.on(events.NewMessage(pattern=rf"\{PREFIX}id$"))
async def whoami(event):
    chat = await event.get_chat()
    await event.reply(f"🪪 <b>ɪᴅ</b>\n"
                      f"├ ᴜsᴇʀ <code>{event.sender_id}</code>\n"
                      f"├ ᴄʜᴀᴛ <code>{event.chat_id}</code>\n"
                      f"└ ᴛʏᴘᴇ <code>{type(chat).__name__}</code>", parse_mode="html")


@client.on(events.NewMessage(pattern=rf"\{PREFIX}help$"))
async def help_menu(event):
    if not auth(event):
        return
    await event.reply(
        "⚡ <b>ɴɪᴋ ʜᴏsᴛᴇʀ · ꜱᴛᴀʀᴛᴇʀ ᴜsᴇʀʙᴏᴛ</b>\n\n"
        f"<code>{PREFIX}ping</code>   ʟᴀᴛᴇɴᴄʏ\n"
        f"<code>{PREFIX}alive</code>  ᴀᴄᴄᴏᴜɴᴛ ɪɴꜰᴏ\n"
        f"<code>{PREFIX}id</code>     ɪᴅꜱ\n"
        f"<code>{PREFIX}help</code>   ʏᴇʜ ᴍᴇɴᴜ\n\n"
        "<i>apna full userbot upload karna ho to hoster me</i> "
        "📤 <b>ᴜᴘʟᴏᴀᴅ .ᴘʏ</b> <i>use karo</i>", parse_mode="html")


async def main():
    await client.start()
    me = await client.get_me()
    print(f"[nik-hoster] online as {me.first_name} (@{me.username})", flush=True)
    print("[nik-hoster] prefix =", PREFIX, flush=True)
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
'''
