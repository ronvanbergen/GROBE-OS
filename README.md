# GROBÉ OS - Render basis v1.0

Deze versie is bewust gebouwd zonder FastAPI/Pydantic, omdat Render op Python 3.14 vastliep bij pydantic-core.

## Render instellingen

Build Command:

```text
pip install -r requirements.txt
```

Start Command:

```text
gunicorn main:app --bind 0.0.0.0:$PORT
```

## Wat werkt

- Homepage/dashboard
- SQLite database wordt automatisch aangemaakt
- Voorraaditems met statuskleur
- Importpagina ontvangt bestanden en logt uploads
- Mutatiepagina
- `/health` endpoint

## Wat nog niet werkt

- Daniel/Michael inhoudelijk uitlezen
- Factuur-engine
- Prijshistorie
- Login
- Dropbox
- PDF-generatie

Deze versie is bedoeld als eerste stabiele live basis op Render.
