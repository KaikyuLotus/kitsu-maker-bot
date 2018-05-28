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


import json
import re

import datetime

from Utils import Logger as Log

import base64
import time

from Core import HTTPLL, Manager
from Core import ThreadedCore as Core
from Cache import BotCache
from Core.Error import NotFound404

def_sections = ["bene", "saluti", "scuse", "amare", "insulti", "notte", "giorno", "ringraziamenti", "complimenti"]

ver = "0.1.8"


def add_trigger(token, trigger, t_type, lang_n):
    try:
        bid = token.split(":")[0]
        if not lang_n:
            lang_n = 0

        if not trigger:
            return "Trigger not specified.", False

        if lang_n != 0:
            triggers = "triggers_eng.json"
            dialogs = "dialogs_eng.json"
        else:
            triggers = "triggers.json"
            dialogs = "dialogs.json"

        if trigger == "":
            return "Devi specificare il trigger!", False

        if not t_type:
            try:
                sec = int(trigger.split(" [")[1].replace("]", ""))
            except:
                return "Non hai inserito un [n] valido!", False
        else:
            if not t_type.isdigit:
                return "[n] deve essere un decimale.", False
            sec = int(t_type)

        if sec < 1 or sec > 6:
            return "I tipi di trigger vanno da 1 a 6 consulta la guida a riguardo!", False

        section = ["contents", "interactions", "equals", "eteractions", "admin_actions", "bot_commands"][sec - 1]
        trigger = trigger.split(" [")[0].lower()

        trigs = json.loads(open("Files/bot_files/%s/%s" % (bid, triggers)).read())
        if trigger in trigs[section]:
            return "Questo trigger e' gia' esistente!", False

        tmp = trigger
        if trigger in ["autom", "insulti", "complimenti", "saluti", "scuse", "giorno", "notte", "bene"]:
            return "Non puoi sovrascrivere un trigger default!", False

        if trigger.startswith("&") or trigger.startswith("|"):
            return "Il trigger non puo' iniziare con & o |, kitsu ><", False

        if trigger.endswith("&") or trigger.endswith("|"):
            return "Il trigger non puo' finire con & o |, kitsu ><", False

        if trigger.count("&") > 1 or trigger.count("|") > 1:
            return "Il trigger non puo' contenere piu' di un & o |, kitsu!", False

        tmp = tmp.replace(" ", "_")

        for sec in def_sections:
            for trig in trigs[sec].split():
                if re.search(r"\b" + re.escape(tmp) + r"\b", trig):
                    return "Stai cercando di sovrascrivere il trigger %s nella sezione %s!" % (trigger, sec), False

        trigs[section].append(trigger)
        with open("Files/bot_files/%s/%s" % (bid, triggers), "w") as file_t:
            file_t.write(json.dumps(trigs))

        dials = json.loads(open("Files/bot_files/%s/%s" % (bid, dialogs)).read())
        dials[trigger] = []

        with open("Files/bot_files/%s/%s" % (bid, dialogs), "w") as file_d:
            file_d.write(json.dumps(dials))

        if token not in BotCache.bots:
            BotCache.bots[token] = HTTPLL.getMe(token)
        bname = BotCache.bots[token]["first_name"]

        return "Il bot %s ha imparato %s di tipo %s" % (bname, trigger, section), True
    except Exception as err:
        Log.e(err)
        return "S-si è verificato un errore...\n%s" % err, False


