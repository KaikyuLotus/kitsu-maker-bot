# coding=utf-8

import io
import json
import shutil
import time

from Utils import Logger as Log
import requests
from urllib.parse import quote

from Core import Unreloaded
from Core.Error import InvalidKickTime, Unauthorized, NoQuotedMessage, UnkownError, NotEnoughtRights, BadRequest, NotFound404

base_url = "https://api.telegram.org/bot"

bans = {"h12": 43200, "h10": 36000, "h8": 28800, "h4": 14400, "h2": 7200, "h1": 3600, "h0": 1800, "ever": 0}


def keyboard_btn(text, url):
    return [{"text": text, "url": url}]


def inline_keyboard(btns):
    return json.dumps({"inline_keyboard": btns})


def get_symbol(text): return "" if text.endswith("?") else "&"


def make_request(method, toke, **kwargs):

    req = base_url + toke + "/" + method + "?"

    for key, value in kwargs.items():
        if not value:
            continue
        req += "&%s=%s" % (key, quote(str(value)))

    req = req.replace("?&", "?", 1)

    r = requests.get(req)

    if r.status_code != 200:
        if "rights" in r.json()["description"]:
            raise NotEnoughtRights

        if r.status_code == 403 or "Unauthorized" in r.json()["description"]:
            raise Unauthorized

        if r.status_code == 400:
            raise BadRequest(r.json()["description"] + " :(")

        if r.status_code == 404:
            raise NotFound404

        else:
            raise UnkownError(r.json()["description"])

    data = r.json()
    data["req"] = req
    del r
    return data


def make_post(method, toke, chat_id, photo=None, voice=None, document=None, certificate=None, caption=None, reply_to_message_id=None):
    url = base_url + toke + "/" + method
    if chat_id:
        url += "?chat_id=" + str(chat_id)

    files = None

    if photo:
        files = {"photo": photo}

    if voice:
        files = {"voice": voice}

    if document:
        files = {"document": document}

    if certificate:
        files = {"certificate": certificate}

    if not files:
        return

    if reply_to_message_id: url += get_symbol(url) + "reply_to_message_id=%s" % reply_to_message_id
    if caption:
        url += get_symbol(url) + "caption=%s" % caption
    try:
        r = requests.post(url, files=files)

        if r.status_code != 200:
            if "rights" in r.json()["description"]:
                raise NotEnoughtRights

            if r.status_code == 403:
                raise Unauthorized

            else:
                raise UnkownError(r.json()["description"])
        return r.json()["result"]
    except Exception as err:
        Log.e(url)
        Log.e(err)


def getUserPhoto(toke, user_id):
    # getUserProfilePhotos
    res = make_request("getUserProfilePhotos", toke, user_id=user_id)["result"]

    try:
        file_id = res["photos"][0][2]["file_id"]
    except Exception as err:
        Log.e("Non è stato possibile recuperare l'immagine di profilo di %s: %s" % (user_id, err))
        file_id = None
    return file_id


def getChatPhoto(toke, chat_id):
    x = io.BytesIO()
    res = make_request("getChat", toke, chat_id=chat_id)["result"]

    try:
        if "photo" not in res:
            Log.d("Chat %s probably has no photo" % chat_id)
            return None

        file_id = res["photo"]["big_file_id"]
        if not file_id:
            Log.d("Non è stato possibile recuperare la propic")
            return None

        x = getFile(toke, file_id, out=x)
        x.seek(0)
        return x
    except Exception as err:
        Log.e("Non è stato possibile recuperare l'immagine di profilo di %s: %s" % (chat_id, err))
        file_id = None

    return file_id


def kickChatMember(toke, chat_id, user_id, until=None):
    if until:
        if until not in bans:
            Log.d("Invalid kick time")
            raise InvalidKickTime(until)

        until = time.time() + bans[until]

    return make_request("kickChatMember", toke, chat_id=chat_id,
                        user_id=user_id,
                        until_date=until)["result"]


def pinMessage(infos, disable_notification=True):
    if not infos.is_reply: raise NoQuotedMessage
    res = make_request("pinChatMessage", infos.token, chat_id=infos.cid, message_id=infos.to_user.message.id,
                       disable_notification=disable_notification)
    return res


def unpinMessage(infos): return make_request("unpinChatMessage", infos.token, chat_id=infos.cid)


def getInviteLink(infos, chat_id=None):
    return make_request("exportChatInviteLink", infos.token, chat_id=infos.cid if not chat_id else chat_id)["result"]


def setChatTitle(infos):
    if not infos.is_reply: raise NoQuotedMessage
    return make_request("setChatTitle", infos.token, chat_id=infos.cid, title=infos.to_user.message.text)


def setChatDesc(infos):
    if not infos.is_reply: raise NoQuotedMessage
    return make_request("setChatDescription", infos.token, chat_id=infos.cid, description=infos.to_user.message.text)


def setChatPhoto(infos):
    if not infos.is_reply: raise NoQuotedMessage
    return make_post("setChatPhoto", infos.token, infos.cid,
                     photo=getFile(infos.token, file_id=infos.to_user.message.item_id, out=io.BytesIO().seek(0)))


def getChatAdministrators(toke, chat_id):
    return make_request("getChatAdministrators", toke, chat_id=chat_id)["result"]


def getChatMember(toke, chat_id, user_id):
    return make_request("getChatMember", toke, chat_id=chat_id, user_id=user_id)


