import os
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from flask import Flask, jsonify, redirect, render_template, request, url_for
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = Path(os.getenv("GROBE_OS_DB", BASE_DIR / "grobe_os.db"))
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024


def db_connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with db_connect() as db:
        db.execute(
            """
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
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_code TEXT NOT NULL,
                change REAL NOT NULL,
                source TEXT NOT NULL,
                reference TEXT,
                note TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS imports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                source TEXT NOT NULL,
                status TEXT NOT NULL,
                message TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        seed_count = db.execute("SELECT COUNT(*) AS c FROM items").fetchone()["c"]
        if seed_count == 0:
            now = datetime.utcnow().isoformat()
            items = [
                ("UNI-5L", "Universol 5 liter", "Gereed product", "stuks", 1552, 800, now),
                ("UNI-1L", "Universol 1 liter", "Gereed product", "stuks", 8640, 2000, now),
                ("UNI-600", "Universol 600 ml spray", "Gereed product", "stuks", 1440, 500, now),
                ("UNI-TANK", "Universol concentraat in tank", "Tank", "liter", 6300, 2000, now),
                ("UNI-CAP-MICHAEL", "Productiecapaciteit Universol volgens Michael", "Capaciteit", "liter", 37800, 10000, now),
                ("BDG", "Butyldiglycol", "Grondstof", "kg", 0, 250, now),
                ("AMPHOLAK", "Ampholak YJH-40", "Grondstof", "kg", 0, 250, now),
                ("KOH", "KOH 50%", "Grondstof", "kg", 0, 250, now),
                ("DISSOLVINE", "Dissolvine", "Grondstof", "kg", 0, 250, now),
                ("NL8P4", "ROKAnol NL8P4", "Grondstof", "kg", 0, 250, now),
                ("GA8W", "GA8W", "Grondstof", "kg", 0, 250, now),
                ("NCS", "Hoesch NCS", "Grondstof", "kg", 0, 250, now),
                ("CAN-5L", "Jerrycan 5 liter", "Verpakking", "stuks", 1320, 500, now),
                ("DOOS-5L", "Doos 4 x 5 liter", "Doos", "stuks", 1320, 300, now),
                ("TRIGGER-LB", "Lichtblauwe trigger", "Verpakking", "stuks", 1200, 500, now),
                ("ETI-UNI-600", "Etiket Universol 600 ml", "Etiket", "stuks", 1480, 500, now),
            ]
            db.executemany(
                "INSERT INTO items (code, name, category, unit, quantity, minimum, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                items,
            )
        db.commit()


def status_for(quantity: float, minimum: float) -> dict[str, str]:
    if minimum <= 0:
        return {"key": "ok", "label": "Ruim voldoende", "color": "#2E3C7A"}
    if quantity <= minimum:
        return {"key": "critical", "label": "Bijna op", "color": "#D32F2F"}
    if quantity <= minimum * 2:
        return {"key": "order", "label": "Bestellen", "color": "#F5A623"}
    if quantity <= minimum * 4:
        return {"key": "enough", "label": "Voldoende", "color": "#8FBCE7"}
    return {"key": "ok", "label": "Ruim voldoende", "color": "#2E3C7A"}


def get_dashboard() -> dict[str, Any]:
    with db_connect() as db:
        rows = db.execute("SELECT * FROM items ORDER BY category, name").fetchall()
        movements = db.execute("SELECT * FROM movements ORDER BY id DESC LIMIT 10").fetchall()
        imports = db.execute("SELECT * FROM imports ORDER BY id DESC LIMIT 10").fetchall()
    items = []
    for r in rows:
        items.append({
            "code": r["code"],
            "name": r["name"],
            "category": r["category"],
            "unit": r["unit"],
            "quantity": r["quantity"],
            "minimum": r["minimum"],
            "status": status_for(r["quantity"], r["minimum"]),
        })
    return {
        "items": items,
        "movements": [dict(x) for x in movements],
        "imports": [dict(x) for x in imports],
        "finance": {"debtors": "Nog niet gekoppeld", "revenue_month": "Nog niet gekoppeld"},
        "version": "1.0-render-flask",
    }


@app.before_request
def ensure_db() -> None:
    init_db()


@app.route("/")
def index():
    return render_template("index.html", dashboard=get_dashboard())


@app.route("/health")
def health():
    return jsonify({"status": "ok", "program": "GROBÉ OS", "version": "1.0-render-flask"})


@app.route("/api/dashboard")
def api_dashboard():
    return jsonify(get_dashboard())


@app.route("/mutaties", methods=["GET", "POST"])
def movements():
    message = None
    if request.method == "POST":
        item_code = request.form.get("item_code", "").strip()
        try:
            change = float(str(request.form.get("change", "0")).replace(",", "."))
        except ValueError:
            change = 0
        source = request.form.get("source", "Handmatig") or "Handmatig"
        reference = request.form.get("reference") or None
        note = request.form.get("note") or None
        now = datetime.utcnow().isoformat()
        with db_connect() as db:
            item = db.execute("SELECT * FROM items WHERE code = ?", (item_code,)).fetchone()
            if item is None:
                message = f"Artikelcode niet gevonden: {item_code}"
            else:
                new_quantity = item["quantity"] + change
                if new_quantity < 0:
                    message = "Mutatie geweigerd: voorraad mag niet negatief worden."
                else:
                    db.execute("UPDATE items SET quantity = ?, updated_at = ? WHERE code = ?", (new_quantity, now, item_code))
                    db.execute(
                        "INSERT INTO movements (item_code, change, source, reference, note, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                        (item_code, change, source, reference, note, now),
                    )
                    db.commit()
                    message = f"Mutatie opgeslagen. Nieuwe voorraad: {new_quantity:g}"
    return render_template("movements.html", dashboard=get_dashboard(), message=message)


@app.route("/import", methods=["GET", "POST"])
def import_page():
    message = None
    if request.method == "POST":
        source = request.form.get("source", "Onbekend")
        file = request.files.get("file")
        if not file or file.filename == "":
            message = "Geen bestand gekozen."
        else:
            filename = secure_filename(file.filename)
            target = UPLOAD_DIR / filename
            file.save(target)
            now = datetime.utcnow().isoformat()
            with db_connect() as db:
                db.execute(
                    "INSERT INTO imports (filename, source, status, message, created_at) VALUES (?, ?, ?, ?, ?)",
                    (filename, source, "ontvangen", "Bestand ontvangen. Inhoudelijke uitlezing volgt in volgende module.", now),
                )
                db.commit()
            message = f"Bestand ontvangen: {filename}. Parser nog niet gekoppeld."
    return render_template("import.html", dashboard=get_dashboard(), message=message)


@app.route("/api/items")
def api_items():
    return jsonify(get_dashboard()["items"])


if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
