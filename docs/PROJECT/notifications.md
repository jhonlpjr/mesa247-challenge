# Notificaciones de llamada

La notificación actual usa el adaptador `WhatsAppLinkNotification`. Este adaptador genera un enlace `https://wa.me/...` con un mensaje preconfigurado y lo abre en una nueva pestaña. No consume una API externa ni envía mensajes automáticamente: el anfitrión confirma el envío desde WhatsApp.

La UI depende únicamente del puerto `NotificationPort` (`notifyCalled`). Por eso una futura integración con Meta WhatsApp Cloud API o Twilio puede reemplazar el adaptador sin modificar las páginas ni los casos de uso. La selección del proveedor deberá definirse junto con credenciales, opt-in, plantillas aprobadas, manejo de errores, costos y políticas de reintento.

El endpoint de llamada por cliente es `POST /queue/{entry_id}/call`; el botón global usa `POST /restaurants/{restaurant_id}/queue/call-next`. Ambos actualizan el estado a `CALLED` antes de preparar la notificación.
