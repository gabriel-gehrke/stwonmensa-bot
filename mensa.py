from typing import Tuple, List, Dict
from dataclasses import dataclass
import urllib.request
import datetime
import json

@dataclass
class Food:
    name: str
    price: float

@dataclass
class Mensa:
    id: int
    name: str

    def get_menu(self) -> List[Food]:
        r = urllib.request.urlopen(f"https://sls.api.stw-on.de/v1/locations/{self.id}/menu/{datetime.date.today()}")
        food_table = json.loads(r.read()).get("meals", None)
        if food_table is None or len(food_table) == 0:
            return list()
        foods = [Food(name=row["name"], price=row["price"]["student"]) for row in food_table]
        return foods

    
    def __hash__(self) -> int:
        return hash(id)


def get_mensa_list() -> List[Mensa]:
    r = urllib.request.urlopen('https://sls.api.stw-on.de/v1/location')
    mensa_table = json.loads(r.read())
    mensa_list = [Mensa(id=row["id"], name=row["name"]) for row in mensa_table]
    return mensa_list