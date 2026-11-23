# ⚡ ɴɪᴋ ᴜꜱᴇʀʙᴏᴛ · ᴠ2

**Ek process · teri saari IDs · ek owner se poora control.**
Ye ek *userbot* hai (koi bot token nahi chahiye) — jise tu apne hoster pe
upload karke chala sakta hai, ya seedha VPS/RDP pe.

```
⚡ ɴɪᴋ ᴜꜱᴇʀʙᴏᴛ  v2
👤 Nik  ·  @nikku
🕐 ᴜᴘ 2h 14m   ·   ᴘʀᴇꜰɪx .
──────────────────
⚡ ᴄᴏʀᴇ
  .alive  ꜱᴛᴀᴛᴜꜱ + ꜱᴘᴇᴇᴅ
  .info   ᴀᴄᴄᴏᴜɴᴛ ᴅᴇᴛᴀɪʟꜱ
  .menu   ᴍᴀɪɴ ᴍᴇɴᴜ
🛰 ꜰʟᴇᴇᴛ
  .add    ɴᴇᴡ ᴀᴄᴄᴏᴜɴᴛ ᴀᴅᴅ
  .sessions / .kill / .reviveall
🔥 ꜰʏᴛ · ꜰᴜɴ
  .fyt    ᴀᴜᴛᴏ ʀᴏᴀꜱᴛ ᴏɴ/ᴏꜰꜰ
  .roast  ᴇᴋ ʀᴏᴀꜱᴛ ᴍᴀᴀʀᴏ
──────────────────
🩸 ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Nikkkwa
```

---

## 🧠 Ye kya karta hai

| Cheez | Detail |
|---|---|
| **Multi-ID fleet** | ek hi script me teri saari sessions — sab ek saath online |
| **Owner control** | `5076760701` sabka master (env `NK_OWNER` se badal sakta hai) |
| **Kabhi na ruke** | auto-reconnect + exponential backoff + heartbeat revive + hoster autostart |
| **Custom emoji** | har section ka emoji badal (normal **aur premium custom emoji**) |
| **Delay management** | har feature ka apna delay: `.delay fyt 10`, `.delay purge 0.4` |
| **fyt mode** | gali wale roast, per-chat opt-in + rate-limited (account safe) |
| **Group tools** | ban / kick / mute / purge / pin / lock |
| **Protection** | antidel mirror, antiflood guard |
| **Branding** | menu me hosted account ka naam + `ᴘᴏᴡᴇʀᴇᴅ ʙʏ @Nikkkwa` |

---

## 🚀 Setup

### 1. Dependency

```bash
pip install telethon
```

### 2. Account(s) do — 3 tarike

**A) single account (env)**

```bash
export NK_API_ID=1234567
export NK_API_HASH=0123456789abcdef0123456789abcdef
export NK_SESSION=1BVtsOK...
python NIK_USERBOT_V2.py
```

**B) multiple accounts (recommended)**

```bash
cp sessions.example.json sessions.json
nano sessions.json          # apni saari IDs daal
python NIK_USERBOT_V2.py
```

**C) runtime pe add** (script chal raha ho, tab bhi)

```
.add acc2 1234567 0123456789abcdef... 1BVtsOK...
.add acc3            ← session string wale message pe reply karke
```

`add` pehle session **verify** karta hai (`get_me`) — galat session save hi nahi hota.

### 3. Hoster pe deploy (nikhoster v1)

- Hoster me **📤 upload .py** → `NIK_USERBOT_V2.py` upload kar
- Ya **⚡ quick deploy** se session string wala starter chala
- `.sessions.json` hoster ke per-bot folder me rakhna ho to zip me
  `sessions.json` + `NIK_USERBOT_V2.py` dono daal ke **📦 .zip** upload kar
- Hoster ka **auto-restart on** rakh — script ke andar bhi supervisor hai,
  matlab hosting do layer se safe hai

---

## 🔐 Owner / Sudo

- `OWNER_ID` default **5076760701** — sab kuch iske paas
- dost/extra IDs: `.sudo add 123456789` (ya reply karke `.sudo add`)
- `.sudo list` / `.sudo del 123456789`
- owner-only commands: `.add` `.kill` `.remove` `.revive` `.reviveall` `.restart` `.stop`

> Hoster pe chala raha hai? `NK_OWNER` env set kar de, phir bhi default 5076760701 hi hai.

