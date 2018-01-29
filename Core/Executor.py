# coding=utf-8
from datetime import timedelta, date

import requests
import random
import re

from LowLevel.LowLevel import *
from LowLevel.KaiDBs import *

from Core import HTTPLL, Dialoger as endPoint

kaID = 52962566
zwnj = "‌"


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


def replacer(infos, text):
    lett = "a" if infos.user.sesso == "1" else "o"
    if infos.is_reply:
        lett2 = "a" if infos.to_user.sesso == "1" else "o"
        text = text.replace("{??}", lett2)

    text = text.replace("+nome+", infos.user.name)

    text = text.replace("+moment+", timemoment()[infos.lang])

    text = text.replace("+nome2+", infos.to_user.name)

    text = text.replace("{?}", lett)

    return text


def check_for_action(infos, risposta):
    if risposta.startswith("+pht+"):
        infos.bot.sendChatAction(chat_id=infos.cid, action='upload_photo')
        time.sleep(0.7)
        risposta = risposta.split("()")[1]
        if ">>" in risposta:
            infos.bot.sendPhoto(photo=risposta.split(">>")[0],
                                caption=risposta.split(">>")[1],
                                chat_id=infos.cid)
        else:
            infos.bot.sendPhoto(photo=risposta, chat_id=infos.cid)
        return

    if risposta.startswith("+aud+"):
        infos.bot.sendChatAction(chat_id=infos.cid, action='record_audio')
        time.sleep(1)
        return infos.bot.sendVoice(chat_id=infos.cid, voice=open("audios/" + risposta.split("()")[1], "rb"))

    if risposta.startswith("+stk+"):
        return infos.bot.sendSticker(chat_id=infos.cid, sticker=risposta.split("()")[1])

    if risposta.startswith("+doc+"):
        return infos.bot.sendDocument(document=risposta.split("()")[1], chat_id=infos.cid)

    return False


def html_link(link, text): return ' <link>%s:>%s</link>' % (link, text)


def get_value(file, item, entity):
    try:
        values = json.loads(codecs.open("files/%s/%s" % (entity, file), encoding='utf8').read(), entity)
        return values[item]
    except Exception as err:
        Log.e(err)
        return None


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\[\]'
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


baseurl = "https://query.yahooapis.com/v1/public/yql?q="
part1 = "select * from weather.forecast where woeid in "
yql_query = part1 + "(select woeid from geo.places(1) where text='%s, it') and u='c' &format=json"
mots = ["^-^",
        ":3",
        "♥",
        "(=^▽^=)",
        "o(^▽^)o",
        "(^～^)",
        "(^ _ ^)/"
        ]

days = {"Mon": "Lunedì",
        "Tue": "Martedì",
        "Wed": "Mercoledì",
        "Thu": "Giovedì",
        "Fri": "Venerdì",
        "Sat": "Sabato",
        "Sun": "Domenica"}

card = {
    "0": ["Nord", "Tramontana"],
    "45": ["Grecale", "Nord-Est"],
    "90": ["Est", "Levante"],
    "135": ["Sud-Est", "Scirocco"],
    "180": ["Sud", "Ostro/Mezzogiorno"],
    "225": ["Sud-Ovest", "Libeccio"],
    "270": ["Ovest", "Ponente"],
    "315": ["Nord-Ovest", "Maestrale"]
}


