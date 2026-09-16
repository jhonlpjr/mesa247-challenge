# Correo y reporte diario

El backend incluye el puerto `EmailNotificationPort` y el adaptador
`EmailLogNotification`. El adaptador actual solo registra el mensaje en logs: no
envía correos ni requiere credenciales. Puede sustituirse por SMTP, SendGrid,
Amazon SES u otro proveedor sin modificar el dominio ni los casos de uso.

La vista `DailyReportPage` es un extra visual del MVP: permite consultar el
cierre diario por restaurante y fecha local, pero no forma parte del flujo
principal de ingreso y llamada. A futuro, un proceso programado podrá construir
el mismo reporte y enviarlo mediante `DAILY_REPORT_EMAIL`, usando el adaptador
seleccionado por `EMAIL_PROVIDER`.

El envío automático permanece desactivado hasta decidir proveedor, credenciales,
horario, plantilla HTML, reintentos y destinatarios. Esas decisiones son de
negocio y operación, no requisitos del flujo principal.

WhatsApp sigue usando por ahora el enlace gratuito `wa.me`. Meta WhatsApp Cloud
API o Twilio podrán incorporarse después mediante el puerto existente, incluyendo
plantillas con botones “Voy en camino” y “Ya no voy”, webhooks/callbacks,
seguridad y actualización de estado. Nada de eso es necesario para el MVP.