---

## 🎛 Custom emoji (menu ka look)

```
.setemoji fun 🔥              ← normal emoji
.setemoji brand 🩸            ← premium custom emoji bhi chalega
                              (premium emoji bhej, entity se id khud uthata hai)
.emoji                        ← list + current set
.setemoji reset               ← default pe wapas
```

Keys: `brand main fleet fun group protect util config user time dot power on off warn`

> Premium custom emoji sirf premium account ke liye render hota hai —
> non-premium pe fallback char dikhega, error nahi aayega.

---

## ⏱ Delay management

```
.delay                     ← poora table
.delay fyt 10              ← auto roast ke beech 10s
.delay roast 4             ← manual .roast gap
.delay purge 0.4           ← purge ke batches ke beech
.delay afk 60              ← same banda ko dobara AFK reply
.delay flood 3             ← antiflood window default
.delay notify 30           ← owner ko notifications
.delay reconnect 5         ← reconnect ka pehla wait
.delay reset
```

Har delay ka **safe range** fix hai (jaise `fyt` min 3s) — account flood-ban
na ho, isliye clamp hota hai aur message me limit bhi dikh jaata hai.

---

## 🔥 fyt mode

```
.fyt on            ← is group me auto roast
.fyt off
.fyt global on     ← jahan bhi ho, roast (careful)
.roast             ← reply pe ek roast
.roast @user
.rate              ← abhi ka rate/delay status
```

- Roasts sirf **non-staff** users pe jaate hain (tu, owner, sudo safe)
- Per chat: min `3s` gap + max **2 roasts / minute** + random 0.6–1.8s human delay
- Text `ROASTS` list me hai (file ke andar) — apne lines add kar sakta hai,
  bas `{u}` placeholder chhod de

---

## 🛡 Group + protect

```
.ban / .unban / .kick        ← reply ya @username
.mute 10m / .unmute
.purge 50                    ← reply se leke command tak
.pin / .unpin
.lock / .unlock              ← chat me sirf admin bol sake

.antidel on                  ← delete hui message ka mirror
.antiflood 5 10              ← 10s me 5 se zyada = messages delete
.antiflood off
```

---

## 🧰 Utility

```
.afk padhai kar raha hoon    ← PM pe auto reply
.unafk
.save wifi                   ← message pe reply
.get wifi
.notes / .delnote wifi
.id / .ping / .alive / .info / .stats
.restart now                 ← owner, process restart (hoster utha dega)
.stop now                    ← owner, band (hoster autostart off rakho to)
```

---

## 🧪 Test (bina Telegram)

```bash
python NIK_USERBOT_V2.py --selftest        # 37 checks (rich text, state, menu)
python nik_userbot/tests/test_dispatch.py  # 54 checks (asli command dispatch)
```

Dono offline chalte hain — fake client/event pe poora flow test hota hai:
menu, auth, delay clamp, premium emoji entity, prefix, roast, antiflood,
antidel, afk, notes, ban rights.

---

## 🩺 Troubleshooting

| Problem | Fix |
|---|---|
| `koi session nahi mila` | `sessions.json` banao ya env do |
| `session authorized nahi hai` | naya session string (logout ho gaya) |
| `floodwait` bar bar | `.delay fyt 15` / `.delay roast 10` badha |
| commands kaam nahi kar rahe | `.menu` dekho — prefix badla hai? `.prefix` |
| group me dono accounts reply kar rahe | primary account hi reply karta hai; specific account se karwana ho to usko `@mention` karo |
| premium emoji nahi dikh raha | account premium nahi hai — fallback char dikhega |
| hoster pe restart loop | logs dekho; `nkstate.json` corrupt ho to delete kar |

---

## 🧭 Files

```
NIK_USERBOT_V2.py        ← poora userbot (single file, hoster-friendly)
sessions.json            ← teri IDs (git me commit mat karo!)
sessions.example.json    ← format
nikstate.json            ← auto: emoji, delays, sudo, notes, stats
tests/test_dispatch.py   ← 54 offline checks
```

> `sessions.json` aur `nikstate.json` me credentials hote hain —
> `.gitignore` me daal, kisi ko mat bhej.

---

**ɴɪᴋ · ᴠ2** — teri IDs, tera control, tera naam. 🩸
