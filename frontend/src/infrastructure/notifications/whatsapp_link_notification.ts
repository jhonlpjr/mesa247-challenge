import type { NotificationPort } from '../../domain/ports/notification_port'
import type { QueueEntry, Restaurant } from '../../domain/models/queue'

function whatsappNumber(phone: string) { return phone.replace(/\D/g, '') }

export class WhatsAppLinkNotification implements NotificationPort {
  async notifyCalled(entry: QueueEntry, restaurant: Restaurant) {
    const message = `¡${entry.name}, tu mesa en ${restaurant.name} ya está lista! Tienes 10 minutos para acercarte a la entrada.`
    const url = `https://wa.me/${whatsappNumber(entry.phone)}?text=${encodeURIComponent(message)}`
    window.open(url, '_blank', 'noopener,noreferrer')
  }
}

// Future adapters can implement the same port without changing the HostPage:
// Meta Cloud API and Twilio should be selected here through configuration once
// credentials, templates, opt-in and provider costs are decided.
export const notificationPort: NotificationPort = new WhatsAppLinkNotification()
