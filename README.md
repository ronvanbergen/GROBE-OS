# GROBÉ OS - Render project v1

Werkende basis voor Render zonder FastAPI/Pydantic.

## Render instellingen

Build Command:

```text
pip install -r requirements.txt
```

Start Command:

```text
gunicorn main:app --bind 0.0.0.0:$PORT
```

## Pagina's

- `/` dashboard
- `/health` health-check
- `/api/dashboard` JSON dashboard
- `/import` importpagina
- `/mutaties` voorraadmutaties

## Status

Dit is een stabiele startbasis. Daniel/Michael-parsers en factuurherkenning zijn nog niet ingebouwd.
