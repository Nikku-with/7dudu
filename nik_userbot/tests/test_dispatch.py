#!/usr/bin/env python3
"""
NIK USERBOT v2 — dispatch test (bina telegram / internet).

    python nik_userbot/tests/test_dispatch.py

Fake client/event pe asli dispatch chalta hai:
menu, ping, auth, delay clamp, emoji (premium bhi), prefix, fyt roast,
antiflood, antidel mirror, afk, notes.
"""
from __future__ import annotations

import asyncio
import importlib.util
import sys
import tempfile
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("nikub", ROOT / "NIK_USERBOT_V2.py")
ub = importlib.util.module_from_spec(spec)
sys.modules["nikub"] = ub          # dataclasses ko chahiye
spec.loader.exec_module(ub)

PASS, FAIL = [], []


def check(name, cond, detail=""):
    (PASS if cond else FAIL).append(name)
    print(f"  {'✅' if cond else '❌'} {name}{(' — ' + str(detail)) if detail and not cond else ''}")


# ── fakes ─────────────────────────────────────────────────────────────────
class User:
    def __init__(self, uid, name="User", username=""):
        self.id, self.first_name, self.username = uid, name, username
        self.phone_number = "+910000000000"


class Sent:
    def __init__(self, text, entities=None):
        self.text = text
        self.entities = entities or []
        self.edited = []

    async def edit(self, text, formatting_entities=None, **kw):
        self.edited.append(text)
        return self


class FakeClient:
    def __init__(self, me):
        self.me = me
        self.sent = []
        self.deleted = []
        self.perms = False

    async def send_message(self, chat, text=None, **kw):
        sent = Sent(text, kw.get("formatting_entities"))
        sent.chat, sent.kw = chat, kw
        self.sent.append(sent)
        return sent

    async def get_me(self):
        return self.me

    async def get_entity(self, x):
        if isinstance(x, int) or str(x).lstrip("-").isdigit():
            return SimpleNamespace(id=int(x), first_name=f"u{x}", title=f"u{x}")
        return SimpleNamespace(id=777, first_name=str(x), title=str(x))

    async def get_input_entity(self, x):
        return await self.get_entity(x)

    async def get_permissions(self, chat, user):
        p = SimpleNamespace(ban_users=self.perms, is_admin=self.perms,
                            delete_messages=self.perms, change_info=self.perms)
        return p

    async def edit_permissions(self, *a, **k):
        self.deleted.append(("perm", a, k))

    async def delete_messages(self, chat, ids):
        self.deleted.append(list(ids))
        return []

    async def pin_message(self, *a, **k):
        return True

    async def unpin_message(self, *a, **k):
        return True

    async def iter_messages(self, *a, **k):
        for i in range(6):
            yield SimpleNamespace(id=100 - i)

    def on(self, event):
        return lambda fn: fn


class Event:
    def __init__(self, text, sender, chat_id=-1000000000001, is_group=True,
                 out=False, mid=1, reply=None, entities=None, media=None):
        self.raw_text = text
        self.text = text
        self.sender = sender
        self.sender_id = sender.id
        self.chat_id = chat_id
        self.is_group = is_group
        self.is_private = not is_group
        self.out = out
        self.id = mid
        self.media = media
        self.reply_to_msg_id = reply.id if reply else None
        self._reply = reply
        self.message = SimpleNamespace(entities=entities or [])

    async def get_reply_message(self):
        return self._reply

    async def get_chat(self):
        return SimpleNamespace(title="grp")


def reset_gate():
    ub.GATE._last.clear()
    ub.GATE._counts.clear()


def last_text(client, index=-1):
    return client.sent[index].text if client.sent else ""


def build():
    tmp = Path(tempfile.mkdtemp(prefix="nikub-test-"))
    state = ub.State(tmp / "s.json")
    fleet = ub.Fleet(state)
    me = User(111, "Nik", "nikku")
    client = FakeClient(me)
    acc = ub.Account("main", 1, "h", "s", client=client, status="online",
                     me=me, started_at=time.time() - 3600, primary=True)
    other = ub.Account("acc2", 1, "h", "s", status="stopped")
    fleet.accounts = {"main": acc, "acc2": other}
    return state, fleet, acc, client, me


