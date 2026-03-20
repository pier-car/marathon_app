import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'maratona.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def inizializza_db():
    conn = get_db()
    c = conn.cursor()

    # Tabella Allenamenti
    c.execute('''CREATE TABLE IF NOT EXISTS allenamenti
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data DATE NOT NULL,
                  km REAL NOT NULL,
                  durata_minuti REAL,
                  passo_min_km REAL,
                  tipo TEXT NOT NULL,
                  fc_media INTEGER,
                  fc_max INTEGER,
                  cadenza INTEGER,
                  calorie INTEGER,
                  note TEXT,
                  sorgente TEXT DEFAULT 'manuale')''')

    # Tabella Dati Biometrici (Galaxy Watch / manuale)
    c.execute('''CREATE TABLE IF NOT EXISTS dati_biometrici
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data DATE NOT NULL,
                  ora TIME,
                  fc_riposo INTEGER,
                  hrv REAL,
                  spo2 REAL,
                  temperatura_corporea REAL,
                  stress_level INTEGER,
                  ore_sonno REAL,
                  qualita_sonno INTEGER,
                  passi INTEGER,
                  calorie_giornaliere INTEGER,
                  sorgente TEXT DEFAULT 'manuale')''')

    # Tabella Misurazioni Corporee
    c.execute('''CREATE TABLE IF NOT EXISTS misurazioni_corporee
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data DATE NOT NULL,
                  peso REAL,
                  grasso_corporeo REAL,
                  massa_muscolare REAL,
                  massa_ossea REAL,
                  acqua_corporea REAL,
                  bmi REAL,
                  circonferenza_vita REAL,
                  circonferenza_fianchi REAL,
                  note TEXT)''')

    # Tabella Integrazione / Nutrizione
    c.execute('''CREATE TABLE IF NOT EXISTS salute
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data DATE NOT NULL,
                  peso REAL,
                  proteine_gr INTEGER,
                  carboidrati_gr INTEGER,
                  grassi_gr INTEGER,
                  calorie_assunte INTEGER,
                  acqua_litri REAL,
                  creatina_preso BOOLEAN DEFAULT 0,
                  note TEXT)''')

    # Migrazione: aggiungi colonne mancanti alle tabelle esistenti
    _migrate_table(c, 'allenamenti', {
        'durata_minuti': 'REAL',
        'fc_media': 'INTEGER',
        'fc_max': 'INTEGER',
        'cadenza': 'INTEGER',
        'calorie': 'INTEGER',
        'note': 'TEXT',
        'sorgente': "TEXT DEFAULT 'manuale'"
    })

    _migrate_table(c, 'salute', {
        'carboidrati_gr': 'INTEGER',
        'grassi_gr': 'INTEGER',
        'calorie_assunte': 'INTEGER',
        'acqua_litri': 'REAL',
        'note': 'TEXT',
        'proteine_prese': 'BOOLEAN DEFAULT 0',
    })

    conn.commit()
    conn.close()


def _migrate_table(cursor, table, columns):
    """Aggiunge colonne mancanti a una tabella esistente."""
    cursor.execute(f"PRAGMA table_info({table})")
    existing = {row[1] for row in cursor.fetchall()}
    for col_name, col_type in columns.items():
        if col_name not in existing:
            cursor.execute(
                f"ALTER TABLE {table} ADD COLUMN {col_name} {col_type}"
            )


if __name__ == "__main__":
    inizializza_db()
    print("Database pronto per la missione 19 Aprile - Maratona di Torino!")