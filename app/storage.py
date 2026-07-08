import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "grobe_os.json"
UPLOAD_DIR = DATA_DIR / "uploads"

RAW_MATERIALS = [
    {"legacy_number": "WATER", "name": "Water", "type": "grondstof", "unit": "kg", "stock": 18000, "min_stock": 0, "max_stock": 20000, "lead_time_days": 0, "supplier": "Intern", "manual_price": 0.00},
    {"legacy_number": "BDG", "name": "Butyldiglycol", "type": "grondstof", "unit": "kg", "stock": 3800, "min_stock": 900, "max_stock": 5000, "lead_time_days": 14, "supplier": "Julius Hoesch", "manual_price": 1.58},
    {"legacy_number": "AMPHOLAK", "name": "Ampholak YJH-40", "type": "grondstof", "unit": "kg", "stock": 2900, "min_stock": 700, "max_stock": 4000, "lead_time_days": 21, "supplier": "Julius Hoesch", "manual_price": 1.94},
    {"legacy_number": "KOH", "name": "KOH 50%", "type": "grondstof", "unit": "kg", "stock": 1100, "min_stock": 250, "max_stock": 1500, "lead_time_days": 14, "supplier": "Julius Hoesch", "manual_price": 0.86},
    {"legacy_number": "DISSOLVINE", "name": "Dissolvine GL-47-S", "type": "grondstof", "unit": "kg", "stock": 2100, "min_stock": 450, "max_stock": 3000, "lead_time_days": 21, "supplier": "Julius Hoesch", "manual_price": 2.48},
    {"legacy_number": "NL8P4", "name": "ROKAnol NL8P4", "type": "grondstof", "unit": "kg", "stock": 900, "min_stock": 250, "max_stock": 1500, "lead_time_days": 21, "supplier": "PCC / Hoesch", "manual_price": 2.12},
    {"legacy_number": "GA8W", "name": "GA8W", "type": "grondstof", "unit": "kg", "stock": 900, "min_stock": 250, "max_stock": 1500, "lead_time_days": 21, "supplier": "PCC / Hoesch", "manual_price": 2.05},
    {"legacy_number": "NCS", "name": "Hoesch NCS", "type": "grondstof", "unit": "kg", "stock": 2050, "min_stock": 500, "max_stock": 3000, "lead_time_days": 21, "supplier": "Julius Hoesch", "manual_price": 1.12},
    {"legacy_number": "ECOSURF", "name": "ECOSURF EH-9", "type": "grondstof", "unit": "kg", "stock": 378, "min_stock": 0, "max_stock": 1000, "lead_time_days": 30, "supplier": "Univar / Dow", "manual_price": 2.35},
]

PACKAGING = [
    {"legacy_number": "CAN5L-BLAUW", "name": "Universol 5L jerrycan blauw", "type": "verpakking", "unit": "st", "stock": 2880, "min_stock": 500, "max_stock": 5000, "lead_time_days": 28, "supplier": "Distrifill", "manual_price": 1.15},
    {"legacy_number": "FLES1L-WIT", "name": "Universol 1L fles wit", "type": "verpakking", "unit": "st", "stock": 8640, "min_stock": 1200, "max_stock": 12000, "lead_time_days": 28, "supplier": "Distrifill", "manual_price": 0.42},
    {"legacy_number": "FLES600-WIT", "name": "600 ml witte fles", "type": "verpakking", "unit": "st", "stock": 2240, "min_stock": 600, "max_stock": 6000, "lead_time_days": 28, "supplier": "Distrifill", "manual_price": 0.24},
    {"legacy_number": "TRIGGER-LB", "name": "Lichtblauwe trigger", "type": "verpakking", "unit": "st", "stock": 1200, "min_stock": 500, "max_stock": 6000, "lead_time_days": 28, "supplier": "Distrifill", "manual_price": 0.31},
    {"legacy_number": "TRIGGER-ZW", "name": "Zwarte trigger", "type": "verpakking", "unit": "st", "stock": 1040, "min_stock": 300, "max_stock": 3000, "lead_time_days": 28, "supplier": "Distrifill", "manual_price": 0.29},
    {"legacy_number": "ETI-UNI-600", "name": "Etiket Universol 600 ml", "type": "etiket", "unit": "st", "stock": 1480, "min_stock": 500, "max_stock": 5000, "lead_time_days": 21, "supplier": "Etikettenleverancier", "manual_price": 0.09},
    {"legacy_number": "DOOS-UNI-4X5", "name": "Doos Universol 4 x 5L", "type": "doos", "unit": "st", "stock": 1320, "min_stock": 250, "max_stock": 2000, "lead_time_days": 21, "supplier": "Superdoos", "manual_price": 0.94},
    {"legacy_number": "DOOS-UNI-12X1", "name": "Doos Universol 12 x 1L", "type": "doos", "unit": "st", "stock": 1320, "min_stock": 250, "max_stock": 2000, "lead_time_days": 21, "supplier": "Superdoos", "manual_price": 0.86},
    {"legacy_number": "DOOS-600", "name": "Doos 12 x 600 ml", "type": "doos", "unit": "st", "stock": 540, "min_stock": 150, "max_stock": 1200, "lead_time_days": 21, "supplier": "Superdoos", "manual_price": 0.72},
]

