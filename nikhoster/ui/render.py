"""Screen -> Telegram message. Edit-in-place = fast & clean (chat spam nahi)."""
from __future__ import annotations

import logging

log = logging.getLogger("nk.render")


def markup_for(screen):
    """Lazy import taaki screens.py bina telebot ke test ho sake."""
    from telebot import types

    kb = types.InlineKeyboardMarkup()
    for row in screen.rows:
        buttons = []
        for btn in row:
            if btn.url:
                buttons.append(types.InlineKeyboardButton(btn.label, url=btn.url))
            else:
                data = btn.data or "nk:noop"
                if len(data.encode("utf-8")) > 64:
                    log.warning("callback data too long, trimming: %s", data)
                    data = data[:64]
                buttons.append(types.InlineKeyboardButton(btn.label, callback_data=data))
        if buttons:
            kb.row(*buttons)
    return kb


def show(ctx, chat_id: int, screen, message_id: int | None = None) -> int | None:
    """Screen ko edit karo (fast path) warna naya message bhejo."""
    bot = ctx.bot
    kb = markup_for(screen)
    if message_id:
        try:
            bot.edit_message_text(screen.text, chat_id, message_id,
                                  reply_markup=kb, parse_mode="HTML",
                                  disable_web_page_preview=True)
            return message_id
        except Exception as exc:
            if "not modified" in str(exc).lower():
                return message_id
            # message purana / delete ho gaya -> naya bhej do
    try:
        msg = bot.send_message(chat_id, screen.text, reply_markup=kb,
                               parse_mode="HTML", disable_web_page_preview=True)
        return msg.message_id
    except Exception as exc:
        log.error("send failed: %s", exc)
        return None


def notify(ctx, chat_id: int, text: str) -> None:
    try:
        ctx.bot.send_message(chat_id, text, parse_mode="HTML",
                             disable_web_page_preview=True)
    except Exception as exc:
        log.warning("notify failed %s: %s", chat_id, exc)


def toast(ctx, callback, text: str) -> None:
    try:
        ctx.bot.answer_callback_query(callback.id, text=text[:190], show_alert=False)
    except Exception:
        pass
