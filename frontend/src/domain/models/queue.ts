export type QueueStatus = 'WAITING' | 'CALLED' | 'SEATED' | 'CANCELLED' | 'NO_SHOW'

export interface QueueEntry {
  id: number
  restaurant_id: number
  name: string
  phone: string
  party_size: number
  status: QueueStatus
  created_at: string
  called_at: string | null
  position: number | null
}

export interface QueueResponse { entries: QueueEntry[] }
export interface Restaurant { id: number; name: string; country_code: string; phone_country_code: string; timezone: string }
export interface DailyReport { restaurant_id: number; restaurant_name: string; date: string; joined_count: number; seated_count: number; cancelled_count: number; no_show_count: number; average_wait_minutes: number | null }
export interface JoinQueueInput { name: string; phone: string; party_size: number }
