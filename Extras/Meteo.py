# coding=utf-8
import json

import requests


baseurl = "https://query.yahooapis.com/v1/public/yql?q="
part1 = "select * from weather.forecast where woeid in "
yql_query = part1 + "(select woeid from geo.places(1) where text='%s, it') and u='c' &format=json"


days = {"Mon": "Lunedì",
        "Tue": "Martedì",
        "Wed": "Mercoledì",
        "Thu": "Giovedì",
        "Fri": "Venerdì",
        "Sat": "Sabato",
        "Sun": "Domenica"}

card = {
        "0":   ["Nord", "Tramontana"],
        "45":  ["Grecale", "Nord-Est"],
        "90":  ["Est", "Levante"],
        "135": ["Sud-Est", "Scirocco"],
        "180": ["Sud", "Ostro/Mezzogiorno"],
        "225": ["Sud-Ovest", "Libeccio"],
        "270": ["Ovest", "Ponente"],
        "315": ["Nord-Ovest", "Maestrale"]
        }


def exists(citta):
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


def get_datas(citta):
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

    dir_vento, tipo_vento = card[dir_vento]

    alba = datas["astronomy"]["sunrise"].split()[0]
    alba = str(alba.split(":")[0]) + ":" + alba.split(":")[1].zfill(2)
    tramonto = datas["astronomy"]["sunset"].split()[0]
    tramonto = str(int(tramonto.split(":")[0]) + 12) + ":" + tramonto.split(":")[1].zfill(2)

    forecast = datas["item"]["forecast"]
    temp_max = forecast[0]["high"]
    temp_min = forecast[0]["low"]
    day = days[forecast[0]["day"]]
    dayn = int(forecast[0]["date"].split()[0])

    try:
        desc = json.loads(open("jsons/condizioni.json").read())[forecast[0]["text"].lower()]
    except:
        desc = forecast[0]["text"]

    datas = {
        "temp": str(temp_max),
        "giorno": str(day),
        "ngiorno":  str(dayn),
        "tramonto": str(tramonto),
        "alba": str(alba),
        "descrizione": desc,
        "umidita": str(umidita),
        "vel_vento": str(vel_vento),
        "dir_vento": dir_vento,
        "tipo_vento": tipo_vento
    }
    return datas
