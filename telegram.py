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
        print(res)
        if not res["ok"]:
            print(res)
            return
        updates = res["result"]
        for update in updates:
            u_id = update["update_id"]
            message = update["message"]
            user_dict = message["from"]
            chat = message["chat"]
            if user_dict["is_bot"]:
                continue

            user = User(id=user_dict["id"])
            
            self.__handle_message(message, user)
            self.__update_highest_update_id(u_id)
            sleep(0.5)
    
    def __handle_message(self, message: Dict, user: User):
        text = message.get("text", None)
        if not text:
            return
        
        first_name = message["chat"]["first_name"]
        print(text)

        if text == "/start":
            msg = "\n".join(
                [
                    f"Willkommen, {first_name}!",
                    f"Bitte wähle eine oder mehrere der verfügbaren Mensen aus!"
                ]
                +
                [str(m) for m in get_mensa_list()]
            )
            self.__send_message(msg, user.id)
        
        if text == "/list":
            msg = "\n".join(f"{m.id} {m.name}" for m in get_mensa_list())
            self.__send_message(msg, user.id)

    def __send_message(self, message: str, chat_id: int):
        print(chat_id)
        message = urllib.parse.quote(message, safe="")
        self.__execute(f"sendMessage?chat_id={chat_id}&text={message}")
    
    def update(self):
        self.__pull_messages()