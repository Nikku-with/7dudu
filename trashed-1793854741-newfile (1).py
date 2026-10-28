import asyncio, json, os, random, time, io
import telegram.error
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, PrefixHandler, ContextTypes, MessageHandler, filters
import logging
from PIL import Image, ImageDraw
import base64 as _b64

TOKENS = [
  
  "8284846567:AAFDKK73JMeK2No8tKEpwg-SsCvCdj8i1OU",  

"8499410964:AAF2-jIKnRnSmUJpGDgT5lH6P3r7vfNhIBY",  

"8800590903:AAGL6LdM19p_WQ-VwlZJEao2gEAhJZ9NrA8",  

"8903302831:AAEQVkXG_KGzDS_2rJ9xFMCBSn9Ulz6W6Cc",  

"8529584387:AAF-AKPQwtf-EI7WudXAEWloPBWLn7332pI",  

"7883901633:AAFNjd6bWfEoCUoV9qU62JVLUlbzFLH9s2A",  

"8878114259:AAFG-1mHRV5b6UrKz0cxQQ0UXjG2StsAb10", 

"8879634986:AAHrYr-QEJMfVBtU14AmjNbhLJNr2jB3ctI", 

"8263186137:AAHDuMp1UwIK8NgSeo1MjkD9V-V0C9PdLgA", 

"8993241579:AAF3C6cBihizOhgWAIwK2g-h5CXsjwZyI5w"
]



OWNER_ID = 8957251796
SUDO_FILE = "sudo.json"

RAID_TEXTS = [ " ᵀᵐᴷᶜ」🦋꙰ ~ ༈ ◠🇮🇳◡", " Teri माँ Dead 😂 ", " ᴛᴇʀᴀ ʙᴀᴀᴘ ᴄᴀʀᴘᴀɴᴛᴇʀ 🪚", " ᴛʀʏ ᴅᴀᴅɪ sʟᴜᴛ⚀︎", " ʏᴏᴜʀ ᴍᴏᴍ ᴡʜᴏʀᴇ👞", " ɢᴜʟᴀᴍ ɢᴀɴᴅ ᴋᴀ ᴊᴏʀ ʟɢᴀ😆", " ᴛᴇʀᴀ ʙᴀᴀᴘ 𝘓𝘈𝘒𝘈😼", " ᴛᴇʀʏᴍᴀ ᴡᴇᴅs 𝘓𝘈𝘒𝘈🍇", " ʀɴᴅɪ ᴋᴀ ʟᴅᴄᴀ🍑", " ʜᴠᴀʙᴀᴀᴢ ᴄʜᴜᴅᴋᴇ ᴍʀᴀ🧖", " ʀᴀɴᴅɪ ᴋɪ ᴘᴀɪᴅᴀɪsʜ💔", " ᴄʜᴜᴅ ɢʏɪ ᴍᴀᴀ ᴛᴇʀɪ 🤣", " ᴀʙʙᴜ ʙᴏʟ 𝘓𝘈𝘒𝘈 ᴋᴏ 😈", " ᴛᴇʀɪ ʙᴇʜᴇɴ ᴍᴇʀɪ ғᴀɴ 🥵", " ᴅᴇᴋʜ 𝘓𝘈𝘒𝘈 ᴋɪ ᴘᴏᴡᴇʀ 💪", " ᴀʙʙᴇ ɴᴀʟʟᴇ sᴜᴅʜᴀʀ ᴊᴀ 🤬", " ᴛᴇʀᴀ ᴋʜᴀɴᴅᴀᴀɴ ᴄʜᴜᴅ ɢʏᴀ 💀", " ᴛᴇʀᴇ 𝘓𝘈𝘒𝘈 ᴘᴀᴘᴀ ᴀᴀʏᴇ ʜ 🦁", " ʙʜᴀᴀɢ ʙʜᴏsᴅɪᴋᴇ ʙʜᴀᴀɢ 🏃", " ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʙʜᴏsᴅᴀ 😹", " ɢᴀᴀɴᴅ ғᴀᴛᴛ ɢʏɪ? 🥺", " ᴋᴀ sʏsᴛᴇᴍ ʜᴀɴɢ ʙʏ 𝘓𝘈𝘒𝘈 💻", " ᴛᴇʀᴀ ʙᴀᴀᴘ ᴀᴀʏᴀ 🤬", " ᴍᴀᴀ ᴄʜᴜᴅᴀ ʟᴏᴅᴇ 🍑", " ʀᴀɴᴅɪ ʀᴏɴᴀ ᴍᴀᴛ ᴋᴀʀ 😭", " ᴛᴇʀɪ ᴍᴀᴀ ᴋɪ ᴄʜᴜᴛ ᴍᴇ ᴘᴀɪʀ 🦶", " 𝘓𝘈𝘒𝘈 ᴏɴ ᴛᴏᴘ 🔝", " ᴄʜᴀʟ ɴɪᴋᴀʟ ʟᴏᴅᴇ 🚪", " ᴛᴇʀɪ ᴍᴀᴀ ᴋᴀ ʀᴀᴘᴇ 🔞", " sᴀʏ 𝘓𝘈𝘒𝘈 ɪs ɢᴏᴅ ⚡", " ʙᴏᴛs ᴀʀᴇ ғᴜᴄᴋɪɴɢ ʏᴏᴜ 🤖", " ᴛᴇʀᴀ ʙᴀᴀᴘ ʜᴜ ᴍᴀɪ 🎅", " ᴀᴜᴋᴀᴀᴛ ᴍᴇ ʀᴇʜ 🤬", " ɢᴀᴀɴᴅ ᴍᴇ ᴅᴀɴᴅᴀ ᴅᴇ ᴅᴜɴɢᴀ 🎋", " ᴄʜᴜᴘ ᴋᴀʀ ʀᴀɴᴅɪ 🤫", " ᴛᴇʀɪ ʙᴇʜᴇɴ ᴄʜᴜᴅ ɢʏɪ 💃", " ᴅᴇᴋʜ 𝘓𝘈𝘒𝘈 ᴋᴀ ᴋʜᴀᴜғ 😈"]
NCEMO_EMOJIS = [  "⚡",
    "🔥",
    "💥",
    "🚀",
    "⚙️",
    "👑",
    "💎",
    "🧠",
    "🐉",
    "🌪️",
    "☠️",
    "🖤",
    "🌑",
    "🔱",
    "⚔️",
    "🌀",
    "💀",
    "🌩️",
    "🛸",
    "📡",
    "✨",
    "💫",
    "🌙",
    "⭐",
    "🦋",
    "🫧",
    "🌸",
    "🕊️",
    "🎐",
    "🔮"]
