import threading
from sqlalchemy import Column, Integer, UnicodeText, String, func
from mizuhara.db import BASE, SESSION


class Users(BASE):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(UnicodeText)

    def __init__(self, user_id, username):
        self.user_id = user_id
        self.username = username

    def __repr__(self):
        return "<User {} ({})>".format(self.username, self.user_id)


class Chats(BASE):
    __tablename__ = "chats"
    chat_id = Column(String, primary_key=True)
    chat_name = Column(UnicodeText)

    def __init__(self, chat_id, chat_name):
        self.chat_id = str(chat_id)
        self.chat_name = chat_name

    def __repr__(self):
        return "<Chat {} ({})>".format(self.chat_name, self.chat_id)


Users.__table__.create(checkfirst=True)
Chats.__table__.create(checkfirst=True)

INSERTION_LOCK = threading.RLock()


def update_user(user_id, username, chat_id=None, chat_name=None):
    with INSERTION_LOCK:
        user = SESSION.query(Users).get(user_id)
        if not user:
            user = Users(user_id, username)
            SESSION.add(user)
            SESSION.flush()
        else:
            user.username = username

        if not chat_id or not chat_name:
            SESSION.commit()
            return

        chat = SESSION.query(Chats).get(str(chat_id))
        if not chat:
            chat = Chats(str(chat_id), chat_name)
            SESSION.add(chat)
            SESSION.flush()

        else:
            chat.chat_name = chat_name
        SESSION.commit()
        SESSION.close()
    return


def get_userid_by_username(username):
    try:
        return (
            SESSION.query(Users)
            .filter(func.lower(Users.username) == username.lower())
            .all()
        )
    finally:
        SESSION.close()


def get_name_by_userid(user_id):
    try:
        return SESSION.query(Users).get(Users.user_id == int(user_id)).first()
    finally:
        SESSION.close()


def get_all_chats():
    try:
        return SESSION.query(Chats).all()
    finally:
        SESSION.close()


def get_all_users():
    try:
        return SESSION.query(Users).all()
    finally:
        SESSION.close()


def num_chats():
    try:
        return SESSION.query(Chats).count()
    finally:
        SESSION.close()


def num_users():
    try:
        return SESSION.query(Users).count()
    finally:
        SESSION.close()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        old_chat = SESSION.query(Chats).get(str(old_chat_id))
        if old_chat:
            old_chat.chat_id = str(new_chat_id)
            SESSION.merge(old_chat)
        SESSION.commit()
        SESSION.close()


def del_user(user_id):
    with INSERTION_LOCK:
        curr = SESSION.query(Users).get(user_id)
        if curr:
            SESSION.delete(curr)
            SESSION.commit()
            return


def rem_chat(chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Chats).get(str(chat_id))
        if chat:
            try:
                SESSION.delete(chat)
                SESSION.commit()
            finally:
                SESSION.close()
        else:
            SESSION.close()
