import type { QueueStatus } from '../../domain/models/queue'
const labels: Record<QueueStatus, string> = { WAITING: 'En espera', CALLED: 'Llamado', SEATED: 'Sentado', CANCELLED: 'Cancelado', NO_SHOW: 'No se presentó' }

export function StatusBadge({ status }: { status: QueueStatus }) {
  return <span className={`status status-${status.toLowerCase()}`}>{labels[status]}</span>
}
