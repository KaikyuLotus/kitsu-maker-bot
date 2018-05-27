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

from Foos import BotsFoos, Commands
from Foos import Foos
from Core import Dialoger
from Utils.Utils import *
from Utils import Logger as Log


master_commands = {
                   "send_message": Foos.send_message,
                   "reset_classifica": Foos.reset_classifica,
                   "detach_bot": Foos.detach_bot,
                   "attach_bot": Foos.attach_bot,
                   "classifica": Foos.classificav2,
                   "status": Foos.stats,
                   "check_unactive": Foos.get_empty_bot,
                   "mcast": Foos.mcast,
                   "proprietario": BotsFoos.proprietary,
                   "reboot": Foos.spegni,
                   "auth": Foos.add_auth,
                   "notice": Foos.notice
                   }

kitsu_commands = {
                   "start": Foos.start,
                   "restart": Foos.restart,
                   "newbot": Foos.newbot,
                   "botlist": Foos.bot_list,
                   "change_token": Commands.change_token,
                   "help": Foos.help
                  }

bot_master_comm = {
                   "quit": BotsFoos.leave_chat,
                   "botid": BotsFoos.get_bid,
                   "generate": BotsFoos.generate,
                   "admin_list": BotsFoos.admin_list,
                   "elimina_bot": BotsFoos.elimina_bot,
                   "backup": Commands.backup,
                   "restore": Commands.restore,
                   "spegni": BotsFoos.spegni,
                   "get_gen_answ": BotsFoos.get_gen_answ,
                   "autorizza": Commands.autorizza,
                   "unjoin": BotsFoos.unjoin
                   }

bot_commands = {
                   "default_list": BotsFoos.default_list,
                   "stats": BotsFoos.botstats,
                   "trigger_list": BotsFoos.triggers,
                   "list_risposte": Commands.list_risps,
                   "get_risposte": Commands.list_risps_form,
                   "del_default": Commands.del_default,
                   "del_risposta": Commands.del_risp,
                   "add_sezione": Commands.add_interazione,
                   "list_sezioni": Commands.list_sezioni,
                   "sezioni_list": Commands.list_sezioni,
                   "del_trigger_vuoti": Commands.del_trigger_vuoti,
                   "triggers_stats": BotsFoos.triggers_stats,
                   "less_used_triggers": BotsFoos.triggers_stats_inv,
                   "riavvia": BotsFoos.riavvia,
                   "set_nascita": Commands.set_nascita,
                   "set_simbolo": Commands.set_symbol,
                   "set_antispam": Commands.set_antispam_time,
                   "broadcast_users": BotsFoos.broadcast_users,
                   "broadcast": BotsFoos.broadcast,
                   "new_trigger": BotsFoos.new_trigger,
                   "del_trigger": BotsFoos.del_trigger,
                   "add_risposta": BotsFoos.add_risposta,
                   "add_risposte": BotsFoos.add_risposta,
                   "del_risposte": BotsFoos.del_risps,
                   "list_default": BotsFoos.list_default
                   }

general_commands = {"join": BotsFoos.join}


def cicler(inter, kl, interact=False):
    try:
        if "&" in inter:
            full = True
            for part in inter.split("&"):
                if not re.search(boundary(regexa(escape(part))), kl):
                    full = False
            if full:
                return inter

        elif "|" in inter:
            for part in inter.split("|"):
                if re.search(boundary(regexa(escape(part))), kl):
                    return inter
        else:
            if re.search(boundary(regexa(escape(inter))), kl):
                if not interact:
                    if not re.search("^" + boundary(regexa(escape(inter))) + r"$", kl):
                        return inter
                else:
                    return inter
        return None
    except Exception as err:
        Log.e("Errore: %s inter: %s" % (err, inter))
        return None


def controlla(infos):
    try:
        frase = infos.text.lower()
        sezioni = ["insulti", "ringraziamenti", "scuse", "complimenti", "saluti", "amare", "bene"]
        cont = LowLevel.jfile("t", infos.bid, infos.user.lang_n)

        for sezione in sezioni:
            tmp = cont[sezione]
            tmp = tmp.split(" ")

            for trigger in tmp:
                if re.search(boundary(regexa(escape(trigger.replace("_", " ")))), frase):
                    return sezione

        return None
    except Exception as err:
        Log.e(err)
        return None


def risposta(infos):
    try:
        cont = LowLevel.jfile("t", infos.bid, infos.user.lang_n)
        eteractions = cont["eteractions"]
        kl = infos.text.lower()
        if re.search(infos.regex + "$", kl) or re.search("^" + infos.regex, kl):
            for inter in eteractions:
                x = cicler(inter, kl)
                if x:
                    return x

        return None
    except Exception as err:
        Log.e(err)


def interaction(infos):
    try:
        cont = LowLevel.jfile("t", infos.bid, infos.user.lang_n)
        moment = LowLevel.get_moment().lower()
        day_parts = cont["day_parts"]
        interactions = cont["interactions"]

        kl = infos.text.lower()

        if infos.user.is_owner:
            for inter in cont["admin_actions"]:
                x = cicler(inter, kl, interact=True)
                if x:
                    return x

        x = controlla(infos)
        if x:
            return x

        for inter in interactions:
            x = cicler(inter, kl, interact=True)
            if x:
                return x

        for day_part in day_parts:
            if "|" in day_part:
                day_part = day_part.split("|")
                for segment in day_part:
                    if segment in kl:
                        return day_part[0] + " " + moment
            else:
                if day_part in kl:
                    return day_part + " " + moment

        return None
    except Exception as err:
        Log.e(err)