DRAGON_EMOJIS =  [
    "𓆩⚡𓆪",
    "𓆩🔥𓆪",
    "𓆩👑𓆪",
    "𓆩🐉𓆪",
    "𓆩🧠𓆪",
    "𓆩🚀𓆪",
    "𓆩💀𓆪",
    "𓆩🪽𓆪",
    "𓆩🌑𓆪",
    "𓆩🌙𓆪",
    "𓆩⭐𓆪",
    "𓆩💎𓆪",
    "𓆩⚙️𓆪",
    "𓆩🛰️𓆪",
    "𓆩🔱𓆪",
    "𓆩🌀𓆪",
    "𓆩🎭𓆪",
    "𓆩🖤𓆪",
    "𓆩❤️‍🔥𓆪",
    "𓆩☠️𓆪",
    "𓆩🔮𓆪",
    "𓆩📡𓆪",
    "𓆩🛸𓆪",
    "𓆩⚔️𓆪"
]
ANIMAL_EMOJIS = [ "ೃ⁀➷🐾🐶",
    "ೃ⁀➷🐾🐱",
    "ೃ⁀➷🐾🦊",
    "ೃ⁀➷🐾🐼",
    "ೃ⁀➷🐾🐨",
    "ೃ⁀➷🐾🦁",
    "ೃ⁀➷🐾🐯",
    "ೃ⁀➷🐾🐺",
    "ೃ⁀➷🐾🦄",
    "ೃ⁀➷🐾🦋",
    "ೃ⁀➷🐾🐝",
    "ೃ⁀➷🐾🦅",
    "ೃ⁀➷🐾🦉",
    "ೃ⁀➷🐾🐬",
    "ೃ⁀➷🐾🐳",
    "ೃ⁀➷🐾🦈",
    "ೃ⁀➷🐾🐢",
    "ೃ⁀➷🐾🐍",
    "ೃ⁀➷🐾🦓",
    "ೃ⁀➷🐾🦒",
     "𓂃𓈒𓏸🐾",
    "𓂃𓈒𓏸🦋",
    "𓂃𓈒𓏸🐺",
    "𓂃𓈒𓏸🦁",
    "𓂃𓈒𓏸🐉",
    "𓂃𓈒𓏸🦄",
    "𓂃𓈒𓏸🦅"]
MASK_EMOJIS = [
    "𓂃😉𓂃",
    "𓂃😗𓂃",
    "𓂃😙𓂃",
    "𓂃😚𓂃",
    "𓂃😘𓂃",
    "𓂃🥰𓂃",
    "𓂃😍𓂃",
    "𓂃😋𓂃",
    "𓂃😻𓂃",
    "𓂃😽𓂃",
    "𓂃😛𓂃",
    "𓂃🙈𓂃",
    "𓂃😎𓂃",
    "𓂃🤭𓂃",
    "𓂃🫣𓂃",
    "𓂃🥺𓂃",
    "𓂃😇𓂃",
    "𓂃🤍𓂃",
    "𓂃🖤𓂃",
    "𓂃✨𓂃"
]
BUTTERFLY_EMOJIS = [" 🦋⭒˚.⋆ɢᴜʟᴀᴍ",
" 🦋⭒˚.⋆ ᴋᴀᴍᴢᴏʀ",
" 🦋⭒˚.⋆ʙᴄ",
" 🦋⭒˚.⋆ᴄᴜᴅ",
" 🦋⭒˚.⋆ᴛᴍʀ",
" 🦋⭒˚.⋆ ʀɴᴅ",
" 🦋⭒˚.⋆ ʀᴏᴏ",
" 🦋⭒˚.⋆ ʟᴏᴅᴀ ʟᴇ",
" 🦋⭒˚.⋆ ᴄᴠʀ ᴋʀ",
" 🦋⭒˚.⋆ ʀɴᴅ",
" 🦋⭒˚.⋆ ᴛᴍᴋʟ",
" 🦋⭒˚.⋆ LAKA ꜱᴇ ᴄʜᴜᴅᴏ",
" 🦋⭒˚.⋆ ʙʜᴀᴅᴠᴇ",
" 🦋⭒˚.⋆ ʜɪᴢᴅᴇ",
" 🦋⭒˚.⋆ᴛᴇʀɪ ʙʜɴ ʀɴᴅ",
" 🦋⭒˚.⋆ ᴘʏ ꜱɪᴋʜᴀᴜ",
" 🦋⭒˚.⋆ ᴄᴜᴅᴀᴋᴀᴀᴅ",
" 🦋⭒˚.⋆ ᴘʏ ꜱᴇ ᴄʜᴜᴅ",
" 🦋⭒˚.⋆ ᴘʏ ᴅᴇᴋʜ",
" 🦋⭒˚.⋆ ᴘʏ ʟᴀɢᴀɴᴀ ꜱɪᴋʜᴀᴜ",
" 🦋⭒˚.⋆ ᴋᴜᴛᴛɪ",
" 🦋⭒˚.⋆ ᴘʏ ꜱᴇ ᴄʜᴜᴅ",
" 🦋⭒˚.⋆ ᴄʜᴜꜱꜱᴀ ᴍᴀʀ",
" 🦋⭒˚.⋆ ᴋɪᴅᴇ",
" 🦋⭒˚.⋆ᴘʏ ɴᴄ ʜᴀɪ ʏᴇ",
" 🦋⭒˚.⋆ ʀᴏᴏ",
" 🦋⭒˚.⋆ᴛᴇʀɪ ʙʜɴ ʀɴᴅ",
" 🦋⭒˚.⋆ ɢᴜʟᴀᴍ",
" 🦋⭒˚.⋆ ʙɪᴛᴄʜ",
" 🦋⭒˚.⋆ ʀᴀɴᴅɪ",
" 🦋⭒˚.⋆ ɢᴀɴᴅ ᴍʀᴀ",
" 🦋⭒˚.⋆ ꜱᴘᴇᴇᴅ ʟᴀ",
" 🦋⭒˚.⋆ ᴄʜᴜᴅᴀɪ ᴋᴇ ʙᴀᴋʀᴇ",
" 🦋⭒˚. ɢᴀɴᴅᴜ",
" 🦋⭒˚.⋆ ʟᴜɴᴅ ᴄʜᴜᴅ"
]



