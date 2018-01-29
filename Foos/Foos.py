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

import os
import pprint
import re
import sys
import time
import schedule

from Cache import BotCache
from LowLevel import DBs, LowLevel
from Utils import Logger as Log, Utils
from Core import HTTPLL, Core, Manager, Dialoger

ver = "0.8"
kaID = 52962566
groupID = -1001141699210
chan_id = -1001141066491
max_bots = 1000
kitsu_token = "447458418:AAEVPQHV16VogYINta2M58a0oSF8AW2gRWI"


limits = {
          52962566: 10,  # Kaikyu
          134585585: 3,  # Veiler
          156343027: 2,  # Kurama
          197896791: 2   # Yuki
          }


def escape_markdown(text): return re.sub(r'([%s])' % '\*_`\[', r'\\\1', text)


def restart(infos):
    if not infos.user.is_master:
        return
    infos.reply("Restarting...")
    os.execv(sys.executable, ['python35'] + sys.argv)


def scheduler():
    Log.i("Schedule impostati!")
    while True:
        schedule.run_pending()
        time.sleep(5)


def start(infos):
    global max_bots
    if DBs.add_user(infos):
        txt = "Avviato da %s per la prima volta!" % infos.user.username
        Dialoger.send(infos, "", special_text=txt, to_id=kaID)
    else:
        Log.d("Questo utente era già registrato")

    text = "Benvenuto *%s*, kitsu! ~\n\n" % infos.user.name
    text += "Io sono *Kitsu*, la tua assistente per *Bot Forge*! ~\n\nTi starai sicuramente chiedendo di cosa sto parlando...\n "
    text += "*Bot Forge* è il progetto creato da [Kaikyu](t.me/Kaikyu) che permette la creazione di chatbot su"
    text += "Telegram *stabili, veloci* e *sempre online!*\n\nSe non ci credi dai un'occhiata su @KitsuRankings, kitsu! ;3\n\n "
    text += "Al momento ci sono solo *%s* bot online su un massimo di ben *%s*!\n" % (Manager.get_bot_count(), max_bots)
    text += "...*%s*?? ...  ...  ...\nAh si!\nIl mio creatore, [Kaikyu](t.me/Kaikyu), ha modificato il mio *Core* ricostruendolo *dalle fondamenta*, ora sono più *ottimizzata* che mai, ogni *KitsuBot* utilizza solo *0,39MB* di *RAM*!" % max_bots
    text += "\n\nAh, prima che me ne dimentichi, [questa](telegra.ph/Come-creare-un-KitsuBot-08-20) è una guida sul mio funzionamento, *potrebbe interessarti*!\n\n "
    if Manager.get_bot_count() >= max_bots:
        text += "Al momento non è possibile creare nuovi bot...\n" \
                "Però puoi controllare che bot funzionano grazie a me al momento!\n" \
                "Usa /botlist per avere la lista ~\n\n"

    text += "Segui il canale @KitsuneCode per *aggiornamenti* ~"

    infos.reply(text, markdown=True, disable_web_page_preview=True)


