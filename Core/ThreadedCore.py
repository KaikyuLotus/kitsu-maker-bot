# coding=utf-8

# Copyright (c) 2017 Kaikyu

import sys
import json
import threading

import time

from Core import Elaborator, Manager, Infos, HTTPLL
from Core.Error import Unauthorized

from Utils import Logger as Log, Utils
from LowLevel import LowLevel
from Foos import BotsFoos, Foos

from Cache import BotCache

offsets = {}
token_black_list = []


def getter(token):
    if token not in offsets:
        offsets[token] = 0

    while token in BotCache.bots:
        for update in HTTPLL.getUpdates(token, offsets[token], timeout=120):
            offsets[token] = update["update_id"] + 1
            update_handler(BotCache.bots[token], update)

    HTTPLL.sendMessage(token, Manager.get_owner_id(), "Bot {} stopped.".format(token))


def update_handler(bot, update):
    try:
        infos = Infos.Infos(bot, update)

        if infos.error:
            return Log.e("Errore nell'update: " + str(update))

        if infos.user.uid in json.loads(open("Files/jsons/blacklist.json").read()) or infos.skip:
            return

        if "message" in update:
            if "new_chat_members" in update["message"]:
                if not update["message"]["new_chat_members"] or "left_chat_member" not in update["message"]:
                    return

                if bot["id"] == Manager.get_main_bot_id():
                    return Foos.status(bot, update)

                return BotsFoos.status(bot, update)

        if infos.user.message.what != "command":
            return Elaborator.reader(infos)

        if infos.user.message.command == "report":
            return Foos.report(infos)

        ok = Elaborator.command_reader(infos)
        if ok != "procedi":
            return
        if infos.user.message.pers_command:
            Elaborator.pers_commands(infos)

    except Exception as error:
        Log.e("Ho trovato un errore: riga %s %s %s" % (sys.exc_info()[-1].tb_lineno, type(error).__name__, error))


def clean_updates(token):
    try:
        offsets[token] = HTTPLL.getUpdates(token, offset=-1)[-1]["update_id"] + 1
    except IndexError:
        pass


def bot_init(token, clean):
    try:
        BotCache.bots[token] = HTTPLL.getMe(token)
        LowLevel.check_files(Manager.get_botid_from_token(token))

        if clean:
            clean_updates(token)

        threading.Thread(target=getter, args=(token,)).start()

    except Unauthorized:
        Log.w("Bot with token '%s' unauthorized." % token)
        Utils.warn_token(token)
    except Exception as error:
        Log.e(error)


def count_bots():
    return len(BotCache.bots)


def is_online(token):
    if token in BotCache.bots:
        if BotCache.bots[token]:
            return True
    return False


def attach_bot(token, bid=None, clean=True):
    if bid:
        token = Manager.get_token_from_bot_id(bid)

    if not token:
        return Log.w("Empty token.")

    if isinstance(token, list):
        Log.d("Passed a list, iterating...")
        for toke in token:
            attach_bot(toke, clean=clean)
        Log.d("Finished iterating tokens!")

    else:
        if token in BotCache.bots:
            if BotCache.bots[token]:
                return Log.w("This bot is already online...")

        threading.Thread(target=bot_init, args=(token, clean)).start()
    return True


def detach_bot(token, bid=None):
    if bid:
        token = Manager.get_token_from_bot_id(bid)

    if not token:
        return Log.w("Empty token.")

    if token not in BotCache.bots:
        return Log.w("This token is not running.")

    HTTPLL.deleteWebhook(token)
    del BotCache.bots[token]

    Log.i("Bot with %s token stopped." % token)
    return True


def idle():
    while True:
        time.sleep(10)
