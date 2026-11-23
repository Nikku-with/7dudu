"""
NIK HOSTER v1 — buttons ka dimaag.

Har callback ek route hai: `nk:<route>:<args…>`
`run()` screen lauta ta hai, app.py use edit kar deta hai.
"""
from __future__ import annotations

import re
import threading
import time

from .. import config
from ..core import fonts as F
from ..core import sessions as SESS
from ..ui import screens as S
from ..ui.render import notify, show

STATE: dict[int, dict] = {}
LIVE: dict[int, dict] = {}
_LIVE_TOKEN = 0
_LIVE_LOCK = threading.Lock()

ADMIN_ROUTES = {
    "admin", "ausers", "auser", "aplan", "aban", "aunban", "astartu", "astopu",
    "amass", "massrun", "aevents", "aset", "afind", "abc",
}


# ── state helpers ──────────────────────────────────────────────────────────
def set_state(uid: int, flow: str, **data) -> None:
    STATE[int(uid)] = {"flow": flow, "ts": time.time(), **data}


def clear_state(uid: int) -> None:
    STATE.pop(int(uid), None)


def get_state(uid: int) -> dict | None:
    st = STATE.get(int(uid))
    if not st:
        return None
    if time.time() - st.get("ts", 0) > config.STATE_TTL:
        STATE.pop(int(uid), None)
        return None
    return st


def stop_live(uid: int) -> None:
    LIVE.pop(int(uid), None)


# ── gates ──────────────────────────────────────────────────────────────────
def gate(ctx, uid: int):
    if config.is_admin(uid):
        return None
    row = ctx.db.user(uid)
    if row and row["banned"]:
        return S.banned_screen(ctx)
    if ctx.db.get_setting("maintenance", "0") == "1":
        return S.maintenance_screen(ctx, uid)
    if not row and ctx.db.get_setting("signups", "1") == "0":
        return S.maintenance_screen(ctx, uid)
    return None


def can_add_bot(ctx, uid: int) -> tuple[bool, str]:
    if config.is_admin(uid):
        return True, ""
    plan = ctx.db.plan_of(uid)
    lim = config.limits_for(plan)
    used = ctx.db.count_bots(uid)
    if used >= lim["bots"]:
        return False, f"plan limit: {lim['bots']} bots. upgrade karo → 💎 ᴘʟᴀɴꜱ"
    return True, ""


def find_bot(ctx, uid: int, query: str):
    """id / exact naam / partial naam se bot dhoondo — panel se tez."""
    q = (query or "").strip().lstrip("@").lower()
    bots = ctx.db.bots_of(uid) if not config.is_admin(uid) else ctx.db.all_bots()
    if not bots:
        return None
    if q.isdigit():
        for row in bots:
            if int(row["id"]) == int(q):
                return row
    if q:
        for row in bots:
            if row["name"].lower() == q:
                return row
        for row in bots:
            if q in row["name"].lower():
                return row
    return None


def _prompt(title: str, body: str, hint: str = "", back: str = "home") -> S.Screen:
    text = "\n".join([
        S.brand(), F.LINE, F.header(title, "", icon="✏️"), "",
        body, "", hint,
    ])
    return S.Screen(text, [[S.b("✖️ ᴄᴀɴᴄᴇʟ", back)]], f"prompt:{title}")


def _err(title: str, body: str, buttons: list[list[S.Btn]] | None = None) -> S.Screen:
    text = "\n".join([S.brand(), F.LINE, f"❌ <b>{F.sc(title)}</b>", "", body])
    return S.Screen(text, buttons or [[S.b("‹ ʜᴏᴍᴇ", "home")]], "err")


