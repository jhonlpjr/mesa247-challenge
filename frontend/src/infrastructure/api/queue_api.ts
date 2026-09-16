import type { DailyReport, JoinQueueInput, QueueEntry, QueueResponse, Restaurant } from '../../domain/models/queue'
import { request } from './http'

export const queueApi = {
  getRestaurant: (restaurantId: number) => request<Restaurant>(`/restaurants/${restaurantId}`),
  getDailyReport: (restaurantId: number, date: string) => request<DailyReport>(`/restaurants/${restaurantId}/reports/daily?date=${encodeURIComponent(date)}`),
  join: (restaurantId: number, input: JoinQueueInput) => request<QueueEntry>(`/restaurants/${restaurantId}/queue`, { method: 'POST', body: JSON.stringify(input) }),
  getEntry: (entryId: number) => request<QueueEntry>(`/queue/${entryId}`),
  getQueue: (restaurantId: number) => request<QueueResponse>(`/restaurants/${restaurantId}/queue`),
  callNext: (restaurantId: number) => request<QueueEntry>(`/restaurants/${restaurantId}/queue/call-next`, { method: 'POST' }),
  call: (entryId: number) => request<QueueEntry>(`/queue/${entryId}/call`, { method: 'POST' }),
  seat: (entryId: number) => request<QueueEntry>(`/queue/${entryId}/seat`, { method: 'POST' }),
  cancel: (entryId: number) => request<QueueEntry>(`/queue/${entryId}/cancel`, { method: 'POST' }),
  noShow: (entryId: number) => request<QueueEntry>(`/queue/${entryId}/no-show`, { method: 'POST' }),
}
