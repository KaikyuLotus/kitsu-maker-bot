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

import operator
import re
import time
import random
import sys
import psutil
import json

from datetime import timedelta, date, datetime
from collections import OrderedDict
from Cache import BotCache
from LowLevel import LowLevel, DBs
from Core import HTTPLL, Manager, Unreloaded
from Utils import Logger as Log
from Extras.LastFM import LastFM, UnvalidUsername, UnregistredUser, EmptyTracks
from Foos import Dialogs


bots_cache = {}

kaID = 487353090
kitsu_token = "569510835:AAHskMqSa02KAditTfztt3KuHtE9oFQRYGs"
zwnj = "‌"


def get_keyboard(text):
    kb = None
    pattern = re.compile(r'(<btn>)(.*?)(->)(.*?)(</btn>)')
    res = re.finditer(pattern, text)
    if res:
        kb = []
        for btn in res:
            btn_text = btn.group(2)
            btn_link = btn.group(4)
            kb.append(HTTPLL.keyboard_btn(btn_text, btn_link))
            text = text.replace(btn.group(0), "")

        kb = HTTPLL.inline_keyboard(kb)

    return text, kb


def link_elab(text, infos):
    links = 0
    while "<link>" in text:
        if links > 10:
            HTTPLL.sendMessage(infos.token, chat_id=infos.prop_id,
                               text="Problema nella formattazione del messagio:\n\n\"%s\"" % text)
            break

        if "<link>" in text and "</link>" in text:
            if ":>" not in text:
                return
            desc = text.split(":>")[1]
            desc = desc.split("</link>")[0]
            link = text.split("<link>")[1]
            link = link.split(":>")[0]
            text = text.replace("<link>%s:>%s</link>" % (link, desc), "[%s](%s)" % (desc, link))
        links += 1
    return text


def rnd_elab(infos, text):
    try:
        x = 0
        while "rnd[" in text:
            if x > 10:
                x = 0 / 0
            minmax = text.split("rnd[")[1]
            minn = int(minmax.split(",")[0])
            maxx = int(minmax.split(",")[1].split("]")[0])
            if minn > maxx:
                x = 0 / 0
            num = random.randint(minn, maxx)
            if "rnd[%s,%s]" % (minn, maxx) in text:
                text = text.replace("rnd[%s,%s]" % (minn, maxx), str(num), 1)
            elif "rnd[%s, %s]" % (minn, maxx) in text:
                text = text.replace("rnd[%s, %s]" % (minn, maxx), str(num), 1)
            x += 1
        return text
    except Exception as err:
        warn = get_phrase("rnd[ err")
        HTTPLL.sendMessage(infos.token, chat_id=Manager.get_prop_id(infos.token), text=warn)
        Log.d("[Bot: @%s | %s] rnd error" % (infos.bid, infos.username))
        return None


