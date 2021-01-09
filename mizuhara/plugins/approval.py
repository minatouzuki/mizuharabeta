from io import BytesIO
from datetime import datetime
from mizuhara.db import approve_db as db
from mizuhara.__main__ import Mizuhara
from pyrogram import filters, errors
from pyrogram.types import Message
from mizuhara import MESSAGE_DUMP, PREFIX_HANDLER, SUPPORT_GROUP, LOGGER
from mizuhara.utils.extract_user import extract_user
from mizuhara.utils.parser import mention_html
from mizuhara.utils.admin_check import admin_check, owner_check

__PLUGIN__ = "Approval"

__help__ = """
Sometimes, you might trust a user not to send unwanted content.
Maybe not enough to make them admin, but you might be ok with locks, blacklists, and antiflood not applying to them.
That's what approvals are for - approve trustworthy users to allow them to send stuff without restrictions!
**Admin commands:**
- /approval: Check a user's approval status in this chat.
- /approve: Approve of a user. Locks, blacklists, and antiflood won't apply to them anymore.
- /unapprove: Unapprove of a user. They will now be subject to blocklists.
- /approved: List all approved users.
- /unapproveall: Unapprove *ALL* users in a chat. This cannot be undone!
"""


@Mizuhara.on_message(filters.command("approve", PREFIX_HANDLER) & filters.group)
async def approve_user(c: Mizuhara, m: Message):

    res = await owner_check(c, m)
    if not res:
        return

    chat_title = m.chat.title
    chat_id = m.chat.id
    user_id, user_first_name = await extract_user(c, m)
    if not user_id:
        await m.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return
    member = await c.get_chat_member(chat_id=chat_id, user_id=user_id)
    if member.status in ["administrator", "creator"]:
        await m.reply_text(
            f"User is already admin - blocklists already don't apply to them."
        )
        return
    if db.is_approved(chat_id, user_id):
        await m.reply_text(
            f"{mention_html(user_first_name, user_id)} is already approved in {chat_title}"
        )
        return
    db.approve(chat_id, user_id)
    await m.reply_text(
        f"{mention_html(user_first_name, user_id)} has been approved in {chat_title}! They will now be ignored by blocklists."
    )
    return


@Mizuhara.on_message(filters.command("disapprove", PREFIX_HANDLER) & filters.group)
async def disapprove_user(c: Mizuhara, m: Message):

    res = await owner_check(c, m)
    if not res:
        return

    chat_title = m.chat.title
    chat_id = m.chat.id
    user_id, user_first_name = await extract_user(c, m)
    if not user_id:
        await m.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return
    member = await c.get_chat_member(chat_id=chat_id, user_id=user_id)
    if member.status in ["administrator", "creator"]:
        await m.reply_text("This user is an admin, they can't be unapproved.")
        return
    if not db.is_approved(chat_id, user_id):
        await m.reply_text(
            f"{mention_html(user_first_name, user_id)} isn't approved yet!"
        )
        return
    db.disapprove(chat_id, user_id)
    await m.reply_text(
        f"{mention_html(user_first_name, user_id)} is no longer approved in {chat_title}."
    )
    return


@Mizuhara.on_message(filters.command("approved", PREFIX_HANDLER) & filters.group)
async def check_approved(c: Mizuhara, m: Message):

    res = await admin_check(c, m)
    if not res:
        return

    chat_title = m.chat.title
    chat = m.chat
    no_users = False
    msg = "The following users are approved:\n"
    x = db.all_approved(m.chat.id)

    for i in x:
        try:
            member = await chat.get_member(int(i.user_id))
        except:
            no_users = True
            break
        msg += f"- `{i.user_id}`: {mention_html(member.user['first_name'], int(i.user_id))}\n"
    if msg.endswith("approved:\n"):
        await m.reply_text(f"No users are approved in {chat_title}.")
        return
    else:
        await m.reply_text(msg)
        return


@Mizuhara.on_message(filters.command("approval", PREFIX_HANDLER) & filters.group)
async def check_approval(c: Mizuhara, m: Message):

    res = await admin_check(c, m)
    if not res:
        return

    user_id, user_first_name = await extract_user(c, m)
    if not user_id:
        await m.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!"
        )
        return
    if db.is_approved(m.chat.id, user_id):
        await m.reply_text(
            f"{mention_html(user_first_name, user_id)} is an approved user. Locks, antiflood, and blocklists won't apply to them."
        )
    else:
        await m.reply_text(
            f"{mention_html(user_first_name, user_id)} is not an approved user. They are affected by normal commands."
        )
    return


@Mizuhara.on_message(filters.command("unapproveall", PREFIX_HANDLER) & filters.group)
async def unapproveall_users(c: Mizuhara, m: Message):

    res = await owner_check(c, m)
    if not res:
        return

    try:
        db.disapprove_all(m.chat.id)
        await m.reply_text(f"All users have been disapproved in {m.chat.title}")
    except Exception as ef:
        await m.reply_text(f"Some Error occured, report at {SUPPORT_GROUP}.\n{ef}")
    return
