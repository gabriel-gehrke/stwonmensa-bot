from mensa import get_mensa_list
from time import sleep
from telegram import Bot, User
from database import DB

if __name__ == "__main__":
    token = ""
    with open("token") as f:
        token = f.read().strip()
    bot = Bot(token)

    c = DB.cursor()
    print(c.execute("SELECT * FROM user").fetchall())
    print(c.execute("SELECT * FROM config").fetchall())
    c.close()

    while True:
        bot.update()
        sleep(2)
        
