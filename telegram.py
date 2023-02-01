from typing import Tuple, List, Dict
from dataclasses import dataclass
import urllib.request
from threading import Lock
import json
import os.path
from time import sleep
from hashlib import sha512

@dataclass
class User:
    id: int

    def hexdigest(self) -> bytes:
        """
        Hashes the user id for privacy.
        Utilizes SHA-512 with salt.
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
        self.io_lock = Lock()
        self.__pull_messages()
    
    def __update_highest_update_id(self, u_id: int = 0) -> int:
        prev_u_id = 0
        with self.io_lock:
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
            user = message["from"]

            print(u_id)
            if user["is_bot"]:
                continue

            self.__handle_message(message, user)
            self.__update_highest_update_id(u_id)
            sleep(0.5)
    
    def __handle_message(self, message: Dict, user: Dict):
        text = message["text"]
        m_id = message["message_id"]
        print(text)

        if text == "/start":
            pass

    def __send_message(self, message: str):
        self.__execute

    def __execute(self, cmd: str):
        return urllib.request.urlopen(f"https://api.telegram.org/bot{self.token}/{cmd}").read()