def get_broadcast(infos, citta, giorno=0):
    try:
        result = requests.get(baseurl + yql_query % citta)

        result = result.json()

        datas = result["query"]["results"]["channel"]

        umidita = datas["atmosphere"]["humidity"] + "%"
        vel_vento = datas["wind"]["speed"] + " km/h"
        dir_vento = int(datas["wind"]["direction"])

        if dir_vento < 45:
            dir_vento = "0"
        elif dir_vento < 90:
            dir_vento = "45"
        elif dir_vento < 135:
            dir_vento = "90"
        elif dir_vento < 180:
            dir_vento = "135"
        elif dir_vento < 225:
            dir_vento = "180"
        elif dir_vento < 270:
            dir_vento = "225"
        elif dir_vento < 315:
            dir_vento = "270"
        else:
            dir_vento = "315"

        alba = datas["astronomy"]["sunrise"].split()[0]
        tramonto = datas["astronomy"]["sunset"].split()[0]
        tramonto = str(int(tramonto.split(":")[0]) + 12) + ":" + tramonto.split(":")[1].zfill(2)

        forecast = datas["item"]["forecast"]
        temp_max = forecast[giorno]["high"]
        temp_min = forecast[giorno]["low"]
        day = days[forecast[giorno]["day"]]
        dayn = int(forecast[giorno]["date"].split()[0])

        try:
            desc = jfile("c", infos.bid, infos.user.lang_n)[forecast[giorno]["text"].lower()]
        except:
            desc = forecast[giorno]["text"]

        text = "Allora...\nEcco il meteo di <b>%s</b> per <b>%s %s</b>~\n\n" % (citta.capitalize(), day, dayn)
        text += get_sec(infos, "meteo_f")[1] % desc
        text += get_sec(infos, "meteo_f")[0] % (temp_min, temp_max)
        if giorno == 0:
            text += "\n\nIl sole sorgerà alle <b>%s</b> e tramonterà alle <b>%s</b>" % (alba, tramonto)
            text += "\nLa velocità del vento sarà di <b>%s</b> verso <b>%s</b> " \
                    "quindi </b>%s</b> ~\nL'umidità sarà al <b>%s</b> circa!" % (
                    vel_vento, card[dir_vento][0], card[dir_vento][1], umidita)

        text += "\n\nNyah +nome+~ ♥"

        return text

    except Exception as err:
        Log.e(err)
        return str(err)


def citta_exists(citta):
    result = requests.get(baseurl + yql_query % citta)
    result = result.json()

    try:
        city = result["query"]["results"]["channel"]["location"]["city"].lower()
    except:
        return False, None

    if city.lower() == citta.lower():
        return True, None

    else:
        return False, city


def reg_meteo(infos):
    Log.a("Registrazione meteo: %s" % infos.user.username)
    try:
        citta = infos.text.split(": ")[1]
    except:
        return send(infos, "Manca la città")

    res, sugg = citta_exists(citta)
    if not res:
        if sugg:
            risp = "La città che mi hai indicato credo non esista...\n"
            risp += "La più simile che ho trovato è %s" % sugg.capitalize()
            return send(infos, risp)
        else:
            return send(infos, "Non credo che questa città esista...")

    add_objs(infos.user.uid, citta, "city", infos.entity)
    return send(infos, "Dovrei averti registrato ~")


def meteo(infos):
    Log.a("Richiesta meteo da: %s" % infos.user.username)
    if ":" in infos.text:

        try:
            day = int(infos.text.split()[-1])
            day = True
        except:
            day = False

        try:
            citta = infos.text.split(": ")[1]
        except:
            return send(infos, "Devi specificare una città se metti i due punti... uwu")

        if day:
            citta = " ".join(citta.split()[:-1])

        res, sugg = citta_exists(citta)
        if not res:
            if sugg:
                risp = "La città che mi hai indicato credo non esista...\n"
                risp += "La più simile che ho trovato è %s" % sugg.capitalize()
                return send(infos, risp)

            else:
                return send(infos, "Non credo che questa città esista...")

    else:
        citta = read_obj(infos.user.uid, infos.entity)["city"]

    if not citta:
        return send(infos, "Sicuro di esserti registrato?\nPer farlo scrivi \"Kai citta: città\"")

    try:
        day = int(infos.text.split()[-1])
    except:
        day = 0

    if day < 0 or day > 9:
        return send(infos, "Puoi scegliere il giorno per cui ottenere il meteo con un numero da 1 a 9")

    return send(infos, get_broadcast(infos, citta, giorno=day))

    # send(infos, "Se ne sta venendo a piovere porcodio")


def ban_user(infos): infos.bot.kickChatMember(chat_id=infos.cid, user_id=infos.to_user.uid)


def say(infos, sezione): return random.choice(jfile("d", infos.bid, infos.user.lang_n)[sezione])


def camellia(infos): send(infos, say(infos, "songs2") + say(infos, "songs"))


def stato_animo(infos): send(infos, say(infos, "felice"))


def state(infos): send(infos, say(infos, "stato_animo" + "_happy"))


def send(infos, reply): return endPoint.send(infos, None, special_text=reply)


def get_sec(infos, sezione):
    dialogs = jfile("d", infos.bid, infos.user.lang_n)
    return dialogs[sezione]


