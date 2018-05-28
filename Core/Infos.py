# coding=utf-8

# Copyright (c) 2017 Kaikyu

import json
import re
import time
from datetime import datetime

from LowLevel import DBs
from Utils import Utils, Logger as Log
from Core import Unreloaded, HTTPLL, Manager
from Core.Settings import *
from pprint import pprint


permissions = [
                "can_change_info", "can_post_messages",
                "can_edit_messages", "can_delete_messages",
                "can_invite_users", "can_restrict_members", "can_pin_messages",
                "can_promote_members", "can_send_messages", "can_send_media_messages",
                "can_add_web_page_previews"
            ]


def blacklista(uid):
    blacklist = json.loads(open("jsons/blacklist.json").read())
    if uid in blacklist:
        return
    blacklist.append(uid)
    with open("jsons/blacklist.json", "w") as fl:
        fl.write(json.dumps(blacklist))


def get_message(update):

    if "edited_channel_post" in update:
        return None, False, None  # return update["edited_channel_post"], False, "edited_channel_post"

    if "channel_post" in update:
        return update["channel_post"], False, "channel_post"

    if "message" in update:
        return update["message"], False, "message"

    if "edited_message" in update:
        return None, False, None  # return update["edited_message"], True, "edited message"

    else:
        Log.w("Non un update valido: %s" % update)
        return None, False, None


def get_admin(token, cid, uid):
    for admin in Unreloaded.get_admin_ids(cid, token):
        if admin["user"]["id"] == uid:
            return admin
    return None


class NoPermisisons:
    def __init__(self):
        self.is_admin = False
        for permission in permissions:
            setattr(self, permission, False)


class Permissions:
    def __init__(self, token, cid, uid):
        if cid > 0:
            self.is_admin = False
            return

        admin = get_admin(token, cid, uid)
        if not admin:
            self.is_admin = False
            return

        self.is_admin = True

        try:
            if admin["status"] == "creator":
                for permission in permissions:
                    setattr(self, permission, True)
            else:
                for permission in permissions:
                    if permission in admin:
                        setattr(self, permission, admin[permission])
                    else:
                        setattr(self, permission, False)

        except Exception as err:
            self.is_admin = False
            Log.e(err)
            pprint(admin)
            time.sleep(1)


class Message:
    def __init__(self, message, bot):
        if "text" in message:
            self.text = message["text"]
        else:
            self.text = ""

        self.id = message["message_id"]
        self.time = time.strftime("%H:%M:%S", time.localtime(int(message["date"])))
        self.unix_time = int(message["date"])
        # self.time = str(message["date"])
        self.my_time = time.strftime("%H:%M:%S")
        self.what = "text"
        self.item_id = None
        self.command = None
        self.pers_command = False
        if self.text != "":
            if self.text.startswith("/") or self.text.startswith(bot["symb"]):
                if self.text.startswith(bot["symb"]):
                    self.pers_command = True
                self.what = "command"
                self.command = self.text.split()[0][1:].lower()
                if self.command == "":
                    self.command = None
                else:
                    self.text = self.text.split()
                    if len(self.text) > 1:
                        self.text = ' '.join(self.text[1:])
                    else:
                        self.text = ""
                self.command = re.sub("@\w+bot", "", self.command, flags=re.IGNORECASE)

        if "sticker" in message:
            self.what = "sticker"
            self.item_id = message["sticker"]["file_id"]

        if "photo" in message:
            if message["photo"]:
                self.what = "photo"
                self.item_id = message["photo"][-1]["file_id"]

        if "document" in message:
            self.what = "document"
            self.item_id = message["document"]["file_id"]

        if "audio" in message:
            self.what = "audio"
            self.item_id = message["audio"]["file_id"]

        if "voice" in message:
            self.what = "voice"
            self.item_id = message["voice"]["file_id"]

        if "video" in message:
            self.what = "video"
            self.item_id = message["video"]["file_id"]

        if "caption" in message:
            self.text = message["caption"]


class DummyUser:
    def __init__(self, bot, message, name=None):
        self.message = Message(message, bot)
        if not name:
            self.name = "??"
        else:
            self.name = name
        self.username = "??"
        self.sname = "??"
        self.lang = "it"
        self.uid = 0
        self.is_to_bot = False
        self.is_admin = False
        self.is_owner = False
        self.is_master = False
        self.sesso = None
        self.lang_n = 0
        self.perms = NoPermisisons()


