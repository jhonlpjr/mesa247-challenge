# Entregable 3 --- Conversaciones con IA

## Parte 2: Backend

> **Nota sobre el recorte**
>
> La conversación fue recortada únicamente para excluir contenido previo
> no relacionado con la prueba técnica, navegación inicial, lectura o
> reproducción del enunciado, metadatos de la herramienta y mensajes
> administrativos o repetitivos que no aportan al proceso técnico.
>
> Los intercambios incluidos relacionados con el análisis, toma de
> decisiones, implementación y revisión de la prueba se mantienen en su
> contenido original, sin reescrituras.

# Implementación base

## Usuario

Implementa el **backend MVP completo de Mesa247 Waiting List** siguiendo
los documentos del proyecto como fuente de verdad:

-   `docs/TECHNICAL_GUIDE.md`
-   `docs/ARCHITECTURE.md`
-   `docs/ROADMAP.md`

Antes de modificar código, léelos completos.

## Objetivo

Construir el vertical slice:

**Comensal entra a la cola → consulta su posición → anfitrión visualiza
la cola → anfitrión llama al siguiente comensal.**

Prioriza simplicidad, corrección y mantenibilidad. Es una prueba técnica
con tiempo limitado: quiero código con criterio de producción, pero sin
sobrearquitectura.

## Stack obligatorio

-   Python
-   FastAPI
-   SQLAlchemy
-   Pydantic
-   SQLite para desarrollo local
-   Alembic para migraciones
-   pytest

La arquitectura debe permitir posteriormente sustituir SQLite por MySQL
sin modificar dominio ni casos de uso.

## Arquitectura

Implementa Clean Architecture pragmática:

`Presentation → Application → Domain`

Infrastructure implementa los contratos/ports requeridos por el núcleo.

Estructura base:

``` text
backend/
├── app/
│   ├── domain/
│   │   ├── entities/
│   │   ├── enums/
│   │   └── repositories/
│   ├── application/
│   │   └── use_cases/
│   ├── infrastructure/
│   │   ├── database/
│   │   │   └── models/
│   │   └── repositories/
│   ├── presentation/
│   │   ├── routes/
│   │   └── schemas/
│   └── main.py
├── migrations/
├── tests/
│   ├── unit/
│   └── integration/
├── alembic.ini
└── .env.example
```

Puedes realizar pequeños ajustes si existe una razón técnica concreta.

## Separación de responsabilidades

Mantén límites claros también a nivel de archivos.

No concentres entidades, interfaces, enums, constantes, DTOs, modelos
ORM, repositorios y casos de uso diferentes en archivos genéricos.

Ejemplos:

-   `queue_entry.py`: entidad de dominio
-   `queue_status.py`: enum
-   `queue_repository.py`: port/interface
-   `call_next.py`: caso de uso
-   `queue_entry_model.py`: modelo SQLAlchemy
-   `sqlalchemy_queue_repository.py`: implementación
-   schemas HTTP dentro de `presentation/schemas`

Una entidad de dominio NO es un modelo SQLAlchemy.

Un schema Pydantic NO es una entidad de dominio.

Una interface/port NO debe mezclarse con su implementación SQLAlchemy.

Las routes deben ser delgadas y delegar las reglas a application/use
cases.

No apliques ciegamente "una clase por archivo"; agrupa únicamente
elementos que realmente pertenezcan a una misma responsabilidad.

## Modelo

Implementa como mínimo:

### Restaurant

-   `id`
-   `name`
-   `created_at`

### QueueEntry

-   `id`
-   `restaurant_id`
-   `name`
-   `phone`
-   `party_size`
-   `status`
-   `created_at`
-   `called_at`

Estados MVP:

-   `WAITING`
-   `CALLED`

`called_at` debe ser nullable hasta que el comensal sea llamado.

La posición NO debe persistirse. Debe calcularse a partir de las
entradas activas `WAITING`, ordenadas por llegada.

## Casos de uso

Implementa:

### JoinQueue

Registra un comensal en estado `WAITING`.

Valida como mínimo los campos necesarios y un `party_size` válido.

### GetQueueEntry

Obtiene el estado actual del comensal y, cuando corresponda, su posición
actual.

### GetRestaurantQueue

Devuelve la cola activa del restaurante ordenada correctamente.

### CallNext

Selecciona el primer comensal elegible en estado `WAITING`.

