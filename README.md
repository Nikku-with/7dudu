# 7dudu

Userbot scripts + **NIK HOSTER v1** — ek naya, tez, clean Telegram userbot hoster.

```
main.py                 ← hoster chalao:  python main.py
nikhoster/              ← poora hoster (engine + UI + preview)
nikhoster/README.md     ← setup, features, troubleshooting (isse padho)

nik_userbot/            ← NIK USERBOT v2 (multi-ID userbot)
nik_userbot/NIK_USERBOT_V2.py
nik_userbot/README.md   ← fleet setup, emoji, delays, fyt
```

**Do projects:**

| Project | Kya hai | Chalao |
|---|---|---|
| **NIK HOSTER v1** | Telegram bot jo userbots host karta hai | `python main.py` |
| **NIK USERBOT v2** | multi-account userbot (ek process, saari IDs) | `python nik_userbot/NIK_USERBOT_V2.py` |

Quick start:

```bash
pip install -r nikhoster/requirements.txt
cp nikhoster/.env.example .env      # BOT_TOKEN + OWNER_ID bharo
python main.py
```

UI preview (bina Telegram, browser me):

```bash
python main.py --preview      # → nikhoster/preview/index.html
```

Tests (bina internet):

```bash
python main.py --test         # 198 checks
```

Userbot setup:

```bash
pip install telethon
cp nik_userbot/sessions.example.json nik_userbot/sessions.json   # apni IDs
python nik_userbot/NIK_USERBOT_V2.py            # --selftest bhi chalta hai
```

Baaki `.py` files purane userbot scripts hain — unhe hoster me
**📤 upload .py** se deploy kar sakte ho.
