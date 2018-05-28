import re
import threading

from Extras.LastFM import LastFM, UnvalidUsername
from LowLevel import DBs
from Foos import Dialogs, BotsFoos
from Core import Error, HTTPLL
from Utils import Logger as Log, Utils
from Extras import Meteo


def action(infos, text, sezione):
    try:
        acts = []

        if "[reg_fm]" in text:
            acts.append("[reg_fm]")
            if not infos.args:
                Dialogs.base_send(infos, "no_args")
                return None
            try:
                LastFM(infos.args)
            except UnvalidUsername:
                Dialogs.base_send(infos, "fmnick_unexistent")
                return None
            DBs.set_data(infos.entity, infos.user.uid, "ext0", infos.args)

        if "[ban_usr]" in text or "ban_usr]" in text:
            acts.append("[ban_usr]")
            acts.append("ban_usr]")
            if not infos.admin:
                return Dialogs.base_send(infos, "bot_non_admin")
            if infos.user.is_admin:
                return Dialogs.base_send(infos, "ban_self_admin")
            HTTPLL.kickChatMember(infos.token, infos.cid, infos.user.uid, until="h0")

        if "[ban]" in text or "ban]" in text:
            acts.append("[ban]")
            acts.append("ban]")
            if infos.is_reply:
                if not infos.admin:
                    return Dialogs.base_send(infos, "bot_non_admin")
                if not infos.user.is_admin:
                    return Dialogs.base_send(infos, "ut_non_admin")
                if infos.to_user.is_admin:
                    return Dialogs.base_send(infos, "ut_admin")
                if infos.user.is_admin:
                    HTTPLL.kickChatMember(infos.token, infos.cid, infos.to_user.uid)

        if "[meteo]" in text:
            if not sezione:
                HTTPLL.sendMessage(infos.token, infos.prop_id, "Errore: meteo_text non può contenere [meteo]!")
                Log.w("Utente avvisato per errore [meteo]")
                return

            if not infos.args:
                Dialogs.base_send(infos, "no_args")
                return None

            res, sugg = Meteo.exists(infos.args)
            if not res:
                if sugg:
                    text = Dialogs.get_text(infos, "meteo_sugg")
                    if not text:
                        return None
                    text = text.replace("+sugg+", sugg.capitalize())
                    Dialogs.base_send(infos, None, special_text=text)
                    return None
                else:
                    text = Dialogs.get_text(infos, "citta_inesist")
                    if not text:
                        return None
                    Dialogs.base_send(infos, None, special_text=text)
                    return None

            text = Dialogs.get_text(infos, "meteo_text")
            if not text:
                return None

            datas = Meteo.get_datas(infos.args)
            for data_name in sorted(datas.keys()):
                text = text.replace("+" + data_name + "+", datas[data_name])
            # Dialogs.base_send(infos, None, special_text=text)

            # return None

        if "[pin]" in text:
            if infos.user.is_admin:
                HTTPLL.pinMessage(infos)
                acts.append("[pin]")
            else:
                Dialogs.base_send(infos, "ut_non_admin")
                return None

        if "[unpin]" in text:
            if infos.user.is_admin:
                HTTPLL.unpinMessage(infos)
                acts.append("[unpin]")
            else:
                return Dialogs.base_send(infos, "ut_non_admin")

        if "[settitle]" in text:
            if infos.user.is_admin:
                HTTPLL.setChatTitle(infos)
                acts.append("[settitle]")
            else:
                return Dialogs.base_send(infos, "ut_non_admin")

        if "[setdesc]" in text:
            if infos.user.is_admin:
                HTTPLL.setChatDescription(infos)
                acts.append("[setdesc]")
            else:
                return Dialogs.base_send(infos, "ut_non_admin")

        if "[setphoto]" in text:
            if infos.user.is_admin:
                if infos.to_user.message.what != "photo":
                    return None
                HTTPLL.setChatPhoto(infos)
                acts.append("[setphoto]")
            else:
                return Dialogs.base_send(infos, "ut_non_admin")

        if "[disable welcome]" in text:
            if infos.chat_private:
                return Dialogs.get_text(infos, "disable welcome privato")

            if infos.user.is_admin:
                state = DBs.read_obj(infos.cid, infos.entity, "groups")["ext"]

                if state == "1":
                    return Dialogs.get_text(infos, "benvenuto gia disabilitato")

                DBs.set_obj(infos.cid, "1", "ext", infos.entity)
                acts.append("[disable welcome]")
            else:
                return Dialogs.base_send(infos, "ut_non_admin")

        if "[enable welcome]" in text:
            if infos.chat_private:
                return Dialogs.get_text(infos, "enable welcome privato")

            if infos.user.is_admin:
                state = DBs.read_obj(infos.cid, infos.entity, "groups")["ext"]

                if not state or state == "0":
                    return Dialogs.get_text(infos, "benvenuto gia abilitato")

                DBs.set_obj(infos.cid, "0", "ext", infos.entity)
                acts.append("[enable welcome]")
            else:
                return Dialogs.base_send(infos, "ut_non_admin")

        if "[warn_usr]" in text:
            if infos.chat_private:
                return

            BotsFoos.warn(infos, self=True)
            acts.append("[warn_usr]")

        if "[mute2]" in text:
            if infos.chat_private:
                return Dialogs.get_text(infos, "mute privato")

            if not infos.user.is_admin:
                return Dialogs.get_text(infos, "ut_non_admin")

            if infos.to_user.is_admin:
                return Dialogs.get_text(infos, "ut_admin")

            if not infos.user.perms.can_restrict_members:
                return Dialogs.get_text(infos, "no_permessi")

            usr = HTTPLL.getChatMember(infos.token, infos.cid, infos.to_user.uid)["result"]
            if "can_send_messages" in usr:
                if not usr["can_send_messages"]:
                    return Dialogs.section_replacer(infos, "{already muted}")

            HTTPLL.restrictChatMember(infos.token, infos.cid, infos.to_user.uid,
                                      can_send_messages=False,
                                      can_add_web_page_previews=False,
                                      can_send_other_messages=False,
                                      can_send_media_messages=False)
            acts.append("[mute2]")

        if infos.is_reply:
            pattern = re.compile(r"\[mute:(\d+)]")
            res = re.search(pattern, text)
            if res:
                if not Utils.check_admin_action(infos):
                    return
                minutes = int(res.group(1))
                text = re.sub(pattern, "", text)
                if minutes > 60:
                    Dialogs.base_send(infos, None, special_text="Il massimo del tempo di mute temporaneo è 60 minuti!",
                                      to_id=infos.prop_id)
                    return
                if minutes < 1:
                    Dialogs.base_send(infos, None, special_text="Il minimo del tempo di mute temporaneo è 1 minuto!",
                                      to_id=infos.prop_id)
                    return

                HTTPLL.restrictChatMember(infos.token, infos.cid, infos.to_user.uid,
                                          can_send_messages=False,
                                          can_add_web_page_previews=False,
                                          can_send_other_messages=False,
                                          can_send_media_messages=False)
                threading.Thread(target=BotsFoos.temp_mute, args=(infos, minutes)).start()

        if "[unmute2]" in text:
            if infos.chat_private:
                return Dialogs.get_text(infos, "unmute privato")

            if not infos.user.is_admin:
                return Dialogs.get_text(infos, "ut_non_admin")

            if not infos.user.perms.can_restrict_members:
                return Dialogs.get_text(infos, "no_permessi")

            HTTPLL.restrictChatMember(infos.token, infos.cid, infos.to_user.uid)
            acts.append("[unmute2]")

        if "[to_en]" in text:
            if not infos.chat_private:
                if not infos.user.is_admin:
                    Dialogs.base_send(infos, "ut_non_admin")
                    return None

            if infos.chat_private:
                to_read = "users"
            else:
                to_read = "groups"
            lang = DBs.read_obj(infos.cid, infos.entity, to_read)["ext2"]
            if lang == "1":
                return Dialogs.get_text(infos, "already english")
            DBs.set_obj(infos.cid, 1, "ext2", infos.entity, where=to_read)
            acts.append("[to_en]")

        if "[to_it]" in text:
            if not infos.chat_private:
                if not infos.user.is_admin:
                    Dialogs.base_send(infos, "ut_non_admin")
                    return None

            if infos.chat_private:
                to_read = "users"
            else:
                to_read = "groups"
            lang = DBs.read_obj(infos.cid, infos.entity, to_read)["ext2"]
            if lang == "0":
                return Dialogs.get_text(infos, "già italiano")
            DBs.set_obj(infos.cid, 0, "ext2", infos.entity, where=to_read)
            acts.append("[to_it]")

        if text.startswith("kick:") and "]" in text:
            if not infos.is_reply:
                return

            if not infos.admin:
                return Dialogs.base_send(infos, "bot_non_admin")

            if not infos.user.is_admin:
                return Dialogs.base_send(infos, "ut_non_admin")

            if infos.to_user.is_admin:
                return Dialogs.base_send(infos, "ut_admin")
            t = text.split(":")[1].split("]")[0]
            acts.append("kick:%s]" % t)
            try:
                HTTPLL.kickChatMember(infos.token, infos.cid, infos.to_user.uid, until="h" + t)
            except Error.InvalidKickTime:
                HTTPLL.sendMessage(infos.token, infos.prop_id, "%s non è un valido kicktime!" % t)
                return None

    except Error.NotEnoughtRights:
        Dialogs.base_send(infos, "bot_non_admin")
        return None

    except Error.GeneralError:
        Dialogs.base_send(infos, "general_error")
        return None

    except Error.UnkownError:
        Dialogs.base_send(infos, "general_error")
        return None

    except Exception as err:
        Log.e(err)
        return None

    for act in acts:
        text = text.replace(act, "")

    return text
