# Mesa247 Waiting List

Mesa247 es una lista de espera digital para restaurantes. El vertical slice obligatorio permite que un comensal se registre, el anfitrión visualice la cola y llame al siguiente grupo.

## Alcance

El CORE priorizado es:

**Comensal se une → anfitrión ve la cola → anfitrión llama al siguiente.**

Incluye además extensiones demostrativas fuera del vertical slice obligatorio: consulta de estado/posición, sentar/cancelar, no-show, reporte diario, polling, persistencia local, drag & drop en la vista del anfitrión y representación de notificación WhatsApp mediante enlace `wa.me`.

No incluye autenticación, WhatsApp automatizado, WebSockets ni emails.

## Requisitos

* Python 3.11+
* Node.js 20+
* npm

No se requiere Docker, Make ni servicios externos.

## Ejecución rápida

Desde la raíz:

```bash
python dev.py setup
python dev.py run
```

`setup` valida requisitos, instala dependencias si faltan, ejecuta `alembic upgrade head` y crea los restaurantes demo de forma idempotente.

`run` inicia backend y frontend. `Ctrl+C` termina ambos procesos.

También está disponible:

```bash
python dev.py test
```

para ejecutar los tests de backend y frontend.

## URLs útiles

Restaurantes del piloto:

* ID `1` — **La Terraza Azul** (Lima)
* ID `2` — **Cuatro Vientos** (Lima)
* ID `3` — **Casa Mediterránea** (Santiago)

Para probar rápidamente con La Terraza Azul:

* Comensal: http://localhost:5173/restaurants/1/join
* Anfitrión: http://localhost:5173/restaurants/1/host
* Reporte diario: http://localhost:5173/restaurants/1/reports/daily
* API health: http://localhost:8000/health
* Documentación API: http://localhost:8000/docs

Las mismas vistas están disponibles para los restaurantes `2` y `3` cambiando el ID en la URL.

### QR para pruebas

Los códigos QR de prueba se encuentran en `docs/PROJECT/qr/`:

- `Restaurante_1_QR.png` → La Terraza Azul → `/restaurants/1/join`
- `Restaurante_2_QR.png` → Cuatro Vientos → `/restaurants/2/join`
- `Restaurante_3_QR.png` → Casa Mediterránea → `/restaurants/3/join`

## Probar el flujo principal

1. Abrir `http://localhost:5173/restaurants/1/join`.
2. Registrar un comensal con nombre, teléfono y cantidad de personas.
3. Abrir `http://localhost:5173/restaurants/1/host`.
4. Verificar que el comensal aparece en la cola.
5. Pulsar **Llamar siguiente**.
6. Verificar que el comensal cambia de estado y deja de ocupar una posición `WAITING`.

Con estos pasos se valida el vertical slice solicitado de punta a punta.

## Stack y arquitectura

* Frontend: React, TypeScript, Vite, React Router, Fetch API y Vitest.
* Backend: Python, FastAPI, Pydantic y SQLAlchemy.
* Persistencia: SQLite local con Alembic; el modelo queda preparado para MySQL.

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

## Ejecución manual

### Backend

```bash
cd backend
python -m venv .venv

# activar .venv según el sistema operativo

pip install -r requirements.txt
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload --port 8000
```

### Frontend

En otra terminal:

```bash
cd frontend
npm install
npm run dev
```

## Configuración y datos demo

Copia `.env.example` al directorio correspondiente (`backend/.env` y `frontend/.env`) o configura las variables directamente.

Defaults:

```text
DATABASE_URL=sqlite:///./mesa247.db
CORS_ORIGINS=http://localhost:5173
VITE_API_BASE_URL=http://localhost:8000
```

La migración inicial crea `restaurants` y `queue_entries`, con índices, constraints y relación.

La posición no se persiste: se calcula ordenando entradas `WAITING` por llegada.

`python -m app.seed` crea tres restaurantes demo determinísticos:

* `1` — La Terraza Azul (PE, America/Lima)
* `2` — Cuatro Vientos (PE, America/Lima)
* `3` — Casa Mediterránea (CL, America/Santiago)

No se insertan datos de prueba en las migraciones.

Las fechas operativas se calculan en el timezone configurado del restaurante a partir de timestamps persistidos en UTC. El teléfono se normaliza a formato internacional (`+51...` o `+56...`) según el restaurante.

El reporte diario está disponible en:

```text
GET /restaurants/{id}/reports/daily?date=YYYY-MM-DD
```

El reporte cuenta entradas, no personas:

* `joined_count`: todo ingreso del día local.
* `seated_count`: entradas en estado `SEATED`.
* `cancelled_count`: entradas en estado `CANCELLED`.
* `no_show_count`: entradas en estado `NO_SHOW`.
* `average_wait_minutes`: promedio de `seated_at - created_at` únicamente para entradas sentadas; devuelve `null` si no existen.

El anfitrión puede usar:

```text
POST /queue/{entry_id}/seat
POST /queue/{entry_id}/cancel
POST /queue/{entry_id}/no-show
```

`no-show` aplica después de una llamada.

## Tests

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
```

El frontend también se verifica mediante:

```bash
npm run build
```

Desde la raíz puede ejecutarse el conjunto mediante:

```bash
python dev.py test
```

Los tests se concentran en las reglas críticas del flujo, evitando buscar cobertura artificial.

## Preparación para Cloud Run

Se dejaron contenedores independientes y sus instrucciones en:

```text
backend/cloud/
frontend/cloud/
```

El backend utiliza el puerto `PORT` proporcionado por Cloud Run.

El frontend se compila utilizando `VITE_API_BASE_URL` y se sirve mediante Nginx.

Para producción, el backend debe utilizar una base de datos administrada, ya que el almacenamiento local de Cloud Run es efímero. Las migraciones se ejecutarían como una operación controlada y no durante el arranque de cada instancia.

## Decisiones y evolución

Se eligieron estado local y polling silencioso de 10 segundos para mantener el MVP pequeño y tolerante a conexiones inestables.

Las vistas de comensal y anfitrión son rutas independientes; no existe un selector de rol en la interfaz.

`call-next` usa lock de proceso y actualización condicional en SQLite. En MySQL evolucionaría a una transacción con bloqueo de filas (`SELECT ... FOR UPDATE`) o una operación atómica equivalente.

La evolución prevista incluye:

* autenticación y roles;
* estados completos;
* notificaciones desacopladas;
* WebSockets si el volumen lo justifica;
* MySQL;
* observabilidad.

## Documentación adicional

La carpeta `docs/` contiene documentación complementaria sobre arquitectura, decisiones técnicas, notificaciones y evolución del MVP.
