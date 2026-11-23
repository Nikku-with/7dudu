#!/usr/bin/env python3
"""
Screen functions se clickable HTML preview banao.

    python -m nikhoster.tools.preview

Output: nikhoster/preview/index.html
Yahi file browser me kholo — saare buttons asli bot jaise kaam karte hain.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from nikhoster.ui import screens as S  # noqa: E402
from nikhoster.tools.sample import build_sample  # noqa: E402


NAV = [
    ("user", "ᴜꜱᴇʀ ꜰʟᴏᴡ", [
        ("welcome", "ᴡᴇʟᴄᴏᴍᴇ"),
        ("home", "ᴅᴀꜱʜʙᴏᴀʀᴅ"),
        ("deploy", "ᴅᴇᴘʟᴏʏ ʜᴜʙ"),
        ("mybots:0", "ᴍʏ ʙᴏᴛꜱ"),
        ("sessions", "ꜱᴇꜱꜱɪᴏɴꜱ"),
        ("plans", "ᴘʟᴀɴꜱ"),
        ("stats", "ᴜꜱᴀɢᴇ"),
        ("support", "ꜱᴜᴘᴘᴏʀᴛ"),
    ]),
    ("bot", "ʙᴏᴛ ᴄᴏɴᴛʀᴏʟ", [
        ("bot:1", "ʙᴏᴛ · ʀᴜɴɴɪɴɢ"),
        ("logs:1", "ʟɪᴠᴇ ʟᴏɢꜱ"),
        ("tools:1", "ᴛᴏᴏʟꜱ"),
        ("env:1", "ᴇɴᴠ ᴠᴀʀꜱ"),
        ("bot:2", "ʙᴏᴛ · ꜱᴛᴏᴘᴘᴇᴅ"),
        ("del:1", "ᴅᴇʟᴇᴛᴇ ᴄᴏɴꜰɪʀᴍ"),
    ]),
    ("admin", "ᴀᴅᴍɪɴ", [
        ("admin", "ꜰʟᴇᴇᴛ"),
        ("ausers:0", "ᴜꜱᴇʀꜱ"),
        ("auser:111", "ᴜꜱᴇʀ ᴄᴀʀᴅ"),
        ("amass", "ᴍᴀꜱꜱ ᴀᴄᴛɪᴏɴ"),
        ("aevents", "ᴇᴠᴇɴᴛꜱ"),
        ("aset", "ꜱᴇᴛᴛɪɴɢꜱ"),
    ]),
    ("wizard", "Qᴜɪᴄᴋ ᴅᴇᴘʟᴏʏ", [
        ("wiz:api_id", "ꜱᴛᴇᴘ 1 · ᴀᴘɪ ɪᴅ"),
        ("wiz:api_hash", "ꜱᴛᴇᴘ 2 · ᴀᴘɪ ʜᴀꜱʜ"),
        ("wiz:session", "ꜱᴛᴇᴘ 3 · ꜱᴇꜱꜱɪᴏɴ"),
        ("wiz:name", "ꜱᴛᴇᴘ 4 · ɴᴀᴍᴇ"),
        ("wiz:verify", "ᴠᴇʀɪꜰʏɪɴɢ"),
        ("done:1", "ᴅᴇᴘʟᴏʏᴇᴅ"),
    ]),
]

ALIASES = {
    "wiz:start": "wiz:api_id",
    "menu": "home",
    "mybots:1": "mybots:0",
}

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>NIK HOSTER v1 · UI preview</title>
<style>
  :root{
    --bg:#0a0e13; --panel:#111923; --line:#1d2a36;
    --chat:#0e1621; --bubble:#182533; --head:#17212b;
    --text:#e9edf0; --dim:#7d8b99; --accent:#6ab2f2; --btn:#202b36;
  }
  *{box-sizing:border-box; -webkit-tap-highlight-color:transparent}
  body{
    margin:0; min-height:100vh; background:
      radial-gradient(900px 600px at 15% -10%, #14324a55, transparent 60%),
      radial-gradient(700px 500px at 100% 110%, #2a1a4a44, transparent 60%),
      var(--bg);
    color:var(--text); font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,
      "Helvetica Neue",Arial,"Noto Sans",sans-serif;
    display:flex; justify-content:center; padding:28px 18px 40px;
  }
  .app{display:flex; gap:34px; align-items:flex-start; max-width:1080px; width:100%;}
  /* ── sidebar ── */
  .side{width:260px; flex:0 0 260px; padding-top:6px}
  .logo{font-size:20px; letter-spacing:.3px; display:flex; align-items:center; gap:8px}
  .logo b{font-weight:700}
  .logo span{font-size:11px; color:var(--accent); border:1px solid #24455f;
    padding:1px 6px; border-radius:20px; background:#12202c}
  .tag{margin:6px 0 16px; color:var(--dim); font-size:12.5px; letter-spacing:.4px}
  .chips{display:flex; flex-wrap:wrap; gap:6px; margin-bottom:20px}
  .chips span{font-size:11px; color:#9fc7e8; background:#12202c;
    border:1px solid #1d3547; padding:3px 8px; border-radius:20px; white-space:nowrap}
  nav h4{margin:16px 0 7px; font-size:10.5px; letter-spacing:1.6px; color:#5c6f80;
    text-transform:uppercase; font-weight:600}
  nav a{display:block; padding:7px 10px; border-radius:8px; color:#b9c6d2;
    font-size:13px; text-decoration:none; cursor:pointer; border:1px solid transparent}
  nav a:hover{background:#131e29; color:#fff}
  nav a.on{background:#16232f; border-color:#24384a; color:#fff}
  .hint{margin-top:22px; color:#5f7183; font-size:11.5px; line-height:1.55}
  /* ── phone ── */
  .stage{flex:1; display:flex; justify-content:center}
  .phone{width:min(400px,100%); height:800px; background:var(--chat);
    border:1px solid var(--line); border-radius:34px; overflow:hidden;
    display:flex; flex-direction:column; position:relative;
    box-shadow:0 30px 80px -20px #000, 0 0 0 8px #0d141c, 0 0 0 9px #1a2632;
  }
  .status{height:26px; display:flex; align-items:center; justify-content:space-between;
    padding:0 20px; font-size:11px; color:#a9b8c6; background:var(--head)}
  .chathead{background:var(--head); border-bottom:1px solid #101a23;
    display:flex; align-items:center; gap:10px; padding:9px 12px 10px}
  .avatar{width:40px; height:40px; border-radius:50%; display:grid; place-items:center;
    font-size:19px; background:linear-gradient(145deg,#2aabee,#1d7fbf);
    box-shadow:0 2px 10px #2aabee44}
  .who{flex:1; min-width:0}
  .name{font-size:15px; font-weight:600; display:flex; align-items:center; gap:5px;
    white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
  .badge{width:13px; height:13px; border-radius:50%; background:#2aabee;
    display:inline-grid; place-items:center; font-size:8px; color:#fff; flex:0 0 13px}
  .sub{font-size:11.5px; color:#7d8b99; margin-top:2px}
  .dots{color:#7d8b99; font-size:20px; letter-spacing:1px; padding:0 4px}
  /* ── chat ── */
  .chat{flex:1; overflow-y:auto; padding:14px 12px 6px;
    background-image:radial-gradient(rgba(255,255,255,.028) 1px, transparent 1px);
    background-size:19px 19px; scrollbar-width:thin}
  .chat::-webkit-scrollbar{width:6px}
  .chat::-webkit-scrollbar-thumb{background:#243240; border-radius:6px}
  .msg{display:flex; flex-direction:column; align-items:flex-start}
  .bubble{background:var(--bubble); border-radius:12px; padding:9px 11px 10px;
    font-size:14.5px; line-height:1.5; max-width:100%; word-break:break-word;
    box-shadow:0 1px 2px #00000033}
  .bubble b{color:#fff; font-weight:700}
  .bubble i{color:#dbe6ee}
  .bubble code{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
    background:#ffffff12; border-radius:5px; padding:1px 5px; font-size:12.5px;
    color:#b9e3ff; white-space:pre-wrap}
  .bubble pre{white-space:pre-wrap; word-break:break-word; background:#101d2a;
    border:1px solid #ffffff0d; border-radius:8px; padding:8px 9px; margin:7px 0 2px;
    color:#cfe8ff; font-size:11.8px; line-height:1.4; max-height:230px; overflow:auto;
    font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
  .bubble pre code{background:none; padding:0; font-size:inherit; color:inherit}
  .bubble blockquote{margin:7px 0; padding:1px 0 1px 9px; border-left:3px solid #43576a;
    color:#cfd9e2}
  .bubble a{color:var(--accent); text-decoration:none}
  .meta{font-size:10.5px; color:#6b7d8e; margin:4px 4px 0; text-align:right;
    align-self:flex-end}
  .kbd{display:flex; flex-direction:column; gap:6px; margin-top:7px; width:100%}
  .krow{display:flex; gap:6px}
  .krow .kbtn{flex:1 1 0}
  .kfull{display:flex}
  .kfull .kbtn{flex:1 1 0}
  .kbtn{background:var(--btn); border:1px solid #2b3a48; border-radius:8px;
    color:var(--accent); font-size:13.5px; padding:9px 8px; text-align:center;
    cursor:pointer; user-select:none; transition:background .12s, border-color .12s,
    transform .06s; white-space:nowrap; overflow:hidden; text-overflow:ellipsis}
  .kbtn:hover{background:#25323f; border-color:#3a4b5c}
  .kbtn:active{transform:translateY(1px)}
  /* ── composer ── */
  .composer{background:var(--head); border-top:1px solid #101a23; padding:8px 12px;
    display:flex; align-items:center; gap:10px; color:#5f7183; font-size:13.5px}
  .composer .field{flex:1; background:#0e1621; border-radius:18px; padding:7px 12px}
  .composer .send{width:34px; height:34px; border-radius:50%; background:#2aabee22;
    color:#4b9fd8; display:grid; place-items:center; font-size:14px}
  /* ── toast ── */
  .toast{position:fixed; left:50%; bottom:26px; transform:translate(-50%,14px);
    background:#25323f; color:#e9edf0; font-size:12.5px; padding:9px 16px;
    border-radius:22px; border:1px solid #33475a; opacity:0; pointer-events:none;
    transition:opacity .18s, transform .18s; z-index:10}
  .toast.show{opacity:1; transform:translate(-50%,0)}
  @media (max-width:860px){
    .app{flex-direction:column; align-items:center; gap:18px}
    .side{width:min(400px,100%); flex:none}
    nav{display:flex; flex-wrap:wrap; gap:4px}
    nav h4{width:100%; margin:10px 0 2px}
    nav a{padding:5px 9px; font-size:12px}
    .phone{height:720px}
  }
</style>
</head>
<body>
<div class="app">
  <aside class="side">
    <div class="logo">⚡ <b>ɴɪᴋ ʜᴏꜱᴛᴇʀ</b> <span>v1</span></div>
    <p class="tag">ꜰᴀꜱᴛ · ᴄʟᴇᴀɴ · ɴᴇᴠᴇʀ ꜱʟᴇᴇᴘꜱ</p>
    <div class="chips">
      <span>ack &lt; 50ms</span><span>logs 0ms</span>
      <span>auto-fix</span><span>live refresh</span><span>edit-in-place</span>
    </div>
    <nav id="nav"></nav>
    <p class="hint">Ye preview asli screen functions se generate hota hai —
      jo yahan dikh raha hai, bilkul wahi Telegram me aayega.
      Buttons dabao, flow chalta rahega.</p>
  </aside>
  <main class="stage">
    <div class="phone">
      <div class="status"><span>10:41</span><span>▮▮▮ ⌁ ▮</span></div>
      <div class="chathead">
        <div class="avatar">⚡</div>
        <div class="who">
          <div class="name">ɴɪᴋ ʜᴏꜱᴛᴇʀ <span class="badge">✓</span></div>
          <div class="sub">bot · online</div>
        </div>
        <div class="dots">⋯</div>
      </div>
      <div class="chat" id="chat">
        <div class="msg">
          <div class="bubble" id="bubble"></div>
          <div class="kbd" id="kbd"></div>
          <div class="meta">edited · <span id="clock">10:41</span></div>
        </div>
      </div>
      <div class="composer"><div class="field">Message</div><div class="send">➤</div></div>
    </div>
  </main>
</div>
<div class="toast" id="toast"></div>
<script>
const SCREENS = /*__PAYLOAD__*/ null;
const NAV = /*__NAV__*/ null;
const START = "home";

const bubble = document.getElementById('bubble');
const kbd = document.getElementById('kbd');
const nav = document.getElementById('nav');
const chat = document.getElementById('chat');
let toastTimer = null;

function toast(text){
  const t = document.getElementById('toast');
  t.textContent = text;
  t.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => t.classList.remove('show'), 1600);
}

function fallback(route){
  const p = route.split(':');
  const has = r => !!SCREENS[r];
  if (['aplan','aban','aunban','astartu','astopu'].includes(p[0]) && has('auser:' + p[1]))
    return 'auser:' + p[1];
  if (['toggle','sendin','rename','start','stop','restart','clearlogs'].includes(p[0])
      && has('tools:' + p[1])) return 'tools:' + p[1];
  if (p[0] === 'sessdeploy' && has('done:1')) return 'done:1';
  if (p[0] === 'sessdel') return 'sessions';
  if (p[0] === 'logsfull' && has('logs:' + p[1])) return 'logs:' + p[1];
  if (p[0] === 'start' || p[0] === 'stop' || p[0] === 'restart'){
    if (has('bot:' + p[1])) return 'bot:' + p[1];
  }
  if (p[0] === 'env') return has('env:1') ? 'env:1' : null;
  if (p[0] === 'wiz') return 'wiz:api_id';
  return null;
}

function go(data, url){
  if (url) { window.open(url, '_blank', 'noopener'); return; }
  if (!data) { toast('preview only'); return; }
  const route = data.startsWith('nk:') ? data.slice(3) : data;
  if (SCREENS[route]) { render(route); return; }
  const alt = fallback(route);
  if (alt) { render(alt); toast('‹ ' + route); return; }
  toast('preview: ' + route);
}

function render(route){
  const s = SCREENS[route] || SCREENS[START];
  bubble.innerHTML = s.text.replace(/\\n/g, '<br>');
  kbd.innerHTML = '';
  (s.rows || []).forEach(row => {
    const wrap = document.createElement('div');
    wrap.className = row.length > 1 ? 'krow' : 'kfull';
    row.forEach(btn => {
      const el = document.createElement('div');
      el.className = 'kbtn';
      el.textContent = btn[0];
      el.title = btn[1] || btn[2] || '';
      el.addEventListener('click', () => go(btn[1], btn[2]));
      wrap.appendChild(el);
    });
    kbd.appendChild(wrap);
  });
  chat.scrollTop = 0;
  document.querySelectorAll('#nav a').forEach(a =>
    a.classList.toggle('on', a.dataset.route === route));
  const d = new Date();
  document.getElementById('clock').textContent =
    String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
  try { history.replaceState(null, '', '#' + route); } catch (e) {}
}

NAV.forEach(group => {
  const h = document.createElement('h4');
  h.textContent = group[1];
  nav.appendChild(h);
  group[2].forEach(item => {
    const a = document.createElement('a');
    a.textContent = item[1];
    a.dataset.route = item[0];
    a.addEventListener('click', () => render(item[0]));
    nav.appendChild(a);
  });
});

const initial = (location.hash || '').slice(1);
render(SCREENS[initial] ? initial : START);
</script>
</body>
</html>
"""


