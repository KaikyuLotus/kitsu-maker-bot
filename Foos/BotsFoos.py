# coding=utf-8

# Copyright (c) 2017 Kaikyu

import json
import operator
import random
import re
import threading
from collections import OrderedDict

import time

import os

from Foos import Commands
from Utils import Utils, Logger as Log
from Core import HTTPLL, Unreloaded, Dialoger, Manager
from Core import ThreadedCore as Core
from Core.Infos import Infos
from Core.Dialoger import send
from Cache import BotCache
from LowLevel import LowLevel, DBs
from Core.Settings import *

chars = "abcdefghijklmnopqrstuwxyz"


def generate(infos):
    if not infos.user.is_owner:
        return
    if not infos.chat_private:
        return infos.reply("Questo comando DEVE essere eseguito in chat privata!")

    paswd = ""
    for i in range(14):
        base = random.randint(1, 3)
        if base == 3:
            paswd += chars[random.randint(0, len(chars) - 1)]
        elif base == 2:
            paswd += chars[random.randint(0, len(chars) - 1)].upper()
        else:
            paswd += str(random.randint(0, 9))
    BotCache.join_keys[infos.token] = paswd
    infos.reply("Password generata: `%s`" % paswd, markdown=True)


def join(infos):
    if infos.user.is_owner:
        return infos.reply("Ma master, non puoi joinare, sei già il mio master....")

    if infos.text == "":
        return infos.reply("Devi inviare il codice di 15 caratteri insieme al comando!")

    if infos.token not in BotCache.join_keys:
        return infos.reply("Il mio master non ha generato alcun codice...")

    code_exp = BotCache.join_keys[infos.token]
    if code_exp != infos.text:
        return infos.reply("Nah, non è questo il codice ;3")

    # Il codice è giusto!
    del BotCache.join_keys[infos.token]  # Elimino la token per evitare furbetti

    admins = DBs.read_obj(infos.bid, infos.bid, "users")
    if not admins["name"]:
        DBs.configure_bot_row(infos)

    admins = DBs.read_obj(infos.bid, infos.bid, "users")["ext3"]
    if not admins:
        DBs.set_obj(infos.bid, "1", "ext", infos.entity)
        DBs.set_obj(infos.bid, str(infos.user.uid), "ext3", infos.bid, where="users")
    else:
        DBs.set_obj(infos.bid, admins + " " + str(infos.user.uid), "ext3", infos.bid, where="users")
    return infos.reply("Codice accettato, nuovo master!")


def admin_list(infos):
    infos.admins.remove(infos.prop_id)
    if not infos.admins:
        return infos.reply("Non hai autorizzato nessuno!")

    msg = "I miei admin sono:\n"
    n = 1
    for admin in infos.admins:
        try:
            name = HTTPLL.getChat(infos.token, admin)["result"]["first_name"]
        except:
            name = "???"
        msg += "%s) %s - %s\n" % (n, admin, name)
        n += 1

    infos.reply(msg)


def unjoin(infos):
    infos.admins.remove(infos.prop_id)
    if not infos.admins:
        return infos.reply("Ma non hai autorizzato nessuno!")

    if infos.text == "":
        return infos.reply("Devi specificare il numero dell'admin da rimuovere!\nGuarda /admin_list")

    if not infos.text.isdecimal():
        return infos.reply("Devi dirmi un numero!")

    num = int(infos.text)
    if num < 1:
        return infos.reply("Mi prendi in giro...?")

    if len(infos.admins) > num:
        return infos.reply("Ma ci sono %s admin..." % len(infos.admins))

    admin = infos.admins[num - 1]
    try:
        name = HTTPLL.getChat(infos.token, admin)["result"]["first_name"]
    except:
        name = "???"

    reply = "Rimuovo %s - %s dagli admin..." % (admin, name)
    admins = DBs.read_obj(infos.bid, infos.bid, "users")["ext3"]
    admins = admins.replace(str(admin), "")
    DBs.set_obj(infos.bid, admins, "ext3", infos.bid, where="users")
    infos.reply(reply)


