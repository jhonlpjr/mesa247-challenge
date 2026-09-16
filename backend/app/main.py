from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.presentation.routes.queue_routes import router

app = FastAPI(
    title="Mesa247 · API de lista de espera",
    version="1.0.0",
    summary="API operativa para gestionar listas de espera de restaurantes.",
    description=(
        "Permite registrar comensales, consultar posiciones, operar llamadas y estados "
        "de atención, y generar reportes diarios. Los timestamps se almacenan en UTC; "
        "las fechas operativas se calculan con la zona horaria configurada por restaurante."
    ),
    openapi_tags=[
        {"name": "Restaurantes", "description": "Consulta de la configuración pública del restaurante."},
        {"name": "Cola · Comensal", "description": "Ingreso y seguimiento de una reserva en la cola."},
        {"name": "Cola · Operación", "description": "Acciones del anfitrión sobre la cola y sus estados."},
        {"name": "Reportes", "description": "Métricas operativas agrupadas por día local."},
        {"name": "Sistema", "description": "Disponibilidad y estado de la API."},
    ],
    swagger_ui_parameters={"docExpansion": "none", "filter": True, "displayRequestDuration": True},
)
app.add_middleware(CORSMiddleware, allow_origins=[x.strip() for x in settings.cors_origins.split(",") if x.strip()],
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(router)


@app.get("/health", tags=["Sistema"], summary="Verificar disponibilidad", description="Confirma que la API está disponible para recibir solicitudes.")
def health():
    return {"status": "ok"}