def newbot(infos):
    user = infos.user.username
    uid = infos.user.uid
    say = infos.reply

    if uid in limits:
        limit = limits[uid]
    else:
        limit = 1

    if infos.text == "token":
        say("B-baka, non devi scrivere \"token\", devi darmi la **token** del tuo **bot**!", markdown=True)
        HTTPLL.sendMessage(infos.token, kaID, "@%s ha usato /newbot \"token\" lol" % infos.user.username)
        return

    if Manager.get_bot_count() >= max_bots and "!!" not in infos.text:
        say("Tutti i posti sono stati occupati!\nSegui @KitsuneCode per sapere quando ce ne saranno altri ~")
        return

    msg = "Nuovo bot da %s (ID: %s)" % (user, uid)

    if infos.text == "":
        say("La sintassi del comando è semplice:\n/newbot token\nRiprova!")
        return Log.a("[Bot: @%s | %s] user: %s ID: %s 'newbot senza chiave'" % (infos.username, infos.bid, user, uid))

    key = infos.text.replace("!!", "")
    if Manager.is_token_used(key):
        Log.a("[Bot: @%s | %s] user: %s ID: %s 'newbot chiave usata'" % (infos.username, infos.bid, user, uid))
        return say("Kitsu!\nQuesta chiave è già usata!\nSe credi che ci sia un errore, contatta @Kaikyu!")

    if Manager.count_bots(uid) >= limit:
        Log.a("[Bot: @%s | %s] user: %s ID: %s 'newbot utente ha già un bot'" % (infos.username, infos.bid, user, uid))
        return say("A quanto pare non puoi fare altri bot ne hai già %s su %s..." % (Manager.count_bots(uid), limit))

    if ":" not in key or len(key) != 45:
        say("%s non credo che questa sia una chiave valida." % user)
        return Log.a("[Bot: @%s | %s] user: %s ID: %s 'newbot chiave errata'" % (infos.username, infos.bid, user, uid))

    try:
        tbot = HTTPLL.getMe(key)
        txt = "Eccomi master.\nEcco una [guida](%s) su come funziono.\nUnisciti al [gruppo ufficiale](%s) per avere " \
              "le novità in tempo reale." % ("telegra.ph/Come-creare-un-KitsuBot-08-20", "t.me/KitsuBotsGroup")
        HTTPLL.sendMessage(key, uid, text=txt, parse_mode="markdown")
        msg += "\nHa usato la token %s\n" % key
    except Exception as err:
        Log.d("L'utente non ha avviato il proprio bot, o c'è qualche problema (%s)" % err)
        return say("Sicuro di aver avviato il tuo bot in privato?")

    if Manager.add_bot(uid, tbot["id"], tbot["token"]):
        say("Registrato con successo!\nTutti i prossimi comandi dovrai eseguirli dal tuo bot: @%s\n"
            "Il tuo bot è il %sesimo su %s!" % (tbot["username"], Manager.get_bot_count(), max_bots))
    else:
        Log.d("Qualcosa è andato storto...")
        return say("Qualcosa è andato storto!")

    msg += "Nome %s\nUsername @%s\nID: %s" % (tbot["first_name"], tbot["username"], tbot["id"])

    HTTPLL.sendMessage(infos.token, kaID, msg)
    Core.attach_bot(key)


def stats(infos):
    t = time.time()
    if infos.user.uid != kaID:
        return
    text = "In questo momento sto mantenendo online %s bot.\n" % Core.count_bots()
    text += "Il tempo di elaborazione di questo messaggio è di %s ms, " % LowLevel.get_time(t)
    text += "quindi il carico di lavoro è leggero.\n\nFoos version: %s" % ver

    Dialoger.send(infos, None, special_text=text)


def report(infos):
    try:
        if not infos.user.is_master: return
        if infos.text == "": return

        Dialoger.send(infos, None, to_id=infos.prop_id, special_text="Questo bot è stato reportato da Kaikyu per:\n%s" % infos.text)
        Dialoger.send(infos, None, to_id=kaID, special_text="Report inviato, master.", special_token=kitsu_token)
    except Exception as err:
        print(err)


def status(bot, update):
    try:
        g_name = update["message"]["chat"]["title"]
        by = update["message"]["from"]["username"]
        byid = update["message"]["from"]["id"]
        gid = update["message"]["chat"]["id"]

        if update["message"]["new_chat_members"]:
            join_user_name = update["message"]["new_chat_members"][0]['first_name']
            if "username" in update["message"]["new_chat_members"][0]:
                join_user_username = update["message"]["new_chat_members"][0]['username']
            else:
                join_user_username = join_user_name
            join_user_id = update["message"]["new_chat_members"][0]['id']

            if join_user_id == bot["id"]:
                text = "Aggiunta a: %s\nUtente: @%s" % (g_name, by)
                bpht = None  # ToDo Get Propic Method
                if bpht:
                    HTTPLL.sendPhoto(kitsu_token, kaID, bpht, caption=text)
                else:
                    HTTPLL.sendMessage(kitsu_token, kaID, text)

            elif gid == groupID:
                if Manager.has_a_bot(join_user_id):
                    HTTPLL.sendMessage(kitsu_token, gid, "%s ha un mio bot, benvenuto! ~" % join_user_name)
                else:
                    if join_user_username.lower().endswith("bot"):
                        if Manager.is_kitsu_bot(join_user_id):
                            return HTTPLL.sendMessage(kitsu_token, gid, "%s è mio bot, kitsu! ~" % join_user_name)
                        HTTPLL.sendMessage(kitsu_token, gid, "%s non è un mio bot, kitsu." % join_user_name)
                    else:
                        HTTPLL.sendMessage(kitsu_token, gid, "%s non ha un mio bot, kitsu." % join_user_name)
                    HTTPLL.kickChatMember(kitsu_token, gid, join_user_id)

        elif update["message"]["left_chat_member"]:
            left_user_name = update["message"]["left_chat_member"]['first_name']
            left_user_id = update["message"]["left_chat_member"]['id']

            if left_user_id == bot["id"]:
                HTTPLL.sendMessage(kitsu_token, kaID, text="Rimossa da: %s\nUtente @%s" % (g_name, by))
                Log.a("[%s] Rimossa da un gruppo da %s" % (bot["first_name"], by))

    except Exception as err:
        Log.e(err)
        pprint.pprint(update)