def del_trigger(token, trigger, t_type, lang_n):
    bid = token.split(":")[0]
    if not lang_n:
        lang_n = 0

    if not trigger:
        return "Trigger not specified.", False

    try:

        if lang_n != 0:
            triggers = "triggers_eng.json"
            dialogs = "dialogs_eng.json"
        else:
            triggers = "triggers.json"
            dialogs = "dialogs.json"

        if trigger == "":
            return "Devi specificare il trigger da cui eliminare le risposte.", False

        if not t_type:
            try:
                sec = int(trigger.split(" [")[1].replace("]", ""))
            except:
                return "Non hai inserito un [n] valido!", False
        else:
            if not t_type.isdigit:
                return "[n] deve essere un decimale.", False
            sec = int(t_type)

        if sec < 1 or sec > 6:
            return "Non credo che [%s] sia compreso tra 1 e 6." % sec, False

        section = ["contents", "interactions", "equals", "eteractions", "admin_actions", "bot_commands"][sec - 1]
        trigger = trigger.split(" [")[0].lower()

        trigs = json.loads(open("Files/bot_files/%s/%s" % (bid, triggers)).read())
        if trigger not in trigs[section]:
            return "Non ho trovato il trigger richiesto.", False

        trigs[section].remove(trigger)
        with open("Files/bot_files/%s/%s" % (bid, triggers), "w") as file_t:
            file_t.write(json.dumps(trigs))

        dials = json.loads(open("Files/bot_files/%s/%s" % (bid, dialogs)).read())

        add = ""

        if trigger not in dials:
            add = "\nPerò non vi era alcuna sezione dei dialoghi con lo stesso nome!"
        else:
            if len(dials[trigger]) == 0:
                add = "\nNon c'erano frasi da eliminare."

            del dials[trigger]
            with open("Files/bot_files/%s/%s" % (bid, dialogs), "w") as file_d:
                file_d.write(json.dumps(dials))

        if token not in BotCache.bots:
            BotCache.bots[token] = HTTPLL.getMe(token)
        bname = BotCache.bots[token]["first_name"]

        return "Il bot %s ha dimenticato %s di tipo %s%s" % (bname, trigger, section, add), True
    except Exception as err:
        Log.e(err)
        return "S-si è verificato un errore...", False


def add_risposta(token, trigger, replies, lang_n):
    try:
        bid = token.split(":")[0]
        if not lang_n:
            lang_n = 0

        if lang_n != 0:
            dialogs = "dialogs_eng.json"
        else:
            dialogs = "dialogs.json"

        if replies == "":
            return "Devi specificare la sezione/trigger a cui aggiungere la/e risposte.", False

        if isinstance(replies, list):
            frasi = replies
        else:
            com = replies
            if " | " not in com:
                return "Devi dirmi le frasi o la frase da aggiungere a trigger", False

            comps = com.split(" | ")

            trigger = comps[0]
            trigger = trigger.lower()
            frasi = comps[1:]

        for frase in frasi:
            if frase.count("[private]") > 1:
                return "Ogni risposta puo' contenere un solo tag \"[private]\"!", False

            if frase.endswith("[private]"):
                return "Il tag [private] puo' andare tra due risposte o ad inizio risposta.", False

        dials = json.loads(open("Files/bot_files/%s/%s" % (bid, dialogs)).read())
        try:
            dials[trigger].extend(frasi)
        except Exception:
            return "Non ho trovato il trigger/sezione %s." % trigger, False

        com = " ".join(frasi)

        if com.count("<b>") != com.count("</b>") or com.count("<i>") != com.count("</i>") \
                or com.count("<c>") != com.count("</c>") or com.count("<link>") != com.count("</link>"):
            return "Formattazione non valida.", False

        if "<link>" in com:
            if com.count(":>") != com.count("<link>") or ":></link>" in com:
                return "Descrizione del link mancante.", False

        with open("Files/bot_files/%s/%s" % (bid, dialogs), "w") as file_d:
            file_d.write(json.dumps(dials))

        return "Nuove frasi imparate! Vai a provarle~", True

    except Exception as err:
        Log.e(err)
        return "S-si è verificato un errore..."


def add_interazione(infos):
    say = infos.reply
    try:
        if infos.user.lang_n != 0:
            dialogs = "dialogs_eng.json"
        else:
            dialogs = "dialogs.json"

        lang_itm = "IT" if infos.user.lang_n == 0 else "EN"

        user = infos.user.username
        uid = infos.user.uid

        if infos.text == "":
            say("Devi specificare il nome della sezione da creare.")
            return Log.a(
                "[Bot: @%s | %s] user: %s ID: %s 'senza trigger'" % (infos.username, infos.user.uid, user, uid))

        trigger = infos.text.lower()
        dials = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, dialogs)).read())
        if trigger in dials:
            return say("Questa sezione e' gia' presente ~")
        else:
            dials[trigger] = []

        with open("Files/bot_files/%s/%s" % (infos.bid, dialogs), "w") as file_d:
            file_d.write(json.dumps(dials))

        say("Sezione aggiunta! (%s)\nAggiungici cio' che vuoi ~" % lang_itm)
        Log.a("[Bot: @%s | %s] user: %s ID: %s 'add_frase riuscito'" % (infos.username, infos.user.uid, user, uid))

    except Exception as err:
        Log.e(err)
        say("S-si è verificato un errore...")


