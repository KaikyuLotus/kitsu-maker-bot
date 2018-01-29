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

import json

import schedule as schedule
import time
import re
import sqlite3

from Utils import Logger as Log
from random import choice as cho
from random import randint

from LowLevel.LowLevel import read
from requests import get
from telegram.ext import Updater


def escape_markdown(text):
    """Helper function to escape telegram markup symbols"""
    escape_chars = '\*_`\[\]'
    return re.sub(r'([%s])' % escape_chars, r'\\\1', text)


uni = None
kaID = 52962566
kaikey = "254429240:AAGUHkP9qL2AGopUANN8YHkyyVmLgsB8Vfc"

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


def composer(nome, citta, lang):
    try:
        baseurl = "https://query.yahooapis.com/v1/public/yql?q="
        yql_query = "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='%s, it') and u='c' &format=json" % citta
        result = get(baseurl + yql_query)

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
        tramonto = str(int(tramonto.split(":")[0]) + 12) + ":" + tramonto.split(":")[1]

        forecast = datas["item"]["forecast"]
        temp_max = forecast[0]["high"]
        temp_min = forecast[0]["low"]
        day = days[forecast[0]["day"]]
        dayn = int(forecast[0]["date"].split()[0])
        desc = forecast[0]["text"].lower()

        try:
            desc = read("condizioni.json", 254429240)[desc]
        except:
            pass

        text = "Ohayou %s! %s\nEcco il meteo per *%s* di questa giornata %s\n\n" % (
                                                                                    escape_markdown(nome),
                                                                                    escape_markdown(cho(mots)),
                                                                                    citta.capitalize(),
                                                                                    escape_markdown(cho(mots))
                                                                                    )
        text += "Probabilmente *%s*\n" % desc
        text += "Con temperatura variabile tra *%s*°C e *%s*°C circa! %s\n" % (temp_min, temp_max, escape_markdown(cho(mots)))
        text += "\n\nIl sole sorgerà alle *%s* e tramonterà alle *%s* %s" % (alba, tramonto, escape_markdown(cho(mots)))
        text += "\nLa velocità del vento sarà di *%s* verso *%s* quindi *%s* ~\nL'umidità sarà al *%s* circa! %s" % (
            vel_vento, card[dir_vento][0], card[dir_vento][1], umidita, escape_markdown(cho(mots)))
        # text += "\n\nBuona gior*nya*ta ~ ♥"
        text += "\n\nBuona gior*nya*ta ~ ♥"
        return text

    except Exception as err:
        Log.e(err)
        return None


def meteo_b():
    bot = Updater(kaikey).bot
    schedule.every().day.at("06:30").do(m_sender, bot)
    while True:
        schedule.run_pending()
        time.sleep(5)


def get_reg_users(entity):
    try:
        conn = sqlite3.connect('files/%s/ProDB.db' % entity)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE city IS NOT NULL')
        got = c.fetchall()
        c.close()
        conn.close()
        return got
    except Exception as err:
        Log.e(err)
        return False


def m_sender(bot):
    global uni
    try:
        if not uni:
            uni = randint(100, 10000)
        else:
            return
        unreg = json.loads(open("jsons/unregistered.json").read())

        for user in get_reg_users(bot.id):
            if user[0] in unreg: continue
            try:
                x = composer(user[2], user[4], user[6])
                if x:
                    bot.sendMessage(chat_id=user[0], text=x, parse_mode="markdown")
                    Log.a("Meteo mattutino inviato a %s!" % user[2])
                time.sleep(0.3)
            except Exception as err:
                Log.w("Meteo non inviato a %s per: %s" % (user[2], err))

    except Exception as err:
        Log.e(err)
