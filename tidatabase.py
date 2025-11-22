import sqlite3

class TI_Adatbazis:
    def __init__(self):
        self.db_nev = "ti_analyzer.db"
        self.TI_init_db()

    def TI_dbconnect(self):
        return sqlite3.connect(self.db_nev)

    def TI_init_db(self):
        conn = self.TI_dbconnect()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS elemzesek (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                description TEXT,
                relev_desc INT,
                relev_keys INT,
                load_time REAL,
                datum TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS kulcsszavak (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                elemzes_id INT,
                szo TEXT,
                db INT,
                FOREIGN KEY(elemzes_id) REFERENCES elemzesek(id)
            )
        """)

        conn.commit()
        conn.close()

    def TI_mentes_eredmeny(self, eredmeny):
        conn = self.TI_dbconnect()
        cur = conn.cursor()


        cur.execute("""
            INSERT INTO elemzesek (url, title, description, relev_desc, relev_keys, load_time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            eredmeny.url,
            eredmeny.title,
            eredmeny.description,
            eredmeny.relev_desc,
            eredmeny.relev_keys,
            eredmeny.load_time
        ))

        elemzes_id = cur.lastrowid


        for szo, db in eredmeny.szoveg_kulcs.most_common(50):
            cur.execute("""
                INSERT INTO kulcsszavak (elemzes_id, szo, db)
                VALUES (?, ?, ?)
            """, (elemzes_id, szo, db))

        conn.commit()
        conn.close()

    def TI_leker_utolso(self, limit=10):
        conn = self.TI_dbconnect()
        cur = conn.cursor()

        cur.execute("""
            SELECT id, url, title, description, relev_desc, relev_keys, load_time, datum
            FROM elemzesek
            ORDER BY id DESC
            LIMIT ?
        """, (limit,))

        adat = cur.fetchall()
        conn.close()
        return adat

    def TI_leker_kulcsszavak(self, elemzes_id):
        conn = self.TI_dbconnect()
        cur = conn.cursor()

        cur.execute("""
            SELECT szo, db FROM kulcsszavak
            WHERE elemzes_id = ?
        """, (elemzes_id,))

        adat = cur.fetchall()
        conn.close()
        return adat
