import random
import re
import sys
import time

from LowLevel import LowLevel
from Utils import Logger as Log, Utils
from Core import Manager, HTTPLL, Error


def get_text(infos, sezione):
    try:
        sezione = sezione.lower()

        if infos.bid == 554500728 and infos.user.uid in [276804260] and sezione == "i'm back":
            sezione += " moon"

        dialogs = LowLevel.jfile("d", infos.bid, infos.user.lang_n)
        if not dialogs:
            return Log.w("Mi è stato impossibile leggere i dialoghi di %s lang_n %s" % (infos.bid, infos.user.lang_n))

        if sezione not in dialogs:
            if sezione == "start":
                dialogs = {"start": ["Nessuno start impostato."]}
            else:
                warning = "sezione dei dialoghi %s in lingua %s non trovata..." % (
                    sezione, "IT" if infos.user.lang_n == 0 else "EN")
                HTTPLL.sendMessage(infos.token, chat_id=Manager.get_prop_id(infos.token), text=warning)
                return None

        if not dialogs[sezione]:
            if sezione == "start":
                dialogs = {"start": ["Nessuno start impostato."]}
            else:
                warning = "%s in lingua %s non ha frasi!" % (sezione, "IT" if infos.user.lang_n == 0 else "EN")
                HTTPLL.sendMessage(infos.token, chat_id=Manager.get_prop_id(infos.token), text=warning)
                return None

        frisp = None
        risposte = dialogs[sezione]
        while risposte:
            try:
                risp = random.choice(risposte)
            except:
                break
            match = re.search("^\[\d{1,2}>\d{1,2}]", risp)
            if match:
                ore = match.group(0).split(">")
                mi = int(str(ore[0]).replace("[", ""))
                ma = int(str(ore[1]).replace("]", ""))
                if ma == 0:
                    ma = 24
                at = int(time.strftime("%H"))
                if at == 0:
                    at = 24
                if mi <= at <= ma:
                    frisp = risp.replace(match.group(0), "")
                    # infos.reply("Trovato: %s > %s : %s" % (mi, ma, at))
                    break
                if not frisp:
                    frisp = "skip"
                risposte.remove(risp)
            else:
                frisp = risp
                risposte.remove(risp)

        if frisp:
            risp = frisp

        # risp = random.choice(dialogs[sezione])
        if risp.startswith("[private]") and not risp.endswith("[private]"):
            if not infos.chat_private:
                while dialogs[sezione]:
                    risp = random.choice(dialogs[sezione])
                    dialogs[sezione].remove(risp)
                    if risp.startswith("[private]") or risp.endswith("[private]"):
                        risp = risp.replace("[private]", "")
                        break
                    elif "[private]" in risp:
                        risp = risp.split("[private]")[1]
                        break
                return None
            else:
                risp = risp.replace("[private]", "")

        elif "[private]" in risp and not risp.endswith("[private]") and not risp.startswith("[private]"):
            if infos.chat_private:
                risp = risp.split("[private]")[0]
            else:
                risp = risp.split("[private]")[1]

        if risp.lower() in ["skip", "+skip+"]:
            return None

        stats = LowLevel.get_stats_file(infos.bid)

        if sezione not in stats:
            stats[sezione] = 0

        stats[sezione] += 1

        LowLevel.write_stats_file(infos.bid, stats)

        return risp
    except Exception as err:
        msg = "Ho trovato l'errore: riga {} {} {}\nSegnalalo a @Kaikyu fast!".format(sys.exc_info()[-1].tb_lineno,
                                                                                     type(err).__name__, err)
        print(msg)
        return None


def section_replacer(infos, text):
    x = 0
    while x < 10:
        matches = re.search("{[^}]{3,}}", text)
        if matches:
            x += 1
            text = text.replace(matches.group(0), str(get_text(infos, matches.group(0).replace("{", "").replace("}", ""))))
        else:
            break
    return text


def base_send(infos, sezione, special_text=None, to_id=None):
    try:
        infos.trigger = sezione
        if special_text:
            text = special_text
        elif sezione:
            text = get_text(infos, sezione)
        else:
            return

        text = Utils.replacer(infos, text)
        if not text:
            return

        text, kb = Utils.get_keyboard(text)
        if text == "":
            return

        text = Utils.escape_markdown(text)

        text = text.replace("<b>", "*").replace("</b>", "*")
        text = text.replace("<c>", "`").replace("</c>", "`")
        text = text.replace("<i>", "_").replace("</i>", "_")

        if to_id:
            infos.cid = to_id

        HTTPLL.sendChatAction(infos.token, infos.cid, 'typing')
        time.sleep(0.2)
        HTTPLL.sendMessage(infos.token, chat_id=infos.cid, text=text)

        return None

    except Error.Unauthorized as err:
        return "ERR"

    except Exception as err:
        return "ERR"
