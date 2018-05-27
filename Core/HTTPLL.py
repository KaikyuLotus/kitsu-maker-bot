# coding=utf-8

import io
import json
import shutil
import time
import requests

from urllib.parse import quote
from Utils import Logger as Log

from Core import Unreloaded
from Core.Error import InvalidKickTime, Unauthorized, NoQuotedMessage, UnkownError, NotEnoughtRights, BadRequest, \
    NotFound404

base_url = "https://api.telegram.org/bot"

bans = {"h12": 43200, "h10": 36000, "h8": 28800, "h4": 14400, "h2": 7200, "h1": 3600, "h0": 1800, "ever": 0}


def keyboard_btn(text, url):
    return [{"text": text, "url": url}]


def inline_keyboard(btns):
    return json.dumps({"inline_keyboard": btns})


def get_symbol(text):
    return "" if text.endswith("?") else "&"


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


def make_post(method, toke, chat_id, photo=None, voice=None, document=None, certificate=None, caption=None,
              reply_to_message_id=None):
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

    if reply_to_message_id:
        url += get_symbol(url) + "reply_to_message_id=%s" % reply_to_message_id
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


def get_user_photo(toke, user_id):
    # getUserProfilePhotos
    res = make_request("getUserProfilePhotos", toke, user_id=user_id)["result"]

    try:
        file_id = res["photos"][0][2]["file_id"]
    except Exception as err:
        Log.e("Non è stato possibile recuperare l'immagine di profilo di %s: %s" % (user_id, err))
        file_id = None
    return file_id


def get_chat_photo(toke, chat_id):
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


def kick_chat_member(toke, chat_id, user_id, until=None):
    if until:
        if until not in bans:
            Log.d("Invalid kick time")
            raise InvalidKickTime(until)

        until = time.time() + bans[until]

    return make_request("kickChatMember", toke, chat_id=chat_id,
                        user_id=user_id,
                        until_date=until)["result"]


def pin_message(infos, disable_notification=True):
    if not infos.is_reply:
        raise NoQuotedMessage
    res = make_request("pinChatMessage", infos.token, chat_id=infos.cid, message_id=infos.to_user.message.id,
                       disable_notification=disable_notification)
    return res


def unpin_message(infos): return make_request("unpinChatMessage", infos.token, chat_id=infos.cid)


def get_invite_link(infos, chat_id=None):
    return make_request("exportChatInviteLink", infos.token, chat_id=infos.cid if not chat_id else chat_id)["result"]


def set_chat_title(infos):
    if not infos.is_reply:
        raise NoQuotedMessage
    return make_request("setChatTitle", infos.token, chat_id=infos.cid, title=infos.to_user.message.text)


def set_chat_description(infos):
    if not infos.is_reply:
        raise NoQuotedMessage
    return make_request("setChatDescription", infos.token, chat_id=infos.cid, description=infos.to_user.message.text)


def set_chat_photo(infos):
    if not infos.is_reply:
        raise NoQuotedMessage
    return make_post("setChatPhoto", infos.token, infos.cid,
                     photo=getFile(infos.token, file_id=infos.to_user.message.item_id, out=io.BytesIO().seek(0)))


def get_chat_administrators(toke, chat_id):
    return make_request("getChatAdministrators", toke, chat_id=chat_id)["result"]


def get_chat_member(toke, chat_id, user_id):
    return make_request("getChatMember", toke, chat_id=chat_id, user_id=user_id)


