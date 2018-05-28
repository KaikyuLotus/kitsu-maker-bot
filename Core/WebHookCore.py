# coding=utf-8

# Copyright (c) 2017 Kaikyu

import ssl
import sys
import json
import threading

from socketserver import ThreadingMixIn
from http.server import BaseHTTPRequestHandler
from http.server import HTTPServer

from Core import Elaborator, Manager, Infos, HTTPLL
from Core.Error import ServerError, Unauthorized
from Core.Settings import *

from Utils import Logger as Log, Utils
from LowLevel import LowLevel
from Foos import BotsFoos, Foos

from Cache import BotCache

# Edit these pats as you prefer
ckey = "Files/Auth/private.key"
certfile = "Files/Auth/cert.pem"
port = 8443

base_url = "http://api.telegram.org/"

offsets = {}
token_black_list = []


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""


class S(BaseHTTPRequestHandler):
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        self.wfile.write('{"ok": True, "result": "Cosa ci fai qui?"}'.encode())

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        try:
            pdata = self.rfile.read(int(self.headers['Content-Length']))
            token = self.path[1:]
            callback(token, pdata.decode())
            self._set_headers()
            self.wfile.write("{}".encode())
        except Exception as err:
            raise ServerError(str(err))

    def log_message(self, format, *args):
        pass


def callback(token, data):
    try:
        update = json.loads(data)
    except Exception as err:
        return Log.w("Not JSON data (%s) (%s)" % (err, data))

    if token not in BotCache.bots:
        Log.w("This token is not in the cache!")
        if token not in token_black_list:
            if len(token) == 45:
                HTTPLL.deleteWebhook(token)
            else:
                Log.w("Invalid token!! (%s) blacklist." % token)
            token_black_list.append(token)
            return

    if token not in offsets:
        offsets[token] = 0

    last_id = offsets[token]
    bot = BotCache.bots[token]
    if update["update_id"] > last_id:
        offsets[token] = update["update_id"]
        try:
            update_handler(bot, update)
        except Exception as err:
            Log.e("UNHANDLED EXCEPTION IN THE UPDATE HANDLER: %s" % str(err))


def update_handler(bot, update):
    infos = Infos.Infos(bot, update)
    if infos.error:
        Log.d("Errore owo!")
        return

    if infos.user.uid in json.loads(open("Files/jsons/blacklist.json").read()): return
    if not infos.error:
        if "message" in update:
            try:
                if "new_chat_members" in update["message"]:
                    if update["message"]["new_chat_members"] or "left_chat_member" in update["message"]:
                        if bot["id"] == main_bot_id:
                            return Foos.status(bot, update)
                        return BotsFoos.status(bot, update)
            except Exception as err:
                Log.e("Ho trovato un errore: riga %s %s %s" % (sys.exc_info()[-1].tb_lineno, type(err).__name__, err))

        if infos.user.message.what == "command":
            if infos.user.message.command == "report":
                return Foos.report(infos)
            try:
                ok = Elaborator.command_reader(infos)
                if ok == "procedi":
                    if infos.user.message.pers_command:
                        Elaborator.pers_commands(infos)
            except Exception as error:
                Log.e("Ho trovato un errore: riga %s %s %s" % (sys.exc_info()[-1].tb_lineno, type(error).__name__, error))
        else:
            Elaborator.reader(infos)
    else:
        Log.w("Error in bot")


def run():
    httpd = ThreadedHTTPServer(('', port), S)
    httpd.socket = ssl.wrap_socket(httpd.socket, certfile=certfile, keyfile=ckey, server_side=True)
    Log.i("Starting server, use <Ctrl-C> to stop")
    HTTPLL.sendMessage("569510835:AAHskMqSa02KAditTfztt3KuHtE9oFQRYGs", 487353090, "Avvio concluso.")
    try:
        httpd.serve_forever()
    except Exception as err:
        print(err)
    Log.e("Server has stopped, warning.")


def clean_updates(token):
    # Puliamo gli update!
    updates = HTTPLL.getUpdates(token)
    if not updates:
        offsets[token] = 0
    while updates:
        offsets[token] = updates[-1]["update_id"] + 1
        updates = HTTPLL.getUpdates(token, offset=updates[-1]["update_id"] + 1)
    # Puliti!


def bot_init(token, clean):
    ok = False
    try:
        BotCache.bots[token] = HTTPLL.getMe(token)
        ok = True
        LowLevel.check_files(Manager.get_botid_from_token(token))
        if clean:
            HTTPLL.deleteWebhook(token)
            clean_updates(token)
        HTTPLL.setWebhook(token, certfile)
    except Unauthorized:
        if ok:
            Log.w("getMe ok but unauth.")
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


def set_main_bot(token, owner__id):
    if Manager.add_bot(owner__id, int(token.split(":")[0]), token):
        attach_bot(token)