def startb(infos):
    if DBs.add_user(infos):
        txt = "Avviato da %s per la prima volta!" % infos.user.username

        Dialoger.send(infos, None, special_text=txt, to_id=infos.prop_id)

    text = "\n\n_______________________"
    text += "\n<b>Bot creato con</b> <link>t.me/ChatbotMakerBot:>Syntaxer</link>!"
    text += "\n<link>t.me/Kaikyu:>Kaikyu Lotus Channel</link>"

    Dialoger.send(infos, "start", add=text)


def spegni(infos):
    if not Manager.has_a_bot(infos.user.uid):
        return

    if not Core.is_online(infos.token):
        return

    if not infos.user.is_owner:
        return

    if not infos.text:
        Dialoger.send(infos, None, special_text="Se mi spegni non potrai più avviarmi fino al riavvio di"
                                                " Kitsu!\nScrivi /spegni ok se ne sei sicuro")
        return

    if infos.text.lower() != "ok":
        return Dialoger.send(infos, None, special_text="Scrivi /spegni ok se ne sei sicuro!")

    try:
        Dialoger.send(infos, None, special_text="Spegnimento...")
        Core.detach_bot(infos.token)

    except Exception as err:
        Dialoger.send(infos, None, special_text="Si è verificato un errore...\n(%s)" % err)


def riavvia(infos):
    if not Manager.has_a_bot(infos.user.uid):
        return
    if not Core.is_online(infos.token):
        return
    if not infos.user.is_owner and infos.user.uid not in infos.admins:
        return
    Core.detach_bot(infos.token)
    time.sleep(0.5)
    Core.attach_bot(infos.token)
    infos.reply("Riavviato.")


def get_gen_answ(infos):
    if not os.path.isfile("Files/bot_files/%s/gen_answ.txt" % infos.bid):
        return infos.reply("File ancora non creato, master.")

    HTTPLL.sendFileDocument(infos.token, infos.cid, "Files/bot_files/%s/gen_answ.txt" % infos.bid,
                            caption="Ecco master.")
    with open("Files/bot_files/%s/gen_answ.txt" % infos.bid, "w") as fl:
        fl.write((">> Log iniziato il %s\n\n" % time.strftime("%A - %H:%M:%S")))
    return


def proprietary(infos):
    prop_id = Manager.get_prop_id(infos.token)
    user = HTTPLL.getChat(infos.token, prop_id)["result"]
    msg = "Il mio padrone è [%s](tg://user?id=%s)" % (escape_markdown(user["first_name"]), prop_id)
    infos.reply(msg, markdown=True)


def elimina_bot(infos):
    try:
        if not infos.user.is_owner:
            return
        if not Core.is_online(infos.token):
            Dialoger.send(infos, None, special_text="M-ma io non sono online...")

        uid = str(infos.user.uid)
        bid = infos.bid

        if not infos.text:
            code = str(random.randint(1000, 9999))
            Dialoger.send(infos, None,
                          special_text="Se mi elimini perderai tutti i dati!\n"
                                       "Scrivi \"/elimina_bot %s\" se ne sei sicuro..." % code)
            Unreloaded.set_delete_code(uid, code)
            return

        if Unreloaded.get_delete_code(uid) == "":
            code = str(random.randint(1000, 9999))
            Dialoger.send(infos, None, special_text="Non avevo ancora generato il codice, eccolo: %s." % code)
            Unreloaded.set_delete_code(uid, code)
            return

        if infos.text != Unreloaded.get_delete_code(uid):
            Dialoger.send(infos, None, special_text="Codice sbagliato, era: %s" % Unreloaded.get_delete_code(uid))
            return

        Dialoger.send(infos, None, special_text="Procedo...")
        Log.d("Elimino il bot %s di %s" % (bid, uid))
        Core.detach_bot(infos.token)
        Manager.delete_bot(bid)

        Dialoger.send(infos, None, special_text="Addio...")
    except Exception as err:
        Log.e(err)


