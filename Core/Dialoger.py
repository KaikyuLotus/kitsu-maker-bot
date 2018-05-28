# coding=utf-8

# Copyright (c) 2017 Kaikyu

import json
import time
import sys
import re

from Foos import Actions, Dialogs, BotsFoos
from Core import HTTPLL, Unreloaded, Error, Manager
from LowLevel import DBs
from Utils import Logger as Log, Utils


recursivity = {}


# Split this function in more methods
def send(infos, sezione,
         antispam=True,
         to_id=None,
         special_name=None,
         special_group_name=None,
         special_user_name=None,
         no_log=False,
         special_token=None,
         special_bid=None,
         special_text=None,
         ignore_specials=False,
         recorsivity=None,
         add=None,
         parse="markdown"):
    text = "<vuoto>"
    try:
        quote = False
        inter_bot_id = None
        sezione_inter = None
        quitta = False
        no_prew = False

        if sezione:
            infos.trigger = sezione
        else:
            infos.trigger = ""

        if recorsivity:
            if recorsivity > 3:
                return
            else:
                recorsivity += 1
        else:
            recorsivity = 1

        if not to_id:
            to_id = infos.cid

        if special_group_name:
            infos.name = special_group_name
        if special_user_name:
            infos.user.name = special_user_name

        if special_token:
            infos.token = special_token

        if special_bid:
            infos.bid = special_bid

        if not special_text:

            text = Dialogs.get_text(infos, sezione)
            if add:
                try:
                    text += add
                except Exception:
                    pass
            if not text:
                return False

            if text.lower() == "skip" or text.lower() == "+skip+":
                return True

            if antispam:
                if Unreloaded.antispam(infos):
                    return True

        else:
            text = special_text

        text = Dialogs.section_replacer(infos, text)

        if infos.api:
            return text

        if "[warn]" in text:
            return BotsFoos.warn(infos)

        if "[unwarn]" in text:
            return BotsFoos.unwarn(infos)

        if "+exe+" in text:
            infos.master_message("Master, +exe+ is deprecated:\n`" + text + "`\nIn `" + sezione + "`",
                                 parse_mode="markdown")
            Log.a("[%s] U: %s %s" % (infos.bot_name, infos.user.username, sezione))
            return

        if not ignore_specials:
            text = Utils.replacer(infos, text)
            text = Actions.action(infos, text, sezione)
            if not text:
                return

        if type(text) is bool:
            return

        if "[noprew]" in text:
            text = text.replace("[noprew]", "")
            no_prew = True

        if "[quote]" in text:
            text = text.replace("[quote]", "")
            quote = infos.user.message.id

        if "[quote2]" in text:
            text = text.replace("[quote2]", "")
            if infos.to_user:
                quote = infos.to_user.message.id

        if "[quit]" in text:
            text = text.replace("[quit]", "")
            quitta = True

        match = re.search("\[(\d+)\]", text)
        if match:
            if int(match.group(1)) not in Manager.get_bots_id():
                return HTTPLL.sendMessage(infos.token, Manager.get_prop_id(infos.token),
                                          "%s non è un ID valido." % match.group(1))

            result = text.split("[" + match.group(1) + "]")

            trigs = json.loads(open("Files/bot_files/%s/%s" % (match.group(1), "triggers.json")).read())

            if "autorizzati" not in trigs:
                HTTPLL.sendMessage(infos.token, infos.prop_id, "%s non ti ha autorizzato." % match.group(1))

            elif infos.bid not in trigs["autorizzati"]:
                HTTPLL.sendMessage(infos.token, infos.prop_id, "%s non ti ha autorizzato." % match.group(1))
                # infos.reply("Autorizzati: %s" % )
            else:
                inter_bot_id = int(match.group(1))
                sezione_inter = result[1]

            text = result[0]

        if special_name:
            text = text.replace("+newuser+", special_name)

        if not text:
            return

        text, kb = Utils.get_keyboard(text)
        if text == "":
            return

        try:
            caption = None
            if "+stk+" in text:
                stk = text.split("()")[1]
                HTTPLL.sendSticker(infos.token, chat_id=to_id, sticker=stk)
                return True

            if "+pht+" in text:
                elems = text.split("()")
                pht = elems[1]
                if len(elems) == 3:
                    caption = elems[2]
                HTTPLL.sendChatAction(infos.token, to_id, 'upload_photo')
                time.sleep(0.3)
                HTTPLL.sendPhoto(infos.token, chat_id=to_id, photo=pht, caption=caption, reply_to_message_id=quote)
                return True

            if "+doc+" in text:
                elems = text.split("()")
                doc = elems[1]
                if len(elems) == 3:
                    caption = elems[2]
                HTTPLL.sendDocument(infos.token, to_id, doc, caption=caption, reply_to_message_id=quote)
                return True

            if "+aud+" in text or "+voi+" in text:
                aud = text.split("()")[1]
                HTTPLL.sendVoice(infos.token, to_id, aud, reply_to_message_id=quote)
                return True

            if "+vid+" in text:
                elems = text.split("()")
                vid = elems[1]
                if len(elems) == 3:
                    caption = elems[2]
                HTTPLL.sendVideo(infos.token, to_id, vid, caption=caption, reply_to_message_id=quote)
                return True
        except Exception as err:
            Log.w("Errore nell'invio del media: %s" % err)
            return False

        text = Utils.escape_markdown(text)

        text = text.replace("<b>", "*").replace("</b>", "*")
        text = text.replace("<c>", "`").replace("</c>", "`")
        text = text.replace("<i>", "_").replace("</i>", "_")

        text = Utils.link_elab(text, infos)

        text = re.sub("\/\w+\\_\w+", "$&", text).replace("\\\\_", "\\_")

        match = re.search("\B<q>.+</q>\B", text)
        if match:
            iquote = "[%s](tg://user?id=%s)" % (str(match.group(0))
                                                .replace("<q>", "").replace("</q>", ""), infos.user.uid)
            text = re.sub("\B<q>.+</q>\B", iquote, text)

        result = re.finditer(re.compile(r"\*.+?\*"), text)
        if result:
            for res in result:
                text = text.replace(res.group(), res.group(0).replace("\_", "_"))

        HTTPLL.sendChatAction(infos.token, to_id, 'typing')
        HTTPLL.sendMessage(infos.token, chat_id=to_id, text=text, parse_mode=parse,
                           disable_web_page_preview=no_prew, reply_to_message_id=quote, reply_markup=kb)

        if not no_log:
            Log.a("%s <- %s -> [%s]" % (infos.bid, infos.user.uid, sezione))

        if infos.chat_private:
            return
        if quitta:
            HTTPLL.leaveChat(infos.token, infos.cid)
        if inter_bot_id and sezione_inter:
            try:
                send(infos, sezione_inter, special_token=Manager.get_token_from_bot_id(inter_bot_id),
                     antispam=False,
                     special_bid=inter_bot_id,
                     recorsivity=recorsivity)
            except Exception:
                pass
        return True

    except Error.Unauthorized:
        if not to_id:
            Log.e("Qualcosa non va, l'ID era None...")
            return "ERR"
        DBs.remove_id(infos.entity, to_id)
        return "ERR"

    except Error.BadRequest as err:
        if "chat not found" in str(err):
            return

        if "group chat was migrated" in str(err):
            DBs.remove_id(infos.entity, to_id)
            return "ERR"

        Log.e("Bot %s -> BadRequest (%s)" % (infos.bot_name, err))

        if infos.user.is_owner:
            infos.reply("Master non sono riuscita ad inviare questo messaggio:\n"
                        "`%s`\nSegnalalo a @Kaikyu o controlla la formattazione." % text, markdown=True)
        return "ERR"

    except Error.NotEnoughtRights:
        DBs.remove_id(infos.entity, to_id)
        return "ERR"

    except Exception as err:
        msg = "Ho trovato un errore: riga {} {} {}".format(sys.exc_info()[-1].tb_lineno, type(err).__name__, err)
        HTTPLL.sendMessage(infos.token, infos.prop_id, msg)
        Log.e(msg)
        if "can't parse" in str(err).lower():
            # noinspection PyTypeChecker
            send(infos, "",
                 to_id=Manager.get_prop_id(infos.token),
                 special_text="C'è un problema con la formattazione del messaggio:\n\n%s" % text,
                 parse=None,
                 antispam=False)
        return "ERR"
