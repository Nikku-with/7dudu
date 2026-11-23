# ⚡ ɴɪᴋ ʜᴏꜱᴛᴇʀ · v1

**Userbot hoster — clean UI, fast engine, zero drama.**
Telegram bot jo tumhare userbots (Telethon / py files) ko host karta hai:
session string paste karo → 2 second me online, live logs, auto-fix, auto-restart.

> Ye naya build hai (purane `USERBOT hoster.py` / `telegram_hosting_bot_rdp_ready.py` se alag).
> Wahi features, par tez + saaf UI + jo cheez crash hoti thi wo khud sambhalti hai.

---

## 👀 Pehle UI dekh lo

```
⚡ ɴɪᴋ ʜᴏꜱᴛᴇʀ  v1
ꜰᴀꜱᴛ · ᴄʟᴇᴀɴ · ɴᴇᴠᴇʀ ꜱʟᴇᴇᴘꜱ
────────────────
👤 Nik  @nikku  ·  ᴘʟᴀɴ ᴘʀᴏ
🤖 ʙᴏᴛꜱ 2/5   🟢 ʀᴜɴɴɪɴɢ 1

│ ᴇɴɢɪɴᴇ ↑ 6h 41m · ʀᴀᴍ 786.0 MB / 1.9 GB
│ ████░░░░░░ 41%   ᴄᴘᴜ 18%   ʙᴏᴛꜱ 1

[ ⚡ ᴅᴇᴘʟᴏʏ ]      [ 🤖 ᴍʏ ʙᴏᴛꜱ ]
[ 🗂 ꜱᴇꜱꜱɪᴏɴꜱ ]    [ 💎 ᴘʟᴀɴꜱ ]
[ 📊 ᴜꜱᴀɢᴇ ]       [ 💬 ꜱᴜᴘᴘᴏʀᴛ ]
```

**Clickable preview** (asli screens se generate hota hai, browser me kholo):

```bash
python -m nikhoster.tools.preview
# → nikhoster/preview/index.html kholo
```

Preview me har button chalta hai — deploy wizard, bot panel, live logs, admin fleet,
sab kuch exactly jaisa Telegram me dikhega.

---

## 🚀 Kya-kya hai

### User side
| Feature | Detail |
|---|---|
| ⚡ Quick deploy | session string + api id/hash → **verify → live** (Telethon `get_me` check) |
| 📤 Upload `.py` | apna ready userbot script |
| 📦 Upload `.zip` | folder upload, entry-point auto detect, zip-slip safe |
| 🗂 Session vault | ek baar save, phir 1 tap redeploy |
| 📜 Live logs | memory se, 0 ms delay, 75s auto-refresh |
| ⌨️ Send input | process ke stdin me line bhejo |
| 🔐 Env vars | `KEY=VALUE` set karo, secrets masked dikhte hain |
| 🔁 Auto-restart | crash pe 3s me wapas, backoff ke saath (5 tries) |
| 🛠 Auto-fix | `ModuleNotFoundError` → pip install → restart (khud) |
| ⏱ Ping/Uptime | per-bot RAM, CPU, PID, uptime |
| ⌨️ Power shortcuts | `/run king` · `/kill king` · `/logs king` · `/bots` |

### Admin side
| Feature | Detail |
|---|---|
| 🛰 Fleet dashboard | users / bots / running / crashed + CPU/RAM/disk bars |
| 👥 User search | id ya @username → user card |
| 💎 Plans | free / pro / elite — 1 tap me grant (30 din) |
| 🚀 Mass action | start all · restart crashed · stop all |
| 📢 Broadcast | progress ke saath, rate-limited |
| ⚙️ Settings | maintenance mode, signups close, auto-fix default |
| 📜 Events | deploy/start/crash/delete ka audit trail |
| ⛔️ Ban | ban karte hi uske saare bots band |

---

## ⚡ Ye tez kyun hai (asli reason)

