# coding=utf-8

import sqlite3
from datetime import datetime


def get_connection(entity):
    dbname = "Files/bot_files/%s/bdb.db" % entity
    connessione = sqlite3.connect(dbname)
    cursore = connessione.cursor()
    cursore.execute(
         'CREATE TABLE IF NOT EXISTS groups(id INTEGER,'
         ' username TEXT, name TEXT, date TEXT, ext TEXT,'
         ' ext2 TEXT, ext3 TEXT)')

    cursore.execute(
        'CREATE TABLE IF NOT EXISTS stats(settimana INTEGER,'
        ' scorsa INTEGER, mese INTEGER, scorso INTEGER, ext TEXT,'
        ' ext2 TEXT, ext3 TEXT)')

    cursore.execute(
        'CREATE TABLE IF NOT EXISTS users(id INTEGER,'
        ' username TEXT, name TEXT, date TEXT, ext TEXT,'
        ' ext2 TEXT, ext3 TEXT)')

    cursore.execute(
        'CREATE TABLE IF NOT EXISTS datas(id INTEGER,'
        ' ext0 TEXT, ext1 TEXT, ext2 TEXT, ext3 TEXT,'
        ' ext4 TEXT, ext5 TEXT)')

    cursore.execute('SELECT settimana FROM stats')
    res = cursore.fetchall()

    if not res:
        cursore.execute("INSERT INTO stats (settimana, scorsa, mese, scorso) VALUES (?, ?, ?, ?)", (0, 0, 0, 0))

    connessione.commit()
    cursore.close()
    connessione.close()

    return sqlite3.connect(dbname)


def add_group(infos):
    if infos.chat_private:
        return

    idg = int(infos.cid)

    conn = get_connection(infos.entity)
    c = conn.cursor()
    c.execute('SELECT id FROM groups')
    allid = c.fetchall()

    if str(idg) not in str(allid).replace(",", " "):
        name = infos.name
        username = infos.group_username
        date = datetime.now().strftime('%d-%m %H:%M')
        c.execute("INSERT INTO groups (id, username, name, date) VALUES (?, ?, ?, ?)", (idg, username, name, date))
        conn.commit()
    else:
        return

    c.close()
    conn.close()


def add_user(infos):
    if not infos.chat_private:
        return False

    idu = int(infos.user.uid)
    conn = get_connection(infos.entity)
    c = conn.cursor()
    c.execute('SELECT id FROM users')
    allid = c.fetchall()

    if str(idu) not in str(allid).replace(",", " "):
        name = infos.user.name
        username = infos.user.username
        date = datetime.now().strftime('%d-%m %H:%M')
        c.execute("INSERT INTO users (id, username, name, date) VALUES (?, ?, ?, ?)", (idu, username, name, date))
        tor = True
        conn.commit()
    else:
        tor = False

    c.close()
    conn.close()
    return tor


def configure_bot_row(infos):
    conn = get_connection(infos.entity)
    c = conn.cursor()
    c.execute("INSERT INTO users (id, username, name, date) VALUES (?, ?, ?, ?)", (infos.entity,
                                                                                   infos.username,
                                                                                   infos.bot_name,
                                                                                   datetime.now().strftime('%d-%m %H:%M')))
    conn.commit()
    c.close()
    conn.close()


def execute(entity, command, *args):
    conn = get_connection(entity)
    c = conn.cursor()
    c.execute(command, *args)
    r = c.fetchall()
    conn.commit()
    c.close()
    conn.close()
    return r


def remove_id(entity, rmid):
    if int(rmid) < 0:
        thing = "groups"
    else:
        thing = "users"
    execute(entity, 'DELETE FROM %s WHERE id = (?)' % thing, (rmid,))


def set_obj(cid, value, obj, entity, where="groups"):
    # ext  = welcome 1 no 0/null si
    # ext2 = ?
    # ext3 = Bot admins
    if obj == "ext":
        execute(entity, 'UPDATE %s SET ext = (?) WHERE id = (?)' % where, (value, cid))
    elif obj == "ext2":
        execute(entity, 'UPDATE %s SET ext2 = (?) WHERE id = (?)' % where, (value, cid))
    elif obj == "ext3":
        execute(entity, 'UPDATE %s SET ext3 = (?) WHERE id = (?)' % where, (value, cid))


def read_obj(idg, entity, fro):
    infos = None
    try:
        infos = execute(entity, 'SELECT * FROM ' + fro + ' WHERE id = (?)', (idg,))[0]
        return {
                "id": infos[0], "name": infos[1], "username": infos[2], "date": infos[3],
                "ext": infos[4], "ext2": infos[5], "ext3": infos[6]
                }
    except IndexError:
        return {"id": None, "name": None, "username": None, "date": None, "ext": None, "ext2": None, "ext3": None, "real": infos}


def read_data(rid, entity, fro):
    infos = None
    try:
        infos = execute(entity, 'SELECT * FROM ' + fro + ' WHERE id = (?)', (rid,))
        if len(infos) == 0:
            execute(entity, "INSERT INTO datas (id, ext0, ext1, ext2, ext3, ext4, ext5) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (rid, None, None, None, None, None, None))
        infos = execute(entity, 'SELECT * FROM ' + fro + ' WHERE id = (?)', (rid,))
        infos = infos[0]
        return {
                "id": infos[0], "ext0": infos[1], "ext1": infos[2], "ext2": infos[3],
                "ext3": infos[4], "ext4": infos[5], "ext5": infos[6]
                }
    except IndexError as err:
        return {"id": None, "ext0": None, "ext1": None, "ext2": None,
                "ext3": None, "ext4": None, "ext5": None, "real": infos, "err": err}


def set_data(entity, uid, ext, value):
    infos = execute(entity, 'SELECT * FROM datas WHERE id = (?)', (uid,))
    if len(infos) == 0:
        execute(entity, "INSERT INTO datas (id, ext0, ext1, ext2, ext3, ext4, ext5) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (uid, None, None, None, None, None, None))
    execute(entity, 'UPDATE datas SET %s = (?) WHERE id = (?)' % ext, (value, uid))


def get_data(entity, what): return execute(entity, 'SELECT * FROM %s WHERE id IS NOT NULL' % what)


def get_groups_number(entity, user=False):
    if user:
        return len(execute(entity, 'SELECT id FROM users'))
    return len(execute(entity, 'SELECT id FROM groups'))
