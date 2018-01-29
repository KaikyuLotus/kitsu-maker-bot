# coding=utf-8

# Copyright (c) 2017 Kaikyu

# 888    d8P  d8b 888                                                .d8888b.                888
# 888   d8P   Y8P 888                                               d88P  Y88b               888
# 888  d8P        888                                               888    888               888
# 888d88K     888 888888 .d8888b  888  888 88888b.   .d88b.         888         .d88b.   .d88888  .d88b.
# 8888888b    888 888    88K      888  888 888 "88b d8P  Y8b        888        d88""88b d88" 888 d8P  Y8b
# 888  Y88b   888 888    "Y8888b. 888  888 888  888 88888888  8888  888    888 888  888 888  888 88888888
# 888   Y88b  888 Y88b.       X88 Y88  888 888  888 Y8b.            Y88b  d88P Y88..88P Y88b 888 Y8b.
# 888    Y88b 888  "Y888  88888P'  "Y88888 888  888  "Y8888          "Y8888P"   "Y88P"   "Y88888  "Y8888

import threading
import time

from Core import Manager, HTTPLL
from Foos import Foos
from Utils import Logger as Log
from Core import Core, Unreloaded
from Extras import MeteoManager
from LowLevel.LowLevel import get_time

ts = time.time()
kitsukey = "447458418:AAEVPQHV16VogYINta2M58a0oSF8AW2gRWI"


def clean():
    try:
        t = int(get_time(float(open("Files/jsons/offmoment.txt").read())))
        res = False if t < 10000 else True
        Log.d("Rebooted %s ms ago" % t)
        return res
    except Exception as err:
        print(err)
        return True


def run():
    HTTPLL.sendMessage(kitsukey, 52962566, "Avvio...")
    cln = clean()
    if not cln:
        Log.i("Executing a non-clean boot...")
    Core.attach_bot(Manager.get_token_list(), clean=cln)
    Log.d("Booted in %s ms..." % get_time(ts))

    threading.Thread(target=Foos.scheduler).start()
    threading.Thread(target=Unreloaded.reset_scores).start()
    threading.Thread(target=Unreloaded.rankings).start()
    threading.Thread(target=MeteoManager.meteo_b).start()
    Log.i("Threads started.")

    try:
        Core.run()
    except KeyboardInterrupt:
        Log.i("Stopping!")
        with open("Files/jsons/offmoment.txt", "w") as f:
            f.write(str(time.time()))
    except Exception as err:
        print("Exeption %s in server, stopping..." % err)


if __name__ == "__main__":
    print("\n\n")
    Log.i("starting Kitsu, version 3.0.")
    run()
