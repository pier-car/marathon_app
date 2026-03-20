import os
import secrets
from datetime import date, datetime

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, jsonify, session
)

from database_manager import get_db, inizializza_db
from samsung_health_parser import (
    parse_samsung_health_exercise,
    parse_samsung_health_heart_rate,
    parse_samsung_health_sleep,
    parse_samsung_health_oxygen,
    parse_samsung_health_body_composition,
    parse_samsung_health_steps,
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

RACE_DATE = date(2026, 4, 19)
TARGET_PACE = 4.35  # min/km

# ---------- Inizializzazione ----------
inizializza_db()


# ---------- Auth ----------
PIN_CODE = os.environ.get('APP_PIN', 'pier2026')


@app.before_request
def require_login():
    allowed = ('login', 'static', 'sw_js', 'manifest_json')
    if request.endpoint not in allowed and not session.get('authenticated'):
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form.get('pin') == PIN_CODE:
            session['authenticated'] = True
            return redirect(url_for('index'))
        flash('PIN errato', 'error')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------- Dashboard ----------
@app.route('/')
def index():
    db = get_db()
    giorni_mancanti = (RACE_DATE - date.today()).days

    # Ultimi allenamenti
    allenamenti = db.execute(
        'SELECT * FROM allenamenti ORDER BY data DESC LIMIT 5'
    ).fetchall()

    # Statistiche
    stats = db.execute('''
        SELECT COUNT(*) as total,
               COALESCE(SUM(km), 0) as km_totali,
               COALESCE(AVG(passo_min_km), 0) as passo_medio,
               COALESCE(MAX(km), 0) as km_max
        FROM allenamenti
    ''').fetchone()

    # Km per settimana (ultime 8 settimane)
    km_settimanali = db.execute('''
        SELECT strftime('%Y-W%W', data) as settimana,
               SUM(km) as km
        FROM allenamenti
        WHERE data >= date('now', '-56 days')
        GROUP BY settimana
        ORDER BY settimana
    ''').fetchall()

    # Passo nel tempo
    passo_trend = db.execute('''
        SELECT data, passo_min_km
        FROM allenamenti
        WHERE passo_min_km IS NOT NULL
        ORDER BY data
    ''').fetchall()

    # Ultimo peso
    ultimo_peso = db.execute(
        'SELECT peso FROM misurazioni_corporee WHERE peso IS NOT NULL '
        'ORDER BY data DESC LIMIT 1'
    ).fetchone()

    # Ultima FC riposo
    ultima_fc = db.execute(
        'SELECT fc_riposo FROM dati_biometrici WHERE fc_riposo IS NOT NULL '
        'ORDER BY data DESC LIMIT 1'
    ).fetchone()

    db.close()
    return render_template(
        'index.html',
        giorni_mancanti=giorni_mancanti,
        race_date=RACE_DATE,
        target_pace=TARGET_PACE,
        allenamenti=allenamenti,
        stats=stats,
        km_settimanali=km_settimanali,
        passo_trend=passo_trend,
        ultimo_peso=ultimo_peso,
        ultima_fc=ultima_fc,
    )


# ---------- Allenamenti ----------
@app.route('/allenamenti')
def allenamenti():
    db = get_db()
    lista = db.execute(
        'SELECT * FROM allenamenti ORDER BY data DESC'
    ).fetchall()
    db.close()
    return render_template('allenamenti.html', allenamenti=lista)


@app.route('/allenamenti/nuovo', methods=['GET', 'POST'])
def nuovo_allenamento():
    if request.method == 'POST':
        db = get_db()
        km = float(request.form['km'])
        durata = request.form.get('durata_minuti')
        durata_val = float(durata) if durata else None
        passo = request.form.get('passo_min_km')
        if passo:
            passo_val = float(passo)
        elif durata_val and km > 0:
            passo_val = round(durata_val / km, 2)
        else:
            passo_val = None

        db.execute(
            '''INSERT INTO allenamenti
               (data, km, durata_minuti, passo_min_km, tipo,
                fc_media, fc_max, cadenza, calorie, note, sorgente)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'manuale')''',
            (
                request.form['data'],
                km,
                durata_val,
                passo_val,
                request.form['tipo'],
                request.form.get('fc_media') or None,
                request.form.get('fc_max') or None,
                request.form.get('cadenza') or None,
                request.form.get('calorie') or None,
                request.form.get('note') or None,
            )
        )
        db.commit()
        db.close()
        flash('Allenamento salvato!', 'success')
        return redirect(url_for('allenamenti'))
    return render_template('nuovo_allenamento.html', oggi=date.today())


@app.route('/allenamenti/elimina/<int:id>', methods=['POST'])
def elimina_allenamento(id):
    db = get_db()
    db.execute('DELETE FROM allenamenti WHERE id = ?', (id,))
    db.commit()
    db.close()
    flash('Allenamento eliminato', 'info')
    return redirect(url_for('allenamenti'))


# ---------- Dati Biometrici ----------
@app.route('/biometrici')
def biometrici():
    db = get_db()
    lista = db.execute(
        'SELECT * FROM dati_biometrici ORDER BY data DESC, ora DESC'
    ).fetchall()
    db.close()
    return render_template('biometrici.html', dati=lista)


@app.route('/biometrici/nuovo', methods=['GET', 'POST'])
def nuovo_biometrico():
    if request.method == 'POST':
        db = get_db()
        db.execute(
            '''INSERT INTO dati_biometrici
               (data, ora, fc_riposo, hrv, spo2, temperatura_corporea,
                stress_level, ore_sonno, qualita_sonno, passi,
                calorie_giornaliere, sorgente)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'manuale')''',
            (
                request.form['data'],
                request.form.get('ora') or None,
                request.form.get('fc_riposo') or None,
                request.form.get('hrv') or None,
                request.form.get('spo2') or None,
                request.form.get('temperatura_corporea') or None,
                request.form.get('stress_level') or None,
                request.form.get('ore_sonno') or None,
                request.form.get('qualita_sonno') or None,
                request.form.get('passi') or None,
                request.form.get('calorie_giornaliere') or None,
            )
        )
        db.commit()
        db.close()
        flash('Dati biometrici salvati!', 'success')
        return redirect(url_for('biometrici'))
    return render_template('nuovo_biometrico.html', oggi=date.today())


@app.route('/biometrici/elimina/<int:id>', methods=['POST'])
def elimina_biometrico(id):
    db = get_db()
    db.execute('DELETE FROM dati_biometrici WHERE id = ?', (id,))
    db.commit()
    db.close()
    flash('Dato eliminato', 'info')
    return redirect(url_for('biometrici'))


# ---------- Misurazioni Corporee ----------
@app.route('/misurazioni')
def misurazioni():
    db = get_db()
    lista = db.execute(
        'SELECT * FROM misurazioni_corporee ORDER BY data DESC'
    ).fetchall()
    db.close()
    return render_template('misurazioni.html', dati=lista)


@app.route('/misurazioni/nuovo', methods=['GET', 'POST'])
def nuova_misurazione():
    if request.method == 'POST':
        db = get_db()
        peso = request.form.get('peso')
        altezza_cm = request.form.get('altezza_cm')
        peso_val = float(peso) if peso else None
        bmi_val = None
        if peso_val and altezza_cm:
            altezza_m = float(altezza_cm) / 100
            if altezza_m > 0:
                bmi_val = round(peso_val / (altezza_m * altezza_m), 1)

        db.execute(
            '''INSERT INTO misurazioni_corporee
               (data, peso, grasso_corporeo, massa_muscolare, massa_ossea,
                acqua_corporea, bmi, circonferenza_vita,
                circonferenza_fianchi, note)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                request.form['data'],
                peso_val,
                request.form.get('grasso_corporeo') or None,
                request.form.get('massa_muscolare') or None,
                request.form.get('massa_ossea') or None,
                request.form.get('acqua_corporea') or None,
                bmi_val,
                request.form.get('circonferenza_vita') or None,
                request.form.get('circonferenza_fianchi') or None,
                request.form.get('note') or None,
            )
        )
        db.commit()
        db.close()
        flash('Misurazione salvata!', 'success')
        return redirect(url_for('misurazioni'))
    return render_template('nuova_misurazione.html', oggi=date.today())


@app.route('/misurazioni/elimina/<int:id>', methods=['POST'])
def elimina_misurazione(id):
    db = get_db()
    db.execute('DELETE FROM misurazioni_corporee WHERE id = ?', (id,))
    db.commit()
    db.close()
    flash('Misurazione eliminata', 'info')
    return redirect(url_for('misurazioni'))


# ---------- Nutrizione ----------
@app.route('/nutrizione')
def nutrizione():
    db = get_db()
    lista = db.execute(
        'SELECT * FROM salute ORDER BY data DESC'
    ).fetchall()
    db.close()
    return render_template('nutrizione.html', dati=lista)


@app.route('/nutrizione/nuovo', methods=['GET', 'POST'])
def nuova_nutrizione():
    if request.method == 'POST':
        db = get_db()
        db.execute(
            '''INSERT INTO salute
               (data, peso, proteine_gr, carboidrati_gr, grassi_gr,
                calorie_assunte, acqua_litri, creatina_preso, note)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (
                request.form['data'],
                request.form.get('peso') or None,
                request.form.get('proteine_gr') or None,
                request.form.get('carboidrati_gr') or None,
                request.form.get('grassi_gr') or None,
                request.form.get('calorie_assunte') or None,
                request.form.get('acqua_litri') or None,
                1 if request.form.get('creatina_preso') else 0,
                request.form.get('note') or None,
            )
        )
        db.commit()
        db.close()
        flash('Dati nutrizione salvati!', 'success')
        return redirect(url_for('nutrizione'))
    return render_template('nuova_nutrizione.html', oggi=date.today())


@app.route('/nutrizione/elimina/<int:id>', methods=['POST'])
def elimina_nutrizione(id):
    db = get_db()
    db.execute('DELETE FROM salute WHERE id = ?', (id,))
    db.commit()
    db.close()
    flash('Dato eliminato', 'info')
    return redirect(url_for('nutrizione'))


# ---------- Import Samsung Health ----------
ALLOWED_EXTENSIONS = {'csv'}
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB


def _allowed_file(filename):
    return (
        '.' in filename
        and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route('/importa', methods=['GET', 'POST'])
def importa():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('Nessun file selezionato', 'error')
            return redirect(url_for('importa'))

        file = request.files['file']
        if file.filename == '':
            flash('Nessun file selezionato', 'error')
            return redirect(url_for('importa'))

        if not _allowed_file(file.filename):
            flash('Formato non supportato. Usa file CSV.', 'error')
            return redirect(url_for('importa'))

        if file.content_length and file.content_length > MAX_CONTENT_LENGTH:
            flash('File troppo grande (max 16 MB)', 'error')
            return redirect(url_for('importa'))

        tipo_dato = request.form.get('tipo_dato', 'exercise')
        try:
            content = file.read().decode('utf-8', errors='replace')
        except (UnicodeDecodeError, MemoryError):
            flash('Errore nella lettura del file', 'error')
            return redirect(url_for('importa'))

        db = get_db()
        count = 0

        if tipo_dato == 'exercise':
            records = parse_samsung_health_exercise(content)
            for r in records:
                db.execute(
                    '''INSERT INTO allenamenti
                       (data, km, durata_minuti, passo_min_km, tipo,
                        fc_media, fc_max, cadenza, calorie, sorgente)
                       VALUES (?,?,?,?,?,?,?,?,?,?)''',
                    (r.get('data'), r.get('km'), r.get('durata_minuti'),
                     r.get('passo_min_km'), r.get('tipo', 'Corsa'),
                     r.get('fc_media'), r.get('fc_max'),
                     r.get('cadenza'), r.get('calorie'), 'galaxy_watch')
                )
                count += 1

        elif tipo_dato == 'heart_rate':
            records = parse_samsung_health_heart_rate(content)
            for r in records:
                db.execute(
                    '''INSERT INTO dati_biometrici
                       (data, ora, fc_riposo, sorgente)
                       VALUES (?,?,?,?)''',
                    (r.get('data'), r.get('ora'),
                     r.get('fc_riposo'), 'galaxy_watch')
                )
                count += 1

        elif tipo_dato == 'sleep':
            records = parse_samsung_health_sleep(content)
            for r in records:
                db.execute(
                    '''INSERT INTO dati_biometrici
                       (data, ore_sonno, qualita_sonno, sorgente)
                       VALUES (?,?,?,?)''',
                    (r.get('data'), r.get('ore_sonno'),
                     r.get('qualita_sonno'), 'galaxy_watch')
                )
                count += 1

        elif tipo_dato == 'oxygen':
            records = parse_samsung_health_oxygen(content)
            for r in records:
                db.execute(
                    '''INSERT INTO dati_biometrici
                       (data, ora, spo2, sorgente)
                       VALUES (?,?,?,?)''',
                    (r.get('data'), r.get('ora'),
                     r.get('spo2'), 'galaxy_watch')
                )
                count += 1

        elif tipo_dato == 'body_composition':
            records = parse_samsung_health_body_composition(content)
            for r in records:
                db.execute(
                    '''INSERT INTO misurazioni_corporee
                       (data, peso, grasso_corporeo, massa_muscolare,
                        acqua_corporea, bmi)
                       VALUES (?,?,?,?,?,?)''',
                    (r.get('data'), r.get('peso'),
                     r.get('grasso_corporeo'), r.get('massa_muscolare'),
                     r.get('acqua_corporea'), r.get('bmi'))
                )
                count += 1

        elif tipo_dato == 'steps':
            records = parse_samsung_health_steps(content)
            for r in records:
                db.execute(
                    '''INSERT INTO dati_biometrici
                       (data, passi, calorie_giornaliere, sorgente)
                       VALUES (?,?,?,?)''',
                    (r.get('data'), r.get('passi'),
                     r.get('calorie_giornaliere'), 'galaxy_watch')
                )
                count += 1

        db.commit()
        db.close()
        flash(f'{count} record importati con successo!', 'success')
        return redirect(url_for('importa'))

    return render_template('importa.html')


# ---------- API per grafici ----------
@app.route('/api/passo-trend')
def api_passo_trend():
    db = get_db()
    rows = db.execute(
        '''SELECT data, passo_min_km FROM allenamenti
           WHERE passo_min_km IS NOT NULL ORDER BY data'''
    ).fetchall()
    db.close()
    return jsonify({
        'labels': [r['data'] for r in rows],
        'values': [r['passo_min_km'] for r in rows],
    })


@app.route('/api/km-settimanali')
def api_km_settimanali():
    db = get_db()
    rows = db.execute(
        '''SELECT strftime('%Y-W%W', data) as sett, SUM(km) as km
           FROM allenamenti WHERE data >= date('now', '-56 days')
           GROUP BY sett ORDER BY sett'''
    ).fetchall()
    db.close()
    return jsonify({
        'labels': [r['sett'] for r in rows],
        'values': [round(r['km'], 1) for r in rows],
    })


@app.route('/api/peso-trend')
def api_peso_trend():
    db = get_db()
    rows = db.execute(
        '''SELECT data, peso FROM misurazioni_corporee
           WHERE peso IS NOT NULL ORDER BY data'''
    ).fetchall()
    db.close()
    return jsonify({
        'labels': [r['data'] for r in rows],
        'values': [r['peso'] for r in rows],
    })


@app.route('/api/fc-trend')
def api_fc_trend():
    db = get_db()
    rows = db.execute(
        '''SELECT data, AVG(fc_riposo) as fc FROM dati_biometrici
           WHERE fc_riposo IS NOT NULL GROUP BY data ORDER BY data'''
    ).fetchall()
    db.close()
    return jsonify({
        'labels': [r['data'] for r in rows],
        'values': [round(r['fc'], 0) for r in rows],
    })


# ---------- PWA ----------
@app.route('/sw.js')
def sw_js():
    return app.send_static_file('sw.js'), 200, {
        'Content-Type': 'application/javascript',
        'Service-Worker-Allowed': '/'
    }


@app.route('/manifest.json')
def manifest_json():
    return app.send_static_file('manifest.json'), 200, {
        'Content-Type': 'application/manifest+json'
    }


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)