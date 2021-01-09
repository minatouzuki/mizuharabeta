import html
import random
from mizuhara.__main__ import Mizuhara
from pyrogram import filters
from pyrogram.types import Message
from mizuhara import PREFIX_HANDLER
from mizuhara.utils.localization import GetLang
from mizuhara.utils import fun_strings
from mizuhara.utils.extract_user import extract_user

__PLUGIN__ = "Fun"

__help__ = """
 - /runs: reply a random string from an array of replies.
 - /slap: slap a user, or get slapped if not a reply.
 - /shrug : get shrug XD.
 - /decide : Randomly answers yes/no/maybe
 - /toss : Tosses A coin
 - /bluetext : check urself :V
 - /roll : Roll a dice.
 - /react : Random Reaction
 - /shout <keyword>: write anything you want to give loud shout.
"""


@Mizuhara.on_message(filters.command("shout", PREFIX_HANDLER))
async def fun_shout(c: Mizuhara, m: Message):
    _ = GetLang(m).strs
    if len(m.text.split()) == 1:
        await m.reply_text(_("general.check_help"), reply_to_message_id=m.message_id)
        return
    text = " ".join(m.text.split(None, 1)[1])
    result = []
    result.append(" ".join([s for s in text]))
    for pos, symbol in enumerate(text[1:]):
        result.append(symbol + " " + "  " * pos + symbol)
    result = list("\n".join(result))
    result[0] = text[0]
    result = "".join(result)
    msg = "```\n" + result + "```"
    await m.reply_text(msg, parse_mode="MARKDOWN")
    return


@Mizuhara.on_message(filters.command("runs", PREFIX_HANDLER))
async def fun_run(c: Mizuhara, m: Message):
    await m.reply_text(random.choice(fun_strings.RUN_STRINGS))
    return


@Mizuhara.on_message(filters.command("slap", PREFIX_HANDLER))
async def fun_slap(c: Mizuhara, m: Message):
    me = await c.get_me()

    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text

    curr_user = html.escape(m.from_user.first_name)
    user_id, first_name = await extract_user(c, m)

    if user_id == me.id:
        temp = random.choice(fun_strings.SLAP_ALITA_TEMPLATES)
        return

    if user_id:
        slapped_user = await c.get_member(user_id)
        user1 = curr_user
        user2 = html.escape(slapped_user.first_name)

    else:
        user1 = me.first_name
        user2 = curr_user

    temp = random.choice(fun_strings.SLAP_ALITA_TEMPLATES)
    item = random.choice(fun_strings.ITEMS)
    hit = random.choice(fun_strings.HIT)
    throw = random.choice(fun_strings.THROW)

    reply = temp.format(user1=user1, user2=user2, item=item, hits=hit, throws=throw)

    await reply_text(reply)
    return


@Mizuhara.on_message(filters.command("roll", PREFIX_HANDLER))
async def fun_roll(c: Mizuhara, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(random.choice(range(1, 7)))
    return


@Mizuhara.on_message(filters.command("toss", PREFIX_HANDLER))
async def fun_toss(c: Mizuhara, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(random.choice(fun_strings.TOSS))
    return


@Mizuhara.on_message(filters.command("shrug", PREFIX_HANDLER))
async def fun_shrug(c: Mizuhara, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(r"¯\_(ツ)_/¯")
    return


@Mizuhara.on_message(filters.command("bluetext", PREFIX_HANDLER))
async def fun_bluetext(c: Mizuhara, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(
        "/BLUE /TEXT\n/MUST /CLICK\n/I /AM /A /STUPID /ANIMAL /THAT /IS /ATTRACTED /TO /COLORS"
    )
    return


@Mizuhara.on_message(filters.command("decide", PREFIX_HANDLER))
async def fun_decide(c: Mizuhara, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(random.choice(fun_strings.DECIDE))
    return


@Mizuhara.on_message(filters.command("react", PREFIX_HANDLER))
async def fun_table(c: Mizuhara, m: Message):
    reply_text = m.reply_to_message.reply_text if m.reply_to_message else m.reply_text
    await reply_text(random.choice(fun_strings.REACTIONS))
    return