| Purana hoster | NIK HOSTER v1 |
|---|---|
| `time.sleep(5)` ke baad hi status pata chalta | status turant, watchdog 3s tick |
| logs har baar file se padhta | **memory ring buffer** → 0 ms |
| sqlite default journal | **WAL + synchronous=NORMAL** → writes ~10x |
| har button pe spinner | **callback ACK pehle**, phir edit |
| naya message har click pe (chat spam) | **edit-in-place** |
| crash pe dead | auto-restart + backoff + auto-fix |
| module missing → user ko error | khud pip install karke restart |
| 5s blocking stop | SIGTERM + background reaper |

Smoke test se real numbers (`python -m nikhoster.tools.smoke_test`):

```
deploy .py            ~10 ms
start → pid           ~15 ms
first log line        ~0.6 s
crash detect          ~0.3 s
198 checks, 0 fail    (python main.py --test)
```

---

## 📦 Install

### 1. Requirements
- Python **3.10+** (3.11 best)
- 1 vCPU / 512 MB RAM se kaafi (per bot ~60 MB)
- Linux VPS, Windows RDP, ya Render/Koyeb — sab chalega

### 2. Code + deps

```bash
cd /home/user/7dudu
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r nikhoster/requirements.txt
```

### 3. Config

```bash
cp nikhoster/.env.example .env
nano .env        # BOT_TOKEN + OWNER_ID bharo
```

`.env` load karne ke 2 tarike — jo pasand ho:

```bash
# A) simple
export $(grep -v '^#' .env | xargs)
python main.py

# B) systemd / docker me EnvironmentFile se (neeche dekho)
```

> `.env` **git me commit mat karo** (`.gitignore` me already hai).

### 4. Chalao

```bash
python main.py
```

Tour Telegram me `/start` → panel khul jaayega.

### 5. 24×7 (Linux VPS / systemd)

```ini
# /etc/systemd/system/nikhoster.service
[Unit]
Description=NIK HOSTER v1
After=network.target

[Service]
WorkingDirectory=/home/user/7dudu
EnvironmentFile=/home/user/7dudu/.env
ExecStart=/home/user/7dudu/.venv/bin/python /home/user/7dudu/main.py
Restart=always
RestartSec=3
KillMode=mixed

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable --now nikhoster
journalctl -u nikhoster -f
```

Windows RDP pe: `python main.py` ek `.bat` me daal do
(`@echo off` / `:loop` / `python main.py` / `goto loop`), ya NSSM se service bana lo.

### 6. Render / Koyeb (free)

- Start command: `python main.py`
- Env me `BOT_TOKEN`, `OWNER_ID` daalo
- `PORT` env diya to bot khud health server chala dega (uptime pings ke liye)
- Free tier pe disk ephemeral hota hai → `NK_DATA_DIR` ko persistent disk pe rakho

---

## 🔑 Env variables

| Var | Default | Kya karta hai |
|---|---|---|
| `BOT_TOKEN` | — | **zaroori**, @BotFather se |
| `OWNER_ID` | — | tera user id (admin panel) |
| `ADMIN_IDS` | — | extra admins, comma separated |
| `SUPPORT_URL` | `https://t.me/nikku` | support button |
| `UPDATES_URL` | — | updates channel (optional) |
| `NK_FREE_BOTS` / `NK_PRO_BOTS` / `NK_ELITE_BOTS` | 1 / 5 / 15 | plan limits |
| `NK_MAX_UPLOAD_MB` | 20 | upload cap |
| `NK_MAX_RESTARTS` | 5 | crash pe max retry |
| `NK_RESTART_BACKOFF` | 4 | pehla retry delay (x2 each) |
| `NK_WATCHDOG_INTERVAL` | 3 | crash detect speed |
| `NK_AUTOFIX` | true | missing module auto-install |
| `NK_AUTOSTART` | true | boot pe bots wapas uthao |
| `NK_LIVE_REFRESH` | 4 | live logs refresh seconds |
| `NK_DATA_DIR` | `nikhoster/data` | db + scripts + logs |

---

## 🧾 Session string kaise banaye (user ke liye guide)

