from mensa import get_mensa_list
from time import sleep
from telegram import Bot, User

if __name__ == "__main__":
    token = ""
    with open("token") as f:
        token = f.read().strip()
    bot = Bot(token)

    while True:
        bot.update()
        sleep(2)
        