def splitword(w):
    split = -((-len(w))//2)
    return [w[:split], w[split:]]


def sendMessage(toke, chat_id, text, reply_to_message_id=None, parse_mode=None, disable_web_page_preview=None, reply_markup=None):
    if len(quote(text)) > 4000:
        for part in splitword(text):
            if parse_mode:
                if part.count("*") % 2 != 0:
                    part += "*"
                if part.count("`") % 2 != 0:
                    part += "`"
            sendMessage(toke, chat_id, part, reply_to_message_id=reply_to_message_id,
                        parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview)
    else:
        return make_request("sendMessage",
                            toke,
                            text=text,
                            chat_id=chat_id,
                            reply_to_message_id=reply_to_message_id,
                            parse_mode=parse_mode, disable_web_page_preview=disable_web_page_preview,
                            reply_markup=reply_markup)["result"]
    return


def restrictChatMember(toke, chat_id, user_id,
                       can_send_messages=True,
                       can_send_media_messages=True,
                       can_send_other_messages=True,
                       can_add_web_page_previews=True):

    return make_request("restrictChatMember", toke,
                        chat_id=chat_id,
                        user_id=user_id,
                        can_send_messages=can_send_messages,
                        can_send_media_messages=can_send_media_messages,
                        can_send_other_messages=can_send_other_messages,
                        can_add_web_page_previews=can_add_web_page_previews)["result"]


def leaveChat(toke, chat_id):
    Unreloaded.gbots[str(chat_id)].remove(int(toke.split(":")[0]))
    return make_request("leaveChat", toke, chat_id=chat_id)


def sendVoice(toke, chat_id, file_id, reply_to_message_id=None, caption=None):
    return make_post("sendVoice", toke, chat_id, voice=getFile(toke, file_id),
                     reply_to_message_id=reply_to_message_id, caption=caption)


def sendSticker(toke, chat_id, sticker=None, reply_to_message_id=None):
    make_request("sendSticker",
                 toke,
                 sticker=sticker,
                 chat_id=chat_id,
                 reply_to_message_id=reply_to_message_id)


def sendPhoto(toke, chat_id, photo, caption=None, reply_to_message_id=None):
    if isinstance(photo, io.BytesIO):
        way = make_post
    else:
        way = make_request
    return way("sendPhoto", toke,
               chat_id=chat_id,
               photo=photo,
               reply_to_message_id=reply_to_message_id,
               caption=caption)


def sendVideo(toke, chat_id, video, caption=None, reply_to_message_id=None):
    return make_request("sendVideo", toke,
                        chat_id=chat_id,
                        reply_to_message_id=reply_to_message_id,
                        video=video, caption=caption)


def sendDocument(toke, chat_id, document, caption=None, reply_to_message_id=None):
    return make_request("sendDocument", toke,
                        chat_id=chat_id,
                        reply_to_message_id=reply_to_message_id,
                        document=document,
                        caption=caption)


def sendFileDocument(toke, chat_id, document_path, caption=None, reply_to_message_id=None):
    return make_post("sendDocument", toke,
                     chat_id=chat_id,
                     reply_to_message_id=reply_to_message_id,
                     document=open(document_path),
                     caption=caption)


def sendPhotoFile(toke, chat_id, photo, caption=None, reply_to=None):
    return make_post("sendPhoto", toke, chat_id=chat_id, photo=photo,
                     caption=caption, reply_to_message_id=reply_to)


def sendChatAction(toke, chat_id, action): return make_request("sendChatAction", toke, chat_id=chat_id, action=action)


def getFileName(toke, file_id): return make_request("getFile", toke, file_id=file_id)["result"]["file_path"].split("/")[1]


def getFile(toke, file_id,  out=None, file_path=None):
    if not out:
        out = io.BytesIO()
    if not file_path:
        file_path = make_request("getFile", toke, file_id=file_id)["result"]["file_path"]
    x = requests.get("https://api.telegram.org/file/bot%s/%s" % (toke, file_path), stream=True)  # .json()["result"]
    if x.status_code == 200:
        x.raw.decode_content = True
        shutil.copyfileobj(x.raw, out)
    else:
        Log.w("Status code non valido %s" % x.status_code)
        return None
    del x
    out.seek(0)
    return out


def unbanChatMember(toke, chat_id, user_id):
    return make_request("unbanChatMember", toke, chat_id=chat_id, user_id=user_id)


def getMe(toke):
    bot = make_request("getMe", toke)
    if not bot:
        return None
    bot = bot["result"]

    bot["token"] = toke
    return bot


def getChat(toke, chat_id):
    return make_request("getChat", toke, chat_id=chat_id)


def setWebhook(toke, certfile, port=8443):
    return make_post("setWebhook?url=https://35.195.192.65:%s/%s" % (port, toke), toke, None, certificate=open(certfile, "rb"))


def deleteWebhook(toke):
    return make_request("deleteWebhook", toke)


def getUpdates(toke, offset=None, timeout=None): return make_request("getUpdates", toke, offset=offset, timeout=timeout)["result"]


def editMessageText(toke, chat_id=None, message_id=None, text=None, parse_mode=None):
    return make_request("editMessageText", toke, chat_id=chat_id,
                        message_id=message_id, text=text, parse_mode=parse_mode)


def deleteMessage(toke, chat_id=None, message_id=None):
    return make_request("deleteMessage", toke, chat_id=chat_id, message_id=message_id)