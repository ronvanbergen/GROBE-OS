import os
import sqlite3
from datetime import datetime
from pathlib import Path
from flask import Flask, jsonify, request, render_template_string, redirect, url_for

APP_VERSION = "1.0-render-flask"
DB_PATH = Path(os.environ.get("DATABASE_PATH", "grobe_os.db"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = db()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            unit TEXT NOT NULL,
            quantity REAL NOT NULL DEFAULT 0,
            minimum REAL NOT NULL DEFAULT 0,
            updated_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS movements (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_code TEXT NOT NULL,
            change REAL NOT NULL,
            source TEXT NOT NULL,
            reference TEXT,
            note TEXT,
            created_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS imports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filename TEXT NOT NULL,
            source TEXT NOT NULL,
            status TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    count = cur.execute("SELECT COUNT(*) AS c FROM items").fetchone()["c"]
    if count == 0:
        now = datetime.utcnow().isoformat()
        seed = [
            ("UNI-5L", "Universol 5 liter", "Gereed product", "stuks", 1552, 800, now),
            ("UNI-1L", "Universol 1 liter", "Gereed product", "stuks", 8640, 2000, now),
            ("UNI-600", "Universol 600 ml spray", "Gereed product", "stuks", 1440, 600, now),
            ("UNI-TANK", "Universol concentraat in tank", "Tank", "liter", 6300, 2000, now),
            ("MICHAEL-CAP", "Productiecapaciteit Universol volgens Michael", "Capaciteit", "liter", 37800, 10000, now),
            ("BDG", "Butyldiglycol", "Grondstof", "kg", 0, 500, now),
            ("AMPHOLAK", "Ampholak", "Grondstof", "kg", 0, 500, now),
            ("KOH", "KOH", "Grondstof", "kg", 0, 200, now),
            ("DISSOLVINE", "Dissolvine", "Grondstof", "kg", 0, 200, now),
            ("NL8P4", "ROKAnol NL8P4", "Grondstof", "kg", 0, 200, now),
            ("GA8W", "ROKAnol GA8W", "Grondstof", "kg", 0, 200, now),
            ("NCS", "Hoesch NCS", "Grondstof", "kg", 0, 200, now),
            ("DOOS-5L", "Doos 4 x 5 liter", "Verpakking", "stuks", 1320, 300, now),
            ("DOOS-1L", "Doos 12 x 1 liter", "Verpakking", "stuks", 1320, 300, now),
            ("TRIGGER-LB", "Lichtblauwe trigger", "Verpakking", "stuks", 1200, 500, now),
            ("ETI-UNI-600", "Etiket Universol 600 ml", "Etiket", "stuks", 1480, 600, now),
        ]
        cur.executemany(
            "INSERT INTO items (code, name, category, unit, quantity, minimum, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            seed,
        )
        cur.execute(
            "INSERT INTO movements (item_code, change, source, reference, note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("SYSTEM", 0, "seed", "start", "Startdata GROBÉ OS aangemaakt", now),
        )
    conn.commit()
    conn.close()


def status_for(row):
    q = float(row["quantity"])
    m = float(row["minimum"])
    if m <= 0:
        return {"label": "ruim voldoende", "color": "#2E3C7A"}
    if q <= m:
        return {"label": "bijna op", "color": "#D32F2F"}
    if q <= m * 2:
        return {"label": "bestellen", "color": "#F5A623"}
    if q <= m * 4:
        return {"label": "voldoende", "color": "#8FBCE7"}
    return {"label": "ruim voldoende", "color": "#2E3C7A"}


HTML = """
<!doctype html>
<html lang="nl">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>GROBÉ OS</title>
  <style>
    :root{--dark:#2E3C7A;--light:#8FBCE7;--orange:#F5A623;--red:#D32F2F;--bg:#F7F9FC;--line:#E4EAF2;--text:#2F3A45;--muted:#667085}
    *{box-sizing:border-box} body{margin:0;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;background:var(--bg);color:var(--text)}
    header{background:white;border-bottom:1px solid var(--line);padding:18px 28px;display:flex;align-items:center;justify-content:space-between;gap:14px;position:sticky;top:0;z-index:2}
    h1{font-size:24px;margin:0;color:var(--dark)} .small{font-size:13px;color:var(--muted)}
    nav a{display:inline-block;text-decoration:none;border:1px solid var(--line);border-radius:999px;padding:9px 14px;color:var(--dark);background:#fff;margin-left:6px}
    main{max-width:1180px;margin:0 auto;padding:24px}.grid{display:grid;grid-template-columns:1fr 1fr;gap:18px}.card{background:white;border:1px solid var(--line);border-radius:18px;padding:20px;box-shadow:0 8px 22px rgba(46,60,122,.06)}
    .full{grid-column:1/-1} h2{margin:0 0 14px;color:var(--dark);font-size:19px} table{width:100%;border-collapse:collapse}th,td{padding:12px 8px;border-bottom:1px solid var(--line);text-align:left}th{color:var(--muted);font-weight:600}.dot{width:14px;height:14px;border-radius:50%;display:inline-block;margin-right:8px;vertical-align:-2px}.pill{display:inline-block;padding:5px 9px;border-radius:999px;background:#F2F5FA;color:var(--muted);font-size:12px}button{background:var(--dark);color:white;border:0;border-radius:12px;padding:10px 14px;font-weight:700;cursor:pointer}input,select{padding:10px;border:1px solid var(--line);border-radius:10px;width:100%;margin:6px 0 12px} .ok{color:#19764b}.warn{color:#b42318}@media(max-width:800px){header{display:block}nav{margin-top:12px}.grid{grid-template-columns:1fr}.full{grid-column:auto}}
  </style>
</head>
<body>
<header>
  <div><h1>GROBÉ OS</h1><div class="small">Live basis · versie {{ version }}</div></div>
  <nav><a href="/">Dashboard</a><a href="/import">Import</a><a href="/movements">Mutaties</a><a href="/health">Health</a></nav>
</header>
<main>{{ body|safe }}</main>
</body>
</html>
"""


def page(body):
    return render_template_string(HTML, body=body, version=APP_VERSION)


@app.before_request
def before_request():
    init_db()


@app.get("/")
def dashboard():
    conn = db()
    rows = conn.execute("SELECT * FROM items ORDER BY category, name").fetchall()
    imports = conn.execute("SELECT * FROM imports ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    grouped = {}
    for r in rows:
        grouped.setdefault(r["category"], []).append(r)
    cards = []
    for cat, items in grouped.items():
        trs = "".join(
            f"<tr><td><span class='dot' style='background:{status_for(i)['color']}'></span>{i['name']}<br><span class='small'>{i['code']}</span></td><td>{i['quantity']:g} {i['unit']}</td><td><span class='pill'>{status_for(i)['label']}</span></td></tr>"
            for i in items
        )
        cards.append(f"<section class='card'><h2>{cat}</h2><table><tbody>{trs}</tbody></table></section>")
    import_rows = "".join(f"<tr><td>{x['filename']}</td><td>{x['source']}</td><td>{x['status']}</td><td>{x['message']}</td></tr>" for x in imports) or "<tr><td>Nog geen imports</td></tr>"
    body = "<div class='grid'>" + "".join(cards) + f"<section class='card full'><h2>Laatste imports</h2><table>{import_rows}</table></section></div>"
    return page(body)


@app.get("/import")
def import_page():
    body = """
    <section class='card'>
      <h2>Importcentrum</h2>
      <p class='small'>Deze basis ontvangt bestanden en logt ze. Inhoudelijke Daniel/Michael-uitlezing wordt hierna toegevoegd.</p>
      <form method='post' action='/import' enctype='multipart/form-data'>
        <label>Bron</label>
        <select name='source'><option>Daniel</option><option>Michael</option><option>Factuur</option><option>Overig</option></select>
        <label>Bestand</label>
        <input type='file' name='file' required>
        <button type='submit'>Uploaden</button>
      </form>
    </section>
    """
    return page(body)


@app.post("/import")
def import_file():
    uploaded = request.files.get("file")
    source = request.form.get("source", "Onbekend")
    if not uploaded:
        return redirect(url_for("import_page"))
    now = datetime.utcnow().isoformat()
    conn = db()
    conn.execute(
        "INSERT INTO imports (filename, source, status, message, created_at) VALUES (?, ?, ?, ?, ?)",
        (uploaded.filename, source, "ontvangen", "Bestand ontvangen. Parser nog niet gekoppeld.", now),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("dashboard"))


@app.get("/movements")
def movement_page():
    conn = db()
    rows = conn.execute("SELECT * FROM movements ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    trs = "".join(f"<tr><td>{r['created_at']}</td><td>{r['item_code']}</td><td>{r['change']:g}</td><td>{r['source']}</td><td>{r['note'] or ''}</td></tr>" for r in rows) or "<tr><td>Nog geen mutaties</td></tr>"
    return page(f"<section class='card'><h2>Voorraadmutaties</h2><table><tr><th>Datum</th><th>Artikel</th><th>Mutatie</th><th>Bron</th><th>Notitie</th></tr>{trs}</table></section>")


@app.get("/api/items")
def api_items():
    conn = db()
    rows = conn.execute("SELECT * FROM items ORDER BY category, name").fetchall()
    conn.close()
    return jsonify([{**dict(r), "status": status_for(r)} for r in rows])


@app.get("/health")
def health():
    return jsonify({"status": "ok", "programma": "GROBÉ OS", "version": APP_VERSION})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
