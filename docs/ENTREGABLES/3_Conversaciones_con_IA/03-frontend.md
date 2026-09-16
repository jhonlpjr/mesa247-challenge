# Entregable 3 --- Conversaciones con IA

## Parte 3: Frontend

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

Implementa el **frontend MVP completo de Mesa247 Waiting List**.

Antes de modificar código, lee y utiliza como fuente de verdad:

-   `docs/TECHNICAL_GUIDE.md`
-   `docs/ARCHITECTURE.md`
-   `docs/ROADMAP.md`

También revisa los contratos/endpoints realmente implementados en el
backend antes de crear el cliente HTTP. No inventes contratos si ya
existen.

## Objetivo

Implementar el vertical slice:

**Comensal entra a la cola → visualiza su posición/estado → anfitrión
visualiza la cola → anfitrión llama al siguiente comensal.**

El frontend debe ser funcional, responsive y suficientemente cuidado
para una prueba técnica, sin invertir tiempo en diseño visual
innecesariamente complejo.

## Stack

-   React
-   TypeScript
-   Vite
-   React Router
-   Fetch API o una abstracción HTTP pequeña y justificada
-   Vitest
-   React Testing Library cuando corresponda

No agregues Redux, Zustand, React Query/TanStack Query u otras
dependencias salvo que exista una necesidad concreta que justifique su
costo para este MVP.

Prefiere herramientas nativas y estado local.

## Arquitectura

Mantén la separación pragmática definida en la documentación.

Estructura conceptual:

``` text
src/
├── domain/
│   └── models/
├── application/
│   └── services/
├── infrastructure/
│   └── api/
├── presentation/
│   ├── components/
│   ├── hooks/
│   └── pages/
├── app/
│   ├── router/
│   └── config/
└── main.tsx
```

Puedes hacer pequeños ajustes si mejoran realmente la organización.

No reproduzcas Clean Architecture de backend de forma artificial en
React. Mantén únicamente separaciones que aporten claridad.

## Separación de responsabilidades

Esta regla es importante.

Evita archivos grandes que mezclen:

-   modelos;
-   tipos;
-   constantes;
-   acceso HTTP;
-   hooks;
-   componentes;
-   páginas;
-   lógica de transformación;
-   configuración.

Cada archivo debe representar una responsabilidad cohesiva.

No apliques ciegamente "un elemento por archivo" si varios elementos
pequeños pertenecen claramente a la misma responsabilidad.

En particular:

-   las páginas coordinan la vista;
-   los componentes representan UI reutilizable;
-   los hooks encapsulan comportamiento React reutilizable;
-   `infrastructure/api` conoce HTTP;
-   los modelos de dominio no deben depender de React;
-   la URL del backend pertenece a configuración;
-   no realices `fetch()` directamente por toda la aplicación.

Evita componentes monolíticos con UI, polling, llamadas HTTP,
transformaciones y reglas mezcladas.

## Flujos

Implementa dos experiencias claramente diferenciadas.

### 1. Comensal

Debe existir una pantalla donde el comensal pueda ingresar a la cola
indicando los datos requeridos por el backend, como mínimo:

-   nombre;
-   teléfono;
-   cantidad de personas.

El restaurante podrá resolverse mediante la ruta o mediante el mecanismo
simple definido para el MVP.

Al enviar:

`POST /restaurants/{restaurant_id}/queue`

maneja:

-   loading;
-   éxito;
-   errores de validación;
-   errores de servidor.

Una vez registrado, muestra una vista clara con:

-   nombre;
-   cantidad de personas si aporta valor;
-   posición actual cuando esté `WAITING`;
-   estado actual;
-   indicación de que debe permanecer atento.

Mientras la entrada permanezca activa, consulta:

`GET /queue/{entry_id}`

mediante **polling aproximadamente cada 5--10 segundos**.

El polling debe:

-   limpiarse al desmontar el componente;
-   evitar timers duplicados;
-   manejar errores temporales razonablemente;
-   no bloquear permanentemente la interfaz;
-   actualizar inmediatamente cuando sea apropiado.