def lastfm(infos):
    try:
        # TODO: Fix error: 'message'
        class Datas:
            def __init__(self):
                self.title = "Title"
                self.artist = "Artist"
                self.album = "Group Name"
                self.image = "Image URL"
                self.np = "Now Playing?"

            def obtain(self, data):
                try:
                    self.title = data['recenttracks']['track'][0]['name']
                    self.artist = data['recenttracks']['track'][0]['artist']['#text']
                    self.album = data['recenttracks']['track'][0]['album']['#text']
                    self.image = data['recenttracks']['track'][0]['image'][3]["#text"]
                    try:
                        self.np = dati['recenttracks']['track'][0]['@attr']['nowplaying']
                        self.np = True
                    except:
                        self.np = False
                except:
                    self.artist = "err"
                return self

        key = "&api_key=ccb28618868b79c238a20e96c9d5a6d2"
        url = "http://ws.audioscrobbler.com/2.0/?"
        metod = "method=user.getrecenttracks"
        if ":" in infos.text:
            nick = infos.text.split(": ")[1]
            try:
                user = "&user=" + nick
            except:
                return send(infos, say(infos, "invalid_user"))
        else:
            try:
                nick = read_obj(infos.user.uid, infos.entity)["fmnick"]
                if not nick:
                    return send(infos, say(infos, "unreg"))
            except Exception as err:
                Log.d("Utente non registrato..?")
                Log.d("(%s)" % err)
                return send(infos, say(infos, "unreg"))
        user = "&user=" + nick
        form = "&format=json&limit=1"
        req = requests.get(url + metod + user + key + form)
        dati = req.json()

        try:
            if dati['message'] == "User not found":
                return send(infos, say(infos, "invalid_user"))
        except:
            pass

        datas = Datas()
        datas = datas.obtain(dati)

        if datas.artist == "err":
            return send(infos, say(infos, "fm_nothing") % nick)

        if datas.np:
            action = get_sec(infos, "fm_action")[0]
        else:
            action = get_sec(infos, "fm_action")[1]

        text = "%s %s %s by %s!" % (nick, action, datas.title, datas.artist)

        if datas.album:
            text += get_sec(infos, "fm_action")[2] % datas.album

        # text += html_link(datas.image, ".")
        if datas.image:
            HTTPLL.sendPhoto(infos.token, chat_id=infos.cid, photo=datas.image, caption=text)
        else:
            return send(infos, text)
            # return send(infos, text)
    except Exception as err:
        Log.e("[executor] " + str(err))
        return send(infos, say(infos, "errore"))


def reg_fm(infos):
    try:
        text = infos.text
        nick = text.split(": ")[1]
        key = "&api_key=ccb28618868b79c238a20e96c9d5a6d2"
        url = "http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks"
        user = "&user=" + nick
        form = "&format=json&limit=1"
        req = requests.get(url + user + key + form)
        dati = req.json()
        try:
            if dati['message'] == "User not found":
                return send(infos, say(infos, "invalid_user"))
        except:
            add_objs(infos.user.uid, nick, "lastfm", infos.entity)
            return send(infos, say(infos, "fatto"))
    except Exception as err:
        Log.e(err)
        return send(infos, say(infos, "errore"))


def uccidi(infos):
    if infos.is_reply:
        if infos.to_user.uid == infos.bid:
            return send(infos, say(infos, "uccidi self"))
        if infos.to_user.uid == infos.user.uid:
            return send(infos, say(infos, "suicidio"))
        if infos.to_user.uid == kaID:
            return send(infos, say(infos, "uccidi master"))
        return send(infos, say(infos, "uccidi"))
    else:
        return send(infos, say(infos, "uccidi none"))


def banna(infos):
    if infos.chat_private:
        return send(infos, say(infos, "ban_private"))

    if not infos.is_reply:
        return send(infos, say(infos, "non_risp"))

    if infos.to_user.is_to_bot:
        return send(infos, say(infos, "auto_ban"))

    if infos.to_user.is_admin:
        return send(infos, say(infos, "user_is_admin"))

    if infos.user.is_admin:
        if infos.admin:
            ban_user(infos)
            return send(infos, say(infos, "banning"))

        else:
            return send(infos, say(infos, "non_admin"))

    else:
        send(infos, say(infos, "ut_non_admin"))


def inglese(infos):
    if infos.chat_private:
        add_objs(infos.user.uid, 1, "lang", infos.entity)
    else:
        if not infos.user.is_admin:
            return send(infos, say(infos, "lang_eng[admin err]"))
        set_group_obj(infos, "lang", 1)

    send(infos, say(infos, "lang_eng"))


