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

import time

from Core import Manager
from Utils import Logger as Log
from Core import ThreadedCore as Core
from Core import HTTPLL
from LowLevel.LowLevel import get_time


def run():
    Log.i("Starting Kitsu, version 3.0.")
    token = "TOKEN"
    your_id = 123  # Your Telegram user ID
    ts = time.time()
    Core.attach_bot(Manager.get_token_list(), clean=True)
    Log.d("Booted in %s ms..." % get_time(ts))
    HTTPLL.sendMessage(token, your_id, "Booted in %s ms..." % get_time(ts))
    Core.idle()


if __name__ == "__main__":
    run()