```bash
pip install telethon
python3 - <<'EOF'
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
api_id = int(input("api id: "))
api_hash = input("api hash: ")
with TelegramClient(StringSession(), api_id, api_hash) as c:
    print("\nSESSION:\n" + c.session.save())
EOF
```

- `api_id` / `api_hash`: [my.telegram.org](https://my.telegram.org) → API development tools
- Session string `1BVts…` jaisi hoti hai — **kabhi kisi ko mat bhejo**, ye account ka password hai
- Hoster deploy se pehle session verify karta hai, galat ho to turant bata deta hai (crash nahi hota)

---

## 🗂 File structure

```
main.py                     # entrypoint
nikhoster/
├── config.py               # env + plans + engine tuning
├── core/
│   ├── db.py               # sqlite WAL: users, bots, env, sessions, events
│   ├── engine.py           # process supervisor, watchdog, auto-fix, log ring
│   ├── sessions.py         # session verify (telethon get_me)
│   ├── templates.py        # starter userbot runner (auto-generated)
│   └── app_context.py      # shared runtime
├── ui/
│   ├── fonts.py            # small caps + clean formatting
│   ├── screens.py          # saare screens (pure, telegram-free)
│   └── render.py           # screen → message (edit-in-place)
├── bot/
│   ├── app.py              # telebot wiring, commands, live logs
│   └── actions.py          # callback router + wizards + broadcast
├── tools/
│   ├── smoke_test.py       # 165 checks, bina telegram
│   ├── sample.py           # preview ke liye fake data
│   └── preview.py          # → preview/index.html
├── preview/index.html      # clickable UI preview
├── requirements.txt
└── .env.example
```

**Design rule:** `screens.py` me kabhi `import telebot` nahi — isliye UI ko
telegram ke bina test/preview kar sakte hain, aur crash ka risk kam rehta hai.

---

## 🧪 Test

```bash
python main.py --test       # ya: python -m nikhoster.tools.smoke_test
python main.py --doctor     # deps + config check
```

Ye bina internet chalta hai (198 checks): db, deploy, start, logs, stop, restart,
crash+backoff, zip-slip guard, session env, saare screens (4096 char limit, 64-byte
callback data, HTML tags balanced), 48 button routes, aur telegram handlers
(`/start`, `/run`, upload, callbacks) — sab stub bot pe.

---

## 🩺 Troubleshooting

| Problem | Fix |
|---|---|
| `BOT_TOKEN missing` | `.env` me token daalo, ya `export BOT_TOKEN=...` |
| bot start hote hi band | panel → 📜 logs kholo; 90% jawab wahine milta hai |
| `ModuleNotFoundError` | auto-fix on hai to khud install hoga; nahi to `pip install <pkg>` host pe |
| `AUTH_KEY_UNREGISTERED` | session dead — naya banao |
| `FloodWaitError` | userbot ke commands bahut fast hain — delay badhao |
| `sqlite3.OperationalError: disk I/O` | disk full; `NK_DATA_DIR` badlo |
| Logs empty | script buffered output de rahi hai → `print(..., flush=True)` |
| Render pe restart pe sab gayab | persistent disk + `NK_DATA_DIR` set karo |

---

## 🔒 Safety

- Session strings DB me store hote hain (`data/nikhoster.db`) — disk permission `600` rakho
- Uploads sirf `.py` / `.zip` / `.js`; 20 MB cap; zip-slip blocked
- Har bot apne process group me chalta hai → stop = poora tree clean
- Plan limit + ban system abuse rokta hai
- Public hoster chala rahe ho to `NK_AUTOFIX` off rakho (random pip installs mat karo)

---

## 🛣 Roadmap (v1.1)

- [ ] Web panel (same screens, Flask + SSE live logs)
- [ ] Per-user Docker sandbox
- [ ] UPI/QR payment + auto approval
- [ ] Scheduled restarts + cron commands
- [ ] Multi-node engine (Redis queue)
- [ ] Command presets (`.ping` `.alive` 1-tap run)

---

**ɴɪᴋ · v1** — banaya tha haar se bachne ke liye, ab jeetne ke liye. 🖤
