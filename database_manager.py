import sqlite3

def inizializza_db():
    # Questo creerà il file maratona.db nella tua cartella
    conn = sqlite3.connect('maratona.db')
    c = conn.cursor()
    
    # Tabella Allenamenti - Focus sul passo target 4:35
    c.execute('''CREATE TABLE IF NOT EXISTS allenamenti
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data DATE,
                  km REAL,
                  passo_min_km REAL,
                  tipo TEXT)''')
    
    # Tabella Integrazione - Proteine e Creatina
    c.execute('''CREATE TABLE IF NOT EXISTS salute
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  data DATE,
                  peso REAL,
                  proteine_gr INTEGER,
                  creatina_preso BOOLEAN)''')
    
    conn.commit()
    conn.close()
    print("Database pronto per la missione 18 Aprile!")

if __name__ == "__main__":
    inizializza_db()