def italiano(infos):
    if infos.chat_private:
        add_objs(infos.user.uid, 0, "lang", infos.entity)
    else:
        if not infos.user.is_admin:
            return send(infos, say(infos, "lang_ita[admin err]"))
        set_group_obj(infos, "lang", 0)

    send(infos, say(infos, "lang_ita"))


def eta(infos):
    x = get_sec(infos, "eta_r")[0]
    days = str(timedelta(days=(date.today() - date(2016, 11, 4)).days)).replace(" ", "")[:3]
    age = str(int(int(days) / 30))
    send(infos, x.replace("xyears", age).replace("xdays", days))


def disable(infos):
    if infos.chat_private or not infos.user.is_admin:
        return

    if read_group_obj(infos.cid, infos.entity)[0] == 1:
        return send(infos, say(infos, "gia disattivato"))

    send(infos, say(infos, "disattivato") if set_group_obj(infos, "muted", 1) else say(infos, "errore"))


def enable(infos):
    if infos.chat_private or not infos.user.is_admin:
        return

    if read_group_obj(infos.cid, infos.entity)[0] == 0:
        return send(infos, say(infos, "gia attivato"))

    send(infos, say(infos, "attivato") if set_group_obj(infos, "muted", 0) else say(infos, "errore"))


def picchia(infos):
    if not infos.is_reply:
        return send(infos, say(infos, "picchia_none"))

    if infos.to_user.is_to_bot:
        return send(infos, say(infos, "picchia_self"))

    if infos.user.is_master:
        return send(infos, say(infos, "picchia_da_master"))

    if infos.to_user.is_master:
        return send(infos, say(infos, "picchia_master"))

    return send(infos, say(infos, "picchia_user"))


def delete(infos):
    try:
        if not infos.user.is_admin:
            return
        infos.bot.deleteMessage(chat_id=infos.cid, message_id=infos.to_user.message.id)
        infos.bot.deleteMessage(chat_id=infos.cid, message_id=infos.user.message.id)
        msg = "uwu" if infos.entity == 0 else ":/"
        msgid = send(infos, msg)["message_id"]
        time.sleep(1.2)
        infos.bot.deleteMessage(chat_id=infos.cid, message_id=msgid)
    except:
        pass


def elab_find_msg(infos, datas):
    uid = datas["id"]
    name = datas["name"]
    username = datas["username"]
    dat = str(datas["date"]).replace(" ", " alle ")
    fmnick = datas["fmnick"]
    city = datas["city"]
    propic_id = infos.bot.getUserProfilePhotos(user_id=datas["id"])["photos"][0][2]["file_id"]

    msg = "Si, @%s, %s, ID %s primo incontro: %s\n" % (username, name, uid, dat)

    if fmnick:
        msg += "E' registrato come %s per last.fm\n" % fmnick
    if city:
        msg += "La sua città per il meteo è %s" % city

    if propic_id:
        infos.bot.sendPhoto(chat_id=infos.cid, photo=propic_id, caption=msg)
    else:
        send(infos, msg)


def find_user(infos):
    try:
        if not infos.user.is_master:
            return
        request = infos.user.message.text.lower()
        if request.startswith("kai conosci "):
            request = request.replace("kai conosci ", "")
            request = request.replace("?", "")
        else:
            return

        try:
            datas = read_obj(int(request), infos.entity)
            if datas["id"]:
                elab_find_msg(infos, datas)
            else:
                send(infos, "Non trovato...")
        except Exception:
            pass

        if request.startswith("@"):
            request = request.replace("@", "")
            datas = get_objs_from_username(infos, request)
            if not datas["id"]:
                return send(infos, "Non ho trovato risultati.")
            elab_find_msg(infos, datas)
            return

        res, cont = get_similars_from_name(infos, request)
        if not res:
            return send(infos, "C'è qualche problema...")

        if res == "zero":
            return send(infos, "No, non ho trovato nessun utente con un nome simile...")
        if res == "one":
            return elab_find_msg(infos, cont)

        msg = "Ho trovato:\n"
        maxi = 0
        for usr in cont:
            if maxi == 10:
                break
            msg += "%s (@%s)\n" % (usr["name"], usr["username"])
            maxi += 1

        send(infos, msg)

    except Exception as err:
        send(infos, "C'è stato qualche problema...")
        Log.e(err)