# ── main router ────────────────────────────────────────────────────────────
def run(ctx, uid: int, payload: str) -> tuple[S.Screen | None, str | None]:
    parts = (payload or "home").split(":")
    route = parts[0] or "home"
    args = parts[1:]
    stop_live(uid)

    blocked = gate(ctx, uid)
    if blocked:
        return blocked, None

    if route in ADMIN_ROUTES and not config.is_admin(uid):
        return S.home(ctx, uid), "admin only"

    db, engine = ctx.db, ctx.engine

    # ── plain screens ──────────────────────────────────────────────────────
    if route in {"home", "menu", "noop2"}:
        return S.home(ctx, uid), None
    if route == "noop":
        return None, None
    if route == "deploy":
        return S.deploy_hub(ctx, uid), None
    if route == "mybots":
        return S.my_bots(ctx, uid, int(args[0]) if args and args[0].isdigit() else 0), None
    if route == "plans":
        return S.plans_screen(ctx, uid), None
    if route == "stats":
        return S.stats_screen(ctx, uid), None
    if route == "support":
        return S.support_screen(ctx, uid), None

    # ── bot control ────────────────────────────────────────────────────────
    if route == "bot" and args:
        scr = S.bot_panel(ctx, uid, int(args[0]))
        return (scr, None) if scr else (S.home(ctx, uid), "bot nahi mila")

    if route in {"start", "stop", "restart"} and args:
        bid = int(args[0])
        row = db.bot(bid)
        if not row or (int(row["user_id"]) != int(uid) and not config.is_admin(uid)):
            return None, "permission nahi"
        fn = {"start": engine.start, "stop": engine.stop_fast,
              "restart": engine.restart_fast}[route]
        ok, msg = fn(bid)
        scr = S.bot_panel(ctx, uid, bid)
        return (scr, None) if ok else (scr, msg)

    if route == "all" and args:
        mode = args[0]
        bots = db.bots_of(uid)
        n = 0
        for row in bots:
            if mode == "start" and not engine.is_running(row["id"]):
                n += 1 if engine.start(row["id"])[0] else 0
            elif mode == "stop" and engine.is_running(row["id"]):
                n += 1 if engine.stop_fast(row["id"])[0] else 0
        return S.my_bots(ctx, uid, 0), f"{n} bots {'started' if mode == 'start' else 'stopped'}"

    if route == "logs" and args:
        return S.bot_logs(ctx, uid, int(args[0])), None
    if route == "logsfull" and args:
        return S.bot_logs(ctx, uid, int(args[0]), full=True), None
    if route == "clearlogs" and args:
        engine.clear_logs(int(args[0]))
        return S.bot_logs(ctx, uid, int(args[0])), "logs clear"

    if route == "tools" and args:
        scr = S.bot_tools(ctx, uid, int(args[0]))
        return (scr, None) if scr else (S.home(ctx, uid), "bot nahi mila")

    if route == "toggle" and len(args) >= 2:
        bid, flag = int(args[0]), args[1]
        row = db.bot(bid)
        if not row:
            return None, "bot nahi mila"
        new = 0 if row[flag] else 1
        db.set_bot_flag(bid, flag, new)
        return S.bot_tools(ctx, uid, bid), f"{flag}: {'on' if new else 'off'}"

    if route == "del" and args:
        scr = S.delete_confirm(ctx, uid, int(args[0]))
        return (scr, None) if scr else (S.home(ctx, uid), "bot nahi mila")
    if route == "delyes" and args:
        bid = int(args[0])
        row = db.bot(bid)
        if row and (int(row["user_id"]) == int(uid) or config.is_admin(uid)):
            engine.delete(bid)
            return S.my_bots(ctx, uid, 0), "delete ho gaya"
        return None, "permission nahi"

    if route == "rename" and args:
        bid = int(args[0])
        set_state(uid, f"rename:{bid}")
        return _prompt("ʀᴇɴᴀᴍᴇ ʙᴏᴛ", f"bot <code>#{bid}</code> ka naya naam bhejo",
                       "<i>sirf letters, numbers, - aur _</i>", f"tools:{bid}"), None
    if route == "sendin" and args:
        bid = int(args[0])
        set_state(uid, f"sendin:{bid}")
        return _prompt("ꜱᴇɴᴅ ɪɴᴘᴜᴛ", f"bot <code>#{bid}</code> ke process me line bhejo",
                       "<i>stdin me jaayega — scripts ke liye useful</i>", f"tools:{bid}"), None
    if route == "env" and args:
        bid = int(args[0])
        env = db.env_of(bid)
        lines = [S.brand(), F.LINE, F.header("ᴇɴᴠ ᴠᴀʀꜱ", f"bot #{bid}", icon="🔐"), ""]
        if not env:
            lines.append("<i>koi env var set nahi hai.</i>")
        for k, v in env.items():
            hidden = k.upper() in {"NK_SESSION", "NK_API_HASH"} or "TOKEN" in k.upper() \
                     or "HASH" in k.upper() or "PASS" in k.upper()
            shown = (v[:6] + "…" + v[-4:]) if hidden and len(v) > 12 else v
            lines.append(f"├ <code>{F.esc(k)}</code> = <code>{F.esc(shown[:42])}</code>")
        lines += ["", "<i>set karne ke liye <code>KEY=VALUE</code> bhejo</i>"]
        set_state(uid, f"env:{bid}")
        return S.Screen(F.clamp("\n".join(lines)),
                        [[S.b("‹ ᴛᴏᴏʟꜱ", f"tools:{bid}")]], f"env:{bid}"), None

    # ── sessions vault ─────────────────────────────────────────────────────
    if route == "sessions":
        return S.sessions_screen(ctx, uid), None
    if route == "sessdeploy" and args:
        raw = db.session(int(args[0]))
        if not raw or int(raw["user_id"]) != int(uid):
            return None, "session nahi mila"
        ok, why = can_add_bot(ctx, uid)
        if not ok:
            return None, why
        t0 = time.perf_counter()
        try:
            bid = engine.deploy_session(uid, raw["label"], raw["api_id"], raw["api_hash"],
                                        raw["session"])
        except Exception as exc:
            return _err("ᴅᴇᴘʟᴏʏ ꜰᴀɪʟ", F.esc(str(exc))), None
        engine.start(bid)
        row = db.bot(bid)
        note = (f"⚡ <code>{time.perf_counter() - t0:.2f}s</code> me deploy · "
                f"<i>vault se uthaya</i>")
        return S.success_screen(ctx, row, note), None
    if route == "sessdel" and args:
        db.del_session(int(args[0]))
        return S.sessions_screen(ctx, uid), "session delete"

    # ── quick deploy wizard ────────────────────────────────────────────────
    if route == "wiz":
        mode = args[0] if args else "start"
        if mode == "start":
            ok, why = can_add_bot(ctx, uid)
            if not ok:
                return _err("ꜱʟᴏᴛ ꜰᴜʟʟ", why, [[S.b("💎 ᴘʟᴀɴꜱ", "plans")],
                                                [S.b("‹ ʜᴏᴍᴇ", "home")]]), None
            set_state(uid, "wiz", step="api_id", data={}, t0=time.time())
            return S.wizard_step(ctx, "api_id", {}), None
        if mode == "upload":
            kind = args[1] if len(args) > 1 else "py"
            set_state(uid, f"upload:{kind}")
            ext = ".zip" if kind == "zip" else ".py"
            body = (f"📤 <b>{ext}</b> file bhejo\n\n"
                    f"<i>max</i> <code>{config.MAX_UPLOAD_MB} MB</code>")
            if kind == "zip":
                body += "\n<i>entry point khud detect ho jaayega</i>"
            return _prompt("ᴜᴘʟᴏᴀᴅ", body, "<i>file bhejte hi deploy shuru</i>", "deploy"), None
        if mode == "back":
            st = get_state(uid)
            data = dict(st.get("data", {})) if st else {}
            return S.wizard_step(ctx, "api_id", data), None

    # ── admin ──────────────────────────────────────────────────────────────
    if route == "admin":
        return S.admin_home(ctx, uid), None
    if route == "ausers":
        return S.admin_users(ctx, int(args[0]) if args and args[0].isdigit() else 0), None
    if route == "auser" and args:
        scr = S.admin_user(ctx, int(args[0]))
        return (scr, None) if scr else (S.admin_users(ctx, 0), "user nahi mila")
    if route == "aplan" and len(args) >= 2:
        target, plan = int(args[0]), args[1]
        db.set_plan(target, plan, days=30 if plan != "free" else 0)
        db.log_event(f"plan {plan} → {target}", "admin", uid, 0)
        return S.admin_user(ctx, target), f"plan: {plan}"
    if route in {"aban", "aunban"} and args:
        target = int(args[0])
        db.set_banned(target, route == "aban")
        if route == "aban":
            for row in db.bots_of(target):
                engine.stop(row["id"])
        db.log_event(f"{route} → {target}", "admin", uid, 0)
        return S.admin_user(ctx, target), "done"
    if route in {"astartu", "astopu"} and args:
        target = int(args[0])
        n = 0
        for row in db.bots_of(target):
            if route == "astartu" and not engine.is_running(row["id"]):
                n += 1 if engine.start(row["id"])[0] else 0
            elif route == "astopu" and engine.is_running(row["id"]):
                n += 1 if engine.stop_fast(row["id"])[0] else 0
        return S.admin_user(ctx, target), f"{n} bots"
    if route == "amass":
        return S.admin_mass(ctx), None
    if route == "massrun" and args:
        mode = args[0]
        n = 0
        for row in db.all_bots():
            if mode == "start" and not engine.is_running(row["id"]):
                n += 1 if engine.start(row["id"])[0] else 0
            elif mode == "stop" and engine.is_running(row["id"]):
                n += 1 if engine.stop_fast(row["id"])[0] else 0
            elif mode == "crashed" and row["status"] == "crashed":
                n += 1 if engine.start(row["id"])[0] else 0
        db.log_event(f"mass {mode} x{n}", "admin", uid, 0)
        return S.admin_mass(ctx), f"{n} bots"
    if route == "aevents":
        return S.admin_events(ctx), None
    if route == "aset":
        if args and args[0] == "toggle" and len(args) > 1:
            msg = toggle_setting(ctx, args[1])
            return S.admin_settings(ctx), msg
        return S.admin_settings(ctx), None
    if route == "afind":
        set_state(uid, "afind")
        return _prompt("ꜰɪɴᴅ ᴜꜱᴇʀ", "user id ya @username bhejo",
                       "<i>example:</i> <code>8905002151</code>", "admin"), None
    if route == "abc":
        set_state(uid, "abc")
        n = db.scalar("SELECT COUNT(*) FROM users")
        return _prompt("ʙʀᴏᴀᴅᴄᴀꜱᴛ", f"message bhejo — <code>{n}</code> users ko jaayega",
                       "<i>HTML allowed: &lt;b&gt; &lt;code&gt; &lt;i&gt;</i>", "admin"), None

    return S.home(ctx, uid), None


