# -*- coding: utf-8 -*-
import importlib.util
import errno
import os
import subprocess
import sys


def _bootstrap_dependencies():
    """Install the bot's own dependencies before importing them.

    This keeps a fresh Windows/RDP machine setup-free: Python and internet
    access are enough for the first launch.
    """
    required = {
        "telebot": "pyTelegramBotAPI",
        "flask": "Flask",
        "psutil": "psutil",
        "requests": "requests",
    }
    missing = [
        package for module, package in required.items()
        if importlib.util.find_spec(module) is None
    ]
    if not missing:
        return

    print(f"Installing missing packages automatically: {', '.join(missing)}",
          flush=True)
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        *missing,
    ]
    result = subprocess.run(command, check=False)

    # A normal Windows Python may not allow system-site installation. Retry
    # in the current user's package directory without requiring admin access.
    if result.returncode != 0 and os.name == "nt":
        print("Retrying package installation for the current Windows user...",
              flush=True)
        result = subprocess.run(
            [*command, "--user"],
            check=False,
        )

    if result.returncode != 0:
        raise RuntimeError(
            "Automatic dependency installation failed. "
            "Check that Python includes pip and the RDP has internet access."
        )


_bootstrap_dependencies()

import telebot

os.environ["PYTHONIOENCODING"] = "utf-8"

try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except:
    pass
    
import zipfile
import tempfile
import shutil
from telebot import types
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from datetime import datetime, timedelta
import psutil
import sqlite3
import json
import logging
import signal
import threading
import re
import shlex
import atexit
import requests
import hashlib
import mimetypes
import struct
from contextlib import contextmanager

# --- Flask Keep Alive ---
from flask import Flask
from threading import Thread

app = Flask('')

@app.route('/')
def home():
    return "bot is running...."

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask Keep-Alive server started.")
# --- End Flask Keep Alive ---

# --- Configuration ---
TOKEN = os.environ.get("8770718359:AAHDNjW_6Hj4L_f1vc8SHjn6cr9C7ANKMgg", "7714690977:AAGhab62zXWS4isKBX4VYUb-hMNNhnsjvkQ").strip()
if not TOKEN:
    raise RuntimeError("BOT_TOKEN is missing. Add it as a Replit Secret/environment variable.")
_owner_id_value = os.environ.get("OWNER_ID", "6084222195").strip()
try:
    OWNER_ID = int(_owner_id_value)
except ValueError as exc:
    raise RuntimeError("OWNER_ID must be a numeric Telegram user ID.") from exc
ADMIN_ID = OWNER_ID     # owner remains the default admin
YOUR_USERNAME = "@aku4x" #yeha tumhra username dala
UPDATE_CHANNEL = 'https://t.me/aku_era' #yeha chnl link dalo''
# Default kept for backward compatibility with the existing deployment.
# Admins can replace or disable it permanently with /setforce1.
FORCE_JOIN_CHANNELS = {
    "@aku_era": "@aku_era",
}
FORCE_JOIN_SLOT_KEYS = tuple(f"force_join_{index}" for index in range(1, 6))
DEFAULT_FORCE_JOIN_CHANNEL = "@aku_era"

# Folder setup - using absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_BOTS_DIR = os.path.join(BASE_DIR, 'upload_bots')
IROTECH_DIR = os.path.join(BASE_DIR, 'inf')
DATABASE_PATH = os.path.join(IROTECH_DIR, 'bot_data.db')
PENDING_DIR = os.path.join(IROTECH_DIR, 'pending_files')
# This is the only directory the automatic storage cleanup is allowed to
# delete from. Uploaded projects, logs, the database and pending approvals
# intentionally live outside this allowlisted cleanup root.
TEMP_DOWNLOAD_DIR = os.path.join(IROTECH_DIR, 'TEMP_DOWNLOADS')
TEMP_FILE_MAX_AGE_SECONDS = 60 * 60
STORAGE_CHECK_INTERVAL_SECONDS = 15 * 60

# Uploaded scripts install missing dependencies into a writable local folder.
# This works both on Replit and on a Windows RDP, where the system
# site-packages directory may be read-only.
PYTHON_PACKAGES_DIR = next(
    (
        path for path in sys.path
        if path.endswith('site-packages')
        and os.path.isdir(path)
        and os.access(path, os.W_OK)
    ),
    os.path.join(BASE_DIR, '.pythonlibs'),
)

# File upload limits
FREE_USER_LIMIT = 1
ADMIN_LIMIT = 500
OWNER_LIMIT = float('inf')

# Premium hosting plans with plan-specific validity
PREMIUM_PLANS = {
    'p100': {'name': '₹100 • 5 Files • 30 Days', 'price': 100, 'limit': 5, 'days': 30},
    'p200': {'name': '₹200 • 10 Files • 60 Days', 'price': 200, 'limit': 10, 'days': 60},
    'p500': {'name': '₹500 • 50 Files • 180 Days', 'price': 500, 'limit': 50, 'days': 180},
    'p1000': {'name': '₹1000 • Unlimited • 365 Days', 'price': 1000, 'limit': None, 'days': 365},
}

# Create necessary directories
os.makedirs(UPLOAD_BOTS_DIR, exist_ok=True)
os.makedirs(IROTECH_DIR, exist_ok=True)
os.makedirs(PENDING_DIR, exist_ok=True)
os.makedirs(TEMP_DOWNLOAD_DIR, exist_ok=True)
os.makedirs(PYTHON_PACKAGES_DIR, exist_ok=True)


def _python_runtime_env(script_path=None):
    """Return an isolated environment for uploaded Python scripts."""
    blocked_keys = {
        "BOT_TOKEN",
        "SESSION_SECRET",
        "ANIMEXXX_BOT_TOKEN",
        "ANIMEXXX_API_ID",
        "ANIMEXXX_API_HASH",
    }
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in blocked_keys
    }
    env["PYTHONIOENCODING"] = "utf-8"
    if script_path and os.path.basename(script_path).lower() == "animexxx.py":
        for key in ("ANIMEXXX_BOT_TOKEN", "ANIMEXXX_API_ID", "ANIMEXXX_API_HASH"):
            value = os.environ.get(key, "").strip()
            if value:
                env[key] = value
    pythonpath = [PYTHON_PACKAGES_DIR]
    if env.get("PYTHONPATH"):
        pythonpath.append(env["PYTHONPATH"])
    env["PYTHONPATH"] = os.pathsep.join(pythonpath)
    return env


def _pip_install_command(*arguments):
    """Build a pip command that works with Replit's pip-less runtime Python."""
    pip_executable = shutil.which("pip") or shutil.which("pip3")
    if not pip_executable:
        return None
    return [
        pip_executable,
        "install",
        "--disable-pip-version-check",
        "--upgrade",
        "--target",
        PYTHON_PACKAGES_DIR,
        *arguments,
    ]

# Initialize bot
bot = telebot.TeleBot(TOKEN)

# --- Data structures ---
bot_scripts = {}
user_subscriptions = {}
user_files = {}
user_profiles = {}
active_users = set()
admin_ids = {ADMIN_ID, OWNER_ID}
bot_locked = False
file_db = {}
file_callback_refs = {}
process_callback_refs = {}

# File Approval System
pending_files = {}
pending_payments = {}
pending_payment_sessions = {}
pending_pip_uninstalls = {}
PIP_OPERATION_LOCK = threading.Lock()
PIP_CONFIRM_LOCK = threading.Lock()
PIP_PACKAGE_PATTERN = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*"
    r"(?:\[[A-Za-z0-9][A-Za-z0-9._,-]*\])?"
    r"(?:(?:===|==|!=|~=|>=|<=|>|<)"
    r"[A-Za-z0-9][A-Za-z0-9._+*!-]*)?$"
)
PIP_OUTPUT_LIMIT = 12000
bot_settings = {
    # Keep the payment identifier plain text.  /set upi can still override it.
    'upi_id': os.environ.get('UPI_ID', 'rajanwins@ibl').strip(),
    'qr_file_id': None,
    'welcome_video_file_id': None,
}

banned_users = set()
banned_usernames = set()

# --- Malware Detection Configuration ---
MALWARE_SIGNATURES = [
    b'MZ',  # Windows executable
    b'\x7fELF',  # Linux executable
    b'\xfe\xed\xfa',  # Mach-O binary
    b'\xce\xfa\xed\xfe',  # Mach-O binary (reverse)
    b'PK',  # ZIP archive (could be encrypted)
    b'Rar!',  # RAR archive
]

ENCRYPTED_FILE_INDICATORS = [
    b'openssl',
    b'encrypted',
    b'cipher',
    b'DES',
    b'RSA',
    b'GPG',
    b'PGP',
]

SUSPICIOUS_KEYWORDS = [
    b'ransomware',
    b'trojan',
    b'virus',
    b'malware',
    b'backdoor',
    b'exploit',
    b'payload',
    b'botnet',
    b'keylogger',
    b'rootkit',
]

# --- Logging Setup ---
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
BOT_START_TIME = datetime.now()

# --- Command Button Layouts (ReplyKeyboardMarkup) ---
COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["🌷 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 𝐂𝐡𝐚𝐧ɴᴇʟ"],
    ["💎 𝐏ᴀɪᴅ 𝐏ᴀɴᴇʟ", "📤 𝐔ᴘʟᴏᴀᴅ Sᴄʀɪᴘᴛ"],
    ["📂 𝐌ʏ Fɪʟᴇs"],
    ["🟢 𝐑ᴜɴɴɪɴɢ Bᴏᴛs"],
    ["⚡ 𝐁ᴏᴛ Sᴛᴀᴛᴜs", "📊 𝐒ᴛᴀᴛɪsᴛɪᴄs"],
    ["💳 𝐒ᴜʙsᴄʀɪᴘᴛɪᴏɴs"],
    ["🛰 𝐒ᴇɴᴅ Cᴏᴍᴍᴀɴᴅ", "💌 𝐂ᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ"]
]
ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC = [
    ["🌷 𝐔𝐩ᴅᴀᴛᴇs Cʜᴀɴɴᴇʟ"],
    ["💎 𝐏ᴀɪᴅ 𝐏ᴀɴᴇʟ", "📤 𝐔ᴘʟᴏᴀᴅ Sᴄʀɪᴘᴛ"],
    ["📂 𝐌ʏ Fɪʟᴇs"],
    ["🟢 𝐑ᴜɴɴɪɴɢ Bᴏᴛs"],
    ["⚡ 𝐁ᴏᴛ Sᴛᴀᴛᴜs", "📊 𝐒ᴛᴀᴛɪsᴛɪᴄs"],
    ["💳 𝐒ᴜʙsᴄʀɪᴘᴛɪᴏɴs", "📢 𝐁ʀᴏᴀᴅᴄᴀsᴛ"],
    ["🔒 𝐋ᴏᴄᴋ Bᴏᴛ", "🟢 𝐑ᴜɴ Aʟʟ Sᴄʀɪᴘᴛs"],
    ["🛰 𝐒ᴇɴᴅ Cᴏᴍᴍᴀɴᴅ", "👑 𝐀ᴅᴍɪɴ Pᴀɴᴇʟ"],
    ["💌 𝐂ᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ"]
]

def _force_join_slots():
    """Return normalized force-join entries in stable slot order.

    Legacy values are plain @usernames. New values are JSON objects so a
    private invite URL, its membership-check chat ID, and its button label can
    be persisted together.
    """
    slots = []
    for index, key in enumerate(FORCE_JOIN_SLOT_KEYS, start=1):
        value = bot_settings.get(key)
        if value is None and index == 1:
            value = DEFAULT_FORCE_JOIN_CHANNEL
        value = str(value or "").strip()
        if not value or value.lower() == "off":
            continue

        config = None
        try:
            decoded = json.loads(value)
            if isinstance(decoded, dict):
                config = decoded
        except (TypeError, ValueError, json.JSONDecodeError):
            config = None

        if config is None:
            config = {"target": value}

        target = str(config.get("target") or "").strip()
        if not target or target.lower() == "off":
            continue
        is_private = target.startswith(("https://t.me/+", "http://t.me/+"))
        default_label = (
            "🔐 Join Private Channel"
            if is_private
            else f"📢 Join Channel {index}"
        )
        label = str(config.get("label") or default_label).strip()[:64]
        chat_id = config.get("chat_id")
        try:
            chat_id = int(chat_id) if chat_id is not None else None
        except (TypeError, ValueError):
            chat_id = None
        slots.append({
            "index": index,
            "target": target,
            "label": label,
            "chat_id": chat_id,
            "private": is_private,
        })
    return slots


def _refresh_force_join_channels():
    """Rebuild the runtime map from the values persisted in bot_settings."""
    FORCE_JOIN_CHANNELS.clear()
    for entry in _force_join_slots():
        FORCE_JOIN_CHANNELS[entry["target"]] = entry["label"]


def send_force_join_msg(chat_id):
    """Show the force-join prompt without silently dropping /start errors."""
    markup = types.InlineKeyboardMarkup(row_width=1)

    for entry in _force_join_slots():
        # Telegram URLs must not contain the leading @.
        target = entry["target"]
        join_url = (
            target
            if entry["private"]
            else f"https://t.me/{target.lstrip('@').strip()}"
        )
        markup.add(
            types.InlineKeyboardButton(
                text=entry["label"],
                url=join_url
            )
        )

    markup.add(
        types.InlineKeyboardButton(
            "✅ Check Again",
            callback_data="force_join_check"
        )
    )

    try:
        bot.send_message(
            chat_id,
                "𝐉𝐎𝐈𝐍 𝐀𝐋𝐋 𝐑𝐄𝐐𝐔𝐈𝐑𝐄𝐃 𝐂𝐇𝐀𝐍𝐍𝐄𝐋𝐒 𝐓𝐎 𝐔𝐒𝐄 𝐌𝐄 🤍🌙:\n\n"
                "Join every channel below, then tap Check Again.",
            reply_markup=markup
        )
    except Exception as e:
        # A malformed/blocked channel button should not make /start appear
        # unresponsive. Send a plain fallback so the user gets feedback.
        logger.error(f"Force-join prompt failed for {chat_id}: {e}", exc_info=True)
        channel_text = "\n".join(
            f"• {entry['label']}"
            for entry in _force_join_slots()
        ) or "• No force-join channel configured"
        try:
            bot.send_message(
                chat_id,
                "⚠️ Please join the required channel first:\n\n"
                f"{channel_text}\n\n"
                "After joining, send /start again.",
            )
        except Exception as fallback_error:
            logger.error(
                f"Force-join fallback also failed for {chat_id}: {fallback_error}",
                exc_info=True,
            )


def is_user_joined_all(user_id):
    """Return whether a user has joined every configured force-join channel.

    Telegram can return ``restricted`` for a member who is still subscribed
    to a channel.  The old check treated that status as not joined, which
    caused an endless /start -> join prompt loop for ordinary users.
    """
    if not FORCE_JOIN_CHANNELS:
        return True

    try:
        for entry in _force_join_slots():
            ch = entry["chat_id"] if entry["private"] else entry["target"]
            if entry["private"] and not entry["chat_id"]:
                logger.error(
                    "Private force-join slot %s has no chat ID; "
                    "configure it as /setforce%s -100... https://t.me/+... | Label",
                    entry["index"], entry["index"]
                )
                return False
            # Do not pass timeout here: pyTelegramBotAPI versions differ and
            # get_chat_member() in the supported versions accepts only the
            # chat ID and user ID.  Passing timeout made every verification
            # fail with "unexpected keyword argument 'timeout'".
            member = bot.get_chat_member(ch, user_id)

            if member.status in ('member', 'administrator', 'creator'):
                continue
            if member.status == 'restricted' and getattr(member, 'is_member', False):
                continue
            # A left/kicked user, and a restricted user who is no longer a
            # member, must join again.
            if member.status in ('left', 'kicked', 'restricted'):
                return False
            return False

        return True

    except Exception as e:
        logger.warning(
            "Force-join verification failed for user %s. "
            "Make sure the bot is an administrator in every configured "
            "channel and that the channel username is correct: %s",
            user_id, e
        )
        return False


def _force_join_guard(message):
    """Block non-admin messages until every enabled channel is joined."""
    user_id = getattr(getattr(message, "from_user", None), "id", None)
    if user_id in admin_ids or not _force_join_slots():
        return True
    if is_user_joined_all(user_id):
        return True
    send_force_join_msg(message.chat.id)
    return False

