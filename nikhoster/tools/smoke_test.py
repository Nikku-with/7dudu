#!/usr/bin/env python3
"""
NIK HOSTER v1 — smoke test (bina Telegram, bina internet).

Chalane ka tarika:
    python -m nikhoster.tools.smoke_test

Kya check hota hai:
  • sqlite WAL + users/bots/plans
  • deploy .py → start → logs → stop → restart
  • crash + auto-restart backoff
  • zip upload ka entry-point detection
  • session deploy ka runner + env
  • har screen: 4096 limit, 64-byte callback data, HTML tags balanced
"""
from __future__ import annotations

import io
import shutil
import sys
import tempfile
import time
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nikhoster import config  # noqa: E402
from nikhoster.core.app_context import Runtime  # noqa: E402
from nikhoster.core.db import DB  # noqa: E402
from nikhoster.core.engine import Engine  # noqa: E402
from nikhoster.ui import screens as S  # noqa: E402
from types import SimpleNamespace  # noqa: E402

PASS, FAIL = [], []


def check(name: str, cond: bool, detail: str = "") -> None:
    (PASS if cond else FAIL).append(name)
    mark = "✅" if cond else "❌"
    print(f"  {mark} {name}{(' — ' + detail) if detail and not cond else ''}")


def wait_until(fn, timeout=12.0, step=0.15) -> bool:
    end = time.time() + timeout
    while time.time() < end:
        if fn():
            return True
        time.sleep(step)
    return False


SCRIPT_OK = """
import time, sys
print("hello from hosted bot", flush=True)
for i in range(60):
    print(f"tick {i}", flush=True)
    time.sleep(0.4)
"""

SCRIPT_CRASH = """
print("about to die", flush=True)
import definitely_not_a_real_module_xyz
"""

SCRIPT_SLOW_BOOT = """
import time
time.sleep(0.9)
print("online after boot", flush=True)
time.sleep(30)
"""


def build_env(tmp: Path):
    db = DB(tmp / "test.db")
    notices: list[tuple[int, str]] = []
    engine = Engine(
        db, notify=lambda uid, text: notices.append((uid, text)),
        users_dir=tmp / "users", logs_dir=tmp / "logs",
        max_restarts=2, backoff=0.4, watchdog=0.4, stop_grace=2.0,
        autofix=True, log_cap_mb=1, ring=200,
        env_inject={"PYTHONUNBUFFERED": "1"},
    )
    ctx = Runtime(db=db, engine=engine, cfg=config, bot=None)
    return ctx, notices


def test_db(ctx) -> None:
    print("\n[1] database")
    db = ctx.db
    db.touch_user(111, "nik", "Nik")
    check("user insert", db.user(111)["username"] == "nik")
    db.touch_user(111, "nik", "Nik")
    check("touch idempotent", db.scalar("SELECT COUNT(*) FROM users") == 1)
    db.set_plan(111, "pro", days=30)
    check("plan set", db.plan_of(111) == "pro")
    db.set_plan(111, "pro", days=-1)
    check("expired plan -> free", db.plan_of(111) == "free")
    bid = db.add_bot(111, "sample", "py", "/tmp/x.py", "/tmp")
    check("bot insert", db.bot(bid)["name"] == "sample")
    db.set_env(bid, "FOO", "bar")
    check("env roundtrip", db.env_of(bid) == {"FOO": "bar"})
    db.set_bot_status(bid, "running", started=True)
    check("status update", db.bot(bid)["status"] == "running")
    db.log_event("test event", "info", 111, bid)
    check("event log", len(db.events(5)) >= 1)
    f = db.fleet()
    check("fleet counts", f["users"] == 1 and f["bots"] == 1, str(f))
    db.x("INSERT INTO users(id,username,name) VALUES(222,'x','X')")
    rows, total = db.users_page(0, 5, "nik")
    check("user search", total == 1 and rows[0]["id"] == 111)