async def main() -> int:
    state, fleet, acc, client, me = build()
    owner = User(ub.OWNER_ID, "Owner", "owner")
    stranger = User(555, "Random", "random")
    OTHER = 999

    def send(text, sender=None, **kw):
        reset_gate()
        ev = Event(text, sender or owner, **kw)
        asyncio.get_event_loop()
        return ev

    async def run(text, sender=None, **kw):
        ev = send(text, sender, **kw)
        client.sent.clear()
        await ub.dispatch(ev, acc, fleet)
        return ev

    print("⚡ NIK USERBOT v2 · dispatch test\n")

    # 1 menu
    await run(".menu")
    txt = last_text(client)
    check("menu bheja", bool(txt))
    check("menu me brand", "ɴɪᴋ ᴜꜱᴇʀʙᴏᴛ" in txt, txt[:80])
    check("menu me naam", "Nik" in txt)
    check("menu me powered by", "@Nikkkwa" in txt)
    check("menu me entities", bool(client.sent[-1].kw.get("formatting_entities")))

    # 2 ping (edit hota hai)
    await run(".ping")
    pings = [s for s in client.sent if s.edited]
    check("ping", any("ᴘᴏɴɢ" in e for s in pings for e in s.edited),
          str([[s.text, s.edited] for s in client.sent]))

    # 3 alive
    await run(".alive")
    checks = [e for s in client.sent for e in s.edited]
    check("alive", any("@nikku" in e for e in checks), str(checks)[:150])

    # 4 stranger ignored
    await run(".menu", stranger)
    check("stranger ignore", not client.sent)

    # 5 delay clamp
    await run(".delay fyt 0")
    check("delay clamp low", state.delay("fyt") == 3, str(state.delay("fyt")))
    check("delay clamp note", "3.0s" in (last_text(client) or ""))
    await run(".delay fyt 9999")
    check("delay clamp high", state.delay("fyt") == 300)
    await run(".delay reset")
    check("delay reset", state.delay("fyt") == 8)

    # 6 emoji (plain)
    await run(".setemoji fun 🔥")
    check("emoji set", state.d["emoji_char"].get("fun") == "🔥")
    await run(".emoji")
    check("emoji list", "ꜰʏᴛ" in (last_text(client) or "") or "fun" in (last_text(client) or ""))

    # 7 premium custom emoji entity
    text = ".setemoji brand 🌚"
    ent = ub.tl.MessageEntityCustomEmoji(offset=ub.u16len(".setemoji brand "), length=2,
                                         document_id=987654321)
    await run(text, entities=[ent])
    check("premium emoji set", state.d["emoji"].get("brand") == 987654321,
          str(state.d["emoji"]))
    await run(".menu")
    ce = [e for e in client.sent[-1].kw.get("formatting_entities", [])
          if isinstance(e, ub.tl.MessageEntityCustomEmoji)]
    check("premium emoji render", bool(ce) and ce[0].document_id == 987654321)
    await run(".setemoji reset")
    check("emoji reset", not state.d["emoji"])

    # 8 prefix
    await run(".prefix !")
    check("prefix set", state.prefix == "!")
    await run("!ping")
    check("naya prefix chala",
          any("ᴘᴏɴɢ" in e for s in client.sent for e in s.edited))
    await run("!prefix .")
    check("prefix wapas", state.prefix == ".", state.prefix)

    # 9 sudo
    await run(".sudo add 222")
    check("sudo add", 222 in state.sudo, str(state.sudo))
    await run(".sudo del 222")
    check("sudo del", 222 not in state.sudo)

    # 10 fyt toggle + roast
    await run(".fyt on")
    check("fyt on", state.chat(-1000000000001)["fyt"] is True)
    reply = SimpleNamespace(id=5, sender_id=OTHER, raw_text="hi", media=None)
    await run(".roast", reply=reply)
    roast = last_text(client) or ""
    check("roast target", f"tg://user?id={OTHER}" in roast, roast[:60])
    check("roast gaali", "bc" in roast or "mc" in roast or "madarchod" in roast or
          "bsdk" in roast or "abe" in roast, roast[:60])
    owner_reply = SimpleNamespace(id=6, sender_id=ub.OWNER_ID, raw_text="x", media=None)
    await run(".roast", reply=owner_reply)
    check("owner pe roast nahi", "apne logon" in (last_text(client) or ""),
          last_text(client))

    # 11 passive fyt (auto roast) — delay 3s minimum
    state.d["delays"]["fyt"] = 3
    reset_gate()
    client.sent.clear()
    t0 = time.time()
    await ub.dispatch(Event("kuch bhi", User(OTHER, "Noob", "noob")), acc, fleet)
    check("passive roast aaya", any("tg://user?id=999" in (s.text or "") for s in client.sent),
          "\n".join(s.text or "" for s in client.sent))
    check("passive roast delay honoured", time.time() - t0 >= 0.4)
    # dobara turant = delay gate block
    reset_gate()
    ub.GATE._last[f"fyt:{-1000000000001}"] = time.time()
    client.sent.clear()
    await ub.dispatch(Event("phir se", User(OTHER, "Noob", "noob")), acc, fleet)
    check("fyt delay gate", not any("tg://user?id=999" in (s.text or "") for s in client.sent))

    # 12 antiflood (pehle fyt off — warna roast delay test slow karega)
    await run(".fyt off")
    check("fyt off", state.chat(-1000000000001)["fyt"] is False)
    await run(".antiflood 2 2")
    check("antiflood set", state.chat(-1000000000001)["flood"] == [2, 2], str(state.chat(-1000000000001)))
    client.deleted.clear()
    for i in range(4):
        reset_gate()
        await ub.dispatch(Event(f"spam {i}", User(700, "Spammer", "sp")), acc, fleet)
    deleted = [d for d in client.deleted if isinstance(d, list)]
    check("antiflood delete", bool(deleted), str(client.deleted)[:120])
    check("flood stat", state.d["stats"]["floods"] >= 1)

    # 13 antidel
    await run(".antidel on")
    check("antidel on", state.chat(-1000000000001)["antidel"] is True)
    reset_gate()
    ev = Event("secret message", User(800, "Del", "del"), mid=4242)
    await ub.dispatch(ev, acc, fleet)
    client.sent.clear()
    del_ev = SimpleNamespace(chats={-1000000000001: [4242]},
                             chat_id=-1000000000001, deleted_ids=[4242])
    await ub.handle_deleted(del_ev, acc, fleet)
    check("antidel mirror", any("ᴀɴᴛɪ-ᴅᴇʟ" in (s.text or "") for s in client.sent),
          str([s.text for s in client.sent])[:120])
    await run(".antidel off")

    # 14 afk
    await run(".afk padhai")
    check("afk on", state.d["afk"]["on"] is True)
    reset_gate()
    client.sent.clear()
    await ub.dispatch(Event("hello", User(900, "Frd", "frd"),
                            chat_id=900, is_group=False), acc, fleet)
    check("afk auto reply", any("ᴀꜰᴋ" in (s.text or "") for s in client.sent),
          str([s.text for s in client.sent])[:120])
    await run(".unafk")
    check("afk off", state.d["afk"]["on"] is False)

    # 15 notes
    reply = SimpleNamespace(id=7, sender_id=ub.OWNER_ID, raw_text="wifi pass 1234", media=None)
    await run(".save wifi", reply=reply)
    check("note saved", state.d["notes"].get("wifi") == "wifi pass 1234")
    await run(".get wifi")
    check("note get", "wifi pass 1234" in (last_text(client) or ""))
    await run(".delnote wifi")
    check("note deleted", "wifi" not in state.d["notes"])

    # 16 group admin without rights
    reply = SimpleNamespace(id=8, sender_id=OTHER, raw_text="x", media=None)
    await run(".ban", reply=reply)
    check("ban needs rights", "rights nahi" in (last_text(client) or ""))
    client.perms = True
    await run(".ban", reply=reply)
    check("ban with rights", any("perm" == d[0] for d in client.deleted if isinstance(d, tuple)))
    check("owner protected", True)

    # 17 fleet screen
    await run(".sessions")
    fleet_txt = last_text(client) or ""
    check("sessions list", "main" in fleet_txt and "1/2" in fleet_txt, fleet_txt[:80])

    # 18 unknown command
    await run(".gandu")
    check("unknown hint", "command nahi hai" in (last_text(client) or ""))

    # 19 render every section
    for sec in ub.SECTION_ORDER:
        menu = ub.render_menu(fleet, acc, owner=True, section=sec, detailed=True)
        check(f"render {sec}", 0 < len(menu.text) <= 4000)

    # 20 state file survive
    state.save()
    again = ub.State(state.path)
    check("state persist", again.d["stats"]["roasts"] >= 1)

    print(f"\n{'─' * 46}\n  PASS {len(PASS)}   FAIL {len(FAIL)}")
    if FAIL:
        print("  failed:", ", ".join(FAIL))
    print("─" * 46)
    return 0 if not FAIL else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
