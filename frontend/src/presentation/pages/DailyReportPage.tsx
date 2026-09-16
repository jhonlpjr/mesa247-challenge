import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import type { DailyReport, Restaurant } from '../../domain/models/queue'
import { queueApi } from '../../infrastructure/api/queue_api'
import { ErrorMessage } from '../components/ErrorMessage'
import { Loading } from '../components/Loading'

const DEFAULT_TIMEZONE = 'America/Lima'

function localDate(timeZone: string) {
  const parts = new Intl.DateTimeFormat('en', { timeZone, year: 'numeric', month: '2-digit', day: '2-digit' }).formatToParts(new Date())
  const values = Object.fromEntries(parts.map(part => [part.type, part.value]))
  return `${values.year}-${values.month}-${values.day}`
}

function formatReportDate(value: string, timeZone: string) {
  // Noon UTC keeps a date-only value on the same calendar day in every supported restaurant zone.
  return new Intl.DateTimeFormat('es-PE', { weekday: 'long', day: 'numeric', month: 'long', timeZone }).format(new Date(`${value}T12:00:00Z`))
}

export function DailyReportPage() {
  const { restaurantId = '1' } = useParams(); const id = Number(restaurantId)
  const [restaurant, setRestaurant] = useState<Restaurant | null>(null); const [date, setDate] = useState(''); const [report, setReport] = useState<DailyReport | null>(null); const [error, setError] = useState(''); const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true); setError('')
    void queueApi.getRestaurant(id).then(value => { setRestaurant(value); setDate(current => current || localDate(value.timezone || DEFAULT_TIMEZONE)) }).catch(() => { setError('No pudimos cargar la información del restaurante.'); setLoading(false) })
  }, [id])

  useEffect(() => {
    if (!date) return
    setLoading(true); setError('')
    void queueApi.getDailyReport(id, date).then(setReport).catch(() => setError('No pudimos cargar el reporte.')).finally(() => setLoading(false))
  }, [id, date])

  const timeZone = restaurant?.timezone || DEFAULT_TIMEZONE
  return <section className="report-page"><div className="report-heading"><div><p className="eyebrow">REPORTE DEL DÍA</p><h1>{report?.restaurant_name || restaurant?.name || 'Reporte diario'}</h1><p className="intro">Cierre operativo del restaurante</p></div><label className="date-picker">Fecha<input type="date" value={date} onChange={event => setDate(event.target.value)} /></label></div>{loading || !date ? <Loading label="Cargando reporte…" /> : error ? <ErrorMessage message={error} /> : report && <div className="report-card"><h2>{formatReportDate(report.date, timeZone)}</h2><p className="report-subtitle">{report.restaurant_name} · cierre del día</p><div className="report-stat"><span>Se unieron</span><strong>{report.joined_count}</strong></div><div className="report-stat"><span>Se sentaron</span><strong>{report.seated_count}</strong></div><div className="report-stat"><span>Se fueron sin sentarse</span><strong className="alert-number">{report.cancelled_count}</strong></div><div className="report-stat"><span>No vinieron al ser llamados</span><strong>{report.no_show_count}</strong></div><div className="report-stat"><span>Espera media</span><strong>{report.average_wait_minutes === null ? '—' : `${report.average_wait_minutes} min`}</strong></div></div>}</section>
}