def test_deploy_start_logs(ctx) -> None:
    print("\n[2] deploy → start → logs → stop")
    eng = ctx.engine
    t0 = time.perf_counter()
    bid = eng.deploy_upload(111, "hello.py", SCRIPT_OK.encode())
    deploy_ms = (time.perf_counter() - t0) * 1000
    check("deploy .py", ctx.db.bot(bid)["kind"] == "py", f"{deploy_ms:.0f}ms")

    t0 = time.perf_counter()
    ok, msg = eng.start(bid)
    start_ms = (time.perf_counter() - t0) * 1000
    check("start returns fast (<1500ms)", ok and start_ms < 1500, f"{start_ms:.0f}ms {msg}")

    check("status becomes running",
          wait_until(lambda: eng.runtime(bid)["status"] == "running", 8),
          eng.runtime(bid)["status"])
    check("logs captured",
          wait_until(lambda: "hello from hosted bot" in eng.logs(bid), 8),
          eng.logs(bid)[-200:])
    rt = eng.runtime(bid)
    check("pid present", bool(rt["pid"]))
    check("uptime > 0", rt["uptime"] > 0)

    ok, _ = eng.stop_fast(bid)
    check("stop returns fast", ok)
    check("process exits",
          wait_until(lambda: not eng.is_running(bid), 8), "still running")
    check("status stopped",
          wait_until(lambda: ctx.db.bot(bid)["status"] in {"stopped"}, 8),
          ctx.db.bot(bid)["status"])
    check("log file on disk", eng.logs_size(bid) > 0)

    ok, _ = eng.restart_fast(bid)
    check("restart accepted", ok)
    check("running again", wait_until(lambda: eng.is_running(bid), 12))
    eng.stop_fast(bid)
    wait_until(lambda: not eng.is_running(bid), 6)


def test_crash_restart(ctx, notices) -> None:
    print("\n[3] crash → auto-restart")
    eng = ctx.engine
    bid = eng.deploy_upload(111, "crasher.py", SCRIPT_CRASH.encode())
    ctx.db.set_bot_flag(bid, "autofix", 0)  # autofix off, restart path test karo
    eng.start(bid)
    check("crash detected",
          wait_until(lambda: ctx.db.bot(bid)["status"] in {"crashed", "queued"}, 10),
          ctx.db.bot(bid)["status"])
    check("restart counter increased",
          wait_until(lambda: (ctx.db.bot(bid)["restarts"] or 0) >= 1, 12),
          str(ctx.db.bot(bid)["restarts"]))
    check("gives up after max_restarts",
          wait_until(lambda: ctx.db.bot(bid)["status"] == "crashed", 25),
          ctx.db.bot(bid)["status"])
    check("owner ko notification gaya", any("crasher" in n[1] for n in notices),
          str(notices[-2:]))
    eng.stop_fast(bid)


def test_zip(ctx) -> None:
    print("\n[4] zip upload")
    eng = ctx.engine
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("project/__init__.py", "")
        zf.writestr("project/main_userbot.py", SCRIPT_SLOW_BOOT)
        zf.writestr("project/readme.txt", "hello")
        zf.writestr("../../evil.py", "print('zip slip')")
    bid = eng.deploy_upload(111, "project.zip", buf.getvalue())
    row = ctx.db.bot(bid)
    check("zip entry detected", row["path"].endswith("main_userbot.py"), row["path"])
    check("zip-slip blocked", not (Path(row["workdir"]).parent.parent.parent / "evil.py").exists())
    ok, _ = eng.start(bid)
    check("zip bot starts", ok)
    check("zip bot logs", wait_until(lambda: "online after boot" in eng.logs(bid), 10),
          eng.logs(bid)[-120:])
    eng.stop_fast(bid)
    wait_until(lambda: not eng.is_running(bid), 6)