def leave_chat(infos): HTTPLL.leaveChat(infos.token, infos.cid)


def get_bid(infos): infos.reply("Il mio ID: %s" % infos.bid)


def triggers(infos):
    try:
        # bid = BotListManager.get_botid_from_prop_id(infos.user.uid)
        dic = LowLevel.get_triggers(infos.bid, "triggers.json" if infos.user.lang_n == 0 else "triggers_eng.json")

        if not dic:
            return Dialoger.send(infos, None, special_text="A quanto pare non hai un bot, kitsu...")

        msg = "Lista dei miei trigger:"
        msg += "\nContenuti    [1]\n"

        tot = len(dic["contents"]) + len(dic["interactions"]) \
            + len(dic["equals"]) + len(dic["admin_actions"]) \
            + len(dic["eteractions"]) + len(dic["bot_commands"])

        if len(dic["contents"]) != 0:
            for trig in dic["contents"]:
                msg += trig + "\n"
        else:
            msg += "Vuoto\n"

        msg += "\nInterazioni  [2]\n"
        if len(dic["interactions"]) != 0:
            for trig in dic["interactions"]:
                msg += trig + "\n"
        else:
            msg += "Vuoto\n"

        msg += "\nEguali           [3]\n"
        if len(dic["equals"]) != 0:
            for trig in dic["equals"]:
                msg += trig + "\n"
        else:
            msg += "Vuoto\n"

        msg += "\nEterazioni   [4]\n"
        if len(dic["eteractions"]) != 0:
            for trig in dic["eteractions"]:
                msg += trig + "\n"
        else:
            msg += "Vuoto\n"

        msg += "\nInterazioni (master) [5]\n"
        if len(dic["admin_actions"]) != 0:
            for trig in dic["admin_actions"]:
                msg += trig + "\n"
        else:
            msg += "Vuoto\n"

        msg += "\nComandi (%s) [6]\n" % Utils.get_com_symbol(infos.entity)
        if len(dic["bot_commands"]) != 0:
            for trig in dic["bot_commands"]:
                msg += trig + "\n"
        else:
            msg += "Vuoto\n"

        if not infos.chat_private:
            to_id = infos.user.message.id
        else:
            to_id = None
        msg += "\n\nTotale di %s triggers!" % tot
        HTTPLL.sendMessage(infos.token, infos.cid, text=msg, reply_to_message_id=to_id)
    except Exception as err:
        infos.reply("K-kitsu errore!\nErr. n°21: @Kaikyu non sa programmare.\n\n(%s)" % err)
        Log.e(err)


def unkown_command(infos):
    if not infos.chat_private:
        return

    Dialoger.send(infos, None, special_text="Comando sconosciuto, kitsu!")
    Log.a("Comando sconosciuto")


def botstats(infos):
    try:

        text = "Ecco le <b>statistiche</b>:\n\n"

        text += "<b>Gruppi</b>:   <c>%s</c>\n" % DBs.get_groups_number(infos.bid)
        text += "<b>Private</b>:  <c>%s</c>\n\n" % DBs.get_groups_number(infos.bid, user=True)

        Dialoger.send(infos, None, special_text=text)
    except Exception as err:
        Log.e(err)