PRODUCTS = [
    {"sku": "111995", "name": "Universol 5 liter concentraat", "brand": "Universol", "liters_per_unit": 5, "units_per_box": 4, "boxes_per_pallet": 40, "stock_units": 2880, "sell_price": 23.16, "fill_cost": 1.65,
     "uses": [{"legacy_number": "CAN5L-BLAUW", "qty": 1}, {"legacy_number": "DOOS-UNI-4X5", "qty": 0.25}]},
    {"sku": "112011", "name": "Universol 1 liter concentraat", "brand": "Universol", "liters_per_unit": 1, "units_per_box": 12, "boxes_per_pallet": 50, "stock_units": 8640, "sell_price": 5.39, "fill_cost": 0.48,
     "uses": [{"legacy_number": "FLES1L-WIT", "qty": 1}, {"legacy_number": "DOOS-UNI-12X1", "qty": 1/12}]},
    {"sku": "112020600", "name": "Universol 600 ml spray kant-en-klaar", "brand": "Universol", "liters_per_unit": 0.6, "units_per_box": 12, "boxes_per_pallet": 60, "stock_units": 1440, "sell_price": 3.88, "fill_cost": 0.36,
     "uses": [{"legacy_number": "FLES600-WIT", "qty": 1}, {"legacy_number": "TRIGGER-LB", "qty": 1}, {"legacy_number": "ETI-UNI-600", "qty": 1}, {"legacy_number": "DOOS-600", "qty": 1/12}]},
    {"sku": "112215", "name": "ProGold Allesreiniger 5 liter concentraat", "brand": "ProGold", "liters_per_unit": 5, "units_per_box": 4, "boxes_per_pallet": 40, "stock_units": 864, "sell_price": 10.43, "fill_cost": 1.65, "uses": []},
    {"sku": "BB-5L", "name": "Behangbikker 5 liter", "brand": "Behangbikker", "liters_per_unit": 5, "units_per_box": 4, "boxes_per_pallet": 40, "stock_units": 160, "sell_price": 24.00, "fill_cost": 1.65, "uses": []},
    {"sku": "MIC-5L", "name": "Microsan 5 liter", "brand": "Microsan", "liters_per_unit": 5, "units_per_box": 4, "boxes_per_pallet": 40, "stock_units": 160, "sell_price": 23.50, "fill_cost": 1.65, "uses": []},
    {"sku": "UNI-5L", "name": "Uniforte 5 liter", "brand": "Uniforte", "liters_per_unit": 5, "units_per_box": 4, "boxes_per_pallet": 40, "stock_units": 160, "sell_price": 23.50, "fill_cost": 1.65, "uses": []},
]

RECIPES = [
    {"id": "universol-ecosurf-4500l", "name": "Universol huidige receptuur met ECOSURF", "product_brand": "Universol", "batch_liters": 4500, "notes": "Bestaande receptuur met 1% ECOSURF. Wordt gebruikt tot ECOSURF op is.", "lines": [
        {"legacy_number": "WATER", "name": "Water", "quantity": 3901.5, "unit": "kg"},
        {"legacy_number": "BDG", "name": "Butyldiglycol", "quantity": 162, "unit": "kg"},
        {"legacy_number": "AMPHOLAK", "name": "Ampholak YJH-40", "quantity": 166.5, "unit": "kg"},
        {"legacy_number": "ECOSURF", "name": "ECOSURF EH-9", "quantity": 45, "unit": "kg"},
        {"legacy_number": "DISSOLVINE", "name": "Dissolvine GL-47-S", "quantity": 90, "unit": "kg"},
        {"legacy_number": "KOH", "name": "KOH 50%", "quantity": 45, "unit": "kg"},
        {"legacy_number": "NCS", "name": "Stepanate/NCS hydrotroop", "quantity": 90, "unit": "kg"},
    ]},
    {"id": "universol-nieuw-1000l", "name": "Universol nieuwe receptuur na ECOSURF", "product_brand": "Universol", "batch_liters": 1000, "notes": "Nieuwe receptuur zodra ECOSURF op is. Totaal telt op tot 1000.", "lines": [
        {"legacy_number": "WATER", "name": "Water", "quantity": 867, "unit": "kg"},
        {"legacy_number": "BDG", "name": "Butyldiglycol", "quantity": 36, "unit": "kg"},
        {"legacy_number": "AMPHOLAK", "name": "Ampholak YJH-40", "quantity": 29, "unit": "kg"},
        {"legacy_number": "KOH", "name": "KOH 50%", "quantity": 10, "unit": "kg"},
        {"legacy_number": "DISSOLVINE", "name": "Dissolvine GL-47-S", "quantity": 20, "unit": "kg"},
        {"legacy_number": "NL8P4", "name": "ROKAnol NL8P4", "quantity": 9, "unit": "kg"},
        {"legacy_number": "GA8W", "name": "GA8W", "quantity": 9, "unit": "kg"},
        {"legacy_number": "NCS", "name": "Hoesch NCS", "quantity": 20, "unit": "kg"},
    ]},
]