No implementar WebSockets.

Cuando el estado cambie a `CALLED`, la interfaz debe comunicar
claramente que el anfitrión lo ha llamado.

NO simules botones de WhatsApp como "Voy en camino" o "Ya no voy".

## 2. Anfitrión / Host

Implementa una vista de cola del restaurante.

Consume:

`GET /restaurants/{restaurant_id}/queue`

Muestra de forma clara como mínimo:

-   orden;
-   nombre;
-   cantidad de personas;
-   estado;
-   tiempo/hora de llegada si el backend lo proporciona.

Debe existir una acción principal:

**Llamar al siguiente**

que consuma:

`POST /restaurants/{restaurant_id}/queue/call-next`

Mientras se procesa:

-   evita múltiples clicks accidentales;
-   muestra estado de carga;
-   maneja cola vacía correctamente;
-   maneja errores del backend.

Después de una acción exitosa, refresca inmediatamente la cola.

Además, mantén la vista sincronizada mediante polling cada
aproximadamente **5--10 segundos**, porque puede existir más de un
anfitrión usando el sistema.

El backend sigue siendo la fuente de verdad.

No intentes resolver concurrencia únicamente desde frontend.

## Navegación

Mantén rutas simples y entendibles.

Por ejemplo, conceptualmente:

`/restaurants/:restaurantId/join`

para comensal.

`/queue/:entryId`

para seguimiento.

`/restaurants/:restaurantId/host`

para anfitrión.

Puedes adaptar los nombres si existe una estructura previa mejor.

No implementar autenticación para el host en este MVP.

## Persistencia del seguimiento

Si aporta simplicidad al flujo, puedes conservar el `entryId` necesario
para recuperar el seguimiento después de refresh utilizando
`localStorage`.

Hazlo mediante una pequeña abstracción y no distribuyas acceso directo a
`localStorage` por distintos componentes.

No almacenes información innecesaria.

El backend continúa siendo la fuente de verdad.

## UX

Prioriza:

-   claridad;
-   jerarquía visual;
-   responsive;
-   uso cómodo desde móvil para el comensal;
-   uso cómodo desde tablet para el anfitrión;
-   feedback inmediato de acciones;
-   estados vacíos;
-   estados loading;
-   estados error.

La prueba menciona conectividad potencialmente inestable, por lo que la
interfaz no debe romperse ante un fallo temporal de polling.

Un error temporal debe poder recuperarse en el siguiente ciclo.

No implementes una UI excesivamente elaborada.

## CSS

Utiliza una estrategia simple y consistente.

Si el proyecto ya tiene una solución de estilos, reutilízala.

Si parte desde cero, evita incorporar un framework pesado únicamente
para este MVP. CSS Modules, CSS convencional organizado o una solución
equivalente simple son suficientes.

Mantén estilos separados de la lógica cuando corresponda.

## Configuración

La URL de la API debe configurarse mediante environment:

`VITE_API_BASE_URL`

Incluye o actualiza:

`.env.example`

No hardcodees URLs del backend dentro de componentes.

## Tipado

Evita `any`.

Los contratos HTTP deben estar correctamente tipados.

Cuando tenga sentido, diferencia entre:

-   modelos utilizados por la aplicación;
-   request/response DTOs provenientes de la API.

No generes capas de mapping innecesarias si las estructuras son
idénticas y no existe beneficio real.

## Tests

Prioriza comportamiento importante sobre cobertura artificial.

Implementa tests fundamentales como mínimo para:

-   formulario de ingreso;
-   validaciones básicas;
-   ingreso exitoso a la cola;
-   visualización de posición;
-   cambio visual de `WAITING` a `CALLED`;
-   cola del host;
-   acción `call-next`;
-   estado de cola vacía;
-   manejo básico de error.

Para polling, prueba el comportamiento importante usando fake timers
cuando corresponda, sin crear tests frágiles dependientes de tiempos
reales.

