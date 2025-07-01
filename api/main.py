
from fastapi import FastAPI
import sys
import os

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from api.controllers import client_routes, info_routes, order_routes, report_routes

app = FastAPI(
    title="Drone Logistics API",
    description="API para interactuar con los datos de la Simulación de Logística con Drones.",
    version="1.0.1"
)

# --- Rutas de la API ---
# Incluir los routers de los diferentes controladores.
app.include_router(client_routes.router, prefix="/api", tags=["Clients"])
app.include_router(order_routes.router, prefix="/api", tags=["Orders"])
app.include_router(report_routes.router, prefix="/api", tags=["Reports"])
app.include_router(info_routes.router, prefix="/api", tags=["Info & Analytics"])

# --- Endpoints Principales ---
@app.get("/", tags=["Root"])
async def read_root():
    """Endpoint raíz que da la bienvenida a la API."""
    return {"message": "Welcome to the Drone Logistics API. Navigate to /docs for the interactive documentation."}

@app.get("/api/health", tags=["Health Check"])
async def health_check():
    """Endpoint simple para verificar que la API está funcionando."""
    return {"status": "ok"}