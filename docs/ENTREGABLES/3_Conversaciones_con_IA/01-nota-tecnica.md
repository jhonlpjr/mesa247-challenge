# Entregable 3 --- Conversaciones con IA

## Parte 1: Nota técnica y documentación base

> **Aclaración de trazabilidad**
>
> El intercambio inicial exacto en el que se solicitó generar la
> documentación base no pudo recuperarse íntegramente desde el enlace
> compartido. Para no presentar contenido reconstruido como una
> transcripción literal, el siguiente bloque se incluye únicamente como
> **contexto reconstruido** del punto de partida. No debe interpretarse
> como una copia textual del chat original.
>
> El resto de los intercambios recuperados se conserva según el material
> disponible.

## Contexto reconstruido del inicio

### Usuario --- reconstrucción

Revisa la descripción de esta prueba técnica en el link y ayúdame a
preparar el contenido base de la documentación del proyecto para poder
desarrollar la solución de forma ordenada.

Quiero que la documentación deje claro el alcance del MVP, la
arquitectura, las decisiones técnicas, qué queda fuera de alcance y un
roadmap de implementación. Dame la documentación lista para descargar y
usar como fuente de verdad durante el desarrollo.

### ChatGPT --- resumen reconstruido

A partir del análisis de la prueba se preparó la documentación base del
proyecto, organizada principalmente en:

-   `docs/TECHNICAL_GUIDE.md`: alcance funcional, vertical slice, stack,
    reglas principales, contratos y criterios de implementación.
-   `docs/ARCHITECTURE.md`: arquitectura React + FastAPI, separación de
    responsabilidades, persistencia SQLite local con evolución prevista
    a MySQL, posición derivada, concurrencia de `call-next`, polling y
    consideraciones de producción.
-   `docs/ROADMAP.md`: orden de implementación priorizando primero el
    flujo obligatorio de la prueba y dejando las extensiones fuera del
    núcleo del MVP.

Estos documentos se utilizaron posteriormente como fuente de verdad en
los prompts de implementación de backend y frontend enviados a Codex.

------------------------------------------------------------------------

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

## Conversación relevante

### Usuario

¿El reporte como vista en lugar de email debería ir en el Entregable 1 o
solamente documentado en el repositorio?

### Asistente

La decisión debe aparecer brevemente en la nota técnica porque forma
parte de las decisiones de alcance: para el MVP el reporte se presenta
como vista y el envío automático por email queda desacoplado para una
evolución posterior. El detalle técnico debe permanecer en la
documentación del repositorio.

### Usuario

¿Cloud Run debería quedar configurado porque en la demo se menciona que
el proyecto real corre ahí?

### Asistente

Sí. Conviene dejar el proyecto preparado para Cloud Run sin convertir la
prueba en un ejercicio de infraestructura. El backend puede quedar
containerizado y preparado para recibir `PORT`, configuración y secretos
por entorno. El frontend puede contar con su preset de contenedor/Nginx,
manteniendo el despliegue desacoplado.

### Usuario

¿Cloud Run sería parecido a ECS/Fargate?

### Asistente

Conceptualmente sí: ambos permiten ejecutar contenedores administrados.
Cloud Run es más serverless y opinionado; abstrae más infraestructura y
escala automáticamente. Para esta prueba basta con demostrar que los
servicios están preparados para ejecutarse correctamente en ese entorno.

## Versión consolidada de la nota técnica

### 1. Tres preguntas al diseñador y supuestos

1.  **¿Qué sucede si un comensal es llamado y no responde?**\
    Para el MVP se asume `WAITING → CALLED`, registrando `called_at`. La
    tolerancia de 10 minutos se comunica, pero no se implementa
    automatización de expiración.

2.  **¿La actualización de la cola necesita tiempo real estricto?**\
    Se asume que una demora de pocos segundos es aceptable. Se utiliza
    polling silencioso cada 10 segundos y actualización inmediata
    después de mutaciones. WebSockets quedan como evolución si el uso
    real lo justifica.

3.  **¿WhatsApp y el reporte deben ser automáticos?**\
    No se consideran parte del núcleo obligatorio. WhatsApp se resuelve
    inicialmente mediante enlace manual `wa.me` y el reporte diario como
    vista. La automatización mediante proveedor de WhatsApp/email queda
    desacoplada para una siguiente etapa.

### 2. Qué construir primero y qué cortar

El vertical slice prioritario es:

`Comensal se registra → entra a la cola → anfitrión visualiza la cola → llama al siguiente`

Estimación inicial:

  Parte                                                     Estimación
  ------------------------------------------------------- ------------
  Modelo y persistencia                                         30 min
  API y reglas de cola                                          60 min
  Vista del comensal                                            45 min
  Vista del anfitrión                                           45 min
  Tests críticos                                                30 min
  Integración, preparación Cloud Run, README y revisión         30 min

Como extensiones, solo si el tiempo lo permite: estado/posición del
comensal, sentar/cancelar/no-show, reporte diario, WhatsApp manual y
mejoras visuales del prototipo.

Fuera del núcleo: WhatsApp automático, emails automáticos, WebSockets,
integración con PHP legado y automatizaciones avanzadas de
no-show/reintentos.

### 3. Modelo de datos

**Restaurant** - `id` - `name` - configuración necesaria del restaurante

**QueueEntry** - `id` - `restaurant_id` - `name` - `phone` -
`party_size` - `status` - `created_at` - `called_at`

La relación es `Restaurant 1:N QueueEntry`.

La posición en cola se deriva de las entradas `WAITING` ordenadas por
llegada; no se persiste como un número mutable.

### 4. Qué devolvería al diseñador

Devolvería las pantallas funcionales junto con las decisiones y
ambigüedades encontradas durante la implementación. Aclararía qué
comportamientos son provisionales ---polling, WhatsApp manual y reporte
como vista--- y qué casos necesitan una decisión de producto antes de
evolucionar.

### 5. Decisiones difíciles de cambiar después

Evitaría acoplar el dominio de cola a un proveedor de WhatsApp/email,
persistir la posición como fuente de verdad, trasladar reglas de
consistencia al frontend o hacer que el dominio dependa de SQLite.

Los estados y sus transiciones sí deben tener semántica clara desde el
inicio porque afectan persistencia, reportes e integraciones futuras.

### 6. Cómo llevarlo a producción

Backend FastAPI containerizado y preparado para Cloud Run; base de datos
MySQL administrada; secretos y configuración fuera del repositorio.
Frontend Vite desplegable de forma independiente, con preset de
contenedor/Nginx disponible.

El pipeline mínimo sería: tests → build → imagen → deploy → health
check. Las migraciones deben ejecutarse de forma controlada y no
automáticamente en cada instancia.

Para detectar una caída un viernes a las 9 p. m. usaría health checks,
logs estructurados y métricas/alertas sobre disponibilidad, errores 5xx
y latencia. Un monitor externo puede verificar periódicamente el
endpoint de salud.

El objetivo es mantener una solución pequeña, observable y evolutiva sin
introducir infraestructura que el piloto todavía no necesita.
