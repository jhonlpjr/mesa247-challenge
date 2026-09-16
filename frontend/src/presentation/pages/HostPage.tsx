import { useCallback, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import type { QueueEntry, Restaurant } from '../../domain/models/queue'
import { queueApi } from '../../infrastructure/api/queue_api'
import { ApiError } from '../../infrastructure/api/http'
import { usePolling } from '../hooks/use_polling'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'
import { StatusBadge } from '../components/StatusBadge'
import './HostPage.css'
import { notificationPort } from '../../infrastructure/notifications/whatsapp_link_notification'

const LOCAL_TIMEZONE = 'America/Lima'
function formatTime(value: string | null, timeZone = LOCAL_TIMEZONE) { return value ? new Intl.DateTimeFormat('es-PE', { hour: '2-digit', minute: '2-digit', timeZone }).format(new Date(value)) : '—' }
function waitingMinutes(value: string) { return Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 60000)) }

export function HostPage() {
  const { restaurantId = '1' } = useParams(); const id = Number(restaurantId)
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null); const [entries, setEntries] = useState<QueueEntry[]>([])
  const [loading, setLoading] = useState(true); const [calling, setCalling] = useState(false); const [busyId, setBusyId] = useState<number | null>(null); const [draggedIndex, setDraggedIndex] = useState<number | null>(null); const [error, setError] = useState('')
  const refresh = useCallback(async () => { try { const [restaurantResult, queueResult] = await Promise.all([queueApi.getRestaurant(id), queueApi.getQueue(id)]); setRestaurant(restaurantResult); setEntries(queueResult.entries); setError('') } catch { setError('No pudimos cargar la cola. Reintentaremos automáticamente.') } finally { setLoading(false) } }, [id])
  useEffect(() => { void refresh() }, [refresh]); usePolling(refresh)
  async function callNext() { setCalling(true); setError(''); try { const calledEntry = await queueApi.callNext(id); if (restaurant) await notificationPort.notifyCalled(calledEntry, restaurant); await refresh() } catch (caught) { setError(caught instanceof ApiError && caught.status === 404 ? 'No hay comensales esperando.' : 'No se pudo llamar al siguiente comensal.') } finally { setCalling(false) } }
  async function transition(entry: QueueEntry, action: 'seat' | 'cancel' | 'noShow') { setBusyId(entry.id); setError(''); try { await queueApi[action](entry.id); await refresh() } catch { setError('No se pudo actualizar este comensal.') } finally { setBusyId(null) } }
  async function callEntry(entry: QueueEntry) { setBusyId(entry.id); setError(''); try { const calledEntry = await queueApi.call(entry.id); if (restaurant) await notificationPort.notifyCalled(calledEntry, restaurant); await refresh() } catch { setError('No se pudo llamar a este comensal.') } finally { setBusyId(null) } }
  function dropEntry(targetIndex: number) { if (draggedIndex === null || draggedIndex === targetIndex) return; setEntries(current => { const next = [...current]; const [moved] = next.splice(draggedIndex, 1); next.splice(targetIndex, 0, moved); return next }); setDraggedIndex(null) }
  const averageWait = entries.length ? Math.round(entries.reduce((total, entry) => { const end = entry.status === 'CALLED' && entry.called_at ? new Date(entry.called_at).getTime() : Date.now(); return total + Math.max(0, (end - new Date(entry.created_at).getTime()) / 60000) }, 0) / entries.length) : 0
  return <section className="host-page"><div className="host-heading"><div><p className="eyebrow">PANEL DE {restaurant?.name || 'RESTAURANTE'}</p><h1>Cola activa</h1><p className="intro">{entries.length} en cola · espera media {averageWait} min</p></div><button onClick={callNext} disabled={calling || entries.every(entry => entry.status !== 'WAITING')}>{calling ? 'Llamando…' : 'Llamar al siguiente'}</button></div>{error && <ErrorMessage message={error} />}{loading ? <Loading label="Cargando cola…" /> : entries.length === 0 ? <div className="empty"><strong>La cola está vacía</strong><span>Los nuevos comensales aparecerán aquí.</span></div> : <div className="queue-table"><div className="table-head"><span></span><span>#</span><span>Comensal</span><span>Grupo</span><span>Espera</span><span>Estado</span><span>Acciones</span></div>{entries.map((entry, index) => <div className={`table-row ${entry.status === 'CALLED' ? 'is-called' : ''} ${draggedIndex === index ? 'is-dragging' : ''}`} onDragOver={event => event.preventDefault()} onDrop={() => dropEntry(index)} key={entry.id}><div className="drag-handle" draggable onDragStart={() => setDraggedIndex(index)} onDragEnd={() => setDraggedIndex(null)} role="button" aria-label={`Arrastrar a ${index + 1}`} title="Arrastra para reordenar">⠿</div><strong>{index + 1}</strong><span>{entry.name}<small>{entry.phone}</small></span><span>{entry.party_size} {entry.party_size === 1 ? 'persona' : 'personas'}</span><span className="wait-time">{entry.status === 'WAITING' ? `${waitingMinutes(entry.created_at)} min` : `Llamado ${formatTime(entry.called_at, restaurant?.timezone)}`}</span><StatusBadge status={entry.status} /><div className="row-actions">{entry.status === 'WAITING' && <><button onClick={() => { void callEntry(entry) }} disabled={busyId === entry.id}>Llamar</button><button onClick={() => { void transition(entry, 'cancel') }} disabled={busyId === entry.id}>Cancelar</button></>}{entry.status === 'CALLED' && <><button onClick={() => { void transition(entry, 'seat') }} disabled={busyId === entry.id}>Sentar</button><button onClick={() => { void transition(entry, 'noShow') }} disabled={busyId === entry.id}>No llegó</button></>}</div></div>)}</div>}</section>
}
