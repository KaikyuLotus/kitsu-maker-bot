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
#

import time
import inspect
import sys


def lt(): return time.strftime("%H:%M:%S")


def call_elab(caller_foo): return caller_foo + (14 - len(caller_foo)) * " "


def printf(tipo, testo, foo):
    text = "[ %s ] %s - [from: %s] - %s" % (tipo, lt(), foo, testo)
    with open("Files/logging.txt", "a") as fl:
        fl.write(text + "\n")
    # if tipo == "Warn  ": return False
    return True


def printe(text):
    with open("Files/errors.txt", "a") as fl:
        fl.write(text + "\n")
        fl.close()


def d(text): printf("Debug ", text, call_elab(inspect.stack()[1][3]))


def i(text): printf("Info  ", text, call_elab(inspect.stack()[1][3]))


def a(text): printf("Action", text, call_elab(inspect.stack()[1][3]))


def w(text): printf("Warn  ", text, call_elab(inspect.stack()[1][3]))


def e(text):

    text = str(text)
    printe("[ Error  ] %s - [from: %s] - Errore: %s line: ~%s" % (lt(), call_elab(inspect.stack()[1][3]), text,
                                                                  inspect.getframeinfo(inspect.stack()[1][0]).lineno))
    return False