No pruebes detalles internos de implementación si puedes probar
comportamiento observable.

## Fuera del alcance

NO implementar:

-   WhatsApp;
-   botones falsos de WhatsApp;
-   WebSockets;
-   autenticación;
-   Redux;
-   drag & drop;
-   reportes;
-   emails;
-   integración PHP;
-   analytics;
-   service workers/offline mode;
-   notificaciones push;
-   funcionalidades no soportadas por el backend.

## Integración

Antes de finalizar, verifica el frontend contra los contratos reales del
backend.

No asumas nombres de propiedades si puedes comprobarlos en el código
existente.

Comprueba manualmente el flujo:

1.  comensal entra a la cola;
2.  recibe su posición;
3.  host visualiza al comensal;
4.  entra un segundo comensal;
5.  ambos aparecen en orden;
6.  host llama al siguiente;
7.  primera entrada cambia a `CALLED`;
8.  segundo comensal actualiza su posición;
9.  dos vistas host terminan reflejando el mismo estado;
10. refresh no rompe el flujo básico de seguimiento.

## Revisión final

Antes de terminar:

1.  Ejecuta tests.
2.  Ejecuta build de producción.
3.  Revisa errores TypeScript.
4.  Revisa imports.
5.  Elimina código muerto.
6.  Revisa timers del polling.
7.  Revisa estados loading/error/empty.
8.  Verifica que no haya `fetch()` dispersos por componentes.
9.  Verifica separación de responsabilidades.
10. No amplíes el alcance.

Finalmente entrega un resumen breve indicando:

-   qué implementaste;
-   estructura principal;
-   rutas creadas;
-   integración con backend;
-   estrategia de polling;
-   resultado de tests;
-   resultado del build;
-   comandos para ejecutar localmente;
-   cualquier decisión o tradeoff relevante.

No continúes agregando funcionalidades fuera del MVP.

## Codex

Implementé el frontend MVP completo en
\[frontend\]\\(C:/Repositorio/Me/GIT/mesa247-challenge/frontend).

Incluye:

-   Rutas:
    -   `/restaurants/:restaurantId/join`
    -   `/queue/:entryId`
    -   `/restaurants/:restaurantId/host`
-   Cliente HTTP tipado conectado al backend existente.
-   Flujo de ingreso, seguimiento y llamada del siguiente.
-   Polling cada 8 segundos con limpieza de timers.
-   Persistencia del `entryId` mediante localStorage encapsulado.
-   Estados loading, error, vacío y éxito.
-   Diseño responsive para móvil y tablet.
-   Tests con Vitest y Testing Library.
-   Configuración mediante `VITE_API_BASE_URL`.
-   CSS separado y sin dependencias de estado global.

Verificación:

-   Tests: 2 archivos, 2 tests pasando.
-   Build de producción: correcto.
-   `fetch()` centralizado en `infrastructure/api/http.ts`.
-   No se agregaron WebSockets, autenticación, WhatsApp ni
    funcionalidades fuera del MVP.

Ejecución local:

``` text
cd frontend
npm install
cp .env.example .env
npm run dev
```

Con backend activo en `http://localhost:8000`.

------------------------------------------------------------------------

# Ajustes posteriores

## Usuario

bien de acuerdo a eso se debe controlar su prefijo code visual ademas
que se debe verificar que el input solo admina numeros y limite numerico
para telefonos

## Codex

Ajusté el formulario telefónico:

-   El prefijo ahora se obtiene desde el restaurante mediante
    `GET /restaurants/{id}`.
-   El prefijo se muestra visualmente como un bloque no editable.
-   El usuario solo puede ingresar números.
-   Se limita la longitud a 9 dígitos para los restaurantes demo.
-   Se eliminan automáticamente espacios, letras y símbolos.
-   Antes de enviar, el frontend combina prefijo y número:

``` text
+51 + 987654321 = +51987654321
```

