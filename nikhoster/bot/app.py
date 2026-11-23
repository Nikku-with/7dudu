"""
NIK HOSTER v1 — Telegram entry point.

Speed rules jo yahan follow hote hain:
  1. callback ka ACK pehle (spinner kabhi nahi ghumta)
  2. message edit-in-place (chat me spam nahi)
  3. heavy kaam threads me (polling block nahi hota)
  4. live logs ke liye background refresher
"""
from __future__ import annotations

import logging
import os
import signal
import sys
import threading
import time
from logging.handlers import RotatingFileHandler

import telebot
from telebot import apihelper

from .. import config
from ..core import fonts as F
from ..core.app_context import Runtime, set_rt
from ..core.db import DB
from ..core.engine import Engine
from ..ui import screens as S
from ..ui.render import notify, show
from . import actions

log = logging.getLogger("nikhoster")

HELP_TEXT = (
    f"⚡ <b>{F.sc('commands')}</b>\n\n"
    "<code>/start</code>   ᴅᴀꜱʜʙᴏᴀʀᴅ\n"
    "<code>/menu</code>    ᴍᴀɪɴ ᴍᴇɴᴜ\n"
    "<code>/ping</code>    ʟᴀᴛᴇɴᴄʏ\n"
    "<code>/id</code>      ᴛᴜᴍʜᴀʀᴀ ɪᴅ\n"
    "<code>/help</code>    ʏᴇʜ ʟɪꜱᴛ\n\n"
    f"⚡ <b>{F.sc('power shortcuts')}</b>\n\n"
    "<code>/bots</code>         ᴍʏ ʙᴏᴛꜱ ʟɪꜱᴛ\n"
    "<code>/run king</code>    ʙᴏᴛ ꜱᴛᴀʀᴛ (naam/id)\n"
    "<code>/kill king</code>   ʙᴏᴛ ꜱᴛᴏᴘ\n"
    "<code>/logs king</code>   ʟɪᴠᴇ ʟᴏɢꜱ\n\n"
    f"<i>admin:</i> <code>/admin</code> <code>/stats</code> "
    "<code>/broadcast</code> <code>/plan</code> <code>/ban</code>"
)


# ── logging ────────────────────────────────────────────────────────────────
def setup_logging() -> None:
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
                            "%H:%M:%S")
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    for h in list(root.handlers):
        root.removeHandler(h)
    stream = logging.StreamHandler(sys.stdout)
    stream.setFormatter(fmt)
    root.addHandler(stream)
    try:
        fh = RotatingFileHandler(config.LOGS_DIR / "hoster.log", maxBytes=2_000_000,
                                 backupCount=2, encoding="utf-8")
        fh.setFormatter(fmt)
        root.addHandler(fh)
    except Exception:
        pass
    logging.getLogger("telebot").setLevel(logging.WARNING)


# ── tiny health server (Render / Koyeb / uptime monitors) ──────────────────
def start_health_server(port: int) -> None:
    from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            body = b"NIK HOSTER v1 - alive\n"
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, *args):
            return

    try:
        ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
    except Exception as exc:
        log.warning("health server failed: %s", exc)


# ── build runtime ──────────────────────────────────────────────────────────
def build():
    if not config.BOT_TOKEN:
        raise SystemExit(
            "BOT_TOKEN missing.\n"
            "  export BOT_TOKEN=123:abc   (ya .env file banao)\n"
            "  .env.example dekho."
        )
    config.USERS_DIR.mkdir(parents=True, exist_ok=True)

    db = DB(config.DB_PATH)
    ctx = Runtime(db=db, engine=None, cfg=config, bot=None)
    engine = Engine(
        db,
        notify=lambda uid, text: notify(ctx, uid, text),
        python_bin=config.PYTHON_BIN,
        users_dir=config.USERS_DIR,
        logs_dir=config.LOGS_DIR,
        max_restarts=config.MAX_RESTARTS,
        backoff=config.RESTART_BACKOFF,
        watchdog=config.WATCHDOG_INTERVAL,
        stop_grace=config.STOP_GRACE,
        autofix=config.AUTOFIX,
        log_cap_mb=config.LOG_HARD_CAP_MB,
        ring=config.LOG_RING,
        env_inject=config.ENV_INJECT,
    )
    ctx.engine = engine
    set_rt(ctx)
    return ctx


