import telegraph
from mizuhara import PREFIX_HANDLER
from mizuhara.__main__ import Mizuhara
from pyrogram import filters
from pyrogram.types import Message

__PLUGIN__ = "Telegraph"

__help__ = """
Uploads a picture, video or text to telegraph.
 × /telegraph: As a reply to picture, video or message to upload to telegraph.
"""


@Mizuhara.on_message(
    filters.command("telegraph", PREFIX_HANDLER) & (filters.group | filters.private)
)
async def telegraph_oof(c: Mizuhara, m: Message):
    if m.reply_to_message:
        if (
            m.reply_to_message.photo
            or m.reply_to_message.video
            or m.reply_to_message.animation
        ):
            d_file = await m.reply_to_message
            the_dl_location = await c.download_media(message=m.reply_to_message, file_name=".")
            media_urls = telegraph.upload_file(the_dl_location)
            tele_link = "https://telegra.ph" + media_urls[0]
            await m.reply_text(tele_link)
        elif m.reply_to_message.text:
            tgph = telegraph.Telegraph()
            tgph.create_account(short_name=m.from_user.first_name)
            response = telegraph.create_page(
                "Hey", html_content=f"<p>{m.reply_to_message.text}</p>"
            )
            await m.reply_text(
                "<b>Link to you Telegraph:</b>\nhttps://telegra.ph/{}".format(
                    response["path"]
                )
            )
    else:
        await m.reply_text("Please Reply to Photo, Video or Text.")
    return
