import sqlite3
import Utils.Logger as Log

_table_utenti = 'CREATE TABLE IF NOT EXISTS utenti('\
                '    ID INTEGER NOT NULL,'          \
                '    username TEXT (20),'           \
                '    name TEXT (20),'               \
                '    date DATE,'                    \
                '    city TEXT (15),'               \
                '    ext2 TEXT (40),'               \
                '    ext3 TEXT (40),'                \
                '    PRIMARY KEY (ID))'

_tables = {"utenti": {"construct": _table_utenti,
                      "elements": ["ID", "username", "name", "date", "city", "ext2", "ext3"]
                      }
           }


class DB:
    def __init__(self, db_name):
        self.dbname = db_name + ".db"
        self.connection = None
        self.cursor = None
        self._connect()

    def _connect(self):
        self.connection = sqlite3.connect(self.dbname)
        self._load_cursor()

        for table in _tables:
            self.cursor.execute(_tables[table]["construct"])

        self.connection.commit()
        self.cursor.close()

    def _load_cursor(self):
        self.cursor = self.connection.cursor()

    def _execute(self, query, fetch=False):
        result = None
        self._load_cursor()
        self.cursor.execute(query)
        if fetch:
            result = self.cursor.fetchall()
        self.connection.commit()
        self.cursor.close()
        return result

    def read(self, table_name, from_id=None, obj=None):
        if table_name not in _tables:
            Log.w("Tabella non riconosciuta, attenzione.")
        else:
            if obj:
                if obj not in _tables[table_name]["elements"]:
                    return Log.e("%s non fa parte della tabella %s, ritorno." % (obj, table_name))
        if not obj:
            obj = "*"

        #  print("SELECT %s FROM %s WHERE id = %s" % (obj, table_name, from_id))
        query = "SELECT %s FROM %s" % (obj, table_name)
        if from_id:
            query += " WHERE id = %s" % from_id

        return self._execute(query, fetch=True)

    def new(self, table_name, objs, values):
        if table_name not in _tables:
            Log.w("Tabella non riconosciuta, attenzione.")
        if not isinstance(objs, tuple) or not isinstance(values, tuple):
            return Log.e("add_info richiede dei tuple come parametri!")

        #  print("INSERT INTO %s %s VALUES %s" % (table_name, objs, values))
        self._execute("INSERT INTO %s %s VALUES %s" % (table_name, objs, values))

    def update(self, table_name, dic, from_id):
        if table_name not in _tables:
            Log.w("Tabella non riconosciuta, attenzione.")
        if not isinstance(dic, dict):
            return "E' necessario un dict con tutti i valori da aggiornare."
        set_string = ""
        for obj in dic:
            set_string += "%s = '%s', " % (obj, dic[obj])
        set_string = set_string[:-2]
        self._execute("UPDATE %s SET %s WHERE ID = %s" % (table_name, set_string, from_id))


if __name__ == "__main__":
    db = DB("test")
    db.new("utenti",                            # Aggiungiamo un nuovo utente
           ("ID", "name", "username", "ext2"),  # Nel primo tuple mettiamo i nomi delle colonne
           (5, "Luifd", "Kaikss", "Qualcosa"))  # Nel secondo mettiamo i valori da dare alle colonne, in ordine
    
    print(db.read("utenti",                     # Leggo da utenti
                  from_id=5                     # Richiedo esattamente l'ID 5
                  )[0])

    db.update("utenti",                         # Aggiorno i valori dalla tabella utenti
              {"username": "Kaikyu",            # Nel dict mettiamo tutto ciò che vogliamo aggiornare
               "name": "Luigi Nicoletti"},      # nel formato "nome colonna" -> valore
              5                                 # ID del quale aggiornare i dati
              )

    print(db.read("utenti",                     # Rileggo dalla tabella utenti
                  from_id=5,                    # Leggo i dati dell'utente con ID 5
                  obj="username")               # Richiedo il campo "username", se il campo non dovesse esistere
          [0])                                  # mi verrà segnalato senza creare eccezioni!
