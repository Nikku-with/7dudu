"""
NIK HOSTER v1 — screen builders (100% pure, koi telegram import nahi).

Har screen `Screen(text, rows)` lauta ta hai. Isi se bot ka message aur
preview/index.html dono bante hain — matlab jo preview me dikhta hai,
bilkul wahi Telegram me aayega.
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from .. import config
from ..core import fonts as F


@dataclass
class Btn:
    label: str
    data: str | None = None
    url: str | None = None


@dataclass
class Screen:
    text: str
    rows: list[list[Btn]] = field(default_factory=list)
    screen_id: str = ""
    toast: str = ""

    def rows_spec(self):
        return [[(b.label, b.data, b.url) for b in row] for row in self.rows]


def b(label: str, data: str) -> Btn:
    return Btn(label=label, data=f"nk:{data}")


def u(label: str, url: str) -> Btn:
    return Btn(label=label, url=url)


# ── shared bits ─────────────────────────────────────────────────────────────
def brand(sub: str = "", icon: str = "⚡") -> str:
    out = f"{icon} <b>{F.sc(config.BRAND)}</b>  <i>{config.VERSION}</i>"
    if sub:
        out += f"\n<i>{sub}</i>"
    return out


def user_line(row) -> str:
    name = F.esc((row["name"] or row["username"] or str(row["id"]))[:20])
    uname = f"@{F.esc(row['username'])}" if row["username"] else F.mono(row["id"])
    plan = config.limits_for(row["plan"] or "free")["label"]
    return f"👤 <b>{name}</b>  {uname}  ·  {F.sc('plan')} <b>{plan}</b>"


def pager(page: int, total: int, per: int, route: str) -> list[Btn]:
    pages = max(1, (total + per - 1) // per)
    if pages == 1:
        return []
    row = []
    if page > 0:
        row.append(b("‹", f"{route}:{page - 1}"))
    row.append(Btn(label=f"{page + 1}/{pages}", data="nk:noop"))
    if page + 1 < pages:
        row.append(b("›", f"{route}:{page + 1}"))
    return row


def status_of(db, engine, bot_row) -> tuple[str, dict]:
    rt = engine.runtime(bot_row["id"])
    return rt["status"], rt


# ── user screens ───────────────────────────────────────────────────────────
def home(ctx, uid: int) -> Screen:
    db, engine = ctx.db, ctx.engine
    row = db.user(uid)
    plan = db.plan_of(uid)
    lim = config.limits_for(plan)
    bots = db.bots_of(uid)
    running = sum(1 for b in bots if engine.is_running(b["id"]))
    host = engine.host_stats()

    lines = [
        brand(config.TAGLINE),
        F.LINE,
        user_line(row) if row else "",
        f"🤖 {F.sc('bots')} <code>{len(bots)}/{lim['bots']}</code>   "
        f"🟢 {F.sc('running')} <code>{running}</code>",
        "",
        F.quote(
            f"{F.sc('engine')} ↑ <code>{F.human_dur(host['uptime'])}</code>  "
            f"· {F.sc('ram')} <code>{F.human_bytes(host['ram_used'])}</code>"
            f" / {F.human_bytes(host['ram_total'])}\n"
            f"{F.bar(host['ram_pct'])} <code>{host['ram_pct']:.0f}%</code>   "
            f"{F.sc('cpu')} <code>{host['cpu']:.0f}%</code>   "
            f"{F.sc('bots')} <code>{host['engine_procs']}</code>"
        ),
    ]

    rows = [
        [b("⚡ ᴅᴇᴘʟᴏʏ", "deploy"), b("🤖 ᴍʏ ʙᴏᴛꜱ", "mybots:0")],
        [b("🗂 ꜱᴇꜱꜱɪᴏɴꜱ", "sessions"), b("💎 ᴘʟᴀɴꜱ", "plans")],
        [b("📊 ᴜꜱᴀɢᴇ", "stats"), b("💬 ꜱᴜᴘᴘᴏʀᴛ", "support")],
    ]
    if config.is_admin(uid):
        rows.append([b("🛰 ᴀᴅᴍɪɴ", "admin")])
    return Screen(F.clamp("\n".join(lines)), rows, "home")


def deploy_hub(ctx, uid: int) -> Screen:
    plan = ctx.db.plan_of(uid)
    lim = config.limits_for(plan)
    used = ctx.db.count_bots(uid)
    text = "\n".join([
        brand(),
        F.LINE,
        F.header("ᴅᴇᴘʟᴏʏ", "3 tarike — sabse fast pehle"),
        "",
        "⚡ <b>Qᴜɪᴄᴋ</b> — session string paste karo, ~5s me online",
        "📤 <b>.ᴘʏ</b> — apna ready userbot script upload karo",
        "📦 <b>.ᴢɪᴘ</b> — folder + files, auto entry detect",
        "",
        f"<i>Slots:</i> <code>{used}/{lim['bots']}</code> · "
        f"<i>max size</i> <code>{config.MAX_UPLOAD_MB} MB</code>",
    ])
    rows = [
        [b("⚡ Qᴜɪᴄᴋ ᴅᴇᴘʟᴏʏ", "wiz:start")],
        [b("📤 ᴜᴘʟᴏᴀᴅ .ᴘʏ", "wiz:upload:py"), b("📦 ᴜᴘʟᴏᴀᴅ .ᴢɪᴘ", "wiz:upload:zip")],
        [b("‹ ʙᴀᴄᴋ", "home")],
    ]
    return Screen(text, rows, "deploy")


def my_bots(ctx, uid: int, page: int = 0, per: int = 5) -> Screen:
    db, engine = ctx.db, ctx.engine
    bots = db.bots_of(uid)
    running = sum(1 for x in bots if engine.is_running(x["id"]))
    total = len(bots)
    page = max(0, min(page, max(0, (total - 1) // per) if total else 0))
    chunk = bots[page * per:(page + 1) * per]

    head = [
        brand(),
        F.LINE,
        F.header("ᴍʏ ʙᴏᴛꜱ", f"{total} total", icon="🤖"),
        f"🟢 <code>{running}</code> {F.sc('running')}   "
        f"⚪️ <code>{sum(1 for x in bots if not engine.is_running(x['id']))}</code> {F.sc('idle')}",
        "",
    ]
    if not bots:
        head.append("<i>abhi koi bot nahi hai — ⚡ ᴅᴇᴘʟᴏʏ se shuru karo</i>")
        body = []
    else:
        body = []
        for bot in chunk:
            rt = engine.runtime(bot["id"])
            dot = F.STATUS_DOT.get(rt["status"], "⚪️")
            label = F.STATUS_LABEL.get(rt["status"], rt["status"])
            up = f" · {F.human_dur(rt['uptime'])}" if rt["uptime"] else ""
            ram = f" · {rt['ram_mb']:.0f}MB" if rt["ram_mb"] else ""
            head.append(f"{dot} <b>{F.esc(bot['name'])}</b>  "
                        f"<i>{F.sc(label)}</i>{up}{ram}")
        head.append("")
        body = [[b(f"{F.STATUS_DOT.get(engine.runtime(x['id'])['status'], '⚪️')} "
                   f"{x['name'][:18]}", f"bot:{x['id']}")] for x in chunk]

    rows = list(body)
    if bots:
        rows.append([b("🟢 ᴀʟʟ ᴏɴ", "all:start"), b("⛔️ ᴀʟʟ ᴏꜰꜰ", "all:stop")])
    pg = pager(page, total, per, "mybots")
    if pg:
        rows.append(pg)
    rows.append([b("⚡ ᴅᴇᴘʟᴏʏ", "deploy"), b("‹ ʜᴏᴍᴇ", "home")])
    return Screen(F.clamp("\n".join(head)), rows, f"mybots:{page}")


def bot_panel(ctx, uid: int, bot_id: int) -> Screen | None:
    db, engine = ctx.db, ctx.engine
    row = db.bot(bot_id)
    if not row or int(row["user_id"]) != int(uid) and not config.is_admin(uid):
        return None
    rt = engine.runtime(bot_id)
    dot = F.STATUS_DOT.get(rt["status"], "⚪️")
    label = F.STATUS_LABEL.get(rt["status"], rt["status"])

    lines = [
        brand(),
        F.LINE,
        f"{dot} <b>{F.esc(row['name'])}</b>  <i>{F.sc(label)}</i>",
        "",
        F.kv("ᴛʏᴘᴇ", F.mono(row["kind"])),
        F.kv("ᴘɪᴅ", F.mono(rt["pid"] or "—")),
        F.kv("ᴜᴘᴛɪᴍᴇ", F.mono(F.human_dur(rt["uptime"]) if rt["uptime"] else "—")),
        F.kv("ʀᴀᴍ", F.mono(f"{rt['ram_mb']:.0f} MB" if rt["ram_mb"] else "—"), "├"),
        F.kv("ᴄᴘᴜ", F.mono(f"{rt['cpu']:.0f}%"), "├"),
        F.kv("ʀᴇꜱᴛᴀʀᴛꜱ", F.mono(f"{row['restarts']}/{engine.max_restarts}"), "├"),
        F.kv("ᴀᴜᴛᴏ-ʀᴇꜱᴛᴀʀᴛ", "on" if row["autostart"] else "off", "├"),
        F.kv("ᴀᴜᴛᴏ-ꜰɪx", "on" if row["autofix"] else "off", "└"),
    ]
    if row["last_error"]:
        lines += ["", f"⚠️ <blockquote>{F.esc(str(row['last_error'])[:220])}</blockquote>"]

    running = rt["status"] in {"running", "starting", "queued", "autofixing"}
    if running:
        rows = [
            [b("⏹ ꜱᴛᴏᴘ", f"stop:{bot_id}"), b("♻️ ʀᴇꜱᴛᴀʀᴛ", f"restart:{bot_id}")],
            [b("📜 ʟɪᴠᴇ ʟᴏɢꜱ", f"logs:{bot_id}"), b("⚙️ ᴛᴏᴏʟꜱ", f"tools:{bot_id}")],
        ]
    else:
        rows = [
            [b("▶️ ꜱᴛᴀʀᴛ", f"start:{bot_id}"), b("📜 ʟᴏɢꜱ", f"logs:{bot_id}")],
            [b("⚙️ ᴛᴏᴏʟꜱ", f"tools:{bot_id}")],
        ]
    rows.append([b("‹ ᴍʏ ʙᴏᴛꜱ", "mybots:0"), b("🏠 ʜᴏᴍᴇ", "home")])
    return Screen(F.clamp("\n".join(lines)), rows, f"bot:{bot_id}")


def bot_tools(ctx, uid: int, bot_id: int) -> Screen | None:
    row = ctx.db.bot(bot_id)
    if not row:
        return None
    lines = [
        brand(),
        F.LINE,
        F.header(f"{row['name']}", "tools", icon="⚙️"),
        "",
        f"🔁 {F.sc('auto-restart')}: <b>{'on' if row['autostart'] else 'off'}</b>",
        f"🛠 {F.sc('auto-fix')}: <b>{'on' if row['autofix'] else 'off'}</b>",
        "",
        "<i>auto-restart = bot crash/boot pe khud wapas uthe</i>",
        "<i>auto-fix = missing module khud install ho</i>",
    ]
    rows = [
        [Btn(f"🔁 ᴀᴜᴛᴏ-ʀᴇꜱᴛᴀʀᴛ {'ᴏɴ' if row['autostart'] else 'ᴏꜰꜰ'}",
             f"nk:toggle:{bot_id}:autostart")],
        [Btn(f"🛠 ᴀᴜᴛᴏ-ꜰɪx {'ᴏɴ' if row['autofix'] else 'ᴏꜰꜰ'}",
             f"nk:toggle:{bot_id}:autofix")],
        [b("⌨️ ꜱᴇɴᴅ ɪɴᴘᴜᴛ", f"sendin:{bot_id}"), b("🏷 ʀᴇɴᴀᴍᴇ", f"rename:{bot_id}")],
        [b("🔐 ᴇɴᴠ ᴠᴀʀꜱ", f"env:{bot_id}"), b("🧹 ᴄʟᴇᴀʀ ʟᴏɢꜱ", f"clearlogs:{bot_id}")],
        [b("🗑 ᴅᴇʟᴇᴛᴇ ʙᴏᴛ", f"del:{bot_id}")],
        [b("‹ ʙᴏᴛ", f"bot:{bot_id}"), b("‹ ᴍʏ ʙᴏᴛꜱ", "mybots:0")],
    ]
    return Screen(F.clamp("\n".join(lines)), rows, f"tools:{bot_id}")


def bot_logs(ctx, uid: int, bot_id: int, lines: int = 18, full: bool = False) -> Screen | None:
    db, engine = ctx.db, ctx.engine
    row = db.bot(bot_id)
    if not row:
        return None
    rt = engine.runtime(bot_id)
    body = engine.logs(bot_id, lines=320 if full else lines) or "<i>abhi koi output nahi…</i>"
    size = engine.logs_size(bot_id)
    head = "\n".join([
        brand(),
        F.LINE,
        f"{F.STATUS_DOT.get(rt['status'], '⚪️')} <b>{F.esc(row['name'])}</b> · "
        f"<i>{F.sc(F.STATUS_LABEL.get(rt['status'], rt['status']))}</i>  "
        f"<code>{F.human_bytes(size)}</code>",
        "",
        f"<pre>{F.esc(body[-config.MAX_LOG_CHARS:])}</pre>",
    ])
    rows = [
        [b("🔄 ʀᴇꜰʀᴇꜱʜ", f"logs:{bot_id}"), b("📄 ꜰᴜʟʟ", f"logsfull:{bot_id}")],
        [b("🧹 ᴄʟᴇᴀʀ", f"clearlogs:{bot_id}"), b("♻️ ʀᴇꜱᴛᴀʀᴛ", f"restart:{bot_id}")],
        [b("‹ ʙᴏᴛ", f"bot:{bot_id}"), b("‹ ᴍʏ ʙᴏᴛꜱ", "mybots:0")],
    ]
    return Screen(F.clamp(head), rows, f"logs:{bot_id}")


def delete_confirm(ctx, uid: int, bot_id: int) -> Screen | None:
    row = ctx.db.bot(bot_id)
    if not row:
        return None
    text = "\n".join([
        brand(),
        F.LINE,
        "🗑 <b>ᴅᴇʟᴇᴛᴇ ʙᴏᴛ?</b>",
        "",
        f"<b>{F.esc(row['name'])}</b>",
        "<i>process band hoga + files delete hongi. wapas nahi aayega.</i>",
    ])
    return Screen(text, [
        [b("✅ ʜᴀᴀɴ, ᴅᴇʟᴇᴛᴇ", f"delyes:{bot_id}"), b("✖️ ɴᴀʜɪ", f"tools:{bot_id}")],
    ], f"del:{bot_id}")


def sessions_screen(ctx, uid: int) -> Screen:
    rows_db = ctx.db.sessions_of(uid)
    head = [
        brand(),
        F.LINE,
        F.header("ꜱᴇꜱꜱɪᴏɴ ᴠᴀᴜʟᴛ", f"{len(rows_db)} saved", icon="🗂"),
        "",
        "<i>ek baar save karo — dobara paste karne ki zaroorat nahi.</i>",
    ]
    rows: list[list[Btn]] = []
    if not rows_db:
        head.append("\n<i>abhi kuch save nahi hai.</i>")
    for s in rows_db[:8]:
        head.append(f"• <b>{F.esc(s['label'])}</b>  "
                    f"<code>{s['api_id']}</code>  <i>{F.human_dur(time.time() - s['created'])} ago</i>")
        rows.append([
            b(f"🚀 {s['label'][:14]}", f"sessdeploy:{s['id']}"),
            b("🗑", f"sessdel:{s['id']}"),
        ])
    rows.append([b("➕ ɴᴀʏᴀ ꜱᴇꜱꜱɪᴏɴ ꜱᴀᴠᴇ", "wiz:start")])
    rows.append([b("‹ ʜᴏᴍᴇ", "home")])
    return Screen(F.clamp("\n".join(head)), rows, "sessions")


def plans_screen(ctx, uid: int) -> Screen:
    plan = ctx.db.plan_of(uid)
    head = [brand(), F.LINE, F.header("ᴘʟᴀɴꜱ", "limits & perks", icon="💎"), ""]
    for key, p in config.PLANS.items():
        if key == "owner":
            continue
        marker = " ✅" if key == plan else ""
        head.append(f"<b>{p['label']}</b>{marker} — <i>{p['note']}</i>")
        head.append(f"└ {F.sc('bots')} <code>{p['bots'] if p['bots'] < 999 else '∞'}</code>"
                    f" · {F.sc('ram')} <code>{p['ram_mb']} MB</code>")
    head.append("")
    head.append("<i>plan upgrade ke liye owner ko message karo.</i>")
    rows = [
        [u("💬 ᴏᴡɴᴇʀ ꜱᴇ ʙᴀᴀᴛ", config.SUPPORT_URL)],
        [b("‹ ʜᴏᴍᴇ", "home")],
    ]
    return Screen(F.clamp("\n".join(head)), rows, "plans")


def stats_screen(ctx, uid: int) -> Screen:
    db, engine = ctx.db, ctx.engine
    bots = db.bots_of(uid)
    host = engine.host_stats()
    lines = [
        brand(),
        F.LINE,
        F.header("ᴜꜱᴀɢᴇ", "", icon="📊"),
        "",
        f"{F.sc('bots')} <code>{len(bots)}</code>  ·  "
        f"{F.sc('running')} <code>{sum(1 for x in bots if engine.is_running(x['id']))}</code>",
        "",
        F.kv("ʜᴏꜱᴛ ᴜᴘᴛɪᴍᴇ", F.mono(F.human_dur(host['uptime']))),
        F.kv("ᴄᴘᴜ", f"{F.bar(host['cpu'])} <code>{host['cpu']:.0f}%</code>"),
        F.kv("ʀᴀᴍ", f"{F.bar(host['ram_pct'])} <code>{host['ram_pct']:.0f}%</code>", "├"),
        F.kv("ᴅɪꜱᴋ", f"{F.bar(host['disk_pct'])} <code>{host['disk_pct']:.0f}%</code>", "└"),
    ]
    for bot in bots[:10]:
        rt = engine.runtime(bot["id"])
        lines.append(f"{F.STATUS_DOT.get(rt['status'], '⚪️')} "
                     f"<code>{F.esc(bot['name'][:14]):<14}</code> "
                     f"<code>{rt['ram_mb']:>5.0f}MB</code> "
                     f"<code>{F.human_dur(rt['uptime']) if rt['uptime'] else '—':>8}</code>")
    rows = [[b("🔄 ʀᴇꜰʀᴇꜱʜ", "stats"), b("‹ ʜᴏᴍᴇ", "home")]]
    return Screen(F.clamp("\n".join(lines)), rows, "stats")


def support_screen(ctx, uid: int) -> Screen:
    text = "\n".join([
        brand(),
        F.LINE,
        F.header("ꜱᴜᴘᴘᴏʀᴛ", "", icon="💬"),
        "",
        f"👤 <b>{F.esc(ctx.owner_name())}</b>",
        "<i>plan, payment, bug — sab ke liye yahin message karo.</i>",
        "",
        F.quote("bot chal raha hai but command kaam nahi kar raha?\n"
                "pehle <b>📜 logs</b> kholo — 90% jawab wahin milta hai."),
    ])
    rows = [[u("💬 ᴍᴇꜱꜱᴀɢᴇ", config.SUPPORT_URL)]]
    if config.UPDATES_URL:
        rows.append([u("📣 ᴜᴘᴅᴀᴛᴇꜱ", config.UPDATES_URL)])
    rows.append([b("‹ ʜᴏᴍᴇ", "home")])
    return Screen(text, rows, "support")


# ── admin screens ──────────────────────────────────────────────────────────
def admin_home(ctx, uid: int) -> Screen:
    db, engine = ctx.db, ctx.engine
    f = db.fleet()
    host = engine.host_stats()
    text = "\n".join([
        brand(),
        F.LINE,
        F.header("ꜰʟᴇᴇᴛ", "live", icon="🛰"),
        "",
        f"👥 {F.sc('users')} <code>{f['users']}</code>  "
        f"<i>(+{f['new_today']} 24h)</i>",
        f"🤖 {F.sc('bots')} <code>{f['bots']}</code>  "
        f"🟢 {F.sc('running')} <code>{f['running']}</code>  "
        f"🔴 {F.sc('crashed')} <code>{f['crashed']}</code>",
        "",
        F.quote(
            f"{F.sc('cpu')}  {F.bar(host['cpu'])} <code>{host['cpu']:.0f}%</code>\n"
            f"{F.sc('ram')}  {F.bar(host['ram_pct'])} <code>{host['ram_pct']:.0f}%</code>  "
            f"<code>{F.human_bytes(host['ram_used'])}</code>\n"
            f"{F.sc('disk')} {F.bar(host['disk_pct'])} <code>{host['disk_pct']:.0f}%</code>  "
            f"<i>{F.human_bytes(host['disk_free'])} free</i>"
        ),
        f"<i>engine {F.human_dur(host['uptime'])} · load {host['load']:.2f} · "
        f"{host['cores']} cores</i>",
    ])
    rows = [
        [b("👥 ᴜꜱᴇʀꜱ", "ausers:0"), b("🔍 ꜰɪɴᴅ", "afind")],
        [b("🚀 ᴍᴀꜱꜱ ᴀᴄᴛɪᴏɴ", "amass"), b("📜 ᴇᴠᴇɴᴛꜱ", "aevents")],
        [b("📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ", "abc"), b("⚙️ ꜱᴇᴛᴛɪɴɢꜱ", "aset")],
        [b("‹ ʜᴏᴍᴇ", "home")],
    ]
    return Screen(F.clamp(text), rows, "admin")


def admin_users(ctx, page: int = 0, per: int = 7, query: str = "") -> Screen:
    rows_db, total = ctx.db.users_page(page, per, query)
    head = [
        brand(),
        F.LINE,
        F.header("ᴜꜱᴇʀꜱ", f"{total} total", icon="👥"),
        "",
    ]
    buttons: list[list[Btn]] = []
    for row in rows_db:
        plan = config.limits_for(row["plan"] or "free")["label"]
        bots = ctx.db.count_bots(row["id"])
        tag = "⛔️" if row["banned"] else "•"
        label = (row["name"] or row["username"] or str(row["id"]))[:16]
        head.append(f"{tag} <b>{F.esc(label)}</b>  <code>{row['id']}</code>  "
                    f"{plan} · {bots} bot")
        buttons.append([b(f"{tag} {label}", f"auser:{row['id']}")])
    if not rows_db:
        head.append("<i>koi user nahi mila</i>")
    pg = pager(page, total, per, "ausers")
    if pg:
        buttons.append(pg)
    buttons.append([b("🔍 ꜰɪɴᴅ ᴜꜱᴇʀ", "afind"), b("‹ ᴀᴅᴍɪɴ", "admin")])
    return Screen(F.clamp("\n".join(head)), buttons, f"ausers:{page}")


def admin_user(ctx, target_id: int) -> Screen | None:
    db, engine = ctx.db, ctx.engine
    row = db.user(target_id)
    if not row:
        return None
    bots = db.bots_of(target_id)
    running = sum(1 for x in bots if engine.is_running(x["id"]))
    plan = db.plan_of(target_id)
    until = row["plan_until"] or 0
    text = "\n".join([
        brand(),
        F.LINE,
        f"👤 <b>{F.esc(row['name'] or row['username'] or target_id)}</b>"
        f"{'  ⛔️' if row['banned'] else ''}",
        "",
        F.kv("ɪᴅ", F.mono(row["id"])),
        F.kv("ᴜꜱᴇʀɴᴀᴍᴇ", f"@{F.esc(row['username'])}" if row["username"] else "—"),
        F.kv("ᴘʟᴀɴ", f"<b>{config.limits_for(plan)['label']}</b>" +
              (f"  <i>till {time.strftime('%d %b', time.localtime(until))}</i>" if until else "")),
        F.kv("ʙᴏᴛꜱ", f"<code>{len(bots)}</code>  🟢 <code>{running}</code>", "├"),
        F.kv("ᴊᴏɪɴ", F.human_dur(time.time() - (row["created"] or time.time())) + " ago", "├"),
        F.kv("ʟᴀꜱᴛ", F.human_dur(time.time() - (row["last_seen"] or time.time())) + " ago", "└"),
    ])
    plan_btns = [b(config.limits_for(p)["label"], f"aplan:{target_id}:{p}")
                 for p in config.PLANS if p != "owner"]
    rows = [plan_btns]
    rows.append([b("🚀 ꜱᴛᴀʀᴛ ᴀʟʟ", f"astartu:{target_id}"),
                 b("⛔️ ꜱᴛᴏᴘ ᴀʟʟ", f"astopu:{target_id}")])
    rows.append([
        b("🔓 ᴜɴʙᴀɴ" if row["banned"] else "⛔️ ʙᴀɴ", f"a{ 'unban' if row['banned'] else 'ban'}:{target_id}"),
    ])
    rows.append([b("‹ ᴜꜱᴇʀꜱ", "ausers:0"), b("‹ ᴀᴅᴍɪɴ", "admin")])
    return Screen(F.clamp(text), rows, f"auser:{target_id}")


def admin_mass(ctx) -> Screen:
    db = ctx.db
    f = db.fleet()
    text = "\n".join([
        brand(),
        F.LINE,
        F.header("ᴍᴀꜱꜱ ᴀᴄᴛɪᴏɴ", "poore fleet pe", icon="🚀"),
        "",
        f"deployed <code>{f['bots']}</code> · running <code>{f['running']}</code> · "
        f"crashed <code>{f['crashed']}</code>",
        "",
        "<i>start all = stopped bots uthao</i>",
        "<i>restart crashed = sirf jo crash huye hain</i>",
        "<i>stop all = sab band (confirm ke baad)</i>",
    ])
    rows = [
        [b("🟢 ꜱᴛᴀʀᴛ ᴀʟʟ", "massrun:start")],
        [b("🔴 ʀᴇꜱᴛᴀʀᴛ ᴄʀᴀꜱʜᴇᴅ", "massrun:crashed")],
        [b("⛔️ ꜱᴛᴏᴘ ᴀʟʟ", "massrun:stop")],
        [b("‹ ᴀᴅᴍɪɴ", "admin")],
    ]
    return Screen(text, rows, "amass")


def admin_events(ctx) -> Screen:
    evs = ctx.db.events(12)
    lines = [brand(), F.LINE, F.header("ᴇᴠᴇɴᴛꜱ", "latest 12", icon="📜"), ""]
    for e in evs:
        icon = {"error": "🔴", "deploy": "🚀", "start": "🟢", "stop": "⚪️",
                "delete": "🗑", "admin": "👑"}.get(e["level"], "•")
        ts = time.strftime("%H:%M", time.localtime(e["ts"]))
        lines.append(f"{icon} <code>{ts}</code> {F.esc(e['text'][:80])}")
    if not evs:
        lines.append("<i>koi event nahi</i>")
    return Screen(F.clamp("\n".join(lines)),
                  [[b("🔄 ʀᴇꜰʀᴇꜱʜ", "aevents"), b("‹ ᴀᴅᴍɪɴ", "admin")]], "aevents")


def admin_settings(ctx) -> Screen:
    db = ctx.db
    maint = db.get_setting("maintenance", "0")
    signup = db.get_setting("signups", "1")
    autofix = db.get_setting("autofix_default", "1")
    text = "\n".join([
        brand(),
        F.LINE,
        F.header("ꜱᴇᴛᴛɪɴɢꜱ", "", icon="⚙️"),
        "",
        F.kv("ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ", "🔴 on" if maint == "1" else "🟢 off"),
        F.kv("ɴᴇᴡ ᴜꜱᴇʀꜱ", "🟢 open" if signup == "1" else "🔴 closed"),
        F.kv("ᴀᴜᴛᴏ-ꜰɪx ᴅᴇꜰᴀᴜʟᴛ", "🟢 on" if autofix == "1" else "🔴 off", "└"),
        "",
        "<i>maintenance on = sirf admins bot use kar sakte hain</i>",
    ])
    rows = [
        [b("🛠 ᴛᴏɢɢʟᴇ ᴍᴀɪɴᴛ", "aset:toggle:maintenance"),
         b("👥 ᴛᴏɢɢʟᴇ ꜱɪɢɴᴜᴘ", "aset:toggle:signups")],
        [b("🧰 ᴀᴜᴛᴏ-ꜰɪx ᴅᴇꜰᴀᴜʟᴛ", "aset:toggle:autofix_default")],
        [b("‹ ᴀᴅᴍɪɴ", "admin")],
    ]
    return Screen(text, rows, "aset")


def maintenance_screen(ctx, uid: int) -> Screen:
    text = "\n".join([
        brand(),
        F.LINE,
        "🛠 <b>ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ</b>",
        "",
        "<i>owner abhi kaam kar raha hai. thodi der baad try karo.</i>",
        "",
        f"💬 {config.SUPPORT_URL}",
    ])
    return Screen(text, [[u("💬 ꜱᴜᴘᴘᴏʀᴛ", config.SUPPORT_URL)]], "maint")


def banned_screen(ctx) -> Screen:
    return Screen("\n".join([
        brand(),
        F.LINE,
        "⛔️ <b>ᴀᴄᴄᴇꜱꜱ ʙʟᴏᴄᴋᴇᴅ</b>",
        "",
        "<i>tumhara access band kar diya gaya hai.</i>",
    ]), [[u("💬 ᴄᴏɴᴛᴀᴄᴛ", config.SUPPORT_URL)]], "banned")


def welcome(ctx, uid: int) -> Screen:
    """Sirf pehli baar."""
    text = "\n".join([
        brand(config.TAGLINE),
        F.LINE,
        "",
        "👋 <b>Welcome!</b>",
        "",
        "ᴛᴜᴍʜᴀʀᴀ ᴜꜱᴇʀʙᴏᴛ, ʜᴜᴍᴀʀᴀ ꜱᴇʀᴠᴇʀ.",
        "",
        "⚡ <b>5 ꜱᴇᴄᴏɴᴅ ᴅᴇᴘʟᴏʏ</b> — session string paste, done",
        "📜 <b>ʟɪᴠᴇ ʟᴏɢꜱ</b> — refresh pe turant output",
        "🛠 <b>ᴀᴜᴛᴏ-ꜰɪx</b> — module missing? khud install",
        "♻️ <b>ᴀᴜᴛᴏ-ʀᴇꜱᴛᴀʀᴛ</b> — crash? 3s me wapas online",
        "",
        "<i>shuru karne ke liye ⚡ ᴅᴇᴘʟᴏʏ dabao</i>",
    ])
    return Screen(text, [
        [b("⚡ ᴅᴇᴘʟᴏʏ", "deploy")],
        [b("📖 ɢᴜɪᴅᴇ", "support"), u("💬 ᴏᴡɴᴇʀ", config.SUPPORT_URL)],
    ], "welcome")


def wizard_step(ctx, step: str, data: dict) -> Screen:
    """Quick-deploy wizard ke steps."""
    if step == "api_id":
        text = "\n".join([
            brand(), F.LINE,
            F.header("Qᴜɪᴄᴋ ᴅᴇᴘʟᴏʏ", "step 1/4", icon="⚡"), "",
            "🔑 <b>API ID</b> bhejo",
            "",
            "<i>my.telegram.org → API development tools</i>",
            "<i>example:</i> <code>36526099</code>",
        ])
        return Screen(text, [[b("✖️ ᴄᴀɴᴄᴇʟ", "home")]], "wiz:api_id")
    if step == "api_hash":
        text = "\n".join([
            brand(), F.LINE,
            F.header("Qᴜɪᴄᴋ ᴅᴇᴘʟᴏʏ", "step 2/4", icon="⚡"), "",
            f"<i>api id</i> <code>{data.get('api_id', '')}</code>  ✅",
            "",
            "🔐 <b>API HASH</b> bhejo",
            "<i>32 characters</i>",
        ])
        return Screen(text, [[b("‹ ʙᴀᴄᴋ", "wiz:start"), b("✖️ ᴄᴀɴᴄᴇʟ", "home")]], "wiz:api_hash")
    if step == "session":
        text = "\n".join([
            brand(), F.LINE,
            F.header("Qᴜɪᴄᴋ ᴅᴇᴘʟᴏʏ", "step 3/4", icon="⚡"), "",
            "🧾 <b>SESSION STRING</b> bhejo",
            "",
            "<i>1)</i> <code>pip install telethon</code>",
            "<i>2)</i> <code>python -m telethon.sessions</code> … ya \" stringsession",
            "<i>3)</i> login karke jo string mile, wahi paste karo",
            "",
            "<i>string</i> <code>1BVtsOK…</code> <i>se shuru hoti hai</i>",
        ])
        return Screen(text, [[b("‹ ʙᴀᴄᴋ", "wiz:start"), b("✖️ ᴄᴀɴᴄᴇʟ", "home")]], "wiz:session")
    if step == "name":
        text = "\n".join([
            brand(), F.LINE,
            F.header("Qᴜɪᴄᴋ ᴅᴇᴘʟᴏʏ", "step 4/4", icon="⚡"), "",
            "🏷 <b>BOT KA NAAM</b> bhejo",
            "",
            "<i>jaisa list me dikhega —</i> <code>king</code>, <code>nik-01</code>",
        ])
        return Screen(text, [[b("✖️ ᴄᴀɴᴄᴇʟ", "home")]], "wiz:name")
    if step == "verify":
        text = "\n".join([
            brand(), F.LINE,
            F.header("ᴠᴇʀɪꜰʏ", "checking session…", icon="🔎"), "",
            f"<i>api id</i> <code>{data.get('api_id', '')}</code>",
            f"<i>string</i> <code>{str(data.get('session', ''))[:22]}…</code>",
            "",
            "⏳ <i>account check ho raha hai…</i>",
        ])
        return Screen(text, [], "wiz:verify")
    # unknown step
    return deploy_hub(ctx, 0)


def success_screen(ctx, bot_row, note: str = "") -> Screen:
    text = "\n".join([
        brand(), F.LINE,
        "✅ <b>ᴅᴇᴘʟᴏʏᴇᴅ</b>",
        "",
        f"🤖 <b>{F.esc(bot_row['name'])}</b>  <i>{F.sc(bot_row['kind'])}</i>",
        "",
        note or "<i>pehla output 1–2 sec me aa jaata hai.</i>",
    ])
    bid = bot_row["id"]
    return Screen(text, [
        [b("📜 ʟɪᴠᴇ ʟᴏɢꜱ", f"logs:{bid}")],
        [b("🎛 ʙᴏᴛ ᴘᴀɴᴇʟ", f"bot:{bid}"), b("‹ ᴍʏ ʙᴏᴛꜱ", "mybots:0")],
    ], f"done:{bid}")