def replacer(infos, text):
    try:

        if "[fm]" in text:
            if DBs.get_groups_number(infos.bid) < 100 and Manager.trigger_count(infos.bid) < 120:
                HTTPLL.sendMessage(infos.token, Manager.get_prop_id(infos.token),
                                   "Master, non posso ancora usare la funzionalità last.fm...")
                return
            text = text.replace("[fm]", "")
            username = infos.user.uid
            if infos.args:
                username = infos.args

            try:
                fm = LastFM(username)
            except UnregistredUser:
                return Dialogs.base_send(infos, "fmnick_missing")
            except UnvalidUsername:
                return Dialogs.base_send(infos, "fmnick_invalid")
            except EmptyTracks:
                return Dialogs.base_send(infos, "fm_no_result")

            text = text.replace("+fmnick+", fm.nickname)
            text = text.replace("+title+", fm.title())
            text = text.replace("+artist+", fm.artist())
            text = text.replace("+album+", fm.album())
            text = text.replace("[img]", "<link>+img_link+:>+zwnj+</link>")
            text = text.replace("+img_link+", fm.image())
            text = text.replace("+action+", fm.np())

        lett = "a" if infos.user.sesso == "1" else "o"

        if infos.name:
            text = text.replace("+gnome+", infos.name)

        text = text.replace("+sesso+", "una ragazza" if infos.user.sesso == "1" else "un ragazzo")

        if "+anni+" in text or "+giorni+" in text or "+anni_reali+" in text:
            date_strig = LowLevel.jfile("d", infos.bid, infos.user.lang_n)["data_nascita"]
            try:
                d, m, y = map(int, date_strig.split("/"))

                Log.d("Quindi %s/%s/%s" % (d, m, y))
                days = str(timedelta(days=(date.today() - date(y, m, d)).days)).split(" ")[0]
                years = str(int(int(days)/365))
                age = str(int(int(days) / 30))

                text = text.replace("+anni+", age)
                text = text.replace("+giorni+", days)
                text = text.replace("+anni_reali+", years)
            except Exception:
                HTTPLL.sendMessage(infos.token, infos.prop_id, "master, reimposta la mia data di nascita con /set_nascita GG/MM/AAA...")
                Log.w("%s non è una data di nascita valida..." % date_strig)
                return None

        text = text.replace("+zwnj+", zwnj)
        text = text.replace("+snome+", infos.user.sname)
        text = text.replace("+username+", infos.user.username)
        text = text.replace("{?}", lett)
        text = text.replace("[_]", "\n")
        text = text.replace("+bcount+", str(infos.bot_count))
        text = text.replace("+tcount+", str(Manager.trigger_count(infos.bid)))
        text = text.replace("+ore+", time.strftime("%H"))
        text = text.replace("+minuti+", time.strftime("%M"))
        text = text.replace("+secondi+", time.strftime("%S"))
        text = text.replace("+nome+", infos.user.name)
        text = text.replace("+moment+", timemoment()[infos.langn])
        text = text.replace("+bnome+", infos.bot_name)
        text = text.replace("+busername+", infos.username)
        text = text.replace("+uid+", str(infos.user.uid))
        text = text.replace("+gid+", str(infos.cid))
        text = text.replace("+bid+", str(infos.bid))
        text = text.replace("+kcu+", str(Unreloaded.get_cpu()) + "%")
        text = text.replace("+kmb+", str(Unreloaded.get_memory()))
        text = text.replace("+csymb+", infos.symbol)
        text = text.replace("+is_admin+", "sì" if infos.user.perms.is_admin else "no")
        text = text.replace("+kbcount+", str(Manager.get_bot_count()))
        text = text.replace("+trigger_count+", str(Manager.trigger_count(infos.bid)))

        if "+glink+" in text:
            if infos.chat_private:
                text = text.replace("+glink+", "t.me/%s" % infos.user.username)
            else:
                try:
                    text = text.replace("+glink+", HTTPLL.getInviteLink(infos))
                except Exception:
                    text = text.replace("+glink+", "<non autorizzata>")

        if infos.user.perms.is_admin:
            text = text.replace("+can_mute+", "sì" if infos.user.perms.can_restrict_members else "no")
        else:
            text = text.replace("+can_mute+", "no")

        if "+is_muted+" in text:
            usr = HTTPLL.getChatMember(infos.token, infos.cid, infos.user.uid)["result"]
            muted = "no"
            if "can_send_messages" in usr:
                if not usr["can_send_messages"]:
                    muted = "si"
            text = text.replace("+is_muted+", muted)

        if "+benvenuto+" in text:
            state = DBs.read_obj(infos.cid, infos.entity, "groups")["ext"]
            if not state or state == "0":
                state = "sì"
            else:
                state = "no"
            text = text.replace("+benvenuto+", state)

        if "cpu%"in text:
            text = text.replace("cpu", str(psutil.cpu_percent()))
        if "ram%" in text:
            text = text.replace("ram", str(psutil.virtual_memory()[2]))
        if "disk%" in text:
            text = text.replace("disk", str(psutil.disk_usage('/')[3]))

        if "+upt+" in text:
            t = datetime.fromtimestamp(Unreloaded.get_time()).strftime("%d alle %H:%M:%S")
            text = text.replace("+upt+", t)

        if infos.to_user and infos.to_user.uid != infos.bid:
            text = text.replace("+is_admin2+", "sì" if infos.to_user.perms.is_admin else "no")

            if infos.to_user.perms.is_admin:
                text = text.replace("+can_mute2+", "sì" if infos.to_user.perms.can_restrict_members else "no")
            else:
                text = text.replace("+can_mute2+", "no")

            if "+is_muted2+" in text:
                usr = HTTPLL.getChatMember(infos.token, infos.cid, infos.to_user.uid)["result"]
                muted = "no"
                if "can_send_messages" in usr:
                    if not usr["can_send_messages"]:
                        muted = "si"
                text = text.replace("+is_muted2+", muted)

            text = text.replace("+snome2+", infos.to_user.sname)
            text = text.replace("+username2+", infos.to_user.username)
            text = text.replace("+nome2+", infos.to_user.name)
            text = text.replace("+uid2+", str(infos.to_user.uid))

            lett2 = "a" if infos.to_user.sesso == "1" else "o"
            text = text.replace("{??}", lett2)
            if "+nwarns+" in text:
                try:
                    warns = json.loads(open("Files/bot_files/%s/warns.json" % infos.bid).read())[str(infos.cid)][str(infos.to_user.uid)]
                except Exception:
                    warns = 0
                text = text.replace("+nwarns+", str(warns))
        else:
            if "+nwarns+" in text:
                try:
                    warns = json.loads(open("Files/bot_files/%s/warns.json" % infos.bid).read())[str(infos.cid)][str(infos.user.uid)]
                except Exception:
                    warns = 0
                text = text.replace("+nwarns+", str(warns))

        text = text.replace("+pingt+", LowLevel.get_time(infos.time))
        text = text.replace("pingt", LowLevel.get_time(infos.time))

        if infos.is_reply:
            try:
                if "|" in infos.trigger:
                    for trigger in infos.trigger.split("|"):
                        text = text.replace("+msg2+", infos.to_user.message.text.replace(str(trigger), ""))
                elif "&" in infos.trigger:
                    for trigger in infos.trigger.split("&"):
                        text = text.replace("+msg2+", infos.to_user.message.text.replace(str(trigger), ""))
                else:
                    msg = re.sub(re.escape(infos.trigger), "", infos.to_user.message.text, flags=re.IGNORECASE)
                    text = text.replace("+msg2+", msg)
            except:
                pass

        try:
            msg = re.sub(infos.regex, "", infos.text, flags=re.IGNORECASE)
            if "|" in infos.trigger:
                for trigger in infos.trigger.split("|"):
                    msg = re.sub(trigger, "", msg, flags=re.IGNORECASE)
            elif "&" in infos.trigger:
                for trigger in infos.trigger.split("&"):
                    msg = re.sub(trigger, "", msg, flags=re.IGNORECASE)
            else:
                msg = re.sub(re.escape(infos.trigger), "", msg, flags=re.IGNORECASE)

            msg = msg.strip()
            text = text.replace("+msg+", msg)
            text = re.sub(" +", " ", text)
            text = text.strip()

        except Exception as err:
            Log.e("Errore: %s" % err)

        text = rnd_elab(infos, text)

        return text
    except Exception as err:
        msg = "riga {} {} {}".format(sys.exc_info()[-1].tb_lineno, type(err).__name__, err)
        Log.e(msg)
        Dialogs.base_send(infos, "general_error")
        return None


