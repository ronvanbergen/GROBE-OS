import os
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)
DB_PATH = os.environ.get('GROBE_DB_PATH', 'grobe_os.db')


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS stock_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        unit TEXT NOT NULL,
        quantity REAL NOT NULL DEFAULT 0,
        minimum REAL NOT NULL DEFAULT 0,
        updated_at TEXT NOT NULL
    )''')
    cur.execute('''CREATE TABLE IF NOT EXISTS movements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_code TEXT NOT NULL,
        change REAL NOT NULL,
        source TEXT NOT NULL,
        reference TEXT,
        created_at TEXT NOT NULL
    )''')
    cur.execute('SELECT COUNT(*) AS c FROM stock_items')
    if cur.fetchone()['c'] == 0:
        now = datetime.utcnow().isoformat()
        rows = [
            ('UNI-5L', 'Universol 5 liter', 'Gereed product', 'stuks', 1552, 800, now),
            ('UNI-1L', 'Universol 1 liter', 'Gereed product', 'stuks', 8640, 2000, now),
            ('UNI-600', 'Universol 600 ml spray', 'Gereed product', 'stuks', 1440, 720, now),
            ('UNI-TANK', 'Universol concentraat in tank', 'Tank', 'liter', 6300, 2000, now),
            ('MICHAEL-CAP', 'Productiecapaciteit Universol volgens Michael', 'Capaciteit', 'liter', 37800, 10000, now),
            ('BDG', 'Butyldiglycol', 'Grondstof', 'kg', 0, 500, now),
            ('AMPHOLAK', 'Ampholak', 'Grondstof', 'kg', 0, 500, now),
            ('KOH', 'KOH', 'Grondstof', 'kg', 0, 250, now),
            ('DISSOLVINE', 'Dissolvine', 'Grondstof', 'kg', 0, 250, now),
            ('NL8P4', 'ROKAnol NL8P4', 'Grondstof', 'kg', 0, 250, now),
            ('GA8W', 'ROKAnol GA8W', 'Grondstof', 'kg', 0, 250, now),
            ('NCS', 'Hoesch NCS', 'Grondstof', 'kg', 0, 250, now),
            ('DOOS-5L', 'Doos 4 x 5 liter', 'Verpakking', 'stuks', 1320, 300, now),
            ('TRIGGER-LB', 'Lichtblauwe trigger', 'Verpakking', 'stuks', 1200, 500, now),
            ('ETI-UNI-600', 'Etiket Universol 600 ml', 'Etiket', 'stuks', 1480, 500, now),
        ]
        cur.executemany('''INSERT INTO stock_items
            (code, name, category, unit, quantity, minimum, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)''', rows)
    conn.commit()
    conn.close()


def status_for(row):
    minimum = float(row['minimum'] or 0)
    qty = float(row['quantity'] or 0)
    if minimum <= 0:
        return {'label': 'Ruim voldoende', 'class': 'blue'}
    if qty <= minimum:
        return {'label': 'Bijna op', 'class': 'red'}
    if qty <= minimum * 2:
        return {'label': 'Bestellen', 'class': 'orange'}
    if qty <= minimum * 4:
        return {'label': 'Voldoende', 'class': 'light'}
    return {'label': 'Ruim voldoende', 'class': 'blue'}


@app.before_request
def before_request():
    init_db()


@app.get('/')
def dashboard():
    conn = db()
    items = [dict(r) for r in conn.execute('SELECT * FROM stock_items ORDER BY category, name').fetchall()]
    movements = [dict(r) for r in conn.execute('SELECT * FROM movements ORDER BY id DESC LIMIT 10').fetchall()]
    conn.close()
    for item in items:
        item['status'] = status_for(item)
    categories = {}
    for item in items:
        categories.setdefault(item['category'], []).append(item)
    return render_template('dashboard.html', categories=categories, movements=movements)


@app.get('/voorraad')
def voorraad():
    conn = db()
    items = [dict(r) for r in conn.execute('SELECT * FROM stock_items ORDER BY category, name').fetchall()]
    conn.close()
    for item in items:
        item['status'] = status_for(item)
    return render_template('voorraad.html', items=items)


@app.route('/mutatie', methods=['GET', 'POST'])
def mutatie():
    conn = db()
    if request.method == 'POST':
        item_code = request.form.get('item_code', '').strip()
        change = float(request.form.get('change') or 0)
        source = request.form.get('source', 'Handmatig').strip() or 'Handmatig'
        reference = request.form.get('reference', '').strip()
        now = datetime.utcnow().isoformat()
        cur = conn.cursor()
        cur.execute('SELECT quantity FROM stock_items WHERE code=?', (item_code,))
        row = cur.fetchone()
        if row:
            new_qty = float(row['quantity']) + change
            cur.execute('UPDATE stock_items SET quantity=?, updated_at=? WHERE code=?', (new_qty, now, item_code))
            cur.execute('INSERT INTO movements (item_code, change, source, reference, created_at) VALUES (?, ?, ?, ?, ?)',
                        (item_code, change, source, reference, now))
            conn.commit()
        conn.close()
        return redirect(url_for('voorraad'))
    items = [dict(r) for r in conn.execute('SELECT code, name FROM stock_items ORDER BY name').fetchall()]
    conn.close()
    return render_template('mutatie.html', items=items)


@app.route('/import', methods=['GET', 'POST'])
def import_page():
    message = None
    if request.method == 'POST':
        f = request.files.get('file')
        if f:
            message = f'Bestand ontvangen: {f.filename}. Inhoudelijke uitlezing volgt in de volgende module.'
        else:
            message = 'Geen bestand gekozen.'
    return render_template('import.html', message=message)


@app.get('/health')
def health():
    return jsonify({'status': 'ok', 'programma': 'GROBÉ OS', 'versie': '1.1-render'})


if __name__ == '__main__':
    port = int(os.environ.get('PORT', '8080'))
    app.run(host='0.0.0.0', port=port)