# ── handlers ───────────────────────────────────────────────────────────────
def register(bot, ctx):
    db, engine = ctx.db, ctx.engine

    def greet(message):
        user = message.from_user
        return db.touch_user(user.id, user.username or "", user.first_name or "")

    def open_home(chat_id: int, uid: int) -> None:
        """Gate (ban/maintenance) + home ek hi jagah se."""
        screen, toast = actions.run(ctx, uid, "home")
        if screen is not None:
            show(ctx, chat_id, screen)
        if toast:
            flash(chat_id, f"› {F.esc(toast)}")

    def flash(chat_id: int, text: str) -> None:
        """Chhota feedback message jo 4s me khud delete ho jaata hai."""
        def _job():
            try:
                msg = bot.send_message(chat_id, text, parse_mode="HTML")
                time.sleep(4)
                bot.delete_message(chat_id, msg.message_id)
            except Exception:
                pass
        threading.Thread(target=_job, daemon=True).start()

    # ── commands ───────────────────────────────────────────────────────────
    @bot.message_handler(commands=["start"])
    def cmd_start(message):
        before = db.user(message.from_user.id)
        greet(message)
        if not before:
            db.log_event(f"new user @{message.from_user.username or message.from_user.id}",
                         "admin")
            blocked = actions.gate(ctx, message.from_user.id)
            show(ctx, message.chat.id,
                 blocked or S.welcome(ctx, message.from_user.id))
        else:
            open_home(message.chat.id, message.from_user.id)

    @bot.message_handler(commands=["menu", "home"])
    def cmd_menu(message):
        greet(message)
        open_home(message.chat.id, message.from_user.id)

    @bot.message_handler(commands=["ping"])
    def cmd_ping(message):
        greet(message)
        t0 = time.perf_counter()
        msg = bot.reply_to(message, "🏓 …")
        dt = (time.perf_counter() - t0) * 1000
        host = engine.host_stats()
        bot.edit_message_text(
            f"🏓 <b>{F.sc('pong')}</b>  <code>{dt:.0f} ms</code>\n"
            f"├ {F.sc('engine')} <code>{F.human_dur(host['uptime'])}</code>\n"
            f"├ {F.sc('bots live')} <code>{host['engine_procs']}</code>\n"
            f"└ {F.sc('cpu')} <code>{host['cpu']:.0f}%</code> · "
            f"{F.sc('ram')} <code>{host['ram_pct']:.0f}%</code>",
            message.chat.id, msg.message_id, parse_mode="HTML")

    @bot.message_handler(commands=["id"])
    def cmd_id(message):
        bot.reply_to(message, f"🪪 <code>{message.from_user.id}</code>\n"
                              f"💬 chat <code>{message.chat.id}</code>",
                     parse_mode="HTML")

    @bot.message_handler(commands=["help"])
    def cmd_help(message):
        greet(message)
        bot.send_message(message.chat.id, HELP_TEXT, parse_mode="HTML")

    @bot.message_handler(commands=["bots", "list"])
    def cmd_bots(message):
        greet(message)
        screen, toast = actions.run(ctx, message.from_user.id, "mybots:0")
        if screen is not None:
            show(ctx, message.chat.id, screen)
        if toast:
            flash(message.chat.id, f"› {F.esc(toast)}")

    def _shortcut(message, mode: str) -> None:
        uid = message.from_user.id
        greet(message)
        query = message.text.partition(" ")[2].strip()
        row = actions.find_bot(ctx, uid, query)
        if not row:
            bot.reply_to(message,
                         "❌ bot nahi mila — <code>/bots</code> se naam dekho",
                         parse_mode="HTML")
            return
        bid = row["id"]
        if mode == "logs":
            show(ctx, message.chat.id, S.bot_logs(ctx, uid, bid))
            return
        ok, msg = (engine.start(bid) if mode == "run" else engine.stop_fast(bid))
        show(ctx, message.chat.id, S.bot_panel(ctx, uid, bid))
        if not ok:
            flash(message.chat.id, f"› {F.esc(msg)}")

    @bot.message_handler(commands=["run"])
    def cmd_run(message):
        _shortcut(message, "run")

    @bot.message_handler(commands=["kill", "stop"])
    def cmd_kill(message):
        _shortcut(message, "kill")

    @bot.message_handler(commands=["logs"])
    def cmd_logs(message):
        _shortcut(message, "logs")

    @bot.message_handler(commands=["admin"])
    def cmd_admin(message):
        if not config.is_admin(message.from_user.id):
            return
        show(ctx, message.chat.id, S.admin_home(ctx, message.from_user.id))

    @bot.message_handler(commands=["stats"])
    def cmd_stats(message):
        if not config.is_admin(message.from_user.id):
            return
        show(ctx, message.chat.id, S.admin_home(ctx, message.from_user.id))

    @bot.message_handler(commands=["broadcast"])
    def cmd_broadcast(message):
        if not config.is_admin(message.from_user.id):
            return
        text = message.text.partition(" ")[2].strip()
        if not text:
            actions.set_state(message.from_user.id, "abc")
            bot.reply_to(message, "📢 broadcast text bhejo")
            return
        actions.broadcast(ctx, message.from_user.id, message.chat.id, text)

    @bot.message_handler(commands=["plan"])
    def cmd_plan(message):
        if not config.is_admin(message.from_user.id):
            return
        parts = message.text.split()
        if len(parts) < 3 or not parts[1].lstrip("-").isdigit():
            bot.reply_to(message, "usage: <code>/plan 12345 pro</code>", parse_mode="HTML")
            return
        uid, plan = int(parts[1]), parts[2].lower()
        if plan not in config.PLANS:
            bot.reply_to(message, "plans: " + ", ".join(config.PLANS))
            return
        db.set_plan(uid, plan, days=30 if plan != "free" else 0)
        bot.reply_to(message, f"✅ <code>{uid}</code> → <b>{plan}</b>", parse_mode="HTML")

    @bot.message_handler(commands=["ban", "unban"])
    def cmd_ban(message):
        if not config.is_admin(message.from_user.id):
            return
        parts = message.text.split()
        if len(parts) < 2 or not parts[1].lstrip("-").isdigit():
            bot.reply_to(message, "usage: <code>/ban 12345</code>", parse_mode="HTML")
            return
        target = int(parts[1])
        banned = message.text.startswith("/ban")
        db.set_banned(target, banned)
        if banned:
            for row in db.bots_of(target):
                engine.stop_fast(row["id"])
        bot.reply_to(message, f"{'⛔️ banned' if banned else '🔓 unbanned'} <code>{target}</code>",
                     parse_mode="HTML")

    @bot.message_handler(commands=["stopall"])
    def cmd_stopall(message):
        if not config.is_admin(message.from_user.id):
            return
        n = 0
        for row in db.all_bots():
            if engine.is_running(row["id"]):
                n += 1 if engine.stop_fast(row["id"])[0] else 0
        bot.reply_to(message, f"⛔️ {n} bots stop")

    # ── callbacks ──────────────────────────────────────────────────────────
    @bot.callback_query_handler(func=lambda c: True)
    def on_callback(call):
        # 1) turant ack — spinner khatam, user ko lagta hai click hua
        try:
            bot.answer_callback_query(call.id)
        except Exception:
            pass
        user = call.from_user
        db.touch_user(user.id, user.username or "", user.first_name or "")
        payload = call.data or "nk:home"
        if payload.startswith("nk:"):
            payload = payload[3:]
        route = payload.split(":")[0]
        args = payload.split(":")[1:]

        try:
            screen, toast = actions.run(ctx, user.id, payload)
        except Exception as exc:
            log.exception("action failed: %s", payload)
            screen, toast = S.home(ctx, user.id), f"error: {exc}"
            notify(ctx, call.message.chat.id, f"❌ <code>{F.esc(str(exc))}</code>")

        if screen is not None:
            try:
                mid = show(ctx, call.message.chat.id, screen, call.message.message_id)
            except Exception:
                mid = None
            if route == "logs" and mid and args and args[0].isdigit():
                # live logs: 75s tak khud refresh hota rahega
                actions.start_live(ctx, user.id, call.message.chat.id, mid, int(args[0]))
        if toast:
            flash(call.message.chat.id, f"› {F.esc(toast)}")

    # ── documents ──────────────────────────────────────────────────────────
    @bot.message_handler(content_types=["document"])
    def on_document(message):
        greet(message)
        doc = message.document
        name = doc.file_name or "script.py"
        if not name.lower().endswith((".py", ".zip", ".js")):
            bot.reply_to(message, "❌ sirf <code>.py</code>, <code>.zip</code> ya "
                                  "<code>.js</code> bhejo", parse_mode="HTML")
            return
        size_mb = (doc.file_size or 0) / (1024 * 1024)
        if size_mb > config.MAX_UPLOAD_MB:
            bot.reply_to(message, f"❌ file <code>{size_mb:.1f} MB</code> hai — "
                                  f"limit <code>{config.MAX_UPLOAD_MB} MB</code>",
                         parse_mode="HTML")
            return
        wait = bot.reply_to(message, f"📥 receiving <code>{F.esc(name)}</code> …",
                            parse_mode="HTML")
        try:
            file_info = bot.get_file(doc.file_id)
            data = bot.download_file(file_info.file_path)
        except Exception as exc:
            bot.edit_message_text(f"❌ download fail: <code>{F.esc(str(exc))}</code>",
                                  message.chat.id, wait.message_id, parse_mode="HTML")
            return
        try:
            bot.delete_message(message.chat.id, wait.message_id)
        except Exception:
            pass
        actions.handle_upload(ctx, message.from_user.id, message.chat.id, name, data)

    # ── text (wizard + flows) ──────────────────────────────────────────────
    @bot.message_handler(content_types=["text"])
    def on_text(message):
        greet(message)
        text = (message.text or "").strip()
        if text.startswith("/"):
            return
        uid = message.from_user.id
        if actions.wizard_text(ctx, uid, message.chat.id, text):
            return
        if actions.flow_text(ctx, uid, message.chat.id, text):
            return
        if actions.get_state(uid):
            # kisi flow ke beech galat input
            bot.reply_to(message, "⚠️ pehle current step poora karo, ya /start dabao")
            return
        open_home(message.chat.id, uid)

    @bot.message_handler(content_types=["photo", "video", "audio", "voice", "sticker"])
    def on_other(message):
        bot.reply_to(message, "📤 bot chalane ke liye <code>.py</code> file bhejo, "
                              "photo nahi 🙂", parse_mode="HTML")


