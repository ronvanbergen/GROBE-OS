from __future__ import annotations
from typing import Any, Dict, List
from math import floor


def money(value: float) -> str:
    return f"€ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def article_price(article: Dict[str, Any]) -> float:
    return float(article.get("last_price") or article.get("manual_price") or 0)


def stock_percentage(article: Dict[str, Any]) -> float:
    max_stock = float(article.get("max_stock") or 0)
    stock = float(article.get("stock") or 0)
    if max_stock <= 0:
        return 0
    return max(0, min(100, (stock / max_stock) * 100))


def stock_status(article: Dict[str, Any]) -> str:
    stock = float(article.get("stock") or 0)
    min_stock = float(article.get("min_stock") or 0)
    if min_stock and stock <= min_stock:
        return "kritiek"
    if min_stock and stock <= min_stock * 1.5:
        return "laag"
    return "ok"


def calculate_recipe_cost(db: Dict[str, Any], recipe: Dict[str, Any]) -> Dict[str, Any]:
    article_map = {a.get("legacy_number"): a for a in db.get("articles", [])}
    lines: List[Dict[str, Any]] = []
    total = 0.0
    limiting = None
    possible_batches = None

    for line in recipe.get("lines", []):
        article = article_map.get(line["legacy_number"])
        unit_price = article_price(article or {})
        qty = float(line.get("quantity") or 0)
        line_total = qty * unit_price
        total += line_total
        stock = float((article or {}).get("stock") or 0)
        batches = floor(stock / qty) if qty > 0 else 0
        if possible_batches is None or batches < possible_batches:
            possible_batches = batches
            limiting = line.get("name")
        lines.append({**line, "unit_price": unit_price, "line_total": line_total, "line_cost": line_total, "stock": stock, "possible_batches": batches})

    batch_liters = float(recipe.get("batch_liters") or 1)
    return {
        "recipe_id": recipe.get("id"),
        "recipe_name": recipe.get("name"),
        "batch_liters": batch_liters,
        "total_cost": total,
        "batch_cost": total,
        "cost_per_liter": total / batch_liters if batch_liters else 0,
        "possible_batches": possible_batches or 0,
        "possible_liters": (possible_batches or 0) * batch_liters,
        "limiting_material": limiting,
        "lines": lines,
    }


def active_universol_cost_per_liter(db: Dict[str, Any]) -> float:
    recipes = db.get("recipes", [])
    # zolang ECOSURF nog aanwezig is, toon huidige receptuur als actief
    ecosurf = next((a for a in db.get("articles", []) if a.get("legacy_number") == "ECOSURF"), None)
    preferred_id = "universol-ecosurf-4500l" if ecosurf and float(ecosurf.get("stock") or 0) > 0 else "universol-nieuw-1000l"
    recipe = next((r for r in recipes if r.get("id") == preferred_id), recipes[0] if recipes else None)
    if not recipe:
        return 0
    return calculate_recipe_cost(db, recipe)["cost_per_liter"]


def calculate_product_cost(db: Dict[str, Any], product: Dict[str, Any]) -> Dict[str, Any]:
    article_map = {a.get("legacy_number"): a for a in db.get("articles", [])}
    liters = float(product.get("liters_per_unit") or 0)
    grondstof_per_liter = active_universol_cost_per_liter(db) if product.get("brand") in ["Universol", "ProGold"] else float(product.get("raw_cost_per_liter") or 0.75)
    grondstof = liters * grondstof_per_liter
    packaging_total = 0.0
    packaging_lines = []
    for use in product.get("uses", []):
        article = article_map.get(use.get("legacy_number"))
        qty = float(use.get("qty") or 0)
        price = article_price(article or {})
        total = qty * price
        packaging_total += total
        packaging_lines.append({"name": (article or {}).get("name", use.get("legacy_number")), "qty": qty, "price": price, "total": total})
    fill_cost = float(product.get("fill_cost") or 0)
    total_cost = grondstof + packaging_total + fill_cost
    sell_price = float(product.get("sell_price") or 0)
    profit = sell_price - total_cost
    margin = (profit / sell_price * 100) if sell_price else 0
    return {
        "sku": product.get("sku"),
        "name": product.get("name"),
        "sell_price": sell_price,
        "grondstof": grondstof,
        "material_cost": grondstof,
        "packaging": packaging_total,
        "packaging_cost": packaging_total,
        "fill_cost": fill_cost,
        "total_cost": total_cost,
        "profit": profit,
        "margin": margin,
        "packaging_lines": packaging_lines,
        "liters_per_unit": liters,
    }


