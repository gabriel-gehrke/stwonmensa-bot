from typing import Tuple, List, Dict
from dataclasses import dataclass
import urllib.request
import datetime
import json

import emojis

@dataclass
class Food:
    name: str
    price: float
    veggie: bool = False
    vegan: bool = False
    json: dict = None

    def get_emoji_string(self):
        s = ""
        if self.vegan:
            s += emojis.VEGAN_EMOJI
        elif self.veggie:
            s += emojis.VEGGIE_EMOJI
        return s
        


@dataclass
class Mensa:
    id: int
    name: str

    def get_menu(self) -> List[Food]:
        r = urllib.request.urlopen(f"https://sls.api.stw-on.de/v1/locations/{self.id}/menu/{datetime.date.today()}")
        food_table = json.loads(r.read()).get("meals", None)
        if food_table is None or len(food_table) == 0:
            return list()
        foods = list()
        for row in food_table:
            f = Food(name=row["name"], price=row["price"]["student"])
            f.vegan = any(t for t in row["tags"]["categories"] if t["id"] == "VEGA")
            f.veggie = f.vegan or any(t for t in row["tags"]["categories"] if t["id"] == "VEGT")
            f.json = row
            allergens = row["tags"]["allergens"]
            foods.append(f)
        # print(food_table)
        return foods
    
    def __hash__(self) -> int:
        return hash(id)

MENSA_LIST = list()

def get_mensa_list() -> List[Mensa]:
    global MENSA_LIST
    if not MENSA_LIST:
        r = urllib.request.urlopen('https://sls.api.stw-on.de/v1/location')
        mensa_table = json.loads(r.read())
        MENSA_LIST = [Mensa(id=row["id"], name=row["name"]) for row in mensa_table]
    return MENSA_LIST