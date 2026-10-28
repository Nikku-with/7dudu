#!/usr/bin/env python3
# Telegram OSINT Bot - Premium 3D Emoji Edition
# Full Professional Version with Admin Panel & TXT Export

import os
import json
import re
import time
import requests
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== CONFIGURATION ====================
BOT_TOKEN = '8585614774:AAGTbt9A2QPzKdM7zR3hnvq8ig1us2r9zHc'
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}/'
FILE_API_URL = f'https://api.telegram.org/file/bot{BOT_TOKEN}/'

BOT_NAME = "OSINT LOOKUP BOT"
BOT_VERSION = "v5.0 Premium"
OWNER_USERNAME = "@SubhaXmd"
OWNER_NAME = "Subhadip"
OWNER_ID = 0
POWERED_BY = "POWERED BY SUBHA-X-MD"

WELCOME_IMAGE = "https://files.catbox.moe/1bwq8x.png"
START_IMAGE = "https://files.catbox.moe/99cebu.png"
BROADCAST_IMAGE = "https://files.catbox.moe/1bwq8x.png"

YOUTUBE_URL = "https://youtube.com/@humming_king_subhadip?si=fLPFmToM1mTr0By2"
INSTAGRAM_URL = "https://www.instagram.com/subha_xmd?stkn=dnB2ZXIxNzRxMjlm"
WHATSAPP_URL = "https://chat.whatsapp.com/LBeNseK80o56sQDwXfeSXI?s=cl&p=a&mlu=4&ilr=4"

SUPPORT_CHANNEL = "t.me/Subhadipstatuszone"
SUPPORT_GROUP = "https://chat.whatsapp.com/LBeNseK80o56sQDwXfeSXI?s=cl&p=a&mlu=4&ilr=4"

NUMBER_API_ENDPOINT = 'https://reuters-memorabilia-insulin-disclose.trycloudflare.com/num?number={term}&key=DADDY'
AADHAAR_API_ENDPOINT = 'https://reuters-memorabilia-insulin-disclose.trycloudflare.com/aadhaar?value={term}&key=DADDY'
EMAIL_API_ENDPOINT = 'https://providence-changed-dont-nutrition.trycloudflare.com/email?value={term}&key=DADDY'
PINCODE_API_ENDPOINT = 'https://api.postalpincode.in/pincode/{term}'

ALLOWED_GROUP_IDS = []

STATE_DIR = './bot_states'
CACHE_DIR = './cache'
EXPORT_DIR = './exports'
LOG_DIR = './logs'

for d in [STATE_DIR, CACHE_DIR, EXPORT_DIR, LOG_DIR]:
    os.makedirs(d, exist_ok=True)

# ==================== PREMIUM EMOJI IDs ====================
EMOJI_FIRE = "5289722755871162900"
EMOJI_STAR = "5372849966689566579"
EMOJI_ROCKET = "5359664288241829619"
EMOJI_CROWN = "6237927637906364256"
EMOJI_SHIELD = "6235476345451716705"
EMOJI_MONEY = "6244678063775289843"
EMOJI_PHONE = "6239930832128056797"
EMOJI_CHECK = "4958689671950369798"
EMOJI_CROSS = "4958900559139570572"
EMOJI_WARNING = "4958526153955476488"
EMOJI_LOCK = "4956719506027185156"
EMOJI_GIFT = "5084613633418199991"
EMOJI_BELL = "5098265504796115765"
EMOJI_GEAR = "5116414868357907335"
EMOJI_VIDEO = "5372849966689566579"

FIRE_EFFECT_ID = "5104841245755180586"

# ==================== PREMIUM EMOJI HELPERS ====================
def pe(emoji_id: str, fallback: str) -> str:
    return f'<tg-emoji emoji-id="{emoji_id}">{fallback}</tg-emoji>'

def E_FIRE(): return pe(EMOJI_FIRE, "🔥")
def E_STAR(): return pe(EMOJI_STAR, "⭐")
def E_ROCKET(): return pe(EMOJI_ROCKET, "🚀")
def E_CROWN(): return pe(EMOJI_CROWN, "👑")
def E_SHIELD(): return pe(EMOJI_SHIELD, "🛡️")
def E_MONEY(): return pe(EMOJI_MONEY, "💰")
def E_PHONE(): return pe(EMOJI_PHONE, "📱")
def E_CHECK(): return pe(EMOJI_CHECK, "✅")
def E_CROSS(): return pe(EMOJI_CROSS, "❌")
def E_WARNING(): return pe(EMOJI_WARNING, "⚠️")
def E_LOCK(): return pe(EMOJI_LOCK, "🔒")
def E_GIFT(): return pe(EMOJI_GIFT, "🎁")
def E_BELL(): return pe(EMOJI_BELL, "🔔")
def E_GEAR(): return pe(EMOJI_GEAR, "⚙️")
def E_VIDEO(): return pe(EMOJI_VIDEO, "📹")

# ==================== SMALL CAPS FONT ====================
SMALL_CAPS_MAP = {
    'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ',
    'g': 'ɢ', 'h': 'ʜ', 'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ',
    'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 'q': 'ǫ', 'r': 'ʀ',
    's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x',
    'y': 'ʏ', 'z': 'ᴢ',
    'A': 'ᴀ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'ᴇ', 'F': 'ꜰ',
    'G': 'ɢ', 'H': 'ʜ', 'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ',
    'M': 'ᴍ', 'N': 'ɴ', 'O': 'ᴏ', 'P': 'ᴘ', 'Q': 'ǫ', 'R': 'ʀ',
    'S': 'ꜱ', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x',
    'Y': 'ʏ', 'Z': 'ᴢ',
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉',
}

def sc(text: str) -> str:
    return ''.join(SMALL_CAPS_MAP.get(c, c) for c in text)

def bold_unicode(text: str) -> str:
    result = []
    for c in text:
        if 'A' <= c <= 'Z':
            result.append(chr(0x1D400 + ord(c) - ord('A')))
        elif 'a' <= c <= 'z':
            result.append(chr(0x1D41A + ord(c) - ord('a')))
        elif '0' <= c <= '9':
            result.append(chr(0x1D7CE + ord(c) - ord('0')))
        else:
            result.append(c)
    return ''.join(result)

# ==================== HELPERS ====================
def http_get(url: str, use_cache: bool = False, retries: int = 3) -> str:
    cache_key = hashlib.md5(url.encode()).hexdigest()
    cache_file = os.path.join(CACHE_DIR, f'{cache_key}.json')
    if use_cache and os.path.exists(cache_file):
        cache_age = time.time() - os.path.getmtime(cache_file)
        if cache_age < 300:
            with open(cache_file, 'r') as f:
                return f.read()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'application/json, text/plain, */*',
    }
    last_error = None
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                if use_cache:
                    with open(cache_file, 'w') as f:
                        f.write(response.text)
                return response.text
            else:
                last_error = f"HTTP {response.status_code}"
        except Exception as e:
            last_error = str(e)
        if attempt < retries - 1:
            time.sleep(2 * (attempt + 1))
    return f"Error: {last_error}"

def clean_response(response: str) -> str:
    patterns = [
        r'💳 BUY API :.*?\n📢 SUPPORT :.*?\n👮 Credit:.*?$',
        r'💳 BUY API :.*?\n📢 SUPPORT :.*?$',
        r'BUY API:.*?\nSUPPORT:.*?$',
        r'Credit :.*?\nApi By :.*?$',
        r'👮 Credit:.*?$',
    ]
    for pattern in patterns:
        response = re.sub(pattern, '', response, flags=re.DOTALL)
    response = re.sub(r'\n{3,}', '\n\n', response)
    return response.strip()

def log_activity(user_id: int, action: str, details: str = ""):
    try:
        log_file = os.path.join(LOG_DIR, f'activity_{datetime.now().strftime("%Y-%m")}.log')
        with open(log_file, 'a', encoding='utf-8') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"[{timestamp}] User: {user_id} | Action: {action} | {details}\n")
    except Exception as e:
        logger.error(f"Log activity failed: {e}")

# ==================== TELEGRAM API ====================
def send_message(chat_id: str, text: str, reply_markup: Dict = None, reply_to: int = None, disable_web_page_preview: bool = True) -> Optional[Dict]:
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': disable_web_page_preview
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    if reply_to:
        payload['reply_to_message_id'] = reply_to
    try:
        return requests.post(API_URL + 'sendMessage', data=payload, timeout=10).json()
    except Exception as e:
        logger.error(f"send_message failed: {e}")
        return None

