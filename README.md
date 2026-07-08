# GROBÉ OS

Startversie voor Render.

## Render instellingen

Language: Python 3
Build Command: `pip install -r requirements.txt`
Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

## Wat werkt in deze startversie

- Dashboard
- Voorraaditems
- Voorraadmutaties
- Zoekfunctie
- Importcentrum voor Excel-bestanden
- Eenvoudige herkenning van bekende grondstoffen/verpakkingen
- Prijshistorie
- Health check: `/api/health`

## Nog niet klaar

- Login
- Permanente productie-database
- PDF-factuurherkenning
- Echte Daniel/Michael layout-specifieke parser
- Dropbox-koppeling
- Pakbon-PDF's

Let op: op Render Free kan de lokale SQLite database bij herstart/deploy opnieuw beginnen. Voor echte productie moet dit later naar PostgreSQL.
