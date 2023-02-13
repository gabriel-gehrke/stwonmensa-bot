import sqlite3
from os import path

DB_PATH = "data.db"

db_existed = path.exists(DB_PATH)
DB = sqlite3.connect(DB_PATH)

if not db_existed:
    cur = DB.cursor()
    # create config
    cur.execute("CREATE TABLE config(progress INTEGER NOT NULL)")
    cur.execute("INSERT INTO config VALUES(0)")
    # create users
    cur.execute("CREATE TABLE user(id INTEGER PRIMARY KEY, vegan BOOLEAN NOT NULL, veggie BOOLEAN NOT NULL, allergic BOOLEAN NOT NULL)")
    # create mensa_prefs
    cur.execute("CREATE TABLE mensa_pref(user INTEGER NOT NULL, mensa INTEGER NOT NULL, FOREIGN KEY(user) REFERENCES user(id))")

    DB.commit()
    cur.close()