def _prompt(title: str, body: str, hint: str = "", back: str = "home") -> S.Screen:
    text = "\n".join([S.brand(), S.F.LINE, S.F.header(title, "", icon="✏️"), "",
                       body, "", hint])
    return S.Screen(text, [[S.b("✖️ ᴄᴀɴᴄᴇʟ", back)]], "prompt:" + title)


def build_screens():
    ctx = build_sample()
    screens: dict[str, S.Screen] = {}
    add = lambda route, scr: screens.__setitem__(route, scr) if scr else None

    add("welcome", S.welcome(ctx, 111))
    add("home", S.home(ctx, 111))
    add("deploy", S.deploy_hub(ctx, 111))
    add("mybots:0", S.my_bots(ctx, 111, 0))
    add("sessions", S.sessions_screen(ctx, 111))
    add("plans", S.plans_screen(ctx, 111))
    add("stats", S.stats_screen(ctx, 111))
    add("support", S.support_screen(ctx, 111))

    for bid in (1, 2):
        add(f"bot:{bid}", S.bot_panel(ctx, 111, bid))
        add(f"tools:{bid}", S.bot_tools(ctx, 111, bid))
        add(f"logs:{bid}", S.bot_logs(ctx, 111, bid))
        add(f"del:{bid}", S.delete_confirm(ctx, 111, bid))

    env = ctx.db.env_of(1)
    lines = [S.brand(), S.F.LINE, S.F.header("ᴇɴᴠ ᴠᴀʀꜱ", "bot #1", icon="🔐"), ""]
    for k, v in env.items():
        hidden = k in {"NK_SESSION", "NK_API_HASH"}
        shown = (v[:6] + "…" + v[-4:]) if hidden and len(v) > 12 else v
        lines.append(f"├ <code>{k}</code> = <code>{shown}</code>")
    lines += ["", "<i>set karne ke liye <code>KEY=VALUE</code> bhejo</i>"]
    add("env:1", S.Screen("\n".join(lines), [[S.b("‹ ᴛᴏᴏʟꜱ", "tools:1")]], "env:1"))

    add("admin", S.admin_home(ctx, 111))
    add("ausers:0", S.admin_users(ctx, 0))
    add("auser:111", S.admin_user(ctx, 111))
    add("amass", S.admin_mass(ctx))
    add("aevents", S.admin_events(ctx))
    add("aset", S.admin_settings(ctx))

    add("wiz:api_id", S.wizard_step(ctx, "api_id", {}))
    add("wiz:api_hash", S.wizard_step(ctx, "api_hash", {"api_id": 36526099}))
    add("wiz:session", S.wizard_step(ctx, "session", {"api_id": 36526099}))
    add("wiz:name", S.wizard_step(ctx, "name", {"api_id": 36526099}))
    add("wiz:verify", S.wizard_step(ctx, "verify", {
        "api_id": 36526099, "session": "1BVtsOK9abcdefghijklmnop"}))
    # action-routes bhi clickable rahein (preview me dead-end nahi)
    add("auser:222", S.admin_user(ctx, 222))
    add("auser:333", S.admin_user(ctx, 333))
    add("auser:444", S.admin_user(ctx, 444))
    add("aplan:111:pro", S.admin_user(ctx, 111))
    add("aplan:111:elite", S.admin_user(ctx, 111))
    add("aplan:111:free", S.admin_user(ctx, 111))
    add("aban:111", S.admin_user(ctx, 111))
    add("aunban:111", S.admin_user(ctx, 111))
    add("astartu:111", S.admin_user(ctx, 111))
    add("astopu:111", S.admin_user(ctx, 111))
    add("all:start", S.my_bots(ctx, 111, 0))
    add("all:stop", S.my_bots(ctx, 111, 0))
    add("delyes:1", S.my_bots(ctx, 111, 0))
    add("delyes:2", S.my_bots(ctx, 111, 0))
    add("massrun:start", S.admin_mass(ctx))
    add("massrun:stop", S.admin_mass(ctx))
    add("massrun:crashed", S.admin_mass(ctx))
    add("aset:toggle:maintenance", S.admin_settings(ctx))
    add("aset:toggle:signups", S.admin_settings(ctx))
    add("aset:toggle:autofix_default", S.admin_settings(ctx))
    add("clearlogs:1", S.bot_logs(ctx, 111, 1))
    add("clearlogs:2", S.bot_logs(ctx, 111, 2))
    add("start:2", S.bot_panel(ctx, 111, 2))
    add("stop:1", S.bot_panel(ctx, 111, 1))
    add("restart:1", S.bot_panel(ctx, 111, 1))
    add("logsfull:1", S.bot_logs(ctx, 111, 1, full=True))
    add("rename:1", _prompt("ʀᴇɴᴀᴍᴇ ʙᴏᴛ", "bot <code>#1</code> ka naya naam bhejo",
                            "<i>sirf letters, numbers, - aur _</i>", "tools:1"))
    add("sendin:1", _prompt("ꜱᴇɴᴅ ɪɴᴘᴜᴛ", "bot <code>#1</code> ke process me line bhejo",
                            "<i>stdin me jaayega — scripts ke liye useful</i>", "tools:1"))
    add("afind", _prompt("ꜰɪɴᴅ ᴜꜱᴇʀ", "user id ya @username bhejo",
                         "<i>example:</i> <code>8905002151</code>", "admin"))
    add("abc", _prompt("ʙʀᴏᴀᴅᴄᴀꜱᴛ", "message bhejo — <code>4</code> users ko jaayega",
                       "<i>HTML allowed: &lt;b&gt; &lt;code&gt; &lt;i&gt;</i>", "admin"))
    add("done:1", S.success_screen(ctx, ctx.db.bot(1),
        "👤 ɴɪᴋ @nikku\n⚡ <code>2.14s</code> me live · vault me save ho gaya"))
    return ctx, screens


def main() -> int:
    ctx, screens = build_screens()
    payload = {}
    for route, scr in screens.items():
        payload[route] = {"text": scr.text, "rows": scr.rows_spec()}

    html = (TEMPLATE
            .replace("/*__PAYLOAD__*/ null",
                     json.dumps(payload, ensure_ascii=False, indent=None))
            .replace("/*__NAV__*/ null",
                     json.dumps([[g[0], g[1], [[i[0], i[1]] for i in g[2]]]
                                 for g in NAV], ensure_ascii=False)))
    out = Path(__file__).resolve().parents[1] / "preview" / "index.html"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    ctx.db.close()
    print(f"✅ {len(screens)} screens → {out}  ({len(html) / 1024:.1f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
