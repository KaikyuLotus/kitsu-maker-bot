import requests
from Core.Settings import *


class BaseError(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class LastFMError(BaseError):
    def __init__(self, url, message, status_code):
        self.message = message
        self.url = url
        self.status_code = status_code


class NicknameError(BaseError):
    def __init__(self, url, message, status_code):
        self.message = message
        self.url = url
        self.status_code = status_code


class ResponseError(BaseError):
    def __init__(self, message):
        self.message = message


class UnregistredUser(BaseError):
    def __init__(self):
        self.message = "You're not registred!"


class UnvalidUsername(BaseError):
    def __init__(self, username):
        self.message = "%s is not a valid username!" % username


class EmptyTracks(BaseError):
    def __init__(self):
        self.message = "Questo utente non ha ascoltato nulla recentemente..."


class LastFM:
    def __init__(self, user_id):
        self._key = "&api_key=" + lastfm_token
        self._url = "http://ws.audioscrobbler.com/2.0/?"
        self._final = "&format=json&limit=1"
        self._method = "method=user.getrecenttracks"
        self.nickname = None
        self._data = None
        self._get_nickname(user_id)
        self._get_data()
        self._check_user()
        if not self._data['recenttracks']['track']:
            raise EmptyTracks()

    def _get_nickname(self, user_id):
        if isinstance(user_id, str):
            self.nickname = user_id
            return

        raise UnregistredUser()

    def _check_user(self):
        if "message"in self._data:
            if self._data['message'] == "User not found":
                raise UnvalidUsername(self.nickname)
            else:
                raise ResponseError(self._data['message'])
        return True

    def _get_data(self):
        url = self._url + self._method + "&user=" + self.nickname + self._key + self._final
        req = requests.get(url)
        if req.status_code != 200:
            raise LastFMError(url, req.text, req.status_code)
        self._data = req.json()

    def title(self):
        return self._data['recenttracks']['track'][0]['name']

    def artist(self):
        return self._data['recenttracks']['track'][0]['artist']['#text']

    def album(self):
        return self._data['recenttracks']['track'][0]['album']['#text']

    def image(self):
        return self._data['recenttracks']['track'][0]['image'][3]["#text"]

    def np(self):
        if "@attr" in self._data['recenttracks']['track'][0]:
            if "nowplaying" in self._data['recenttracks']['track'][0]['@attr']:
                if self._data['recenttracks']['track'][0]['@attr']['nowplaying']:
                    return "sta ascoltando"
        return "ha ascoltato"