def classificav2(infos): infos.reply(Utils.class_text(), markdown=True)


def get_empty_bot(infos):
    try:
        infos.reply("Ok, master.")
        d = 0
        w = 0
        wb = 0
        u_bots = "Zero-Trigger bots:"
        bids = Manager.get_bots_id()
        for bid in bids:
            tot = Manager.trigger_count(bid)
            toke = Manager.get_token_from_bot_id(bid)
            if tot < 5:
                if toke not in BotCache.bots:
                    BotCache.bots[toke] = HTTPLL.getMe(toke)

                bot = BotCache.bots[toke]
                u_bots += "\n%s - %s" % (bid, bot["username"])
                Manager.delete_bot(bid)
                d += 1
            elif tot < 20:
                try:
                    HTTPLL.sendMessage(toke, Manager.get_prop_id(toke), "Master, t-ti sei dimenticato di me...?")
                except Exception as err:
                    wb += 1
                    Manager.delete_bot(bid)
                w += 1
        u_bots += "\n\n%s unactive bots detached.\n%s warns sent to the bot masters but %s of them had blocked their bot." % (d, w, wb)
        infos.reply(u_bots)
    except Exception as err:
        Log.e("Ho trovato un errore: riga %s %s %s (%s)" % (sys.exc_info()[-1].tb_lineno, type(err).__name__, err, infos.text))
        infos.reply("M-master... Controlla il log... k-kitsu! ><")


def bot_list(infos):
    tokens = Manager.get_token_list()
    ls = "Ecco la lista dei miei bot!\n\n"

    for token in tokens:
        try:
            bot = BotCache.bots[token]
            ls += "• *%s*\n - @%s\n\n" % (bot["first_name"], bot["username"].replace("_", "\_"))
        except: pass
    infos.reply(ls, markdown=True)


def mcast(infos):
    unsend = 0
    send = 0
    bids = Manager.get_bots_id()
    tot = len(bids)
    msg = infos.text
    for bid in bids:
        btoken = Manager.get_token_from_bot_id(bid)
        pid = Manager.get_prop_id(btoken)
        try:
            HTTPLL.sendMessage(btoken, pid, msg)
            send += 1
        except Exception:
            Manager.delete_bot(bid)
            unsend += 1

    infos.reply("Inviato a %s su %s (%s avevano bloccato il proprio bot e sono stati eliminati)" % (send, tot, unsend))


def attach_bot(infos):
    bid = infos.user.message.text
    res = Core.attach_bot(None, bid=bid)
    msg = "Qualcosa non va..."
    if res:
        msg = "Bot avviato con successo, kitsu."
    infos.reply(msg)


def detach_bot(infos):
    bid = infos.user.message.text
    res = Core.detach_bot(None, bid=bid)
    msg = "Qualcosa non va..."
    if res:
        msg = "Bot stoppato con successo, kitsu."
    infos.reply(msg)


def reset_classifica(infos):
    bids = Manager.get_bots_id()

    for bid in bids:
        with open("Files/bot_files/%s/trig_usage.json" % bid, "w") as fl:
            fl.write("{}")
    infos.reply("Fatto!")
    return


def spegni(infos):
    HTTPLL.sendMessage(infos.token, infos.cid, "Rebooting...")
    name = "MainKitsu.py"
    kill = "pkill -f %s" % name
    os.system("echo Kaikyudev1! | sudo -S %s" % kill)