def status(bot, update):
    try:
        g_name = update["message"]["chat"]["title"]
        gid = update["message"]["chat"]["id"]
        if "username" in update["message"]["from"]:
            by = update["message"]["from"]["username"]
        else:
            by = "[no username]"
        byid = update["message"]["from"]["id"]
        # gid = update["message"]["chat"]["id"]
        propid = Manager.get_prop_id(bot["token"])

        if update["message"]["new_chat_members"]:
            join_user_name = update["message"]["new_chat_members"][0]['first_name']
            # join_user_username = update["message"]["new_chat_members"][0]['username']
            join_user_id = update["message"]["new_chat_members"][0]['id']

            if join_user_id == bot["id"]:
                text = "Aggiunta a: %s\nUtente: @%s" % (g_name, by)

                bpht = HTTPLL.getChatPhoto(bot["token"], gid)
                if bpht:
                    HTTPLL.sendPhoto(bot["token"], propid, bpht, caption=text)
                else:
                    HTTPLL.sendMessage(bot["token"], propid, text)

                Log.a("[Bot: %s | @%s] Aggiunto a %s da %s" % (bot["username"], bot["id"], g_name, byid))
                Dialoger.send(Infos(bot, update), "newgroup", special_token=bot["token"])
            else:
                state = DBs.read_obj(gid, bot["id"], "groups")["ext"]
                if not state or state == "0":
                    Dialoger.send(Infos(bot, update), "welcome", special_name=join_user_name,
                                  special_token=bot["token"])

        elif update["message"]["left_chat_member"]:
            left_user_id = update["message"]["left_chat_member"]['id']

            if left_user_id == bot["id"]:
                Log.i("bot quitt")
                Unreloaded.gbots[str(update["message"]["chat"]["id"])].remove(bot["id"])
                HTTPLL.sendMessage(bot["token"], propid, "Rimossa da: %s\nUtente @%s" % (g_name, by))
                Log.a("[%s] Rimosso da un gruppo da %s" % (bot["first_name"], by))

    except Exception as err:
        Log.e(err)


def bcast(infos, who):
    if not infos.user.is_owner:
        return
    dialogs = LowLevel.jfile("d", infos.bid, infos.user.lang_n)
    if "broadcast" not in dialogs:
        infos.reply("Crea la sezione con \"/add_sezione broadcast\" prima...")
        return

    if not dialogs["broadcast"]:
        infos.reply("Aggiungi le risposte alla sezione \"broadcast\" con \"/add_risposte broadcast | Risposta\" prima!")
        return

    Log.d("Broadcast utenti avviato da %s ID %s" % (infos.user.username, infos.user.uid))
    try:
        itms = DBs.get_data(infos.entity, who)
        n_itms = len(itms)
        msg_id = infos.reply("Invio 0/%s..." % n_itms)["message_id"]

        uns = 0
        s = 0

        for itm in itms:
            res = Dialoger.send(infos, "broadcast", special_user_name=itm[2], to_id=itm[0], antispam=False, no_log=True)

            if res == "ERR":
                uns += 1
            else:
                s += 1
                time.sleep(0.05)

            if (s + uns) % 10 == 0:
                HTTPLL.editMessageText(infos.token, chat_id=infos.cid,
                                       message_id=msg_id, text="Invio %s/%s..." % (s + uns, n_itms))

        Dialoger.send(infos, None, special_text="Fatto!\nInviato a %s su %s!" % (s, n_itms))

    except Exception as err:
        Log.w(str(err))
        Dialoger.send(infos, "general_error", antispam=False)


def extractor(infos):
    if not infos.chat_private:
        return

    uid = infos.user.uid
    if infos.user.uid != owner_id:
        if Manager.get_prop_id(infos.token) != uid:
            return

    stkid = infos.user.message.item_id
    thing = infos.user.message.what

    if thing == "document":
        try:
            f_name = HTTPLL.getFileName(infos.token, stkid)
            if f_name.endswith(".kb"):
                content = HTTPLL.getFile(infos.token, None, file_path="documents/" + f_name).read().decode("utf-8")
                success, message = Commands.restore(content, infos.bid, infos.user.lang_n)
                if success:
                    repl = "Restore riuscito!"
                else:
                    repl = "Restore fallito: %s" % message
                return infos.reply(repl)
        except Exception as err:
            Log.e("Errore: %s" % err)
            return

    msg = "Vuoi aggiungere [%s], master? ~\nInviami il trigger a cui aggiungerlo!\n...*aspetta*" % thing
    wait_list = json.loads(open("Files/jsons/wait_for.json").read())
    if str(uid) in wait_list:
        x = wait_list[str(uid)]
        obj = x["thing"]
        obj_id = x["id"]
        msg = "Sto ancora aspettando il trigger per:\n%s con ID: %s~" % (obj, obj_id)
    else:
        wait_list[str(uid)] = {}
        wait_list[str(uid)]["thing"] = thing
        wait_list[str(uid)]["id"] = stkid

        if infos.user.message.text != "":
            wait_list[str(uid)]["text"] = infos.user.message.text
        else:
            wait_list[str(uid)]["text"] = None

        with open("Files/jsons/wait_for.json", "w") as fl:
            fl.write(json.dumps(wait_list))

    Dialoger.send(infos, None, special_text=msg)