def autorizza(infos):
    try:
        if infos.text == "":
            return infos.reply("Devi dirmi un ID!")

        if not infos.text.isdigit():
            return infos.reply("L'ID e' un numero decimale!")

        auth_id = int(infos.text)

        if auth_id == infos.bid:
            return infos.reply("Non puoi autorizzare il tuo stesso bot!")

        if auth_id not in Manager.get_bots_id():
            return infos.reply("Puoi autorizzare solo kitsubots!")

        trigs = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, "triggers.json")).read())
        if "autorizzati" not in trigs:
            trigs["autorizzati"] = [auth_id]
        else:
            if auth_id in trigs["autorizzati"]:
                return infos.reply("Hai gia' autorizzato questo ID!")
            else:
                trigs["autorizzati"].append(auth_id)

        with open("Files/bot_files/%s/%s" % (infos.bid, "triggers.json"), "w") as fl:
            fl.write(json.dumps(trigs))

        return infos.reply("Fatto! ID %s autorizzato!" % auth_id)
    except Exception as err:
        infos.reply("Errore: %s" % err)


# ok
def del_risps(token, section, lang_n=None):
    try:
        bid = token.split(":")[0]
        if not lang_n:
            lang_n = 0

        if lang_n != 0:
            dialogs = "dialogs_eng.json"
        else:
            dialogs = "dialogs.json"

        if section == "":
            return "Devi specificare la sezione/trigger da cui eliminare le risposte.", False

        trigger = section.lower()

        dials = json.loads(open("Files/bot_files/%s/%s" % (bid, dialogs)).read())

        if trigger not in dials:
            return "non ho trovato il trigger richiesto (%s)" % trigger, False

        if not dials[trigger]:
            return "Non ci sono gia' frasi in questa sezione.", False

        dials[trigger] = []

        with open("Files/bot_files/%s/%s" % (bid, dialogs), "w") as file_d:
            file_d.write(json.dumps(dials))

        return "Risposte dal trigger %s eliminate." % trigger, True
    except Exception as err:
        Log.e(err)
        return "S-si è verificato un errore...", False


# ok
def list_risps(infos):
    say = infos.reply
    try:

        if infos.user.lang_n != 0:
            dialogs = "dialogs_eng.json"
        else:
            dialogs = "dialogs.json"

        lang_itm = "IT" if infos.user.lang_n == 0 else "EN"

        if infos.text == "":
            say("Devi specificare il trigger da cui eliminare le risposte.")
            return

        trigger = infos.text.lower()

        dials = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, dialogs)).read())

        if trigger not in dials:
            say("Non ho trovato questa sezione.. kitsu...")
            return

        if not dials[trigger]:
            say("Non ci sono gia' frasi in questa sezione kitsu!")
            return

        msg = "Ecco le frasi (%s) per `%s`:\n\n" % (lang_itm, trigger)
        frasi = dials[trigger]
        x = 1
        for frase in frasi:
            msg += "`%s`) `%s`\n\n" % (x, frase)
            x += 1

        msg += "\nTotale di %s frasi!" % len(frasi)

        say(msg, markdown=True)

        Log.a("%s <- %s -> [list_risposte]" % (infos.bid, infos.user.uid))
    except Exception as err:
        say("S-si è verificato un errore...")
        Log.e(err)


def list_risps_form(infos):
    say = infos.reply
    try:

        if infos.user.lang_n != 0:
            dialogs = "dialogs_eng.json"
        else:
            dialogs = "dialogs.json"

        if infos.text == "":
            say("Devi specificare il trigger per cui listare le risposte.")
            return

        trigger = infos.text.lower()

        dials = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, dialogs)).read())

        if trigger not in dials:
            say("Non ho trovato questa sezione.. kitsu...")
            return

        if not dials[trigger]:
            say("Non ci sono gia' frasi in questa sezione kitsu!")
            return

        com = "Ecco a te:\n`%s" % trigger
        for frase in dials[trigger]:
            com += " | %s" % frase
        com += "`"

        say(com, markdown=True)

        Log.a("%s <- %s -> [list_risposte_form]" % (infos.bid, infos.user.uid))
    except Exception as err:
        say("S-si è verificato un errore...")
        Log.e(err)


