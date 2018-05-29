# coding=utf-8

# Copyright (c) 2017 Kaikyu

import time
import inspect


def lt():
    return time.strftime("%H:%M:%S")


def call_elab(caller_foo):
    return caller_foo + (14 - len(caller_foo)) * " "


def printf(tipo, testo, foo):
    text = "[ %s ] %s - [from: %s] - %s" % (tipo, lt(), foo, testo)
    with open("Files/logging.txt", "a") as fl:
        fl.write(text + "\n")
    print(text)
    return True


def printe(text):
    with open("Files/errors.txt", "a") as fl:
        fl.write(text + "\n")
        fl.close()
    print(text)


def d(text):
    printf("Debug ", text, call_elab(inspect.stack()[1][3]))


def i(text):
    printf("Info  ", text, call_elab(inspect.stack()[1][3]))


def a(text):
    printf("Action", text, call_elab(inspect.stack()[1][3]))


def w(text):
    printf("Warn  ", text, call_elab(inspect.stack()[1][3]))


def e(text):
    text = str(text)
    printe("[ Error  ] %s - [from: %s] - Errore: %s line: ~%s" % (lt(), call_elab(inspect.stack()[1][3]), text,
                                                                  inspect.getframeinfo(inspect.stack()[1][0]).lineno))
    return False


def critical(text, shutdown=True):
    text = str(text)
    printe("[CRITICAL] %s - [from: %s] - Errore critico: %s line: ~%s" % (lt(), call_elab(inspect.stack()[1][3]), text,
                                                                          inspect.getframeinfo(
                                                                              inspect.stack()[1][0]).lineno))
    if shutdown:
        exit()