# ── wizard helpers (text steps) ────────────────────────────────────────────
def wizard_text(ctx, uid: int, chat_id: int, text: str) -> bool:
    st = get_state(uid)
    if not st or st.get("flow") != "wiz":
        return False
    step = st.get("step")
    data = dict(st.get("data", {}))
    text = (text or "").strip()

    if step == "api_id":
        if not text.isdigit() or not (3 <= len(text) <= 12):
            show(ctx, chat_id, _err("ɢᴀʟᴀᴛ ᴀᴘɪ ɪᴅ", "sirf numbers bhejo, jaise <code>36526099</code>",
                                    [[S.b("🔄 ᴅᴏʙᴀʀᴀ", "wiz:start")], [S.b("‹ ʜᴏᴍᴇ", "home")]]))
            return True
        data["api_id"] = int(text)
        set_state(uid, "wiz", step="api_hash", data=data, t0=st.get("t0", time.time()))
        show(ctx, chat_id, S.wizard_step(ctx, "api_hash", data))
        return True

    if step == "api_hash":
        if not re.fullmatch(r"[0-9a-fA-F]{32}", text):
            show(ctx, chat_id, _err("ɢᴀʟᴀᴛ ᴀᴘɪ ʜᴀꜱʜ",
                                    "32 characters ka hex hash chahiye. phir se bhejo.",
                                    [[S.b("‹ ʙᴀᴄᴋ", "wiz:start")]]))
            return True
        data["api_hash"] = text.lower()
        set_state(uid, "wiz", step="session", data=data, t0=st.get("t0", time.time()))
        show(ctx, chat_id, S.wizard_step(ctx, "session", data))
        return True

    if step == "session":
        cleaned = SESS.clean(text)
        if not SESS.looks_like_session(cleaned):
            show(ctx, chat_id, _err(
                "ꜱᴇꜱꜱɪᴏɴ ɢᴀʟᴀᴛ",
                "ye session string jaisi nahi lag rahi.\n"
                "<i>ye <code>1BVts…</code> se start hoti hai aur lambi hoti hai.</i>",
                [[S.b("🔄 ᴅᴏʙᴀʀᴀ", "wiz:start")]]))
            return True
        data["session"] = cleaned
        set_state(uid, "wiz", step="name", data=data, t0=st.get("t0", time.time()))
        show(ctx, chat_id, S.wizard_step(ctx, "name", data))
        return True

    if step == "name":
        name = ctx.engine.safe_name(text, "account")
        if len(name) < 2:
            show(ctx, chat_id, _err("ɴᴀᴀᴍ ᴄʜʜᴏᴛᴀ", "kam se kam 2 letters chahiye."))
            return True
        data["name"] = name
        clear_state(uid)
        show(ctx, chat_id, S.wizard_step(ctx, "verify", data))
        threading.Thread(target=_verify_and_deploy,
                         args=(ctx, uid, chat_id, data), daemon=True).start()
        return True
    return False