def default_list(infos):
    say = infos.reply
    try:
        text = "Le sezioni default al momento sono:\n\n"
        text += "complimenti\nbene\ninsulti\ngiorno\nscuse\nringraziamenti\nnotte\nsaluti\namare\n"
        text += "\nVedendo il contenuto di essi puoi facilmente kitsucapire a cosa servono ~"
        say(text)
        Log.a("[Bot: @%s | %s] user: %s ID: %s 'list_risposte riuscito'" % (infos.username, infos.bid,
                                                                            infos.user.username, infos.user.uid))
    except Exception as err:
        say(Utils.get_phrase("error"))
        Log.e(err)


def escape_markdown(text): return re.sub(r'([%s])' % '\*_`\[', r'\\\1', text)


def triggers_stats(infos):
    try:
        stats = LowLevel.get_stats_file(infos.bid)
        sorted_stats = OrderedDict(sorted(stats.items(), key=operator.itemgetter(1), reverse=True))
        msg = "Ecco la lista dei trigger più utilizzati!\n\n"
        tot = 0
        for trigger in sorted_stats:
            if tot == 25:
                break
            msg += "*%s* -> *%s* utilizzi,\n" % (trigger, sorted_stats[trigger])
            tot += 1

        msg += "\nCon un totale di %s utilizzi!" % sum(stats.values())

        infos.reply(msg, markdown=True)
    except Exception as err:
        Log.e(err)
        infos.reply("Errore: %s" % err)


def triggers_stats_inv(infos):
    try:
        stats = LowLevel.get_stats_file(infos.bid)
        sorted_stats = OrderedDict(sorted(stats.items(), key=operator.itemgetter(1)))
        msg = "Ecco la lista dei trigger meno utilizzati!\n\n"
        tot = 0
        for trigger in sorted_stats:
            if tot == 25:
                break
            msg += "*%s* -> *%s* utilizzi,\n" % (trigger, sorted_stats[trigger])
            tot += 1

        msg += "\nCon un totale di %s utilizzi!" % sum(stats.values())

        infos.reply(msg, markdown=True)
    except Exception as err:
        Log.e(err)
        infos.reply("Errore: %s" % err)


def broadcast(infos): threading.Thread(target=bcast, args=(infos, "groups")).start()


def broadcast_users(infos): threading.Thread(target=bcast, args=(infos, "users")).start()


def new_trigger(infos):
    infos.reply(Commands.add_trigger(infos.token, infos.text, None, infos.user.lang_n)[0])


def del_trigger(infos):
    infos.reply(Commands.del_trigger(infos.token, infos.text, None, infos.user.lang_n)[0])


def add_risposta(infos):
    infos.reply(Commands.add_risposta(infos.token, None, infos.text, infos.user.lang_n)[0])


def del_risps(infos):
    infos.reply(Commands.del_risps(infos.token, infos.text, lang_n=infos.user.lang_n)[0])


def list_default(infos): infos.reply(Commands.list_default(infos.token, infos.text, infos.user.lang_n)[0])


