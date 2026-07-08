# GROBÉ OS Render fix v1.1

Deze versie lost de Render-templatefout op en maakt de eerste klikbare basis:

- Dashboard
- Voorraad
- Mutatie
- Import-test
- Health-check
- SQLite database

Render instellingen:

Build Command:

```text
pip install -r requirements.txt
```

Start Command:

```text
gunicorn main:app --bind 0.0.0.0:$PORT
```