def _verify_and_deploy(ctx, uid: int, chat_id: int, data: dict) -> None:
    t0 = time.time()
    res = SESS.verify(data["api_id"], data["api_hash"], data["session"])
    if not res.get("ok"):
        scr = _err("ꜱᴇꜱꜱɪᴏɴ ꜰᴀɪʟ",
                   f"<blockquote>{F.esc(str(res.get('error', 'unknown')))}</blockquote>\n"
                   "<i>naya session banao aur dobara try karo.</i>",
                   [[S.b("🔄 ᴅᴏʙᴀʀᴀ", "wiz:start")], [S.b("‹ ʜᴏᴍᴇ", "home")]])
        show(ctx, chat_id, scr)
        return

    ok, why = can_add_bot(ctx, uid)
    if not ok:
        show(ctx, chat_id, _err("ꜱʟᴏᴛ ꜰᴜʟʟ", why,
                                [[S.b("💎 ᴘʟᴀɴꜱ", "plans")], [S.b("‹ ʜᴏᴍᴇ", "home")]]))
        return

    try:
        label = data["name"]
        ctx.db.add_session(uid, label, data["api_id"], data["api_hash"],
                           data["session"], res.get("phone", ""))
        bid = ctx.engine.deploy_session(uid, label, data["api_id"], data["api_hash"],
                                        data["session"])
        ctx.engine.start(bid)
    except Exception as exc:
        show(ctx, chat_id, _err("ᴅᴇᴘʟᴏʏ ꜰᴀɪʟ", F.esc(str(exc))))
        return

    row = ctx.db.bot(bid)
    who = F.esc(res.get("name", "account"))
    uname = f" @{F.esc(res['username'])}" if res.get("username") else ""
    note = (f"👤 {who}{uname}\n"
            f"⚡ <code>{time.time() - t0:.2f}s</code> me live · vault me save ho gaya")
    show(ctx, chat_id, S.success_screen(ctx, row, note))