def sono_femmina(infos):
    if infos.user.sesso == "1":
        return send(infos, "Ma lo so già... ouo")
    if not add_objs(infos.user.uid, "1", "sesso", infos.entity):
        return send(infos, "Qualcosa non va...")
    send(infos, say(infos, "to_femmina"))


def sono_maschio(infos):
    if infos.user.sesso == "0":
        return send(infos, "Ma lo so già... ouo")
    if not add_objs(infos.user.uid, "0", "sesso", infos.entity):
        return send(infos, "Qualcosa non va...")
    send(infos, say(infos, "to_maschio"))


def warn_user(infos):
    try:
        warns = json.loads(open("jsons/warns.json").read())

        if not infos.admin:
            return send(infos, say(infos, "non_admin"))
        if infos.is_auto:
            return send(infos, say(infos, "auto_warn"))
        if not infos.user.is_admin:
            return send(infos, say(infos, "ut_non_admin"))
        if infos.to_user.is_admin:
            return send(infos, say(infos, "user_is_admin"))
        if infos.to_user.is_master:
            return send(infos, say(infos, "user_is_master"))

        gid = str(infos.cid)
        ut_to_warn = str(infos.to_user.uid)

        if gid not in warns:
            warns[gid] = {}

        if ut_to_warn not in warns[gid]:
            warns[gid][ut_to_warn] = 0

        warns[gid][ut_to_warn] += 1
        nwarns = warns[gid][ut_to_warn]

        if nwarns == 1:
            send(infos, say(infos, "warn1"))
            Log.d("Utente %s del gruppo %s warnato da %s per la prima volta" % (ut_to_warn, gid, infos.user.username))

        if nwarns == 2:
            send(infos, say(infos, "warn2"))
            Log.d("Utente %s del gruppo %s warnato da %s per la seconda volta" % (ut_to_warn, gid, infos.user.username))

        if nwarns == 3:
            warns[gid][ut_to_warn] = 0
            send(infos, say(infos, "warn3"))
            ban_user(infos)
            Log.d("Utente %s del gruppo %s warnato da %s per la terza volta" % (ut_to_warn, gid, infos.user.username))

        with open("jsons/warns.json", "w") as fl:
            fl.write(json.dumps(warns))

    except Exception as err:
        send(infos, say(infos, "errore"))
        Log.e(err)


def unwarn_user(infos):
    try:
        warns = json.loads(open("jsons/warns.json").read())

        if not infos.admin:
            return send(infos, say(infos, "non_admin"))
        if infos.is_auto:
            return send(infos, say(infos, "auto_unwarn"))
        if not infos.user.is_admin:
            return send(infos, say(infos, "ut_non_admin"))
        if infos.to_user.is_admin:
            return send(infos, say(infos, "user_is_admin"))
        if infos.to_user.is_master:
            return send(infos, say(infos, "user_is_master"))

        gid = str(infos.cid)
        ut_to_unwarn = str(infos.to_user.uid)

        if gid not in warns:
            warns[gid] = {}

        if ut_to_unwarn not in warns[gid]:
            warns[gid][ut_to_unwarn] = 0

        warns[gid][ut_to_unwarn] -= 1
        nwarns = warns[gid][ut_to_unwarn]

        if nwarns == -1:
            send(infos, say(infos, "unwarn_-1"))
            Log.d(
                "Utente %s del gruppo %s unwarnato da %s ma non aveva warns" % (ut_to_unwarn, gid, infos.user.username))
            return

        if nwarns == 0:
            send(infos, say(infos, "unwarn_0"))
            Log.d("Utente %s del gruppo %s unwarnato da %s, ora non ha più warns" % (
                ut_to_unwarn, gid, infos.user.username))

        if nwarns == 1:
            send(infos, say(infos, "unwarn_1"))
            Log.d("Utente %s del gruppo %s warnato da %s, ora ha un warn" % (ut_to_unwarn, gid, infos.user.username))

        with open("jsons/warns.json", "w") as fl:
            fl.write(json.dumps(warns))

    except Exception as err:
        send(infos, say(infos, "errore"))
        Log.e(err)


def no_meteo(infos):
    unreg = json.loads(open("jsons/unregistered.json").read())
    Log.a("%s si è de-registrato" % infos.user.username)
    if infos.user.uid in unreg:
        return send(infos, "L-lo so già!")
    else:
        unreg.append(infos.user.uid)
        with open("jsons/unregistered.json", "w") as fl:
            fl.write(json.dumps(unreg))
        return send(infos, "O-ok!")
