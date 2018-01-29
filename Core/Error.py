# coding=utf-8


class KitsuError(Exception):
    def __init__(self, m):
        self.message = m

    def __str__(self):
        return self.message


class InvalidKickTime(KitsuError):
    def __init__(self, until):
        super(InvalidKickTime, self).__init__('%s non è valido come kicktime' % until)


class Unauthorized(KitsuError):
    def __init__(self):
        self.message = "Non autorizzato."


class NoQuotedMessage(KitsuError):
    def __init__(self):
        self.message = "Nessun messaggio è stato quotato."


class UnkownError(KitsuError):
    def __init__(self, value):
        self.message = "Errore sconosciuto: %s" % value


class NotOkError(KitsuError):
    def __init__(self, value):
        self.message = "Richiesta non ok: %s" % value


class NotEnoughtRights(KitsuError):
    def __init__(self):
        self.message = "Il bot non ha abbastanza permessi."


class GeneralError(KitsuError):
    def __init__(self, desc):
        self.message = "Errore generico: %s" % desc


class BadRequest(KitsuError):
    def __init__(self, desc):
        self.message = "%s" % desc


class NotFound404(KitsuError):
    def __init__(self):
        self.message = "La risorsa richiesta non è stata trovata."


class ServerError(Exception):
    def __init__(self, message):
        super(ServerError, self).__init__()
        self.message = message

    def __str__(self):
        return '%s' % self.message


class TelegramError(Exception):
    def __init__(self, message):
        super(TelegramError, self).__init__()
        self.message = message

    def __str__(self):
        return '%s' % self.message