Realiza:

`WAITING → CALLED`

y registra:

`called_at = current timestamp`

La operación debe diseñarse para impedir que dos anfitriones puedan
llamar exitosamente al mismo comensal ante solicitudes concurrentes.

Ten presente que localmente usamos SQLite pero producción podría
utilizar MySQL.

No soluciones la concurrencia únicamente en frontend.

Si SQLite impone alguna limitación respecto a la estrategia que
usaríamos en MySQL, implementa una solución local correcta y documenta
brevemente cómo evolucionaría en MySQL, por ejemplo mediante
transacción/locking/actualización condicional según corresponda.

## API

Implementa endpoints equivalentes a:

`POST /restaurants/{restaurant_id}/queue`

Agregar comensal.

`GET /queue/{entry_id}`

Consultar estado/posición del comensal.

`GET /restaurants/{restaurant_id}/queue`

Consultar cola activa para anfitrión.

`POST /restaurants/{restaurant_id}/queue/call-next`

Llamar al siguiente comensal.

También:

`GET /health`

para health check.

Utiliza códigos HTTP y respuestas de error coherentes.

## SQLite y migraciones

Configura SQLite mediante SQLAlchemy.

NO dependas de `create_all()` como mecanismo principal de evolución del
esquema.

Configura **Alembic** correctamente.

Genera una migración inicial que cree las tablas necesarias, índices,
constraints y relaciones correspondientes.

Debe poder ejecutarse:

``` bash
alembic upgrade head
```

sobre una base vacía y dejarla lista para ejecutar la aplicación.

Incluye una forma simple y documentada de disponer de al menos un
restaurante para probar el MVP. Puede ser seed explícito o mecanismo
equivalente, pero no mezcles datos de prueba con las migraciones
estructurales salvo que exista una razón justificada.

La URL de BD debe ser configurable mediante environment.

Incluye `.env.example`.

## Tests

Prioriza tests sobre reglas importantes, no cobertura artificial.

Unit tests de application/domain usando fake/in-memory repositories
cuando tenga sentido:

-   nuevo comensal entra como `WAITING`;
-   posición respeta orden de llegada;
-   `call-next` selecciona el primero elegible;
-   transición `WAITING → CALLED`;
-   `called_at` queda registrado;
-   una entrada ya llamada no vuelve a seleccionarse.

Agrega integration tests mínimos para:

-   repositorio SQLAlchemy + SQLite;
-   endpoints críticos;
-   persistencia;
-   comportamiento de `call-next`;
-   protección contra doble llamada dentro de las capacidades del
    entorno local.

Mantén unit tests independientes de FastAPI y SQLAlchemy siempre que
corresponda.

## Configuración

Configura:

-   FastAPI;
-   SQLAlchemy;
-   SQLite;
-   Alembic;
-   CORS para desarrollo;
-   variables de entorno;
-   pytest.

Mantén `main.py` y las routes simples.

## Fuera del alcance

NO implementar:

-   WhatsApp real ni simulado;
-   WebSockets;
-   autenticación;
-   drag & drop;
-   reportes;
-   emails;
-   integración PHP;
-   Celery/workers;
-   Redis;
-   infraestructura cloud;
-   lógica avanzada de no-show;
-   estados adicionales que el MVP todavía no utiliza.

La tolerancia de 10 minutos podrá derivarse posteriormente de
`called_at`; no agregues scheduler para esto.

## Verificación final

Antes de terminar:

1.  Ejecuta las migraciones sobre una BD limpia.
2.  Ejecuta todos los tests.
3.  Verifica que FastAPI inicie.
4.  Revisa la dirección de dependencias entre capas.
5.  Comprueba que domain no importe FastAPI, SQLAlchemy ni Pydantic.
6.  Comprueba que presentation no contenga reglas de negocio.
7.  Comprueba que los modelos ORM estén separados de las entidades.
8.  Revisa imports, código muerto y archivos innecesarios.
9.  No amplíes el alcance.

Finalmente dame un resumen corto con:

-   qué implementaste;
-   estructura principal creada;
-   resultado de migraciones;
-   resultado de tests;
-   cómo ejecutar localmente;
-   decisiones/tradeoffs relevantes, especialmente SQLite vs MySQL para
    concurrencia.

No continúes agregando funcionalidades fuera de este alcance.

## Codex