def test_session(ctx) -> None:
    print("\n[5] session deploy")
    eng, db = ctx.engine, ctx.db
    db.add_session(111, "acc1", 12345, "a" * 32, "1BVtsOK_fake_session_string_" + "x" * 40,
                   "+911234567890")
    ses = db.sessions_of(111)[0]
    check("session saved", ses["label"] == "acc1")
    bid = eng.deploy_session(111, "acc1", ses["api_id"], ses["api_hash"], ses["session"])
    row = db.bot(bid)
    check("runner generated", Path(row["path"]).name == "runner.py" and
          Path(row["path"]).exists())
    env = db.env_of(bid)
    check("creds in env not in file",
          env.get("NK_API_ID") == "12345" and "1BVtsOK" in env.get("NK_SESSION", ""))
    check("runner uses env", "NK_SESSION" in Path(row["path"]).read_text())
    check("session kind", row["kind"] == "session")
    db.del_session(ses["id"])
    check("session delete", not db.sessions_of(111))


def test_screens(ctx) -> None:
    print("\n[6] screens (text + buttons)")
    eng, db = ctx.engine, ctx.db
    db.touch_user(999, "tester", "Tester <&>")
    bid = eng.deploy_upload(999, "demo.py", SCRIPT_OK.encode())
    eng.start(bid)
    wait_until(lambda: eng.runtime(bid)["status"] == "running", 8)

    screens = {
        "welcome": S.welcome(ctx, 999),
        "home": S.home(ctx, 999),
        "deploy": S.deploy_hub(ctx, 999),
        "mybots": S.my_bots(ctx, 999),
        "panel": S.bot_panel(ctx, 999, bid),
        "tools": S.bot_tools(ctx, 999, bid),
        "logs": S.bot_logs(ctx, 999, bid),
        "delete": S.delete_confirm(ctx, 999, bid),
        "sessions": S.sessions_screen(ctx, 999),
        "plans": S.plans_screen(ctx, 999),
        "stats": S.stats_screen(ctx, 999),
        "support": S.support_screen(ctx, 999),
        "admin": S.admin_home(ctx, 999),
        "users": S.admin_users(ctx, 0),
        "user": S.admin_user(ctx, 999),
        "mass": S.admin_mass(ctx),
        "events": S.admin_events(ctx),
        "settings": S.admin_settings(ctx),
        "wiz1": S.wizard_step(ctx, "api_id", {}),
        "wiz3": S.wizard_step(ctx, "session", {"api_id": 1}),
        "success": S.success_screen(ctx, db.bot(bid)),
    }
    for name, scr in screens.items():
        ok_len = len(scr.text) <= 4096
        check(f"{name}: <=4096 chars", ok_len, f"{len(scr.text)}")
        check(f"{name}: has text", bool(scr.text.strip()))
        bad = [btn for row in scr.rows for btn in row
               if not btn.url and len((btn.data or "").encode()) > 64]
        check(f"{name}: callback data <=64B", not bad, str([x.data for x in bad]))
        check(f"{name}: buttons have target",
              all(btn.url or btn.data for row in scr.rows for btn in row))

    # html tags balanced
    import re
    for name, scr in screens.items():
        tags = re.findall(r"</?([a-z]+)[^>]*>", scr.text)
        allowed = {"b", "i", "code", "pre", "blockquote", "a"}
        check(f"{name}: only allowed tags", set(tags) <= allowed, str(set(tags) - allowed))
        opens = len(re.findall(r"<(b|i|code|pre|blockquote)>", scr.text))
        closes = len(re.findall(r"</(b|i|code|pre|blockquote)>", scr.text))
        check(f"{name}: tags balanced", opens == closes, f"{opens}/{closes}")

    eng.stop_fast(bid)
    wait_until(lambda: not eng.is_running(bid), 6)


