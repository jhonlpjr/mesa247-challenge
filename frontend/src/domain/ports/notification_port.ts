import type { QueueEntry, Restaurant } from '../models/queue'

/** Port for customer notifications. Provider details stay outside the UI. */
export interface NotificationPort {
  notifyCalled(entry: QueueEntry, restaurant: Restaurant): Promise<void>
}
