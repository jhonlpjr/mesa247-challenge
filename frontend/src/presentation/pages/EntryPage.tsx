import { useCallback, useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import type { QueueEntry } from '../../domain/models/queue'
import { queueApi } from '../../infrastructure/api/queue_api'
import { followedEntryStorage } from '../../infrastructure/storage/followed_entry'
import { usePolling } from '../hooks/use_polling'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { StatusBadge } from '../components/StatusBadge'
import './EntryPage.css'

export function EntryPage() {
  const { entryId } = useParams(); const id = Number(entryId)
  const [entry, setEntry] = useState<QueueEntry | null>(null); const [error, setError] = useState(''); const [cancelling, setCancelling] = useState(false)
  const refresh = useCallback(async () => { try { setEntry(await queueApi.getEntry(id)); setError('') } catch { setError('No pudimos actualizar la información. Reintentaremos automáticamente.') } }, [id])
  useEffect(() => { void refresh() }, [refresh]); usePolling(refresh, Boolean(entry && entry.status === 'WAITING'))
  async function leaveQueue() { if (!entry) return; setCancelling(true); setError(''); try { setEntry(await queueApi.cancel(entry.id)); followedEntryStorage.clear() } catch { setError('No se pudo cancelar tu ingreso.') } finally { setCancelling(false) } }
  if (!entry && !error) return <Loading label="Buscando tu lugar…" />
  if (!entry) return <section className="panel narrow"><ErrorMessage message={error} /><Link className="text-link" to="/restaurants/1/join">Volver a registrarme</Link></section>
  const isWaiting = entry.status === 'WAITING'; const isCalled = entry.status === 'CALLED'
  return <section className={`panel narrow entry-card ${isCalled ? 'called' : ''}`}><StatusBadge status={entry.status} />{isWaiting ? <><p className="eyebrow">TU SEGUIMIENTO</p><p className="entry-kicker">Estás en el puesto</p><h1 className="entry-position">{entry.position ?? '—'}</h1><p className="position-label">posición actual</p><p className="muted">Te avisaremos por WhatsApp cuando tu mesa esté lista</p>{error && <ErrorMessage message={error} />}<p className="muted small">Grupo de {entry.party_size} · {entry.phone}</p><button className="secondary leave-button" onClick={() => { void leaveQueue() }} disabled={cancelling}>{cancelling ? 'Cancelando…' : 'Ya no voy'}</button></> : isCalled ? <><p className="eyebrow">TU SEGUIMIENTO</p><h1>¡Es tu turno!</h1><p className="called-message">Tu mesa está lista. Acércate a la entrada dentro de los próximos 10 minutos.</p><p className="muted small">Grupo de {entry.party_size} · {entry.phone}</p></> : <><p className="eyebrow">TU SEGUIMIENTO</p><h1>Has salido de la cola</h1><p className="muted">Si cambias de opinión, puedes registrarte nuevamente.</p><Link className="secondary entry-link" to={`/restaurants/${entry.restaurant_id}/join`}>Volver a la cola</Link></>}</section>
}
