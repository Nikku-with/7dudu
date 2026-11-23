# 7dudu

Userbot scripts + **NIK HOSTER v1** — ek naya, tez, clean Telegram userbot hoster.

```
main.py                 ← hoster chalao:  python main.py
nikhoster/              ← poora hoster (engine + UI + preview)
nikhoster/README.md     ← setup, features, troubleshooting (isse padho)
```

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

Baaki `.py` files purane userbot scripts hain — unhe hoster me
**📤 upload .py** se deploy kar sakte ho.