def test_limits(ctx) -> None:
    print("\n[7] limits")
    eng = ctx.engine
    db = ctx.db
    db.touch_user(555, "lim", "Limit")
    plan = db.plan_of(555)
    check("default plan free", plan == "free")
    for i in range(config.limits_for("free")["bots"]):
        eng.deploy_upload(555, f"l{i}.py", SCRIPT_OK.encode())
    from nikhoster.bot import actions
    ok, why = actions.can_add_bot(ctx, 555)
    check("free plan cap enforced", not ok, why)
    db.set_plan(555, "pro", days=30)
    ok, _ = actions.can_add_bot(ctx, 555)
    check("pro plan raises cap", ok)


# ── fake telegram (buttons ko bina network test karne ke liye) ─────────────
class FakeBot:
    def __init__(self):
        self.sent = []
        self.edits = []
        self.acked = 0
        self.deleted = 0

    def send_message(self, chat_id, text, **kw):
        self.sent.append((chat_id, text))
        return SimpleNamespace(message_id=len(self.sent))

    def edit_message_text(self, text, chat_id, message_id, **kw):
        self.edits.append(text)
        return True

    def answer_callback_query(self, cid, text=None, **kw):
        self.acked += 1

    def delete_message(self, chat_id, message_id):
        self.deleted += 1


ALL_ROUTES = [
    "home", "deploy", "mybots:0", "bot:1", "bot:2", "logs:1", "logsfull:1",
    "tools:1", "del:1", "toggle:1:autofix", "toggle:1:autostart", "env:1",
    "sessions", "plans", "stats", "support", "noop", "garbage:1:2",
    "start:2", "stop:2", "restart:2", "logs:2", "clearlogs:2",
    "all:start", "all:stop", "sessdel:999", "sessdeploy:999", "delyes:999",
    "admin", "ausers:0", "auser:111", "auser:222", "aplan:111:pro",
    "amass", "massrun:crashed", "aevents", "aset", "aset:toggle:signups",
    "afind", "abc", "astartu:111", "astopu:111", "aban:222", "aunban:222",
    "wiz:start", "wiz:upload:py", "wiz:upload:zip", "wiz:back",
]