# ok
def del_default(infos):
    say = infos.reply
    try:
        user = infos.user.username
        uid = infos.user.uid

        if infos.user.lang_n != 0:
            triggers = "triggers_eng.json"
        else:
            triggers = "triggers.json"

        lang_itm = "IT" if infos.user.lang_n == 0 else "EN"

        if infos.text == "":
            say("Cosa devo kitsueliminare?")
            return Log.a(
                "[Bot: @%s | %s] user: %s ID: %s 'senza trigger'" % (infos.username, infos.user.uid, user, uid))

        trigger = infos.text.lower()
        try:
            sec = trigger.split(" | ")[0]
            parola = trigger.split(" | ")[1]
        except:
            say("La sintassi e' \"/del_default default | trigger\"!")
            return Log.a("[Bot: @%s | %s] user: %s ID: %s 'del_risposte senza args necs'" % (infos.username,
                                                                                             infos.user.uid,
                                                                                             user, uid))
        trigs = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, triggers)).read())

        if sec not in trigs:
            say("Non credo esista questo default...")
            return Log.a("[Bot: @%s | %s] user: %s ID: %s 'del_risposte senza avere il trigger'" % (infos.username,
                                                                                                    infos.user.uid,
                                                                                                    user, uid))

        if not trigs[sec]:
            say("Ma questo default e' kitsuvuoto...")
            return Log.a("[Bot: @%s | %s] user: %s ID: %s 'del_risposte senza frasi'" % (infos.username, infos.user.uid,
                                                                                         user, uid))

        if parola not in trigs[sec]:
            say("Questo trigger non e' in %s, kitsu e.e" % sec)
            return Log.a("[Bot: @%s | %s] user: %s ID: %s 'del_risposte senza frasi'" % (infos.username, infos.user.uid,
                                                                                         user, uid))

        if parola + " " in trigs[sec]:
            trigs[sec] = trigs[sec].replace(parola + " ", "")
        else:
            trigs[sec] = trigs[sec].replace(" " + parola, "")
        with open("Files/bot_files/%s/%s" % (infos.bid, triggers), "w") as file_d:
            file_d.write(json.dumps(trigs))

        say("Default (%s) kitsueliminato!! ~" % lang_itm)
        Log.a("[Bot: @%s | %s] user: %s ID: %s 'del_default riuscito'" % (infos.username, infos.user.uid, user, uid))
    except Exception as err:
        say("S-si è verificato un errore...")
        Log.e(err)


# ok
def list_default(token, text, lang_n):
    try:
        bid = token.split(":")[0]
        default = text.lower()

        if lang_n != 0:
            triggers = "triggers_eng.json"
        else:
            triggers = "triggers.json"

        lang_itm = "IT" if lang_n == 0 else "EN"

        if text == "":
            return "Devi dirmi il default del quale elencare i trigger", False

        triggers = json.loads(open("Files/bot_files/%s/%s" % (bid, triggers)).read())

        if default not in ["complimenti", "bene", "insulti", "scuse", "ringraziamenti", "saluti", "amare"]:
            return "Non ho trovato questa sezione.. kitsu...", False

        if default not in triggers:
            return "Non ho trovato questa sezione.. kitsu...", False

        if not triggers[default]:
            return "ma... Questo default e'... kitsuvuoto!", False

        msg = "Ecco i trigger (%s) default per %s:\n\n" % (lang_itm, default)
        trigs = triggers[default]
        msg += trigs
        msg += "\n\nTotale di %s triggers!" % len(trigs.split())

        return msg, True
    except Exception as err:
        Log.e(err)
        return "Qualcosa e' andato storto...", False


def set_nascita(infos):
    say = infos.reply
    try:
        data_nascita = infos.text.lower()

        if infos.user.lang_n != 0:
            dialogs = "dialogs_eng.json"
        else:
            dialogs = "dialogs.json"

        if infos.text == "":
            return say("Devi dirmi la data di nasciata nel formato DD/MM/YYYY")

        dialogs_f = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, dialogs)).read())

        try:
            d, m, y = data_nascita.split("/")
            datetime.date(int(y), int(m), int(d))
        except Exception as err:
            return say("A quanto pare %s non e' una data reale (%s)" % (infos.text, err))

        dialogs_f["data_nascita"] = data_nascita

        with open("Files/bot_files/%s/%s" % (infos.bid, dialogs), "w") as file_d:
            file_d.write(json.dumps(dialogs_f))

        say("Data di nascita impostata a %s!" % infos.text)
    except Exception as err:
        say("S-si è verificato un errore...")
        Log.e(err)


