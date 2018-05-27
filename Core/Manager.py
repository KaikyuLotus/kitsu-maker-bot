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

import codecs
import json

from Utils import Logger as Log
from Cache import BotCache


def read_bot_list(): return json.loads(open("Files/jsons/bots.json").read())


def get_token_list(): return [key for key in json.loads(open("Files/jsons/bots.json").read())]


def is_token_used(token): return True if token in json.loads(open("Files/jsons/bots.json").read()) else False


def get_online_bots(): return json.loads(open("Files/jsons/stats.json").read())["online_bots"]


def get_bot_count():
    try:
        return len(get_token_list())
    except:
        print("Cannot get token list!!")
        return 0


def get_bot_instance(bid):
    try:
        return BotCache.bots[str(bid)]
    except:
        print("Errore critico, il bot non esiste.")
        return None


def get_prop_id(token):
    try:
        return json.loads(open("Files/jsons/bots.json").read())[token]["user_id"]
    except Exception:
        Log.e("Token non trovata nel db.")
        return None


def get_bot_from_token(token):
    try:
        return json.loads(open("Files/jsons/bots.json").read())[token]
    except Exception as err:
        Log.e(err)
        return None


def has_a_bot(uid):
    int(uid)
    bots = json.loads(open("Files/jsons/bots.json").read())
    for token in bots:
        if bots[token]["user_id"] == uid:
            return True
    return False


def count_bots(uid):
    int(uid)
    tot = 0
    bots = json.loads(open("Files/jsons/bots.json").read())
    for token in bots:
        if bots[token]["user_id"] == uid:
            tot += 1
    return tot


def add_bot(user_id, bot_id, bot_token):
    try:
        new = {"user_id": user_id, "bot_id": bot_id}
        bots = json.loads(open("Files/jsons/bots.json").read())
        bots[bot_token] = new
        Log.d("Nuovo bot (%s) aggiunto al file bots" % bot_id)
        with open("Files/jsons/bots.json", "w") as fl:
            fl.write(json.dumps(bots))
        return True
    except Exception as err:
        Log.e(err)
        return False


def get_bots_id():
    bots = json.loads(open("Files/jsons/bots.json").read())
    return [bots[token]["bot_id"] for token in bots]


def get_botid_from_prop_id(pid):
    """
        Ritorna una lista contenente tutti i bot dell'utente
        Se l'utente non ha un bot ritorna una lista vuota
    """
    pid = int(pid)
    bids = []
    bots = json.loads(open("Files/jsons/bots.json").read())
    for token in bots:
        if bots[token]["user_id"] == pid:
            bids.append(bots[token]["bot_id"])
    return bids


def get_botid_from_token(token):
    """
        Ritorna una lista contenente tutti i bot dell'utente
        Se l'utente non ha un bot ritorna una lista vuota
    """
    bots = json.loads(open("Files/jsons/bots.json").read())
    if token in bots:
        bid = token.split(":")[0]
        return bid
    return None


def get_token_from_bot_id(bid):
    bid = int(bid)
    bots = json.loads(open("Files/jsons/bots.json").read())
    for token in bots:
        if int(bots[token]["bot_id"]) == bid:
            return token
    print("Bot ID (%s) non trovato ? ? ?" % bid)
    return None


def get_tokens_from_prop_id(pid):
    """
        Ritorna una lista contenente tutti i bot dell'utente
        Se l'utente non ha un bot ritorna una lista vuota
    """
    pid = int(pid)
    tokens = []
    bots = json.loads(open("Files/jsons/bots.json").read())
    for token in bots:
        if bots[token]["user_id"] == pid:
            tokens.append(token)
    return tokens


def delete_bot(bid):
    bots = json.loads(open("Files/jsons/bots.json").read())
    token = get_token_from_bot_id(bid)

    if not token:
        Log.d("Token (%s) non trovata!" % token)
        return False

    try:
        del bots[token]
    except:
        Log.w("Token non trovata?")
        return False

    with open("Files/jsons/bots.json", "w") as fl:
        fl.write(json.dumps(bots))

    Log.d("File bots scritto")
    return True


def is_kitsu_bot(bid):
    bid = int(bid)
    bots = json.loads(open("Files/jsons/bots.json").read())
    for token in bots:
        if bots[token]["bot_id"] == bid:
            return True
    else:
        return False


def trigger_count(bid):
    trigs = json.loads(codecs.open("Files/bot_files/%s/%s" % (bid, "triggers.json")).read(), encoding='utf8')

    tot = sum([len(trigs["interactions"]),
               len(trigs["eteractions"]),
               len(trigs["contents"]),
               len(trigs["equals"]),
               len(trigs["admin_actions"]),
               len(trigs["bot_commands"])])

    return tot
