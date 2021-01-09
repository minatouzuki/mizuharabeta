from mizuhara.__main__ import Mizuhara
from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message,
    CallbackQuery,
)
from mizuhara import PREFIX_HANDLER, LOGGER
from mizuhara.utils.msg_types import Types, get_note_type
from mizuhara.utils.string import parse_button, build_keyboard
from mizuhara.db import notes_db as db
from mizuhara.utils.admin_check import admin_check, owner_check


__PLUGIN__ = "Notes"
__help__ = """
Save a note, get that, even you can delete that note.
This note only avaiable for yourself only!
Also notes support inline button powered by inline query assistant bot.
**Save Note**
/save <note>
Save a note, you can get or delete that later.
**Get Note**
/get <note>
Get that note, if avaiable.
**Delete Note**
/clear <note>
Delete that note, if avaiable.
/clearall
Clears all notes in the chat!
**NOTE:** Can only be used by owner of chat!
**All Notes**
/saved or /notes
Get all your notes, if too much notes, please use this in your saved message instead!
── **Note Format** ──
-> **Button**
`[Button Text](buttonurl:github.com)`
-> **Bold**
`**Bold**`
-> __Italic__
`__Italic__`
-> `Code`
`Code` (grave accent)
"""

GET_FORMAT = {
    Types.TEXT.value: Mizuhara.send_message,
    Types.DOCUMENT.value: Mizuhara.send_document,
    Types.PHOTO.value: Mizuhara.send_photo,
    Types.VIDEO.value: Mizuhara.send_video,
    Types.STICKER.value: Mizuhara.send_sticker,
    Types.AUDIO.value: Mizuhara.send_audio,
    Types.VOICE.value: Mizuhara.send_voice,
    Types.VIDEO_NOTE.value: Mizuhara.send_video_note,
    Types.ANIMATION.value: Mizuhara.send_animation,
    Types.ANIMATED_STICKER.value: Mizuhara.send_sticker,
    Types.CONTACT: Mizuhara.send_contact,
}


@Mizuhara.on_message(filters.command("save", PREFIX_HANDLER) & filters.group)
async def save_note(c: Mizuhara, m: Message):

    res = await admin_check(c, m)
    if not res:
        return

    note_name, text, data_type, content = get_note_type(m)

    if not note_name:
        await m.reply_text(
            "```" + m.text + "```\n\nError: You must give a name for this note!"
        )
        return

    if data_type == Types.TEXT:
        teks, _ = parse_button(text)
        if not teks:
            await m.reply_text(
                "```" + m.text + "```\n\nError: There is no text in here!"
            )
            return

    db.save_note(str(m.chat.id), note_name, text, data_type, content)
    await m.reply_text(f"Saved note `{note_name}`!")
    return


@Mizuhara.on_message(filters.command("get", PREFIX_HANDLER) & filters.group)
async def get_note(c: Mizuhara, m: Message):
    if len(m.text.split()) >= 2:
        note = m.text.split()[1]
    else:
        await m.reply_text("Give me a note tag!")

    getnotes = db.get_note(m.chat.id, note)
    if not getnotes:
        await m.reply_text("This note does not exist!")
        return

    if getnotes["type"] == Types.TEXT:
        teks, button = parse_button(getnotes.get("value"))
        button = build_keyboard(button)
        button = InlineKeyboardMarkup(button) if button else None
        if button:
            try:
                await m.reply_text(teks, reply_markup=button)
                return
            except Exception as ef:
                await m.reply_text("An error has accured! Cannot parse note.")
                LOGGER.error(ef)
                return
        else:
            await m.reply_text(teks)
            return
    elif getnotes["type"] in (
        Types.STICKER,
        Types.VOICE,
        Types.VIDEO_NOTE,
        Types.CONTACT,
        Types.ANIMATED_STICKER,
    ):
        await GET_FORMAT[getnotes["type"]](m.chat.id, getnotes["file"])
    else:
        if getnotes.get("value"):
            teks, button = parse_button(getnotes.get("value"))
            button = build_keyboard(button)
            button = InlineKeyboardMarkup(button) if button else None
        else:
            teks = None
            button = None
        if button:
            try:
                await m.reply_text(teks, reply_markup=button)
                return
            except Exception as ef:
                await m.reply_text("An error has accured! Cannot parse note.")
                LOGGER.error(ef)
                return
        else:
            await GET_FORMAT[getnotes["type"]](
                m.chat.id, getnotes["file"], caption=teks
            )
    return


@Mizuhara.on_message(filters.command(["notes", "saved"], PREFIX_HANDLER) & filters.group)
async def local_notes(c: Mizuhara, m: Message):
    getnotes = db.get_all_notes(m.chat.id)
    if not getnotes:
        await m.reply_text(f"There are no notes in <b>{m.chat.title}</b>.")
        return
    rply = f"**Notes in <b>{m.chat.title}</b>:**\n"
    for x in getnotes:
        if len(rply) >= 1800:
            await m.reply(rply)
            rply = f"**Notes in <b>{m.chat.title}</b>:**\n"
        rply += f"- `{x}`\n"

    await m.reply_text(rply)
    return


@Mizuhara.on_message(filters.command("clear", PREFIX_HANDLER) & filters.group)
async def clear_note(c: Mizuhara, m: Message):

    res = await admin_check(c, m)
    if not res:
        return

    if len(m.text.split()) <= 1:
        await m.reply_text("What do you want to clear?")
        return

    note = m.text.split()[1]
    getnote = db.rm_note(m.chat.id, note)
    if not getnote:
        await m.reply_text("This note does not exist!")
        return

    await m.reply_text(f"Deleted note `{note}`!")
    return


@Mizuhara.on_message(filters.command("clearall", PREFIX_HANDLER) & filters.group)
async def clear_allnote(c: Mizuhara, m: Message):

    res = await owner_check(c, m)
    if not res:
        return

    all_notes = db.get_all_notes(m.chat.id)
    if not all_notes:
        await m.reply_text("No notes are there in this chat")
        return

    await m.reply_text(
        "Are you sure you want to clear all notes?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("⚠️ Confirm", callback_data="clear.notes"),
                    InlineKeyboardButton("❌ Cancel", callback_data="close"),
                ]
            ]
        ),
    )
    return


@Mizuhara.on_callback_query(filters.regex("^clear.notes$"))
async def clearallnotes_callback(c: Mizuhara, q: CallbackQuery):
    await q.message.edit_text("Clearing all notes...!")
    db.rm_all_note(q.message.chat.id)
    await q.message.edit_text(f"Cleared all notes!")
    await q.answer()
    return