def set_symbol(infos):
    say = infos.reply
    try:
        if infos.user.lang_n != 0:
            triggers = "triggers_eng.json"
        else:
            triggers = "triggers.json"

        if infos.text == "":
            return say("Devi dirmi il simbolo con cui riconoscero' i comandi!")
        if len(infos.text) > 1:
            return say("Il simbolo puo' essere di un solo carattere!")

        trigs = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, triggers)).read())
        trigs["bot_comm_symbol"] = infos.text

        with open("Files/bot_files/%s/%s" % (infos.bid, triggers), "w") as file_d:
            file_d.write(json.dumps(trigs))

        say("*%s* impostato come simbolo per i comandi!" % infos.text, markdown=True)
    except Exception as err:
        say("S-si è verificato un errore...")
        Log.e(err)


def set_antispam_time(infos):
    say = infos.reply
    try:
        if infos.user.lang_n != 0:
            triggers = "triggers_eng.json"
        else:
            triggers = "triggers.json"

        if infos.text == "":
            return say("Devi dirmi un numero che indica il tempo di antispam!")

        try:
            infos.text = float(infos.text)
        except ValueError:
            return say("L'antispam time deve essere un numero intero o un decimale!")

        if infos.text > 10:
            return say("L'antispam time deve essere compreso tra 1.2 e 10!")

        if infos.text < 1.2:
            return say("L'antispam time deve essere compreso tra 1.2 e 10!")

        trigs = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, triggers)).read())
        trigs["antispam time"] = infos.text

        with open("Files/bot_files/%s/%s" % (infos.bid, triggers), "w") as file_d:
            file_d.write(json.dumps(trigs))

        say("*%s* impostato come antispam time!" % infos.text, markdown=True)
    except Exception as err:
        say("S-si è verificato un errore...")
        Log.e(err)


def del_risp(infos):
    say = infos.reply
    try:

        if infos.user.lang_n != 0:
            dialogs = "dialogs_eng.json"
        else:
            dialogs = "dialogs.json"

        if infos.text == "":
            return say("Devi specificare la sezione da cui eliminare e il numero della frase da eliminare:\n"
                       "/del_risposta sezione (n)")

        trigger = infos.text.lower()

        matches = re.search("\(\d+\)", trigger)
        if matches:
            n = matches.group(0)
            trigger = trigger.replace(" " + n, "").replace(n, "")
            n = int(re.search("\d+", n).group(0))
            if n < 1:
                return say("(n) non valida \"(%s)\"" % n)
        else:
            return say("Non hai specificato il numero della risposta da eliminare \"(n)\"")

        dials = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, dialogs)).read())

        if trigger not in dials:
            return say("non ho trovato il trigger %s." % trigger)

        if not dials[trigger]:
            return say("Non ci sono gia' frasi in questa sezione kitsu!")

        if len(dials[trigger]) < n:
            return say("Ci sono %s risposte, impossibile trovare la risposta n°%s..." % (len(dials[trigger]), n))

        phrase = dials[trigger].pop(n - 1)

        with open("Files/bot_files/%s/%s" % (infos.bid, dialogs), "w") as file_d:
            file_d.write(json.dumps(dials))

        say("Frase:\n`%s`\nEliminata con successo." % phrase, markdown=True)
    except Exception as err:
        say("S-si è verificato un errore...")
        Log.e(err)


def list_sezioni(infos):
    say = infos.reply
    try:
        if infos.user.lang_n != 0:
            dialogs = "dialogs_eng.json"
        else:
            dialogs = "dialogs.json"

        dials = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, dialogs)).read())

        msg = "Ecco le mie sezioni dei dialoghi:\nSezione    [numero risposte]\n\n"
        for section in dials:
            msg += "%s      [%s]\n" % (section, len(dials[section]))

        msg += "\nTotale di %s sezioni." % len(dials)

        say(msg)
    except Exception as err:
        say("S-si è verificato un errore...")
        Log.e(err)


def encode(key, clear):
    enc = []
    for i in range(len(clear)):
        key_c = key[i % len(key)]
        enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
        enc.append(enc_c)
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()


def decode(key, enc):
    dec = []
    enc = base64.urlsafe_b64decode(enc).decode()
    for i in range(len(enc)):
        key_c = key[i % len(key)]
        dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
        dec.append(dec_c)
    return "".join(dec)