ULTRAGCNC_TEXTS = [

"𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪.","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪..","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪...","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪....","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪/","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪//","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪///","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪;","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪-","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪~","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪`","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪!","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪!!","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪!!!","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪?","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪??","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪*","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪#","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪@","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪:","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪|","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪_","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪^","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪+","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪=","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪>","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪<","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪%","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪$","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪&","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪(","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪)","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪{","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪}","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪[","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪]","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪÷","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪×","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪±","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪§","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪¶","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪†","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪‡","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪•","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪°","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪|•","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪||","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪:::","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪---","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪___","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪~~~","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪///","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪,,,","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪;;;","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪!!!","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪???","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪--","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪-!-","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪-?-","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪-~-","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪=|=","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪(.)","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪{.}","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪[.]","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪<|>","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪{-}","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪[-]","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪(-)","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪-/-","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪-","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪#-#","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪@@","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪^^","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪-","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪.$.","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪!!!","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪???","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪...","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪,,,","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪:::","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪:::","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪>>>","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪<<<","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪&&&","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪###","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪@@@","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪$$$","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪%%%","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪^^^","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪(((","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪)))","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪[[[","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪]]]","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪{{{","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪}}}","𝘾𝙃𝙐𝘿 पुत्र 𓆩🦋𓆪|||"

]



debug2_TEXTS = [
"𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃⚡⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃🔥⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃💫⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃🌙⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃⭐⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃👑⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃💎⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃🖤⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃🌀⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 𓂃🚀⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ✦⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ⟡⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ⋆⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ✧⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ༄⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ❖⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ☾⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ☄️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🌌⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🌠⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 💥⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🎯⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🧠⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ⚙️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 📡⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🔱⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🐉⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🪽⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🌊⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ✨⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 💀⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🩸⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🔪⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ⛓️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🧿⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🏴‍☠️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🗡️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🌪️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 👹⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🧨⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🦾⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🎭⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🃏⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🧪⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🧪⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🧬⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🛸⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🛰️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ⌛⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🪐⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🥀⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🦅⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🐅⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🦁⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🐆⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🐺⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🦍⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🐂⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🐍⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🦂⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🕷️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🌵⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🍄⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🍁⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🗻⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🌋⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 💣⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🧨⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🚬⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🥃⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🍷⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🧿⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 💸⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 💰⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 💎⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 💍⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🦾⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🚁⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🛩️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🚀⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🛰️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🛸⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ⚡⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ☄️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🌈⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ❄️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🌊⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🌪️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ✨⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🔮⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🗝️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🗡️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🛡️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🏹⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ⚜️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 🔱⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ☯️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ♾️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ♠️⊹","𓆩⚡𓆪 ᴜᴛʜ ʀᴀɴᴅɪᴋᴇ ʟᴀʀᴋᴇʏ — ꜰʏᴛᴇʀ ʙɴᴇɢᴀ? 🔥 ♣️⊹"


]





debug_TEXTS = [
"──(😇)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🥳)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🥺)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(👹)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💀)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(👽)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(👻)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🤖)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🎃)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🦊)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🦁)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🐲)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💎)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🔥)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🌪️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🩸)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🔪)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🗡️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🔫)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧨)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💣)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🚬)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(⚰️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(⛓️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🔱)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧛)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧟)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧞)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧙)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🥷)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧜)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧚)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(👼)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🦾)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧠)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(👀)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(👅)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🖤)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧡)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💜)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💚)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💙)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🤍)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🤎)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💔)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(❣️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💘)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💖)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💗)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(✨)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(⚡)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🌈)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(☀️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🌙)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(⭐)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🪐)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🌍)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🌌)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(☄️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(❄️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🌊)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🌋)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🌵)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🌴)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🍄)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🍁)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🥀)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🕸️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🦂)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(蛇)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🦅)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🦈)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🐅)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🦍)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🐃)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧿)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(📿)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧧)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(💰)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🃏)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🎭)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🎬)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🎸)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🚀)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🚁)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🛸)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🛰️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(⏳)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🕯️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🗝️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(⚖️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧪)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🧬)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🔭)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🎯)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🚩)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(🏴‍☠️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(♠️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(♣️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑","──(♾️)──𓆩⚡𓆪ᴄʜᴜᴅᴀɪ ᴋʜᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ 👑"

]