def split_word(w):
    split = -((-len(w)) // 2)
    return [w[:split], w[split:]]


def send_message(toke, chat_id, text, reply_to_message_id=None, parse_mode=None, disable_web_page_preview=None,
                 reply_markup=None):
    if len(quote(text)) > 4000:
        for part in split_word(text):
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


def restrict_chat_member(toke, chat_id, user_id,
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


def leave_chat(toke, chat_id):
    Unreloaded.gbots[str(chat_id)].remove(int(toke.split(":")[0]))
    return make_request("leaveChat", toke, chat_id=chat_id)


def send_voice(toke, chat_id, file_id, reply_to_message_id=None, caption=None):
    return make_post("sendVoice", toke, chat_id, voice=getFile(toke, file_id),
                     reply_to_message_id=reply_to_message_id, caption=caption)


def send_sticker(toke, chat_id, sticker=None, reply_to_message_id=None):
    make_request("sendSticker",
                 toke,
                 sticker=sticker,
                 chat_id=chat_id,
                 reply_to_message_id=reply_to_message_id)


def send_photo(toke, chat_id, photo, caption=None, reply_to_message_id=None):
    if isinstance(photo, io.BytesIO):
        way = make_post
    else:
        way = make_request
    return way("sendPhoto", toke,
               chat_id=chat_id,
               photo=photo,
               reply_to_message_id=reply_to_message_id,
               caption=caption)


def send_video(toke, chat_id, video, caption=None, reply_to_message_id=None):
    return make_request("sendVideo", toke,
                        chat_id=chat_id,
                        reply_to_message_id=reply_to_message_id,
                        video=video, caption=caption)


def send_document(toke, chat_id, document, caption=None, reply_to_message_id=None):
    return make_request("sendDocument", toke,
                        chat_id=chat_id,
                        reply_to_message_id=reply_to_message_id,
                        document=document,
                        caption=caption)


def send_file_document(toke, chat_id, document_path, caption=None, reply_to_message_id=None):
    return make_post("sendDocument", toke,
                     chat_id=chat_id,
                     reply_to_message_id=reply_to_message_id,
                     document=open(document_path),
                     caption=caption)


def send_photo_file(toke, chat_id, photo, caption=None, reply_to=None):
    return make_post("sendPhoto", toke, chat_id=chat_id, photo=photo,
                     caption=caption, reply_to_message_id=reply_to)


def send_chat_action(toke, chat_id, action): return make_request("sendChatAction", toke, chat_id=chat_id, action=action)


def get_file_name(toke, file_id):
    return make_request("getFile", toke, file_id=file_id)["result"]["file_path"].split("/")[1]


def get_file(toke, file_id, out=None, file_path=None):
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


def unban_chat_member(toke, chat_id, user_id):
    return make_request("unbanChatMember", toke, chat_id=chat_id, user_id=user_id)


def get_me(toke):
    bot = make_request("getMe", toke)
    if not bot:
        return None
    bot = bot["result"]

    bot["token"] = toke
    return bot


def get_chat(toke, chat_id):
    return make_request("getChat", toke, chat_id=chat_id)


def set_webhook(toke, certfile, port=8443):
    return make_post("setWebhook?url=https://35.195.192.65:%s/%s" % (port, toke), toke, None,
                     certificate=open(certfile, "rb"))


def delete_webhook(toke):
    return make_request("deleteWebhook", toke)


def get_updates(toke, offset=None, timeout=None):
    return make_request("getUpdates", toke, offset=offset, timeout=timeout)["result"]


def edit_message_text(toke, chat_id=None, message_id=None, text=None, parse_mode=None):
    return make_request("editMessageText", toke, chat_id=chat_id,
                        message_id=message_id, text=text, parse_mode=parse_mode)


def delete_message(toke, chat_id=None, message_id=None):
    return make_request("deleteMessage", toke, chat_id=chat_id, message_id=message_id)


deleteMessage = delete_message
editMessageText = edit_message_text
getUpdates = get_updates
deleteWebhook = delete_webhook
setWebhook = set_webhook
getChat = get_chat
getMe = get_me
unbanChatMember = unban_chat_member
getFile = get_file
getFileName = get_file_name
sendChatAction = send_chat_action
sendPhotoFile = send_photo_file
sendFileDocument = send_file_document
sendDocument = send_document
sendVide = send_video
sendPhoto = send_photo
sendSticker = send_sticker
sendVoice = send_voice
sendVideo = send_video
leaveChat = leave_chat
restrictChatMember = restrict_chat_member
sendMessage = send_message
getChatMember = get_chat_member
getChatAdministrators = get_chat_administrators
setChatPhoto = set_chat_photo
setChatDescription = set_chat_description
setChatTitle = set_chat_title
getInviteLink = get_invite_link
unpinMessage = unpin_message
pinMessage = pin_message
kickChatMember = kick_chat_member
getChatPhoto = get_chat_photo
getUserPhoto = get_user_photo