# ── main ───────────────────────────────────────────────────────────────────
def main() -> None:
    setup_logging()
    log.info("starting NIK HOSTER %s", config.VERSION)
    ctx = build()

    apihelper.CONNECT_TIMEOUT = 15
    apihelper.READ_TIMEOUT = 25
    bot = telebot.TeleBot(config.BOT_TOKEN, parse_mode="HTML",
                          threaded=True, num_threads=16)
    ctx.bot = bot

    me = None
    try:
        me = bot.get_me()
        log.info("connected as @%s (id %s)", me.username, me.id)
    except Exception as exc:
        raise SystemExit(f"Telegram connect fail: {exc}")

    register(bot, ctx)

    port = os.getenv("PORT")
    if port and port.isdigit():
        threading.Thread(target=start_health_server, args=(int(port),), daemon=True).start()
        log.info("health server on :%s", port)

    def _boot():
        try:
            n = ctx.engine.boot()
            log.info("autostart: %s bots back online", n)
        except Exception:
            log.exception("boot failed")

    threading.Thread(target=_boot, daemon=True).start()

    def _bye(signum, frame):
        log.info("shutting down…")
        ctx.engine.shutdown()
        ctx.db.close()
        raise SystemExit(0)

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            signal.signal(sig, _bye)
        except Exception:
            pass

    log.info("polling started")
    try:
        bot.infinity_polling(timeout=25, long_polling_timeout=20,
                             skip_pending=True, allowed_updates=["message", "callback_query"])
    except KeyboardInterrupt:
        pass
    finally:
        ctx.engine.shutdown()
        ctx.db.close()


if __name__ == "__main__":
    main()