# ── other text flows ───────────────────────────────────────────────────────
def flow_text(ctx, uid: int, chat_id: int, text: str) -> bool:
    st = get_state(uid)
    if not st:
        return False
    flow = st["flow"]
    text = (text or "").strip()
    db, engine = ctx.db, ctx.engine

    if flow.startswith("rename:"):
        bid = int(flow.split(":")[1])
        name = engine.safe_name(text, "")
        if len(name) < 2:
            show(ctx, chat_id, _err("ɴᴀᴀᴍ ɢᴀʟᴀᴛ", "kam se kam 2 letters chahiye."))
            return True
        db.rename_bot(bid, name)
        clear_state(uid)
        show(ctx, chat_id, S.bot_tools(ctx, uid, bid))
        return True

    if flow.startswith("sendin:"):
        bid = int(flow.split(":")[1])
        ok, msg = engine.send_input(bid, text)
        clear_state(uid)
        show(ctx, chat_id, S.bot_panel(ctx, uid, bid))
        notify(ctx, chat_id, f"⌨️ <i>{F.esc(msg)}</i>")
        return True

    if flow.startswith("env:"):
        bid = int(flow.split(":")[1])
        if "=" not in text:
            show(ctx, chat_id, _err("ꜰᴏʀᴍᴀᴛ", "aisa bhejo: <code>API_KEY=12345</code>"))
            return True
        key, _, value = text.partition("=")
        key = re.sub(r"[^A-Za-z0-9_]", "_", key.strip())[:40].upper()
        db.set_env(bid, key, value.strip()[:800])
        clear_state(uid)
        show(ctx, chat_id, S.bot_panel(ctx, uid, bid))
        notify(ctx, chat_id, f"🔐 <code>{F.esc(key)}</code> set · restart karo apply ke liye")
        return True

    if flow == "afind":
        clear_state(uid)
        target = None
        q = text.lstrip("@")
        if q.isdigit():
            target = int(q)
        else:
            row = db.one("SELECT id FROM users WHERE lower(username)=lower(?)", (q,))
            if row:
                target = row["id"]
        scr = S.admin_user(ctx, target) if target else None
        if not scr:
            show(ctx, chat_id, S.admin_users(ctx, 0, query=q))
            return True
        show(ctx, chat_id, scr)
        return True

    if flow == "abc":
        clear_state(uid)
        broadcast(ctx, uid, chat_id, text)
        return True
    return False


