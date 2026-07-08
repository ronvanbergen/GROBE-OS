from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="GROBÉ OS")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parents[2]
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

@app.get("/api/health")
def health():
    return {"status": "ok", "app": "GROBÉ OS", "version": "react-milestone-1"}

@app.get("/api/dashboard")
def dashboard():
    return {
        "kpis": [
            {"label": "Omzet deze maand", "value": "€ 61.245", "sub": "+12,4% vs vorige maand", "trend": "up", "icon": "€"},
            {"label": "Openstaande debiteuren", "value": "€ 84.230", "sub": "12 facturen", "trend": "warn", "icon": "👥"},
            {"label": "Open orders", "value": "12", "sub": "3 wachten op voorraad", "trend": "warn", "icon": "📋"},
            {"label": "Pakbonnen vandaag", "value": "5", "sub": "Laatste: 2026-0451", "trend": "ok", "icon": "🚚"},
        ],
        "finishedProducts": [
            {"name": "Universol 5 L", "qty": "1.552 stuks", "status": "Ruim voldoende", "type": "blue"},
            {"name": "Universol 1 L", "qty": "4.692 stuks", "status": "Voldoende", "type": "blue"},
            {"name": "Universol 600 ml", "qty": "852 stuks", "status": "Bestellen", "type": "orange"},
            {"name": "Behangbikker", "qty": "2.020 L", "status": "Voldoende", "type": "paper"},
            {"name": "Microsan", "qty": "1.500 L", "status": "Voldoende", "type": "green"},
            {"name": "Uniforte 1:10", "qty": "603 L", "status": "Voldoende", "type": "dark"},
            {"name": "Universol doekjes (per 6)", "qty": "0 stuks", "status": "Bijna op", "type": "wipes"},
        ],
        "tanks": [
            {"name": "Universol", "liters": 6300, "capacity": 10000},
            {"name": "Behangbikker", "liters": 2020, "capacity": 5000},
            {"name": "Microsan", "liters": 1500, "capacity": 5000},
            {"name": "Uniforte 1:10", "liters": 603, "capacity": 3000},
            {"name": "Uniforte concentraat", "liters": 200, "capacity": 2000},
        ],
        "packaging": [
            {"name": "Jerrycan 5L", "qty": "4.850 stuks", "status": "Ruim voldoende", "icon": "🧴"},
            {"name": "Fles 1L", "qty": "2.300 stuks", "status": "Voldoende", "icon": "🧴"},
            {"name": "Fles 600 ml", "qty": "420 stuks", "status": "Bestellen", "icon": "🧴"},
            {"name": "Triggers lichtblauw", "qty": "80 stuks", "status": "Bijna op", "icon": "🔫"},
            {"name": "Dozen 4 x 5L", "qty": "1.250 stuks", "status": "Ruim voldoende", "icon": "📦"},
            {"name": "Etiketten 1L", "qty": "600 stuks", "status": "Bestellen", "icon": "🏷️"},
        ],
        "alerts": [
            {"level": "danger", "text": "Triggers lichtblauw bijna op (80 stuks)"},
            {"level": "warning", "text": "Etiketten Universol 1L bestellen (600 stuks)"},
            {"level": "info", "text": "Nieuwe factuur Superdoos ontvangen"},
            {"level": "info", "text": "Nieuwe voorraad Excel Michael beschikbaar"},
        ],
        "activity": [
            {"time": "09:14", "text": "Pakbon 2026-0451 gemaakt voor Copagro"},
            {"time": "09:02", "text": "Afvulling: 400 stuks Universol 5L"},
            {"time": "08:47", "text": "Inkoopfactuur Superdoos verwerkt"},
            {"time": "08:30", "text": "Nieuwe batch Universol geproduceerd (4.500 L)"},
        ]
    }

if FRONTEND_DIST.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIST / "assets"), name="assets")

@app.get("/{full_path:path}")
def serve_react(full_path: str):
    index = FRONTEND_DIST / "index.html"
    if index.exists():
        return FileResponse(index)
    return {"message": "Frontend build not found. Run npm install && npm run build in frontend."}
