# Mesa247 Waiting List — Guía Técnica MVP

## 1. Objetivo
Implementar el vertical slice obligatorio del sistema de lista de espera:

**Comensal se registra → entra a la cola → anfitrión visualiza la cola → anfitrión llama al siguiente comensal.**

El objetivo no es reproducir todo el producto diseñado, sino validar el núcleo operativo dentro de la restricción de 4 horas.

## 2. Stack
### Frontend
- React
- TypeScript
- Vite
- Fetch API o cliente HTTP liviano

### Backend
- Python
- FastAPI
- SQLAlchemy
- Pydantic

### Persistencia
- SQLite para ejecución local.
- MySQL como destino de producción según la infraestructura indicada.

SQLite reduce configuración durante la prueba sin condicionar el modelo de dominio.

## 3. Flujo MVP
### Comensal
1. Accede a la URL del restaurante.
2. Ingresa nombre, teléfono y cantidad de personas.
3. Se registra en la cola.
4. Visualiza su posición y estado.
5. La vista se actualiza periódicamente.

### Anfitrión
1. Accede a la cola del restaurante.
2. Visualiza comensales en espera.
3. Llama al siguiente.
4. El backend cambia `WAITING → CALLED`.
5. Se registra `called_at`.
6. Las demás vistas reciben el cambio mediante polling.

## 4. Estados
- `WAITING`: esperando ser llamado.
- `CALLED`: llamado por el anfitrión.

`called_at` permite controlar posteriormente la tolerancia de 10 minutos.

`CANCELLED`, `SEATED` y `NO_SHOW` están implementados como extensiones demostrativas fuera del vertical slice obligatorio. `ON_THE_WAY` queda para una iteración posterior.

## 5. Sincronización
El MVP utilizará polling silencioso cada **10 segundos**, además de refrescar inmediatamente después de cada operación. La vista de comensal y la vista de anfitrión son rutas independientes; la UI no incluye un selector de roles.

No se implementarán WebSockets en este corte. Para el volumen inicial, polling ofrece suficiente frescura con menor complejidad y mejor tolerancia a conexiones inestables.

La consistencia nunca dependerá del polling: el backend y la base de datos son la fuente de verdad.

## 6. Concurrencia
Dos anfitriones pueden operar sobre una misma cola. El backend debe garantizar que un mismo comensal no pueda ser llamado dos veces ante solicitudes concurrentes.

En producción con MySQL, la selección/actualización del siguiente comensal deberá ejecutarse mediante una operación transaccional o actualización condicional apropiada.

## 7. Posición
La posición no se almacena como un número fijo. Se calcula a partir de las entradas `WAITING`, ordenadas por llegada (`created_at ASC`).

## 8. Tolerancia de llamada
Al llamar:
- `status = CALLED`
- `called_at = current_timestamp`

Se consideran 10 minutos de tolerancia según el flujo comunicado al comensal. El MVP evita introducir workers o cron jobs únicamente para esta regla.

## 9. WhatsApp
La integración real queda fuera del primer corte porque introduce decisiones y dependencias adicionales. Actualmente solo se representa el flujo mediante un enlace `wa.me` que el anfitrión confirma manualmente:
- Meta, Twilio u otro proveedor;
- templates aprobados;
- costos por país;
- webhooks;
- retries y manejo de fallos;
- respuestas como “Voy en camino” / “Ya no voy”.

La lógica de cola no se acoplará a un proveedor concreto para permitir esta evolución posteriormente.

## 10. Validaciones y errores
Como mínimo:
- campos obligatorios;
- teléfono inválido;
- cantidad de personas inválida;
- restaurante/entrada inexistente;
- operación sobre estado no válido;
- errores inesperados.

## 11. Scope
### CORE obligatorio
- Registro del comensal.
- Cola activa del anfitrión.
- Llamar al siguiente.

### Extensiones demostrativas fuera del vertical slice obligatorio
- Consulta de posición/estado.
- Sentar, cancelar y no-show.
- Reporte diario.
- Enlace WhatsApp manual.
- Drag & drop visual en la cola del anfitrión.
- Polling.
- Protección ante llamadas simultáneas.
- Validaciones y errores básicos.

### Fuera del corte
- WhatsApp automatizado mediante Meta/Twilio.
- WebSockets.
- Emails.
- Integración con PHP legado.
- Flujo avanzado de no-show/reintentos.


## 12. Organización del código y Clean Architecture

El proyecto mantendrá separación de responsabilidades inspirada en **Clean Architecture**, aplicada de forma pragmática para no sobrearquitectar el MVP.

### Backend

```text
app/
├── domain/
│   ├── entities/
│   └── repositories/
├── application/
│   └── use_cases/
├── infrastructure/
│   ├── database/
│   └── repositories/
├── presentation/
│   ├── routes/
│   └── schemas/
└── main.py
```

- **domain:** entidades, estados y contratos sin dependencia de FastAPI/SQLAlchemy.
- **application:** casos de uso y reglas de negocio.
- **infrastructure:** persistencia e implementaciones concretas.
- **presentation:** endpoints HTTP y DTO/schemas de entrada/salida.

Las rutas FastAPI deben ser delgadas: validan/adaptan HTTP y delegan la lógica al caso de uso.

### Frontend

```text
src/
├── domain/
│   └── models/
├── application/
│   └── services/
├── infrastructure/
│   └── api/
├── presentation/
│   ├── components/
│   └── pages/
└── app/
```

Se mantendrá la misma intención de separación, evitando abstracciones innecesarias para una aplicación pequeña.

## 13. Unit tests fundamentales

Los tests se concentrarán en reglas de negocio con mayor riesgo, no en buscar cobertura artificial.

Prioridad:

1. Un nuevo comensal entra en estado `WAITING`.
2. La posición respeta el orden de llegada y solo considera entradas activas.
3. `call-next` selecciona al primer comensal elegible.
4. Al llamar se produce `WAITING → CALLED` y se registra `called_at`.
5. Un comensal ya llamado no puede ser reclamado nuevamente.
6. Dos operaciones concurrentes no deben producir una doble llamada.

Los casos de uso del application layer deberán poder probarse sin levantar el servidor HTTP. Se podrán utilizar repositorios fake/in-memory para tests unitarios y reservar los tests con SQLite para verificar integración con persistencia.