Implementé el backend MVP completo en
\[backend\]\\(C:/Repositorio/Me/GIT/mesa247-challenge/backend):

-   Clean Architecture: domain, application, infrastructure y
    presentation.
-   Endpoints de registro, consulta, cola activa, `call-next` y health
    check.
-   SQLAlchemy + SQLite configurable por `DATABASE_URL`.
-   Migración Alembic inicial con relaciones, índices y constraints.
-   Seed explícito mediante `python -m app.seed`.
-   Tests unitarios e integración, incluyendo protección contra doble
    llamada concurrente.
-   CORS y `.env.example`.
-   Documentación en
    \[backend/README.md\]\\(C:/Repositorio/Me/GIT/mesa247-challenge/backend/README.md).

La migración está en `migrations/versions/0001_initial.py` y se ejecuta
con:

``` text
cd backend
alembic upgrade head
```

No pude ejecutar Alembic ni pytest porque el entorno no tiene un
intérprete Python funcional instalado; solo está disponible el alias de
Microsoft Store. La revisión estática pasó y confirmó que el dominio no
depende de frameworks externos.

La concurrencia local usa lock de proceso más actualización condicional.
Para MySQL queda documentado evolucionar a una transacción con
`SELECT ... FOR UPDATE`.

------------------------------------------------------------------------

# Evoluciones y correcciones posteriores

## Usuario

ERROR: Exception in ASGI application Traceback (most recent call last):
File "C...

errores

## Codex

Corregido.

El error era:

``` text
NameError: name 'restaurant' is not defined
```

En `GetRestaurantQueue` se validaba el restaurante, pero no se guardaba
el resultado antes de acceder a `restaurant.timezone`.

Ahora se obtiene correctamente:

``` text
restaurant = self.restaurants.get(restaurant_id)
```

Reinicia el backend para que Uvicorn recargue el cambio:

``` text
python dev.py run
```

Luego vuelve a consultar:

``` text
GET /restaurants/1/queue
```

El error no estaba relacionado con la migración ni con SQLite.

## Usuario

se esta guardando pais por cada restaurante?

## Codex

Sí. Cada restaurante guarda su propia configuración:

-   `country_code`
-   `phone_country_code`
-   `timezone`

Estos campos están en la tabla `restaurants`, se agregan mediante la
migración `0002` y se exponen mediante:

``` text
GET /restaurants/{restaurant_id}
```

Además, el teléfono se normaliza usando el `phone_country_code` del
restaurante, no un prefijo enviado arbitrariamente desde el frontend.

## Usuario

Revisa el backend actual de Mesa247 y determina primero si el **Reporte
del Día** mostrado en el prototipo ya está soportado completa o
parcialmente.

Usa como fuente de verdad:

-   código actual;
-   `docs/TECHNICAL_GUIDE.md`;
-   `docs/ARCHITECTURE.md`;
-   `docs/ROADMAP.md`;
-   modelo funcional del prototipo.

NO asumas que falta todo y NO dupliques implementaciones existentes.

\[En la copia original compartida, el resto de este prompt aparece
truncado por la interfaz.\]

## Codex

El Reporte del Día estaba soportado parcialmente:

-   Ya existían estados, timestamps, transición a `SEATED`, cancelación,
    caso de uso y endpoint.
-   Faltaban filtro temporal eficiente por límites UTC, endpoint
    `NO_SHOW`, manejo correcto de transiciones inválidas y cobertura
    completa.

Implementé:

-   Reporte aislado por `restaurant_id + día local`.
-   Conversión correcta de fecha local a rango UTC antes de consultar la
    BD.
-   Métricas según la semántica solicitada.
-   `average_wait_minutes` solo para entradas `SEATED`.
-   `null` cuando no hay datos suficientes.
-   Endpoint:

``` text
GET /restaurants/{restaurant_id}/reports/daily?date=YYYY-MM-DD
```

-   Endpoint adicional:

``` text
POST /queue/{entry_id}/no-show
```

-   Corrección de errores `409` para transiciones inválidas.
-   Repositorio con consulta temporal `entries_between`.
-   README actualizado con definiciones y estrategia temporal.

La migración `0002` ya contiene los campos y estados necesarios. El
backend debe validarse localmente con:

``` text
cd backend
alembic upgrade head
pytest
```

No pude ejecutar Python desde este entorno de agente, pero corregí el
error concreto del reporte mostrado en el traceback.
