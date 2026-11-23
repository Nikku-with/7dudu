"""Session-string ki asli check — deploy se pehle account verify (faster failures)."""
from __future__ import annotations

import asyncio
import concurrent.futures
import re
import time

SESSION_RE = re.compile(r"^1[0-9A-Za-z_\-+/=]{30,}$")


def looks_like_session(text: str) -> bool:
    text = (text or "").strip().replace("\n", "")
    return bool(SESSION_RE.match(text))


def clean(text: str) -> str:
    return (text or "").strip().replace("\n", "").replace(" ", "")


async def _check(api_id: int, api_hash: str, session: str) -> dict:
    from telethon import TelegramClient  # local import: boot fast rahe
    from telethon.sessions import StringSession

    client = TelegramClient(StringSession(session), int(api_id), api_hash,
                            timeout=10, connection_retries=1,
                            device_model="NIK-HOST", system_version="v1")
    await client.connect()
    try:
        if not await client.is_user_authorized():
            return {"ok": False, "error": "session authorized nahi hai (logout/expired)"}
        me = await client.get_me()
        return {
            "ok": True,
            "name": " ".join(x for x in [me.first_name, me.last_name] if x) or "account",
            "username": me.username or "",
            "id": me.id,
            "phone": me.phone or "",
        }
    finally:
        try:
            await client.disconnect()
        except Exception:
            pass


def verify(api_id: int, api_hash: str, session: str, timeout: float = 18) -> dict:
    """Blocking verify — hamesha thread me chalao."""
    session = clean(session)
    t0 = time.perf_counter()

    def _run():
        return asyncio.run(asyncio.wait_for(_check(int(api_id), api_hash, session),
                                            timeout=timeout))

    try:
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as pool:
            result = pool.submit(_run).result(timeout=timeout + 2)
    except concurrent.futures.TimeoutError:
        return {"ok": False, "error": "telegram se connect nahi hua (timeout)"}
    except ModuleNotFoundError:
        return {"ok": False, "error": "telethon install nahi hai — `pip install telethon`"}
    except Exception as exc:
        msg = str(exc)
        friendly = msg
        if "AUTH_KEY_UNREGISTERED" in msg.upper():
            friendly = "session dead hai (AUTH_KEY_UNREGISTERED)"
        elif "API_ID_INVALID" in msg.upper() or "api_id" in msg.lower():
            friendly = "api id / hash galat hai"
        elif "database is locked" in msg.lower():
            friendly = "session string corrupt hai"
        return {"ok": False, "error": friendly[:200]}

    result["elapsed"] = round(time.perf_counter() - t0, 2)
    return result