def test_actions(ctx) -> None:
    print("\n[8] button routes (fake telegram)")
    from nikhoster.bot import actions
    from nikhoster.ui import render

    config.ADMIN_IDS.add(111)
    ctx.bot = FakeBot()
    db, eng = ctx.db, ctx.engine
    db.touch_user(111, "nik", "Nik")
    db.set_plan(111, "elite", days=30)
    db.touch_user(222, "arjun", "Arjun")

    for i in range(2):
        if not db.bots_of(111):
            eng.deploy_upload(111, f"btn{i}.py", SCRIPT_OK.encode())
    b1 = db.bots_of(111)[0]["id"]
    eng.start(b1)

    broken = []
    for route in ALL_ROUTES:
        try:
            screen, toast = actions.run(ctx, 111, route)
        except Exception as exc:
            broken.append(f"{route}: {type(exc).__name__} {exc}")
            continue
        if screen is not None:
            if len(screen.text) > 4096 or not screen.text.strip():
                broken.append(f"{route}: bad text len {len(screen.text)}")
            for row in screen.rows:
                for btn in row:
                    if not btn.url and len((btn.data or "").encode()) > 64:
                        broken.append(f"{route}: long callback")
    check("saare routes bina crash chale", not broken, "; ".join(broken[:3]))

    # markup build (telebot)
    try:
        kb = render.markup_for(S.home(ctx, 111))
        check("inline markup banti hai", len(kb.keyboard) >= 3)
    except ImportError:
        print("  ⚠️ telebot nahi hai — markup check skip")

    # wizard: verify ko stub karo, real deploy_session chalao
    real_verify = actions.SESS.verify
    real_start = eng.start
    actions.SESS.verify = lambda *a, **k: {"ok": True, "name": "Nik", "username": "nikku",
                                          "phone": ""}
    eng.start = lambda *a, **k: (True, "stub")
    before = len(db.bots_of(111))
    actions.set_state(111, "wiz", step="api_id", data={}, t0=time.time())
    actions.wizard_text(ctx, 111, 1, "36526099")
    actions.wizard_text(ctx, 111, 1, "a" * 32)
    actions.wizard_text(ctx, 111, 1, "1BVtsOK_" + "x" * 60)
    actions.wizard_text(ctx, 111, 1, "wizard-bot")
    ok = wait_until(lambda: len(db.bots_of(111)) > before, 8)
    check("wizard ne bot deploy kiya", ok)
    check("wizard ne session vault me save kiya", bool(db.sessions_of(111)))
    new_name = db.bots_of(111)[-1]["name"] if len(db.bots_of(111)) > before else ""
    check("wizard name sanitized", new_name == "wizard-bot", new_name)
    actions.SESS.verify = real_verify
    eng.start = real_start

    # text flows
    actions.set_state(111, f"rename:{b1}")
    actions.flow_text(ctx, 111, 1, "renamed-bot")
    check("rename flow", db.bot(b1)["name"] == "renamed-bot", db.bot(b1)["name"])

    actions.set_state(111, f"env:{b1}")
    actions.flow_text(ctx, 111, 1, "API_KEY=secret123")
    check("env flow", db.env_of(b1).get("API_KEY") == "secret123")

    actions.set_state(111, "afind")
    before_screens = len(ctx.bot.sent)
    actions.flow_text(ctx, 111, 1, "111")
    check("find user flow", len(ctx.bot.sent) > before_screens)

    actions.set_state(111, "abc")
    actions.flow_text(ctx, 111, 1, "hello <b>all</b>")
    check("broadcast start", wait_until(
        lambda: any("📢" in str(t) or "ʙʀᴏᴀᴅᴄᴀꜱᴛ" in str(t) for _, t in ctx.bot.sent), 6))

    # gate: banned user blocked
    db.set_banned(222, True)
    scr, _ = actions.run(ctx, 222, "home")
    check("banned user blocked", scr is not None and "ʙʟᴏᴄᴋᴇᴅ" in scr.text)
    db.set_banned(222, False)

    # maintenance
    db.set_setting("maintenance", "1")
    scr, _ = actions.run(ctx, 222, "home")
    check("maintenance gate", scr is not None and "ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ" in scr.text)
    scr, _ = actions.run(ctx, 111, "home")
    check("admin maintenance ke paar", scr is not None and "ʙʟᴏᴄᴋᴇᴅ" not in scr.text)
    db.set_setting("maintenance", "0")

    # plan limits + free user
    db.set_plan(222, "free", days=0)
    ok, why = actions.can_add_bot(ctx, 222)
    check("free user ka pehla bot allowed", ok, why)

    actions.clear_state(111)
    eng.stop_fast(b1)
    wait_until(lambda: not eng.is_running(b1), 6)


# ── handler registration + real handlers (bina telegram network) ───────────
class HandlerBot(FakeBot):
    """Decorator capture karne wala bot stub."""

    def __init__(self):
        super().__init__()
        self.msg_handlers = []
        self.cb_handlers = []

    def message_handler(self, **kw):
        def deco(fn):
            self.msg_handlers.append((kw, fn))
            return fn
        return deco

    def callback_query_handler(self, func):
        def deco(fn):
            self.cb_handlers.append(fn)
            return fn
        return deco

    def reply_to(self, message, text, **kw):
        return self.send_message(message.chat.id, text, **kw)

    def get_file(self, file_id):
        if file_id == "big":
            return SimpleNamespace(file_path="x", file_size=99 * 1024 * 1024)
        return SimpleNamespace(file_path="files/x.py")

    def download_file(self, path):
        return SCRIPT_OK.encode()


def _msg(uid=111, text="", chat_id=1, document=None):
    return SimpleNamespace(
        from_user=SimpleNamespace(id=uid, username="nik", first_name="Nik"),
        chat=SimpleNamespace(id=chat_id),
        message_id=42,
        text=text,
        document=document,
    )