def handle_upload(ctx, uid: int, chat_id: int, file_name: str, data: bytes) -> None:
    db, engine = ctx.db, ctx.engine
    ok, why = can_add_bot(ctx, uid)
    if not ok:
        notify(ctx, chat_id, f"⚠️ {why}")
        return
    t0 = time.perf_counter()
    try:
        bid = engine.deploy_upload(uid, file_name, data)
        engine.start(bid)
    except Exception as exc:
        notify(ctx, chat_id, f"❌ deploy fail: <code>{F.esc(str(exc))}</code>")
        return
    row = db.bot(bid)
    note = (f"📦 <code>{F.esc(file_name)}</code> · <code>{len(data) / 1024:.0f} KB</code>\n"
            f"⚡ <code>{time.perf_counter() - t0:.2f}s</code> me deploy ho gaya")
    show(ctx, chat_id, S.success_screen(ctx, row, note))


# ── live logs ──────────────────────────────────────────────────────────────
def start_live(ctx, uid: int, chat_id: int, message_id: int, bot_id: int,
               seconds: int = 75) -> None:
    global _LIVE_TOKEN
    with _LIVE_LOCK:
        _LIVE_TOKEN += 1
        token = _LIVE_TOKEN
        LIVE[int(uid)] = {"bot": bot_id, "chat": chat_id, "mid": message_id,
                          "until": time.time() + seconds, "token": token}
    threading.Thread(target=_live_loop, args=(ctx, uid, bot_id, token), daemon=True).start()


def _live_loop(ctx, uid: int, bot_id: int, token: int) -> None:
    while True:
        time.sleep(config.LIVE_LOG_REFRESH)
        info = LIVE.get(int(uid))
        if (not info or info["bot"] != bot_id or info["token"] != token
                or time.time() > info["until"]):
            break
        scr = S.bot_logs(ctx, uid, bot_id, lines=18)
        if not scr:
            break
        show(ctx, info["chat"], scr, info["mid"])
    with _LIVE_LOCK:
        info = LIVE.get(int(uid))
        if info and info["token"] == token:
            LIVE.pop(int(uid), None)


# ── broadcast ──────────────────────────────────────────────────────────────
def broadcast(ctx, uid: int, chat_id: int, text: str) -> None:
    users = [r["id"] for r in ctx.db.all("SELECT id FROM users")]
    total = len(users)
    if not total:
        notify(ctx, chat_id, "koi user nahi hai")
        return
    msg = ctx.bot.send_message(chat_id, f"📢 <b>{F.sc('broadcast')}</b> · 0/{total}",
                               parse_mode="HTML")

    def _worker():
        sent = failed = 0
        for i, target in enumerate(users, 1):
            try:
                ctx.bot.send_message(target, text, parse_mode="HTML",
                                     disable_web_page_preview=True)
                sent += 1
            except Exception:
                failed += 1
            if i % 25 == 0 or i == total:
                try:
                    ctx.bot.edit_message_text(
                        f"📢 <b>{F.sc('broadcast')}</b> · {i}/{total}\n"
                        f"✅ <code>{sent}</code>  ❌ <code>{failed}</code>",
                        chat_id, msg.message_id, parse_mode="HTML")
                except Exception:
                    pass
            time.sleep(config.BROADCAST_SLEEP)
        ctx.db.log_event(f"broadcast {sent}/{total}", "admin", uid, 0)
        try:
            ctx.bot.edit_message_text(
                f"✅ <b>{F.sc('broadcast done')}</b>\n"
                f"sent <code>{sent}</code> · failed <code>{failed}</code>",
                chat_id, msg.message_id, parse_mode="HTML")
        except Exception:
            pass

    threading.Thread(target=_worker, daemon=True).start()


# ── admin settings toggle ──────────────────────────────────────────────────
def toggle_setting(ctx, key: str) -> str:
    cur = ctx.db.get_setting(key, "1" if key != "maintenance" else "0")
    new = "0" if cur == "1" else "1"
    ctx.db.set_setting(key, new)
    return f"{key}: {'on' if new == '1' else 'off'}"
