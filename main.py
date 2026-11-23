#!/usr/bin/env python3
"""
NIK HOSTER v1 — entrypoint.

    python main.py              # bot chalao
    python main.py --test       # smoke test (bina telegram)
    python main.py --preview    # UI preview banao (preview/index.html)
    python main.py --doctor     # config/deps check
"""
import os
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)


def _doctor() -> int:
    from nikhoster import config

    print("⚡ NIK HOSTER", config.VERSION, "· doctor")
    ok = True
    print(f"  python      {sys.version.split()[0]}")
    for mod in ("telebot", "telethon", "psutil"):
        try:
            __import__(mod)
            print(f"  {mod:<11} ✅")
        except ImportError:
            print(f"  {mod:<11} ❌  → pip install -r nikhoster/requirements.txt")
            ok = False
    print(f"  BOT_TOKEN   {'✅ set' if config.BOT_TOKEN else '❌ missing (.env)'}")
    print(f"  OWNER_ID    {config.OWNER_ID or '❌ missing'}")
    print(f"  data dir    {config.DATA_DIR}")
    return 0 if ok and config.BOT_TOKEN else 1


def _bootstrap() -> None:
    """Fresh RDP/VPS pe pehla run: missing packages khud install ho jaate hain."""
    if os.getenv("NK_NO_BOOTSTRAP"):
        return
    import importlib.util
    import subprocess

    want = {"telebot": "pyTelegramBotAPI", "telethon": "telethon", "psutil": "psutil"}
    missing = [pkg for mod, pkg in want.items()
               if importlib.util.find_spec(mod) is None]
    if not missing:
        return
    print(f"⚡ installing: {', '.join(missing)}", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "install",
                    "--disable-pip-version-check", *missing], check=False)
    subprocess.run([sys.executable, "-m", "pip", "install",
                    "--disable-pip-version-check", "-q",
                    "-r", os.path.join(ROOT, "nikhoster", "requirements.txt")],
                   check=False)


def main() -> None:
    args = sys.argv[1:]
    if "--doctor" in args:
        raise SystemExit(_doctor())
    if "--test" in args:
        from nikhoster.tools.smoke_test import main as test_main
        raise SystemExit(test_main())
    if "--preview" in args:
        from nikhoster.tools.preview import main as preview_main
        raise SystemExit(preview_main())

    _bootstrap()
    try:
        __import__("telebot")
        __import__("telethon")
    except ImportError as exc:
        raise SystemExit(
            f"missing dependency: {exc.name}\n"
            "  pip install -r nikhoster/requirements.txt"
        )

    from nikhoster.bot.app import main as bot_main
    bot_main()


if __name__ == "__main__":
    main()
