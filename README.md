# GROBÉ OS - React milestone 1

Nieuwe basis voor GROBÉ OS als webapplicatie.

## Stack
- Frontend: React + Vite
- Backend: FastAPI
- Hosting: Render compatible

## Lokaal draaien

Backend:
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

## Render
Deze versie bevat `render.yaml` voor een webservice die de React build serveert via FastAPI.
