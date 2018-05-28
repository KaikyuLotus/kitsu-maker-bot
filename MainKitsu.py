# coding=utf-8

# Copyright (c) 2018 Kaikyu

# 888    d8P  d8b 888                                                .d8888b.                888
# 888   d8P   Y8P 888                                               d88P  Y88b               888
# 888  d8P        888                                               888    888               888
# 888d88K     888 888888 .d8888b  888  888 88888b.   .d88b.         888         .d88b.   .d88888  .d88b.
# 8888888b    888 888    88K      888  888 888 "88b d8P  Y8b        888        d88""88b d88" 888 d8P  Y8b
# 888  Y88b   888 888    "Y8888b. 888  888 888  888 88888888  8888  888    888 888  888 888  888 88888888
# 888   Y88b  888 Y88b.       X88 Y88  888 888  888 Y8b.            Y88b  d88P Y88..88P Y88b 888 Y8b.
# 888    Y88b 888  "Y888  88888P'  "Y88888 888  888  "Y8888          "Y8888P"   "Y88P"   "Y88888  "Y8888


from Core import Manager
from Utils import Logger as Log
from Core import ThreadedCore as Core
from Core import HTTPLL
from Core.Settings import *


def run():
    Core.attach_bot(Manager.get_token_list(), clean=True)
    Core.set_main_bot(main_bot_token, owner_id)
    HTTPLL.sendMessage(main_bot_token, owner_id, "Booted.")
    Core.idle()


if __name__ == "__main__":
    Log.i("Starting Kitsu, version 3.0.")
    run()