# --- Database Setup ---
def init_db():
    """Initialize the database with required tables"""
    logger.info(f"Initializing database at: {DATABASE_PATH}")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS subscriptions
                     (user_id INTEGER PRIMARY KEY, expiry TEXT, plan TEXT, price INTEGER,
                      activation_date TEXT, file_limit INTEGER,
                      status TEXT DEFAULT 'active', payment_status TEXT DEFAULT 'approved')''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_files
                     (user_id INTEGER, file_name TEXT, file_type TEXT,
                      PRIMARY KEY (user_id, file_name))''')
        c.execute('''CREATE TABLE IF NOT EXISTS active_users
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS admins
                     (user_id INTEGER PRIMARY KEY)''')
        c.execute('''CREATE TABLE IF NOT EXISTS user_profiles
                     (user_id INTEGER PRIMARY KEY, first_name TEXT, username TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS payment_requests
                     (request_id TEXT PRIMARY KEY, user_id INTEGER, user_name TEXT, plan TEXT,
                      price INTEGER, file_limit INTEGER, validity_days INTEGER,
                      screenshot_file_id TEXT, status TEXT DEFAULT 'pending',
                      payment_status TEXT DEFAULT 'pending', created_at TEXT, decided_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS payment_sessions
                     (user_id INTEGER PRIMARY KEY, plan TEXT, updated_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS pending_file_requests
                     (request_id TEXT PRIMARY KEY, user_id INTEGER, chat_id INTEGER, user_name TEXT, file_name TEXT, file_ext TEXT, file_size INTEGER, stored_path TEXT, status TEXT DEFAULT 'pending', created_at TEXT, decided_at TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS bot_settings
                     (key TEXT PRIMARY KEY, value TEXT)''')
        c.execute('''CREATE TABLE IF NOT EXISTS storage_cleanup_status
                     (id INTEGER PRIMARY KEY CHECK (id = 1),
                      last_cleanup_at TEXT,
                      files_cleaned INTEGER DEFAULT 0,
                      bytes_freed INTEGER DEFAULT 0)''')
        c.execute(
            'INSERT OR IGNORE INTO storage_cleanup_status '
            '(id, last_cleanup_at, files_cleaned, bytes_freed) VALUES (1, NULL, 0, 0)'
        )
        c.execute(
            'INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)',
            ('force_join_1', DEFAULT_FORCE_JOIN_CHANNEL)
        )
        # Backward-compatible schema migration for older subscriptions DBs.
        existing_cols = {row[1] for row in c.execute('PRAGMA table_info(subscriptions)').fetchall()}
        for col, definition in [
            ('plan', 'TEXT'), ('price', 'INTEGER'), ('activation_date', 'TEXT'),
            ('file_limit', 'INTEGER'), ('status', "TEXT DEFAULT 'active'"),
            ('payment_status', "TEXT DEFAULT 'approved'")
        ]:
            if col not in existing_cols:
                c.execute(f'ALTER TABLE subscriptions ADD COLUMN {col} {definition}')

        existing_payment_cols = {
            row[1] for row in c.execute('PRAGMA table_info(payment_requests)').fetchall()
        }
        for col, definition in [
            ('file_limit', 'INTEGER'), ('validity_days', 'INTEGER'),
            ('payment_status', "TEXT DEFAULT 'pending'")
        ]:
            if col not in existing_payment_cols:
                c.execute(f'ALTER TABLE payment_requests ADD COLUMN {col} {definition}')

        c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (OWNER_ID,))
        if ADMIN_ID != OWNER_ID:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (ADMIN_ID,))
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully.")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {e}", exc_info=True)

def load_data():
    """Load data from database into memory"""
    logger.info("Loading data from database...")
    try:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()

        # Load subscriptions
        c.execute(
            'SELECT user_id, expiry, plan, price, activation_date, file_limit, '
            'status, payment_status FROM subscriptions'
        )
        for user_id, expiry, plan, price, activation_date, file_limit, status, payment_status in c.fetchall():
            try:
                user_subscriptions[user_id] = {
                    'expiry': datetime.fromisoformat(expiry),
                    'plan': plan or 'legacy',
                    'price': price,
                    'activation_date': activation_date,
                    'file_limit': file_limit,
                    'status': status or 'active',
                    'payment_status': payment_status or 'approved',
                }
            except ValueError:
                logger.warning(f"⚠️ Invalid expiry date format for user {user_id}: {expiry}. Skipping.")

        # Load user files
        c.execute('SELECT user_id, file_name, file_type FROM user_files')
        for user_id, file_name, file_type in c.fetchall():
            if user_id not in user_files:
                user_files[user_id] = []
            user_files[user_id].append((file_name, file_type))

        # Load active users
        c.execute('SELECT user_id FROM active_users')
        active_users.update(user_id for (user_id,) in c.fetchall())

        # Load admins
        c.execute('SELECT user_id FROM admins')
        admin_ids.update(user_id for (user_id,) in c.fetchall())

        c.execute('SELECT key, value FROM bot_settings')
        for key, value in c.fetchall():
            bot_settings[key] = value

        c.execute("SELECT request_id, user_id, user_name, plan, price, screenshot_file_id, status, created_at FROM payment_requests WHERE status = 'pending'")
        for row in c.fetchall():
            rid, uid, uname, plan, price, screenshot_id, status, created_at = row
            pending_payments[rid] = {'user_id': uid, 'user_name': uname, 'plan': plan, 'price': price, 'screenshot_file_id': screenshot_id, 'status': status, 'created_at': created_at}

        c.execute('SELECT user_id, plan FROM payment_sessions')
        for user_id, plan in c.fetchall():
            if plan in PREMIUM_PLANS:
                pending_payment_sessions[user_id] = plan

        c.execute("SELECT request_id, user_id, chat_id, user_name, file_name, file_ext, file_size, stored_path, status, created_at FROM pending_file_requests WHERE status = 'pending'")
        for row in c.fetchall():
            rid, uid, cid, uname, fname, fext, fsize, stored_path, status, created_at = row
            if stored_path and os.path.exists(stored_path):
                try:
                    with open(stored_path, 'rb') as fh: content = fh.read()
                except Exception: content = None
            else: content = None
            pending_files[rid] = {'user_id': uid, 'chat_id': cid, 'file_name': fname, 'file_ext': fext, 'file_size': fsize, 'content': content, 'stored_path': stored_path, 'status': status, 'user_name': uname, 'created_at': created_at}

        c.execute('SELECT user_id, first_name, username FROM user_profiles')
        for user_id, first_name, username in c.fetchall():
            user_profiles[user_id] = {
                'first_name': first_name or 'Unknown',
                'username': username or ''
            }

        conn.close()
        logger.info(f"Data loaded: {len(active_users)} users, {len(user_subscriptions)} subscriptions, {len(admin_ids)} admins.")
    except Exception as e:
        logger.error(f"❌ Error loading data: {e}", exc_info=True)

# Initialize DB and Load Data at startup
init_db()
load_data()
_refresh_force_join_channels()
# --- End Database Setup ---

# --- Safe temporary storage management ---
_TEMP_PATH_LOCK = threading.RLock()
_ACTIVE_TEMP_PATHS = set()
_STORAGE_STATE_LOCK = threading.RLock()
_storage_cleanup_state = {
    "last_cleanup_at": None,
    "files_cleaned": 0,
    "bytes_freed": 0,
    "last_error": None,
}
_storage_warning_level = 0
_storage_warning_sent_at = 0.0


def _safe_temp_path(path):
    """Return True only for a real path below the dedicated temp root."""
    try:
        root = os.path.realpath(TEMP_DOWNLOAD_DIR)
        candidate = os.path.realpath(path)
        return (
            not os.path.islink(path)
            and os.path.commonpath((root, candidate)) == root
            and candidate != root
        )
    except (OSError, ValueError):
        return False


def _is_active_temp_path(path):
    try:
        candidate = os.path.realpath(path)
        with _TEMP_PATH_LOCK:
            for active in _ACTIVE_TEMP_PATHS:
                active_real = os.path.realpath(active)
                if candidate == active_real:
                    return True
                if os.path.commonpath((active_real, candidate)) == active_real:
                    return True
    except (OSError, ValueError):
        return True
    return False


def _mark_temp_path_active(path):
    if _safe_temp_path(path):
        with _TEMP_PATH_LOCK:
            _ACTIVE_TEMP_PATHS.add(path)


def _unmark_temp_path_active(path):
    with _TEMP_PATH_LOCK:
        _ACTIVE_TEMP_PATHS.discard(path)


def _create_temp_download_file(file_name, content):
    """Stage a downloaded file only inside the cleanup allowlist."""
    suffix = os.path.splitext(os.path.basename(file_name or ""))[1][:16]
    fd, path = tempfile.mkstemp(
        prefix="download_",
        suffix=suffix,
        dir=TEMP_DOWNLOAD_DIR,
    )
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
        _mark_temp_path_active(path)
        return path
    except Exception:
        try:
            os.close(fd)
        except OSError:
            pass
        try:
            if _safe_temp_path(path):
                os.remove(path)
        except OSError:
            pass
        raise


def _release_temp_download_file(path):
    if not path:
        return
    _unmark_temp_path_active(path)
    try:
        if _safe_temp_path(path) and os.path.isfile(path):
            os.remove(path)
    except OSError as exc:
        logger.warning("Could not remove staged download %s: %s", path, exc)


def _format_bytes(value):
    value = float(max(0, value))
    units = ("B", "KB", "MB", "GB", "TB")
    for unit in units:
        if value < 1024 or unit == units[-1]:
            return f"{value:.1f} {unit}" if unit != "B" else f"{int(value)} B"
        value /= 1024


def _disk_usage():
    usage = shutil.disk_usage(BASE_DIR)
    percent = (usage.used / usage.total * 100) if usage.total else 0.0
    return {
        "total": usage.total,
        "used": usage.used,
        "free": usage.free,
        "percent": percent,
    }


def _load_cleanup_state():
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            row = conn.execute(
                "SELECT last_cleanup_at, files_cleaned, bytes_freed "
                "FROM storage_cleanup_status WHERE id = 1"
            ).fetchone()
            conn.close()
        if row:
            with _STORAGE_STATE_LOCK:
                _storage_cleanup_state.update({
                    "last_cleanup_at": row[0],
                    "files_cleaned": int(row[1] or 0),
                    "bytes_freed": int(row[2] or 0),
                })
    except Exception as exc:
        logger.warning("Could not load cleanup status: %s", exc)


def _save_cleanup_state():
    with _STORAGE_STATE_LOCK:
        state = dict(_storage_cleanup_state)
    try:
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            conn.execute(
                "UPDATE storage_cleanup_status SET last_cleanup_at = ?, "
                "files_cleaned = ?, bytes_freed = ? WHERE id = 1",
                (state["last_cleanup_at"], state["files_cleaned"],
                 state["bytes_freed"]),
            )
            conn.commit()
            conn.close()
    except Exception as exc:
        logger.warning("Could not persist cleanup status: %s", exc)


def cleanup_temporary_downloads(max_age_seconds=TEMP_FILE_MAX_AGE_SECONDS):
    """Delete old files only inside TEMP_DOWNLOAD_DIR.

    This function never follows symlinks, never walks outside the allowlist,
    and skips paths currently registered by a download or ZIP extraction.
    """
    cutoff = time.time() - max(0, int(max_age_seconds))
    deleted_files = 0
    freed_bytes = 0
    errors = []
    root = os.path.realpath(TEMP_DOWNLOAD_DIR)

    try:
        os.makedirs(root, exist_ok=True)
        for current_root, dirs, files in os.walk(
            root, topdown=True, followlinks=False
        ):
            current_root_real = os.path.realpath(current_root)
            if current_root_real != root and not _safe_temp_path(current_root):
                dirs[:] = []
                continue
            dirs[:] = [
                name for name in dirs
                if not os.path.islink(os.path.join(current_root, name))
                and _safe_temp_path(os.path.join(current_root, name))
            ]
            for name in files:
                candidate = os.path.join(current_root, name)
                if not _safe_temp_path(candidate) or _is_active_temp_path(candidate):
                    continue
                try:
                    stat_result = os.stat(candidate, follow_symlinks=False)
                    if stat_result.st_mtime > cutoff:
                        continue
                    size = stat_result.st_size
                    os.remove(candidate)
                    deleted_files += 1
                    freed_bytes += size
                except FileNotFoundError:
                    continue
                except OSError as exc:
                    errors.append(f"{candidate}: {exc}")

        # Empty subdirectories are safe to remove, but keep the root itself.
        for current_root, dirs, _ in os.walk(
            root, topdown=False, followlinks=False
        ):
            for name in dirs:
                candidate = os.path.join(current_root, name)
                if _safe_temp_path(candidate) and not _is_active_temp_path(candidate):
                    try:
                        os.rmdir(candidate)
                    except OSError:
                        pass
    except Exception as exc:
        errors.append(str(exc))

    now = datetime.now().isoformat(timespec="seconds")
    with _STORAGE_STATE_LOCK:
        _storage_cleanup_state.update({
            "last_cleanup_at": now,
            "files_cleaned": deleted_files,
            "bytes_freed": freed_bytes,
            "last_error": "; ".join(errors[:3]) if errors else None,
        })
    _save_cleanup_state()
    if errors:
        logger.warning("Temporary cleanup completed with skipped paths: %s", errors[:3])
    else:
        logger.info(
            "Temporary cleanup completed: %d files, %s freed",
            deleted_files, _format_bytes(freed_bytes),
        )
    return {
        "files_cleaned": deleted_files,
        "bytes_freed": freed_bytes,
        "errors": errors,
    }


def _storage_warning_text(level, usage):
    if level >= 2:
        return (
            "🚨 CRITICAL STORAGE WARNING\n"
            f"💾 Disk usage: {usage['percent']:.1f}%\n"
            f"🟢 Free space: {_format_bytes(usage['free'])}\n"
            "🧹 Safe temporary cleanup was attempted. "
            "Uploaded projects and running bots were not touched."
        )
    return (
        "⚠️ STORAGE WARNING\n"
        f"📊 Disk usage: {usage['percent']:.1f}%\n"
        f"🟢 Free space: {_format_bytes(usage['free'])}\n"
        "Only the dedicated temporary/download folder is eligible for cleanup."
    )


def _send_storage_warning(level, usage, force=False):
    global _storage_warning_level, _storage_warning_sent_at
    now = time.time()
    if (
        not force
        and level == _storage_warning_level
        and now - _storage_warning_sent_at < 3600
    ):
        return
    _storage_warning_level = level
    _storage_warning_sent_at = now
    text = _storage_warning_text(level, usage)
    for admin_id in list(admin_ids):
        try:
            bot.send_message(admin_id, text)
        except Exception as exc:
            logger.warning("Could not send storage warning to %s: %s", admin_id, exc)


def _storage_check_once(notify=True):
    usage = _disk_usage()
    if usage["percent"] > 90:
        result = cleanup_temporary_downloads()
        usage = _disk_usage()
        if notify:
            _send_storage_warning(2, usage)
        return usage, result
    if usage["percent"] > 80:
        if notify:
            _send_storage_warning(1, usage)
        return usage, None
    global _storage_warning_level
    _storage_warning_level = 0
    return usage, None


def _storage_monitor_worker():
    while True:
        try:
            _, critical_cleanup = _storage_check_once(notify=True)
            if critical_cleanup is None:
                cleanup_temporary_downloads()
        except Exception as exc:
            # Storage monitoring must never take down polling or hosted bots.
            logger.error("Storage monitor error: %s", exc, exc_info=True)
        time.sleep(STORAGE_CHECK_INTERVAL_SECONDS)


def _is_no_space_error(exc):
    return (
        isinstance(exc, OSError) and getattr(exc, "errno", None) == errno.ENOSPC
    ) or "no space left on device" in str(exc).lower()


def _handle_no_space_error(context, chat_id=None):
    logger.error("No space left while %s", context, exc_info=True)
    cleanup_result = cleanup_temporary_downloads()
    usage = _disk_usage()
    warning = (
        "🚨 No space left on device\n"
        f"📍 During: {context}\n"
        f"🧹 Safe cleanup freed {_format_bytes(cleanup_result['bytes_freed'])} "
        f"from {cleanup_result['files_cleaned']} temporary files.\n"
        f"🟢 Current free space: {_format_bytes(usage['free'])}"
    )
    if usage["free"] < 10 * 1024 * 1024:
        warning += (
            "\n❗ Space is still critically low. Stop new uploads and free "
            "disk space manually; hosted project files were not deleted."
        )
    for admin_id in list(admin_ids):
        try:
            bot.send_message(admin_id, warning)
        except Exception as send_exc:
            logger.warning("Could not notify admin about ENOSPC: %s", send_exc)
    if chat_id is not None:
        try:
            bot.send_message(chat_id, warning)
        except Exception:
            pass
    return cleanup_result, usage


def _cleanup_status_text():
    usage = _disk_usage()
    with _STORAGE_STATE_LOCK:
        state = dict(_storage_cleanup_state)
    last = state["last_cleanup_at"] or "Not run since startup"
    next_run = datetime.now() + timedelta(seconds=STORAGE_CHECK_INTERVAL_SECONDS)
    return (
        "🧹 Cleanup Status\n\n"
        f"🕒 Last cleanup: {last}\n"
        f"📁 Files cleaned: {state['files_cleaned']}\n"
        f"💾 Space freed: {_format_bytes(state['bytes_freed'])}\n"
        f"🟢 Current free space: {_format_bytes(usage['free'])}\n"
        f"⏱️ Next automatic cleanup: {next_run:%Y-%m-%d %H:%M:%S}\n"
        f"📂 Scope: {TEMP_DOWNLOAD_DIR}"
    )


# --- Malware Detection Functions ---
# Replace the magic import and is_suspicious_file function

def get_file_type(file_content):
    """Determine file type using magic numbers and mimetypes"""
    # Common file signatures
    signatures = {
        b'\x7fELF': 'application/x-executable',
        b'MZ': 'application/x-dosexec',
        b'\xfe\xed\xfa': 'application/x-mach-binary',
        b'\xce\xfa\xed\xfe': 'application/x-mach-binary',
        b'PK': 'application/zip',
        b'Rar!': 'application/x-rar',
    }
    
    for signature, mime_type in signatures.items():
        if file_content.startswith(signature):
            return mime_type
    
    # Fallback to extension-based detection or return unknown
    return 'application/octet-stream'

def is_suspicious_file(file_content, file_name):
    """
    Check if file contains malware signatures, encrypted content, or suspicious keywords.
    Returns (is_suspicious, reason)
    """
    file_lower = file_name.lower()
    
    # Check file extensions first (same as before)
    suspicious_extensions = ['.exe', '.dll', '.bat', '.cmd', '.scr', '.com', '.pif', '.application', '.gadget',
                            '.msi', '.msp', '.com', '.scr', '.hta', '.cpl', '.msc', '.jar', '.bin', '.deb', '.rpm',
                            '.apk', '.app', '.dmg', '.iso', '.img']
    
    if any(file_lower.endswith(ext) for ext in suspicious_extensions):
        return True, f"Suspicious file extension: {file_name}"
    
    # Check for malware signatures in file content
    for signature in MALWARE_SIGNATURES:
        if file_content.startswith(signature):
            return True, f"Malware signature detected: {signature}"
    
    # Check for encrypted file indicators
    sample_size = min(len(file_content), 4096)
    file_sample = file_content[:sample_size]
    
    for indicator in ENCRYPTED_FILE_INDICATORS:
        if indicator in file_sample:
            return True, f"Encrypted file indicator: {indicator.decode('utf-8', errors='ignore')}"
    
    # Check for suspicious keywords in first 8KB
    sample_text = file_sample.decode('utf-8', errors='ignore').lower()
    for keyword in SUSPICIOUS_KEYWORDS:
        if keyword.decode('utf-8').lower() in sample_text:
            return True, f"Suspicious keyword found: {keyword.decode('utf-8')}"
    
    # Check file type using our custom function instead of magic
    try:
        file_type = get_file_type(file_sample)
        if file_type in ['application/x-dosexec', 'application/x-executable', 'application/x-mach-binary']:
            return True, f"Executable file type detected: {file_type}"
    except Exception as e:
        logger.warning(f"Could not determine file type: {e}")
    
    return False, "File appears safe"

def scan_file_for_malware(file_content, file_name, user_id):
    """
    Comprehensive malware scan for uploaded files.
    Only owner can bypass these checks.
    """
    if user_id == OWNER_ID:
        return True, "Owner bypassed security check"
    
    is_suspicious, reason = is_suspicious_file(file_content, file_name)
    
    if is_suspicious:
        logger.warning(f"🚨 Malware detected in {file_name} from user {user_id}: {reason}")
        return False, f"Security violation: {reason}"
    
    return True, "File passed security check"

# --- Helper Functions ---
def get_user_folder(user_id):
    """Get or create user's folder for storing files"""
    user_folder = os.path.join(UPLOAD_BOTS_DIR, str(user_id))
    os.makedirs(user_folder, exist_ok=True)
    return user_folder


def _safe_uploaded_file_name(file_name):
    """Reject path traversal while preserving normal Telegram file names."""
    raw_name = str(file_name or "").strip()
    normalized = raw_name.replace("\\", "/")
    safe_name = os.path.basename(normalized)
    if (
        not safe_name
        or safe_name in {".", ".."}
        or safe_name != normalized
        or os.path.isabs(raw_name)
    ):
        return None
    return safe_name

def expire_subscription_if_needed(user_id):
    sub = user_subscriptions.get(user_id)
    if sub and sub.get('expiry') and sub['expiry'] <= datetime.now():
        remove_subscription_db(user_id)
        return True
    return False

def subscription_expiry_worker():
    """Keep expired plans out of the active in-memory and DB state."""
    while True:
        try:
            for user_id in list(user_subscriptions):
                expire_subscription_if_needed(user_id)
        except Exception as e:
            logger.error(f"Subscription expiry worker error: {e}", exc_info=True)
        time.sleep(60)

def get_user_file_limit(user_id):
    """Get the active hosting limit; expired premium automatically falls back to free."""
    if user_id == OWNER_ID: return OWNER_LIMIT
    if user_id in admin_ids: return ADMIN_LIMIT
    expire_subscription_if_needed(user_id)
    if user_id in user_subscriptions:
        limit = user_subscriptions[user_id].get('file_limit')
        return int(limit) if limit is not None else float('inf')
    return FREE_USER_LIMIT

def get_user_file_count(user_id):
    """Get the number of files uploaded by a user"""
    return len(user_files.get(user_id, []))

def get_user_pending_file_count(user_id):
    return sum(1 for item in pending_files.values() if item.get('user_id') == user_id and item.get('status', 'pending') == 'pending')

def is_bot_running(script_owner_id, file_name):
    """Check if a bot script is currently running for a specific user"""
    script_key = f"{script_owner_id}_{file_name}"
    script_info = bot_scripts.get(script_key)
    if script_info and script_info.get('process'):
        try:
            proc = psutil.Process(script_info['process'].pid)
            is_running = proc.is_running() and proc.status() != psutil.STATUS_ZOMBIE
            if not is_running:
                logger.warning(f"Process {script_info['process'].pid} for {script_key} found in memory but not running/zombie. Cleaning up.")
                if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                    try:
                        script_info['log_file'].close()
                    except Exception as log_e:
                        logger.error(f"Error closing log file during zombie cleanup {script_key}: {log_e}")
                if script_key in bot_scripts:
                    del bot_scripts[script_key]
            return is_running
        except psutil.NoSuchProcess:
            logger.warning(f"Process for {script_key} not found (NoSuchProcess). Cleaning up.")
            if 'log_file' in script_info and hasattr(script_info['log_file'], 'close') and not script_info['log_file'].closed:
                try:
                    script_info['log_file'].close()
                except Exception as log_e:
                    logger.error(f"Error closing log file during cleanup of non-existent process {script_key}: {log_e}")
            if script_key in bot_scripts:
                del bot_scripts[script_key]
            return False
        except Exception as e:
            logger.error(f"Error checking process status for {script_key}: {e}", exc_info=True)
            return False
    return False

def kill_process_tree(process_info):
    """Kill a process and all its children, ensuring log file is closed."""
    pid = None
    log_file_closed = False
    script_key = process_info.get('script_key', 'N/A')

    try:
        if 'log_file' in process_info and hasattr(process_info['log_file'], 'close') and not process_info['log_file'].closed:
            try:
                process_info['log_file'].close()
                log_file_closed = True
                logger.info(f"Closed log file for {script_key} (PID: {process_info.get('process', {}).get('pid', 'N/A')})")
            except Exception as log_e:
                logger.error(f"Error closing log file during kill for {script_key}: {log_e}")

        process = process_info.get('process')
        if process and hasattr(process, 'pid'):
            pid = process.pid
            if pid:
                try:
                    parent = psutil.Process(pid)
                    children = parent.children(recursive=True)
                    logger.info(f"Attempting to kill process tree for {script_key} (PID: {pid}, Children: {[c.pid for c in children]})")

                    for child in children:
                        try:
                            child.terminate()
                            logger.info(f"Terminated child process {child.pid} for {script_key}")
                        except psutil.NoSuchProcess:
                            logger.warning(f"Child process {child.pid} for {script_key} already gone.")
                        except Exception as e:
                            logger.error(f"Error terminating child {child.pid} for {script_key}: {e}. Trying kill...")
                            try:
                                child.kill()
                                logger.info(f"Killed child process {child.pid} for {script_key}")
                            except Exception as e2:
                                logger.error(f"Failed to kill child {child.pid} for {script_key}: {e2}")

                    gone, alive = psutil.wait_procs(children, timeout=1)
                    for p in alive:
                        logger.warning(f"Child process {p.pid} for {script_key} still alive. Killing.")
                        try:
                            p.kill()
                        except Exception as e:
                            logger.error(f"Failed to kill child {p.pid} for {script_key} after wait: {e}")

                    try:
                        parent.terminate()
                        logger.info(f"Terminated parent process {pid} for {script_key}")
                        try:
                            parent.wait(timeout=1)
                        except psutil.TimeoutExpired:
                            logger.warning(f"Parent process {pid} for {script_key} did not terminate. Killing.")
                            parent.kill()
                            logger.info(f"Killed parent process {pid} for {script_key}")
                    except psutil.NoSuchProcess:
                        logger.warning(f"Parent process {pid} for {script_key} already gone.")
                    except Exception as e:
                        logger.error(f"Error terminating parent {pid} for {script_key}: {e}. Trying kill...")
                        try:
                            parent.kill()
                            logger.info(f"Killed parent process {pid} for {script_key}")
                        except Exception as e2:
                            logger.error(f"Failed to kill parent {pid} for {script_key}: {e2}")

                except psutil.NoSuchProcess:
                    logger.warning(f"Process {pid or 'N/A'} for {script_key} not found during kill. Already terminated?")
            else:
                logger.error(f"Process PID is None for {script_key}.")
        elif log_file_closed:
            logger.warning(f"Process object missing for {script_key}, but log file closed.")
        else:
            logger.error(f"Process object missing for {script_key}, and no log file. Cannot kill.")
    except Exception as e:
        logger.error(f"❌ Unexpected error killing process tree for PID {pid or 'N/A'} ({script_key}): {e}", exc_info=True)

# --- Automatic Package Installation & Script Running ---

def attempt_install_pip(module_name, message):

    package_name = TELEGRAM_MODULES.get(
        module_name.lower(),
        module_name
    )

    # PIL fix
    if module_name.lower() == "pil":
        package_name = "pillow"

    if package_name is None:
        logger.info(
            f"Module '{module_name}' is core. Skipping pip install."
        )
        return False

    try:

        bot.reply_to(
            message,
            f"🐍 Module `{module_name}` not found. Installing `{package_name}`...",
            parse_mode='Markdown'
        )

        command = _pip_install_command(package_name)
        if command is None:
            error_msg = (
                f"❌ Could not install `{package_name}` because pip is not "
                "available in the runtime."
            )
            logger.error(error_msg)
            bot.reply_to(message, error_msg)
            return False

        logger.info(f"Running install: {' '.join(command)}")

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            encoding='utf-8',
            errors='replace',
            env=_python_runtime_env()
        )

        if result.returncode == 0:

            logger.info(
                f"Installed {package_name}. Output:\n{result.stdout}"
            )

            bot.reply_to(
                message,
                f"✅ Package `{package_name}` (for `{module_name}`) installed.",
                parse_mode='Markdown'
            )

            return True

        else:

            error_msg = (
                f"❌ Failed to install `{package_name}` "
                f"for `{module_name}`.\n"
                f"Log:\n```\n"
                f"{result.stderr or result.stdout}\n```"
            )

            logger.error(error_msg)

            if len(error_msg) > 4000:
                error_msg = (
                    error_msg[:4000] +
                    "\n... (Log truncated)"
                )

            bot.reply_to(
                message,
                error_msg,
                parse_mode='Markdown'
            )

            return False

    except Exception as e:

        error_msg = (
            f"❌ Error installing `{package_name}`: {str(e)}"
        )

        logger.error(error_msg, exc_info=True)

        bot.reply_to(message, error_msg)

        return False

def attempt_install_npm(module_name, user_folder, message):

    try:

        bot.reply_to(
            message,
            f"🟠 Node package `{module_name}` not found. Installing locally...",
            parse_mode='Markdown'
        )

        command = [
            'npm',
            'install',
            module_name
        ]

        logger.info(
            f"Running npm install: {' '.join(command)} in {user_folder}"
        )

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            cwd=user_folder,
            encoding='utf-8',
            errors='replace'
        )

        if result.returncode == 0:

            logger.info(
                f"Installed {module_name}. Output:\n{result.stdout}"
            )

            bot.reply_to(
                message,
                f"✅ Node package `{module_name}` installed locally.",
                parse_mode='Markdown'
            )

            return True

        else:

            error_msg = (
                f"❌ Failed to install Node package `{module_name}`.\n"
                f"Log:\n```\n"
                f"{result.stderr or result.stdout}\n```"
            )

            logger.error(error_msg)

            if len(error_msg) > 4000:
                error_msg = (
                    error_msg[:4000] +
                    "\n... (Log truncated)"
                )

            bot.reply_to(
                message,
                error_msg,
                parse_mode='Markdown'
            )

            return False

    except FileNotFoundError:

        error_msg = (
            "❌ Error: 'npm' not found. "
            "Ensure Node.js/npm are installed and in PATH."
        )

        logger.error(error_msg)

        bot.reply_to(message, error_msg)

        return False

    except Exception as e:

        error_msg = (
            f"❌ Error installing Node package "
            f"`{module_name}`: {str(e)}"
        )

        logger.error(error_msg, exc_info=True)

        bot.reply_to(message, error_msg)

        return False

def run_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    """Run Python script safely with UTF-8 support"""

    max_attempts = 2

    if attempt > max_attempts:
        bot.reply_to(
            message_obj_for_reply,
            f"❌ Failed to run '{file_name}' after {max_attempts} attempts."
        )
        return

    script_key = f"{script_owner_id}_{file_name}"

    logger.info(
        f"Attempt {attempt} to run Python script: "
        f"{script_path} (Key: {script_key})"
    )

    try:
        # ================= FILE EXISTS CHECK =================

        if not os.path.exists(script_path):

            bot.reply_to(
                message_obj_for_reply,
                f"❌ Script '{file_name}' not found!"
            )

            logger.error(f"Script not found: {script_path}")

            if script_owner_id in user_files:
                user_files[script_owner_id] = [
                    f for f in user_files.get(script_owner_id, [])
                    if f[0] != file_name
                ]

            remove_user_file_db(script_owner_id, file_name)
            return

        # ================= PRE CHECK =================

        if attempt == 1:

            check_command = [sys.executable, script_path]

            logger.info(
                f"Running Python pre-check: {' '.join(check_command)}"
            )

            check_proc = None

            try:

                check_proc = subprocess.Popen(
                    check_command,
                    cwd=user_folder,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    env=_python_runtime_env(script_path)
                )

                stdout, stderr = check_proc.communicate(timeout=5)

                return_code = check_proc.returncode

                logger.info(
                    f"Python Pre-check RC: {return_code} | "
                    f"STDERR: {stderr[:200]}"
                )

                # ================= MODULE CHECK =================

                if return_code != 0 and stderr:

                    match_py = re.search(
                        r"ModuleNotFoundError: No module named '(.+?)'",
                        stderr
                    )

                    if match_py:

                        module_name = match_py.group(1).strip()

                        logger.info(
                            f"Detected missing Python module: {module_name}"
                        )

                        if attempt_install_pip(
                            module_name,
                            message_obj_for_reply
                        ):

                            bot.reply_to(
                                message_obj_for_reply,
                                f"🔄 Retrying '{file_name}'..."
                            )

                            time.sleep(2)

                            threading.Thread(
                                target=run_script,
                                args=(
                                    script_path,
                                    script_owner_id,
                                    user_folder,
                                    file_name,
                                    message_obj_for_reply,
                                    attempt + 1
                                )
                            ).start()

                            return

                        else:

                            bot.reply_to(
                                message_obj_for_reply,
                                f"❌ Install failed for '{module_name}'"
                            )

                            return

                    else:

                        error_summary = stderr[:500]

                        bot.reply_to(
                            message_obj_for_reply,
                            f"❌ Error in script pre-check:\n```{error_summary}```",
                            parse_mode='Markdown'
                        )

                        return

            except subprocess.TimeoutExpired:

                logger.info(
                    "Pre-check timeout -> imports likely OK"
                )

                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()

            except FileNotFoundError:

                logger.error(
                    f"Python interpreter not found: {sys.executable}"
                )

                bot.reply_to(
                    message_obj_for_reply,
                    f"❌ Python interpreter not found."
                )

                return

            except Exception as e:

                logger.error(
                    f"Pre-check error: {e}",
                    exc_info=True
                )

                bot.reply_to(
                    message_obj_for_reply,
                    f"❌ Pre-check error:\n{e}"
                )

                return

            finally:

                if check_proc and check_proc.poll() is None:

                    logger.warning(
                        f"Killing stuck pre-check process {check_proc.pid}"
                    )

                    check_proc.kill()
                    check_proc.communicate()

        # ================= START LONG RUN =================

        logger.info(
            f"Starting long-running Python process for {script_key}"
        )

        log_file_path = os.path.join(
            user_folder,
            f"{os.path.splitext(file_name)[0]}.log"
        )

        log_file = None
        process = None

        try:

            log_file = open(
                log_file_path,
                'w',
                encoding='utf-8',
                errors='replace'
            )

        except Exception as e:

            logger.error(
                f"Failed to open log file: {e}",
                exc_info=True
            )

            bot.reply_to(
                message_obj_for_reply,
                f"❌ Failed to open log file:\n{e}"
            )

            return

        try:

            startupinfo = None
            creationflags = 0

            if os.name == 'nt':

                startupinfo = subprocess.STARTUPINFO()

                startupinfo.dwFlags |= (
                    subprocess.STARTF_USESHOWWINDOW
                )

                startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                [sys.executable, script_path],

                cwd=user_folder,

                stdout=log_file,
                stderr=log_file,

                stdin=subprocess.PIPE,

                startupinfo=startupinfo,
                creationflags=creationflags,

                text=True,

                encoding='utf-8',
                errors='replace',

                env=_python_runtime_env(script_path)
            )

            logger.info(
                f"Started Python process {process.pid} "
                f"for {script_key}"
            )

            bot_scripts[script_key] = {
                'process': process,
                'log_file': log_file,
                'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id,
                'script_owner_id': script_owner_id,
                'start_time': datetime.now(),
                'user_folder': user_folder,
                'type': 'py',
                'script_key': script_key
            }

            bot.reply_to(
                message_obj_for_reply,
                f"✅ Python script '{file_name}' started!\n"
                f"🆔 PID: {process.pid}"
            )

        except FileNotFoundError:

            logger.error(
                f"Python interpreter not found for long run"
            )

            bot.reply_to(
                message_obj_for_reply,
                "❌ Python interpreter not found."
            )

            if log_file and not log_file.closed:
                log_file.close()

            if script_key in bot_scripts:
                del bot_scripts[script_key]

        except Exception as e:

            if log_file and not log_file.closed:
                log_file.close()

            logger.error(
                f"Error starting script: {e}",
                exc_info=True
            )

            bot.reply_to(
                message_obj_for_reply,
                f"❌ Failed to start script:\n{e}"
            )

            if process and process.poll() is None:

                kill_process_tree({
                    'process': process,
                    'log_file': log_file,
                    'script_key': script_key
                })

            if script_key in bot_scripts:
                del bot_scripts[script_key]

    except Exception as e:

        logger.error(
            f"Unexpected run_script error: {e}",
            exc_info=True
        )

        if _is_no_space_error(e):
            chat = getattr(message_obj_for_reply, "chat", None)
            _handle_no_space_error(
                f"running Python script {file_name}",
                getattr(chat, "id", None),
            )

        bot.reply_to(
            message_obj_for_reply,
            f"❌ Unexpected error:\n{e}"
        )

        if script_key in bot_scripts:

            kill_process_tree(
                bot_scripts[script_key]
            )

            del bot_scripts[script_key]

def run_js_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply, attempt=1):
    """Run JS script safely with UTF-8 support"""

    max_attempts = 2

    if attempt > max_attempts:
        bot.reply_to(
            message_obj_for_reply,
            f"❌ Failed to run '{file_name}' after {max_attempts} attempts."
        )
        return

    script_key = f"{script_owner_id}_{file_name}"

    logger.info(
        f"Attempt {attempt} to run JS script: "
        f"{script_path} (Key: {script_key})"
    )

    try:

        # ================= FILE EXISTS CHECK =================

        if not os.path.exists(script_path):

            bot.reply_to(
                message_obj_for_reply,
                f"❌ Script '{file_name}' not found!"
            )

            logger.error(f"JS Script not found: {script_path}")

            if script_owner_id in user_files:
                user_files[script_owner_id] = [
                    f for f in user_files.get(script_owner_id, [])
                    if f[0] != file_name
                ]

            remove_user_file_db(script_owner_id, file_name)

            return

        # ================= PRE CHECK =================

        if attempt == 1:

            check_command = ['node', script_path]

            logger.info(
                f"Running JS pre-check: {' '.join(check_command)}"
            )

            check_proc = None

            try:

                check_proc = subprocess.Popen(
                    check_command,
                    cwd=user_folder,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    encoding='utf-8',
                    errors='replace',
                    env=_python_runtime_env()
                )

                stdout, stderr = check_proc.communicate(timeout=5)

                return_code = check_proc.returncode

                logger.info(
                    f"JS Pre-check RC: {return_code} | "
                    f"STDERR: {stderr[:200]}"
                )

                # ================= MODULE CHECK =================

                if return_code != 0 and stderr:

                    match_js = re.search(
                        r"Cannot find module '(.+?)'",
                        stderr
                    )

                    if match_js:

                        module_name = match_js.group(1).strip()

                        # Skip relative paths
                        if not module_name.startswith('.') and not module_name.startswith('/'):

                            logger.info(
                                f"Detected missing Node module: {module_name}"
                            )

                            if attempt_install_npm(
                                module_name,
                                user_folder,
                                message_obj_for_reply
                            ):

                                bot.reply_to(
                                    message_obj_for_reply,
                                    f"🔄 Retrying '{file_name}'..."
                                )

                                time.sleep(2)

                                threading.Thread(
                                    target=run_js_script,
                                    args=(
                                        script_path,
                                        script_owner_id,
                                        user_folder,
                                        file_name,
                                        message_obj_for_reply,
                                        attempt + 1
                                    )
                                ).start()

                                return

                            else:

                                bot.reply_to(
                                    message_obj_for_reply,
                                    f"❌ Failed to install '{module_name}'"
                                )

                                return

                    error_summary = stderr[:500]

                    bot.reply_to(
                        message_obj_for_reply,
                        f"❌ JS Script Error:\n```{error_summary}```",
                        parse_mode='Markdown'
                    )

                    return

            except subprocess.TimeoutExpired:

                logger.info(
                    "JS Pre-check timeout -> imports likely OK"
                )

                if check_proc and check_proc.poll() is None:
                    check_proc.kill()
                    check_proc.communicate()

            except FileNotFoundError:

                logger.error("Node.js not found")

                bot.reply_to(
                    message_obj_for_reply,
                    "❌ Node.js not installed."
                )

                return

            except Exception as e:

                logger.error(
                    f"JS pre-check error: {e}",
                    exc_info=True
                )

                bot.reply_to(
                    message_obj_for_reply,
                    f"❌ JS pre-check error:\n{e}"
                )

                return

            finally:

                if check_proc and check_proc.poll() is None:

                    logger.warning(
                        f"Killing stuck JS check process {check_proc.pid}"
                    )

                    check_proc.kill()
                    check_proc.communicate()

        # ================= START LONG RUN =================

        logger.info(
            f"Starting long-running JS process for {script_key}"
        )

        log_file_path = os.path.join(
            user_folder,
            f"{os.path.splitext(file_name)[0]}.log"
        )

        log_file = None
        process = None

        try:

            log_file = open(
                log_file_path,
                'w',
                encoding='utf-8',
                errors='replace'
            )

        except Exception as e:

            logger.error(
                f"Failed to open JS log file: {e}",
                exc_info=True
            )

            bot.reply_to(
                message_obj_for_reply,
                f"❌ Failed to open log file:\n{e}"
            )

            return

        try:

            startupinfo = None
            creationflags = 0

            if os.name == 'nt':

                startupinfo = subprocess.STARTUPINFO()

                startupinfo.dwFlags |= (
                    subprocess.STARTF_USESHOWWINDOW
                )

                startupinfo.wShowWindow = subprocess.SW_HIDE

            process = subprocess.Popen(
                ['node', script_path],

                cwd=user_folder,

                stdout=log_file,
                stderr=log_file,

                stdin=subprocess.PIPE,

                startupinfo=startupinfo,
                creationflags=creationflags,

                text=True,

                encoding='utf-8',
                errors='replace',

                env=_python_runtime_env()
            )

            logger.info(
                f"Started JS process {process.pid} "
                f"for {script_key}"
            )

            bot_scripts[script_key] = {
                'process': process,
                'log_file': log_file,
                'file_name': file_name,
                'chat_id': message_obj_for_reply.chat.id,
                'script_owner_id': script_owner_id,
                'start_time': datetime.now(),
                'user_folder': user_folder,
                'type': 'js',
                'script_key': script_key
            }

            bot.reply_to(
                message_obj_for_reply,
                f"✅ JS script '{file_name}' started!\n"
                f"🆔 PID: {process.pid}"
            )

        except FileNotFoundError:

            logger.error("Node.js not found for long run")

            bot.reply_to(
                message_obj_for_reply,
                "❌ Node.js not installed."
            )

            if log_file and not log_file.closed:
                log_file.close()

            if script_key in bot_scripts:
                del bot_scripts[script_key]

        except Exception as e:

            if log_file and not log_file.closed:
                log_file.close()

            logger.error(
                f"Error starting JS script: {e}",
                exc_info=True
            )

            bot.reply_to(
                message_obj_for_reply,
                f"❌ Failed to start JS script:\n{e}"
            )

            if process and process.poll() is None:

                kill_process_tree({
                    'process': process,
                    'log_file': log_file,
                    'script_key': script_key
                })

            if script_key in bot_scripts:
                del bot_scripts[script_key]

    except Exception as e:

        logger.error(
            f"Unexpected run_js_script error: {e}",
            exc_info=True
        )

        if _is_no_space_error(e):
            chat = getattr(message_obj_for_reply, "chat", None)
            _handle_no_space_error(
                f"running JavaScript script {file_name}",
                getattr(chat, "id", None),
            )

        bot.reply_to(
            message_obj_for_reply,
            f"❌ Unexpected JS error:\n{e}"
        )

        if script_key in bot_scripts:

            kill_process_tree(
                bot_scripts[script_key]
            )

            del bot_scripts[script_key]

# --- Map Telegram import names to actual PyPI package names ---
TELEGRAM_MODULES = {
    'telebot': 'pyTelegramBotAPI',
    'telegram': 'python-telegram-bot',
    'python_telegram_bot': 'python-telegram-bot',
    'aiogram': 'aiogram',
    'pyrogram': 'pyrogram',
    'telethon': 'telethon',
    'telethon.sync': 'telethon',
    'from telethon.sync import telegramclient': 'telethon',
    'telepot': 'telepot',
    'pytg': 'pytg',
    'tgcrypto': 'tgcrypto',
    'telegram_upload': 'telegram-upload',
    'telegram_send': 'telegram-send',
    'telegram_text': 'telegram-text',
    'mtproto': 'telegram-mtproto',
    'tl': 'telethon',
    'telegram_utils': 'telegram-utils',
    'telegram_logger': 'telegram-logger',
    'telegram_handlers': 'python-telegram-handlers',
    'telegram_redis': 'telegram-redis',
    'telegram_sqlalchemy': 'telegram-sqlalchemy',
    'telegram_payment': 'telegram-payment',
    'telegram_shop': 'telegram-shop-sdk',
    'pytest_telegram': 'pytest-telegram',
    'telegram_debug': 'telegram-debug',
    'telegram_scraper': 'telegram-scraper',
    'telegram_analytics': 'telegram-analytics',
    'telegram_nlp': 'telegram-nlp-toolkit',
    'telegram_ai': 'telegram-ai',
    'telegram_api': 'telegram-api-client',
    'telegram_web': 'telegram-web-integration',
    'telegram_games': 'telegram-games',
    'telegram_quiz': 'telegram-quiz-bot',
    'telegram_ffmpeg': 'telegram-ffmpeg',
    'telegram_media': 'telegram-media-utils',
    'telegram_2fa': 'telegram-twofa',
    'telegram_crypto': 'telegram-crypto-bot',
    'telegram_i18n': 'telegram-i18n',
    'telegram_translate': 'telegram-translate',
    'bs4': 'beautifulsoup4',
    'requests': 'requests',
    'pillow': 'Pillow',
    'cv2': 'opencv-python',
    'yaml': 'PyYAML',
    'dotenv': 'python-dotenv',
    'dateutil': 'python-dateutil',
    'pandas': 'pandas',
    'numpy': 'numpy',
    'flask': 'Flask',
    'django': 'Django',
    'sqlalchemy': 'SQLAlchemy',
    'asyncio': None,
    'json': None,
    'datetime': None,
    'os': None,
    'sys': None,
    're': None,
    'time': None,
    'math': None,
    'random': None,
    'logging': None,
    'threading': None,
    'subprocess': None,
    'zipfile': None,
    'tempfile': None,
    'shutil': None,
    'sqlite3': None,
    'psutil': 'psutil',
    'atexit': None
}
# --- End Automatic Package Installation & Script Running ---

# --- Database Operations ---
DB_LOCK = threading.Lock() 
_load_cleanup_state()

def save_user_file(user_id, file_name, file_type='py'):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR REPLACE INTO user_files (user_id, file_name, file_type) VALUES (?, ?, ?)',
                      (user_id, file_name, file_type))
            conn.commit()
            if user_id not in user_files: user_files[user_id] = []
            user_files[user_id] = [(fn, ft) for fn, ft in user_files[user_id] if fn != file_name]
            user_files[user_id].append((file_name, file_type))
            logger.info(f"Saved file '{file_name}' ({file_type}) for user {user_id}")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error saving file for user {user_id}, {file_name}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error saving file for {user_id}, {file_name}: {e}", exc_info=True)
        finally: conn.close()

def remove_user_file_db(user_id, file_name):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM user_files WHERE user_id = ? AND file_name = ?', (user_id, file_name))
            conn.commit()
            if user_id in user_files:
                user_files[user_id] = [f for f in user_files[user_id] if f[0] != file_name]
                if not user_files[user_id]: del user_files[user_id]
            logger.info(f"Removed file '{file_name}' for user {user_id} from DB")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error removing file for {user_id}, {file_name}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error removing file for {user_id}, {file_name}: {e}", exc_info=True)
        finally: conn.close()

def add_active_user(user_id):
    active_users.add(user_id) 
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO active_users (user_id) VALUES (?)', (user_id,))
            conn.commit()
            logger.info(f"Added/Confirmed active user {user_id} in DB")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error adding active user {user_id}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error adding active user {user_id}: {e}", exc_info=True)
        finally: conn.close()

def save_user_profile(user_id, first_name, username):
    """Persist display details for the owner/admin process dashboard."""
    first_name = (first_name or 'Unknown').strip()[:128]
    username = (username or '').strip().lstrip('@')[:64]
    user_profiles[user_id] = {'first_name': first_name, 'username': username}
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute(
                'INSERT OR REPLACE INTO user_profiles '
                '(user_id, first_name, username) VALUES (?, ?, ?)',
                (user_id, first_name, username)
            )
            conn.commit()
        except sqlite3.Error as e:
            logger.error(f"SQLite error saving profile {user_id}: {e}")
        finally:
            conn.close()

def user_display_name(user_id):
    profile = user_profiles.get(user_id, {})
    name = profile.get('first_name')
    username = profile.get('username')
    if not name:
        try:
            chat = bot.get_chat(user_id)
            name = chat.first_name or 'Unknown'
            username = chat.username or username or ''
            save_user_profile(user_id, name, username)
        except Exception:
            name = 'Unknown'
    return f"{name} (@{username})" if username else name

def make_file_callback(action, owner_id, file_name):
    """Keep Telegram callback_data under its 64-byte limit for long filenames."""
    token = hashlib.sha1(f"{owner_id}:{file_name}".encode('utf-8')).hexdigest()[:12]
    file_callback_refs[token] = (int(owner_id), file_name)
    return f"{action}_{owner_id}_{token}"

def parse_file_callback(data):
    parts = data.split('_', 2)
    if len(parts) != 3 or parts[2] not in file_callback_refs:
        raise ValueError("Expired or invalid file button")
    owner_id, file_name = file_callback_refs[parts[2]]
    if int(parts[1]) != owner_id:
        raise ValueError("Invalid file owner")
    return owner_id, file_name

def make_process_callback(script_key):
    token = hashlib.sha1(script_key.encode('utf-8')).hexdigest()[:12]
    process_callback_refs[token] = script_key
    return f"sendcmd_select_{token}"

def save_subscription(
    user_id, expiry, plan='legacy', price=None, activation_date=None,
    file_limit=None, status='active', payment_status='approved'
):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            expiry_str = expiry.isoformat()
            activation_date = activation_date or datetime.now().isoformat()
            conn.execute(
                'INSERT OR REPLACE INTO subscriptions '
                '(user_id, expiry, plan, price, activation_date, file_limit, status, payment_status) '
                'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
                (user_id, expiry_str, plan, price, activation_date, file_limit,
                 status, payment_status)
            )
            conn.commit()
            user_subscriptions[user_id] = {
                'expiry': expiry, 'plan': plan, 'price': price,
                'activation_date': activation_date, 'file_limit': file_limit,
                'status': status, 'payment_status': payment_status
            }
            logger.info(f"Saved subscription for {user_id}, plan={plan}, expiry={expiry_str}")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error saving subscription for {user_id}: {e}")
        finally: conn.close()

def set_pending_payment_plan(user_id, plan_key):
    """Persist the plan selected in the payment flow so restarts do not lose it."""
    if plan_key not in PREMIUM_PLANS:
        return False
    now = datetime.now().isoformat()
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute(
                'INSERT OR REPLACE INTO payment_sessions (user_id, plan, updated_at) '
                'VALUES (?, ?, ?)', (user_id, plan_key, now)
            )
            conn.commit()
        finally:
            conn.close()
    pending_payment_sessions[user_id] = plan_key
    return True

def clear_pending_payment_plan(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute('DELETE FROM payment_sessions WHERE user_id = ?', (user_id,))
            conn.commit()
        finally:
            conn.close()
    pending_payment_sessions.pop(user_id, None)

def remove_subscription_db(user_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('DELETE FROM subscriptions WHERE user_id = ?', (user_id,))
            conn.commit()
            if user_id in user_subscriptions: del user_subscriptions[user_id]
            logger.info(f"Removed subscription for {user_id} from DB")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error removing subscription for {user_id}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error removing subscription for {user_id}: {e}", exc_info=True)
        finally: conn.close()

def add_admin_db(admin_id):
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        try:
            c.execute('INSERT OR IGNORE INTO admins (user_id) VALUES (?)', (admin_id,))
            conn.commit()
            admin_ids.add(admin_id) 
            logger.info(f"Added admin {admin_id} to DB")
        except sqlite3.Error as e: logger.error(f"❌ SQLite error adding admin {admin_id}: {e}")
        except Exception as e: logger.error(f"❌ Unexpected error adding admin {admin_id}: {e}", exc_info=True)
        finally: conn.close()

def remove_admin_db(admin_id):
    if admin_id == OWNER_ID:
        logger.warning("Attempted to remove OWNER_ID from admins.")
        return False 
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        c = conn.cursor()
        removed = False
        try:
            c.execute('SELECT 1 FROM admins WHERE user_id = ?', (admin_id,))
            if c.fetchone():
                c.execute('DELETE FROM admins WHERE user_id = ?', (admin_id,))
                conn.commit()
                removed = c.rowcount > 0 
                if removed: admin_ids.discard(admin_id); logger.info(f"Removed admin {admin_id} from DB")
                else: logger.warning(f"Admin {admin_id} found but delete affected 0 rows.")
            else:
                logger.warning(f"Admin {admin_id} not found in DB.")
                admin_ids.discard(admin_id)
            return removed
        except sqlite3.Error as e: logger.error(f"❌ SQLite error removing admin {admin_id}: {e}"); return False
        except Exception as e: logger.error(f"❌ Unexpected error removing admin {admin_id}: {e}", exc_info=True); return False
        finally: conn.close()
# --- End Database Operations ---

# --- Premium Hosting / Payment System ---
def _is_admin(user_id):
    return user_id in admin_ids

def _plan_limit_text(plan):
    return "Unlimited" if plan.get('limit') is None else str(plan['limit'])

def premium_panel_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    for key, plan in PREMIUM_PLANS.items():
        markup.add(types.InlineKeyboardButton(
            f'💎 ₹{plan["price"]} • {_plan_limit_text(plan)} Files',
            callback_data=f'plan_{key}'
        ))
    markup.add(types.InlineKeyboardButton('💳 Current Plan', callback_data='my_plan'))
    markup.add(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def payment_markup(plan_key):
    plan = PREMIUM_PLANS[plan_key]
    upi_id = bot_settings.get('upi_id') or 'rajanwins@ibl'
    markup = types.InlineKeyboardMarkup(row_width=1)
    # Telegram's native copy button copies the UPI ID directly on tap.
    # Keep the callback handler below for older payment messages/clients.
    markup.add(types.InlineKeyboardButton(
        '💞😈 Copy UPI ID',
        copy_text=types.CopyTextButton(text=upi_id),
    ))
    markup.add(types.InlineKeyboardButton('📱 Pay via UPI', callback_data=f'pay_upi_{plan_key}'))
    markup.add(types.InlineKeyboardButton('🖼️ Show QR', callback_data=f'show_qr_{plan_key}'))
    markup.add(types.InlineKeyboardButton('📸 Send Payment Screenshot', callback_data=f'send_screenshot_{plan_key}'))
    markup.add(types.InlineKeyboardButton(
        '💌 Contact Owner',
        url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'
    ))
    markup.add(types.InlineKeyboardButton('⬅️ Back to Plans', callback_data='paid_panel'))
    return markup

def _paid_panel_text(user_id):
    lines = [
        '🌷💗 AKSHAYY!! 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐇𝐎𝐒𝐓𝐈𝐍𝐆 💗🌷',
        '━━━━━━━━━━━━━━━━━━',
        '',
        '💎 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐏𝐋𝐀𝐍𝐒',
        '',
        '💗 ₹100 ➜ 𝟓 𝐅𝐢𝐥𝐞𝐬 • 𝟑𝟎 𝐃𝐚𝐲𝐬',
        '🌷 ₹200 ➜ 𝟏𝟎 𝐅𝐢𝐥𝐞𝐬 • 𝟔𝟎 𝐃𝐚𝐲𝐬',
        '💎 ₹500 ➜ 𝟓𝟎 𝐅𝐢𝐥𝐞𝐬 • 𝟏𝟖𝟎 𝐃𝐚𝐲𝐬',
        '👑 ₹1000 ➜ 𝐔𝐧𝐥𝐢𝐦𝐢𝐭𝐞𝐝 𝐅𝐢𝐥𝐞𝐬 • 𝟑𝟔𝟓 𝐃𝐚𝐲𝐬',
        '',
        '━━━━━━━━━━━━━━━━━━',
        '💌 𝐂ʟɪᴄᴋ 𝐀 𝐏ʟᴀɴ 𝐁ᴇʟᴏᴡ 𝐓ᴏ 𝐂ᴏɴᴛɪɴᴜᴇ',
        '━━━━━━━━━━━━━━━━━━',
    ]
    expire_subscription_if_needed(user_id)
    sub = user_subscriptions.get(user_id)
    if sub and sub.get('expiry') and sub['expiry'] > datetime.now():
        plan_label = PREMIUM_PLANS.get(sub.get('plan'), {}).get(
            'name', sub.get('plan', 'Premium')
        )
        lines += [
            '',
            f'✅ 𝐂ᴜʀʀᴇɴᴛ 𝐏ʟᴀɴ: {plan_label}',
            f'📁 𝐋ɪᴍɪᴛ: {_plan_limit_text(sub)} files',
            f'⏳ 𝐄xᴘɪʀʏ: {sub["expiry"]:%d %b %Y • %I:%M %p}',
        ]
    else:
        lines += ['', '🆓 𝐂ᴜʀʀᴇɴᴛ 𝐏ʟᴀɴ: 𝐅ʀᴇᴇ • 𝟏 𝐅ɪʟᴇ']
    return '\n'.join(lines)

def show_paid_panel(chat_id, user_id, message_id=None):
    text = _paid_panel_text(user_id)
    if message_id:
        bot.edit_message_text(text, chat_id, message_id, reply_markup=premium_panel_markup())
    else:
        bot.send_message(chat_id, text, reply_markup=premium_panel_markup())

def _payment_page_text(plan_key):
    plan = PREMIUM_PLANS[plan_key]
    upi_id = bot_settings.get('upi_id') or 'rajanwins@ibl'
    return (
        '🇮🇳 𝐂𝐎𝐍𝐅𝐈𝐑𝐌 𝐃𝐄𝐏𝐎𝐒𝐈𝐓 🇮🇳\n'
        '━━━━━━━━━━━━━━━━━━\n\n'
        f'💰 𝐀𝐦𝐨ᴜɴᴛ: ₹{plan["price"]:.2f}\n\n'
        '📲 𝐏𝐚ʏ ᴛᴏ UPI:\n'
        f'"{upi_id}"\n\n'
        '📸 𝐀ғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ, sᴇɴᴅ\n'
        '𝐏ᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ ʜᴇʀᴇ.\n\n'
        '━━━━━━━━━━━━━━━━━━\n'
        '💗 𝐇𝐈𝐍𝐀𝐓𝐀 𝐏𝐑𝐄𝐌𝐈𝐔𝐌 𝐇𝐎𝐒𝐓𝐈𝐍𝐆'
    )

def show_payment_page(call, plan_key):
    if plan_key not in PREMIUM_PLANS:
        bot.answer_callback_query(call.id, 'Invalid plan.', show_alert=True)
        return
    set_pending_payment_plan(call.from_user.id, plan_key)
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text(
            _payment_page_text(plan_key),
            call.message.chat.id,
            call.message.message_id,
            reply_markup=payment_markup(plan_key)
        )
    except telebot.apihelper.ApiTelegramException as e:
        if 'message is not modified' not in str(e).lower():
            logger.warning("Could not edit payment page, sending a new one: %s", e)
        bot.send_message(
            call.message.chat.id,
            _payment_page_text(plan_key),
            reply_markup=payment_markup(plan_key)
        )

def _send_payment_qr(call, plan_key):
    if plan_key not in PREMIUM_PLANS:
        bot.answer_callback_query(call.id, 'Invalid plan.', show_alert=True)
        return
    if not bot_settings.get('qr_file_id'):
        bot.answer_callback_query(
            call.id,
            'Payment QR is not configured yet. Use the UPI ID above.',
            show_alert=True
        )
        return
    upi_id = bot_settings.get('upi_id') or 'rajanwins@ibl'
    bot.answer_callback_query(call.id, 'Opening configured QR...')
    bot.send_photo(
        call.message.chat.id,
        bot_settings['qr_file_id'],
        caption=(
            '💳 𝐔ᴘɪ ID:\n\n'
            f'{upi_id}\n\n'
            '📱 PhonePe • Google Pay • Paytm • UPI'
        ),
        reply_markup=payment_markup(plan_key)
    )

def _save_bot_setting(key, value):
    bot_settings[key] = value
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute('INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)', (key, value))
            conn.commit()
        finally:
            conn.close()

def _create_payment_request(user_id, plan_key, screenshot_file_id, user_name):
    plan = PREMIUM_PLANS[plan_key]
    request_id = f'pay_{user_id}_{int(time.time())}_{hashlib.sha1(str(screenshot_file_id).encode()).hexdigest()[:8]}'
    created_at = datetime.now().isoformat()
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            conn.execute(
                'INSERT INTO payment_requests '
                '(request_id,user_id,user_name,plan,price,file_limit,validity_days,'
                'screenshot_file_id,status,payment_status,created_at) '
                'VALUES (?,?,?,?,?,?,?,?,?,?,?)',
                (
                    request_id, user_id, user_name, plan_key, plan['price'],
                    plan['limit'], plan['days'], screenshot_file_id,
                    'pending', 'pending', created_at
                )
            )
            conn.commit()
        finally:
            conn.close()
    pending_payments[request_id] = {
        'user_id': user_id,
        'user_name': user_name,
        'plan': plan_key,
        'price': plan['price'],
        'file_limit': plan['limit'],
        'validity_days': plan['days'],
        'screenshot_file_id': screenshot_file_id,
        'status': 'pending',
        'created_at': created_at,
    }
    return request_id

def _send_payment_request_to_admin(request_id):
    item = pending_payments.get(request_id)
    if not item:
        return
    plan = PREMIUM_PLANS[item['plan']]
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(types.InlineKeyboardButton('✅ APPROVE', callback_data=f'payapprove_{request_id}'), types.InlineKeyboardButton('❌ REJECT', callback_data=f'payreject_{request_id}'))
    text = (
        '🌷💗 𝐍ᴇᴡ Pᴀʏᴍᴇɴᴛ Rᴇǫᴜᴇsᴛ 💗🌷\n'
        '━━━━━━━━━━━━━━━━━━\n\n'
        f'👤 𝐔sᴇʀ: {item["user_name"]}\n'
        f'🆔 𝐔sᴇʀ ID: `{item["user_id"]}`\n\n'
        f'💎 𝐏ʟᴀɴ: ₹{plan["price"]}\n'
        f'📁 𝐅ɪʟᴇ Lɪᴍɪᴛ: {_plan_limit_text(plan)}\n'
        f'⏳ 𝐕ᴀʟɪᴅɪᴛʏ: {plan["days"]} Days\n'
        f'💰 𝐀ᴍᴏᴜɴᴛ: ₹{plan["price"]}\n\n'
        '━━━━━━━━━━━━━━━━━━\n'
        f'🆔 Request: `{request_id}`'
    )
    for aid in sorted(admin_ids):
        try:
            bot.send_photo(aid, item['screenshot_file_id'], caption=text, reply_markup=markup, parse_mode='Markdown')
        except Exception as e:
            logger.error(f'Payment request send failed to admin {aid}: {e}')

def _activate_paid_plan(request_id, approver_id):
    if approver_id not in admin_ids:
        return False, 'Unauthorized'
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            row = conn.execute('SELECT user_id, plan, price, status FROM payment_requests WHERE request_id=?', (request_id,)).fetchone()
            if not row:
                return False, 'Payment request not found'
            user_id, plan_key, price, status = row
            if status != 'pending':
                return False, f'Already {status}'
            plan = PREMIUM_PLANS.get(plan_key)
            if not plan:
                return False, 'Invalid plan'
            now = datetime.now()
            expiry = now + timedelta(days=plan['days'])
            cur = conn.execute(
                'UPDATE payment_requests SET status=?, payment_status=?, decided_at=? '
                'WHERE request_id=? AND status=?',
                ('approved', 'approved', now.isoformat(), request_id, 'pending')
            )
            if cur.rowcount != 1:
                return False, 'Already decided'
            conn.execute(
                'INSERT OR REPLACE INTO subscriptions '
                '(user_id,expiry,plan,price,activation_date,file_limit,status,payment_status) '
                'VALUES (?,?,?,?,?,?,?,?)',
                (
                    user_id, expiry.isoformat(), plan_key, price, now.isoformat(),
                    plan['limit'], 'active', 'approved'
                )
            )
            conn.commit()
        finally:
            conn.close()
    pending_payments.pop(request_id, None)
    user_subscriptions[user_id] = {
        'expiry': expiry, 'plan': plan_key, 'price': price,
        'activation_date': now.isoformat(), 'file_limit': plan['limit'],
        'status': 'active', 'payment_status': 'approved'
    }
    return True, (user_id, plan_key, expiry)

def _reject_payment(request_id, approver_id):
    if approver_id not in admin_ids:
        return False, 'Unauthorized'
    with DB_LOCK:
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            row = conn.execute('SELECT user_id,status FROM payment_requests WHERE request_id=?', (request_id,)).fetchone()
            if not row:
                return False, 'Payment request not found'
            user_id, status = row
            if status != 'pending':
                return False, f'Already {status}'
            cur = conn.execute(
                'UPDATE payment_requests SET status=?, payment_status=?, decided_at=? '
                'WHERE request_id=? AND status=?',
                ('rejected', 'rejected', datetime.now().isoformat(),
                 request_id, 'pending')
            )
            if cur.rowcount != 1:
                return False, 'Already decided'
            conn.commit()
        finally:
            conn.close()
    pending_payments.pop(request_id, None)
    return True, user_id

def _logic_paid_panel(message):
    show_paid_panel(message.chat.id, message.from_user.id)

@bot.message_handler(commands=['setup'])
def command_setup(message):
    """Compatibility entry point retained for existing deployments."""
    if not _force_join_guard(message):
        return
    _logic_send_welcome(message)

@bot.message_handler(commands=['set'])
def command_set(message):
    """Keep the original /set style while supporting QR/UPI configuration."""
    if not _is_admin(message.from_user.id):
        bot.reply_to(message, '⚠️ Admin/Owner only.')
        return
    parts = message.text.split(maxsplit=2)
    setting = parts[1].lower() if len(parts) > 1 else ''
    if setting == 'qr':
        if not message.reply_to_message or not message.reply_to_message.photo:
            bot.reply_to(message, '📱 QR image ko reply karke `/set qr` use karo.')
            return
        _save_bot_setting('qr_file_id', message.reply_to_message.photo[-1].file_id)
        bot.reply_to(message, '✅ Payment QR saved/updated successfully.')
    elif setting in ('upi', 'upi_id'):
        upi = parts[2].strip() if len(parts) > 2 else ''
        if not upi or '@' not in upi:
            bot.reply_to(message, '❌ Use: `/set upi yourupi@upi`')
            return
        _save_bot_setting('upi_id', upi[:128])
        bot.reply_to(message, f'✅ UPI ID saved: `{upi[:128]}`', parse_mode='Markdown')
    elif setting == 'video':
        if not message.reply_to_message or not message.reply_to_message.video:
            bot.reply_to(message, '🎬 Video ko reply karke `/set video` use karo.')
            return
        _save_bot_setting('welcome_video_file_id', message.reply_to_message.video.file_id)
        bot.reply_to(message, '✅ Welcome video saved/updated successfully.')
    else:
        bot.reply_to(
            message,
            '⚙️ Settings:\n'
            '• Reply to a QR image: `/set qr`\n'
            '• Set UPI: `/set upi yourupi@upi`\n'
            '• Reply to a video: `/set video`'
        )


def _force_join_settings_text():
    lines = [
        "🔒 Force Join Settings",
        "━━━━━━━━━━━━━━━━━━",
        "All enabled channels are required before users can use the bot.",
        "",
    ]
    configured = {
        entry["index"]: entry
        for entry in _force_join_slots()
    }
    for index in range(1, 6):
        entry = configured.get(index)
        if not entry:
            lines.append(f"{index}. OFF")
        elif entry["private"]:
            lines.append(f"{index}. 🔐 {entry['label']} (private invite)")
        else:
            lines.append(f"{index}. {entry['target']} → {entry['label']}")
    lines.extend([
        "",
        "Commands:",
        "/setforce1 @channel | Button Text",
        "/setforce2 @channel | Button Text",
        "/setforce3 @channel | Button Text",
        "/setforce4 @channel | Button Text",
        "/setforce5 @channel | Button Text",
        "",
        "Disable: /setforce1 off",
        "Private: /setforce1 -1001234567890 https://t.me/+INVITE | 🔐 Join Private Channel",
    ])
    return "\n".join(lines)


@bot.message_handler(commands=['force'])
def command_force(message):
    if not _is_admin(message.from_user.id):
        bot.reply_to(message, '⚠️ Admin/Owner only.')
        return
    bot.reply_to(message, _force_join_settings_text())


def _set_force_join_slot(message, slot):
    if not _is_admin(message.from_user.id):
        bot.reply_to(message, '⚠️ Admin/Owner only.')
        return

    parts = message.text.split(maxsplit=1)
    raw_value = parts[1].strip() if len(parts) == 2 else ""
    if "|" in raw_value:
        target_part, label = raw_value.split("|", 1)
        target_part = target_part.strip()
        label = label.strip()
    else:
        target_part = raw_value
        label = ""
    if label.lower() == "off":
        label = ""

    if target_part.lower() == "off":
        value = "off"
    else:
        private_match = re.fullmatch(
            r"(-100\d{5,})\s+(https?://t\.me/\+[A-Za-z0-9_-]+)",
            target_part,
            re.IGNORECASE,
        )
        private_link_match = re.fullmatch(
            r"https?://t\.me/\+[A-Za-z0-9_-]+",
            target_part,
            re.IGNORECASE,
        )

        if private_match:
            chat_id = int(private_match.group(1))
            target = private_match.group(2)
            if not label:
                label = "🔐 Join Private Channel"
            value = json.dumps(
                {"target": target, "chat_id": chat_id, "label": label[:64]},
                ensure_ascii=False,
            )
        elif private_link_match:
            bot.reply_to(
                message,
                "❌ Private invite link ke saath channel chat ID bhi chahiye.\n\n"
                f"Use: `/setforce{slot} -1001234567890 {target_part} | "
                "🔐 Join Private Channel`",
                parse_mode="Markdown",
            )
            return
        elif re.fullmatch(r"@[A-Za-z0-9_]{3,64}", target_part):
            value = json.dumps(
                {
                    "target": target_part,
                    "label": (label or f"📢 Join Channel {slot}")[:64],
                },
                ensure_ascii=False,
            )
        else:
            value = None

    if value is None:
        bot.reply_to(
            message,
            f"❌ Use: `/setforce{slot} @channel | Button Text` "
            f"or `/setforce{slot} off`",
            parse_mode="Markdown",
        )
        return

    _save_bot_setting(f"force_join_{slot}", value)
    _refresh_force_join_channels()
    if value == "off":
        bot.reply_to(message, f"✅ Force Join Channel {slot} disabled permanently.")
    else:
        bot.reply_to(
            message,
            f"✅ Force Join Channel {slot} saved: {value}\n"
            "Make sure the bot is an administrator in that channel.",
        )


@bot.message_handler(commands=[
    'setforce1', 'setforce2', 'setforce3', 'setforce4', 'setforce5'
])
def command_setforce(message):
    match = re.match(r"^/setforce([1-5])(?:@\w+)?", message.text or "", re.IGNORECASE)
    if not match:
        bot.reply_to(message, "❌ Invalid Force Join command.")
        return
    _set_force_join_slot(message, int(match.group(1)))


@bot.message_handler(commands=['paidpanel','premium','plans'])
def command_paid_panel(message):
    if not _force_join_guard(message):
        return
    _logic_paid_panel(message)

@bot.message_handler(commands=['setupi'])
def command_setupi(message):
    if not _is_admin(message.from_user.id):
        bot.reply_to(message, '⚠️ Admin/Owner only.')
        return
    if not _force_join_guard(message):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) != 2 or '@' not in parts[1]:
        bot.reply_to(message, '❌ Use: /setupi yourupi@upi')
        return
    upi = parts[1].strip()[:128]
    _save_bot_setting('upi_id', upi)
    bot.reply_to(message, f'✅ UPI ID saved: `{upi}`', parse_mode='Markdown')

@bot.message_handler(commands=['setqr'])
def command_setqr(message):
    if not _is_admin(message.from_user.id):
        bot.reply_to(message, '⚠️ Admin/Owner only.')
        return
    if not _force_join_guard(message):
        return
    if not message.reply_to_message or not message.reply_to_message.photo:
        bot.reply_to(message, '📱 QR image ko reply karke /setqr use karo.')
        return
    _save_bot_setting('qr_file_id', message.reply_to_message.photo[-1].file_id)
    bot.reply_to(message, '✅ PhonePe UPI QR saved/updated successfully.')

@bot.message_handler(commands=['setvideo'])
def command_setvideo(message):
    if not _is_admin(message.from_user.id):
        bot.reply_to(message, '⚠️ Admin/Owner only.')
        return
    if not _force_join_guard(message):
        return
    if not message.reply_to_message or not message.reply_to_message.video:
        bot.reply_to(message, '🎬 Video ko reply karke /setvideo use karo.')
        return
    _save_bot_setting('welcome_video_file_id', message.reply_to_message.video.file_id)
    bot.reply_to(message, '✅ Welcome video saved/updated successfully.')

@bot.message_handler(content_types=['photo'])
def handle_payment_screenshot(message):
    user_id = message.from_user.id
    if not _force_join_guard(message):
        return
    plan_key = pending_payment_sessions.get(user_id)
    if not plan_key:
        # Photos outside the payment flow should not be treated as payments.
        return
    plan = PREMIUM_PLANS.get(plan_key)
    if not plan:
        return
    if not bot_settings.get('upi_id') and not bot_settings.get('qr_file_id'):
        bot.reply_to(message, '⚠️ Payment setup abhi configured nahi hai. Admin se UPI/QR set karwayein.')
        return
    file_id = message.photo[-1].file_id
    rid = _create_payment_request(user_id, plan_key, file_id, message.from_user.first_name or 'User')
    clear_pending_payment_plan(user_id)
    _send_payment_request_to_admin(rid)
    bot.reply_to(
        message,
        '🌷💗 𝐏ᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ 💗🌷\n\n'
        '✅ Screenshot received.\n\n'
        'Your payment request has been sent to the admin for manual verification.\n'
        '⏳ Please wait for approval.\n\n'
        f'💎 Plan: ₹{plan["price"]}\n🆔 Request: `{rid}`',
        parse_mode='Markdown'
    )

# --- Menu creation (Inline and ReplyKeyboards) ---
def create_main_menu_inline(user_id):
    markup = types.InlineKeyboardMarkup(row_width=2)
    buttons = [
        types.InlineKeyboardButton('🌷 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 𝐂𝐡𝐚𝐧𝐧𝐞𝐥', url=UPDATE_CHANNEL),
        types.InlineKeyboardButton('📤 𝐔𝐩𝐥𝐨𝐚𝐝 𝐒ᴄʀɪᴘᴛ', callback_data='upload'),
        types.InlineKeyboardButton('📂 𝐌ʏ Fɪʟᴇs', callback_data='check_files'),
        types.InlineKeyboardButton('🟢 𝐑ᴜɴɴɪɴɢ Bᴏᴛs', callback_data='running_bots'),
        types.InlineKeyboardButton('⚡ 𝐁ᴏᴛ Sᴛᴀᴛᴜs', callback_data='speed'),
        types.InlineKeyboardButton('🛰 𝐒ᴇɴᴅ Cᴏᴍᴍᴀɴᴅ', callback_data='send_command'),
        types.InlineKeyboardButton('💳 𝐒ᴜʙsᴄʀɪᴘᴛɪᴏɴs', callback_data='my_subscription'),
        types.InlineKeyboardButton('💌 𝐂ᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}')
    ]

    if user_id in admin_ids:
        admin_buttons = [
            types.InlineKeyboardButton('💎 𝐒ᴜʙsᴄʀɪᴘᴛɪᴏɴs', callback_data='subscription'),
            types.InlineKeyboardButton('📊 𝐒ᴛᴀᴛɪsᴛɪᴄs', callback_data='stats'),
            types.InlineKeyboardButton('🔒 𝐋ᴏᴄᴋ Bᴏᴛ' if not bot_locked else '🔓 𝐔ɴʟᴏᴄᴋ Bᴏᴛ',
                                     callback_data='lock_bot' if not bot_locked else 'unlock_bot'),
            types.InlineKeyboardButton('📢 𝐁ʀᴏᴀᴅᴄᴀsᴛ', callback_data='broadcast'),
            types.InlineKeyboardButton('👑 𝐀ᴅᴍɪɴ Pᴀɴᴇʟ', callback_data='admin_panel'),
            types.InlineKeyboardButton('🟢 𝐑ᴜɴ Aʟʟ Sᴄʀɪᴘᴛs', callback_data='run_all_scripts')
        ]
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], admin_buttons[0])
        markup.add(admin_buttons[1], admin_buttons[3])
        markup.add(admin_buttons[2], admin_buttons[5])
        markup.add(buttons[4])  # Send Command
        markup.add(admin_buttons[4])
        markup.add(buttons[5])
    else:
        markup.add(buttons[0])
        markup.add(buttons[1], buttons[2])
        markup.add(buttons[3], buttons[4])
        markup.add(buttons[5])
        markup.add(types.InlineKeyboardButton('📊 Statistics', callback_data='stats'))
        markup.add(buttons[6])
        markup.add(buttons[7])
    return markup

def create_reply_keyboard_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    layout_to_use = ADMIN_COMMAND_BUTTONS_LAYOUT_USER_SPEC if user_id in admin_ids else COMMAND_BUTTONS_LAYOUT_USER_SPEC
    for row_buttons_text in layout_to_use:
        markup.add(*[types.KeyboardButton(text) for text in row_buttons_text])
    return markup

def create_control_buttons(script_owner_id, file_name, is_running=True):
    markup = types.InlineKeyboardMarkup(row_width=2)
    if is_running:
        markup.row(
            types.InlineKeyboardButton("⛔ Stop Script", callback_data=make_file_callback('stop', script_owner_id, file_name)),
            types.InlineKeyboardButton("♻️ Restart", callback_data=make_file_callback('restart', script_owner_id, file_name))
        )
        markup.row(
            types.InlineKeyboardButton("🗑️ Delete File", callback_data=make_file_callback('delete', script_owner_id, file_name)),
            types.InlineKeyboardButton("📜 View Logs", callback_data=make_file_callback('logs', script_owner_id, file_name))
        )
    else:
        markup.row(
            types.InlineKeyboardButton("🚀 Start Script", callback_data=make_file_callback('start', script_owner_id, file_name)),
            types.InlineKeyboardButton("🗑️ Delete File", callback_data=make_file_callback('delete', script_owner_id, file_name))
        )
        markup.row(
            types.InlineKeyboardButton("📜 View Logs", callback_data=make_file_callback('logs', script_owner_id, file_name))
        )
    markup.add(types.InlineKeyboardButton("↩️ Back to My Files", callback_data='check_files'))
    return markup

def create_admin_panel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('📊 𝐒ᴛᴀᴛɪsᴛɪᴄs', callback_data='stats'),
        types.InlineKeyboardButton('📤 𝐔ᴘʟᴏᴀᴅ Sᴄʀɪᴘᴛ', callback_data='upload')
    )
    markup.row(
        types.InlineKeyboardButton('🟢 𝐑ᴜɴɴɪɴɢ Bᴏᴛs', callback_data='running_bots'),
        types.InlineKeyboardButton('⚡ 𝐁ᴏᴛ Sᴛᴀᴛᴜs', callback_data='speed')
    )
    markup.row(
        types.InlineKeyboardButton('💳 𝐒ᴜʙsᴄʀɪᴘᴛɪᴏɴs', callback_data='subscription'),
        types.InlineKeyboardButton('📢 𝐁ʀᴏᴀᴅᴄᴀsᴛ', callback_data='broadcast')
    )
    markup.row(
        types.InlineKeyboardButton(
            '🔒 𝐋ᴏᴄᴋ Bᴏᴛ' if not bot_locked else '🔓 𝐔ɴʟᴏᴄᴋ Bᴏᴛ',
            callback_data='lock_bot' if not bot_locked else 'unlock_bot'
        ),
        types.InlineKeyboardButton('🟢 𝐑ᴜɴ Aʟʟ Sᴄʀɪᴘᴛs', callback_data='run_all_scripts')
    )
    markup.row(types.InlineKeyboardButton('🛰 𝐒ᴇɴᴅ Cᴏᴍᴍᴀɴᴅ', callback_data='send_command'))
    markup.row(
        types.InlineKeyboardButton('➕ Add Admin', callback_data='add_admin'),
        types.InlineKeyboardButton('➖ Remove Admin', callback_data='remove_admin')
    )
    markup.row(types.InlineKeyboardButton('📋 List Admins', callback_data='list_admins'))
    markup.row(types.InlineKeyboardButton(
        '💌 𝐂ᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ',
        url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'
    ))
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def create_subscription_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('➕ Add Subscription', callback_data='add_subscription'),
        types.InlineKeyboardButton('➖ Remove Subscription', callback_data='remove_subscription')
    )
    markup.row(types.InlineKeyboardButton('🔍 Check Subscription', callback_data='check_subscription'))
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup

def create_send_command_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.row(
        types.InlineKeyboardButton('📝 Send to Process', callback_data='send_to_process'),
        types.InlineKeyboardButton('🔍 View All Logs', callback_data='view_all_logs')
    )
    markup.row(types.InlineKeyboardButton('🔙 Back to Main', callback_data='back_to_main'))
    return markup
# --- End Menu Creation ---

# --- File Handling with Malware Detection ---
def handle_zip_file(downloaded_file_content, file_name_zip, message, owner_id=None):
    user_id = owner_id if owner_id is not None else message.from_user.id
    user_folder = get_user_folder(user_id)
    temp_dir = None
    
    # Security check for ZIP files (except owner)
    if user_id != OWNER_ID:
        is_safe, reason = scan_file_for_malware(downloaded_file_content, file_name_zip, user_id)
        if not is_safe:
            bot.reply_to(message, f"🚨 Security Alert: {reason}\nOnly owner can upload this type of file.")
            return
    
    try:
        temp_dir = tempfile.mkdtemp(
            prefix=f"user_{user_id}_zip_",
            dir=TEMP_DOWNLOAD_DIR,
        )
        _mark_temp_path_active(temp_dir)
        logger.info(f"Temp dir for zip: {temp_dir}")
        safe_zip_name = _safe_uploaded_file_name(file_name_zip) or "upload.zip"
        zip_path = os.path.join(temp_dir, safe_zip_name)
        with open(zip_path, 'wb') as new_file:
            new_file.write(downloaded_file_content)
        
        # Open Zip to Extract
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Additional security check on content
            for member in zip_ref.infolist():
                member_path = os.path.abspath(
                    os.path.join(temp_dir, member.filename)
                )
                if (
                    os.path.isabs(member.filename)
                    or os.path.commonpath((
                        os.path.abspath(temp_dir), member_path
                    )) != os.path.abspath(temp_dir)
                ):
                    raise zipfile.BadZipFile(
                        f"Zip has unsafe path: {member.filename}"
                    )
                if user_id != OWNER_ID:
                    member_name_lower = member.filename.lower()
                    suspicious_extensions = ['.exe', '.dll', '.bat', '.cmd', '.scr', '.com']
                    if any(member_name_lower.endswith(ext) for ext in suspicious_extensions):
                        bot.reply_to(message, f"🚨 Security Alert: ZIP contains suspicious file: {member.filename}\nOnly owner can upload such files.")
                        return
            
            # Extract everything
            zip_ref.extractall(temp_dir)
            logger.info(f"Extracted zip to {temp_dir}")

        # --- FIX: Recursively find script if not in root (ignores __MACOSX) ---
        target_dir = temp_dir
        root_files = os.listdir(target_dir)
        
        # Check if script exists in root
        if not any(f.lower().endswith(('.py', '.js', '.java')) for f in root_files):
            # Recursively search for a folder containing a supported source file.
            for root, dirs, files in os.walk(temp_dir):
                # Ignore system/hidden folders like __MACOSX or .git
                dirs[:] = [d for d in dirs if not d.startswith('.') and not d.startswith('__')]
                
                if any(f.lower().endswith(('.py', '.js', '.java')) for f in files):
                    target_dir = root
                    break
        
        # If the script is in a subdirectory, move everything up to temp_dir
        if target_dir != temp_dir:
            logger.info(f"Flattening extracted files from {target_dir} to {temp_dir}")
            for item in os.listdir(target_dir):
                s = os.path.join(target_dir, item)
                d = os.path.join(temp_dir, item)
                # Overwrite if exists (shouldn't happen often in this temp context)
                if os.path.exists(d):
                    if os.path.isdir(d): shutil.rmtree(d)
                    else: os.remove(d)
                shutil.move(s, d)
            # Refresh list after flattening
            extracted_items = os.listdir(temp_dir)
        else:
            extracted_items = root_files
        # --- END FIX ---

        py_files = [f for f in extracted_items if f.lower().endswith('.py')]
        js_files = [f for f in extracted_items if f.lower().endswith('.js')]
        java_files = [f for f in extracted_items if f.lower().endswith('.java')]
        req_file = 'requirements.txt' if 'requirements.txt' in extracted_items else None
        pkg_json = 'package.json' if 'package.json' in extracted_items else None

        if req_file:
            req_path = os.path.join(temp_dir, req_file)
            logger.info(f"requirements.txt found, installing: {req_path}")
            bot.reply_to(message, f"🔄 Installing Python deps from `{req_file}`...")
            try:
                command = _pip_install_command('-r', req_path)
                if command is None:
                    raise RuntimeError("pip is not available in the runtime.")
                result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8', errors='ignore')
                logger.info(f"pip install from requirements.txt OK. Output:\n{result.stdout}")
                bot.reply_to(message, f"✅ Python deps from `{req_file}` installed.")
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ Failed to install Python deps from `{req_file}`.\nLog:\n```\n{e.stderr or e.stdout}\n```"
                logger.error(error_msg)
                if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log truncated)"
                bot.reply_to(message, error_msg, parse_mode='Markdown'); return
            except Exception as e:
                 error_msg = f"❌ Unexpected error installing Python deps: {e}"
                 logger.error(error_msg, exc_info=True); bot.reply_to(message, error_msg); return

        if pkg_json:
            logger.info(f"package.json found, npm install in: {temp_dir}")
            bot.reply_to(message, f"🔄 Installing Node deps from `{pkg_json}`...")
            try:
                command = ['npm', 'install']
                result = subprocess.run(command, capture_output=True, text=True, check=True, cwd=temp_dir, encoding='utf-8', errors='ignore')
                logger.info(f"npm install OK. Output:\n{result.stdout}")
                bot.reply_to(message, f"✅ Node deps from `{pkg_json}` installed.")
            except FileNotFoundError:
                bot.reply_to(message, "❌ 'npm' not found. Cannot install Node deps."); return 
            except subprocess.CalledProcessError as e:
                error_msg = f"❌ Failed to install Node deps from `{pkg_json}`.\nLog:\n```\n{e.stderr or e.stdout}\n```"
                logger.error(error_msg)
                if len(error_msg) > 4000: error_msg = error_msg[:4000] + "\n... (Log truncated)"
                bot.reply_to(message, error_msg, parse_mode='Markdown'); return
            except Exception as e:
                 error_msg = f"❌ Unexpected error installing Node deps: {e}"
                 logger.error(error_msg, exc_info=True); bot.reply_to(message, error_msg); return

        main_script_name = None; file_type = None
        preferred_py = ['main.py', 'bot.py', 'app.py']; preferred_js = ['index.js', 'main.js', 'bot.js', 'app.js']
        preferred_java = ['Main.java', 'Bot.java', 'App.java']
        for p in preferred_py:
            if p in py_files: main_script_name = p; file_type = 'py'; break
        if not main_script_name:
             for p in preferred_js:
                 if p in js_files: main_script_name = p; file_type = 'js'; break
        if not main_script_name:
             for p in preferred_java:
                 if p in java_files: main_script_name = p; file_type = 'java'; break
        if not main_script_name:
            if py_files: main_script_name = py_files[0]; file_type = 'py'
            elif js_files: main_script_name = js_files[0]; file_type = 'js'
            elif java_files: main_script_name = java_files[0]; file_type = 'java'
        if not main_script_name:
            bot.reply_to(message, "❌ No `.py`, `.js`, or `.java` script found in archive!"); return

        logger.info(f"Moving extracted files from {temp_dir} to {user_folder}")
        moved_count = 0
        for item_name in os.listdir(temp_dir):
            if item_name == file_name_zip: continue # Don't move the zip file itself if it's there
            src_path = os.path.join(temp_dir, item_name)
            dest_path = os.path.join(user_folder, item_name)
            if os.path.isdir(dest_path): shutil.rmtree(dest_path)
            elif os.path.exists(dest_path): os.remove(dest_path)
            shutil.move(src_path, dest_path); moved_count +=1
        logger.info(f"Moved {moved_count} items to {user_folder}")

        save_user_file(user_id, main_script_name, file_type)
        logger.info(f"Saved main script '{main_script_name}' ({file_type}) for {user_id} from zip.")
        main_script_path = os.path.join(user_folder, main_script_name)
        bot.reply_to(message, f"✅ Files extracted. Starting main script: `{main_script_name}`...", parse_mode='Markdown')

        if file_type == 'py':
             threading.Thread(target=run_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
        elif file_type == 'js':
             threading.Thread(target=run_js_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()
        elif file_type == 'java':
             threading.Thread(target=run_java_script, args=(main_script_path, user_id, user_folder, main_script_name, message)).start()

    except zipfile.BadZipFile as e:
        logger.error(f"Bad zip file from {user_id}: {e}")
        bot.reply_to(message, f"❌ Error: Invalid/corrupted ZIP. {e}")
    except Exception as e:
        logger.error(f"❌ Error processing zip for {user_id}: {e}", exc_info=True)
        if _is_no_space_error(e):
            _handle_no_space_error("ZIP upload/extraction", message.chat.id)
        bot.reply_to(message, f"❌ Error processing zip: {str(e)}")
    finally:
        if temp_dir and os.path.exists(temp_dir):
            _unmark_temp_path_active(temp_dir)
            try: shutil.rmtree(temp_dir); logger.info(f"Cleaned temp dir: {temp_dir}")
            except Exception as e: logger.error(f"Failed to clean temp dir {temp_dir}: {e}", exc_info=True)
def handle_js_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'js')
        threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"❌ Error processing JS file {file_name} for {script_owner_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error processing JS file: {str(e)}")

def handle_py_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, 'py')
        threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, message)).start()
    except Exception as e:
        logger.error(f"❌ Error processing Python file {file_name} for {script_owner_id}: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Error processing Python file: {str(e)}")


def run_java_script(script_path, script_owner_id, user_folder, file_name, message_obj_for_reply):
    """Compile and host one Java source file without touching project files."""
    script_key = f"{script_owner_id}_{file_name}"
    class_name = os.path.splitext(os.path.basename(file_name))[0]
    process = None
    log_file = None
    try:
        if not os.path.isfile(script_path):
            bot.reply_to(message_obj_for_reply, f"❌ Java file '{file_name}' not found.")
            return
        if shutil.which("javac") is None or shutil.which("java") is None:
            bot.reply_to(
                message_obj_for_reply,
                "❌ Java runtime/compiler not found. Install JDK (javac + java) on the host."
            )
            return

        compile_result = subprocess.run(
            ["javac", script_path],
            cwd=user_folder,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if compile_result.returncode != 0:
            output = (compile_result.stderr or compile_result.stdout or "Unknown compile error")[-3500:]
            bot.reply_to(message_obj_for_reply, f"❌ Java compile failed:\n{output}")
            return

        log_file_path = os.path.join(
            user_folder, f"{os.path.splitext(file_name)[0]}.log"
        )
        log_file = open(log_file_path, "w", encoding="utf-8", errors="replace")
        process = subprocess.Popen(
            ["java", "-cp", user_folder, class_name],
            cwd=user_folder,
            stdout=log_file,
            stderr=log_file,
            stdin=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        bot_scripts[script_key] = {
            "process": process,
            "log_file": log_file,
            "file_name": file_name,
            "chat_id": message_obj_for_reply.chat.id,
            "script_owner_id": script_owner_id,
            "start_time": datetime.now(),
            "user_folder": user_folder,
            "type": "java",
            "script_key": script_key,
        }
        bot.reply_to(
            message_obj_for_reply,
            f"✅ Java script '{file_name}' started!\n🆔 PID: {process.pid}",
        )
    except Exception as exc:
        if _is_no_space_error(exc):
            _handle_no_space_error("starting Java script", message_obj_for_reply.chat.id)
        else:
            logger.error("Error starting Java script %s: %s", file_name, exc, exc_info=True)
            bot.reply_to(message_obj_for_reply, f"❌ Failed to start Java script:\n{exc}")
        if process is not None and process.poll() is None:
            kill_process_tree({
                "process": process,
                "log_file": log_file,
                "script_key": script_key,
            })
        elif log_file and not log_file.closed:
            log_file.close()
        bot_scripts.pop(script_key, None)


def handle_java_file(file_path, script_owner_id, user_folder, file_name, message):
    try:
        save_user_file(script_owner_id, file_name, "java")
        threading.Thread(
            target=run_java_script,
            args=(file_path, script_owner_id, user_folder, file_name, message),
            daemon=True,
        ).start()
    except Exception as exc:
        logger.error("Error processing Java file %s: %s", file_name, exc, exc_info=True)
        bot.reply_to(message, f"❌ Error processing Java file: {exc}")

# --- Send Command and Enhanced Logs Functions ---
def _get_running_script_records(requesting_user_id):
    """Return running scripts visible to the requesting user."""
    running = []
    for script_key, script_info in list(bot_scripts.items()):
        owner_id = script_info.get('script_owner_id')
        file_name = script_info.get('file_name', 'Unknown')
        if owner_id is None:
            continue
        if requesting_user_id != owner_id and requesting_user_id not in admin_ids:
            continue
        if is_bot_running(owner_id, file_name):
            process = script_info.get('process')
            pid = getattr(process, 'pid', None)
            if pid:
                running.append((script_key, script_info, pid))
    return running


def _format_running_scripts_message(requesting_user_id):
    """Build a readable name/PID list for /runningbots."""
    running = _get_running_script_records(requesting_user_id)
    if not running:
        return "❌ No running scripts found."

    lines = ["𝐑𝐀𝐉𝐀𝐍 𝐗 𝐇𝐈𝐍𝐀𝐓𝐀\n\n🟢 Currently running scripts:\n"]
    for _, script_info, pid in sorted(
        running,
        key=lambda item: (str(item[1].get('file_name', '')).lower(), item[2])
    ):
        owner_id = script_info.get('script_owner_id')
        script_type = str(script_info.get('type', 'unknown')).upper()
        start_time = script_info.get('start_time')
        uptime = ""
        if isinstance(start_time, datetime):
            elapsed = max(0, int((datetime.now() - start_time).total_seconds()))
            hours, remainder = divmod(elapsed, 3600)
            minutes, seconds = divmod(remainder, 60)
            uptime = f" | Uptime: {hours:02d}:{minutes:02d}:{seconds:02d}"
        owner_text = (
            f" | User: {user_display_name(owner_id)} [{owner_id}]"
            if requesting_user_id in admin_ids else ""
        )
        lines.append(
            f"📄 {script_info.get('file_name', 'Unknown')}"
            f" ({script_type})\n"
            f"🆔 PID: {pid}{owner_text}{uptime}\n"
        )
    return "\n".join(lines).strip()


def _logic_running_bots(message):
    """Show all running scripts with their names and PIDs."""
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot locked by admin.")
        return
    bot.reply_to(message, _format_running_scripts_message(user_id))


def _logic_stop_bot(message):
    """Stop one visible script by PID or exact file name."""
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot locked by admin.")
        return

    argument = message.text.partition(' ')[2].strip()
    if not argument:
        bot.reply_to(
            message,
            "ℹ️ Use: `/stopbot <PID ya filename>`\n"
            "Example: `/stopbot 2544` or `/stopbot ayushv1.py`",
            parse_mode='Markdown'
        )
        return

    running = _get_running_script_records(user_id)
    matches = []
    if argument.isdigit():
        requested_pid = int(argument)
        matches = [record for record in running if record[2] == requested_pid]
    else:
        requested_name = os.path.basename(argument).casefold()
        matches = [
            record for record in running
            if os.path.basename(str(record[1].get('file_name', '')).casefold())
            == requested_name
        ]

    if not matches:
        bot.reply_to(
            message,
            f"❌ Running script nahi mila: `{argument}`\n"
            "Pehle `/runningbots` se name/PID check karein.",
            parse_mode='Markdown'
        )
        return

    # A filename can exist under multiple users; do not stop an ambiguous
    # process silently. PID is always unambiguous.
    if len(matches) > 1:
        choices = "\n".join(
            f"• `{record[1].get('file_name')}` — PID `{record[2]}`, User `{record[1].get('script_owner_id')}`"
            for record in matches
        )
        bot.reply_to(
            message,
            "⚠️ Same filename multiple users ki running hai. PID se stop karein:\n" + choices,
            parse_mode='Markdown'
        )
        return

    script_key, script_info, pid = matches[0]
    file_name = script_info.get('file_name', 'Unknown')
    try:
        kill_process_tree(script_info)
        bot_scripts.pop(script_key, None)
        logger.info(f"Script {script_key} stopped by command from user {user_id}.")
        bot.reply_to(
            message,
            f"🛑 Script `{file_name}` stopped successfully.\n🆔 PID: {pid}",
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error stopping {script_key} by command: {e}", exc_info=True)
        bot.reply_to(message, f"❌ Script stop karne mein error: {e}")


def _logic_send_command(message):
    """Handle send command functionality"""
    user_id = message.from_user.id
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot locked by admin.")
        return
        
    bot.reply_to(message, "🎀 HINATA X RAJAN 🌷\n\n🛰 Send Command", reply_markup=create_send_command_menu())

def send_to_process_init(message):
    """Initialize process for sending command to a running script"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    # Get user's running processes
    user_running_scripts = []
    for script_key, script_info in bot_scripts.items():
        script_owner_id = script_info['script_owner_id']
        if (user_id == script_owner_id or user_id in admin_ids) and is_bot_running(script_owner_id, script_info['file_name']):
            user_running_scripts.append((script_key, script_info))
    
    if not user_running_scripts:
        bot.reply_to(message, "❌ No running scripts found.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for script_key, script_info in user_running_scripts:
        btn_text = f"{script_info['file_name']} (User: {script_info['script_owner_id']})"
        markup.add(types.InlineKeyboardButton(
            btn_text[:60],
            callback_data=make_process_callback(script_key)
        ))
    
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='send_command'))
    bot.reply_to(message, "📝 Select a running script to send command to:", reply_markup=markup)

def process_send_command(message, script_key):
    """Process the actual command to send to the script"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if script_key not in bot_scripts:
        bot.reply_to(message, "❌ Script no longer running.")
        return
    
    script_info = bot_scripts[script_key]
    command_text = message.text
    
    try:
        process = script_info['process']
        if process and process.poll() is None:
            # Send command to process stdin
            process.stdin.write(command_text + '\n')
            process.stdin.flush()
            bot.reply_to(message, f"✅ Command sent to `{script_info['file_name']}`:\n`{command_text}`", parse_mode='Markdown')
            
            # Wait a bit and check if process is still running
            time.sleep(1)
            if process.poll() is not None:
                bot.reply_to(message, f"⚠️ Script `{script_info['file_name']}` stopped after receiving command.")
        else:
            bot.reply_to(message, f"❌ Script `{script_info['file_name']}` is not running.")
    except Exception as e:
        logger.error(f"Error sending command to {script_key}: {e}")
        bot.reply_to(message, f"❌ Error sending command: {str(e)}")

def view_all_logs(message):
    """Show all available logs for user"""
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    user_logs = []
    
    # Get user's folder and all log files
    user_folder = get_user_folder(user_id)
    if os.path.exists(user_folder):
        for file in os.listdir(user_folder):
            if file.endswith('.log'):
                log_path = os.path.join(user_folder, file)
                file_size = os.path.getsize(log_path)
                user_logs.append((file, file_size, log_path))
    
    if not user_logs:
        bot.reply_to(message, "📜 No log files found.")
        return
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    for log_file, size, log_path in sorted(user_logs):
        size_kb = size / 1024
        btn_text = f"{log_file} ({size_kb:.1f} KB)"
        markup.add(types.InlineKeyboardButton(
            btn_text[:60],
            callback_data=make_file_callback('viewlog', user_id, log_file)
        ))
    
    markup.add(types.InlineKeyboardButton("🔙 Back", callback_data='send_command'))
    bot.reply_to(message, "🎀 HINATA X RAJAN 🌷\n\n📜 Available Log Files:", reply_markup=markup)

def send_log_file(message, log_path, log_filename):
    """Send log file as document"""
    try:
        file_size = os.path.getsize(log_path)
        if file_size > 50 * 1024 * 1024:  # 50MB limit
            bot.reply_to(message, f"❌ Log file too large ({file_size/1024/1024:.1f} MB). Maximum 50MB.")
            return
        
        with open(log_path, 'rb') as log_file:
            bot.send_document(message.chat.id, log_file, caption=f"📜 {log_filename}")
            
    except Exception as e:
        logger.error(f"Error sending log file {log_path}: {e}")
        bot.reply_to(message, f"❌ Error sending log file: {str(e)}")

# --- Logic Functions (called by commands and text handlers) ---
def _logic_send_welcome(message, user=None):
    """Send the main menu for the actual Telegram user.

    CallbackQuery.message.from_user is the bot itself.  A force-join
    callback must therefore pass call.from_user explicitly; otherwise every
    non-owner is checked using the bot's ID and can never pass verification.
    """
    actor = user or message.from_user
    user_id = actor.id
    chat_id = message.chat.id
    user_name = actor.first_name or "User"
    user_username = actor.username
    save_user_profile(user_id, user_name, user_username)

    logger.info(f"Welcome request from user_id: {user_id}, username: @{user_username}")

# 🔒 Force Join Check
    if user_id not in admin_ids:
        if not is_user_joined_all(user_id):
            send_force_join_msg(chat_id)
            return

    if bot_locked and user_id not in admin_ids:
        bot.send_message(chat_id, "⚠️ Bot locked by admin. Try later.")
        return

    user_bio = "Could not fetch bio"
    try: user_bio = bot.get_chat(user_id).bio or "No bio"
    except Exception: pass

    if user_id not in active_users:
        add_active_user(user_id)
        try:
            owner_notification = (f"🎉 New user!\n👤 Name: {user_name}\n✳️ User: @{user_username or 'N/A'}\n"
                                  f"🆔 ID: `{user_id}`\n📝 Bio: {user_bio}")
            bot.send_message(OWNER_ID, owner_notification, parse_mode='Markdown')
        except Exception as e: logger.error(f"⚠️ Failed to notify owner about new user {user_id}: {e}")

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
    expiry_info = ""
    if user_id == OWNER_ID: user_status = "🤍 Owner"
    elif user_id in admin_ids: user_status = "🌙 Admin"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "⭐ Premium"; days_left = (expiry_date - datetime.now()).days
            expiry_info = f"\n⏳ Subscription expires in: {days_left} days"
        else: user_status = "🆓 Free User (Expired Sub)"; remove_subscription_db(user_id)
    else: user_status = "🆓 Free User"

    welcome_msg_text = (f"🎀 𝐇𝐈𝐍𝐀𝐓𝐀 × 𝐑𝐀𝐉𝐀𝐍 🌷\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"🌸 𝐖𝐞𝐥𝐜𝐨𝐦𝐞, 𝐑ᴀᴊᴀɴ 𝐖ɪɴ𝐒~! ♡\n\n"
                        f"🆔 𝐔𝐬𝐞𝐫 𝐈𝐃 ➜ `{user_id}`\n"
                        f"✳️ 𝐔𝐬ᴇʀɴᴀᴍᴇ ➜ `@{user_username or 'Not set'}`\n"
                        f"🔰 𝐒ᴛᴀᴛᴜs ➜ {user_status}{expiry_info}\n"
                        f"📁 𝐅ɪʟᴇs ➜ `{current_files} / {limit_str}`\n\n"
                        f"🤖 𝐇ᴏsᴛ & 𝐑ᴜɴ 𝐘ᴏᴜʀ 𝐒ᴄʀɪᴘᴛs\n"
                        f"╰┈➤ 🐍 `.py`  •  🟨 `.js`  •  ☕ `.java`  •  📦 `.zip`\n\n"
                        f"✨ 𝑷𝒓𝒆𝒎𝒊𝒖𝒎 𝑯𝒐𝒔𝒕𝒊𝒏𝒈 𝑪𝒐𝒏𝒕𝒓𝒐𝒍 𝑷𝒂𝒏𝒆𝒍\n"
                        f"━━━━━━━━━━━━━━━━━━\n"
                        f"👇 𝐂ʜᴏᴏsᴇ 𝐀ɴ 𝐎ᴘᴛɪᴏɴ 𝐁ᴇʟᴏᴡ 🎀")
    main_reply_markup = create_reply_keyboard_main_menu(user_id)
    try:
        welcome_video_file_id = bot_settings.get('welcome_video_file_id')
        if welcome_video_file_id:
            bot.send_video(
                chat_id,
                welcome_video_file_id,
                caption=welcome_msg_text,
                reply_markup=main_reply_markup,
                parse_mode='Markdown',
            )
        else:
            bot.send_message(
                chat_id,
                welcome_msg_text,
                reply_markup=main_reply_markup,
                parse_mode='Markdown',
            )
    except Exception as e:
        logger.error(f"Error sending welcome to {user_id}: {e}", exc_info=True)
        if welcome_video_file_id:
            try:
                bot.send_message(
                    chat_id,
                    welcome_msg_text,
                    reply_markup=main_reply_markup,
                    parse_mode='Markdown',
                )
            except Exception as fallback_e:
                logger.error(f"Fallback send_message failed for {user_id}: {fallback_e}")

def _logic_updates_channel(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('🌷 𝐎𝐩𝐞𝐧 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 𝐂𝐡𝐚𝐧𝐧𝐞𝐥', url=UPDATE_CHANNEL))
    bot.reply_to(
        message,
        "🎀 𝐇𝐈𝐍𝐀𝐓𝐀 × 𝐑𝐀𝐉𝐀𝐍 🌷\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📢 𝐎𝐟𝐟𝐢𝐜𝐢𝐚𝐥 𝐔𝐩𝐝𝐚𝐭𝐞𝐬\n\n"
        "✨ New features, maintenance alerts aur important announcements "
        "yahin milenge.",
        reply_markup=markup
    )

def _logic_upload_file(message):
    user_id = message.from_user.id
    save_user_profile(user_id, message.from_user.first_name, message.from_user.username)
    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot locked by admin, cannot accept files.")
        return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    pending_count = get_user_pending_file_count(user_id)
    if current_files + pending_count >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.reply_to(message, f"⚠️ File limit ({current_files}/{limit_str}) reached. Delete files first.")
        return
    bot.reply_to(
        message,
        "🎀 𝐇𝐈𝐍𝐀𝐓𝐀 × 𝐑𝐀𝐉𝐀𝐍 🌷\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "📤 𝐔𝐏𝐋𝐎𝐀𝐃 𝐘𝐎𝐔𝐑 𝐒𝐂𝐑𝐈𝐏𝐓\n\n"
        "🐍 𝐏𝐘𝐓𝐇𝐎𝐍   •   🟨 𝐉𝐀𝐕𝐀𝐒𝐂𝐑𝐈𝐏𝐓   •   📦 𝐙𝐈𝐏\n\n"
        "╭──────────────────╮\n"
        "💌 𝐀𝐏𝐍𝐈 𝐅𝐈𝐋𝐄 𝐒𝐄𝐍𝐃 𝐊𝐀𝐑𝐎\n"
        "⚡ 𝐀𝐔𝐓𝐎𝐌𝐀𝐓𝐈𝐂 𝐏𝐑𝐎𝐂𝐄𝐒𝐒𝐈𝐍𝐆\n"
        "💾 𝐒𝐀𝐕𝐄 & 𝐑𝐔𝐍 𝐀𝐔𝐓𝐎𝐌𝐀𝐓𝐈𝐂𝐀𝐋𝐋𝐘\n"
        "╰──────────────────╯\n\n"
        "🤍 𝐉𝐔𝐒𝐓 𝐒𝐄𝐍𝐃 𝐘𝐎𝐔𝐑 𝐒𝐂𝐑𝐈𝐏𝐓… 🌙",
        parse_mode='Markdown'
    )

def _logic_check_files(message):
    user_id = message.from_user.id
    visible_users = sorted(user_files) if user_id in admin_ids else [user_id]
    file_rows = [
        (owner_id, file_name, file_type)
        for owner_id in visible_users
        for file_name, file_type in user_files.get(owner_id, [])
    ]
    if not file_rows:
        bot.reply_to(message, "𝐑𝐀𝐉𝐀𝐍 𝐗 𝐇𝐈𝐍𝐀𝐓𝐀\n\n📂 My Files\n(No files uploaded yet)")
        return
    markup = types.InlineKeyboardMarkup(row_width=1)
    for owner_id, file_name, file_type in sorted(file_rows, key=lambda row: (user_display_name(row[0]).casefold(), row[1].casefold())):
        is_running = is_bot_running(owner_id, file_name)
        status_icon = "🟢 Running" if is_running else "🔴 Stopped"
        owner_text = f" • {user_display_name(owner_id)} [{owner_id}]" if user_id in admin_ids else ""
        btn_text = f"{file_name} ({file_type}) - {status_icon}{owner_text}"
        markup.add(types.InlineKeyboardButton(btn_text[:60], callback_data=make_file_callback('file', owner_id, file_name)))
    bot.reply_to(message, "𝐑𝐀𝐉𝐀𝐍 𝐗 𝐇𝐈𝐍𝐀𝐓𝐀\n\n📂 My Files\nClick a script to manage it.", reply_markup=markup, parse_mode='Markdown')

def _format_runtime(start_time):
    elapsed = max(0, int((datetime.now() - start_time).total_seconds()))
    days, remainder = divmod(elapsed, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f'{days}d {hours:02d}h {minutes:02d}m {seconds:02d}s'

def _status_level(user_id):
    expire_subscription_if_needed(user_id)
    if user_id == OWNER_ID:
        return '👑 𝐎ᴡɴᴇʀ'
    if user_id in admin_ids:
        return '🌙 𝐀ᴅᴍɪɴ'
    if user_id in user_subscriptions:
        return '⭐ 𝐏ʀᴇᴍɪᴜᴍ'
    return '🆓 𝐅ʀᴇᴇ'

def _bot_status_text(user_id, response_ms):
    return (
        '🌷💗 𝐇𝐈𝐍𝐀𝐓𝐀 — 𝐁𝐎𝐓 Sᴛᴀᴛᴜs 💗🌷\n'
        '━━━━━━━━━━━━━━━━━━\n\n'
        '⚡ 𝐁ᴏᴛ Sᴘᴇᴇᴅ & Sᴛᴀᴛᴜs\n\n'
        f'⏱️ 𝐀𝐏𝐈 Rᴇsᴘᴏɴsᴇ: `{response_ms} ms`\n'
        f'🚦 𝐁ᴏᴛ Sᴛᴀᴛᴜs: {"🔒 𝐋ᴏᴄᴋᴇᴅ" if bot_locked else "🔓 𝐔ɴʟᴏᴄᴋᴇᴅ"}\n'
        f'👤 𝐘ᴏᴜʀ Lᴇᴠᴇʟ: {_status_level(user_id)}\n\n'
        f'⏱️ 𝐁ᴏᴛ Rᴜɴᴛɪᴍᴇ:\n`{_format_runtime(BOT_START_TIME)}`\n\n'
        f'🌷 𝐁ᴏᴛ Sᴛᴀʀᴛᴇᴅ:\n`{BOT_START_TIME:%d %b %Y • %I:%M %p}`\n\n'
        '✨ 𝐅ᴀsᴛ • 𝐒ᴇᴄᴜʀᴇ • 𝐀ʟᴡᴀʏs Rᴇᴀᴅʏ\n'
        '━━━━━━━━━━━━━━━━━━'
    )

def _logic_bot_speed(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    wait_msg = bot.reply_to(message, "🏃 Testing speed...")
    try:
        start_time_ping = time.perf_counter()
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.perf_counter() - start_time_ping) * 1000, 2)
        bot.edit_message_text(
            _bot_status_text(user_id, response_time),
            chat_id, wait_msg.message_id, parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error during speed test (cmd): {e}", exc_info=True)
        bot.edit_message_text("❌ Error during speed test.", chat_id, wait_msg.message_id)
    return

    # Legacy fallback retained below for compatibility with older edits.
    start_time_ping = time.time()
    wait_msg = bot.reply_to(message, "🏃 Testing speed...")
    try:
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.time() - start_time_ping) * 1000, 2)
        status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
        if user_id == OWNER_ID: user_level = "🤍 Owner"
        elif user_id in admin_ids: user_level = "🌙 Admin"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now(): user_level = "⭐ Premium"
        else: user_level = "🆓 Free User"
        speed_msg = (
            "⚡ 𝐁ᴏᴛ Sᴘᴇᴇᴅ & Sᴛᴀᴛᴜs\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            f"⏱️ 𝐀𝐏𝐈 𝐑𝐞𝐬𝐩𝐨𝐧𝐬𝐞: `{response_time} ms`\n"
            f"🚦 𝐁𝐨𝐭 𝐒𝐭𝐚𝐭𝐮𝐬: {status}\n"
            f"👤 𝐘𝐨𝐮𝐫 𝐋𝐞𝐯𝐞𝐥: {user_level}\n\n"
            "✨ Fast • Secure • Always Ready"
        )
        bot.edit_message_text(speed_msg, chat_id, wait_msg.message_id, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error during speed test (cmd): {e}", exc_info=True)
        bot.edit_message_text("❌ Error during speed test.", chat_id, wait_msg.message_id)

def _logic_contact_owner(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('📞 Contact Owner', url=f'https://t.me/{YOUR_USERNAME.replace("@", "")}'))
    bot.reply_to(message, "Click to contact Owner:", reply_markup=markup)

# --- Admin Logic Functions ---
def _logic_subscriptions_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    bot.reply_to(message, "🎀 HINATA X RAJAN 🌷\n\n💎 Subscription Management\nUse the premium controls below.", reply_markup=create_subscription_menu())

def _logic_user_subscription(message):
    user_id = message.from_user.id
    expire_subscription_if_needed(user_id)
    sub = user_subscriptions.get(user_id)
    if sub and sub.get('expiry') and sub['expiry'] > datetime.now():
        plan_label = PREMIUM_PLANS.get(sub.get('plan'), {}).get(
            'name', sub.get('plan', 'Premium')
        )
        current_plan = (
            f'{plan_label}\n'
            f'⏳ Expires: {sub["expiry"]:%d %b %Y • %I:%M %p}'
        )
    else:
        current_plan = '𝐅ʀᴇᴇ • 𝟏 𝐅ɪʟᴇ'
    bot.reply_to(
        message,
        '🌷💗 𝐇𝐈𝐍𝐀𝐓𝐀 — 𝐒ᴜʙsᴄʀɪᴘᴛɪᴏɴ 💗🌷\n'
        '━━━━━━━━━━━━━━━━━━\n\n'
        '💳 𝐒ᴇʟᴇᴄᴛ 𝐀 𝐏ʟᴀɴ 𝐁ᴇʟᴏᴡ 𝐓ᴏ 𝐂ᴏɴᴛɪɴᴜᴇ.\n\n'
        f'🆓 𝐂ᴜʀʀᴇɴᴛ 𝐏ʟᴀɴ:\n{current_plan}\n\n'
        '🌷 𝐔ᴘɢʀᴀᴅᴇ 𝐓ᴏ 𝐏ʀᴇᴍɪᴜᴍ\n'
        '💗 𝐆ᴇᴛ Mᴏʀᴇ Fɪʟᴇs & 𝐏ʟᴀɴ-𝐁ᴀsᴇᴅ Vᴀʟɪᴅɪᴛʏ\n\n'
        '━━━━━━━━━━━━━━━━━━',
        reply_markup=premium_panel_markup()
    )

def _logic_statistics(message, actor_id=None):
    user_id = actor_id if actor_id is not None else message.from_user.id
    total_users = len(active_users)
    total_files_records = sum(len(files) for files in user_files.values())

    running_bots_count = 0
    user_running_bots = 0

    for script_key_iter, script_info_iter in list(bot_scripts.items()):
        s_owner_id, _ = script_key_iter.split('_', 1)
        if is_bot_running(int(s_owner_id), script_info_iter['file_name']):
            running_bots_count += 1
            if int(s_owner_id) == user_id:
                user_running_bots +=1

    stats_msg_base = (f"📊 Bot Statistics:\n\n"
                      f"👥 Total Users: {total_users}\n"
                      f"📂 Total File Records: {total_files_records}\n"
                      f"🟢 Total Active Bots: {running_bots_count}\n")

    if user_id in admin_ids:
        stats_msg_admin = (f"🔒 Bot Status: {'🔴 Locked' if bot_locked else '🟢 Unlocked'}\n"
                           f"🤖 Your Running Bots: {user_running_bots}")
        stats_msg = stats_msg_base + stats_msg_admin
    else:
        stats_msg = stats_msg_base + f"🤖 Your Running Bots: {user_running_bots}"

    bot.reply_to(message, stats_msg)

def _logic_broadcast_init(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    msg = bot.reply_to(message, "📢 Send message to broadcast to all active users.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_broadcast_message)

def _logic_toggle_lock_bot(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    global bot_locked
    bot_locked = not bot_locked
    status = "locked" if bot_locked else "unlocked"
    logger.warning(f"Bot {status} by Admin {message.from_user.id} via command/button.")
    bot.reply_to(message, f"🔒 Bot has been {status}.")

def _logic_admin_panel(message):
    if message.from_user.id not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return
    bot.reply_to(
        message,
        '🌷💗 𝐇𝐈𝐍𝐀𝐓𝐀 — 𝐀ᴅᴍɪɴ Pᴀɴᴇʟ 💗🌷\n'
        '━━━━━━━━━━━━━━━━━━\n\n'
        '📊 𝐒ᴛᴀᴛɪsᴛɪᴄs\n📤 𝐔ᴘʟᴏᴀᴅ Sᴄʀɪᴘᴛ\n'
        '🟢 𝐑ᴜɴɴɪɴɢ Bᴏᴛs\n⚡ 𝐁ᴏᴛ Sᴛᴀᴛᴜs\n'
        '💳 𝐒ᴜʙsᴄʀɪᴘᴛɪᴏɴs\n📢 𝐁ʀᴏᴀᴅᴄᴀsᴛ\n'
        '🔒 𝐋ᴏᴄᴋ Bᴏᴛ\n🟢 𝐑ᴜɴ Aʟʟ Sᴄʀɪᴘᴛs\n'
        '🛰 𝐒ᴇɴᴅ Cᴏᴍᴍᴀɴᴅ\n👑 𝐀ᴅᴍɪɴ Pᴀɴᴇʟ\n'
        '💌 𝐂ᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ\n\n'
        '━━━━━━━━━━━━━━━━━━',
                 reply_markup=create_admin_panel())

def _logic_run_all_scripts(message_or_call):
    if isinstance(message_or_call, telebot.types.Message):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.chat.id
        reply_func = lambda text, **kwargs: bot.reply_to(message_or_call, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call
    elif isinstance(message_or_call, telebot.types.CallbackQuery):
        admin_user_id = message_or_call.from_user.id
        admin_chat_id = message_or_call.message.chat.id
        bot.answer_callback_query(message_or_call.id)
        reply_func = lambda text, **kwargs: bot.send_message(admin_chat_id, text, **kwargs)
        admin_message_obj_for_script_runner = message_or_call.message 
    else:
        logger.error("Invalid argument for _logic_run_all_scripts")
        return

    if admin_user_id not in admin_ids:
        reply_func("⚠️ Admin permissions required.")
        return

    reply_func("⏳ Starting process to run all user scripts. This may take a while...")
    logger.info(f"Admin {admin_user_id} initiated 'run all scripts' from chat {admin_chat_id}.")

    started_count = 0; attempted_users = 0; skipped_files = 0; error_files_details = []

    all_user_files_snapshot = dict(user_files)

    for target_user_id, files_for_user in all_user_files_snapshot.items():
        if not files_for_user: continue
        attempted_users += 1
        logger.info(f"Processing scripts for user {target_user_id}...")
        user_folder = get_user_folder(target_user_id)
        for file_name, file_type in files_for_user:
            if not is_bot_running(target_user_id, file_name):
                file_path = os.path.join(user_folder, file_name)
                if os.path.exists(file_path):
                    logger.info(f"Admin {admin_user_id} attempting to start '{file_name}' ({file_type}) for user {target_user_id}.")
                    try:
                        if file_type == 'py':
                            threading.Thread(target=run_script, args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        elif file_type == 'js':
                            threading.Thread(target=run_js_script, args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        elif file_type == 'java':
                            threading.Thread(target=run_java_script, args=(file_path, target_user_id, user_folder, file_name, admin_message_obj_for_script_runner)).start()
                            started_count += 1
                        else:
                            logger.warning(f"Unknown file type '{file_type}' for {file_name} (user {target_user_id}). Skipping.")
                            error_files_details.append(f"`{file_name}` (User {target_user_id}) - Unknown type")
                            skipped_files += 1
                        time.sleep(0.7)
                    except Exception as e:
                        logger.error(f"Error queueing start for '{file_name}' (user {target_user_id}): {e}")
                        error_files_details.append(f"`{file_name}` (User {target_user_id}) - Start error")
                        skipped_files += 1
                else:
                    logger.warning(f"File '{file_name}' for user {target_user_id} not found at '{file_path}'. Skipping.")
                    error_files_details.append(f"`{file_name}` (User {target_user_id}) - File not found")
                    skipped_files += 1

    summary_msg = (f"✅ All Users' Scripts - Processing Complete:\n\n"
                   f"▶️ Attempted to start: {started_count} scripts.\n"
                   f"👥 Users processed: {attempted_users}.\n")
    if skipped_files > 0:
        summary_msg += f"⚠️ Skipped/Error files: {skipped_files}\n"
        if error_files_details:
             summary_msg += "Details (first 5):\n" + "\n".join([f"  - {err}" for err in error_files_details[:5]])
             if len(error_files_details) > 5: summary_msg += "\n  ... and more (check logs)."

    reply_func(summary_msg, parse_mode='Markdown')
    logger.info(f"Run all scripts finished. Admin: {admin_user_id}. Started: {started_count}. Skipped/Errors: {skipped_files}")

# --- Command Handlers & Text Handlers for ReplyKeyboard ---
@bot.message_handler(commands=['start', 'help'])
def command_send_welcome(message):
    """Never leave /start silent if one of the optional checks fails."""
    try:
        _logic_send_welcome(message)
    except Exception as e:
        user_id = getattr(getattr(message, 'from_user', None), 'id', 'unknown')
        logger.error("Unhandled /start error for user %s: %s", user_id, e, exc_info=True)
        try:
            bot.reply_to(
                message,
                "⚠️ Start karte waqt temporary error aaya. "
                "Please 10 seconds baad /start dobara bhejein."
            )
        except Exception as reply_error:
            logger.error("Could not send /start error message to %s: %s", user_id, reply_error)

@bot.message_handler(commands=['status'])
def command_show_status(message):
    if _force_join_guard(message):
        _logic_statistics(message)

BUTTON_TEXT_TO_LOGIC = {
    "🌷 𝐔𝐩𝐝𝐚𝐭𝐞𝐬 𝐂𝐡𝐚𝐧𝐧𝐞𝐥": _logic_updates_channel,
    "💎 𝐏ᴀɪᴅ 𝐏ᴀɴᴇʟ": _logic_paid_panel,
    "📤 𝐔𝐩𝐥𝐨𝐚𝐝 𝐒𝐜𝐫𝐢𝐩𝐭": _logic_upload_file,
    "📂 𝐌ʏ Fɪʟᴇs": _logic_check_files,
    "🟢 𝐑ᴜɴɴɪɴɢ Bᴏᴛs": _logic_running_bots,
    "⚡ 𝐁ᴏᴛ Sᴛᴀᴛᴜs": _logic_bot_speed,
    "🛰 𝐒ᴇɴᴅ Cᴏᴍᴍᴀɴᴅ": _logic_send_command,
    "💌 𝐂ᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ": _logic_contact_owner,
    "📊 𝐒ᴛᴀᴛɪsᴛɪᴄs": _logic_statistics,
    "💳 𝐒ᴜʙsᴄʀɪᴘᴛɪᴏɴs": lambda message: (
        _logic_subscriptions_panel(message)
        if message.from_user.id in admin_ids
        else _logic_user_subscription(message)
    ),
    "📢 𝐁ʀᴏᴀᴅᴄᴀsᴛ": _logic_broadcast_init,
    "🔒 𝐋ᴏᴄᴋ Bᴏᴛ": _logic_toggle_lock_bot,
    "🟢 𝐑ᴜɴ Aʟʟ Sᴄʀɪᴘᴛs": _logic_run_all_scripts,
    "👑 𝐀ᴅᴍɪɴ Pᴀɴᴇʟ": _logic_admin_panel,
}

# Keep reply-keyboard compatibility with older/plain-text keyboards already
# visible in users' chats. Telegram sends the exact button label as message text.
BUTTON_TEXT_TO_LOGIC.update({
    "🌷 Updates Channel": _logic_updates_channel,
    "💎 Paid Panel": _logic_paid_panel,
    "📤 Upload Script": _logic_upload_file,
    "📂 My Files": _logic_check_files,
    "🟢 Running Bots": _logic_running_bots,
    "⚡ Bot Status": _logic_bot_speed,
    "📊 Statistics": _logic_statistics,
    "💳 Subscriptions": lambda message: (
        _logic_subscriptions_panel(message)
        if message.from_user.id in admin_ids
        else _logic_user_subscription(message)
    ),
    "🛰 Send Command": _logic_send_command,
    "💌 Contact Owner": _logic_contact_owner,
    "📢 Broadcast": _logic_broadcast_init,
    "🔒 Lock Bot": _logic_toggle_lock_bot,
    "🟢 Run All Scripts": _logic_run_all_scripts,
    "👑 Admin Panel": _logic_admin_panel,
})

BUTTON_EMOJI_TO_LOGIC = {
    "🌷": _logic_updates_channel,
    "💎": _logic_paid_panel,
    "📤": _logic_upload_file,
    "📂": _logic_check_files,
    "🟢": _logic_running_bots,
    "⚡": _logic_bot_speed,
    "📊": _logic_statistics,
    "💳": lambda message: (
        _logic_subscriptions_panel(message)
        if message.from_user.id in admin_ids
        else _logic_user_subscription(message)
    ),
    "🛰": _logic_send_command,
    "💌": _logic_contact_owner,
    "📢": _logic_broadcast_init,
    "🔒": _logic_toggle_lock_bot,
    "👑": _logic_admin_panel,
}


def _resolve_button_logic(text):
    """Resolve exact, plain, and Telegram fancy-font reply labels."""
    text = (text or "").strip()
    if text in BUTTON_TEXT_TO_LOGIC:
        return BUTTON_TEXT_TO_LOGIC[text]
    for emoji, logic_func in BUTTON_EMOJI_TO_LOGIC.items():
        if text.startswith(emoji):
            return logic_func
    return None


@bot.message_handler(func=lambda message: _resolve_button_logic(message.text) is not None)
def handle_button_text(message):
    if not _force_join_guard(message):
        return
    logic_func = _resolve_button_logic(message.text)
    if logic_func: logic_func(message)
    else: logger.warning(f"Button text '{message.text}' matched but no logic func.")

@bot.message_handler(commands=['updateschannel'])
def command_updates_channel(message):
    if _force_join_guard(message):
        _logic_updates_channel(message)
@bot.message_handler(commands=['uploadfile'])
def command_upload_file(message):
    if _force_join_guard(message):
        _logic_upload_file(message)
@bot.message_handler(commands=['checkfiles'])
def command_check_files(message):
    if _force_join_guard(message):
        _logic_check_files(message)
@bot.message_handler(commands=['runningbots', 'running'])
def command_running_bots(message):
    if _force_join_guard(message):
        _logic_running_bots(message)
@bot.message_handler(commands=['stopbot'])
def command_stop_bot(message):
    if _force_join_guard(message):
        _logic_stop_bot(message)
@bot.message_handler(commands=['botspeed'])
def command_bot_speed(message):
    if _force_join_guard(message):
        _logic_bot_speed(message)
@bot.message_handler(commands=['sendcommand'])  # Added Send Command
def command_send_command(message):
    if _force_join_guard(message):
        _logic_send_command(message)
@bot.message_handler(commands=['contactowner'])
def command_contact_owner(message):
    if _force_join_guard(message):
        _logic_contact_owner(message)
@bot.message_handler(commands=['subscriptions'])
def command_subscriptions(message):
    if _force_join_guard(message):
        _logic_subscriptions_panel(message)
@bot.message_handler(commands=['statistics'])
def command_statistics(message):
    if _force_join_guard(message):
        _logic_statistics(message)
@bot.message_handler(commands=['broadcast'])
def command_broadcast(message):
    if _force_join_guard(message):
        _logic_broadcast_init(message)
@bot.message_handler(commands=['lockbot']) 
def command_lock_bot(message):
    if _force_join_guard(message):
        _logic_toggle_lock_bot(message)
@bot.message_handler(commands=['adminpanel'])
def command_admin_panel(message):
    if _force_join_guard(message):
        _logic_admin_panel(message)
@bot.message_handler(commands=['runningallcode'])
def command_run_all_code(message):
    if _force_join_guard(message):
        _logic_run_all_scripts(message)

@bot.message_handler(commands=['ping'])
def ping(message):
    if not _force_join_guard(message):
        return
    start_ping_time = time.time() 
    msg = bot.reply_to(message, "Pong!")
    latency = round((time.time() - start_ping_time) * 1000, 2)
    bot.edit_message_text(f"Pong! Latency: {latency} ms", message.chat.id, msg.message_id)


# --- Admin-only storage commands ---
def _require_storage_admin(message):
    if getattr(getattr(message, "from_user", None), "id", None) not in admin_ids:
        bot.reply_to(message, "⚠️ Admin permissions required.")
        return False
    return True


@bot.message_handler(commands=['disk', 'storage'])
def command_disk(message):
    if not _require_storage_admin(message):
        return
    try:
        usage, cleanup_result = _storage_check_once(notify=True)
        text = (
            "💾 Disk Storage\n\n"
            f"💾 Total Disk: {_format_bytes(usage['total'])}\n"
            f"📦 Used Disk: {_format_bytes(usage['used'])}\n"
            f"🟢 Free Disk: {_format_bytes(usage['free'])}\n"
            f"📊 Usage Percentage: {usage['percent']:.1f}%"
        )
        if cleanup_result:
            text += (
                "\n\n🧹 Critical threshold cleanup:\n"
                f"Files cleaned: {cleanup_result['files_cleaned']}\n"
                f"Space freed: {_format_bytes(cleanup_result['bytes_freed'])}"
            )
        if usage["percent"] > 90:
            text += "\n🚨 Critical: free space is still low after safe cleanup."
        elif usage["percent"] > 80:
            text += "\n⚠️ Warning: disk usage is above 80%."
        bot.reply_to(message, text)
    except Exception as exc:
        logger.error("Admin /disk failed: %s", exc, exc_info=True)
        bot.reply_to(message, "❌ Could not read disk usage safely.")


@bot.message_handler(commands=['cleanup'])
def command_cleanup(message):
    if not _require_storage_admin(message):
        return
    try:
        result = cleanup_temporary_downloads()
        usage = _disk_usage()
        bot.reply_to(
            message,
            "🧹 Safe temporary cleanup complete\n\n"
            f"📁 Files cleaned: {result['files_cleaned']}\n"
            f"💾 Space freed: {_format_bytes(result['bytes_freed'])}\n"
            f"🟢 Remaining free space: {_format_bytes(usage['free'])}\n"
            f"📊 Usage: {usage['percent']:.1f}%\n"
            "✅ Uploaded files, databases, configs and running bots were not touched."
        )
    except Exception as exc:
        logger.error("Admin /cleanup failed: %s", exc, exc_info=True)
        bot.reply_to(message, "❌ Cleanup failed safely; no protected path was touched.")


@bot.message_handler(commands=['cleanup_status'])
def command_cleanup_status(message):
    if not _require_storage_admin(message):
        return
    try:
        bot.reply_to(message, _cleanup_status_text())
    except Exception as exc:
        logger.error("Admin /cleanup_status failed: %s", exc, exc_info=True)
        bot.reply_to(message, "❌ Could not read cleanup status.")


# --- Owner-only Python Package Management ---
def _pip_usage_text():
    return (
        "📦 Owner-only package management\n\n"
        "/pip install <package>\n"
        "/pip uninstall <package>\n"
        "/pip list\n"
        "/pip show <package>\n"
        "/pip freeze"
    )


def _parse_pip_command(message):
    """Parse one safe package-management command; never accept shell syntax."""
    try:
        parts = shlex.split((message.text or "").strip(), posix=True)
    except ValueError:
        return None, None, "❌ Invalid command quoting."

    if not parts or parts[0].lower().split("@", 1)[0] != "/pip":
        return None, None, _pip_usage_text()

    if len(parts) < 2:
        return None, None, _pip_usage_text()

    action = parts[1].lower()
    args = parts[2:]
    if action in {"list", "freeze"}:
        if args:
            return None, None, _pip_usage_text()
        return action, None, None

    if action not in {"install", "uninstall", "show"} or len(args) != 1:
        return None, None, _pip_usage_text()

    package = args[0].strip()
    if (
        len(package) > 128
        or package.startswith("-")
        or not PIP_PACKAGE_PATTERN.fullmatch(package)
    ):
        return (
            None,
            None,
            "❌ Invalid package name. Only a package name/specifier is allowed; "
            "shell flags, paths, URLs and commands are blocked.",
        )
    return action, package, None


def _send_pip_output(chat_id, heading, output, success):
    output = (output or "").strip()
    if len(output) > PIP_OUTPUT_LIMIT:
        output = (
            output[:PIP_OUTPUT_LIMIT]
            + "\n\n...[output truncated for Telegram]"
        )
    status = "✅" if success else "❌"
    text = f"{status} {heading}\n\n{output or '(no output)'}"
    # Telegram messages are limited to 4096 characters.
    for offset in range(0, len(text), 3900):
        bot.send_message(chat_id, text[offset:offset + 3900])


def _pip_worker(chat_id, action, package=None):
    try:
        bot.send_message(
            chat_id,
            f"⏳ Running `{action}`"
            + (f" for `{package}`..." if package else "..."),
            parse_mode="Markdown",
        )
        command = [
            sys.executable,
            "-m",
            "pip",
            action,
            "--disable-pip-version-check",
        ]
        if action == "uninstall":
            command.extend(["--yes", package])
        elif package:
            command.append(package)

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            timeout=300,
            encoding="utf-8",
            errors="replace",
            env={**os.environ, "PYTHONIOENCODING": "utf-8"},
        )
        output = "\n".join(
            part for part in (result.stdout, result.stderr) if part
        )
        if result.returncode != 0 and "no module named pip" in output.lower():
            output = (
                f"pip is not available for interpreter `{sys.executable}`.\n"
                "Install Python with pip enabled, then restart the bot.\n\n"
                + output
            )
        _send_pip_output(
            chat_id,
            f"`python -m pip {action}` finished with exit code {result.returncode}.",
            output,
            result.returncode == 0,
        )
    except subprocess.TimeoutExpired:
        _send_pip_output(
            chat_id,
            f"`python -m pip {action}` timed out after 300 seconds.",
            "The operation was stopped. Check the package or network and try again.",
            False,
        )
    except Exception as exc:
        logger.error("Owner pip operation failed: %s", exc, exc_info=True)
        _send_pip_output(
            chat_id,
            f"`python -m pip {action}` failed.",
            str(exc),
            False,
        )
    finally:
        PIP_OPERATION_LOCK.release()


def _start_pip_operation(chat_id, action, package=None):
    if not PIP_OPERATION_LOCK.acquire(blocking=False):
        bot.send_message(
            chat_id,
            "⏳ Another pip operation is already running. Please wait for it to finish.",
        )
        return False
    threading.Thread(
        target=_pip_worker,
        args=(chat_id, action, package),
        daemon=True,
        name="owner-pip-operation",
    ).start()
    return True


def _pip_confirmation_markup(token):
    markup = InlineKeyboardMarkup(row_width=2)
    markup.add(
        InlineKeyboardButton(
            "✅ Confirm Uninstall",
            callback_data=f"pip_uninstall_confirm:{token}",
        ),
        InlineKeyboardButton(
            "✖️ Cancel",
            callback_data=f"pip_uninstall_cancel:{token}",
        ),
    )
    return markup


@bot.message_handler(commands=["pip"])
def command_pip(message):
    if message.from_user.id != OWNER_ID:
        bot.reply_to(message, "❌ Owner Only")
        return

    action, package, error = _parse_pip_command(message)
    if error:
        bot.reply_to(message, error)
        return

    if action == "uninstall":
        token = hashlib.sha256(
            f"{message.from_user.id}:{package}:{time.time_ns()}".encode()
        ).hexdigest()[:16]
        with PIP_CONFIRM_LOCK:
            pending_pip_uninstalls[token] = {
                "owner_id": message.from_user.id,
                "package": package,
                "expires_at": time.time() + 300,
            }
        bot.reply_to(
            message,
            f"⚠️ Confirm uninstall of `{package}`?\n"
            "This can remove a dependency used by the bot.",
            parse_mode="Markdown",
            reply_markup=_pip_confirmation_markup(token),
        )
        return

    _start_pip_operation(message.chat.id, action, package)


# --- Document (File) Handler with Malware Detection ---
@bot.message_handler(content_types=['document'])
def handle_file_upload_doc(message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    doc = message.document
    if not _force_join_guard(message):
        return
    save_user_profile(user_id, message.from_user.first_name, message.from_user.username)

    logger.info(f"Doc from {user_id}: {doc.file_name} ({doc.mime_type}), Size: {doc.file_size}")

    if bot_locked and user_id not in admin_ids:
        bot.reply_to(message, "⚠️ Bot locked, cannot accept files.")
        return

    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    pending_count = get_user_pending_file_count(user_id)

    if current_files + pending_count >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.reply_to(
            message,
            f"⚠️ File limit ({current_files}/{limit_str}) reached. Pending approvals: {pending_count}."
        )
        return

    file_name = _safe_uploaded_file_name(doc.file_name)

    if not file_name:
        bot.reply_to(message, "⚠️ Invalid or unsafe file name.")
        return

    file_ext = os.path.splitext(file_name)[1].lower()

    if file_ext not in ['.py', '.js', '.zip', '.java']:
        bot.reply_to(
            message,
            "⚠️ Unsupported type! Only `.py`, `.js`, `.java`, `.zip` allowed."
        )
        return

    max_file_size = 20 * 1024 * 1024
    temp_download_path = None

    if doc.file_size > max_file_size:
        bot.reply_to(
            message,
            f"⚠️ File too large (Max: {max_file_size // 1024 // 1024} MB)."
        )
        return

    try:

        download_wait_msg = bot.reply_to(
            message,
            f"⏳ Downloading `{file_name}`..."
        )

        file_info_tg_doc = bot.get_file(doc.file_id)
        downloaded_file_content = bot.download_file(
            file_info_tg_doc.file_path
        )
        temp_download_path = _create_temp_download_file(
            file_name, downloaded_file_content
        )

        # Malware Scan
        if user_id != OWNER_ID:
            is_safe, reason = scan_file_for_malware(
                downloaded_file_content,
                file_name,
                user_id
            )

            if not is_safe:
                bot.edit_message_text(
                    f"🚨 Security Alert: {reason}",
                    chat_id,
                    download_wait_msg.message_id
                )
                return

        # OWNER uploads = direct processing
        if user_id == OWNER_ID:

            bot.edit_message_text(
                f"✅ Downloaded `{file_name}`. Processing...",
                chat_id,
                download_wait_msg.message_id
            )

            user_folder = get_user_folder(user_id)

            if file_ext == '.zip':
                handle_zip_file(
                    downloaded_file_content,
                    file_name,
                    message
                )

            else:
                file_path = os.path.join(
                    user_folder,
                    file_name
                )

                with open(file_path, "wb") as f:
                    f.write(downloaded_file_content)

                if file_ext == ".js":
                    handle_js_file(
                        file_path,
                        user_id,
                        user_folder,
                        file_name,
                        message
                    )

                elif file_ext == ".py":
                    handle_py_file(
                        file_path,
                        user_id,
                        user_folder,
                        file_name,
                        message
                    )
                elif file_ext == ".java":
                    handle_java_file(
                        file_path,
                        user_id,
                        user_folder,
                        file_name,
                        message
                    )

            return

        # ========= APPROVAL SYSTEM =========

        request_id = f"{user_id}_{int(time.time())}_{hashlib.sha1(file_name.encode()).hexdigest()[:8]}"
        pending_path = os.path.join(PENDING_DIR, request_id + os.path.splitext(file_name)[1])
        with open(pending_path, 'wb') as pending_handle:
            pending_handle.write(downloaded_file_content)
        user_name = message.from_user.first_name or 'User'
        pending_files[request_id] = {
            "user_id": user_id, "chat_id": chat_id, "file_name": file_name,
            "file_ext": file_ext, "file_size": doc.file_size, "content": downloaded_file_content,
            "stored_path": pending_path, "status": "pending", "user_name": user_name,
            "created_at": datetime.now().isoformat()
        }
        with DB_LOCK:
            conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
            try:
                conn.execute('INSERT INTO pending_file_requests (request_id,user_id,chat_id,user_name,file_name,file_ext,file_size,stored_path,status,created_at) VALUES (?,?,?,?,?,?,?,?,?,?)',
                             (request_id,user_id,chat_id,user_name,file_name,file_ext,doc.file_size,pending_path,'pending',datetime.now().isoformat()))
                conn.commit()
            finally: conn.close()

        markup = InlineKeyboardMarkup()

        markup.row(
            InlineKeyboardButton(
                "✅ Approve",
                callback_data=f"approve_{request_id}"
            ),
            InlineKeyboardButton(
                "❌ Reject",
                callback_data=f"reject_{request_id}"
            )
        )

        try:
            bot.forward_message(
                OWNER_ID,
                chat_id,
                message.message_id
            )
        except:
            pass

        bot.send_message(
            OWNER_ID,
            f"📥 New Upload Request\n\n"
            f"👤 User: {message.from_user.first_name}\n"
            f"🆔 User ID: {user_id}\n"
            f"📄 File: {file_name}\n"
            f"🧩 Type: {file_ext}\n"
            f"📦 Size: {doc.file_size / 1024 / 1024:.2f} MB\n"
            f"🆔 Request: `{request_id}`",
            reply_markup=markup
        )

        bot.edit_message_text(
            "⏳ File sent for admin approval.",
            chat_id,
            download_wait_msg.message_id
        )

    except telebot.apihelper.ApiTelegramException as e:

        logger.error(
            f"Telegram API Error handling file for {user_id}: {e}",
            exc_info=True
        )

        if "file is too big" in str(e).lower():

            bot.reply_to(
                message,
                "❌ Telegram API Error: File too large to download (~20MB limit)."
            )

        else:

            bot.reply_to(
                message,
                f"❌ Telegram API Error: {str(e)}. Try later."
            )

    except Exception as e:

        logger.error(
            f"❌ General error handling file for {user_id}: {e}",
            exc_info=True
        )

        if _is_no_space_error(e):
            _handle_no_space_error("file upload", chat_id)
            return

        bot.reply_to(
            message,
            f"❌ Unexpected error: {str(e)}"
        )
    finally:
        _release_temp_download_file(temp_download_path)

# --- Callback Query Handlers (for Inline Buttons) ---
@bot.callback_query_handler(func=lambda call: call.data == "force_join_check")
def force_join_recheck(call):
    user_id = call.from_user.id

    try:
        joined = is_user_joined_all(user_id)
    except Exception as e:
        logger.error("Force-join callback failed for %s: %s", user_id, e, exc_info=True)
        joined = False

    if not joined:
        missing_channels = ", ".join(
            entry["label"]
            for entry in _force_join_slots()
        ) or "required channels"
        bot.answer_callback_query(
            call.id,
            f"❌ Join all required channels ({missing_channels}) first, "
            "then tap Check Again.",
            show_alert=True
        )
        return

    bot.answer_callback_query(call.id, "✅ Verified! Bot start ho raha hai...")
    # Do not pass call.message.from_user here: that is the bot account.
    _logic_send_welcome(call.message, user=call.from_user)


@bot.callback_query_handler(
    func=lambda call: (call.data or "").startswith("pip_uninstall_")
)
def handle_pip_uninstall_callback(call):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(call.id, "❌ Owner Only", show_alert=True)
        return

    data = call.data or ""
    if data.startswith("pip_uninstall_cancel:"):
        token = data.split(":", 1)[1]
        with PIP_CONFIRM_LOCK:
            pending_pip_uninstalls.pop(token, None)
        bot.answer_callback_query(call.id, "Cancelled")
        try:
            bot.edit_message_text(
                "✖️ Package uninstall cancelled.",
                call.message.chat.id,
                call.message.message_id,
            )
        except Exception:
            pass
        return

    if not data.startswith("pip_uninstall_confirm:"):
        bot.answer_callback_query(call.id, "Invalid action.", show_alert=True)
        return

    token = data.split(":", 1)[1]
    with PIP_CONFIRM_LOCK:
        request = pending_pip_uninstalls.pop(token, None)

    if (
        not request
        or request["owner_id"] != call.from_user.id
        or request["expires_at"] < time.time()
    ):
        bot.answer_callback_query(
            call.id,
            "This uninstall confirmation expired.",
            show_alert=True,
        )
        return

    bot.answer_callback_query(call.id, "Uninstall confirmed.")
    try:
        bot.edit_message_text(
            f"✅ Uninstall confirmed for `{request['package']}`. Starting...",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown",
        )
    except Exception:
        pass
    _start_pip_operation(
        call.message.chat.id,
        "uninstall",
        request["package"],
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data

    logger.info(
        f"Callback: User={user_id}, Data='{data}'"
    )

    if (
        user_id not in admin_ids
        and data != "force_join_check"
        and not is_user_joined_all(user_id)
    ):
        bot.answer_callback_query(
            call.id,
            "❌ Please join all required channels first.",
            show_alert=True,
        )
        send_force_join_msg(call.message.chat.id)
        return

    if (
        bot_locked
        and user_id not in admin_ids
        and data not in ['back_to_main', 'speed', 'stats']
    ):
        bot.answer_callback_query(
            call.id,
            "⚠️ Bot locked by admin.",
            show_alert=True
        )
        return

    try:

        # =========================
        # FILE APPROVAL SYSTEM
        # =========================
        if data.startswith("approve_") or data.startswith("reject_"):
            handle_file_approval(call)

        elif data == 'paid_panel':
            bot.answer_callback_query(call.id)
            show_paid_panel(call.message.chat.id, call.from_user.id, call.message.message_id)

        elif data.startswith('plan_'):
            show_payment_page(call, data.replace('plan_', '', 1))

        elif data == 'my_plan':
            bot.answer_callback_query(call.id)
            bot.send_message(
                call.message.chat.id,
                _paid_panel_text(call.from_user.id),
                reply_markup=premium_panel_markup()
            )

        elif data == 'my_subscription':
            bot.answer_callback_query(call.id)
            bot.send_message(
                call.message.chat.id,
                _paid_panel_text(call.from_user.id),
                reply_markup=premium_panel_markup()
            )

        elif data.startswith('copy_upi_'):
            plan_key = data.replace('copy_upi_', '', 1)
            if plan_key not in PREMIUM_PLANS:
                bot.answer_callback_query(call.id, 'Invalid plan.', show_alert=True)
            else:
                upi_id = bot_settings.get('upi_id') or 'rajanwins@ibl'
                bot.answer_callback_query(call.id, upi_id, show_alert=True)
                bot.send_message(
                    call.message.chat.id,
                    upi_id
                )

        elif data.startswith('pay_upi_'):
            plan_key = data.replace('pay_upi_', '', 1)
            if plan_key not in PREMIUM_PLANS:
                bot.answer_callback_query(call.id, 'Invalid plan.', show_alert=True)
            else:
                upi_id = bot_settings.get('upi_id') or 'rajanwins@ibl'
                bot.answer_callback_query(call.id, upi_id, show_alert=True)
                bot.send_message(call.message.chat.id, upi_id)

        elif data.startswith('show_qr_'):
            _send_payment_qr(call, data.replace('show_qr_', '', 1))

        elif data.startswith('send_screenshot_'):
            plan_key = data.replace('send_screenshot_', '', 1)
            if plan_key not in PREMIUM_PLANS:
                bot.answer_callback_query(call.id, 'Invalid plan.', show_alert=True)
            else:
                set_pending_payment_plan(call.from_user.id, plan_key)
                bot.answer_callback_query(call.id)
                bot.send_message(
                    call.message.chat.id,
                    '🌷💗 𝐏ᴀʏᴍᴇɴᴛ Sᴄʀᴇᴇɴsʜᴏᴛ 💗🌷\n\n'
                    'Please send your payment screenshot here.'
                )

        elif data.startswith('payapprove_') or data.startswith('payreject_'):
            if call.from_user.id not in admin_ids:
                bot.answer_callback_query(call.id,'⚠️ Admin only.',show_alert=True)
            else:
                rid=data.split('_',1)[1]
                if data.startswith('payapprove_'):
                    ok,result=_activate_paid_plan(rid,call.from_user.id)
                    if ok:
                        bot.answer_callback_query(call.id,'✅ Approved')
                        try:
                            bot.edit_message_caption(
                                f'✅ APPROVED\n🆔 Request: {rid}',
                                call.message.chat.id, call.message.message_id
                            )
                        except Exception as edit_error:
                            logger.warning("Could not update approved payment caption: %s", edit_error)
                        bot.send_message(
                            result[0],
                            '🎉 Premium activated!\n'
                            f'💎 Plan: {PREMIUM_PLANS.get(result[1], {}).get("name", "Premium")}\n'
                            f'⏳ Expires: {result[2]:%d-%m-%Y %H:%M}'
                        )
                    else: bot.answer_callback_query(call.id,str(result),show_alert=True)
                else:
                    ok,result=_reject_payment(rid,call.from_user.id)
                    if ok:
                        bot.answer_callback_query(call.id,'❌ Rejected')
                        try:
                            bot.edit_message_caption(
                                f'❌ REJECTED\n🆔 Request: {rid}',
                                call.message.chat.id, call.message.message_id
                            )
                        except Exception as edit_error:
                            logger.warning("Could not update rejected payment caption: %s", edit_error)
                        bot.send_message(result,'❌ Your Premium payment request was rejected by admin. Premium was not activated.')
                    else: bot.answer_callback_query(call.id,str(result),show_alert=True)

        elif data == 'upload':
            upload_callback(call)

        elif data == 'check_files':
            check_files_callback(call)

        elif data == 'running_bots':
            bot.answer_callback_query(call.id)
            bot.send_message(
                call.message.chat.id,
                _format_running_scripts_message(call.from_user.id)
            )

        elif data.startswith('file_'):
            file_control_callback(call)

        elif data.startswith('start_'):
            start_bot_callback(call)

        elif data.startswith('stop_'):
            stop_bot_callback(call)

        elif data.startswith('restart_'):
            restart_bot_callback(call)

        elif data.startswith('delete_'):
            delete_bot_callback(call)

        elif data.startswith('logs_'):
            logs_bot_callback(call)

        elif data == 'speed':
            speed_callback(call)

        elif data == 'back_to_main':
            back_to_main_callback(call)

        elif data.startswith('confirm_broadcast_'):
            handle_confirm_broadcast(call)

        elif data == 'cancel_broadcast':
            handle_cancel_broadcast(call)

        # Send Command
        elif data == 'send_command':
            send_command_callback(call)

        elif data == 'send_to_process':
            send_to_process_callback(call)

        elif data.startswith('sendcmd_select_'):
            sendcmd_select_callback(call)

        elif data == 'view_all_logs':
            view_all_logs_callback(call)

        elif data.startswith('viewlog_'):
            viewlog_callback(call)

        # Admin
        elif data == 'subscription':
            admin_required_callback(
                call,
                subscription_management_callback
            )

        elif data == 'stats':
            stats_callback(call)

        elif data == 'lock_bot':
            admin_required_callback(
                call,
                lock_bot_callback
            )

        elif data == 'unlock_bot':
            admin_required_callback(
                call,
                unlock_bot_callback
            )

        elif data == 'run_all_scripts':
            admin_required_callback(
                call,
                run_all_scripts_callback
            )

        elif data == 'broadcast':
            admin_required_callback(
                call,
                broadcast_init_callback
            )

        elif data == 'admin_panel':
            admin_required_callback(
                call,
                admin_panel_callback
            )

        elif data == 'add_admin':
            owner_required_callback(
                call,
                add_admin_init_callback
            )

        elif data == 'remove_admin':
            owner_required_callback(
                call,
                remove_admin_init_callback
            )

        elif data == 'list_admins':
            admin_required_callback(
                call,
                list_admins_callback
            )

        elif data == 'add_subscription':
            admin_required_callback(
                call,
                add_subscription_init_callback
            )

        elif data == 'remove_subscription':
            admin_required_callback(
                call,
                remove_subscription_init_callback
            )

        elif data == 'check_subscription':
            admin_required_callback(
                call,
                check_subscription_init_callback
            )

        else:
            bot.answer_callback_query(
                call.id,
                "Unknown action."
            )

            logger.warning(
                f"Unhandled callback data: {data} "
                f"from user {user_id}"
            )

    except Exception as e:

        logger.error(
            f"Error handling callback '{data}' "
            f"for {user_id}: {e}",
            exc_info=True
        )

        try:
            bot.answer_callback_query(
                call.id,
                "Error processing request.",
                show_alert=True
            )
        except Exception as e_ans:
            logger.error(
                f"Failed to answer callback after error: {e_ans}"
            )


def admin_required_callback(call, func_to_run):
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(
            call.id,
            "⚠️ Admin permissions required.",
            show_alert=True
        )
        return

    func_to_run(call)


# =========================
# FILE APPROVAL FUNCTION
# =========================
def handle_file_approval(call):
    global pending_files
    if call.from_user.id not in admin_ids:
        bot.answer_callback_query(call.id, "⚠️ Admin permissions required!", show_alert=True)
        return
    action, request_id = call.data.split("_", 1)
    if request_id not in pending_files:
        # Recover metadata/content from DB after restart if possible.
        conn = sqlite3.connect(DATABASE_PATH, check_same_thread=False)
        try:
            row = conn.execute("SELECT user_id,chat_id,user_name,file_name,file_ext,file_size,stored_path,status,created_at FROM pending_file_requests WHERE request_id=?", (request_id,)).fetchone()
        finally: conn.close()
        if row:
            uid,cid,uname,fname,fext,fsize,spath,status,created = row
            content = None
            if spath and os.path.exists(spath):
                try:
                    with open(spath,'rb') as fh: content=fh.read()
                except Exception: pass
            pending_files[request_id] = {'user_id':uid,'chat_id':cid,'user_name':uname,'file_name':fname,'file_ext':fext,'file_size':fsize,'stored_path':spath,'status':status,'created_at':created,'content':content}
    if request_id not in pending_files:
        bot.answer_callback_query(call.id, "Request expired!", show_alert=True)
        return
    file_data = pending_files[request_id]
    if file_data.get('status') != 'pending':
        bot.answer_callback_query(call.id, f"Already {file_data.get('status')}", show_alert=True)
        return
    user_id = file_data["user_id"]; chat_id = file_data["chat_id"]; file_name = file_data["file_name"]; file_ext = file_data["file_ext"]; content = file_data.get("content")
    if content is None and file_data.get('stored_path') and os.path.exists(file_data['stored_path']):
        with open(file_data['stored_path'],'rb') as fh: content=fh.read()
    if content is None:
        bot.answer_callback_query(call.id, "Pending file data missing.", show_alert=True); return
    if action == "reject":
        with DB_LOCK:
            conn=sqlite3.connect(DATABASE_PATH,check_same_thread=False)
            try:
                cur=conn.execute("UPDATE pending_file_requests SET status='rejected',decided_at=? WHERE request_id=? AND status='pending'",(datetime.now().isoformat(),request_id)); conn.commit()
            finally: conn.close()
        if cur.rowcount != 1: bot.answer_callback_query(call.id,"Already decided",show_alert=True); return
        bot.send_message(chat_id, f"❌ Your file '{file_name}' was rejected by admin.")
        bot.edit_message_text(f"❌ Rejected: {file_name}",call.message.chat.id,call.message.message_id)
        pending_files.pop(request_id,None)
        try: os.remove(file_data.get('stored_path',''))
        except Exception: pass
        return
    # Re-check the active + pending limit at approval time.
    limit=get_user_file_limit(user_id); current=get_user_file_count(user_id)
    if current >= limit:
        bot.answer_callback_query(call.id, "User file limit is already full.", show_alert=True); return
    with DB_LOCK:
        conn=sqlite3.connect(DATABASE_PATH,check_same_thread=False)
        try:
            cur=conn.execute("UPDATE pending_file_requests SET status='approved',decided_at=? WHERE request_id=? AND status='pending'",(datetime.now().isoformat(),request_id)); conn.commit()
        finally: conn.close()
    if cur.rowcount != 1:
        bot.answer_callback_query(call.id,"Already decided",show_alert=True); return
    try:
        user_folder=get_user_folder(user_id)
        if file_ext=='.zip':
            handle_zip_file(content,file_name,call.message,owner_id=user_id)
        else:
            file_path=os.path.join(user_folder,file_name)
            with open(file_path,'wb') as f: f.write(content)
            if file_ext=='.js':
                handle_js_file(file_path,user_id,user_folder,file_name,call.message)
            elif file_ext=='.py':
                handle_py_file(file_path,user_id,user_folder,file_name,call.message)
            elif file_ext=='.java':
                handle_java_file(file_path,user_id,user_folder,file_name,call.message)
        bot.send_message(chat_id,f"✅ Your file '{file_name}' approved successfully.")
        bot.edit_message_text(f"✅ Approved: {file_name}",call.message.chat.id,call.message.message_id)
    except Exception as e:
        logger.error(f"Approval processing error: {e}",exc_info=True)
        # Roll back status if processing failed.
        with DB_LOCK:
            conn=sqlite3.connect(DATABASE_PATH,check_same_thread=False)
            try: conn.execute("UPDATE pending_file_requests SET status='pending',decided_at=NULL WHERE request_id=?",(request_id,)); conn.commit()
            finally: conn.close()
        bot.send_message(chat_id,f"❌ Processing failed: {e}")
        return
    pending_files.pop(request_id,None)
    try: os.remove(file_data.get('stored_path',''))
    except Exception: pass

def owner_required_callback(call, func_to_run):
    if call.from_user.id != OWNER_ID:
        bot.answer_callback_query(
            call.id,
            "⚠️ Owner permissions required.",
            show_alert=True
        )
        return

    func_to_run(call)

# --- New Send Command Callback Functions ---
def send_command_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("📤 Send Command Options:",
                              call.message.chat.id, call.message.message_id, 
                              reply_markup=create_send_command_menu())
    except Exception as e:
        logger.error(f"Error showing send command menu: {e}")

def send_to_process_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📝 Send the command you want to execute:")
    bot.register_next_step_handler(msg, lambda m: send_to_process_init(m))

def sendcmd_select_callback(call):
    try:
        token = call.data.replace('sendcmd_select_', '', 1)
        script_key = process_callback_refs.get(token)
        if not script_key:
            raise ValueError("Expired process button")
        bot.answer_callback_query(call.id, f"Selected script: {script_key}")
        msg = bot.send_message(call.message.chat.id, f"📝 Enter command to send to {script_key}:")
        bot.register_next_step_handler(msg, lambda m: process_send_command(m, script_key))
    except Exception as e:
        logger.error(f"Error in sendcmd_select_callback: {e}")
        bot.answer_callback_query(call.id, "Error selecting script.")

def view_all_logs_callback(call):
    bot.answer_callback_query(call.id)
    view_all_logs(call.message)

def viewlog_callback(call):
    try:
        user_id, log_filename = parse_file_callback(call.data)
        requesting_user_id = call.from_user.id
        
        if not (requesting_user_id == user_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ You can only view your own logs.", show_alert=True)
            return
            
        user_folder = get_user_folder(user_id)
        log_path = os.path.join(user_folder, os.path.basename(log_filename))
        
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, "❌ Log file not found.", show_alert=True)
            return
            
        bot.answer_callback_query(call.id, "📜 Sending log file...")
        send_log_file(call.message, log_path, log_filename)
        
    except Exception as e:
        logger.error(f"Error in viewlog_callback: {e}")
        bot.answer_callback_query(call.id, "Error viewing log.")

# ... (rest of the existing callback functions remain the same)

def upload_callback(call):
    user_id = call.from_user.id
    logger.info(f"Upload button clicked by user {user_id}")
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    pending_count = get_user_pending_file_count(user_id)
    if current_files + pending_count >= file_limit:
        limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
        bot.answer_callback_query(
            call.id,
            f"⚠️ File limit ({current_files}/{limit_str}) reached.",
            show_alert=True
        )
        return
    bot.answer_callback_query(call.id, "📤 Upload mode enabled.")
    prompt = bot.send_message(
        call.message.chat.id,
        '📤 𝐔ᴘʟᴏᴀᴅ Sᴄʀɪᴘᴛ\n\n'
        'Ab apni `.py`, `.js`, `.java`, ya `.zip` file Document ke रूप में send karo.\n'
        'Maximum size: 20 MB\n\n'
        'Text bhejne par upload mode active rahega.'
    )
    bot.register_next_step_handler(prompt, _upload_prompt_next_step)

def _upload_prompt_next_step(message):
    if message.content_type == 'document':
        handle_file_upload_doc(message)
        return
    if message.content_type == 'text' and message.text and message.text.lower() == '/cancel':
        bot.reply_to(message, '❌ Upload cancelled.')
        return
    bot.reply_to(
        message,
        '⚠️ Please send a `.py`, `.js`, `.java`, or `.zip` file as a Telegram Document.'
    )
    prompt = bot.send_message(
        message.chat.id,
        '📤 Upload mode active — file bhejo, ya `/cancel` likho.'
    )
    bot.register_next_step_handler(prompt, _upload_prompt_next_step)

def check_files_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id 
    visible_users = sorted(user_files) if user_id in admin_ids else [user_id]
    file_rows = [
        (owner_id, file_name, file_type)
        for owner_id in visible_users
        for file_name, file_type in user_files.get(owner_id, [])
    ]
    if not file_rows:
        bot.answer_callback_query(call.id, "⚠️ No files uploaded.", show_alert=True)
        try:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
            bot.edit_message_text("📂 Your files:\n\n(No files uploaded)", chat_id, call.message.message_id, reply_markup=markup)
        except Exception as e: logger.error(f"Error editing msg for empty file list: {e}")
        return
    bot.answer_callback_query(call.id) 
    markup = types.InlineKeyboardMarkup(row_width=1) 
    for owner_id, file_name, file_type in sorted(file_rows, key=lambda row: (user_display_name(row[0]).casefold(), row[1].casefold())):
        is_running = is_bot_running(owner_id, file_name)
        status_icon = "🟢 Running" if is_running else "🔴 Stopped"
        owner_text = f" • {user_display_name(owner_id)} [{owner_id}]" if user_id in admin_ids else ""
        btn_text = f"{file_name} ({file_type}) - {status_icon}{owner_text}"
        markup.add(types.InlineKeyboardButton(btn_text[:60], callback_data=make_file_callback('file', owner_id, file_name)))
    markup.add(types.InlineKeyboardButton("🔙 Back to Main", callback_data='back_to_main'))
    try:
        title = "📂 All Users' Files" if user_id in admin_ids else "📂 Your Files"
        bot.edit_message_text(f"𝐑𝐀𝐉𝐀𝐍 𝐗 𝐇𝐈𝐍𝐀𝐓𝐀\n\n{title}\nClick to manage.", chat_id, call.message.message_id, reply_markup=markup, parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
         if "message is not modified" in str(e): logger.warning("Msg not modified (files).")
         else: logger.error(f"Error editing msg for file list: {e}")
    except Exception as e: logger.error(f"Unexpected error editing msg for file list: {e}", exc_info=True)

def file_control_callback(call):
    try:
        script_owner_id, file_name = parse_file_callback(call.data)
        requesting_user_id = call.from_user.id

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            logger.warning(f"User {requesting_user_id} tried to access file '{file_name}' of user {script_owner_id} without permission.")
            bot.answer_callback_query(call.id, "⚠️ You can only manage your own files.", show_alert=True)
            check_files_callback(call)
            return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            logger.warning(f"File '{file_name}' not found for user {script_owner_id} during control.")
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True)
            check_files_callback(call) 
            return

        bot.answer_callback_query(call.id) 
        is_running = is_bot_running(script_owner_id, file_name)
        status_text = '🟢 Running' if is_running else '🔴 Stopped'
        file_type = next((f[1] for f in user_files_list if f[0] == file_name), '?') 
        try:
            bot.edit_message_text(
                f"⚙️ Controls for: `{file_name}` ({file_type}) of User `{script_owner_id}`\nStatus: {status_text}",
                call.message.chat.id, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_running),
                parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified (controls for {file_name})")
             else: raise 
    except (ValueError, IndexError) as ve:
        logger.error(f"Error parsing file control callback: {ve}. Data: '{call.data}'")
        bot.answer_callback_query(call.id, "Error: Invalid action data.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in file_control_callback for data '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "An error occurred.", show_alert=True)

def start_bot_callback(call):
    try:
        script_owner_id, file_name = parse_file_callback(call.data)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Start request: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")

        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied to start this script.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1]
        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)

        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"⚠️ Error: File `{file_name}` missing! Re-upload.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name); check_files_callback(call); return

        if is_bot_running(script_owner_id, file_name):
            bot.answer_callback_query(call.id, f"⚠️ Script '{file_name}' already running.", show_alert=True)
            try: bot.edit_message_reply_markup(chat_id_for_reply, call.message.message_id, reply_markup=create_control_buttons(script_owner_id, file_name, True))
            except Exception as e: logger.error(f"Error updating buttons (already running): {e}")
            return

        bot.answer_callback_query(call.id, f"⏳ Attempting to start {file_name} for user {script_owner_id}...")

        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'java':
            threading.Thread(target=run_java_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
             bot.send_message(chat_id_for_reply, f"❌ Error: Unknown file type '{file_type}' for '{file_name}'."); return 

        time.sleep(1.5)
        is_now_running = is_bot_running(script_owner_id, file_name) 
        status_text = '🟢 Running' if is_now_running else '🟡 Starting (or failed, check logs/replies)'
        try:
            bot.edit_message_text(
                f"⚙️ Controls for: `{file_name}` ({file_type}) of User `{script_owner_id}`\nStatus: {status_text}",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified after starting {file_name}")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing start callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Error: Invalid start command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in start_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Error starting script.", show_alert=True)
        try:
            script_owner_id_err, file_name_err = parse_file_callback(call.data)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(script_owner_id_err, file_name_err, False))
        except Exception as e_btn: logger.error(f"Failed to update buttons after start error: {e_btn}")

def stop_bot_callback(call):
    try:
        script_owner_id, file_name = parse_file_callback(call.data)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Stop request: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1] 
        script_key = f"{script_owner_id}_{file_name}"

        if not is_bot_running(script_owner_id, file_name): 
            bot.answer_callback_query(call.id, f"⚠️ Script '{file_name}' already stopped.", show_alert=True)
            try:
                 bot.edit_message_text(
                     f"⚙️ Controls for: `{file_name}` ({file_type}) of User `{script_owner_id}`\nStatus: 🔴 Stopped",
                     chat_id_for_reply, call.message.message_id,
                     reply_markup=create_control_buttons(script_owner_id, file_name, False), parse_mode='Markdown')
            except Exception as e: logger.error(f"Error updating buttons (already stopped): {e}")
            return

        bot.answer_callback_query(call.id, f"⏳ Stopping {file_name} for user {script_owner_id}...")
        process_info = bot_scripts.get(script_key)
        if process_info:
            kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]; logger.info(f"Removed {script_key} from running after stop.")
        else: logger.warning(f"Script {script_key} running by psutil but not in bot_scripts dict.")

        try:
            bot.edit_message_text(
                f"⚙️ Controls for: `{file_name}` ({file_type}) of User `{script_owner_id}`\nStatus: 🔴 Stopped",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, False), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified after stopping {file_name}")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing stop callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Error: Invalid stop command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in stop_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Error stopping script.", show_alert=True)

def restart_bot_callback(call):
    try:
        script_owner_id, file_name = parse_file_callback(call.data)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Restart: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        file_info = next((f for f in user_files_list if f[0] == file_name), None)
        if not file_info:
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        file_type = file_info[1]; user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name); script_key = f"{script_owner_id}_{file_name}"

        if not os.path.exists(file_path):
            bot.answer_callback_query(call.id, f"⚠️ Error: File `{file_name}` missing! Re-upload.", show_alert=True)
            remove_user_file_db(script_owner_id, file_name)
            if script_key in bot_scripts: del bot_scripts[script_key]
            check_files_callback(call); return

        bot.answer_callback_query(call.id, f"⏳ Restarting {file_name} for user {script_owner_id}...")
        if is_bot_running(script_owner_id, file_name):
            logger.info(f"Restart: Stopping existing {script_key}...")
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(1.5) 

        logger.info(f"Restart: Starting script {script_key}...")
        if file_type == 'py':
            threading.Thread(target=run_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'js':
            threading.Thread(target=run_js_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        elif file_type == 'java':
            threading.Thread(target=run_java_script, args=(file_path, script_owner_id, user_folder, file_name, call.message)).start()
        else:
             bot.send_message(chat_id_for_reply, f"❌ Unknown type '{file_type}' for '{file_name}'."); return

        time.sleep(1.5) 
        is_now_running = is_bot_running(script_owner_id, file_name) 
        status_text = '🟢 Running' if is_now_running else '🟡 Starting (or failed)'
        try:
            bot.edit_message_text(
                f"⚙️ Controls for: `{file_name}` ({file_type}) of User `{script_owner_id}`\nStatus: {status_text}",
                chat_id_for_reply, call.message.message_id,
                reply_markup=create_control_buttons(script_owner_id, file_name, is_now_running), parse_mode='Markdown'
            )
        except telebot.apihelper.ApiTelegramException as e:
             if "message is not modified" in str(e): logger.warning(f"Msg not modified (restart {file_name})")
             else: raise
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing restart callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Error: Invalid restart command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in restart_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Error restarting.", show_alert=True)
        try:
            script_owner_id_err, file_name_err = parse_file_callback(call.data)
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_control_buttons(script_owner_id_err, file_name_err, False))
        except Exception as e_btn: logger.error(f"Failed to update buttons after restart error: {e_btn}")

def delete_bot_callback(call):
    try:
        script_owner_id, file_name = parse_file_callback(call.data)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Delete: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        bot.answer_callback_query(call.id, f"🗑️ Deleting {file_name} for user {script_owner_id}...")
        script_key = f"{script_owner_id}_{file_name}"
        if is_bot_running(script_owner_id, file_name):
            logger.info(f"Delete: Stopping {script_key}...")
            process_info = bot_scripts.get(script_key)
            if process_info: kill_process_tree(process_info)
            if script_key in bot_scripts: del bot_scripts[script_key]
            time.sleep(0.5) 

        user_folder = get_user_folder(script_owner_id)
        file_path = os.path.join(user_folder, file_name)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        deleted_disk = []
        if os.path.exists(file_path):
            try: os.remove(file_path); deleted_disk.append(file_name); logger.info(f"Deleted file: {file_path}")
            except OSError as e: logger.error(f"Error deleting {file_path}: {e}")
        if os.path.exists(log_path):
            try: os.remove(log_path); deleted_disk.append(os.path.basename(log_path)); logger.info(f"Deleted log: {log_path}")
            except OSError as e: logger.error(f"Error deleting log {log_path}: {e}")

        remove_user_file_db(script_owner_id, file_name)
        deleted_str = ", ".join(f"`{f}`" for f in deleted_disk) if deleted_disk else "associated files"
        try:
            bot.edit_message_text(
                f"🗑️ Record `{file_name}` (User `{script_owner_id}`) and {deleted_str} deleted!",
                chat_id_for_reply, call.message.message_id, reply_markup=None, parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error editing msg after delete: {e}")
            bot.send_message(chat_id_for_reply, f"🗑️ Record `{file_name}` deleted.", parse_mode='Markdown')
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing delete callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Error: Invalid delete command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in delete_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Error deleting.", show_alert=True)

def logs_bot_callback(call):
    try:
        script_owner_id, file_name = parse_file_callback(call.data)
        requesting_user_id = call.from_user.id
        chat_id_for_reply = call.message.chat.id

        logger.info(f"Logs: Requester={requesting_user_id}, Owner={script_owner_id}, File='{file_name}'")
        if not (requesting_user_id == script_owner_id or requesting_user_id in admin_ids):
            bot.answer_callback_query(call.id, "⚠️ Permission denied.", show_alert=True); return

        user_files_list = user_files.get(script_owner_id, [])
        if not any(f[0] == file_name for f in user_files_list):
            bot.answer_callback_query(call.id, "⚠️ File not found.", show_alert=True); check_files_callback(call); return

        user_folder = get_user_folder(script_owner_id)
        log_path = os.path.join(user_folder, f"{os.path.splitext(file_name)[0]}.log")
        if not os.path.exists(log_path):
            bot.answer_callback_query(call.id, f"⚠️ No logs for '{file_name}'.", show_alert=True); return

        bot.answer_callback_query(call.id) 
        try:
            log_content = ""; file_size = os.path.getsize(log_path)
            max_log_kb = 100; max_tg_msg = 4096
            if file_size == 0: log_content = "(Log empty)"
            elif file_size > max_log_kb * 1024:
                 with open(log_path, 'rb') as f: f.seek(-max_log_kb * 1024, os.SEEK_END); log_bytes = f.read()
                 log_content = log_bytes.decode('utf-8', errors='ignore')
                 log_content = f"(Last {max_log_kb} KB)\n...\n" + log_content
            else:
                 with open(log_path, 'r', encoding='utf-8', errors='ignore') as f: log_content = f.read()

            if len(log_content) > max_tg_msg:
                log_content = log_content[-max_tg_msg:]
                first_nl = log_content.find('\n')
                if first_nl != -1: log_content = "...\n" + log_content[first_nl+1:]
                else: log_content = "...\n" + log_content 
            if not log_content.strip(): log_content = "(No visible content)"

            bot.send_message(chat_id_for_reply, f"📜 Logs for `{file_name}` (User `{script_owner_id}`):\n```\n{log_content}\n```", parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error reading/sending log {log_path}: {e}", exc_info=True)
            bot.send_message(chat_id_for_reply, f"❌ Error reading log for `{file_name}`.")
    except (ValueError, IndexError) as e:
        logger.error(f"Error parsing logs callback '{call.data}': {e}")
        bot.answer_callback_query(call.id, "Error: Invalid logs command.", show_alert=True)
    except Exception as e:
        logger.error(f"Error in logs_bot_callback for '{call.data}': {e}", exc_info=True)
        bot.answer_callback_query(call.id, "Error fetching logs.", show_alert=True)

def speed_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    bot.answer_callback_query(call.id)
    start_cb_ping_time = time.perf_counter()
    try:
        bot.send_chat_action(chat_id, 'typing')
        response_time = round((time.perf_counter() - start_cb_ping_time) * 1000, 2)
        bot.edit_message_text(
            _bot_status_text(user_id, response_time),
            chat_id,
            call.message.message_id,
            reply_markup=create_main_menu_inline(user_id),
            parse_mode='Markdown'
        )
    except Exception as e:
        logger.error(f"Error during speed test (cb): {e}", exc_info=True)
        try:
            bot.edit_message_text(
                "❌ Error in speed test.",
                chat_id,
                call.message.message_id,
                reply_markup=create_main_menu_inline(user_id)
            )
        except Exception:
            pass
    return

    # Legacy callback implementation retained below for old deployments.
    start_cb_ping_time = time.time() 
    try:
        bot.edit_message_text("🏃 Testing speed...", chat_id, call.message.message_id)
        bot.send_chat_action(chat_id, 'typing') 
        response_time = round((time.time() - start_cb_ping_time) * 1000, 2)
        status = "🔓 Unlocked" if not bot_locked else "🔒 Locked"
        if user_id == OWNER_ID: user_level = "🤍 Owner"
        elif user_id in admin_ids: user_level = "🌙 Admin"
        elif user_id in user_subscriptions and user_subscriptions[user_id].get('expiry', datetime.min) > datetime.now(): user_level = "⭐ Premium"
        else: user_level = "🆓 Free User"
        speed_msg = (f"⚡ Bot Speed & Status:\n\n⏱️ API Response Time: {response_time} ms\n"
                     f"🚦 Bot Status: {status}\n"
                     f"👤 Your Level: {user_level}")
        bot.answer_callback_query(call.id) 
        bot.edit_message_text(speed_msg, chat_id, call.message.message_id, reply_markup=create_main_menu_inline(user_id))
    except Exception as e:
         logger.error(f"Error during speed test (cb): {e}", exc_info=True)
         bot.answer_callback_query(call.id, "Error in speed test.", show_alert=True)
         try: bot.edit_message_text("〽️ Main Menu", chat_id, call.message.message_id, reply_markup=create_main_menu_inline(user_id))
         except Exception: pass

def back_to_main_callback(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    file_limit = get_user_file_limit(user_id)
    current_files = get_user_file_count(user_id)
    limit_str = str(file_limit) if file_limit != float('inf') else "Unlimited"
    expiry_info = ""
    if user_id == OWNER_ID: user_status = "🤍 Owner"
    elif user_id in admin_ids: user_status = "🌙 Admin"
    elif user_id in user_subscriptions:
        expiry_date = user_subscriptions[user_id].get('expiry')
        if expiry_date and expiry_date > datetime.now():
            user_status = "⭐ Premium"; days_left = (expiry_date - datetime.now()).days
            expiry_info = f"\n⏳ Subscription expires in: {days_left} days"
        else: user_status = "🆓 Free User (Expired Sub)"
    else: user_status = "🆓 Free User"
    main_menu_text = (f"〽️ Welcome back, {call.from_user.first_name}!\n\n🆔 ID: `{user_id}`\n"
                      f"🔰 Status: {user_status}{expiry_info}\n📁 Files: {current_files} / {limit_str}\n\n"
                      f"👇 Use buttons or type commands.")
    try:
        bot.answer_callback_query(call.id)
        bot.edit_message_text(main_menu_text, chat_id, call.message.message_id,
                              reply_markup=create_main_menu_inline(user_id), parse_mode='Markdown')
    except telebot.apihelper.ApiTelegramException as e:
         if "message is not modified" in str(e): logger.warning("Msg not modified (back_to_main).")
         else: logger.error(f"API error on back_to_main: {e}")
    except Exception as e: logger.error(f"Error handling back_to_main: {e}", exc_info=True)

# --- Admin Callback Implementations ---
def subscription_management_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text("💳 Subscription Management\nSelect action:",
                              call.message.chat.id, call.message.message_id, reply_markup=create_subscription_menu())
    except Exception as e: logger.error(f"Error showing sub menu: {e}")

def stats_callback(call):
    bot.answer_callback_query(call.id)
    _logic_statistics(call.message, actor_id=call.from_user.id)
    try:
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id,
                                      reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e:
        logger.error(f"Error updating menu after stats_callback: {e}")

def lock_bot_callback(call):
    global bot_locked; bot_locked = True
    logger.warning(f"Bot locked by Admin {call.from_user.id}")
    bot.answer_callback_query(call.id, "🔒 Bot locked.")
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e: logger.error(f"Error updating menu (lock): {e}")

def unlock_bot_callback(call):
    global bot_locked; bot_locked = False
    logger.warning(f"Bot unlocked by Admin {call.from_user.id}")
    bot.answer_callback_query(call.id, "🔓 Bot unlocked.")
    try: bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=create_main_menu_inline(call.from_user.id))
    except Exception as e: logger.error(f"Error updating menu (unlock): {e}")

def run_all_scripts_callback(call):
    _logic_run_all_scripts(call)

def broadcast_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "📢 Send message to broadcast.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_broadcast_message)

def process_broadcast_message(message):
    user_id = message.from_user.id
    if user_id not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    if message.text and message.text.lower() == '/cancel': bot.reply_to(message, "Broadcast cancelled."); return

    broadcast_content = message.text
    if not broadcast_content and not (message.photo or message.video or message.document or message.sticker or message.voice or message.audio):
         bot.reply_to(message, "⚠️ Cannot broadcast empty message. Send text or media, or /cancel.")
         msg = bot.send_message(message.chat.id, "📢 Send broadcast message or /cancel.")
         bot.register_next_step_handler(msg, process_broadcast_message)
         return

    target_count = len(active_users)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton("✅ Confirm & Send", callback_data=f"confirm_broadcast_{message.message_id}"),
               types.InlineKeyboardButton("❌ Cancel", callback_data="cancel_broadcast"))

    preview_text = broadcast_content[:1000].strip() if broadcast_content else "(Media message)"
    bot.reply_to(message, f"⚠️ Confirm Broadcast:\n\n```\n{preview_text}\n```\n" 
                          f"To **{target_count}** users. Sure?", reply_markup=markup, parse_mode='Markdown')

def handle_confirm_broadcast(call):
    user_id = call.from_user.id
    chat_id = call.message.chat.id
    if user_id not in admin_ids: bot.answer_callback_query(call.id, "⚠️ Admin only.", show_alert=True); return
    try:
        original_message = call.message.reply_to_message
        if not original_message: raise ValueError("Could not retrieve original message.")

        broadcast_text = None
        broadcast_photo_id = None
        broadcast_video_id = None

        if original_message.text:
            broadcast_text = original_message.text
        elif original_message.photo:
            broadcast_photo_id = original_message.photo[-1].file_id
        elif original_message.video:
            broadcast_video_id = original_message.video.file_id
        else:
            raise ValueError("Message has no text or supported media for broadcast.")

        bot.answer_callback_query(call.id, "🚀 Starting broadcast...")
        bot.edit_message_text(f"📢 Broadcasting to {len(active_users)} users...",
                              chat_id, call.message.message_id, reply_markup=None)
        thread = threading.Thread(target=execute_broadcast, args=(
            broadcast_text, broadcast_photo_id, broadcast_video_id, 
            original_message.caption if (broadcast_photo_id or broadcast_video_id) else None,
            chat_id))
        thread.start()
    except ValueError as ve: 
        logger.error(f"Error retrieving msg for broadcast confirm: {ve}")
        bot.edit_message_text(f"❌ Error starting broadcast: {ve}", chat_id, call.message.message_id, reply_markup=None)
    except Exception as e:
        logger.error(f"Error in handle_confirm_broadcast: {e}", exc_info=True)
        bot.edit_message_text("❌ Unexpected error during broadcast confirm.", chat_id, call.message.message_id, reply_markup=None)

def handle_cancel_broadcast(call):
    bot.answer_callback_query(call.id, "Broadcast cancelled.")
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.message.reply_to_message:
        try: bot.delete_message(call.message.chat.id, call.message.reply_to_message.message_id)
        except: pass

def execute_broadcast(broadcast_text, photo_id, video_id, caption, admin_chat_id):
    sent_count = 0; failed_count = 0; blocked_count = 0
    start_exec_time = time.time() 
    users_to_broadcast = list(active_users); total_users = len(users_to_broadcast)
    logger.info(f"Executing broadcast to {total_users} users.")
    batch_size = 25; delay_batches = 1.5

    for i, user_id_bc in enumerate(users_to_broadcast):
        try:
            if broadcast_text:
                bot.send_message(user_id_bc, broadcast_text, parse_mode='Markdown')
            elif photo_id:
                bot.send_photo(user_id_bc, photo_id, caption=caption, parse_mode='Markdown' if caption else None)
            elif video_id:
                bot.send_video(user_id_bc, video_id, caption=caption, parse_mode='Markdown' if caption else None)
            sent_count += 1
        except telebot.apihelper.ApiTelegramException as e:
            err_desc = str(e).lower()
            if any(s in err_desc for s in ["bot was blocked", "user is deactivated", "chat not found", "kicked from", "restricted"]): 
                logger.warning(f"Broadcast failed to {user_id_bc}: User blocked/inactive.")
                blocked_count += 1
            elif "flood control" in err_desc or "too many requests" in err_desc:
                retry_after = 5; match = re.search(r"retry after (\d+)", err_desc)
                if match: retry_after = int(match.group(1)) + 1 
                logger.warning(f"Flood control. Sleeping {retry_after}s...")
                time.sleep(retry_after)
                try:
                    if broadcast_text: bot.send_message(user_id_bc, broadcast_text, parse_mode='Markdown')
                    elif photo_id: bot.send_photo(user_id_bc, photo_id, caption=caption, parse_mode='Markdown' if caption else None)
                    elif video_id: bot.send_video(user_id_bc, video_id, caption=caption, parse_mode='Markdown' if caption else None)
                    sent_count += 1
                except Exception as e_retry: logger.error(f"Broadcast retry failed to {user_id_bc}: {e_retry}"); failed_count +=1
            else: logger.error(f"Broadcast failed to {user_id_bc}: {e}"); failed_count += 1
        except Exception as e: logger.error(f"Unexpected error broadcasting to {user_id_bc}: {e}"); failed_count += 1

        if (i + 1) % batch_size == 0 and i < total_users - 1:
            logger.info(f"Broadcast batch {i//batch_size + 1} sent. Sleeping {delay_batches}s...")
            time.sleep(delay_batches)
        elif i % 5 == 0: time.sleep(0.2) 

    duration = round(time.time() - start_exec_time, 2)
    result_msg = (f"📢 Broadcast Complete!\n\n✅ Sent: {sent_count}\n❌ Failed: {failed_count}\n"
                  f"🚫 Blocked/Inactive: {blocked_count}\n👥 Targets: {total_users}\n⏱️ Duration: {duration}s")
    logger.info(result_msg)
    try: bot.send_message(admin_chat_id, result_msg)
    except Exception as e: logger.error(f"Failed to send broadcast result to admin {admin_chat_id}: {e}")

def admin_panel_callback(call):
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text(
                              '🌷💗 𝐇𝐈𝐍𝐀𝐓𝐀 — 𝐀ᴅᴍɪɴ Pᴀɴᴇʟ 💗🌷\n'
                              '━━━━━━━━━━━━━━━━━━\n\n'
                              '📊 𝐒ᴛᴀᴛɪsᴛɪᴄs\n📤 𝐔ᴘʟᴏᴀᴅ Sᴄʀɪᴘᴛ\n'
                              '🟢 𝐑ᴜɴɴɪɴɢ Bᴏᴛs\n⚡ 𝐁ᴏᴛ Sᴛᴀᴛᴜs\n'
                              '💳 𝐒ᴜʙsᴄʀɪᴘᴛɪᴏɴs\n📢 𝐁ʀᴏᴀᴅᴄᴀsᴛ\n'
                              '🔒 𝐋ᴏᴄᴋ Bᴏᴛ\n🟢 𝐑ᴜɴ Aʟʟ Sᴄʀɪᴘᴛs\n'
                              '🛰 𝐒ᴇɴᴅ Cᴏᴍᴍᴀɴᴅ\n👑 𝐀ᴅᴍɪɴ Pᴀɴᴇʟ\n'
                              '💌 𝐂ᴏɴᴛᴀᴄᴛ Oᴡɴᴇʀ\n\n'
                              '━━━━━━━━━━━━━━━━━━',
                              call.message.chat.id, call.message.message_id, reply_markup=create_admin_panel())
    except Exception as e: logger.error(f"Error showing admin panel: {e}")

def add_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "👑 Enter User ID to promote to Admin.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_add_admin_id)

def process_add_admin_id(message):
    owner_id_check = message.from_user.id 
    if owner_id_check != OWNER_ID: bot.reply_to(message, "⚠️ Owner only."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Admin promotion cancelled."); return
    try:
        new_admin_id = int(message.text.strip())
        if new_admin_id <= 0: raise ValueError("ID must be positive")
        if new_admin_id == OWNER_ID: bot.reply_to(message, "⚠️ Owner is already Owner."); return
        if new_admin_id in admin_ids: bot.reply_to(message, f"⚠️ User `{new_admin_id}` already Admin."); return
        add_admin_db(new_admin_id) 
        logger.warning(f"Admin {new_admin_id} added by Owner {owner_id_check}.")
        bot.reply_to(message, f"✅ User `{new_admin_id}` promoted to Admin.")
        try: bot.send_message(new_admin_id, "🎉 Congrats! You are now an Admin.")
        except Exception as e: logger.error(f"Failed to notify new admin {new_admin_id}: {e}")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "👑 Enter User ID to promote or /cancel.")
        bot.register_next_step_handler(msg, process_add_admin_id)
    except Exception as e: logger.error(f"Error processing add admin: {e}", exc_info=True); bot.reply_to(message, "Error.")

def remove_admin_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "👑 Enter User ID of Admin to remove.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_remove_admin_id)

def process_remove_admin_id(message):
    owner_id_check = message.from_user.id
    if owner_id_check != OWNER_ID: bot.reply_to(message, "⚠️ Owner only."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Admin removal cancelled."); return
    try:
        admin_id_remove = int(message.text.strip())
        if admin_id_remove <= 0: raise ValueError("ID must be positive")
        if admin_id_remove == OWNER_ID: bot.reply_to(message, "⚠️ Owner cannot remove self."); return
        if admin_id_remove not in admin_ids: bot.reply_to(message, f"⚠️ User `{admin_id_remove}` not Admin."); return
        if remove_admin_db(admin_id_remove): 
            logger.warning(f"Admin {admin_id_remove} removed by Owner {owner_id_check}.")
            bot.reply_to(message, f"✅ Admin `{admin_id_remove}` removed.")
            try: bot.send_message(admin_id_remove, "ℹ️ You are no longer an Admin.")
            except Exception as e: logger.error(f"Failed to notify removed admin {admin_id_remove}: {e}")
        else: bot.reply_to(message, f"❌ Failed to remove admin `{admin_id_remove}`. Check logs.")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "👑 Enter Admin ID to remove or /cancel.")
        bot.register_next_step_handler(msg, process_remove_admin_id)
    except Exception as e: logger.error(f"Error processing remove admin: {e}", exc_info=True); bot.reply_to(message, "Error.")

def list_admins_callback(call):
    bot.answer_callback_query(call.id)
    try:
        admin_list_str = "\n".join(f"- `{aid}` {'(Owner)' if aid == OWNER_ID else ''}" for aid in sorted(list(admin_ids)))
        if not admin_list_str: admin_list_str = "(No Owner/Admins configured!)"
        bot.edit_message_text(f"👑 Current Admins:\n\n{admin_list_str}", call.message.chat.id,
                              call.message.message_id, reply_markup=create_admin_panel(), parse_mode='Markdown')
    except Exception as e: logger.error(f"Error listing admins: {e}")

def add_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "💳 Enter User ID & days (e.g., `12345678 30`).\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_add_subscription_details)

def process_add_subscription_details(message):
    admin_id_check = message.from_user.id 
    if admin_id_check not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Sub add cancelled."); return
    try:
        parts = message.text.split();
        if len(parts) != 2: raise ValueError("Incorrect format")
        sub_user_id = int(parts[0].strip()); days = int(parts[1].strip())
        if sub_user_id <= 0 or days <= 0: raise ValueError("User ID/days must be positive")

        current_expiry = user_subscriptions.get(sub_user_id, {}).get('expiry')
        start_date_new_sub = datetime.now()
        if current_expiry and current_expiry > start_date_new_sub: start_date_new_sub = current_expiry
        new_expiry = start_date_new_sub + timedelta(days=days)
        save_subscription(sub_user_id, new_expiry)

        logger.info(f"Sub for {sub_user_id} by admin {admin_id_check}. Expiry: {new_expiry:%Y-%m-%d}")
        bot.reply_to(message, f"✅ Sub for `{sub_user_id}` by {days} days.\nNew expiry: {new_expiry:%Y-%m-%d}")
        try: bot.send_message(sub_user_id, f"🎉 Sub activated/extended by {days} days! Expires: {new_expiry:%Y-%m-%d}.")
        except Exception as e: logger.error(f"Failed to notify {sub_user_id} of new sub: {e}")
    except ValueError as e:
        bot.reply_to(message, f"⚠️ Invalid: {e}. Format: `ID days` or /cancel.")
        msg = bot.send_message(message.chat.id, "💳 Enter User ID & days, or /cancel.")
        bot.register_next_step_handler(msg, process_add_subscription_details)
    except Exception as e: logger.error(f"Error processing add sub: {e}", exc_info=True); bot.reply_to(message, "Error.")

def remove_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "💳 Enter User ID to remove sub.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_remove_subscription_id)

def process_remove_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Sub removal cancelled."); return
    try:
        sub_user_id_remove = int(message.text.strip())
        if sub_user_id_remove <= 0: raise ValueError("ID must be positive")
        if sub_user_id_remove not in user_subscriptions:
            bot.reply_to(message, f"⚠️ User `{sub_user_id_remove}` no active sub in memory."); return
        remove_subscription_db(sub_user_id_remove) 
        logger.warning(f"Sub removed for {sub_user_id_remove} by admin {admin_id_check}.")
        bot.reply_to(message, f"✅ Sub for `{sub_user_id_remove}` removed.")
        try: bot.send_message(sub_user_id_remove, "ℹ️ Your subscription removed by admin.")
        except Exception as e: logger.error(f"Failed to notify {sub_user_id_remove} of sub removal: {e}")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "💳 Enter User ID to remove sub from, or /cancel.")
        bot.register_next_step_handler(msg, process_remove_subscription_id)
    except Exception as e: logger.error(f"Error processing remove sub: {e}", exc_info=True); bot.reply_to(message, "Error.")

def check_subscription_init_callback(call):
    bot.answer_callback_query(call.id)
    msg = bot.send_message(call.message.chat.id, "💳 Enter User ID to check sub.\n/cancel to abort.")
    bot.register_next_step_handler(msg, process_check_subscription_id)

def process_check_subscription_id(message):
    admin_id_check = message.from_user.id
    if admin_id_check not in admin_ids: bot.reply_to(message, "⚠️ Not authorized."); return
    if message.text.lower() == '/cancel': bot.reply_to(message, "Sub check cancelled."); return
    try:
        sub_user_id_check = int(message.text.strip())
        if sub_user_id_check <= 0: raise ValueError("ID must be positive")
        if sub_user_id_check in user_subscriptions:
            expiry_dt = user_subscriptions[sub_user_id_check].get('expiry')
            if expiry_dt:
                if expiry_dt > datetime.now():
                    days_left = (expiry_dt - datetime.now()).days
                    bot.reply_to(message, f"✅ User `{sub_user_id_check}` active sub.\nExpires: {expiry_dt:%Y-%m-%d %H:%M:%S} ({days_left} days left).")
                else:
                    bot.reply_to(message, f"⚠️ User `{sub_user_id_check}` expired sub (On: {expiry_dt:%Y-%m-%d %H:%M:%S}).")
                    remove_subscription_db(sub_user_id_check)
            else: bot.reply_to(message, f"⚠️ User `{sub_user_id_check}` in sub list, but expiry missing. Re-add if needed.")
        else: bot.reply_to(message, f"ℹ️ User `{sub_user_id_check}` no active sub record.")
    except ValueError:
        bot.reply_to(message, "⚠️ Invalid ID. Send numerical ID or /cancel.")
        msg = bot.send_message(message.chat.id, "💳 Enter User ID to check, or /cancel.")
        bot.register_next_step_handler(msg, process_check_subscription_id)
    except Exception as e: logger.error(f"Error processing check sub: {e}", exc_info=True); bot.reply_to(message, "Error.")

# --- Cleanup Function ---
def cleanup():
    logger.warning("Shutdown. Cleaning up processes...")
    script_keys_to_stop = list(bot_scripts.keys()) 
    if not script_keys_to_stop: logger.info("No scripts running. Exiting."); return
    logger.info(f"Stopping {len(script_keys_to_stop)} scripts...")
    for key in script_keys_to_stop:
        if key in bot_scripts: logger.info(f"Stopping: {key}"); kill_process_tree(bot_scripts[key])
        else: logger.info(f"Script {key} already removed.")
    logger.warning("Cleanup finished.")
atexit.register(cleanup)

# --- Main Execution ---
if __name__ == '__main__':
    logger.info("="*40 + "\n🤖 Bot Starting Up...\n" + f"🐍 Python: {sys.version.split()[0]}\n" +
                f"🔧 Base Dir: {BASE_DIR}\n📁 Upload Dir: {UPLOAD_BOTS_DIR}\n" +
                f"📊 Data Dir: {IROTECH_DIR}\n🔑 Owner ID: {OWNER_ID}\n🛡️ Admins: {admin_ids}\n" + "="*40)
    keep_alive()
    threading.Thread(target=subscription_expiry_worker, daemon=True).start()
    threading.Thread(
        target=_storage_monitor_worker,
        daemon=True,
        name="safe-storage-monitor",
    ).start()
    logger.info("🚀 Starting polling...")
    while True:
        try:
            bot.infinity_polling(logger_level=logging.INFO, timeout=60, long_polling_timeout=30)
        except requests.exceptions.ReadTimeout: logger.warning("Polling ReadTimeout. Restarting in 5s..."); time.sleep(5)
        except requests.exceptions.ConnectionError as ce: logger.error(f"Polling ConnectionError: {ce}. Retrying in 15s..."); time.sleep(15)
        except Exception as e:
            logger.critical(f"💥 Unrecoverable polling error: {e}", exc_info=True)
            logger.info("Restarting polling in 30s due to critical error..."); time.sleep(30)
        finally: logger.warning("Polling attempt finished. Will restart if in loop."); time.sleep(1)
