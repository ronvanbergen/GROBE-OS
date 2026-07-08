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
        lines.append({**line, "unit_price": unit_price, "line_total": line_total, "stock": stock, "possible_batches": batches})

    batch_liters = float(recipe.get("batch_liters") or 1)
    return {
        "recipe_id": recipe.get("id"),
        "recipe_name": recipe.get("name"),
        "batch_liters": batch_liters,
        "total_cost": total,
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
        "packaging": packaging_total,
        "fill_cost": fill_cost,
        "total_cost": total_cost,
        "profit": profit,
        "margin": margin,
        "packaging_lines": packaging_lines,
    }


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
    return {
        "raw_materials": [a for a in articles if a.get("type") == "grondstof"],
        "packaging": [a for a in articles if a.get("type") in ["verpakking", "etiket", "doos"]],
        "recipes": recipe_costs,
        "products": product_costs,
        "warnings": warnings[:12],
        "open_mutations": [m for m in db.get("stock_mutations", []) if m.get("status") != "approved"],
    }
