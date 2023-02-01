from typing import Tuple, List, Dict, Any
from dataclasses import dataclass
import urllib.request
import urllib.parse
import json
import os.path
import os
from time import sleep
from hashlib import sha512

from mensa import Mensa, Food, get_mensa_list

@dataclass
class User:
    id: int

    def __get_or_make_path(self) -> str:
        p = f"users/{self.hexdigest()}"
        os.makedirs(p, exist_ok=True)
        return p
    
    def __load_attributes(self) -> Dict[str, Any]:
        """
        Loads the attributes associated with this user.
        """
        p = self.__get_or_make_path()
        try:
            with open(p + "/attributes.json", "r") as f:
                return json.load(f)
        except:
            return dict()
    
    def __store_attributes(self, attribs: Dict[str, Any]):
        p = self.__get_or_make_path()
        with open(p + "/attributes.json", "w") as f:
            json.dump(attribs, f)


    def set_attribute(self, key: str, val: Any):
        attribs = self.__load_attributes()
        attribs[key] = val
        self.__store_attributes(attribs)


    def get_attribute(self, key: str, default: Any = None):
        a = self.__load_attributes()
        print(a)
        return self.__load_attributes().get(key, default)

    def hexdigest(self) -> bytes:
        """
        Hashes the user id for privacy.
        Utilizes salted SHA-512.
        """
        magic_number = 63378574301438552054793830010137
        salt = "eu96vjdjaCcjEQx5DsJCJVuX"
        n = self.id * magic_number
        s = str(n) + salt + hex(n)
        hashobj = sha512(s.encode("ascii"))
        return hashobj.hexdigest()

    def __hash__(self) -> int:
        return hash(self.id)

class Bot:
    def __init__(self, token: str) -> None:
        self.token = token
        self.__pull_messages()
    
    def __execute(self, cmd: str):
        return urllib.request.urlopen(f"https://api.telegram.org/bot{self.token}/{cmd}").read()

    def __update_highest_update_id(self, u_id: int = 0) -> int:
        prev_u_id = 0
        # see if file can be opened
        if not os.path.exists("progress"):
            with open("progress", "w") as f:
                f.write(str(u_id))
        else:
            with open("progress", "r+") as f:
                prev_u_id = int(f.read())
                if u_id > prev_u_id:
                    f.seek(0)
                    f.write(str(u_id))
        return max(prev_u_id, u_id)

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
            user.set_attribute("chat_id", chat["id"])
            
            self.__handle_message(message, user)
            self.__update_highest_update_id(u_id)
            sleep(0.5)
    
    def __handle_message(self, message: Dict, user: User):
        text = message["text"]
        cid = user.get_attribute("chat_id")
        print(text)

        if text == "/start":
            msg = "\n".join(
                [
                    f"Willkommen, {user.name}!",
                    f"Bitte wähle eine oder mehrere der verfügbaren Mensen aus!"
                ]
                +
                [str(m) for m in get_mensa_list()]
            )
            self.__send_message(msg, cid)
        
        if text == "/list":
            msg = "\n".join(f"{m.id} {m.name}" for m in get_mensa_list())
            self.__send_message(msg, cid)

    def __send_message(self, message: str, chat_id: int):
        print(chat_id)
        message = urllib.parse.quote(message, safe="")
        self.__execute(f"sendMessage?chat_id={chat_id}&text={message}")
    
    def update(self):
        self.__pull_messages()