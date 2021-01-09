import threading
from sqlalchemy import Column, UnicodeText, Integer, String
from mizuhara.db import BASE, SESSION
from mizuhara.utils.msg_types import Types


class Notes(BASE):

    __tablename__ = "notes"
    chat_id = Column(String(14), primary_key=True)
    name = Column(UnicodeText, primary_key=True)
    value = Column(UnicodeText, nullable=False)
    msgtype = Column(Integer, default=Types.TEXT)
    file = Column(UnicodeText)

    def __init__(self, chat_id, name, value, msgtype, file):
        """initializing db"""
        self.chat_id = chat_id
        self.name = name
        self.value = value
        self.msgtype = msgtype
        self.file = file

    def __repr__(self):
        return "<Note {} at {}>".format(self.name, self.chat_id)


Notes.__table__.create(checkfirst=True)
INSERTION_LOCK = threading.RLock()
CHAT_NOTES = {}


def save_note(chat_id, note_name, note_data, msgtype, file=None):
    global CHAT_NOTES
    with INSERTION_LOCK:
        prev = SESSION.query(Notes).get((str(chat_id), note_name))
        if prev:
            SESSION.delete(prev)
        note = Notes(str(chat_id), note_name, note_data, msgtype, file)
        SESSION.add(note)
        SESSION.commit()

        if not CHAT_NOTES.get(chat_id):
            CHAT_NOTES[chat_id] = {}
        CHAT_NOTES[chat_id][note_name] = {
            "value": note_data,
            "type": msgtype,
            "file": file,
        }


def get_note(chat_id, note_name):
    if not CHAT_NOTES.get(str(chat_id)):
        CHAT_NOTES[str(chat_id)] = {}
    return CHAT_NOTES[str(chat_id)].get(note_name)


def get_all_notes(chat_id):
    if not CHAT_NOTES.get(str(chat_id)):
        CHAT_NOTES[str(chat_id)] = {}
        return None
    allnotes = list(CHAT_NOTES[str(chat_id)])
    allnotes.sort()
    return allnotes


def rm_note(chat_id, note_name):
    global CHAT_NOTES
    with INSERTION_LOCK:
        note = SESSION.query(Notes).get((str(chat_id), note_name))
        if note:
            SESSION.delete(note)
            SESSION.commit()
            CHAT_NOTES[str(chat_id)].pop(note_name)
            return True

        else:
            SESSION.close()
            return False


def rm_all_note(chat_id):
    global CHAT_NOTES
    with INSERTION_LOCK:
        all_notes = get_all_notes(chat_id)
        for note_name in all_notes:
            note = SESSION.query(Notes).get((str(chat_id), note_name))
            if note:
                try:
                    SESSION.delete(note)
                    SESSION.commit()
                    CHAT_NOTES[str(chat_id)].pop(note_name)
                except:
                    pass
            SESSION.close()
        del CHAT_NOTES[str(chat_id)]
    return True


def all_notes_chats():
    if CHAT_NOTES:
        return len(CHAT_NOTES.keys())
    return 0


def num_notes_all():
    count = 0
    if CHAT_NOTES:
        for i in CHAT_NOTES.values():
            for j in i:
                count += 1
    return count


def __load_all_notes():
    global CHAT_NOTES
    getall = SESSION.query(Notes).distinct().all()
    for x in getall:
        if not CHAT_NOTES.get(x.chat_id):
            CHAT_NOTES[x.chat_id] = {}
        CHAT_NOTES[x.chat_id][x.name] = {
            "value": x.value,
            "type": x.msgtype,
            "file": x.file,
        }


__load_all_notes()


def migrate_chat(old_chat_id, new_chat_id):
    with INSERTION_LOCK:
        chat = SESSION.query(Notes).get(str(old_chat_id))
        if chat:
            chat.chat_id = str(new_chat_id)
            SESSION.merge(chat)
        SESSION.commit()
        SESSION.close()