def _handler(bot, *, command=None, content=None):
    for kw, fn in bot.msg_handlers:
        if command and command in (kw.get("commands") or []):
            return fn
        if content and content in (kw.get("content_types") or []):
            return fn
    return None


def test_handlers(ctx) -> None:
    print("\n[9] telegram handlers (stub)")
    from nikhoster.bot import app as APP

    config.ADMIN_IDS.add(111)
    bot = HandlerBot()
    ctx.bot = bot
    APP.register(bot, ctx)
    check("handlers registered", len(bot.msg_handlers) >= 8 and len(bot.cb_handlers) == 1,
          f"{len(bot.msg_handlers)} msg / {len(bot.cb_handlers)} cb")

    try:
        _handler(bot, command="start")(_msg(111, "/start"))
        check("/start chala", any("⚡" in t for _, t in bot.sent))
    except Exception as exc:
        check("/start chala", False, f"{type(exc).__name__}: {exc}")

    for cmd, label in [("menu", "/menu"), ("ping", "/ping"), ("help", "/help"),
                       ("bots", "/bots"), ("run", "/run btn0"), ("logs", "/logs btn0"),
                       ("kill", "/kill btn0"), ("admin", "/admin")]:
        fn = _handler(bot, command=cmd)
        try:
            fn(_msg(111, label))
            check(f"{label} chala", True)
        except Exception as exc:
            check(f"{label} chala", False, f"{type(exc).__name__}: {exc}")

    # text fallback
    try:
        _handler(bot, content="text")(_msg(111, "random hello"))
        check("text fallback chala", True)
    except Exception as exc:
        check("text fallback chala", False, str(exc))

    # document upload
    doc = SimpleNamespace(file_name="uploaded.py", file_id="ok", file_size=2048)
    before = len(ctx.db.bots_of(111))
    try:
        _handler(bot, content="document")(_msg(111, document=doc))
        check("document upload chala", True)
        check("upload se bot bana", wait_until(
            lambda: len(ctx.db.bots_of(111)) > before, 8))
    except Exception as exc:
        check("document upload chala", False, f"{type(exc).__name__}: {exc}")

    # bad extension
    bad = SimpleNamespace(file_name="virus.exe", file_id="ok", file_size=10)
    try:
        _handler(bot, content="document")(_msg(111, document=bad))
        check("galat extension block", any("sirf" in t for _, t in bot.sent))
    except Exception as exc:
        check("galat extension block", False, str(exc))

    # callback flow: home + deploy
    class Call(SimpleNamespace):
        pass

    for data in ("nk:home", "nk:deploy", "nk:mybots:0", "nk:noop", "nk:garbage:9"):
        call = Call(id="cb1", data=data,
                    from_user=SimpleNamespace(id=111, username="nik", first_name="Nik"),
                    message=SimpleNamespace(chat=SimpleNamespace(id=1), message_id=42))
        try:
            bot.cb_handlers[0](call)
            check(f"callback {data}", True)
        except Exception as exc:
            check(f"callback {data}", False, f"{type(exc).__name__}: {exc}")
    check("callbacks ack huye", bot.acked >= 5, str(bot.acked))


def main() -> int:
    tmp = Path(tempfile.mkdtemp(prefix="nikhoster-test-"))
    try:
        # notification spam se bachne ke liye logs quiet
        ctx, notices = build_env(tmp)
        test_db(ctx)
        test_deploy_start_logs(ctx)
        test_crash_restart(ctx, notices)
        test_zip(ctx)
        test_session(ctx)
        test_screens(ctx)
        test_limits(ctx)
        test_actions(ctx)
        test_handlers(ctx)
        ctx.engine.shutdown()
        ctx.db.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "─" * 46)
    print(f"  PASS {len(PASS)}   FAIL {len(FAIL)}")
    if FAIL:
        print("  failed:", ", ".join(FAIL))
    print("─" * 46)
    return 1 if FAIL else 0


if __name__ == "__main__":
    raise SystemExit(main())
