# coding=utf-8

import sqlite3
from datetime import datetime
from Utils import Logger as Log


def getdbname(entity):
    try:
        return sqlite3.connect('Files/bot_files/%s/ProDB.db' % entity)
    except:
        Log.d("Questa entity (%s) non ha un ProDB" % entity)
        return None


def update_user(infos):
    try:
        idu = infos.user.uid
        name = infos.user.name
        username = str(infos.user.username)

        conn = getdbname(infos.entity)
        c = conn.cursor()
        c.execute("DELETE FROM users where id = (?)", (idu,))
        datas = read_obj(idu, infos.entity)
        date = datas["date"]
        fmnick = datas["fmnick"]
        city = datas["city"]
        sesso = datas["sesso"]
        lang = datas["lang"]
        if not username:
            c.execute("INSERT INTO users (id, name, date, city, fmnick, lang, sesso) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (idu, name, date, city, fmnick, lang, sesso))
        else:
            c.execute("INSERT INTO users (id, username, name, date, city, fmnick, lang, sesso) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (idu, username, name, date, city, fmnick, lang, sesso))
        conn.commit()
        c.close()
        conn.close()
    except Exception as err:
        Log.e(err)


def add_users(infos):
    try:

        idu = int(infos.user.uid)
        name = infos.user.name
        username = str(infos.user.username)
        conn = getdbname(infos.entity)
        c = conn.cursor()
        c.execute('SELECT id FROM users')
        allid = c.fetchall()
        date = datetime.now().strftime('%d-%m %H:%M')
        if str(idu) not in str(allid).replace(",", ""):
            if not username:
                c.execute("INSERT INTO users (id, name, date, city, fmnick, sesso) VALUES (?, ?, ?, ?, ?, ?)",
                          (idu, name, date, None, None, 0))
            else:
                c.execute("INSERT INTO users (id, username, name, date, city, fmnick, sesso) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (idu, username, name, date, None, None, 0))
        else:
            update_user(infos)
        conn.commit()
        c.close()
        conn.close()
    except Exception as err:
        Log.e(str(err))


def add_groups(infos):
    try:
        if infos.chat_private:
            return
        idg = int(infos.cid)
        name = infos.name
        username = None
        conn = getdbname(infos.entity)
        c = conn.cursor()
        c.execute('SELECT id FROM groups')
        allid = c.fetchall()
        date = datetime.now().strftime('%d-%m %H:%M')
        if str(idg) not in str(allid).replace(",", ""):
            if not username:
                c.execute("INSERT INTO groups (id, name, date) VALUES (?, ?, ?)", (idg, name, date))
            else:
                c.execute("INSERT INTO groups (id, username, name, date) VALUES (?, ?, ?, ?)",
                          (idg, username, name, date))
        else:
            pass
        conn.commit()
        c.close()
        conn.close()
    except Exception as err:
        Log.e(str(err))


def rem_group(idg, entity):
    try:
        conn = getdbname(entity)
        c = conn.cursor()
        c.execute('DELETE FROM groups WHERE id = (?)', (idg,))
        conn.commit()
        c.close()
        conn.close()
    except Exception as err:
        Log.e(str(err))


def add_objs(idu, value, obj, entity):
    try:
        conn = getdbname(entity)
        c = conn.cursor()
        if obj == "city": c.execute('UPDATE users SET city = (?) WHERE id = (?)', (value, idu))
        elif obj == "lastfm": c.execute('UPDATE users SET fmnick = (?) WHERE id = (?)', (value, idu))
        elif obj == "lang":
            c.execute('UPDATE users SET lang = (?) WHERE id = (?)', (value, idu))
            Log.d("Lang set to %s" % value)

        elif obj == "sesso": c.execute('UPDATE users SET sesso = (?) WHERE id = (?)', (value, idu))
        else:
            Log.e("%s non è un obj valido" % obj)
            return False
        conn.commit()
        c.close()
        conn.close()
        return True
    except Exception as err:
        Log.w(str(err))
        return False


def read_obj(idu, entity):
    try:
        conn = getdbname(entity)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE id = (?)', (idu,))
        infos = c.fetchall()
        uid = infos[0][0]
        username = infos[0][1]
        name = infos[0][2]
        date = infos[0][3]
        meteo = infos[0][4]
        lastfm = infos[0][5]
        lang = infos[0][6]
        sesso = infos[0][7]
        return {'id': uid, 'name': name, 'username': username,
                'fmnick': lastfm, 'city': meteo, 'lang': lang, 'date': date, 'sesso': sesso}
    except:
        return {'id': None, 'name': None, 'username': None,
                'fmnick': None, 'city': None, 'lang': None, 'date': None, 'sesso': None}


def read_group_obj(idg, entity):
    try:
        conn = getdbname(entity)

        c = conn.cursor()
        c.execute('SELECT * FROM groups WHERE id = (?)', (idg,))
        infos = c.fetchall()
        try:
            muted = infos[0][4]
            lang = infos[0][5]
        except Exception as err:
            lang = 0
            muted = 0
        return muted, lang
    except Exception as err:
        Log.e(str(err))
        return 0, 0


def get_last_group(entity):
    conn = getdbname(entity)
    c = conn.cursor()
    c.execute('SELECT * FROM groups WHERE id IS NOT NULL')
    got = c.fetchall()
    c.close()
    conn.close()
    return got[len(got)-1]


def set_group_obj(infos, obj, value):
    try:
        conn = getdbname(infos.entity)
        c = conn.cursor()
        if obj == "lang":
            c.execute('UPDATE groups SET lang = (?) WHERE id = (?)', (value, infos.cid))
        if obj == "muted":
            c.execute('UPDATE groups SET muted = (?) WHERE id = (?)', (value, infos.cid))
        conn.commit()
        c.close()
        conn.close()
        return True
    except Exception as err:
        Log.e(err)
        return False


def get_reg_users(entity):
    try:
        conn = getdbname(entity)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE city IS NOT NULL')
        got = c.fetchall()
        c.close()
        conn.close()
        return got
    except Exception as err:
        Log.e(err)
        return False


def get_groups_data(entity):
    try:
        conn = getdbname(entity)
        c = conn.cursor()
        c.execute('SELECT * FROM groups WHERE id IS NOT NULL')
        got = c.fetchall()
        c.close()
        conn.close()
        return got
    except Exception as err:
        Log.e(str(err))
        return False


def get_groups(entity):
    conn = getdbname(entity)
    c = conn.cursor()
    c.execute('SELECT id FROM groups')
    allid = c.fetchall()
    gruppi = len(allid)
    c.close()
    conn.close()
    return gruppi


def get_users(entity):
    conn = getdbname(entity)
    c = conn.cursor()
    c.execute('SELECT id FROM users')
    allid = c.fetchall()
    utenti = len(allid)
    c.close()
    conn.close()
    return utenti


def get_numbers(entity): return get_groups(entity), get_users(entity)


def get_objs_from_username(infos, username):
    try:
        conn = getdbname(infos.entity)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE lower(username) = (?)', (username.lower(),))
        infos = c.fetchall()
        uid = infos[0][0]
        username = infos[0][1]
        name = infos[0][2]
        date = infos[0][3]
        meteo = infos[0][4]
        lastfm = infos[0][5]
        lang = infos[0][6]
        sesso = infos[0][7]
        return {'id': uid, 'name': name, 'username': username,
                'fmnick': lastfm, 'city': meteo, 'lang': lang,
                'date': date, 'sesso': sesso}
    except:
        return {'id': None, 'name': None, 'username': None,
                'fmnick': None, 'city': None, 'lang': None,
                'date': None, 'sesso': None}


def get_similars_from_name(infos, username):
    try:
        conn = getdbname(infos.entity)
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE lower(name) LIKE (?)', ("%" + username.lower() + "%",))
        infos = c.fetchall()

        if len(infos) == 0: return "zero", None

        if len(infos) == 1:
            return "one", {'id': infos[0][0], 'name': infos[0][2], 'username': infos[0][1],
                           'fmnick': infos[0][5], 'city': infos[0][4], 'lang': infos[0][6],
                           'date': infos[0][3], 'sesso': infos[0][7]}
        ulist = []
        for elem in infos:
            uid = elem[0]
            username = elem[1]
            name = elem[2]
            date = elem[3]
            meteo = elem[4]
            lastfm = elem[5]
            lang = elem[6]
            sesso = elem[7]

            usr = {'id': uid, 'name': name, 'username': username,
                   'fmnick': lastfm, 'city': meteo, 'lang': lang,
                   'date': date, 'sesso': sesso}

            ulist.append(usr)
        return True, ulist

    except Exception as err:
        Log.e(err)
        return None, None