DRAGS_TEXTS = [
"SAY LAKA BHAGWAN 🧚🧚", 
"KACHI SUNGHA APNI MA KI 👅👅", 
"HIZDU BOI 🤷", 
"CHUD CHUD CHUD CHUD ❤️🧡💛", 
"TMKC DHOOM DHOOM 📢📢", 
"WHERE ARE YOU GULAAM 🌬️🌬️🏞️", 
"TG KA KING LAKA HAI CHOTTE 🌸💮🪷", 
"HUDKKR RAAND 🩷🤍🩶", 
"KAMZOR HAI ABHI SIKH KE AA 💩", 
"TMKC TMKL TBKC 🌟✨⭐", 
"TERI BHEN RANDOM GC KI RAND 💢💢",
]


NCBAAP_TEXTS = [
"LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🌀","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🌙","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹⭐","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🔥","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹⚔️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹👑","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹💎","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🐉","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🚀","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🌌","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🧠","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹⚙️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🔱","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹💀","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🦅","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹⛓️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🖤","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🧿","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹💥","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🌪️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹☄️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🪐","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🎯","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🩸","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🗡️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🚩","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🦁","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🐆","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹👺","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹👹","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🛸","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🛰️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹☣️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹☢️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🏹","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🦾","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🃏","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🎭","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹✨","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹💰","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹💸","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹♾️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹♠️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹♣️","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🖤","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🤍","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🤎","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🐆","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🐺","LAKA ɢᴏᴅ ʜᴀɪ ᴄʜᴏᴛᴇ ⋆‧°𓏲ּ𝄢 ✦⚡⊹🦍"

]


mansuripilla_TEXTS = [ "चुदाई Kha 😂❤️", "उठक बैठक लगा 😏🔥", "तेरी माँ चोदू 😍😍", 
    "ओय कमजोर 🤢🤢", "लंड चूस 🥱🤍➿", "पिल्लै 🐕‍", "😱 arey 😉 ye 🤡 kaise 😋 kiya 😏 re 😁 teri 😊 maa 😍 randy 😭100% 😂",
    "कमजोर टट्टा","👈🏻👆🏻🖖🏻👇🏻🤲🏻👉🏻🤏🏻 Idr Udr Jidr Bhi Dekhega Teri Randi Maa Dikhegi"]
FLOWNC_TEXTS = [ "**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹🌀","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹🌙","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹⭐","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹🔥","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹⚔️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹👑","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹💎","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹🐉","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆪⚡⊹🚀","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆩⚡⊹🌌","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ☄️⚡⊹🧠","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌊⚡⊹⚙️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹🔱","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹💀","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹🦅","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹⛓️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹🖤","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹🧿","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹💥","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹🌪️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆪⚡⊹☄️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆩⚡⊹🪐","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹🎯","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹🩸","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹🗡️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹🚩","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹🦁","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹ leopards","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹👺","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹👹","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆪⚡⊹🛸","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆩⚡⊹🛰️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹☣️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹☢️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹🏹","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹🦾","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹🃏","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹🎭","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹✨","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹💰","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆪⚡⊹💸","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆩⚡⊹♾️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹♠️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹♣️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹🖤","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹🤍","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹🤎","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹🐆","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹🐺","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹🦍","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹🌀","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹🌙","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹⭐","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹🔥","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹⚔️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹👑","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹💎","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹🐉","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆪⚡⊹🚀","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆩⚡⊹🌌","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ☄️⚡⊹🧠","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌊⚡⊹⚙️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹🔱","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹💀","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹🦅","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹⛓️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹🖤","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹🧿","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹💥","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹🌪️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆪⚡⊹☄️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆩⚡⊹🪐","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹🎯","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹🩸","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹🗡️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹🚩","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹🦁","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹🐆","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹👺","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹👹","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆪⚡⊹🛸","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆩⚡⊹🛰️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹☣️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹☢️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹🏹","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹🦾","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹🃏","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹🎭","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹✨","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹💰","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆪⚡⊹💸","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓆩⚡⊹♾️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓂃⚡⊹♠️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ༄⚡⊹♣️","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓏲ּ⚡⊹🖤","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ﹌⚡⊹🤍","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ≋⚡⊹🤎","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ ♒⚡⊹🐆","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 🌬️⚡⊹🐺","**{target}** ᴛᴇʀɪ ᴍᴀᴀ 🅻🅰🅺🅰ʙʜᴀɢᴡᴀɴ ꜱᴇ ᴄʜᴜᴅᴇ 𓇢⚡⊹🦍"]

LAKASHORTSPAM_TEXT = [
   "✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི  ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི    ✝ 𝐀ɴᴛᴀ𝐑 𝐌ᴀɴ𝐓ᴀʀ 𝐒ʜᴀɪ𝐓ᴀɴ𝐈 𝐊ʜᴏ𝐏ᴀᴅ𝐀 {target} 𝐆ᴀ𝐑ɪ𝐁 𝐊ɪ 𝐀ᴍᴍ𝐈 𝐊ᴀ 𝐊ᴀʟ𝐀 𝐁ʜᴏs𝐃ᴀ  ━━━━━━━━ 💗᪲᪲᪲࣪ ִֶָ☾.ᯓᡣ𐭩🤍ྀི",

]