def send_photo(chat_id: str, photo_url: str, caption: str = '', reply_markup: Dict = None) -> Optional[Dict]:
    payload = {'chat_id': chat_id, 'photo': photo_url, 'caption': caption, 'parse_mode': 'HTML'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        return requests.post(API_URL + 'sendPhoto', data=payload, timeout=10).json()
    except Exception as e:
        logger.error(f"send_photo failed: {e}")
        return None

def send_document(chat_id: str, document: bytes, filename: str, caption: str = '') -> Optional[Dict]:
    try:
        files = {'document': (filename, document, 'text/plain')}
        data = {'chat_id': chat_id, 'caption': caption, 'parse_mode': 'HTML'}
        return requests.post(API_URL + 'sendDocument', data=data, files=files, timeout=30).json()
    except Exception as e:
        logger.error(f"send_document failed: {e}")
        return None

def send_chat_action(chat_id: str, action: str = 'typing') -> None:
    try:
        requests.post(API_URL + 'sendChatAction', data={'chat_id': chat_id, 'action': action}, timeout=5)
    except Exception:
        pass

def answer_callback(callback_id: str, text: str = "") -> None:
    try:
        requests.post(API_URL + 'answerCallbackQuery', data={'callback_query_id': callback_id, 'text': text}, timeout=10)
    except Exception as e:
        logger.error(f"answer_callback failed: {e}")

def edit_message(chat_id: str, message_id: int, text: str, reply_markup: Dict = None) -> Optional[Dict]:
    payload = {'chat_id': chat_id, 'message_id': message_id, 'text': text, 'parse_mode': 'HTML'}
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        return requests.post(API_URL + 'editMessageText', data=payload, timeout=10).json()
    except Exception as e:
        logger.error(f"edit_message failed: {e}")
        return None

def set_bot_commands() -> None:
    commands = [
        {"command": "start",   "description": "🚀 Start the bot"},
        {"command": "num",     "description": "📱 Lookup mobile number"},
        {"command": "adhar",   "description": "🪪 Lookup Aadhaar"},
        {"command": "gmail",   "description": "📧 Lookup email"},
        {"command": "pincode", "description": "📮 Lookup pincode"},
        {"command": "help",    "description": "📖 Help"},
        {"command": "owner",   "description": "👑 Owner"},
        {"command": "about",   "description": "ℹ️ About"},
        {"command": "id",      "description": "🆔 Your ID"},
        {"command": "stats",   "description": "📊 Statistics"},
        {"command": "ping",    "description": "🏓 Ping"},
    ]
    try:
        requests.post(API_URL + 'setMyCommands', json={"commands": commands}, timeout=10)
        requests.post(API_URL + 'setMyCommands', json={
            "commands": commands,
            "scope": {"type": "all_group_chats"}
        }, timeout=10)
        logger.info("Bot commands set successfully")
    except Exception as e:
        logger.error(f"set_bot_commands failed: {e}")

# ==================== ANIMATED LOADING ====================
def animated_loading(chat_id: str, text: str = "ʟᴏᴀᴅɪɴɢ", emoji_id: str = None, fallback: str = "🔥", duration: float = 2.5) -> Optional[int]:
    if emoji_id is None:
        emoji_id = EMOJI_FIRE
    frames = [
        (10, "▓░░░░░░░░░"),
        (25, "▓▓▓░░░░░░░"),
        (40, "▓▓▓▓░░░░░░"),
        (55, "▓▓▓▓▓▓░░░░"),
        (70, "▓▓▓▓▓▓▓░░░"),
        (85, "▓▓▓▓▓▓▓▓▓░"),
        (100, "▓▓▓▓▓▓▓▓▓▓"),
    ]
    emoji_tag = pe(emoji_id, fallback)
    
    msg = send_message(chat_id, (
        "╔══════════════════════════════╗\n"
        f"║      {E_FIRE()} ᴘʀᴏᴄᴇꜱꜱɪɴɢ {E_FIRE()}         ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{emoji_tag} <b>{text}...</b>\n\n"
        f"<code>[▓░░░░░░░░░] 0%</code>"
    ))
    
    if not msg or not msg.get('ok'):
        return None
    
    msg_id = msg['result']['message_id']
    step_time = duration / len(frames)
    
    for pct, bar in frames:
        try:
            edit_message(chat_id, msg_id, (
                "╔══════════════════════════════╗\n"
                f"║      {E_FIRE()} ᴘʀᴏᴄᴇꜱꜱɪɴɢ {E_FIRE()}         ║\n"
                "╚══════════════════════════════╝\n\n"
                f"{emoji_tag} <b>{text}...</b>\n\n"
                f"<code>[{bar}] {pct}%</code>"
            ))
            time.sleep(step_time)
        except Exception:
            pass
    
    return msg_id

def premium_loading(chat_id: str, text: str = "ꜰᴇᴛᴄʜɪɴɢ ᴅᴀᴛᴀ", style: str = 'fire') -> Optional[int]:
    styles = {
        'fire': (EMOJI_FIRE, "🔥"),
        'star': (EMOJI_STAR, "⭐"),
        'rocket': (EMOJI_ROCKET, "🚀"),
        'crown': (EMOJI_CROWN, "👑"),
        'shield': (EMOJI_SHIELD, "🛡️"),
        'money': (EMOJI_MONEY, "💰"),
        'phone': (EMOJI_PHONE, "📱"),
        'video': (EMOJI_VIDEO, "📹"),
    }
    emoji_id, fallback = styles.get(style, styles['fire'])
    return animated_loading(chat_id, text, emoji_id, fallback)

# ==================== KEYBOARDS ====================
def social_buttons() -> Dict:
    return {
        'inline_keyboard': [
            [
                {'text': f"▶️ {bold_unicode('YOUTUBE')}", 'url': YOUTUBE_URL, 'style': 'danger'},
                {'text': f"📸 {bold_unicode('INSTAGRAM')}", 'url': INSTAGRAM_URL, 'style': 'primary'}
            ],
            [
                {'text': f"💬 {bold_unicode('WHATSAPP')}", 'url': WHATSAPP_URL, 'style': 'success'}
            ]
        ]
    }

def admin_panel_keyboard() -> Dict:
    return {
        'inline_keyboard': [
            [
                {'text': "📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ", 'callback_data': 'admin_broadcast', 'style': 'primary'},
                {'text': "📊 ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ", 'callback_data': 'admin_stats', 'style': 'primary'}
            ],
            [
                {'text': "👥 ɢʀᴏᴜᴘꜱ", 'callback_data': 'admin_groups', 'style': 'primary'},
                {'text': "🚫 ʙᴀɴɴᴇᴅ", 'callback_data': 'admin_banned', 'style': 'danger'}
            ],
            [
                {'text': "📝 ʟᴏɢꜱ", 'callback_data': 'admin_logs', 'style': 'primary'},
                {'text': "⚙️ ꜱᴇᴛᴛɪɴɢꜱ", 'callback_data': 'admin_settings', 'style': 'primary'}
            ],
            [
                {'text': "🔄 ʀᴇꜰʀᴇꜱʜ", 'callback_data': 'admin_refresh', 'style': 'success'},
                {'text': "❌ ᴄʟᴏꜱᴇ", 'callback_data': 'admin_close', 'style': 'danger'}
            ]
        ]
    }

def settings_keyboard() -> Dict:
    return {
        'inline_keyboard': [
            [{'text': "👋 ᴡᴇʟᴄᴏᴍᴇ ᴏɴ/ᴏꜰꜰ", 'callback_data': 'toggle_welcome', 'style': 'primary'}],
            [{'text': "🕊️ ɢᴏᴏᴅʙʏᴇ ᴏɴ/ᴏꜰꜰ", 'callback_data': 'toggle_goodbye', 'style': 'primary'}],
            [{'text': "📄 ᴛxᴛ ᴇxᴘᴏʀᴛ ᴏɴ/ᴏꜰꜰ", 'callback_data': 'toggle_txt', 'style': 'primary'}],
            [{'text': "⬅️ ʙᴀᴄᴋ", 'callback_data': 'admin_back', 'style': 'danger'}]
        ]
    }

# ==================== DATA MANAGEMENT ====================
def data_file(name: str) -> str:
    return os.path.join(STATE_DIR, f'{name}.json')

def load_data(name: str, default: Any = None) -> Any:
    try:
        with open(data_file(name), 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return default if default is not None else {}

def save_data(name: str, data: Any) -> None:
    try:
        with open(data_file(name), 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Save data failed for {name}: {e}")

def get_groups() -> Dict:
    return load_data('groups', {})

def save_group(chat_id: int, chat_title: str, chat_type: str = 'group'):
    groups = get_groups()
    groups[str(chat_id)] = {
        'title': chat_title,
        'type': chat_type,
        'added_at': datetime.now().isoformat(),
        'last_active': datetime.now().isoformat()
    }
    save_data('groups', groups)
    logger.info(f"Group saved: {chat_title} ({chat_id})")

def update_group_activity(chat_id: int):
    groups = get_groups()
    if str(chat_id) in groups:
        groups[str(chat_id)]['last_active'] = datetime.now().isoformat()
        save_data('groups', groups)

def get_banned_users() -> List[int]:
    return load_data('banned', [])

def ban_user(user_id: int):
    banned = get_banned_users()
    if user_id not in banned:
        banned.append(user_id)
        save_data('banned', banned)

def unban_user(user_id: int):
    banned = get_banned_users()
    if user_id in banned:
        banned.remove(user_id)
        save_data('banned', banned)

def is_banned(user_id: int) -> bool:
    return user_id in get_banned_users()

def get_settings() -> Dict:
    return load_data('settings', {
        'welcome_enabled': True,
        'goodbye_enabled': True,
        'txt_export': True
    })

def save_settings(settings: Dict):
    save_data('settings', settings)

# ==================== BOT STATS ====================
BOT_STATS = {
    'start_time': time.time(),
    'total_queries': 0,
    'num_queries': 0,
    'adhar_queries': 0,
    'gmail_queries': 0,
    'pincode_queries': 0,
    'welcome_count': 0,
    'goodbye_count': 0,
}

def stats_file() -> str:
    return os.path.join(STATE_DIR, 'bot_stats.json')

def load_stats() -> Dict:
    try:
        with open(stats_file(), 'r') as f:
            data = json.load(f)
            if 'start_time' not in data:
                data['start_time'] = time.time()
            return data
    except Exception:
        return dict(BOT_STATS)

def save_stats(stats: Dict) -> None:
    try:
        with open(stats_file(), 'w') as f:
            json.dump(stats, f, indent=2)
    except Exception:
        pass

def increment_stat(key: str, amount: int = 1) -> None:
    stats = load_stats()
    stats[key] = stats.get(key, 0) + amount
    save_stats(stats)

# ==================== TXT EXPORT ====================
def generate_txt_content(title: str, query: str, data: dict, user_info: dict = None) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("=" * 60)
    lines.append(f"  {title}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  Query        : {query}")
    lines.append(f"  Generated    : {timestamp}")
    lines.append(f"  Bot          : {BOT_NAME} {BOT_VERSION}")
    if user_info:
        lines.append(f"  Requested By : {user_info.get('first_name', 'Unknown')}")
        lines.append(f"  User ID      : {user_info.get('id', 'N/A')}")
        if user_info.get('username'):
            lines.append(f"  Username     : @{user_info.get('username')}")
    lines.append("")
    lines.append("=" * 60)
    lines.append("")
    results = data.get('result', [])
    total = data.get('count', len(results))
    lines.append(f"  TOTAL RECORDS: {total}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("")
    for idx, record in enumerate(results, 1):
        lines.append(f"  +-----------------------------+")
        lines.append(f"  |        RECORD #{idx:<3}       |")
        lines.append(f"  +-----------------------------+")
        lines.append("")
        fields = [
            ('name', 'Name'), ('father_name', 'Father Name'),
            ('mobile', 'Mobile'), ('alt_mobile', 'Alt Mobile'),
            ('aadhaar', 'Aadhaar'), ('email', 'Email'),
            ('address', 'Address'), ('circle', 'Circle'),
            ('dob', 'Date of Birth'), ('gender', 'Gender'),
            ('state', 'State'), ('district', 'District'),
        ]
        for key, label in fields:
            val = record.get(key)
            if val:
                lines.append(f"  {label:<15}: {val}")
        for key, val in record.items():
            if key not in [f[0] for f in fields] and val:
                lines.append(f"  {key.replace('_', ' ').title():<15}: {val}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("")
    lines.append("=" * 60)
    lines.append(f"  Generated by: {BOT_NAME}")
    lines.append(f"  {POWERED_BY}")
    lines.append("=" * 60)
    return "\n".join(lines)

def generate_pincode_txt(query: str, post_offices: list, user_info: dict = None) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = []
    lines.append("=" * 60)
    lines.append(f"  PINCODE LOOKUP RESULT")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  Pincode      : {query}")
    lines.append(f"  Generated    : {timestamp}")
    lines.append(f"  Bot          : {BOT_NAME} {BOT_VERSION}")
    if user_info:
        lines.append(f"  Requested By : {user_info.get('first_name', 'Unknown')}")
        if user_info.get('username'):
            lines.append(f"  Username     : @{user_info.get('username')}")
    lines.append("")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"  TOTAL POST OFFICES: {len(post_offices)}")
    lines.append("")
    lines.append("-" * 60)
    lines.append("")
    for idx, po in enumerate(post_offices, 1):
        lines.append(f"  +-----------------------------+")
        lines.append(f"  |      POST OFFICE #{idx:<3}     |")
        lines.append(f"  +-----------------------------+")
        lines.append("")
        mapping = [
            ('Name', 'Name'), ('BranchType', 'Branch Type'),
            ('DeliveryStatus', 'Delivery Status'), ('Circle', 'Circle'),
            ('District', 'District'), ('Division', 'Division'),
            ('Region', 'Region'), ('Block', 'Block'),
            ('State', 'State'), ('Country', 'Country'),
        ]
        for key, label in mapping:
            if po.get(key):
                lines.append(f"  {label:<15}: {po[key]}")
        lines.append("")
        lines.append("-" * 60)
        lines.append("")
    lines.append("=" * 60)
    lines.append(f"  Generated by: {BOT_NAME}")
    lines.append(f"  {POWERED_BY}")
    lines.append("=" * 60)
    return "\n".join(lines)

def txt_caption(query: str, user: dict, emoji_id: str, fallback: str) -> str:
    first = user.get('first_name', 'User')
    last = user.get('last_name', '')
    full = f"{first} {last}".strip()
    username = user.get('username')
    if username:
        mention = f'<a href="tg://user?id={user.get("id")}">@{username}</a>'
    else:
        mention = f'<a href="tg://user?id={user.get("id")}">{full}</a>'
    emoji = pe(emoji_id, fallback)
    return (
        "╔══════════════════════════════╗\n"
        f"║   {emoji} ᴅᴇᴛᴀɪʟꜱ ꜰᴏᴜɴᴅ {emoji}         ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_STAR()} {mention}\n\n"
        f"{E_CHECK()} <b>{sc('Here is your details')}</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_ROCKET()} <b>{sc('Query')}:</b> <code>{query}</code>\n"
        f"{E_BELL()} <b>{sc('Date')}:</b> <code>{datetime.now().strftime('%Y-%m-%d %H:%M')}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{E_GIFT()} <b>{sc('Check the TXT file below')}</b> 👇"
        + powered_by_footer()
    )

# ==================== FORMAT FUNCTIONS ====================
def powered_by_footer() -> str:
    return (
        "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_FIRE()} <b>ᴘᴏᴡᴇʀᴇᴅ ʙʏ</b> {E_FIRE()}\n"
        f"{E_ROCKET()} <b>{bold_unicode('SUBHA-X-MD')}</b> {E_ROCKET()}\n"
        f"{E_CROWN()} <b>ᴘʀᴇᴍɪᴜᴍ ᴇᴅɪᴛɪᴏɴ</b> {E_CROWN()}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

def format_number_response(response: str, term: str, retry: bool = True) -> tuple:
    if "Error" in response or not response:
        if retry:
            time.sleep(1)
            return format_number_response(http_get(NUMBER_API_ENDPOINT.replace('{term}', term)), term, False)
        return f"{E_CROSS()} <b>ᴇʀʀᴏʀ:</b> ɴᴏ ᴅᴀᴛᴀ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴛʜɪꜱ ɴᴜᴍʙᴇʀ.", None
    try:
        data = json.loads(response)
    except Exception:
        return f"{E_PHONE()} <b>ɴᴜᴍʙᴇʀ ʟᴏᴏᴋᴜᴘ ʀᴇꜱᴜʟᴛ</b>\n\n{clean_response(response)}", None
    if not data.get('success') or not data.get('found'):
        return f"{E_CROSS()} <b>ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ</b>\n\n<code>{term}</code>{powered_by_footer()}", None
    return "✅", data

def format_aadhaar_response(response: str, term: str, retry: bool = True) -> tuple:
    if "Error" in response or not response:
        if retry:
            time.sleep(1)
            return format_aadhaar_response(http_get(AADHAAR_API_ENDPOINT.replace('{term}', term)), term, False)
        return f"{E_CROSS()} <b>ᴇʀʀᴏʀ:</b> ɴᴏ ᴅᴀᴛᴀ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴛʜɪꜱ ᴀᴀᴅʜᴀᴀʀ.", None
    try:
        data = json.loads(response)
    except Exception:
        return f"{E_SHIELD()} <b>ᴀᴀᴅʜᴀᴀʀ ʟᴏᴏᴋᴜᴘ ʀᴇꜱᴜʟᴛ</b>\n\n{clean_response(response)}", None
    if not data.get('success') or not data.get('found'):
        return f"{E_CROSS()} <b>ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ</b>\n\n<code>{term}</code>{powered_by_footer()}", None
    return "✅", data

def format_email_response(response: str, term: str, retry: bool = True) -> tuple:
    if "Error" in response or not response:
        if retry:
            time.sleep(1)
            return format_email_response(http_get(EMAIL_API_ENDPOINT.replace('{term}', term)), term, False)
        return f"{E_CROSS()} <b>ᴇʀʀᴏʀ:</b> ɴᴏ ᴅᴀᴛᴀ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴛʜɪꜱ ᴇᴍᴀɪʟ.", None
    try:
        data = json.loads(response)
    except Exception:
        return f"{E_BELL()} <b>ᴇᴍᴀɪʟ ʟᴏᴏᴋᴜᴘ ʀᴇꜱᴜʟᴛ</b>\n\n{clean_response(response)}", None
    if not data.get('success') or not data.get('found'):
        return f"{E_CROSS()} <b>ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ</b>\n\n<code>{term}</code>{powered_by_footer()}", None
    return "✅", data

def format_pincode_response(response: str, term: str, retry: bool = True) -> tuple:
    if "Error" in response or not response:
        if retry:
            time.sleep(1)
            return format_pincode_response(http_get(PINCODE_API_ENDPOINT.replace('{term}', term)), term, False)
        return f"{E_CROSS()} <b>ᴇʀʀᴏʀ:</b> ɴᴏ ᴅᴀᴛᴀ ꜰᴏᴜɴᴅ ꜰᴏʀ ᴛʜɪꜱ ᴘɪɴᴄᴏᴅᴇ.", None
    try:
        data = json.loads(response)
    except Exception:
        return f"{E_SHIELD()} <b>ᴘɪɴᴄᴏᴅᴇ ʟᴏᴏᴋᴜᴘ ʀᴇꜱᴜʟᴛ</b>\n\n{clean_response(response)}", None
    if not isinstance(data, list) or not data:
        return f"{E_CROSS()} <b>ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ</b>\n\n<code>{term}</code>{powered_by_footer()}", None
    first = data[0]
    if first.get('Status') != 'Success':
        return f"{E_CROSS()} <b>ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ</b>\n\n<code>{term}</code>{powered_by_footer()}", None
    post_offices = first.get('PostOffice', [])
    if not post_offices:
        return f"{E_CROSS()} <b>ɴᴏ ʀᴇᴄᴏʀᴅꜱ ꜰᴏᴜɴᴅ</b>\n\n<code>{term}</code>{powered_by_footer()}", None
    return "✅", {'result': post_offices, 'count': len(post_offices)}

# ==================== STATIC MESSAGES ====================
def welcome_message(user: dict, chat_title: str) -> str:
    name = user.get('first_name', 'User')
    last = user.get('last_name', '')
    full_name = f"{name} {last}".strip()
    return (
        "╔══════════════════════════════╗\n"
        f"║   {E_GIFT()} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴛʜᴇ ɢʀᴏᴜᴘ {E_GIFT()}   ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_STAR()} <a href=\"tg://user?id={user.get('id')}\">{full_name}</a>\n"
        f"{E_SHIELD()} <code>{user.get('id')}</code>\n"
        f"{E_CROWN()} {chat_title}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PHONE()} <code>/num &lt;10-digit&gt;</code>\n"
        f"{E_SHIELD()} <code>/adhar &lt;12-digit&gt;</code>\n"
        f"{E_BELL()} <code>/gmail &lt;email&gt;</code>\n"
        f"{E_SHIELD()} <code>/pincode &lt;6-digit&gt;</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{E_BELL()} <b>ᴋɴᴏᴡ ᴡɪᴛʜ ᴜꜱ</b> 👇"
    )

def goodbye_message(user: dict, chat_title: str) -> str:
    name = user.get('first_name', 'User')
    last = user.get('last_name', '')
    full_name = f"{name} {last}".strip()
    return (
        "╔══════════════════════════════╗\n"
        f"║      {E_STAR()} ɢᴏᴏᴅʙʏᴇ ᴍᴇᴍʙᴇʀ {E_STAR()}     ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_STAR()} <code>{full_name}</code>\n"
        f"{E_SHIELD()} <code>{user.get('id')}</code>\n"
        f"{E_CROWN()} {chat_title}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_STAR()} <b>ᴡᴇ ᴡɪꜱʜ ʏᴏᴜ ᴀʟʟ ᴛʜᴇ ʙᴇꜱᴛ!</b>\n"
        f"{E_GIFT()} <b>ʜᴏᴘᴇ ᴛᴏ ꜱᴇᴇ ʏᴏᴜ ꜱᴏᴏɴ.</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{E_BELL()} <b>ꜱᴛᴀʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ</b> 👇"
    )

def private_message() -> str:
    return (
        "╔══════════════════════════════╗\n"
        f"║   {E_LOCK()} ᴘʀɪᴠᴀᴛᴇ ᴏɴʟʏ ʙᴏᴛ {E_LOCK()}        ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_WARNING()} <b>ᴛʜɪꜱ ʙᴏᴛ ᴏɴʟʏ ᴡᴏʀᴋꜱ ɪɴ ɢʀᴏᴜᴘꜱ!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_GEAR()} <b>ʜᴏᴡ ᴛᴏ ᴜꜱᴇ:</b>\n"
        "1️⃣ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ\n"
        "2️⃣ ᴜꜱᴇ ᴄᴏᴍᴍᴀɴᴅꜱ ʙᴇʟᴏᴡ\n"
        "3️⃣ ɢᴇᴛ ɪɴꜱᴛᴀɴᴛ ʀᴇꜱᴜʟᴛꜱ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{E_STAR()} <b>ᴄᴏᴍᴍᴀɴᴅꜱ:</b>\n"
        f"{E_PHONE()} <code>/num &lt;10-digit&gt;</code>\n"
        f"{E_SHIELD()} <code>/adhar &lt;12-digit&gt;</code>\n"
        f"{E_BELL()} <code>/gmail &lt;email&gt;</code>\n"
        f"{E_SHIELD()} <code>/pincode &lt;6-digit&gt;</code>\n"
        f"{E_GEAR()} <code>/help</code> | {E_CROWN()} <code>/owner</code>\n"
        f"{E_WARNING()} <code>/about</code>\n\n"
        f"{E_BELL()} <b>ᴋɴᴏᴡ ᴡɪᴛʜ ᴜꜱ</b> 👇"
    )

def help_message() -> str:
    return (
        "╔══════════════════════════════╗\n"
        f"║    {E_GEAR()} ʜᴇʟᴘ & ᴜꜱᴀɢᴇ ɢᴜɪᴅᴇ     ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_STAR()} <b>ᴀᴠᴀɪʟᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅꜱ</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_PHONE()} <b>ɴᴜᴍʙᴇʀ</b>\n<code>/num 9876543210</code>\n\n"
        f"{E_SHIELD()} <b>ᴀᴀᴅʜᴀᴀʀ</b>\n<code>/adhar 123456789012</code>\n\n"
        f"{E_BELL()} <b>ᴇᴍᴀɪʟ</b>\n<code>/gmail user@gmail.com</code>\n\n"
        f"{E_SHIELD()} <b>ᴘɪɴᴄᴏᴅᴇ</b>\n<code>/pincode 722134</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🔹 <code>/start</code> • <code>/help</code>\n"
        f"🔹 <code>/owner</code> • <code>/about</code>\n"
        f"🔹 <code>/id</code> • <code>/ping</code> • <code>/stats</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
        + powered_by_footer()
    )

def owner_message() -> str:
    return (
        "╔══════════════════════════════╗\n"
        f"║       {E_CROWN()} ʙᴏᴛ ᴏᴡɴᴇʀ {E_CROWN()}        ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_STAR()} <b>ɴᴀᴍᴇ:</b> {OWNER_NAME}\n"
        f"{E_BELL()} <b>ᴜꜱᴇʀɴᴀᴍᴇ:</b> {OWNER_USERNAME}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_GEAR()} <b>ꜰᴏʀ ᴀɴʏ ɪꜱꜱᴜᴇ ᴏʀ ǫᴜᴇʀʏ\nᴅᴍ ᴛʜᴇ ᴏᴡɴᴇʀ.</b>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
        + powered_by_footer()
    )

def about_message() -> str:
    return (
        "╔══════════════════════════════╗\n"
        f"║       {E_WARNING()} ᴀʙᴏᴜᴛ ᴛʜɪꜱ ʙᴏᴛ       ║\n"
        "╚══════════════════════════════╝\n\n"
        f"🤖 <b>ɴᴀᴍᴇ:</b> {BOT_NAME}\n"
        f"{E_ROCKET()} <b>ᴠᴇʀꜱɪᴏɴ:</b> {BOT_VERSION}\n"
        f"{E_STAR()} <b>ᴛʏᴘᴇ:</b> ᴏꜱɪɴᴛ ʟᴏᴏᴋᴜᴘ\n"
        f"{E_LOCK()} <b>ᴘʀɪᴠᴀᴄʏ:</b> ɢʀᴏᴜᴘ ᴏɴʟʏ\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_STAR()} <b>ꜰᴇᴀᴛᴜʀᴇꜱ:</b>\n"
        f"{E_PHONE()} ɴᴜᴍʙᴇʀ ʟᴏᴏᴋᴜᴘ\n"
        f"{E_SHIELD()} ᴀᴀᴅʜᴀᴀʀ ʟᴏᴏᴋᴜᴘ\n"
        f"{E_BELL()} ᴇᴍᴀɪʟ ʟᴏᴏᴋᴜᴘ\n"
        f"{E_SHIELD()} ᴘɪɴᴄᴏᴅᴇ ʟᴏᴏᴋᴜᴘ\n"
        f"{E_GEAR()} ᴛxᴛ ꜰɪʟᴇ ᴇxᴘᴏʀᴛ\n"
        f"{E_ROCKET()} ꜰᴀꜱᴛ ʀᴇꜱᴘᴏɴꜱᴇ\n"
        f"{E_STAR()} ᴘʀᴇᴍɪᴜᴍ ᴅᴇꜱɪɢɴ\n"
        f"{E_GIFT()} ᴀᴜᴛᴏ ᴡᴇʟᴄᴏᴍᴇ/ɢᴏᴏᴅʙʏᴇ\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_SHIELD()} <b>ᴅɪꜱᴄʟᴀɪᴍᴇʀ:</b> ᴛʜɪꜱ ʙᴏᴛ ɪꜱ ꜰᴏʀ\n"
        "ᴇᴅᴜᴄᴀᴛɪᴏɴᴀʟ ᴘᴜʀᴘᴏꜱᴇꜱ ᴏɴʟʏ.\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
        + powered_by_footer()
    )

def start_message() -> str:
    return (
        "╔══════════════════════════════╗\n"
        f"║ {E_FIRE()} ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴏꜱɪɴᴛ ʟᴏᴏᴋᴜᴘ {E_FIRE()} ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_ROCKET()} <b>{BOT_NAME}</b>\n"
        f"{E_STAR()} {BOT_VERSION}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_STAR()} <b>ꜰᴇᴀᴛᴜʀᴇꜱ:</b>\n"
        f"{E_PHONE()} ɴᴜᴍʙᴇʀ • {E_SHIELD()} ᴀᴀᴅʜᴀᴀʀ\n"
        f"{E_BELL()} ᴇᴍᴀɪʟ • {E_SHIELD()} ᴘɪɴᴄᴏᴅᴇ\n"
        f"{E_GEAR()} ᴛxᴛ ꜰɪʟᴇ ᴇxᴘᴏʀᴛ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{E_STAR()} <b>ǫᴜɪᴄᴋ ꜱᴛᴀʀᴛ:</b>\n"
        f"{E_PHONE()} <code>/num 9876543210</code>\n"
        f"{E_SHIELD()} <code>/adhar 123456789012</code>\n"
        f"{E_BELL()} <code>/gmail user@gmail.com</code>\n"
        f"{E_SHIELD()} <code>/pincode 722134</code>\n\n"
        f"{E_GEAR()} ᴛʏᴘᴇ <code>/help</code> ꜰᴏʀ ᴍᴏʀᴇ\n\n"
        f"{E_CROWN()} <b>ᴏᴡɴᴇʀ:</b> {OWNER_USERNAME}\n"
        f"{E_BELL()} <b>ᴄʜᴀɴɴᴇʟ:</b> {SUPPORT_CHANNEL}"
        + powered_by_footer()
    )

# ==================== ADMIN PANEL ====================
def admin_panel_message() -> str:
    groups = get_groups()
    banned = get_banned_users()
    stats = load_stats()
    uptime = int(time.time() - stats.get('start_time', time.time()))
    hours = uptime // 3600
    minutes = (uptime % 3600) // 60
    return (
        "╔══════════════════════════════╗\n"
        f"║      {E_CROWN()} ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ {E_CROWN()}       ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_STAR()} <b>ᴡᴇʟᴄᴏᴍᴇ ᴏᴡɴᴇʀ!</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_GEAR()} <b>ǫᴜɪᴄᴋ ꜱᴛᴀᴛꜱ:</b>\n"
        f"{E_CROWN()} <b>ɢʀᴏᴜᴘꜱ:</b> <code>{len(groups)}</code>\n"
        f"{E_SHIELD()} <b>ʙᴀɴɴᴇᴅ:</b> <code>{len(banned)}</code>\n"
        f"{E_STAR()} <b>ᴜᴘᴛɪᴍᴇ:</b> <code>{hours}ʜ {minutes}ᴍ</code>\n"
        f"{E_GEAR()} <b>ᴛᴏᴛᴀʟ ǫᴜᴇʀɪᴇꜱ:</b> <code>{stats.get('total_queries', 0)}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{E_STAR()} <b>ꜱᴇʟᴇᴄᴛ ᴀɴ ᴏᴘᴛɪᴏɴ ʙᴇʟᴏᴡ:</b>"
    )

def admin_stats_message() -> str:
    stats = load_stats()
    groups = get_groups()
    banned = get_banned_users()
    uptime = int(time.time() - stats.get('start_time', time.time()))
    hours = uptime // 3600
    minutes = (uptime % 3600) // 60
    seconds = uptime % 60
    days = hours // 24
    hours = hours % 24
    return (
        "╔══════════════════════════════╗\n"
        f"║      {E_GEAR()} ᴅᴇᴛᴀɪʟᴇᴅ ꜱᴛᴀᴛꜱ       ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_STAR()} <b>ᴜᴘᴛɪᴍᴇ</b>\n"
        f"<code>{days}ᴅ {hours}ʜ {minutes}ᴍ {seconds}ꜱ</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_GEAR()} <b>ǫᴜᴇʀʏ ꜱᴛᴀᴛꜱ</b>\n"
        f"{E_PHONE()} ɴᴜᴍʙᴇʀ: <code>{stats.get('num_queries', 0)}</code>\n"
        f"{E_SHIELD()} ᴀᴀᴅʜᴀᴀʀ: <code>{stats.get('adhar_queries', 0)}</code>\n"
        f"{E_BELL()} ᴇᴍᴀɪʟ: <code>{stats.get('gmail_queries', 0)}</code>\n"
        f"{E_SHIELD()} ᴘɪɴᴄᴏᴅᴇ: <code>{stats.get('pincode_queries', 0)}</code>\n"
        f"{E_GEAR()} ᴛᴏᴛᴀʟ: <code>{stats.get('total_queries', 0)}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_CROWN()} <b>ɢʀᴏᴜᴘ ꜱᴛᴀᴛꜱ</b>\n"
        f"{E_CROWN()} ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘꜱ: <code>{len(groups)}</code>\n"
        f"{E_SHIELD()} ʙᴀɴɴᴇᴅ: <code>{len(banned)}</code>\n"
        f"{E_GIFT()} ᴡᴇʟᴄᴏᴍᴇꜱ: <code>{stats.get('welcome_count', 0)}</code>\n"
        f"{E_STAR()} ɢᴏᴏᴅʙʏᴇꜱ: <code>{stats.get('goodbye_count', 0)}</code>\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

def admin_groups_message() -> str:
    groups = get_groups()
    if not groups:
        return (
            "╔══════════════════════════════╗\n"
            f"║        {E_CROWN()} ɢʀᴏᴜᴘ ʟɪꜱᴛ          ║\n"
            "╚══════════════════════════════╝\n\n"
            f"{E_CROSS()} <b>ɴᴏ ɢʀᴏᴜᴘꜱ ʏᴇᴛ!</b>\n\n"
            "ᴀᴅᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴀ ɢʀᴏᴜᴘ ᴛᴏ ꜱᴛᴀʀᴛ."
        )
    out = (
        "╔══════════════════════════════╗\n"
        f"║        {E_CROWN()} ɢʀᴏᴜᴘ ʟɪꜱᴛ          ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_GEAR()} <b>ᴛᴏᴛᴀʟ:</b> <code>{len(groups)}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    for i, (gid, info) in enumerate(list(groups.items())[:20], 1):
        title = info.get('title', 'Unknown')[:25]
        out += f"{i}. <b>{title}</b>\n"
        out += f"   <code>{gid}</code>\n"
        out += f"   {E_BELL()} {info.get('added_at', 'N/A')[:10]}\n\n"
    if len(groups) > 20:
        out += f"... ᴀɴᴅ {len(groups) - 20} ᴍᴏʀᴇ\n"
    out += "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    return out

def admin_banned_message() -> str:
    banned = get_banned_users()
    if not banned:
        return (
            "╔══════════════════════════════╗\n"
            f"║       {E_SHIELD()} ʙᴀɴɴᴇᴅ ʟɪꜱᴛ         ║\n"
            "╚══════════════════════════════╝\n\n"
            f"{E_CHECK()} <b>ɴᴏ ʙᴀɴɴᴇᴅ ᴜꜱᴇʀꜱ!</b>\n\n"
            "ᴜꜱᴇ <code>/ban &lt;user_id&gt;</code> ᴛᴏ ʙᴀɴ"
        )
    out = (
        "╔══════════════════════════════╗\n"
        f"║       {E_SHIELD()} ʙᴀɴɴᴇᴅ ʟɪꜱᴛ         ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_GEAR()} <b>ᴛᴏᴛᴀʟ:</b> <code>{len(banned)}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    )
    for i, uid in enumerate(banned, 1):
        out += f"{i}. <code>{uid}</code>\n"
    out += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    out += "ᴜꜱᴇ <code>/unban &lt;user_id&gt;</code> ᴛᴏ ᴜɴʙᴀɴ"
    return out

def admin_settings_message() -> str:
    settings = get_settings()
    return (
        "╔══════════════════════════════╗\n"
        f"║      {E_GEAR()} ꜱᴇᴛᴛɪɴɢꜱ ᴍᴇɴᴜ        ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_STAR()} <b>ᴛᴏɢɢʟᴇ ᴏᴘᴛɪᴏɴꜱ ʙᴇʟᴏᴡ:</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_GIFT()} ᴡᴇʟᴄᴏᴍᴇ: {'✅ ᴏɴ' if settings.get('welcome_enabled', True) else '❌ ᴏꜰꜰ'}\n"
        f"{E_STAR()} ɢᴏᴏᴅʙʏᴇ: {'✅ ᴏɴ' if settings.get('goodbye_enabled', True) else '❌ ᴏꜰꜰ'}\n"
        f"{E_GEAR()} ᴛxᴛ ᴇxᴘᴏʀᴛ: {'✅ ᴏɴ' if settings.get('txt_export', True) else '❌ ᴏꜰꜰ'}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    )

def admin_logs_message() -> str:
    try:
        log_file = os.path.join(LOG_DIR, f'activity_{datetime.now().strftime("%Y-%m")}.log')
        if not os.path.exists(log_file):
            return f"{E_GEAR()} <b>ɴᴏ ʟᴏɢꜱ ʏᴇᴛ!</b>"
        with open(log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        recent = lines[-20:] if len(lines) > 20 else lines
        out = (
            "╔══════════════════════════════╗\n"
            f"║       {E_GEAR()} ʀᴇᴄᴇɴᴛ ʟᴏɢꜱ         ║\n"
            "╚══════════════════════════════╝\n\n"
            f"{E_GEAR()} <b>ᴛᴏᴛᴀʟ ʟᴏɢꜱ:</b> <code>{len(lines)}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        )
        for line in recent:
            out += f"<code>{line.strip()[:80]}</code>\n"
        out += "━━━━━━━━━━━━━━━━━━━━━━━━━━"
        return out
    except Exception as e:
        return f"{E_CROSS()} <b>ᴇʀʀᴏʀ:</b> {e}"

# ==================== BROADCAST ====================
BROADCAST_STATE = {}

def start_broadcast(user_id: int, chat_id: str):
    BROADCAST_STATE[user_id] = {
        'step': 'awaiting_message',
        'chat_id': chat_id,
        'started_at': time.time()
    }
    send_message(chat_id, (
        "╔══════════════════════════════╗\n"
        f"║       {E_BELL()} ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴍᴏᴅᴇ       ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_GEAR()} <b>ꜱᴇɴᴅ ᴛʜᴇ ᴍᴇꜱꜱᴀɢᴇ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ</b>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_STAR()} <b>ᴛɪᴘꜱ:</b>\n"
        "• ꜱᴜᴘᴘᴏʀᴛꜱ ᴛᴇxᴛ ᴀɴᴅ ᴇᴍᴏᴊɪ\n"
        "• ᴜꜱᴇ /cancel ᴛᴏ ᴄᴀɴᴄᴇʟ\n"
        "• ᴡɪʟʟ ʙᴇ ꜱᴇɴᴛ ᴛᴏ ᴀʟʟ ɢʀᴏᴜᴘꜱ\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━"
    ))

def execute_broadcast(user_id: int, message_text: str, chat_id: str):
    groups = get_groups()
    if not groups:
        send_message(chat_id, f"{E_CROSS()} <b>ɴᴏ ɢʀᴏᴜᴘꜱ ᴛᴏ ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴛᴏ!</b>")
        return
    formatted_msg = sc(message_text)
    broadcast_text = (
        "╔══════════════════════════════╗\n"
        f"║      {E_BELL()} ᴀɴɴᴏᴜɴᴄᴇᴍᴇɴᴛ {E_BELL()}       ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{formatted_msg}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_CROWN()} <b>ᴏᴡɴᴇʀ:</b> " + OWNER_USERNAME + "\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{E_BELL()} <b>ꜱᴛᴀʏ ᴄᴏɴɴᴇᴄᴛᴇᴅ</b> 👇"
    )
    status_msg = send_message(chat_id, (
        "╔══════════════════════════════╗\n"
        f"║    {E_ROCKET()} ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...       ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_CROWN()} <b>ᴛᴏᴛᴀʟ ɢʀᴏᴜᴘꜱ:</b> <code>{len(groups)}</code>\n"
        f"{E_STAR()} ᴘʟᴇᴀꜱᴇ ᴡᴀɪᴛ..."
    ))
    if not status_msg or not status_msg.get('ok'):
        return
    status_msg_id = status_msg['result']['message_id']
    success = 0
    failed = 0
    for gid, info in groups.items():
        try:
            result = send_photo(gid, BROADCAST_IMAGE, broadcast_text, social_buttons())
            if result and result.get('ok'):
                success += 1
            else:
                result = send_message(gid, broadcast_text, social_buttons())
                if result and result.get('ok'):
                    success += 1
                else:
                    failed += 1
        except Exception as e:
            logger.error(f"Broadcast failed to {gid}: {e}")
            failed += 1
        time.sleep(0.5)
        if (success + failed) % 5 == 0:
            edit_message(chat_id, status_msg_id, (
                "╔══════════════════════════════╗\n"
                f"║    {E_ROCKET()} ʙʀᴏᴀᴅᴄᴀꜱᴛɪɴɢ...       ║\n"
                "╚══════════════════════════════╝\n\n"
                f"{E_CHECK()} <b>ꜱᴇɴᴛ:</b> <code>{success}</code>\n"
                f"{E_CROSS()} <b>ꜰᴀɪʟᴇᴅ:</b> <code>{failed}</code>\n"
                f"{E_GEAR()} <b>ᴘʀᴏɢʀᴇꜱꜱ:</b> <code>{success + failed}/{len(groups)}</code>"
            ))
    edit_message(chat_id, status_msg_id, (
        "╔══════════════════════════════╗\n"
        f"║   {E_CHECK()} ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴏᴍᴘʟᴇᴛᴇ {E_CHECK()}   ║\n"
        "╚══════════════════════════════╝\n\n"
        f"{E_CHECK()} <b>ꜱᴜᴄᴄᴇꜱꜱ:</b> <code>{success}</code>\n"
        f"{E_CROSS()} <b>ꜰᴀɪʟᴇᴅ:</b> <code>{failed}</code>\n"
        f"{E_GEAR()} <b>ᴛᴏᴛᴀʟ:</b> <code>{len(groups)}</code>\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{E_BELL()} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    ))

# ==================== CALLBACK HANDLER ====================
def handle_callback(callback: Dict) -> None:
    callback_id = callback['id']
    user_id = callback['from']['id']
    chat_id = str(callback['message']['chat']['id'])
    message_id = callback['message']['message_id']
    data = callback.get('data', '')
    is_owner = (user_id == OWNER_ID) or (OWNER_ID == 0)
    if not is_owner:
        answer_callback(callback_id, "❌ ᴏᴡɴᴇʀ ᴏɴʟʏ!")
        return
    answer_callback(callback_id, "✅")
    
    back_kb = {'inline_keyboard': [[{'text': "⬅️ ʙᴀᴄᴋ", 'callback_data': 'admin_back', 'style': 'danger'}]]}
    
    if data == 'admin_broadcast':
        start_broadcast(user_id, chat_id)
    elif data == 'admin_stats':
        edit_message(chat_id, message_id, admin_stats_message(), back_kb)
    elif data == 'admin_groups':
        edit_message(chat_id, message_id, admin_groups_message(), back_kb)
    elif data == 'admin_banned':
        edit_message(chat_id, message_id, admin_banned_message(), back_kb)
    elif data == 'admin_logs':
        edit_message(chat_id, message_id, admin_logs_message(), back_kb)
    elif data == 'admin_settings':
        edit_message(chat_id, message_id, admin_settings_message(), settings_keyboard())
    elif data == 'admin_refresh':
        edit_message(chat_id, message_id, admin_panel_message(), admin_panel_keyboard())
    elif data == 'admin_close':
        edit_message(chat_id, message_id, f"{E_CROSS()} <b>ᴀᴅᴍɪɴ ᴘᴀɴᴇʟ ᴄʟᴏꜱᴇᴅ!</b>")
    elif data == 'admin_back':
        edit_message(chat_id, message_id, admin_panel_message(), admin_panel_keyboard())
    elif data == 'toggle_welcome':
        settings = get_settings()
        settings['welcome_enabled'] = not settings.get('welcome_enabled', True)
        save_settings(settings)
        edit_message(chat_id, message_id, admin_settings_message(), settings_keyboard())
    elif data == 'toggle_goodbye':
        settings = get_settings()
        settings['goodbye_enabled'] = not settings.get('goodbye_enabled', True)
        save_settings(settings)
        edit_message(chat_id, message_id, admin_settings_message(), settings_keyboard())
    elif data == 'toggle_txt':
        settings = get_settings()
        settings['txt_export'] = not settings.get('txt_export', True)
        save_settings(settings)
        edit_message(chat_id, message_id, admin_settings_message(), settings_keyboard())
    elif data == 'broadcast_send':
        if user_id in BROADCAST_STATE:
            state = BROADCAST_STATE[user_id]
            broadcast_msg = state.get('message', '')
            del BROADCAST_STATE[user_id]
            edit_message(chat_id, message_id, f"{E_ROCKET()} <b>ꜱᴛᴀʀᴛɪɴɢ ʙʀᴏᴀᴅᴄᴀꜱᴛ...</b>")
            execute_broadcast(user_id, broadcast_msg, chat_id)
        else:
            answer_callback(callback_id, "❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ʙʀᴏᴀᴅᴄᴀꜱᴛ!")
    elif data == 'broadcast_cancel':
        if user_id in BROADCAST_STATE:
            del BROADCAST_STATE[user_id]
        edit_message(chat_id, message_id, f"{E_CROSS()} <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")

# ==================== MESSAGE HANDLER ====================
def handle_message(update: Dict) -> None:
    message = update.get('message')
    callback = update.get('callback_query')
    if not message and not callback:
        return
    if callback:
        handle_callback(callback)
        return
    
    if 'new_chat_members' in message:
        chat_id = str(message['chat']['id'])
        chat_type = message['chat'].get('type', 'private')
        chat_title = message['chat'].get('title', 'Group')
        if chat_type in ['group', 'supergroup']:
            groups = get_groups()
            if str(chat_id) not in groups:
                save_group(int(chat_id), chat_title, chat_type)
            settings = get_settings()
            if not settings.get('welcome_enabled', True):
                return
            for new_member in message['new_chat_members']:
                if new_member.get('is_bot'):
                    continue
                try:
                    send_photo(chat_id, WELCOME_IMAGE, welcome_message(new_member, chat_title), social_buttons())
                    increment_stat('welcome_count')
                    log_activity(new_member.get('id', 0), 'JOINED_GROUP', chat_title)
                except Exception as e:
                    logger.error(f"Welcome failed: {e}")
        return
    
    if 'left_chat_member' in message:
        chat_id = str(message['chat']['id'])
        chat_type = message['chat'].get('type', 'private')
        chat_title = message['chat'].get('title', 'Group')
        if chat_type in ['group', 'supergroup']:
            groups = get_groups()
            if str(chat_id) not in groups:
                save_group(int(chat_id), chat_title, chat_type)
            settings = get_settings()
            if not settings.get('goodbye_enabled', True):
                return
            left_member = message['left_chat_member']
            if not left_member.get('is_bot'):
                try:
                    send_message(chat_id, goodbye_message(left_member, chat_title), social_buttons())
                    increment_stat('goodbye_count')
                    log_activity(left_member.get('id', 0), 'LEFT_GROUP', chat_title)
                except Exception as e:
                    logger.error(f"Goodbye failed: {e}")
        return
    
    chat_id = str(message['chat']['id'])
    chat_type = message['chat'].get('type', 'private')
    text = message.get('text', '').strip()
    user = message.get('from', {})
    user_id = user.get('id', 0)
    if not text:
        return
    if is_banned(user_id):
        return
    if text.startswith('/'):
        text = re.sub(r'^(\/[a-zA-Z0-9_]+)@[a-zA-Z0-9_]+', r'\1', text)
    
    is_group = chat_type in ['group', 'supergroup']
    is_owner = (user_id == OWNER_ID) or (OWNER_ID == 0)
    
    if user_id in BROADCAST_STATE and not is_group:
        state = BROADCAST_STATE[user_id]
        if text == '/cancel':
            del BROADCAST_STATE[user_id]
            send_message(chat_id, f"{E_CROSS()} <b>ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴄᴀɴᴄᴇʟʟᴇᴅ!</b>")
            return
        if state['step'] == 'awaiting_message':
            preview = (
                "╔══════════════════════════════╗\n"
                f"║     {E_BELL()} ʙʀᴏᴀᴅᴄᴀꜱᴛ ᴘʀᴇᴠɪᴇᴡ      ║\n"
                "╚══════════════════════════════╝\n\n"
                f"{E_GEAR()} <b>ʏᴏᴜʀ ᴍᴇꜱꜱᴀɢᴇ:</b>\n\n"
                f"{sc(text)}\n\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                f"{E_CROWN()} <b>ᴡɪʟʟ ʙᴇ ꜱᴇɴᴛ ᴛᴏ:</b> <code>{len(get_groups())}</code> ɢʀᴏᴜᴘꜱ\n"
                "━━━━━━━━━━━━━━━━━━━━━━━━━━"
            )
            BROADCAST_STATE[user_id] = {
                'step': 'confirming',
                'chat_id': chat_id,
                'message': text
            }
            send_message(chat_id, preview, {
                'inline_keyboard': [
                    [
                        {'text': "✅ ꜱᴇɴᴅ ɴᴏᴡ", 'callback_data': 'broadcast_send', 'style': 'success'},
                        {'text': "❌ ᴄᴀɴᴄᴇʟ", 'callback_data': 'broadcast_cancel', 'style': 'danger'}
                    ]
                ]
            })
        return
    
    if not is_group:
        if is_owner:
            if text in ['/admin', '/panel', '/dashboard']:
                send_message(chat_id, admin_panel_message(), admin_panel_keyboard())
                return
            if text == '/broadcast':
                start_broadcast(user_id, chat_id)
                return
            if text.startswith('/ban'):
                parts = text.split()
                if len(parts) >= 2:
                    try:
                        target = int(parts[1])
                        ban_user(target)
                        send_message(chat_id, f"{E_CHECK()} <b>ᴜꜱᴇʀ ʙᴀɴɴᴇᴅ:</b> <code>{target}</code>")
                    except ValueError:
                        send_message(chat_id, f"{E_CROSS()} <b>ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ!</b>")
                else:
                    send_message(chat_id, f"{E_CROSS()} <b>ᴜꜱᴇ:</b> <code>/ban &lt;user_id&gt;</code>")
                return
            if text.startswith('/unban'):
                parts = text.split()
                if len(parts) >= 2:
                    try:
                        target = int(parts[1])
                        unban_user(target)
                        send_message(chat_id, f"{E_CHECK()} <b>ᴜꜱᴇʀ ᴜɴʙᴀɴɴᴇᴅ:</b> <code>{target}</code>")
                    except ValueError:
                        send_message(chat_id, f"{E_CROSS()} <b>ɪɴᴠᴀʟɪᴅ ᴜꜱᴇʀ ɪᴅ!</b>")
                else:
                    send_message(chat_id, f"{E_CROSS()} <b>ᴜꜱᴇ:</b> <code>/unban &lt;user_id&gt;</code>")
                return
            if text == '/groups':
                send_message(chat_id, admin_groups_message())
                return
            if text == '/banned':
                send_message(chat_id, admin_banned_message())
                return
            if text == '/logs':
                send_message(chat_id, admin_logs_message())
                return
        
        if text == '/id':
            uname = user.get('username', 'N/A')
            send_message(chat_id, (
                "╔══════════════════════════════╗\n"
                f"║          {E_SHIELD()} ʏᴏᴜʀ ɪᴅ           ║\n"
                "╚══════════════════════════════╝\n\n"
                f"{E_STAR()} <b>ɴᴀᴍᴇ:</b> <code>{user.get('first_name', 'N/A')}</code>\n"
                f"{E_SHIELD()} <b>ɪᴅ:</b> <code>{user_id}</code>\n"
                f"{E_BELL()} <b>ᴜꜱᴇʀɴᴀᴍᴇ:</b> @{uname if uname != 'N/A' else 'N/A'}\n"
                + powered_by_footer()
            ))
        elif text in ['/admin', '/panel'] and not is_owner:
            send_message(chat_id, f"{E_CROSS()} <b>ᴏᴡɴᴇʀ ᴏɴʟʏ!</b>")
        else:
            send_message(chat_id, private_message(), social_buttons())
        return
    
    if ALLOWED_GROUP_IDS and int(chat_id) not in ALLOWED_GROUP_IDS:
        logger.info(f"Unauthorized group: {chat_id}")
        return
    
    chat_title = message['chat'].get('title', 'Unknown Group')
    groups = get_groups()
    if str(chat_id) not in groups:
        save_group(int(chat_id), chat_title, chat_type)
        logger.info(f"New group auto-saved: {chat_title} ({chat_id})")
    update_group_activity(int(chat_id))
    settings = get_settings()
    show_txt = settings.get('txt_export', True)
    
    if text == '/start':
        send_photo(chat_id, START_IMAGE, start_message(), social_buttons())
        return
    if text == '/help':
        send_message(chat_id, help_message(), social_buttons())
        return
    if text == '/about':
        send_message(chat_id, about_message(), social_buttons())
        return
    if text == '/owner':
        send_message(chat_id, owner_message(), social_buttons())
        return
    if text == '/id':
        uname = user.get('username', 'N/A')
        send_message(chat_id, (
            "╔══════════════════════════════╗\n"
            f"║          {E_SHIELD()} ʏᴏᴜʀ ɪᴅ           ║\n"
            "╚══════════════════════════════╝\n\n"
            f"{E_STAR()} <b>ɴᴀᴍᴇ:</b> <code>{user.get('first_name', 'N/A')}</code>\n"
            f"{E_SHIELD()} <b>ɪᴅ:</b> <code>{user_id}</code>\n"
            f"{E_BELL()} <b>ᴜꜱᴇʀɴᴀᴍᴇ:</b> @{uname if uname != 'N/A' else 'N/A'}\n"
            + powered_by_footer()
        ))
        return
    if text == '/ping':
        t1 = time.time()
        send_message(chat_id, f"{E_STAR()} <b>ᴘɪɴɢɪɴɢ...</b>")
        t2 = time.time()
        latency = int((t2 - t1) * 1000)
        send_message(chat_id, (
            "╔══════════════════════════════╗\n"
            f"║           {E_STAR()} ᴘᴏɴɢ!             ║\n"
            "╚══════════════════════════════╝\n\n"
            f"{E_ROCKET()} <b>ʟᴀᴛᴇɴᴄʏ:</b> <code>{latency} ms</code>\n"
            f"{E_CHECK()} <b>ꜱᴛᴀᴛᴜꜱ:</b> ᴏɴʟɪɴᴇ\n"
            + powered_by_footer()
        ))
        return
    if text == '/stats':
        stats = load_stats()
        uptime = int(time.time() - stats.get('start_time', time.time()))
        hours = uptime // 3600
        minutes = (uptime % 3600) // 60
        seconds = uptime % 60
        send_message(chat_id, (
            "╔══════════════════════════════╗\n"
            f"║       {E_GEAR()} ʙᴏᴛ ꜱᴛᴀᴛɪꜱᴛɪᴄꜱ       ║\n"
            "╚══════════════════════════════╝\n\n"
            f"{E_STAR()} <b>ᴜᴘᴛɪᴍᴇ:</b> {hours}ʜ {minutes}ᴍ {seconds}ꜱ\n"
            f"{E_GEAR()} <b>ǫᴜᴇʀɪᴇꜱ:</b> <code>{stats.get('total_queries', 0)}</code>\n"
            f"{E_GIFT()} <b>ᴡᴇʟᴄᴏᴍᴇꜱ:</b> <code>{stats.get('welcome_count', 0)}</code>\n"
            f"{E_STAR()} <b>ɢᴏᴏᴅʙʏᴇꜱ:</b> <code>{stats.get('goodbye_count', 0)}</code>\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{E_PHONE()} ɴᴜᴍʙᴇʀ: {stats.get('num_queries', 0)}\n"
            f"{E_SHIELD()} ᴀᴀᴅʜᴀᴀʀ: {stats.get('adhar_queries', 0)}\n"
            f"{E_BELL()} ᴇᴍᴀɪʟ: {stats.get('gmail_queries', 0)}\n"
            f"{E_SHIELD()} ᴘɪɴᴄᴏᴅᴇ: {stats.get('pincode_queries', 0)}\n"
            + powered_by_footer()
        ))
        return
    
    if text.startswith('/num'):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, f"{E_CROSS()} <b>ᴘʀᴏᴠɪᴅᴇ ǫᴜᴇʀʏ!</b>\n\n{E_CHECK()} <b>ᴜꜱᴇ:</b> <code>/num 9876543210</code>")
            return
        query = parts[1].strip()
        if not re.match(r'^\d{10}$', query):
            send_message(chat_id, f"{E_CROSS()} <b>ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ!</b>\n\nᴜꜱᴇ 10 ᴅɪɢɪᴛꜱ.\n\n{E_PHONE()} <code>/num 9876543210</code>")
            return
        send_chat_action(chat_id, 'typing')
        premium_loading(chat_id, "ꜰᴇᴛᴄʜɪɴɢ ɴᴜᴍʙᴇʀ ᴅᴀᴛᴀ", style='phone')
        increment_stat('num_queries')
        increment_stat('total_queries')
        log_activity(user_id, 'NUM_LOOKUP', query)
        response = http_get(NUMBER_API_ENDPOINT.replace('{term}', query))
        msg, data = format_number_response(response, query)
        if data and show_txt:
            txt_content = generate_txt_content(f"📱 NUMBER LOOKUP RESULT", query, data, user)
            filename = f"number_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            send_document(chat_id, txt_content.encode('utf-8'), filename, txt_caption(query, user, EMOJI_PHONE, "📱"))
        else:
            send_message(chat_id, msg)
        return
    
    if text.startswith('/adhar') or text.startswith('/aadhaar'):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, f"{E_CROSS()} <b>ᴘʀᴏᴠɪᴅᴇ ǫᴜᴇʀʏ!</b>\n\n{E_CHECK()} <b>ᴜꜱᴇ:</b> <code>/adhar 123456789012</code>")
            return
        query = parts[1].strip()
        if not re.match(r'^\d{12}$', query):
            send_message(chat_id, f"{E_CROSS()} <b>ɪɴᴠᴀʟɪᴅ ᴀᴀᴅʜᴀᴀʀ!</b>\n\nᴜꜱᴇ 12 ᴅɪɢɪᴛꜱ.\n\n{E_SHIELD()} <code>/adhar 123456789012</code>")
            return
        send_chat_action(chat_id, 'typing')
        premium_loading(chat_id, "ꜰᴇᴛᴄʜɪɴɢ ᴀᴀᴅʜᴀᴀʀ ᴅᴀᴛᴀ", style='shield')
        increment_stat('adhar_queries')
        increment_stat('total_queries')
        log_activity(user_id, 'AADHAAR_LOOKUP', query)
        response = http_get(AADHAAR_API_ENDPOINT.replace('{term}', query))
        msg, data = format_aadhaar_response(response, query)
        if data and show_txt:
            txt_content = generate_txt_content(f"🪪 AADHAAR LOOKUP RESULT", query, data, user)
            filename = f"aadhaar_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            send_document(chat_id, txt_content.encode('utf-8'), filename, txt_caption(query, user, EMOJI_SHIELD, "🪪"))
        else:
            send_message(chat_id, msg)
        return
    
    if text.startswith('/gmail') or text.startswith('/email'):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, f"{E_CROSS()} <b>ᴘʀᴏᴠɪᴅᴇ ǫᴜᴇʀʏ!</b>\n\n{E_CHECK()} <b>ᴜꜱᴇ:</b> <code>/gmail user@gmail.com</code>")
            return
        query = parts[1].strip().lower()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', query):
            send_message(chat_id, f"{E_CROSS()} <b>ɪɴᴠᴀʟɪᴅ ᴇᴍᴀɪʟ!</b>\n\n{E_BELL()} <code>/gmail user@gmail.com</code>")
            return
        send_chat_action(chat_id, 'typing')
        premium_loading(chat_id, "ꜰᴇᴛᴄʜɪɴɢ ᴇᴍᴀɪʟ ᴅᴀᴛᴀ", style='star')
        increment_stat('gmail_queries')
        increment_stat('total_queries')
        log_activity(user_id, 'EMAIL_LOOKUP', query)
        response = http_get(EMAIL_API_ENDPOINT.replace('{term}', query))
        msg, data = format_email_response(response, query)
        if data and show_txt:
            txt_content = generate_txt_content(f"📧 EMAIL LOOKUP RESULT", query, data, user)
            filename = f"email_{query.replace('@', '_at_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            send_document(chat_id, txt_content.encode('utf-8'), filename, txt_caption(query, user, EMOJI_BELL, "📧"))
        else:
            send_message(chat_id, msg)
        return
    
    if text.startswith('/pincode'):
        parts = text.split()
        if len(parts) < 2:
            send_message(chat_id, f"{E_CROSS()} <b>ᴘʀᴏᴠɪᴅᴇ ǫᴜᴇʀʏ!</b>\n\n{E_CHECK()} <b>ᴜꜱᴇ:</b> <code>/pincode 722134</code>")
            return
        query = parts[1].strip()
        if not re.match(r'^\d{6}$', query):
            send_message(chat_id, f"{E_CROSS()} <b>ɪɴᴠᴀʟɪᴅ ᴘɪɴᴄᴏᴅᴇ!</b>\n\nᴜꜱᴇ 6 ᴅɪɢɪᴛꜱ.\n\n{E_SHIELD()} <code>/pincode 722134</code>")
            return
        send_chat_action(chat_id, 'typing')
        premium_loading(chat_id, "ꜰᴇᴛᴄʜɪɴɢ ᴘɪɴᴄᴏᴅᴇ ᴅᴀᴛᴀ", style='rocket')
        increment_stat('pincode_queries')
        increment_stat('total_queries')
        log_activity(user_id, 'PINCODE_LOOKUP', query)
        response = http_get(PINCODE_API_ENDPOINT.replace('{term}', query))
        msg, data = format_pincode_response(response, query)
        if data and show_txt:
            txt_content = generate_pincode_txt(query, data.get('result', []), user)
            filename = f"pincode_{query}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            send_document(chat_id, txt_content.encode('utf-8'), filename, txt_caption(query, user, EMOJI_ROCKET, "📮"))
        else:
            send_message(chat_id, msg)
        return
    
    if text.startswith('/'):
        send_message(chat_id, (
            f"{E_CROSS()} <b>ᴜɴᴋɴᴏᴡɴ ᴄᴏᴍᴍᴀɴᴅ!</b>\n\n"
            f"{E_CHECK()} <b>ᴀᴠᴀɪʟᴀʙʟᴇ:</b>\n"
            f"{E_PHONE()} <code>/num &lt;10-digit&gt;</code>\n"
            f"{E_SHIELD()} <code>/adhar &lt;12-digit&gt;</code>\n"
            f"{E_BELL()} <code>/gmail &lt;email&gt;</code>\n"
            f"{E_SHIELD()} <code>/pincode &lt;6-digit&gt;</code>\n"
            f"{E_GEAR()} <code>/help</code>"
        ))

# ==================== MAIN ====================
def main():
    logger.info(f"{BOT_NAME} {BOT_VERSION} started. Polling...")
    set_bot_commands()
    if not os.path.exists(stats_file()):
        save_stats(dict(BOT_STATS))
    last_update_id = 0
    while True:
        try:
            response = requests.get(
                API_URL + 'getUpdates',
                params={'offset': last_update_id + 1, 'timeout': 30},
                timeout=35
            )
            if response.status_code == 200:
                data = response.json()
                if data.get('ok'):
                    for update in data.get('result', []):
                        last_update_id = update['update_id']
                        try:
                            handle_message(update)
                        except Exception as e:
                            logger.error(f"Error handling update {last_update_id}: {e}")
            time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()