class User:
    def __init__(self, bot, x, message):
        self.message = Message(message, bot)
        self.name = x["first_name"]
        self.username = ""
        self.sname = ""
        self.lang = "it"
        self.uid = int(x["id"])
        self.is_to_bot = False
        self.is_admin = False
        self.is_owner = True if Manager.get_prop_id(bot["token"]) == self.uid else False
        if self.uid == owner_id:
            self.is_owner = True
        self.is_master = True if self.uid == owner_id else False
        self.sesso = None
        self.lang_n = 0

        if "username" in x:
            self.username = x["username"]

        if "last_name" in x:
            self.sname = x["last_name"]

        if "language_code" in x:
            self.lang = str(x["language_code"]).lower()

        if message["chat"]["type"] == 'private':
            to_read = "users"
        else:
            to_read = "groups"
        lang = DBs.read_obj(message["chat"]["id"], bot["id"], to_read)["ext2"]
        if lang:
            self.lang_n = int(lang)

        self.perms = Permissions(bot["token"], message["chat"]["id"], self.uid)

        if message["chat"]["type"] != 'private':
            self.is_admin = self.perms.is_admin

        if self.is_master:
            self.is_admin = True

        if not self.lang_n:
            self.lang_n = 0


class Infos:
    def __init__(self, bot, update):
        try:
            self.api = False
            self.time = time.time()

            message, tipe, what = get_message(update)
            self.error = False

            if not message:
                self.skip = True
                return

            self.skip = False
            self.prop_id = Manager.get_prop_id(bot["token"])
            self.what = what
            self.token = bot["token"]
            self.update_id = update["update_id"]
            self.bid = int(bot["id"])
            self.cid = int(message["chat"]["id"])
            tmp = DBs.read_obj(self.bid, self.bid, "users")["ext3"]
            if not tmp:
                self.admins = []
            else:
                self.admins = [int(uid) for uid in tmp.split()]

            self.admins.append(self.prop_id)

            self.entity = self.bid
            self.symbol = Utils.get_com_symbol(self.entity)
            bot["symb"] = self.symbol
            self.bot_name = bot["first_name"]
            self.username = bot["username"]

            if " " in bot["first_name"]:
                self.regex = Utils.regexa(bot["first_name"].lower().split()[0])
            else:
                self.regex = Utils.regexa(bot["first_name"].lower())

            self.regex = Utils.boundary(self.regex)
            self.text = ""
            self.group_username = None
            self.is_reply = False
            self.chat_private = False
            self.error = False
            self.edited = False
            self.admin = False
            self.to_user = None
            self.is_auto = False

            self.is_kitsu = False if 569510835 != self.bid else True

            if "from" in message:
                self.user = User(bot, message["from"], message)
            else:
                if what == "channel_post":
                    name = None
                    if "author_signature" in update["channel_post"]:
                        name = update["channel_post"]["author_signature"]
                    self.user = DummyUser(bot, message, name=name)
                else:
                    self.error = True
                    return

            self.name = message["chat"]["title"] if "title" in message["chat"] else message["chat"]["first_name"]

            self.lang = "ita" if "it" in self.user.lang else "eng"

            self.langn = 0 if "it" in self.user.lang else 1

            if "username" in message["chat"]:
                self.group_username = message["chat"]["username"]

            if "text" in message:
                self.text = message["text"]

            if what != "channel post":
                if "reply_to_message" in message:
                    self.to_user = User(bot, message["reply_to_message"]["from"], message["reply_to_message"])
                    self.is_auto = True if self.bid == self.to_user.uid else False
                    self.is_reply = True
                    if self.to_user.uid == self.bid:
                        self.to_user.is_to_bot = True

            if message["chat"]["type"] == 'private':
                self.chat_private = True
                self.admin = True
            else:
                self.perms = Permissions(bot["token"], message["chat"]["id"], self.bid)
                self.admin = self.perms.is_admin

            self.bot_count = 0

            if tipe:
                self.edited = True
                self.time_diff = int(abs((datetime.strptime(self.user.message.my_time, "%H:%M:%S")
                                          - datetime.strptime(self.user.message.time, "%H:%M:%S")).seconds))
                self.timed_out = True if self.time_diff > 7 else False

            self.text = self.user.message.text

            self.args = None

            if ": " in self.text:
                tmp_args = self.text.split(": ")
                if len(tmp_args) > 1:
                    self.args = self.text.split(": ")[1]

        except Exception as err:
            Log.w("Qualcosa è andato storto: %s" % err)
            # pprint.pprint(update)
            self.error = True

    def reply(self, text, quote=None, markdown=None, **kwargs):
        return HTTPLL.sendMessage(self.token, self.cid, text,
                                  reply_to_message_id=self.user.message.id if quote else None,
                                  parse_mode="markdown" if markdown else None, **kwargs)

    def master_message(self, text, parse_mode=None):
        return HTTPLL.sendMessage(self.token, self.prop_id, text, parse_mode=parse_mode)
