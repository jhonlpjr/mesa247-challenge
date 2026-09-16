# Mesa247 Waiting List

Mesa247 es una lista de espera digital para restaurantes. El vertical slice obligatorio permite que un comensal se registre, el anfitrión visualice la cola y llame al siguiente grupo.

## Alcance

El CORE priorizado es: comensal se une → anfitrión ve la cola → anfitrión llama al siguiente. Incluye además extensiones demostrativas fuera del vertical slice obligatorio: consulta de estado/posición, sentar/cancelar, no-show, reporte diario, polling, persistencia local, drag & drop en la vista del anfitrión y representación de notificación WhatsApp mediante enlace `wa.me`. No incluye autenticación, WhatsApp automatizado, WebSockets ni emails.

## Stack y arquitectura

- Frontend: React, TypeScript, Vite, React Router, Fetch API y Vitest.
- Backend: Python, FastAPI, Pydantic y SQLAlchemy.
- Persistencia: SQLite local con Alembic; el modelo queda preparado para MySQL.

La solución usa una Clean Architecture pragmática: `presentation` coordina HTTP/UI, `application` contiene casos de uso, `domain` contiene entidades/estados/puertos, e `infrastructure` implementa API, almacenamiento y SQLAlchemy.

## Estructura principal

```text
backend/
  app/domain/              # Entidades, enums y contratos
  app/application/         # Casos de uso
  app/infrastructure/      # SQLAlchemy, SQLite y repositorios
  app/presentation/        # FastAPI, rutas y schemas
  migrations/              # Migraciones Alembic
  tests/                   # Unitarios e integración
frontend/
  src/domain/              # Modelos TypeScript
  src/infrastructure/      # Cliente HTTP y storage
  src/presentation/        # Páginas, componentes y polling
  src/app/                 # Configuración y router
docs/                      # Guía técnica, arquitectura y roadmap
dev.py                     # Atajo opcional de desarrollo
```

## Requisitos

Python 3.11+ y Node.js 20+ con npm. No se requiere Docker, Make ni servicios externos.

## Ejecución rápida

Desde la raíz:

```bash
python dev.py setup
python dev.py run
```

`setup` valida requisitos, instala dependencias si faltan, ejecuta `alembic upgrade head` y crea el restaurante demo de forma idempotente. `run` inicia backend y frontend; detenerlo con `Ctrl+C` termina ambos procesos.

También están disponibles `python dev.py test` para ejecutar los tests de backend y frontend.

## Ejecución manual

Backend:

```bash
cd backend
python -m venv .venv
# activar .venv según el sistema operativo
pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

Frontend, en otra terminal:

```bash
cd frontend
npm install
npm run dev
```

## Configuración y datos demo

Copia `.env.example` al directorio correspondiente (`backend/.env` y `frontend/.env`) o configura las variables directamente. Defaults:

```text
DATABASE_URL=sqlite:///./mesa247.db
CORS_ORIGINS=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000
```

La migración inicial crea `restaurants` y `queue_entries`, con índices, constraints y relación. La posición no se persiste: se calcula ordenando entradas `WAITING` por llegada. `python -m app.seed` crea tres restaurantes demo determinísticos: `1` La Terraza Azul (PE, America/Lima), `2` Cuatro Vientos (PE, America/Lima) y `3` Casa Mediterránea (CL, America/Santiago). No inserta datos de prueba en las migraciones.

Las fechas operativas se calculan en el timezone configurado del restaurante a partir de timestamps persistidos en UTC. El teléfono se normaliza a formato internacional (`+51...` o `+56...`) según el restaurante. El reporte diario está disponible en `GET /restaurants/{id}/reports/daily?date=YYYY-MM-DD` y calcula la espera media únicamente para entradas sentadas.

El reporte cuenta entradas (no personas): `joined_count` incluye todo ingreso del día local, `seated_count` estados `SEATED`, `cancelled_count` estados `CANCELLED` y `no_show_count` estados `NO_SHOW`. `average_wait_minutes` es el promedio de `seated_at - created_at` solo para entradas sentadas; si no hay ninguna devuelve `null`. El anfitrión puede usar `POST /queue/{entry_id}/seat`, y la cancelación/abandono usa `POST /queue/{entry_id}/cancel` (o `POST /queue/{entry_id}/no-show` tras una llamada).

## URLs útiles

Restaurantes del piloto: ID 1 **La Terraza Azul** (Lima), ID 2 **Cuatro Vientos** (Lima) e ID 3 **Casa Mediterránea** (Santiago).

- Comensal: http://localhost:5173/restaurants/1/join (también `/2/join` y `/3/join`)
- Anfitrión: http://localhost:5173/restaurants/1/host (también `/2/host` y `/3/host`)
- Reporte diario: http://localhost:5173/restaurants/1/reports/daily (también `/2/reports/daily` y `/3/reports/daily`)
- API health: http://localhost:8000/health
- Documentación API: http://localhost:8000/docs

## Tests

```bash
cd backend && pytest
cd ../frontend && npm test
```

El frontend también se verifica con `npm run build`.

## Despliegue futuro en Cloud Run

Se dejaron contenedores independientes y sus instrucciones en `backend/cloud/`
y `frontend/cloud/`. El backend usa el puerto `PORT` de Cloud Run; el frontend
se compila con `VITE_API_BASE_URL` y se sirve con Nginx. Para producción, el
backend debe usar una base administrada, porque el almacenamiento local de Cloud
Run es efímero.

## Decisiones y evolución

Se eligieron estado local y polling silencioso de 10 segundos para mantener el MVP pequeño y tolerante a conexiones inestables. Las vistas de comensal y anfitrión son rutas independientes; no existe un selector de rol en la interfaz. `call-next` usa lock de proceso y actualización condicional en SQLite; en MySQL se evolucionaría a una transacción con bloqueo de filas (`SELECT ... FOR UPDATE`) o equivalente atómico. La evolución prevista incluye autenticación/roles, estados completos, notificaciones desacopladas, WebSockets si el volumen lo justifica, MySQL y observabilidad.