def checking(infos):
    try:

        kl = infos.text.lower()
        cont = LowLevel.jfile("t", infos.bid, infos.user.lang_n)

        # controllo equals
        for trigger in cont["equals"]:
            if "|" in trigger:
                for part in trigger.split("|"):
                    if re.search("^%s$" % regexa(escape(part)), kl):
                        return trigger

            elif re.search("^%s$" % regexa(escape(trigger)), kl):
                return trigger

        # controllo contenuti
        for content in cont["contents"]:
            x = cicler(content, kl)
            if x:
                return x

        return False
    except Exception as err:
        Log.e(err)


def reader(i):
    try:

        kl = i.text.lower()
        inter = False

        if i.chat_private:
            if i.user.message.what != "text":
                return BotsFoos.extractor(i)

            wait_list = json.loads(open("Files/jsons/wait_for.json").read())
            if str(i.user.uid) in wait_list:
                try:
                    if i.text.lower() == "annulla":
                        del wait_list[str(i.user.uid)]
                        with open("Files/jsons/wait_for.json", "w") as fl:
                            fl.write(json.dumps(wait_list))
                        Dialoger.send(i, None, special_text="Annullato!")
                        return

                    x = wait_list[str(i.user.uid)]
                    obj = x["thing"]
                    cosa = "???"
                    prefix = None
                    if obj == "photo":
                        cosa = "la foto"
                        prefix = "+pht+"

                    if obj == "sticker":
                        cosa = "lo sticker"
                        prefix = "+stk+"

                    if obj == "document":
                        cosa = "il documento"
                        prefix = "+doc+"

                    if obj == "voice":
                        cosa = "la registrazione"
                        prefix = "+voi+"

                    if obj == "audio":
                        cosa = "l'audio"
                        prefix = "+aud+"

                    if obj == "video":
                        cosa = "il video"
                        prefix = "+vid+"

                    if not prefix:
                        return
                    obj_id = x["id"]
                    trigger = i.text.lower()
                    Dialoger.send(i, None, special_text="Aggiungo %s alla sezione %s" % (cosa, trigger))

                    reply = "%s()%s" % (prefix, obj_id)

                    if x["text"]:
                        reply += "()%s" % x["text"]

                    if LowLevel.add_risposta(i.bid, reply, trigger, i.user.lang_n):
                        risp = "Aggiunto!"
                        del wait_list[str(i.user.uid)]
                        with open("Files/jsons/wait_for.json", "w") as fl:
                            fl.write(json.dumps(wait_list))
                    else:
                        risp = "C'è qualche problema..."
                    Dialoger.send(i, None, special_text=risp)
                    return
                except Exception as err:
                    Log.e(err)
            else:
                pass

        DBs.add_group(i)
        DBs.add_user(i)

        if re.search("^" + i.regex + "\W*$", kl):
            return Dialoger.send(i, "chiamata")

        if (re.search(i.regex + "$", kl) or re.search("^" + i.regex, kl)) or i.chat_private:
            sezione = interaction(i)
            inter = True
            if sezione:
                return Dialoger.send(i, sezione)

        if i.is_reply:
            if i.to_user.uid != i.bid:
                sezione = risposta(i)
                if sezione:
                    return Dialoger.send(i, sezione)
            else:
                sezione = interaction(i)
                inter = True
                if sezione:
                    return Dialoger.send(i, sezione)

        sezione = checking(i)

        if sezione:
            return Dialoger.send(i, sezione)

        if inter:
            Dialoger.send(i, "gen_answ")
            t = "a"
            if not os.path.isfile("Files/bot_files/%s/gen_answ.txt" % i.bid):
                t = "w"
            with open("Files/bot_files/%s/gen_answ.txt" % i.bid, t) as fl:
                fl.write("@%s: %s \n\n" % (i.user.username, i.text))

        if random.randint(0, 750) == 500:
            return Dialoger.send(i, ("autom_" + timemoment()[0]).lower())
    except Exception as err:
        Log.e(err)


def command_reader(infos):
    try:
        command = infos.user.message.command

        if infos.is_kitsu:
            for com in kitsu_commands:
                if command == com:
                    return kitsu_commands[com](infos)

            if infos.user.is_master:
                    for com in master_commands:
                        if command == com:
                            return master_commands[com](infos)

        if command == "start":
            return BotsFoos.startb(infos)

        if infos.user.is_owner:
            for com in bot_master_comm:
                if command == com:
                    return bot_master_comm[com](infos)

        infos.admins.append(kaID)

        if infos.user.uid in infos.admins:
            for com in bot_commands:
                if command == com:
                    return bot_commands[com](infos)

        for com in general_commands:
            if command == com:
                return general_commands[com](infos)

        return "procedi"
    except Exception as err:
        Log.e("Ho trovato un errore: riga %s %s %s (%s)" % (sys.exc_info()[-1].tb_lineno, type(err).__name__, err, infos.text))
        infos.reply("C-c'è stato un errore...\nInoltra a @Kaikyu il tuo ultimo messaggio!")


def pers_commands(infos):
    command = infos.user.message.command
    cont = LowLevel.jfile("t", infos.bid, infos.user.lang_n)

    # controllo commands
    if "bot_commands" not in cont:
        Log.w("BOT ID %s non ha bot_commands!" % infos.entity)
        return

    for trigger in cont["bot_commands"]:
        if "|" in trigger:
            for part in trigger.split("|"):
                if re.search("^%s$" % escape(part), command):
                    return Dialoger.send(infos, trigger, antispam=False)
        else:
            if re.search("^%s$" % escape(trigger), command):
                if Unreloaded.antispam(infos): return
                return Dialoger.send(infos, trigger, antispam=False)

    if infos.chat_private:
        return Dialoger.send(infos, "comando sconosciuto", antispam=False)
