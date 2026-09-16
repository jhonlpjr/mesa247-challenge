# Mesa247 Waiting List — Arquitectura MVP

## 1. Principio
Arquitectura mínima orientada a un vertical slice end-to-end, evitando infraestructura que no aporte valor al piloto.

```text
Comensal React ─┐
                ├── HTTP/JSON ── FastAPI ── SQLAlchemy ── SQLite
Host React ─────┘                                  │
                                                  └─ MySQL (producción)
```

## 2. Componentes
### React
Dos experiencias dentro de la misma aplicación:
- vista del comensal;
- vista del anfitrión.

Responsabilidades:
- presentación;
- formularios y validación básica;
- consumo de API;
- polling;
- estados de carga/error.

No resuelve reglas de negocio ni concurrencia.

### FastAPI
Fuente de verdad del sistema.

Responsabilidades:
- validación;
- reglas de cola;
- cálculo de posición;
- transiciones de estado;
- protección ante operaciones concurrentes;
- persistencia.

### Base de datos
SQLite para la entrega local y MySQL como objetivo de producción.

## 3. Modelo mínimo

### Restaurant
- `id`
- `name`
- `created_at`

### QueueEntry
- `id`
- `restaurant_id`
- `name`
- `phone`
- `party_size`
- `status`
- `created_at`
- `called_at`

Relación:

```text
Restaurant 1 ───── N QueueEntry
```

La posición es derivada, no persistida.

## 4. API propuesta

### Comensal
`POST /restaurants/{restaurant_id}/queue`
Crea una entrada `WAITING`.

`GET /queue/{entry_id}`
Devuelve estado y posición actual.

### Anfitrión
`GET /restaurants/{restaurant_id}/queue`
Devuelve la cola activa ordenada por llegada.

`POST /restaurants/{restaurant_id}/queue/call-next`
Selecciona de forma segura el siguiente `WAITING`, lo cambia a `CALLED` y registra `called_at`.

## 5. Concurrencia
El caso crítico es que dos anfitriones ejecuten `call-next` simultáneamente.

La garantía debe residir en backend/BD, no en React. La implementación local será simple y compatible con SQLite; para MySQL se utilizaría una transacción/bloqueo o actualización condicional que impida reclamar dos veces la misma entrada.

## 6. Actualización de vistas
Polling silencioso de 10 segundos:

```text
React ── GET cola ──> API
      <── estado ────
          ...
      ── GET cola ──> API
```

Las mutaciones fuerzan además un refetch inmediato.

WebSockets quedan como evolución si el piloto demuestra necesidad de realtime estricto.

## 7. WhatsApp futuro
La integración debe quedar desacoplada del dominio:

```text
CallNext
   │
   ├── actualiza QueueEntry
   │
   └── evento/notificación
             │
        NotificationService
             │
      WhatsApp Provider
       ├─ Meta
       └─ Twilio
```

El proveedor no debe formar parte de la regla de negocio de la cola.

## 8. Evolución a producción
Despliegue previsto:
- frontend estático/CDN;
- FastAPI en Cloud Run;
- MySQL administrado;
- secretos fuera del repositorio;
- logs estructurados;
- health checks;
- métricas de latencia/error;
- tracing/correlation ID cuando el volumen lo justifique.

## 9. Decisiones difíciles de revertir
Se evita acoplar:
- cola a WhatsApp/proveedor;
- posición a una columna persistida;
- consistencia al estado del frontend;
- dominio a SQLite.

Las decisiones deliberadamente simples —polling y monolito pequeño— son fáciles de evolucionar.


## 10. Clean Architecture pragmática

La dirección de dependencias será:

```text
Presentation ──> Application ──> Domain
                      ↑
Infrastructure ───────┘
```

El **Domain** no conoce FastAPI, SQLAlchemy, SQLite/MySQL ni React.

El **Application layer** coordina casos de uso mediante interfaces de repositorio definidas hacia el núcleo.

**Infrastructure** implementa esas interfaces utilizando SQLAlchemy.

**Presentation** transforma HTTP/JSON en llamadas a casos de uso.

Esto permite cambiar SQLite por MySQL o incorporar WhatsApp posteriormente sin mover las reglas centrales de la cola.

No se crearán capas, factories o patrones adicionales si no resuelven una necesidad concreta del MVP.

### Flujo de ejemplo

```text
POST /restaurants/{id}/queue/call-next
                 │
          QueueController
                 │
          CallNextUseCase
                 │
       QueueRepository (port)
                 │
     SQLAlchemyQueueRepository
                 │
              Database
```

## 11. Estrategia de testing

```text
Unit tests
    │
    ├── Domain/Application
    │     ├── join queue
    │     ├── calculate position
    │     ├── call next
    │     └── invalid transitions
    │
Integration tests
    │
    └── Repository + SQLite
    │
API smoke/integration
          └── endpoints críticos
```

La mayor inversión estará en tests unitarios de reglas y casos de uso. Los tests de infraestructura se limitarán a comportamientos que realmente dependan de la base de datos, especialmente persistencia y concurrencia.