def _status_label(stock: float, minimum: float) -> tuple[str, str]:
    if minimum and stock <= minimum:
        return "Bijna op", "bad"
    if minimum and stock <= minimum * 1.8:
        return "Bestellen", "warn"
    if minimum and stock >= minimum * 4:
        return "Ruim voldoende", "good"
    return "Voldoende", "ok"


def dashboard_metrics(db: Dict[str, Any]) -> Dict[str, Any]:
    articles = db.get("articles", [])
    products = db.get("products", [])
    recipes = db.get("recipes", [])
    recipe_costs = [calculate_recipe_cost(db, r) for r in recipes]
    product_costs = [calculate_product_cost(db, p) for p in products]
    warnings = []
    for article in articles:
        status = stock_status(article)
        if status != "ok":
            warnings.append({"level": status, "text": f"{article.get('name')} staat laag: {article.get('stock')} {article.get('unit')}"})
    for rc in recipe_costs:
        if rc["limiting_material"]:
            warnings.append({"level": "info", "text": f"{rc['recipe_name']}: {rc['possible_liters']:,.0f} liter mogelijk. Beperkend: {rc['limiting_material']}".replace(",", ".")})

    dashboard_products = []
    icons = {"Universol": "▣", "ProGold": "▣", "Behangbikker": "▣", "Microsan": "▯", "Uniforte": "▣"}
    css = {"Universol": "", "ProGold": "orange", "Behangbikker": "orange", "Microsan": "green", "Uniforte": "gray"}
    for product in products[:8]:
        stock_units = float(product.get("stock_units") or 0)
        minimum = max(100, float(product.get("units_per_box") or 1) * 40)
        status, status_class = _status_label(stock_units, minimum)
        unit = "stuks" if stock_units >= 1000 or product.get("liters_per_unit", 0) <= 1 else "L"
        stock_label = f"{stock_units:,.0f} {unit}".replace(",", ".")
        if product.get("brand") in ["Behangbikker", "Microsan", "Uniforte"]:
            stock_label = f"{stock_units * float(product.get('liters_per_unit') or 0):,.0f} L".replace(",", ".")
        dashboard_products.append({
            "name": product.get("name", ""),
            "stock": stock_label,
            "status": status,
            "status_class": status_class,
            "icon": icons.get(product.get("brand"), "▣"),
            "css": css.get(product.get("brand"), ""),
        })

    tanks_source = [
        {"name": "Universol", "stock": 6300, "capacity": 10000},
        {"name": "Behangbikker", "stock": 2020, "capacity": 5000},
        {"name": "Microsan", "stock": 1500, "capacity": 5000},
        {"name": "Uniforte 1:10", "stock": 603, "capacity": 3000},
        {"name": "Uniforte concentraat", "stock": 200, "capacity": 2000},
    ]
    dashboard_tanks = []
    for tank in tanks_source:
        pct = int(max(0, min(100, tank["stock"] / tank["capacity"] * 100))) if tank["capacity"] else 0
        dashboard_tanks.append({
            "name": tank["name"],
            "stock": f"{tank['stock']:,.0f} L".replace(",", "."),
            "capacity": f"{tank['capacity']:,.0f} L".replace(",", "."),
            "percent": pct,
        })

    packaging_lookup = {a.get("legacy_number"): a for a in articles}
    pack_codes = [
        ("CAN5L-BLAUW", "Jerrycan 5L", "▯"),
        ("FLES1L-WIT", "Fles 1L", "▯"),
        ("FLES600-WIT", "Fles 600 ml", "▯"),
        ("TRIGGER-LB", "Triggers lichtblauw", "⌁"),
        ("DOOS-UNI-4X5", "Dozen 4 x 5L", "□"),
        ("ETI-UNI-600", "Etiketten 600 ml", "▤"),
    ]
    dashboard_packaging = []
    for code, label, icon in pack_codes:
        article = packaging_lookup.get(code, {})
        stock = float(article.get("stock") or 0)
        minimum = float(article.get("min_stock") or 0)
        status, status_class = _status_label(stock, minimum)
        dashboard_packaging.append({
            "name": label,
            "stock": f"{stock:,.0f} stuks".replace(",", "."),
            "status": status,
            "status_class": status_class,
            "icon": icon,
        })

    return {
        "raw_materials": [a for a in articles if a.get("type") == "grondstof"],
        "packaging": [a for a in articles if a.get("type") in ["verpakking", "etiket", "doos"]],
        "recipes": recipe_costs,
        "products": product_costs,
        "warnings": warnings[:12],
        "open_mutations": [m for m in db.get("stock_mutations", []) if m.get("status") != "approved"],
        "dashboard_products": dashboard_products,
        "dashboard_tanks": dashboard_tanks,
        "dashboard_packaging": dashboard_packaging,
    }