def warn(infos, self=False):
    try:
        try:
            warns = json.loads(open("Files/bot_files/%s/warns.json" % infos.bid).read())
        except Exception:
            warns = {}

        gid = str(infos.cid)

        if not self:
            ut_to_warn = str(infos.to_user.uid)
            if not infos.admin:
                return send(infos, "non_admin", antispam=False, recorsivity=1)
            if infos.is_auto:
                return send(infos, "auto_warn", antispam=False, recorsivity=1)
            if not infos.user.is_admin:
                return send(infos, "ut_non_admin", antispam=False, recorsivity=1)
            if infos.to_user.is_owner:
                return send(infos, "user_is_owner", antispam=False, recorsivity=1)
            if infos.to_user.is_admin:
                return send(infos, "ut_admin", antispam=False, recorsivity=1)
        else:
            ut_to_warn = str(infos.user.uid)
            if infos.user.is_admin:
                return
            if infos.user.is_owner:
                return
            if infos.user.is_admin:
                return

        if gid not in warns:
            warns[gid] = {}

        if ut_to_warn not in warns[gid]:
            warns[gid][ut_to_warn] = 0

        warns[gid][ut_to_warn] += 1
        nwarns = warns[gid][ut_to_warn]

        if not self:
            if nwarns == 1:
                send(infos, "warn1", antispam=False, recorsivity=1)

            if nwarns == 2:
                send(infos, "warn2", antispam=False, recorsivity=1)

            if nwarns == 3:
                warns[gid][ut_to_warn] = 0
                send(infos, "warn3", antispam=False, recorsivity=1)
                HTTPLL.kickChatMember(infos.token, infos.cid, ut_to_warn)
        else:
            if nwarns == 3:
                warns[gid][ut_to_warn] = 0
                HTTPLL.kickChatMember(infos.token, infos.cid, ut_to_warn)

        with open("Files/bot_files/%s/warns.json" % infos.bid, "w") as fl:
            fl.write(json.dumps(warns))

    except Exception as err:
        send(infos, "general_error", antispam=False, recorsivity=1)
        Log.e(err)


def unwarn(infos):
    try:
        try:
            warns = json.loads(open("Files/bot_files/%s/warns.json" % infos.bid).read())
        except Exception:
            warns = {}

        if not infos.admin:
            return send(infos, "non_admin", antispam=False, recorsivity=1)
        if infos.is_auto:
            return send(infos, "auto_unwarn", antispam=False, recorsivity=1)
        if not infos.user.is_admin:
            return send(infos, "ut_non_admin", antispam=False, recorsivity=1)
        if infos.to_user.is_owner:
            return send(infos, "user_is_owner", antispam=False, recorsivity=1)
        if infos.to_user.is_admin:
            return send(infos, "ut_admin", antispam=False, recorsivity=1)

        gid = str(infos.cid)
        ut_to_unwarn = str(infos.to_user.uid)

        if gid not in warns:
            warns[gid] = {}

        if ut_to_unwarn not in warns[gid]: warns[gid][ut_to_unwarn] = 0

        warns[gid][ut_to_unwarn] -= 1
        nwarns = warns[gid][ut_to_unwarn]

        if nwarns == -1:
            return send(infos, "unwarn_-1", antispam=False, recorsivity=1)

        if nwarns == 0:
            send(infos, "unwarn_0", antispam=False, recorsivity=1)

        if nwarns == 1:
            send(infos, "unwarn_1", antispam=False, recorsivity=1)

        with open("Files/bot_files/%s/warns.json" % infos.bid, "w") as fl:
            fl.write(json.dumps(warns))

    except Exception as err:
        send(infos, "general_error", antispam=False, recorsivity=1)
        Log.e(err)


def temp_mute(infos, minutes):
    try:
        time.sleep(minutes * 60)
        HTTPLL.restrictChatMember(infos.token, infos.cid, infos.to_user.uid)
        send(infos, "user_unmuted")
    except Exception as err:
        HTTPLL.sendMessage(infos.token, infos.cid, "Non ho potuto unmutare l'utente con ID %s..." % infos.to_user.uid)
        Log.d("Errore nel unmute: %s" % err)