-   El backend continúa validando y normalizando nuevamente de forma
    autoritativa.

También actualicé los tests.

Verificación:

-   Tests frontend: 2/2 pasando.
-   Build frontend: correcto.

## Usuario

actualiza la doc y las referenciuas porque no esta claro para reporte
adicional no debe haber un sleector comensal anfitrion ya que cada ista
es independiente la tabla de la cola activa debe actualzarse cada 10
segundos y no debe mostrarse el mensaje literal que lo esta haciendo no
debe mostrarse como error el que no haya elementos de la cola ya que eso
no es error es solo que no no hay clientes en espera , ese mensaje solo
debe ser para casos de errores

## Codex

Actualicé la documentación y el comportamiento de la interfaz:

-   Eliminé el selector de navegación "Comensal / Anfitrión".
-   Cada vista queda como ruta independiente:
    -   `/restaurants/:id/join`
    -   `/queue/:entryId`
    -   `/restaurants/:id/host`
-   La cola del anfitrión se actualiza silenciosamente cada 10 segundos.
-   Eliminé el texto visible "Actualizada automáticamente...".
-   La cola vacía ahora muestra un estado informativo normal:
    -   "La cola está vacía"
    -   "Los nuevos comensales aparecerán aquí."
-   El mensaje rojo solo aparece cuando existe un error real de API o
    conectividad.
-   Actualicé `README.md`, `TECHNICAL_GUIDE.md`, `ARCHITECTURE.md` y
    `ROADMAP.md` para reflejar polling silencioso de 10 segundos y
    vistas independientes.
-   Actualicé el test de polling.

Verificación:

-   Tests frontend: 2/2 pasando.
-   Build frontend: correcto.

## Usuario

se quito el drag and drop para el orden cuando en el prototipo si lo
tiene le haz quitado hasta datos de tiemp en espera promedio

## Codex

Corregido:

-   Restaurado el drag & drop visual en la cola del anfitrión.

-   Restaurado el resumen:

    `X en cola · espera media Y min`

-   La espera media se calcula usando timestamps reales:

    -   `WAITING`: desde ingreso hasta ahora.
    -   `CALLED`: desde ingreso hasta `called_at`.

-   Se mantuvo la corrección de posiciones únicamente para entradas
    `WAITING`.

-   Documentación actualizada para reflejar estas extensiones.

Verificación:

-   Frontend tests: 2 pasaron.
-   Frontend build: correcto.
-   Backend tests: 5 pasaron previamente.

Nota: el drag & drop actual es visual/local; `call-next` continúa usando
el orden persistido del backend. La persistencia del orden requeriría
una decisión adicional de modelo de datos y migración.

## Usuario

los textos de estado deberian ser mas centrados

## Codex

Ajustado:

-   Texto del estado centrado dentro de la etiqueta.
-   Columna "Estado" centrada.
-   Ancho uniforme para las etiquetas de estado.

Build frontend verificado correctamente.

## Usuario

de accuerdo al diseño de la tabla deberia ser la data de numero en cola
y espera en la parte superior derecha suin boton superior de llamar al
siguiente

## Codex

Ajustado según el prototipo:

-   Eliminado el botón superior "Llamar al siguiente".

-   Movido el resumen al encabezado de la tabla, alineado a la derecha:

    `X en cola · espera media Y min`

-   Conservados los botones "Llamar" por cliente.

-   Manteniendo drag & drop y tiempos reales de espera.

-   Build y pruebas frontend verificados correctamente.

## Usuario

las cabeceras mas al centro

## Codex

Listo. Las cabeceras de todas las columnas ahora están centradas,
manteniendo los datos con su alineación actual.

Build verificado correctamente.

## Usuario

las demas filas /columnas tambien

## Codex

Listo. Ahora están centrados:

-   Número de posición.
-   Asa de arrastre.
-   Nombre y teléfono.
-   Grupo.
-   Tiempo de espera.
-   Estado.
-   Botones de acciones.

Build verificado correctamente.
