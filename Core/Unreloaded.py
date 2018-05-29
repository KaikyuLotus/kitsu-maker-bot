# coding=utf-8

# Copyright (c) 2017 Kaikyu

import json
import os
import threading
import time

from Utils import Logger as Log, Utils
import psutil

from Core import HTTPLL


# Thanks to Python Telegram Bot for this MWT
class MWT(object):
    _caches = {}
    _timeouts = {}

    def __init__(self, timeout=2):
        self.timeout = timeout

    def collect(self):
        for func in self._caches:
            cache = {}
            for key in self._caches[func]:
                if (time.time() - self._caches[func][key][1]) < self._timeouts[func]:
                    cache[key] = self._caches[func][key]
            self._caches[func] = cache

    def __call__(self, f):
        self.cache = self._caches[f] = {}
        self._timeouts[f] = self.timeout

        def func(*args, **kwargs):
            kw = sorted(kwargs.items())
            key = (args, tuple(kw))
            try:
                v = self.cache[key]
                if (time.time() - v[1]) > self.timeout:
                    raise KeyError
            except KeyError:
                v = self.cache[key] = f(*args, **kwargs), time.time()
            return v[0]

        func.func_name = f.__name__

        return func


delete_codes = {}
antisp = {}
scores = {}
gbots = {}

p = psutil.Process(os.getpid())


def blacklista(uid):
    blacklist = json.loads(open("Files/jsons/blacklist.json").read())
    blacklist.append(uid)
    with open("Files/jsons/blacklist.json", "w") as fl:
        fl.write(json.dumps(blacklist))


def remover(uid, entity):
    time.sleep(Utils.get_antispam_time(entity))
    antisp[entity].remove(uid)


def antispam(infos):
    entity = str(infos.entity)
    if entity not in antisp:
        antisp[entity] = []

    if infos.user.uid in antisp[entity]:

        if infos.user.uid not in scores:
            scores[infos.user.uid] = 0

        scores[infos.user.uid] += 1

        Log.w("%s <- %s -> [spam %s]" % (infos.bid, infos.user.uid, scores[infos.user.uid]))

        if scores[infos.user.uid] == 30:
            blacklista(infos.user.uid)
            infos.reply("Utente ID %s blacklistato." % infos.user.uid)
            Log.w("Utente ID %s blacklistato." % infos.user.uid)

        return True
    else:
        antisp[entity].append(infos.user.uid)
        threading.Thread(target=remover, args=(infos.user.uid, entity)).start()
        return False


@MWT(timeout=240)
def get_admin_ids(chat_id, token):
    return [admin for admin in HTTPLL.getChatAdministrators(token, chat_id)]


def get_cpu():
    return p.cpu_percent()


def get_memory():
    return int(p.memory_info()[0] / float(2 ** 20))


def get_time():
    return p.create_time()


def get_system_memory():
    mem = psutil.virtual_memory()
    return (mem[0] - mem[1]) >> 20


def set_delete_code(uid, code):
    delete_codes[str(uid)] = str(code)
    return True


def get_delete_code(uid):
    if str(uid) in delete_codes:
        return delete_codes[str(uid)]
    else:
        return ""
