from pyrogram import filters
from mizuhara import OWNER_ID, DEV_USERS, SUDO_USERS


def f_dev_filter(_, __, m):
    return bool(m.from_user.id in DEV_USERS or m.from_user.id == OWNER_ID)


def f_sudo_filter(_, __, m):
    return bool(
        m.from_user.id in SUDO_USERS
        or m.from_user.id in DEV_USERS
        or m.from_user.id == OWNER_ID
    )


dev_filter = filters.create(f_dev_filter)
sudo_filter = filters.create(f_sudo_filter)
