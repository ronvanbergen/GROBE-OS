from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename

from .storage import load_db, save_db, upsert_article, approve_stock_mutation, UPLOAD_DIR, now_iso
from .invoice_engine import pdf_to_text, detect_supplier, match_invoice_lines
from .business_engine import dashboard_metrics, calculate_recipe_cost, calculate_product_cost, money

app = Flask(__name__)
app.secret_key = "grobe-os-development"
app.jinja_env.filters["money"] = money


@app.route("/")
def dashboard():
    db = load_db()
    metrics = dashboard_metrics(db)
    return render_template("dashboard.html", db=db, metrics=metrics)


@app.route("/articles", methods=["GET", "POST"])
def articles():
    if request.method == "POST":
        legacy_number = request.form.get("legacy_number", "").strip()
        name = request.form.get("name", "").strip()
        if not legacy_number or not name:
            flash("Legacy-nummer en naam zijn verplicht.", "error")
            return redirect(url_for("articles"))
        article = {
            "legacy_number": legacy_number.upper(),
            "name": name,
            "type": request.form.get("type", "grondstof"),
            "unit": request.form.get("unit", "kg"),
            "stock": float(request.form.get("stock", "0") or 0),
            "min_stock": float(request.form.get("min_stock", "0") or 0),
            "max_stock": float(request.form.get("max_stock", "0") or 0),
            "lead_time_days": int(float(request.form.get("lead_time_days", "0") or 0)),
            "supplier": request.form.get("supplier", ""),
            "manual_price": float(request.form.get("manual_price", "0") or 0)
        }
        upsert_article(article)
        flash("Artikel opgeslagen.", "success")
        return redirect(url_for("articles"))
    db = load_db()
    return render_template("articles.html", articles=db.get("articles", []))


@app.route("/materials")
def materials():
    db = load_db()
    raw = [a for a in db.get("articles", []) if a.get("type") == "grondstof"]
    return render_template("materials.html", raw_materials=raw)


@app.route("/products")
def products():
    db = load_db()
    rows = [{"product": p, "cost": calculate_product_cost(db, p)} for p in db.get("products", [])]
    return render_template("products.html", rows=rows)


@app.route("/invoice", methods=["GET", "POST"])
def invoice():
    db = load_db()
    if request.method == "POST":
        file = request.files.get("invoice_pdf")
        if not file or not file.filename.lower().endswith(".pdf"):
            flash("Upload een PDF-factuur.", "error")
            return redirect(url_for("invoice"))
        filename = secure_filename(file.filename)
        path = UPLOAD_DIR / f"{now_iso().replace(':','-')}_{filename}"
        path.parent.mkdir(parents=True, exist_ok=True)
        file.save(path)

        text = pdf_to_text(path)
        supplier = detect_supplier(text)
        matches = match_invoice_lines(text, db.get("articles", []))

        db.setdefault("invoice_imports", []).append({
            "filename": filename,
            "stored_path": str(path),
            "supplier": supplier,
            "matched_lines": len(matches),
            "created_at": now_iso()
        })

        for match in matches:
            db.setdefault("price_history", []).append({
                "created_at": now_iso(),
                "supplier": supplier,
                "legacy_number": match["legacy_number"],
                "article_name": match["article_name"],
                "unit_price": match["unit_price"],
                "source_file": filename,
                "raw_line": match["raw_line"]
            })
            # prijs direct zichtbaar maken als laatste prijs; voorraad blijft pending
            for article in db.get("articles", []):
                if article.get("legacy_number") == match["legacy_number"]:
                    article["last_price"] = match["unit_price"]
            db.setdefault("stock_mutations", []).append({
                "created_at": now_iso(),
                "status": "pending",
                "target_type": "article",
                "type": "inkoop_factuur",
                "supplier": supplier,
                "legacy_number": match["legacy_number"],
                "article_name": match["article_name"],
                "quantity": match["quantity"],
                "unit_price": match["unit_price"],
                "source_file": filename,
                "raw_line": match["raw_line"]
            })
        save_db(db)
        flash(f"Factuur verwerkt. {len(matches)} regels herkend. Voorraad staat klaar voor goedkeuring.", "success")
        return redirect(url_for("invoice"))
    return render_template("invoice.html", imports=db.get("invoice_imports", []), history=db.get("price_history", [])[-20:])


@app.route("/mutations")
def mutations():
    db = load_db()
    return render_template("mutations.html", mutations=db.get("stock_mutations", []))


@app.route("/mutations/<int:index>/approve", methods=["POST"])
def approve_mutation(index: int):
    if approve_stock_mutation(index):
        flash("Voorraadmutatie goedgekeurd en voorraad aangepast.", "success")
    else:
        flash("Mutatie kon niet worden goedgekeurd.", "error")
    return redirect(url_for("mutations"))


@app.route("/recipes")
def recipes():
    db = load_db()
    rows = []
    for recipe in db.get("recipes", []):
        cost = calculate_recipe_cost(db, recipe)
        rows.append({"recipe": recipe, "cost": cost})
    return render_template("recipes.html", rows=rows)


@app.route("/costs")
def costs():
    db = load_db()
    recipe_costs = [calculate_recipe_cost(db, r) for r in db.get("recipes", [])]
    product_costs = [calculate_product_cost(db, p) for p in db.get("products", [])]
    return render_template("costs.html", recipe_costs=recipe_costs, product_costs=product_costs)


@app.route("/prices")
def prices():
    db = load_db()
    return render_template("prices.html", history=list(reversed(db.get("price_history", []))))


if __name__ == "__main__":
    app.run(debug=True)