def check_admin_action(infos):
    """
    Returns True if the user&bot CAN do the admin action
    If the bot|user can't do the action the this foo automatically sends the warning
    ToDo: Find a way to configure per-action reports
    """
    if not infos.admin:
        Dialogs.base_send(infos, "bot_non_admin")
        return False
    if not infos.user.is_admin:
        Dialogs.base_send(infos, "ut_non_admin")
        return False
    if infos.to_user.is_admin:
        Dialogs.base_send(infos, "ut_admin")
        return False
    return True


def escape_markdown(text): return re.sub(r'([%s])' % '\*_`\[', r'\\\1', text)


def get_ordered_bots():
    ids = Manager.get_bots_id()
    bot_scores = {}
    bot_usages = {}

    for bid in ids:
        bstats = LowLevel.get_stats_file(bid)
        triggers = LowLevel.jfile("t", bid, 0)
        if not triggers:
            Manager.delete_bot(bid)
            continue

        bot_scores[str(bid)] = 0
        bot_usages[str(bid)] = 0

        for trigger in triggers["equals"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 0.5 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["contents"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 0.2 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["interactions"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 1 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["eteractions"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 1.5 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["admin_actions"]:
            if trigger in bstats:
                bot_scores[str(bid)] -= 2 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for trigger in triggers["bot_commands"]:
            if trigger in bstats:
                bot_scores[str(bid)] += 0.7 * bstats[trigger]
                bot_usages[str(bid)] += 1 * bstats[trigger]

        for section in ["insulti", "complimenti", "bene", "amare", "saluti", "scuse", "ringraziamenti"]:
            if section in bstats:
                bot_scores[str(bid)] += 0.7 * bstats[section]
                bot_usages[str(bid)] += 1 * bstats[section]

        for section in ["autom_mattina", "autom_pomeriggio", "autom_sera", "autom_notte"]:
            if section in bstats:
                bot_scores[str(bid)] += 0.3 * bstats[section]
                bot_usages[str(bid)] += 1 * bstats[section]

        if "gen_answ" in bstats:
            bot_scores[str(bid)] += 0.1 * bstats["gen_answ"]
            bot_usages[str(bid)] += 1 * bstats["gen_answ"]

        if "chiamata" in bstats:
            bot_scores[str(bid)] += 0.7 * bstats["chiamata"]
            bot_usages[str(bid)] += 1 * bstats["chiamata"]

    bot_scores = OrderedDict(sorted(bot_scores.items(), key=operator.itemgetter(1), reverse=True))
    return bot_scores, bot_scores, bot_usages


def get_rankings():
    bot_scores, bot_scores, bot_usages = get_ordered_bots()
    rankings = []
    n = 1
    for bid in bot_scores:
        token = Manager.get_token_from_bot_id(bid)
        if token not in bots_cache:
            bot = HTTPLL.getMe(token)
            del bot["token"]
            del bot["is_bot"]
            del bot["id"]
            bots_cache[token] = bot

        bots_cache[token]["score"] = int(bot_scores[str(bid)])
        bots_cache[token]["usages"] = bot_usages[str(bid)]
        bots_cache[token]["position"] = n

        rankings.append(bots_cache[token])
        n += 1
        if n >= 101:
            return rankings

    return rankings


def get_bot_from_rankings(username, ranks):
    for bot in ranks:
        if bot["username"].lower() == username.lower():
            return bot
    return None


def class_text():
    try:
        wait = False

        bot_scores, bot_scores, bot_usages = get_ordered_bots()

        n = 1
        msg = "Classifica dei *25* bot più *utilizzati*!\n\n"
        for bid in bot_scores:
            try:
                bot = BotCache.bots[Manager.get_token_from_bot_id(bid)]
                simbol = ""

                if n == 1:
                    simbol = "🥇"
                elif n == 2:
                    simbol = "🥈"
                elif n == 3:
                    simbol = "🥉"

                msg += "#*%s* - *%s* %s\n • @%s\n   *%s punti - %s utilizzi*\n\n" % (n,
                                                                                     bot["first_name"],
                                                                                     simbol,
                                                                                     escape_markdown(bot["username"]),
                                                                                     int(bot_scores[str(bid)]),
                                                                                     bot_usages[str(bid)])
            except Exception:
                wait = True
                msg += "#*%s* - *%s* %s\n • @%s\n   *%s punti - %s utilizzi*\n\n" % (n,
                                                                                     "???",
                                                                                     "???",
                                                                                     "???",
                                                                                     "???",
                                                                                     "???")
            n += 1
            if n == 26:
                break
        if wait:
            time.sleep(2)
        return msg
    except Exception as err:
        msg = "Ho trovato un errore: riga {} {} {}".format(sys.exc_info()[-1].tb_lineno, type(err).__name__, err)
        Log.e(msg)
        return None


def timemoment():
    actual = int(time.strftime("%H"))
    if 5 < actual < 12:
        return "Mattina", "Morning"
    if 12 <= actual < 18:
        return "Pomeriggio", "Evening"
    if 18 <= actual < 23:
        return "Sera", "Afternoon"
    if 23 <= actual:
        return "Notte", "Night"
    if actual <= 5:
        return "Notte", "Night"


def escape(text):
    text = text.replace("\\", "\\\\")
    text = text.replace("*", "\*")
    text = text.replace("|", "\!")
    text = text.replace("(", "\(")
    text = text.replace(")", "\)")
    text = text.replace(".", "\.")
    text = text.replace("$", "\$")
    text = text.replace("?", "\?")
    text = text.replace("+", "\+")
    return text


def regexa(text):
    f = ""
    if text.startswith("\+"):
        text = text[2:]
    text = text.replace("\+", "<>")
    for lettera in text:
        if lettera + "+" != " +":
            if lettera in 'aeiouy':
                f += lettera + "+"
            else:
                f += lettera
        else:
            f += " "
    f = f.replace("<>", "+")
    f = re.sub("\++", "+", f)
    return f


def boundary(text):
    b1, b2 = r"\b", r"\b"
    tmp = text
    text = text.replace("+", "")
    if not text[0].isalpha() and not text[0].isdigit():
        b1 = r"\B"
    if not text[-1].isalpha() and not text[0].isdigit():
        b2 = r"\B"

    return "%s%s%s" % (b1, tmp,  b2)


def get_com_symbol(entity):
    try:
        return LowLevel.read("triggers.json", entity)["bot_comm_symbol"]
    except Exception:
        return "/"


def get_antispam_time(entity):
    try:
        return float(LowLevel.read("triggers.json", entity)["antispam time"])
    except Exception:
        return 1.2


def warn_token(key):
    ids = Manager.get_bot_from_token(key)
    pid = ids["user_id"]
    bid = ids["bot_id"]

    try:
        HTTPLL.sendMessage(kitsu_token, pid, "Il tuo bot è stato scollegato per token revokata o invalida,"
                                             " registra la sua nuova token per tornare ad utilizzarlo!")
    except Exception:
        pass

    if Manager.delete_bot(bid):
            Log.a("Master, ho scollegato il bot di %s per token revocata." % pid)


def get_phrase(section): return LowLevel.dial_read("ita")[section]


def get_trigger_list(token, lang_n=0):
    try:
        result = {}
        tot = 0
        bid = Manager.get_botid_from_token(token)
        dic = LowLevel.get_triggers(bid, "triggers.json" if lang_n == 0 else "triggers_eng.json")
        sections = ["contents", "equals", "interactions", "eteractions", "bot_commands", "admin_actions"]

        for section in sections:
            tot += len(dic[section])
            result[section] = []
            for trig in dic[section]:
                result[section].append(trig)

        result["total"] = tot
        result["symbol"] = get_com_symbol(bid)

        return result
    except Exception as err:
        Log.e(err)
        return str(err)
