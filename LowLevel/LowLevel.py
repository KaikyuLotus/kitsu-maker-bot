# coding=utf-8
import json
import os
import time
import codecs
import shutil

from Utils import Logger as Log


def name_regexer(name):
    namer = ""
    for char in name.lower():
        if char in "aeiouy":
            namer += char + "+"
        else:
            namer += char
    return namer


def defaults_loader(bid):
    try:
        bid = str(bid)
        os.makedirs("Files/bot_files/" + bid)

        names = ["dialogs.json", "triggers.json", "dialogs_eng.json", "triggers_eng.json"]
        for name in names:
            with open("Files/bot_files/%s/%s" % (bid, name), "w") as f:
                f.write(open("Files/bot_files/default/%s" % name).read())

    except Exception as err:
        print(err)


def check_files(bid):
    bid = str(bid)
    if not os.path.exists("Files/bot_files/" + bid):
        defaults_loader(bid)
        return True
    names = ["dialogs.json", "triggers.json", "dialogs_eng.json", "triggers_eng.json"]
    for name in names:
        if not os.path.isfile("Files/bot_files/%s/%s" % (bid, name)):
            with open("Files/bot_files/%s/%s" % (bid, name), "w") as f:
                f.write(open("Files/bot_files/default/%s" % name).read())
    if os.path.isfile("Files/bot_files/%s/%s" % (bid, "triggers.jsons")):
        os.remove("Files/bot_files/%s/%s" % (bid, "triggers.jsons"))
    return False


def delete_files(bid):
    if not bid:
        Log.w("Non posso eliminare i bot di None")
        return False

    bid = str(bid)
    try:
        shutil.rmtree("Files/bot_files/" + bid)
        Log.d("File rimossi")
        return True
    except:
        Log.w("I file del bot %s non esistono" % bid)
        return False


def get_moment():
    actual = int(time.strftime("%H"))
    if 5 < actual < 12:
        return "Mattina"
    if 12 <= actual < 18:
        return "Pomeriggio"
    if 18 <= actual < 23:
        return "Sera"
    if 23 <= actual:
        return "Notte"
    if actual <= 5:
        return "Notte"


def get_time(t0): return str(int((time.time() - t0) * 1000))


def read(name, bot_id): return json.loads(codecs.open("Files/bot_files/%s/%s" % (bot_id, name)).read(), encoding='utf8')


def dial_read(lang):
    try:
        return json.loads(codecs.open("Files/jsons/%s.json" % lang, encoding='utf8').read())
    except Exception as err:
        print("Linguaggio non trovato (%s) o file corrotto." % lang)
        return None


def get_triggers(bid, name):
    triggs = read(name, bid)
    return {
            "interactions": triggs["interactions"],
            "eteractions": triggs["eteractions"],
            "contents": triggs["contents"],
            "equals": triggs["equals"],
            "admin_actions": triggs["admin_actions"],
            "bot_commands": triggs["bot_commands"]
            }


def jfile(desc, bid, lang):
    try:
        if not bid:
            print("Impossibile leggere con bid nullo.")
            return False

        lang = int(lang)
        f = None
        if desc == "d":
            if lang == 0:
                try:
                    return read("dialogs.json", bid)
                except:
                    pass
            try:
                return read("dialogs_eng.json", bid)
            except:
                return read("dialogs.json", bid)

        if desc == "t":
            if lang == 0:
                return read("triggers.json", bid)
            return read("triggers_eng.json", bid)

        if desc == "c":
            if lang == 0:
                return read("condizioni.json", bid)
            return read("condizioni_eng.json", bid)

        if not f:
            return print("Descrittore errato (%s)." % desc)
        return json.loads(open("Files/bot_files/%s/%s" % (bid, f)).read())
    except Exception as err:
        Log.w("File non trovato? %s" % err)
        return None


def jwrite(desc, bid, jsn, lang):
    try:
        if not bid:
            print("Impossibile scrivere con bid nullo.")
            return False
        f = None
        if desc == "d": f = "dialogs"
        if desc == "t": f = "triggers"
        if lang != 0: f += "_eng.json"
        else:
            f += ".json"

        if not f:
            return print("Descrittore errato.")
        with open("Files/bot_files/%s/%s" % (bid, f), "w") as fl: fl.write(json.dumps(jsn))
        return True
    except Exception as err:
        print("Errore in jwrite %s" % err)
        return False


def write_stats(obj, value, obj2=None):
    try:
        sts = json.loads(open("Files/jsons/stats.json").read())
        if not obj2:
            sts[obj] = value
        else:
            try:
                sts[obj][obj2] = value
            except:
                sts[obj] = {}
                sts[obj][obj2] = value
        with open("Files/jsons/stats.json", "w") as fl:
            fl.write(json.dumps(sts))
        return True
    except Exception as err:
        Log.e(err)
        return False


def add_risposta(bid, risp, sec, lang):
    try:
        dials = jfile("d", bid, lang)
        dials[sec].append(risp)
        return True if jwrite("d", bid, dials, lang) else False
    except Exception as err:
        return False


def get_stats_file(bid):
    try:
        return json.loads(open("Files/bot_files/%s/trig_usage.json" % bid).read())
    except:
        return {}


def write_stats_file(bid, stats):
    with open("Files/bot_files/%s/trig_usage.json" % bid, "w") as fl:
        fl.write(json.dumps(stats))