def backup(infos):
    say = infos.reply
    try:
        if infos.user.lang_n != 0:
            dialogs = "dialogs_eng.json"
            triggers = "triggers_eng.json"
        else:
            dialogs = "dialogs.json"
            triggers = "triggers.json"

        name = "Files/bot_files/%s/backup - %s.kb" % (infos.bid, time.strftime("%A - %H:%M:%S"))
        d = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, dialogs)).read())
        t = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, triggers)).read())
        f = json.dumps({"dialogs": d, "triggers": t})
        with open(name, "w") as fl:
            fl.write(encode("kitsu", f))

        HTTPLL.sendFileDocument(infos.token, infos.cid, name, caption="Ecco il backup.")
    except Exception as err:
        say("S-si è verificato un errore...")
        say(str(err))
        Log.e(err)


def restore(content, bid, lang_n):
    try:
        if lang_n != 0:
            dialogs = "dialogs_eng.json"
            triggers = "triggers_eng.json"
        else:
            dialogs = "dialogs.json"
            triggers = "triggers.json"

        new = decode("kitsu", content)
        x = json.loads(new)
        Log.d("Decode ok! JSON ok!")

        if "dialogs" not in x or "triggers" not in x:
            return False, "File di backup invalido!"

        with open("Files/bot_files/%s/%s" % (bid, dialogs), "w") as f:
            f.write(json.dumps(x["dialogs"]))
        with open("Files/bot_files/%s/%s" % (bid, triggers), "w") as f:
            f.write(json.dumps(x["triggers"]))

        return True, "Backup ripristinato con successo!"

    except Exception as err:
        Log.e(err)
        return False, str(err)


def del_trigger_vuoti(infos):
    say = infos.reply
    try:

        if infos.user.lang_n != 0:
            triggers = "triggers_eng.json"
            dialogs = "dialogs_eng.json"
        else:
            triggers = "triggers.json"
            dialogs = "dialogs.json"

        dials = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, dialogs)).read())
        trigs = json.loads(open("Files/bot_files/%s/%s" % (infos.bid, triggers)).read())

        sections = ["contents", "interactions", "equals", "eteractions", "admin_actions", "bot_commands"]
        msg = "Sezioni rimosse:\n"
        msg2 = "Trigger rimossi:\n"

        to_remove = []
        for sezione in dials.keys():
            if not dials[sezione]:
                to_remove.append(sezione)
                # dials.pop(sezione)
                msg += "- `%s`\n" % sezione
                for section in sections:
                    if sezione in trigs[section]:
                        trigs[section].remove(sezione)
                        msg += "- `%s`\n" % sezione

        for element in to_remove:
            dials.pop(element)

        msg = msg + msg2

        with open("Files/bot_files/%s/%s" % (infos.bid, dialogs), "w") as file_d:
            file_d.write(json.dumps(dials))

        with open("Files/bot_files/%s/%s" % (infos.bid, triggers), "w") as file_d:
            file_d.write(json.dumps(trigs))

        msg += "\nEseguito con successo!"
        say(msg, markdown=True)

    except Exception as err:
        say("S-si è verificato un errore...")
        Log.e(err)


def change_token(infos):
    token = infos.text
    try:
        bot = HTTPLL.getMe(token)

    except NotFound404:
        infos.reply("Token non valida.")
        return

    except Exception as err:
        infos.reply("Eccezione: %s" % err)
        return

    nbid = bot["id"]
    obids = Manager.get_botid_from_prop_id(infos.user.uid)

    if len(obids) == 0:
        infos.reply("Non hai un bot!")
        return

    if len(obids) == 1:
        if obids[0] != nbid:
            infos.reply("Devi darmi la chiave dello stesso tuo bot!")
            return

    elif nbid not in obids:
        infos.reply("Non riconsco questo bot.\nPuoi cambiare token, non bot...")
        return

    bots = json.loads(open("Files/jsons/bots.json").read())
    bots.pop(Manager.get_token_from_bot_id(nbid))
    bots[token] = {"bot_id": nbid, "user_id": infos.user.uid}

    with open("Files/jsons/bots.json", "w") as fl:
        fl.write(json.dumps(bots))

    infos.reply("Token sostituita!")

    Core.attach_bot(token)

    infos.reply("Ora il bot dovrebbe essere on!")
