from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import urllib.request
import urllib.parse
import json
import os.path
import os
from time import sleep
from hashlib import sha512
from database import DB

from mensa import Mensa, Food, get_mensa_list
import emojis

class User:
    id: int

    def __init__(self, id: int) -> None:
        self.id = id
        c = DB.cursor()
        res = c.execute("SELECT * FROM user WHERE id = ?", (id, ))
        if not res.fetchone():
            c.execute("INSERT INTO user VALUES(?, false, false, false)", (id,))
            DB.commit()
        c.close()
    
    def set_vegan(self, vegan: bool):
        c = DB.cursor()
        c.execute("UPDATE user SET vegan = ? WHERE id = ?", (vegan, self.id))
        if vegan:
            c.execute("UPDATE user SET veggie = true WHERE id = ?", (self.id,))
        DB.commit()
        c.close()

    def update_preferences(self, vegan = False, vegetarian = False, allergic = False) -> None:
        if vegan:
            vegetarian = True
        
        c = DB.cursor()
        c.execute()

class Bot:
    def __init__(self, token: str) -> None:
        self.token = token
        self.__pull_messages()
    
    def __execute(self, cmd: str):
        return urllib.request.urlopen(f"https://api.telegram.org/bot{self.token}/{cmd}").read()

    def __update_highest_update_id(self, u_id: int = 0) -> int:
        c = DB.cursor()
        prev_u_id = int(c.execute("SELECT progress FROM config").fetchone()[0])
        u_id = max(u_id, prev_u_id)
        c.execute("UPDATE config SET progress = ?", (u_id,))
        DB.commit()
        c.close()
        return u_id

    def __pull_messages(self):
        res = json.loads(self.__execute(f"getUpdates?offset={self.__update_highest_update_id() + 1}"))
        # print(res)
        if not res["ok"]:
            print(res)
            return
        updates = res["result"]
        for update in updates:
            u_id = update["update_id"]
            self.__update_highest_update_id(u_id)
            message = update.get("message", None)
            if not message:
                continue
            user_dict = message["from"]
            chat = message["chat"]
            if user_dict["is_bot"]:
                continue

            user = User(id=user_dict["id"])
            
            self.__handle_message(message, user)
            sleep(0.5)
    
    def __handle_message(self, message: Dict, user: User):
        text: str = message.get("text", None)
        if not text:
            return
        
        first_name = message["chat"]["first_name"]
        # print(text)

        c = DB.cursor()

        if text == "/start":
            msg = "\n".join(
                [
                    f"Willkommen, {first_name}!",
                    f"Bitte wähle eine oder mehrere der verfügbaren Mensen aus!"
                ]
                +
                [str(m) for m in get_mensa_list()]
            )
            self.__send_message(msg, user)
        
        elif text == "/list":
            msg = "\n".join(f"{m.id} {m.name}" for m in get_mensa_list())
            self.__send_message(msg, user)
        
        elif text == "/food":
            preferred_mensa = c.execute("SELECT mensa FROM mensa_pref WHERE user = ?", (user.id,)).fetchall()
            if len(preferred_mensa) == 0:
                self.__send_message("Du hast bisher keine Mensa als Präferenz eingetragen!", user)
            else:
                msg = ""
                for mensa_id in preferred_mensa:
                    if type(mensa_id) == tuple:
                        mensa_id = mensa_id[0]
                    mensa = next((m for m in get_mensa_list() if m.id == mensa_id), None)
                    if not mensa:
                        continue
                    msg += f"- - - {mensa.name} - - -\n\n"
                    for food in mensa.get_menu():
                        msg += f"[{food.price}€] {food.name} {food.get_emoji_string()}\n"
                    msg += "\n"
                
                # print legend
                msg += f"\n{emojis.VEGAN_EMOJI} = Vegan\n{emojis.VEGGIE_EMOJI} = Vegetarisch"
                self.__send_message(msg, user)
        
        elif text.startswith("/subscribe"):
            ss = text.split()
            if len(ss) != 2 or not ss[1].isnumeric():
                self.__send_message("Benutzung: /subscribe {mensa_id}", user)
            else:
                mensa_id = int(ss[1])
                is_already_preferred = bool(
                    c.execute(
                        "SELECT EXISTS(SELECT * FROM mensa_pref WHERE mensa = ? AND user = ?)",
                        (mensa_id, user.id)
                    ).fetchone()[0]
                )
                if is_already_preferred:
                    self.__send_message(f"Du hast {mensa_id} bereits abonniert!", user)
                else:
                    c.execute("INSERT INTO mensa_pref VALUES(?, ?)", (user.id, mensa_id))
                    DB.commit()
                    self.__send_message("DB updated!", user)
        
        elif text.startswith("/unsubscribe"):
            ss = text.split()
            if len(ss) != 2 or not ss[1].isnumeric():
                self.__send_message("Benutzung: /unsubscribe {mensa_id}", user)
            else:
                mensa_id = int(ss[1])
                is_subscribed = bool(
                    c.execute(
                        "SELECT EXISTS(SELECT * FROM mensa_pref WHERE mensa = ? AND user = ?)",
                        (mensa_id, user.id)
                    ).fetchone()[0]
                )
                if not is_subscribed:
                    self.__send_message(f"Du hast {mensa_id} gar nicht abonniert!", user)
                else:
                    c.execute("DELETE FROM mensa_pref WHERE user = ? AND mensa = ?", (user.id, mensa_id))
                    DB.commit()
                    self.__send_message("DB updated!", user)
        
        c.close()

    def __send_message(self, message: str, user: User):
        message = urllib.parse.quote(message, safe="")
        self.__execute(f"sendMessage?chat_id={user.id}&text={message}")
    
    def update(self):
        self.__pull_messages()
