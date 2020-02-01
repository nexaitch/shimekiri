import sqlite3
from sqlite3 import Error
import deadline

class DBHelper:
    dbname: str
    conn: sqlite3.Connection

    def __init__(self, dbname: str):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname,
                                    detect_types=sqlite3.PARSE_DECLTYPES |
                                    sqlite3.PARSE_COLNAMES)

    def setup(self):
        stmt = """CREATE TABLE IF NOT EXISTS deadlines (
        id INTEGER PRIMARY KEY,
        chat_id INTEGER,
        dl_time timestamp,
        comment TEXT)"""
        self.conn.execute(stmt)
        self.conn.commit()

    def fetch_deadlines(self, chat_id):
        stmt = """SELECT * FROM deadlines WHERE chat_id = (?) ORDER BY dl_time"""
        results = [(deadline_id, deadline.Deadline(t, c))
                   for (deadline_id, c_id, t, c)
                   in self.conn.execute(stmt, (chat_id,))]
        return results

    def insert_deadline(self, chat_id, deadline):
        stmt = """INSERT INTO deadlines (chat_id, dl_time, comment) values (?,?,?)"""
        self.conn.execute(stmt, (chat_id, deadline.time, deadline.comment))
        self.conn.commit()

    def delete_deadline(self, deadline_id):
        stmt = """DELETE FROM deadlines WHERE id = (?)"""
        self.conn.execute(stmt, (deadline_id,))
        self.conn.commit()

    def clear_old_deadlines(self):
        stmt = """DELETE FROM deadlines WHERE julianday(dl_time) < julianday("now", "-1 day")"""
        self.conn.execute(stmt)
        self.conn.commit()