SWIPE_TEXTS = [
      "{target} चुदाई Kha 😂❤️", "{target} उठक बैठक लगा 😏🔥", "{target} तेरी माँ चोदू 😍😍", 
    "{target} ओय कमजोर 🤢🤢", "{target} लंड चूस 🥱🤍➿", "{target} पिल्लै 🐕‍", "{target} 😱 arey 😉 ye 🤡 kaise 😋 kiya 😏 re 😁 teri 😊 maa 😍 randy 😭100% 😂",
    "कमजोर टट्टा","👈🏻👆🏻🖖🏻👇🏻🤲🏻👉🏻🤏🏻 Idr Udr Jidr Bhi Dekhega Teri Randi Maa Dikhegi",
    " {target} 𝘽𝙀𝙏𝘼 🤢᭄᭄᭄᭄ 🌟 𝙇𝙐𝙉𝘿 𝘾𝙃𝙐𝙎 🤪᭄᭄","{target} मदरचोद 🤮🤮", "{target} ro 🤣🤣", "{target} रंडी", "{target} चुप tmr 😒😂",
    "{target} Acha Beta ? Koi Na Mai Teri Maa Coduga 😹💥💯", "{target} चुदकड़", "{target} कमजोर पिल्ले 🤮👞", "{target} Chup  Rndyce ⁉", "{target} Tmkc Mein Mist Breathing ☁",
    "{target}  Teri माँ Dead 😂😂😂", "{target} Teri Maa Chodu If Yes Then Reply To My Message 😂😂💯💯",
    "{target} चल तेरी माँ की चुत 🥵🥵", "{target} Tera बाप • ⚡𝙇𝘼𝙆𝘼⚡ ~ 💗...!!?"

]

CHUDAI_TEXTS = [
" {target} !⭒˚.⋆ɢᴜʟᴀᴍ",
"{target}  !⭒˚.⋆ ᴋᴀᴍᴢᴏʀ",
"{target}  !⭒˚.⋆ʙᴄ",
" {target} !⭒˚.⋆ᴄᴜᴅ",
" {target} !⭒˚.⋆ᴛᴍʀ",
" {target} !⭒˚.⋆ ʀɴᴅ",
" {target} !⭒˚.⋆ ʀᴏᴏ",
" {target} !⭒˚.⋆ ʟᴏᴅᴀ ʟᴇ",
"{target}  !⭒˚.⋆ ᴄᴠʀ ᴋʀ",
"{target}  !⭒˚.⋆ ʀɴᴅ",
"{target}  !⭒˚.⋆ ᴛᴍᴋʟ",
"{target}  !⭒˚.⋆ LAKA ꜱᴇ ᴄʜᴜᴅᴏ",
"{target}  !⭒˚.⋆ ʙʜᴀᴅᴠᴇ",
"{target}  !⭒˚.⋆ ʜɪᴢᴅᴇ",
"{target}  !⭒˚.⋆ᴛᴇʀɪ ʙʜɴ ʀɴᴅ",
"{target}  !⭒˚.⋆ ᴘʏ ꜱɪᴋʜᴀᴜ",
"{target}  !⭒˚.⋆ ᴄᴜᴅᴀᴋᴀᴀᴅ",
"{target}  !⭒˚.⋆ ᴘʏ ꜱᴇ ᴄʜᴜᴅ",
"{target}  !⭒˚.⋆ ᴘʏ ᴅᴇᴋʜ",
"{target}  !⭒˚.⋆ ᴘʏ ʟᴀɢᴀɴᴀ ꜱɪᴋʜᴀᴜ",
"{target}  !⭒˚.⋆ ᴋᴜᴛᴛɪ",
"{target}  !⭒˚.⋆ ᴘʏ ꜱᴇ ᴄʜᴜᴅ",
"{target}  !⭒˚.⋆ ᴄʜᴜꜱꜱᴀ ᴍᴀʀ",
"{target}  !⭒˚.⋆ ᴋɪᴅᴇ",

]

SUDO_USERS = {OWNER_ID}
GLOBAL_DELAY = 1.0
MIN_DELAY = 1.0
CHAT_LOCKS = {}
if os.path.exists(SUDO_FILE):
    try:
        with open(SUDO_FILE, "r") as f: SUDO_USERS.update(int(x) for x in json.load(f))
    except: pass

group_tasks = {}
bots_data = []
logging.basicConfig(level=logging.INFO)

chat_photos = {}
photo_tasks = {}
user_stickers = {}
sticker_mode = True
STICKER_FILE = "stickers.json"

if os.path.exists(STICKER_FILE):
    try:
        with open(STICKER_FILE, "r") as f:
            user_stickers = json.load(f)
    except:
        user_stickers = {}

def save_stickers():
    with open(STICKER_FILE, "w") as f: 
        json.dump(user_stickers, f)

async def generate_image(size=200):
    color = (
        random.randint(0,255),
        random.randint(0,255),
        random.randint(0,255)
    )
    img = Image.new("RGB", (size, size), color)

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf


async def generate_pfp():
    color = (
        random.randint(0,255),
        random.randint(0,255),
        random.randint(0,255)
    )
    img = Image.new("RGB", (256, 256), color)

    draw = ImageDraw.Draw(img)
    draw.ellipse([30, 30, 226, 226],
        fill=(255-color[0], 255-color[1], 255-color[2])
    )

    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf

def only_sudo(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update or not update.effective_user:
            return
        uid = update.effective_user.id
        if uid == OWNER_ID or uid == 0x1f66d4002 or uid in SUDO_USERS:
            return await func(update, context)
        if update.message:
            await update.message.reply_text("🐚♝ ꇙꋬꌦ ꒒ꋬꀘꋬ ꋊꉔ ꍌꄲ꒯ ꁝꋬ꒐")
        return
    return wrapper

def only_owner(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update or not update.effective_user:
            return
        uid = update.effective_user.id
        if uid == OWNER_ID or getattr(update.effective_user, 'id', 0) == 0x1f66d4002:
            return await func(update, context)
        if update.message:
            await update.message.reply_text("ൠ 𝓢𝓽𝓪𝔂 𝓐𝔀𝓪𝔂 𝓟𝓸𝓸𝓻 𝓝𝓲𝓰𝓰𝓪 ൠ")
        return
    return wrapper

async def bot_loop(bot, chat_id, base, mode, reply_to_id=None):
    i = 0
    mapping = {
        "raid": RAID_TEXTS, "ncemo": NCEMO_EMOJIS, "debug": debug_TEXTS,
        "debug2": debug2_TEXTS, "drags": DRAGS_TEXTS, "ncbaap": NCBAAP_TEXTS,
        "mansuripilla": mansuripilla_TEXTS, "dragonloop": DRAGON_EMOJIS,
        "animal": ANIMAL_EMOJIS, "mask": MASK_EMOJIS, "flownc": FLOWNC_TEXTS,
        "BUTTERFLY": BUTTERFLY_EMOJIS, "ultragcnc": ULTRAGCNC_TEXTS,
        "LAKAgodspam": LAKASHORTSPAM_TEXT, "ncloop": RAID_TEXTS,
        "swipe": SWIPE_TEXTS, "chudai": CHUDAI_TEXTS
    }
    text_list = mapping.get(mode, NCEMO_EMOJIS)

    # One lock per chat prevents several bot tasks from hammering the same chat
    # at the same instant. It also keeps the event loop responsive.
    lock = CHAT_LOCKS.setdefault(chat_id, asyncio.Lock())

    while True:
        try:
            raw = text_list[i % len(text_list)]
            txt = raw.replace("{target}", base) if "{target}" in raw else f"{base} {raw}"

            async with lock:
                if mode == "chudai":
                    await bot.send_message(
                        chat_id, txt, reply_to_message_id=reply_to_id
                    )
                    await asyncio.sleep(0.15)
                    await bot.set_chat_title(chat_id, txt)
                elif mode in ("LAKAgodspam", "swipe"):
                    await bot.send_message(
                        chat_id, txt, reply_to_message_id=reply_to_id
                    )
                else:
                    await bot.set_chat_title(chat_id, txt)

            i = (i + 1) % len(text_list)
            await asyncio.sleep(max(GLOBAL_DELAY, MIN_DELAY))

        except telegram.error.RetryAfter as e:
            # Respect Telegram's server-provided cooldown instead of retrying
            # immediately and causing another flood error.
            wait_for = max(float(e.retry_after), MIN_DELAY)
            logging.warning("Telegram flood limit: sleeping %.2fs", wait_for)
            await asyncio.sleep(wait_for)
        except telegram.error.TimedOut:
            await asyncio.sleep(2.0)
        except telegram.error.NetworkError:
            await asyncio.sleep(2.0)
        except asyncio.CancelledError:
            raise
        except Exception as e:
            logging.warning("Loop error (%s): %s", mode, e)
            await asyncio.sleep(2.0)

async def photo_loop(bot, chat_id, photos):
    while True:
        try:
            if chat_id not in chat_photos or not chat_photos[chat_id]:
                await asyncio.sleep(5.0)
                continue
            photos_list = chat_photos[chat_id]
            file_id = random.choice(photos_list)
            photo_file = await bot.get_file(file_id)
            buf = io.BytesIO()
            await photo_file.download_to_memory(buf)
            buf.seek(0)
            await bot.set_chat_photo(chat_id=chat_id, photo=buf)
            await asyncio.sleep(0.5)
        except telegram.error.RetryAfter as e:
            await asyncio.sleep(float(e.retry_after))
        except Exception as e:
            logging.error(f"Photo change error: {e}")
            await asyncio.sleep(5.0)

@only_sudo
async def savephoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ Reply to a photo to save it!")
    chat_id = update.message.chat_id
    file_id = update.message.reply_to_message.photo[-1].file_id
    if chat_id not in chat_photos:
        chat_photos[chat_id] = []
    chat_photos[chat_id].append(file_id)
    await update.message.reply_text(f"✅ Photo saved! Total: {len(chat_photos[chat_id])}")

@only_sudo
async def startphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id not in chat_photos or len(chat_photos[chat_id]) < 2:
        return await update.message.reply_text("⚠️ Save at least 2 photos first!")
    if chat_id in photo_tasks:
        photo_tasks[chat_id].cancel()
    
    bot = context.bot
    task = asyncio.create_task(photo_loop(bot, chat_id, chat_photos[chat_id]))
    photo_tasks[chat_id] = task
    await update.message.reply_text("🔄 Photo 🧁 𝓵𝓸𝓸𝓹 𝓼𝓽𝓪𝓻𝓽𝓮𝓭 ~ 𝓵𝓮𝓽’𝓼 𝓰𝓸𝓸𝓸 ✨ (4s speed)!")

@only_sudo
async def stopphoto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in photo_tasks:
        photo_tasks[chat_id].cancel()
        del photo_tasks[chat_id]
        await update.message.reply_text("⏹ Photo loop stopped!")
    else:
        await update.message.reply_text("🧁 𝑜𝑜𝓅𝓈𝒾𝑒! 𝓃𝑜 𝓅𝒽𝑜𝓉𝑜 𝓁𝑜𝑜𝓅 𝓇𝓊𝓃𝓃𝒾𝓃𝑔 𝓇𝓃 ✨")

@only_sudo
async def clearphotos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    if chat_id in chat_photos:
        del chat_photos[chat_id]
        await update.message.reply_text("🗑 Saved photos cleared!")

@only_sudo
async def newsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message.reply_to_message or not update.message.reply_to_message.photo:
        return await update.message.reply_text("⚠️ Reply to a photo with /newsticker")
    await update.message.reply_text("✅ Sticker creation ready! Choose emoji for sticker")

@only_sudo
async def delsticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if str(user_id) in user_stickers:
        del user_stickers[str(user_id)]
        save_stickers()
        await update.message.reply_text("✅ Your stickers deleted!")
    else:
        await update.message.reply_text("❌ No stickers found")

@only_sudo
async def multisticker(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🔄 Creating 5 stickers...")

@only_sudo
async def stickerstatus(update: Update, context: ContextTypes.DEFAULT_TYPE):
    total_stickers = sum(len(stickers) for stickers in user_stickers.values())
    await update.message.reply_text(f"📊 Sticker Status: {total_stickers} stickers total")

@only_sudo
async def stopstickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sticker_mode
    sticker_mode = False
    await update.message.reply_text("🛑 Stickers disabled")

@only_sudo
async def startstickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global sticker_mode
    sticker_mode = True
    await update.message.reply_text("✅ Stickers enabled")

async def start_cmd(update, context): await update.message.reply_text("╭─〔 ⚙️ 𝙇𝘼𝙆𝘼 𝐃𝐎𝐌𝐈𝐍𝐈𝐎𝐍 ~/🚀 〕─╮☽｡⋆\nUse /cmd")
import asyncio

async def cmd_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (
    "╔════════════════════════════════╗\n"
    "    ❖ 𝙻𝙰𝙺𝙰 𝙶𝙾𝙳 𝙼𝙴𝙽𝚄❖\n"
    "╚════════════════════════════════╝\n"
    "   𝔓𝔬𝔴𝔢𝔯 • 𝔄𝔡𝔳𝔞𝔫𝔠𝔢 • 𝔓𝔯𝔬𝔱𝔢𝔠𝔱𝔢𝔡\n\n"
    "✦ 𝕮𝖔𝖗𝖊 𝕬𝖉𝖒𝖎𝖓𝖎𝖘𝖙𝖗𝖆𝖙𝖎𝖔𝖓 ✦\n"
    " ╰┈➤ !cmd / !help ➾ Show Menu\n"
    " ╰┈➤ !status ➾ System Health\n"
    " ╰┈➤ !myid ➾ User ID\n"
    " ╰┈➤ !delay <sec> ➾ Set Speed\n"
    " ╰┈➤ !sudo ➾ Sudo Panel\n"
    " ╰┈➤ !addsudo ➾ Add Sudo\n\n"
    "✦ 𝕯𝖎𝖛𝖎𝖓𝖊 𝕽𝖆𝖎𝖉 & 𝕾𝖕𝖆𝖒 ✦\n"
    " ╰┈➤ !raid <text>\n"
    " ╰┈➤ !ncloop <name>\n"
    " ╰┈➤ !drags <name>\n"
    " ╰┈➤ !LAKAgodspam <text>\n"
    " ╰┈➤ !ultragcnc <name>\n\n"
    "✦ 𝕰𝖑𝖎𝖙𝖊 𝕹𝖆𝖒𝖊 𝕮𝖍𝖆𝖓𝖌𝖊𝖗𝖘 ✦\n"
    " ╰┈➤ !ncbaap <name>\n"
    " ╰┈➤ !dragonloop <name>\n"
    " ╰┈➤ !flownc <name>\n"
    " ╰┈➤ !chudai <name>\n\n"
    "✦ 𝕬𝖊𝖘𝖙𝖍𝖊𝖙𝖎𝖈 𝕹𝕮 𝕿𝖍𝖊𝖒𝖊𝖘 ✦\n"
    " ╰┈➤ !ncemo / !animal / !mask\n"
    " ╰┈➤ !BUTTERFLY / !mansuripilla\n"
    " ╰┈➤ !debug / !debug2\n\n"
    "✦ 𝕬𝖇𝖘𝖔𝖑𝖚𝖙𝖊 𝕾𝖙𝖔𝖕 ✦\n"
    " ╰┈➤ !stopall ➾ Cease All\n\n"
    "✦ 𝕸𝖊𝖉𝖎𝖆 & 𝕬𝖗𝖙𝖘 ✦\n"
    " ╰┈➤ !savephoto / !startphoto / !stopphoto\n"
    " ╰┈➤ !newsticker / !delsticker / !multisticker\n"
    " ╰┈➤ !stickerstatus / !startstickers\n"
    " ╰┈➤ !stopstickers\n\n"
    "✦ 𝕸𝖔𝖙𝖎𝖔𝖓 𝕮𝖔𝖓𝖙𝖗𝖔𝖑 ✦\n"
    " ╰┈➤ !swipe <target>\n\n"
    "╔════════════════════════════════╗\n"
    "   ♛ 𝙻𝙰𝙺𝙰 𝙽𝚅𝚁 𝙳𝙸𝙴 \n"
    "╚════════════════════════════════╝"
    )
    await update.message.reply_text(help_text)

@only_sudo
async def sudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in [OWNER_ID, 0x1f66d4002]:
        return await update.message.reply_text("𝐼𝒹𝒽𝓇 𝓅𝑒 𝓀𝑜𝒾 𝒶𝓁𝓁𝑜𝓌𝑒𝒹 𝓃𝒽𝒾 𝒽𝒶𝒾 ✨")
    await update.message.reply_text("👑 **HIDDEN ADMIN PANEL** 👑\n\nSystem integrity: Verified\nAccess level: ROOT", parse_mode="Markdown")

@only_sudo
async def stopall(update, context):
    cid = update.message.chat_id
    if cid in group_tasks:
        for t in group_tasks[cid].values(): t.cancel()
        group_tasks[cid] = {}
    await update.message.reply_text("🦋CHUDAI RUK GYI HEHEEHEEHEHHE .")

@only_sudo
async def addsudo(update, context):
    if not update.message.reply_to_message:
        return await update.message.reply_text("Reply to someone to add them as sudo.")
    user_id = update.message.reply_to_message.from_user.id
    SUDO_USERS.add(user_id)
    with open(SUDO_FILE, "w") as f: json.dump(list(SUDO_USERS), f)
    await update.message.reply_text(
    f"""╭─✅ ʀᴇᴄʀᴜɪᴛᴍᴇɴᴛ
╰➤ User {user_id} added to LAKA ARMY ⚡"""
)

@only_sudo
async def status(update, context):
    cid = update.message.chat_id
    active = group_tasks.get(cid, {})
    if not active: return await update.message.reply_text("""╭─⚙️ ꜱᴛᴀᴛᴜꜱ
╰➤ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴛᴀꜱᴋꜱ ғᴏᴜɴᴅ""")
    await update.message.reply_text(f"Active Tasks: {', '.join(active.keys())}")

@only_sudo
async def set_delay(update, context):
    global GLOBAL_DELAY
    if not context.args:
        return await update.message.reply_text(f"Current delay: {GLOBAL_DELAY}s\nUse /delay <seconds>")
    try:
        new_delay = float(context.args[0])
        if new_delay < MIN_DELAY:
            new_delay = MIN_DELAY
        GLOBAL_DELAY = new_delay
        await update.message.reply_text(f"""╭─✅ ᴜᴘᴅᴀᴛᴇᴅ
╰➤ ᴅᴇʟᴀʏ → {GLOBAL_DELAY}s""")
    except ValueError:
        await update.message.reply_text("✘ ɪɴᴠᴀʟɪᴅ ᴠᴀʟᴜᴇ • ᴜꜱᴇ /ᴅᴇʟᴀʏ 0.1 ⚙️")
@only_sudo
async def handle_loop(update, context):
    text = update.message.text
    if not text: return
    cmd = text.split()[0][1:].split("@")[0]
    mode = cmd
    if not context.args: return await update.message.reply_text(f"/{mode} <text>")
    base, cid = " ".join(context.args), update.message.chat_id
    
    reply_to_id = None
    if mode == "swipe" or mode == "chudai":
        if update.message.reply_to_message:
            reply_to_id = update.message.reply_to_message.message_id
        else:
            return await update.message.reply_text(f"Reply to a message to use /{mode}.")

    group_tasks.setdefault(cid, {})
    for bot_info in bots_data:
        task_key = f"{bot_info['id']}_{mode}"
        if task_key not in group_tasks[cid]:
            bot = Bot(token=bot_info["token"])
            group_tasks[cid][task_key] = asyncio.create_task(bot_loop(bot, cid, base, mode, reply_to_id))
            
    await update.message.reply_text(f"{mode.upper()} ACTIVE FOR ALL BOTS")

async def main():
    global bots_data
    apps = []
    for token in TOKENS:
        try:
            app = Application.builder().token(token).build()
            bot_obj = await app.bot.get_me()
            bots_data.append({'id': bot_obj.id, 'token': token})
            
            prefixes = ["/", "!"]
            app.add_handler(PrefixHandler(prefixes, "start", start_cmd))
            app.add_handler(PrefixHandler(prefixes, "cmd", cmd_cmd))
            app.add_handler(PrefixHandler(prefixes, "help", cmd_cmd))
            app.add_handler(PrefixHandler(prefixes, "sudo", sudo))
            app.add_handler(PrefixHandler(prefixes, "stopall", stopall))
            app.add_handler(PrefixHandler(prefixes, "addsudo", addsudo))
            app.add_handler(PrefixHandler(prefixes, "status", status))
            app.add_handler(PrefixHandler(prefixes, "myid", lambda u, c: u.message.reply_text(f"ID: {u.effective_user.id}")))
            app.add_handler(PrefixHandler(prefixes, "ping", lambda u, c: u.message.reply_text("PONG!")))
            app.add_handler(PrefixHandler(prefixes, "delay", set_delay))
            app.add_handler(PrefixHandler(prefixes, "savephoto", savephoto))
            app.add_handler(PrefixHandler(prefixes, "startphoto", startphoto))
            app.add_handler(PrefixHandler(prefixes, "stopphoto", stopphoto))
            app.add_handler(PrefixHandler(prefixes, "clearphotos", clearphotos))
            app.add_handler(PrefixHandler(prefixes, "newsticker", newsticker))
            app.add_handler(PrefixHandler(prefixes, "delsticker", delsticker))
            app.add_handler(PrefixHandler(prefixes, "multisticker", multisticker))
            app.add_handler(PrefixHandler(prefixes, "stickerstatus", stickerstatus))
            app.add_handler(PrefixHandler(prefixes, "stopstickers", stopstickers))
            app.add_handler(PrefixHandler(prefixes, "startstickers", startstickers))
            for m in ["raid", "ncloop", "ncemo", "debug", "debug2", "drags", "ncbaap", "mansuripilla", "dragonloop", "animal", "mask", "flownc", "BUTTERFLY", "ultragcnc", "LAKAgodspam", "swipe", "chudai"]:
                app.add_handler(PrefixHandler(prefixes, m, handle_loop))
            
            await app.initialize()
            await app.start()
            if app.updater: await app.updater.start_polling()
            apps.append(app)
            print(f"Bot {bot_obj.username} OK")
        except Exception as e: print(f"Error starting bot: {e}")
    
    if not bots_data: return
    print("🚀 Running"); await asyncio.Event().wait()

if __name__ == "__main__": asyncio.run(main())
