# Mesa247 Waiting List — Roadmap MVP

## Objetivo
Entregar en aproximadamente 4 horas un vertical slice demostrable:

**Join queue → persistencia → host ve cola → call next → actualización de estado.**

## Fase 0 — Alcance y decisiones (20–30 min)
- Revisar flujo.
- Documentar 3 preguntas y supuestos.
- Definir scope IN/OUT.
- Confirmar estados mínimos.
- Definir contratos API y modelo.

**Salida:** alcance cerrado antes de programar.

## Fase 1 — Bootstrap y scaffolding (20–25 min)
### Backend
- Crear FastAPI.
- Crear scaffolding Clean Architecture pragmático: `domain`, `application`, `infrastructure`, `presentation`.
- Configurar SQLAlchemy + SQLite.
- Configurar CORS.
- Configurar pytest.

### Frontend
- Crear React + TypeScript + Vite.
- Separar `domain`, `application`, `infrastructure`, `presentation` y `app` sin sobrearquitectar.
- Configurar API base URL.
- Definir rutas/vistas.

**Salida:** frontend y backend ejecutándose localmente.

## Fase 2 — Backend vertical slice (50–65 min)
- `Restaurant`.
- `QueueEntry`.
- Estados `WAITING` / `CALLED`.
- Seed de restaurante.
- `POST /restaurants/{id}/queue`.
- `GET /queue/{id}`.
- `GET /restaurants/{id}/queue`.
- `POST /restaurants/{id}/queue/call-next`.
- Cálculo dinámico de posición.
- Manejo de errores.
- Protección básica de concurrencia.

**Salida:** flujo completo comprobable mediante API.

## Fase 3 — Vista comensal (30–40 min)
- Formulario.
- Nombre/teléfono/party size.
- Join queue.
- Pantalla de posición/estado.
- Polling silencioso cada 10 s.
- Loading/error states.

**Salida:** un usuario puede entrar y seguir su estado.

## Fase 4 — Vista anfitrión (30–40 min)
- Cola activa.
- Orden de llegada.
- Datos esenciales.
- “Llamar siguiente”.
- Refetch inmediato.
- Polling silencioso cada 10 s.

**Salida:** host opera la cola desde UI.

## Fase 5 — Tests y validación crítica (25–35 min)

### Unit tests prioritarios
- Join queue crea `WAITING`.
- Posición respeta orden de llegada.
- Call next selecciona correctamente.
- Transición `WAITING → CALLED`.
- Registro de `called_at`.
- Una entrada llamada no puede reclamarse otra vez.
- Caso crítico de concurrencia, dentro de las capacidades del motor local.

Los casos de uso se probarán aislados mediante repositorios fake/in-memory cuando corresponda.

### Validación end-to-end
Probar:
1. Usuario entra.
2. Host lo visualiza.
3. Segundo usuario entra.
4. Orden correcto.
5. Host llama al primero.
6. Estado cambia a `CALLED`.
7. Posición del segundo cambia.
8. Dos vistas host se sincronizan.
9. Intentos simultáneos no llaman dos veces al mismo usuario.
10. Refresh no pierde información.

Priorizar tests backend de reglas críticas si queda tiempo.

## Fase 6 — Entrega (20–30 min)
- README con instalación.
- Comandos de ejecución.
- Variables de entorno de ejemplo.
- Revisar documentos.
- Limpiar código/debug.
- Confirmar que el repo arranca desde cero.
- Registrar trade-offs y trabajo futuro.

## Fuera del vertical slice obligatorio
No comenzar salvo que el flujo obligatorio esté terminado:
- WhatsApp automatizado mediante Meta/Twilio.
- WebSockets.
- botones interactivos de WhatsApp (“Voy en camino” / “Ya no voy”).
- email;
- integración PHP;
- autenticación completa;
- infraestructura cloud;
- UI avanzada.

## Después del MVP
### Extensiones ya demostradas fuera del vertical slice
- Reporte diario.
- Estados `SEATED`, `CANCELLED` y `NO_SHOW`.
- Enlace WhatsApp manual mediante `wa.me`.
- Drag & drop visual en la cola del anfitrión.

### Iteración 2
- Ciclo completo `CALLED → ON_THE_WAY / CANCELLED / EXPIRED / SEATED`.
- Regla explícita de 10 minutos.
- WhatsApp mediante abstracción de proveedor.
- Webhooks.
- Idempotencia.

### Iteración 3
- WebSockets/eventos si los datos del piloto justifican realtime.
- Integración con sistema existente.
- Autenticación/roles.
- Auditoría.

### Iteración 4
- Cloud Run + MySQL.
- Observabilidad.
- métricas de negocio;
- reportes;
- estrategia para escalar de 3 a 150 restaurantes.

## Criterio de éxito
El MVP está terminado cuando puede demostrarse sin intervención manual:

```text
Comensal
   ↓
Se registra
   ↓
Aparece en BD
   ↓
Host lo visualiza
   ↓
Host llama siguiente
   ↓
Estado CALLED
   ↓
Comensal/otros hosts observan el cambio
```

Todo lo demás es secundario frente a este recorrido.