DEFAULT_DB: Dict[str, Any] = {
    "settings": {"company_name": "GROBÉ Nederland", "currency": "EUR", "dashboard_note": "GROBÉ OS v3 basis"},
    "articles": RAW_MATERIALS + PACKAGING,
    "products": PRODUCTS,
    "recipes": RECIPES,
    "suppliers": [
        {"name": "Julius Hoesch", "type": "grondstoffen"},
        {"name": "Distrifill", "type": "afvullen / verpakking"},
        {"name": "Superdoos", "type": "dozen"},
    ],
    "product_costs": [],
    "price_history": [],
    "stock_mutations": [],
    "invoice_imports": [],
    "production_batches": [],
}

def now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")

def ensure_db() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    if not DB_PATH.exists():
        save_db(DEFAULT_DB)

def _merge_defaults(db: Dict[str, Any]) -> bool:
    changed = False
    for key, value in DEFAULT_DB.items():
        if key not in db:
            db[key] = value
            changed = True
    existing_numbers = {a.get("legacy_number", "").upper() for a in db.get("articles", [])}
    for article in DEFAULT_DB["articles"]:
        if article["legacy_number"].upper() not in existing_numbers:
            db.setdefault("articles", []).append(article)
            changed = True
    existing_skus = {p.get("sku", "").upper() for p in db.get("products", [])}
    for product in DEFAULT_DB["products"]:
        if product["sku"].upper() not in existing_skus:
            db.setdefault("products", []).append(product)
            changed = True
    existing_recipes = {r.get("id") for r in db.get("recipes", [])}
    for recipe in DEFAULT_DB["recipes"]:
        if recipe["id"] not in existing_recipes:
            db.setdefault("recipes", []).append(recipe)
            changed = True
    return changed

def load_db() -> Dict[str, Any]:
    ensure_db()
    with DB_PATH.open("r", encoding="utf-8") as f:
        db = json.load(f)
    if _merge_defaults(db):
        save_db(db)
    return db

def save_db(db: Dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    tmp = DB_PATH.with_suffix(".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)
    tmp.replace(DB_PATH)

def find_article(db: Dict[str, Any], legacy_number: str) -> Dict[str, Any] | None:
    needle = legacy_number.strip().upper()
    for article in db.get("articles", []):
        if article.get("legacy_number", "").strip().upper() == needle:
            return article
    return None

def find_product(db: Dict[str, Any], sku: str) -> Dict[str, Any] | None:
    needle = sku.strip().upper()
    for product in db.get("products", []):
        if product.get("sku", "").strip().upper() == needle:
            return product
    return None

def upsert_article(article: Dict[str, Any]) -> None:
    db = load_db()
    existing = find_article(db, article["legacy_number"])
    if existing:
        existing.update(article)
    else:
        db.setdefault("articles", []).append(article)
    save_db(db)

def add_stock_mutation(db: Dict[str, Any], mutation: Dict[str, Any]) -> None:
    mutation.setdefault("created_at", now_iso())
    mutation.setdefault("status", "pending")
    db.setdefault("stock_mutations", []).append(mutation)

def approve_stock_mutation(index: int) -> bool:
    db = load_db()
    mutations: List[Dict[str, Any]] = db.get("stock_mutations", [])
    if index < 0 or index >= len(mutations):
        return False
    mutation = mutations[index]
    if mutation.get("status") == "approved":
        return True
    target_type = mutation.get("target_type", "article")
    qty = float(mutation.get("quantity", 0) or 0)
    if target_type == "product":
        product = find_product(db, mutation.get("sku", ""))
        if not product:
            return False
        product["stock_units"] = float(product.get("stock_units", 0) or 0) + qty
    else:
        article = find_article(db, mutation.get("legacy_number", ""))
        if not article:
            return False
        article["stock"] = float(article.get("stock", 0) or 0) + qty
    mutation["status"] = "approved"
    mutation["approved_at"] = now_iso()
    save_db(db)
    return True
