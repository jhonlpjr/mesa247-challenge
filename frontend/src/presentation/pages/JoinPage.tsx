import { FormEvent, useEffect, useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { queueApi } from '../../infrastructure/api/queue_api'
import { followedEntryStorage } from '../../infrastructure/storage/followed_entry'
import { ApiError } from '../../infrastructure/api/http'
import { ErrorMessage } from '../components/ErrorMessage'
import './JoinPage.css'

export function JoinPage() {
  const { restaurantId = '1' } = useParams(); const navigate = useNavigate(); const id = Number(restaurantId)
  const [restaurantName, setRestaurantName] = useState('Mesa247'); const [phoneCode, setPhoneCode] = useState('+51')
  const [name, setName] = useState(''); const [phone, setPhone] = useState(''); const [partySize, setPartySize] = useState('2'); const [error, setError] = useState(''); const [loading, setLoading] = useState(false)
  const phoneLength = 9
  useEffect(() => { void queueApi.getRestaurant(id).then(restaurant => { setRestaurantName(restaurant.name); setPhoneCode(restaurant.phone_country_code) }).catch(() => setError('No pudimos cargar la información del restaurante.')) }, [id])
  function updatePhone(value: string) { setPhone(value.replace(/\D/g, '').slice(0, phoneLength)) }
  function updateName(value: string) { setName(value.replace(/[^\p{L} '\u2019]/gu, '')) }
  function changePartySize(delta: number) { setPartySize(current => String(Math.min(20, Math.max(1, Number(current || 1) + delta)))) }
  async function submit(event: FormEvent) {
    event.preventDefault(); setError(''); const size = Number(partySize)
    if (!name.trim()) { setError('Completa el nombre de una persona de contacto.'); return }
    if (phone.length !== phoneLength) { setError(`Ingresa un número de teléfono válido de ${phoneLength} dígitos. Ejemplo: 987 654 321.`); return }
    if (!Number.isInteger(size) || size < 1 || size > 20) { setError('Indica una cantidad válida de entre 1 y 20 personas.'); return }
    setLoading(true)
    try { const entry = await queueApi.join(id, { name: name.trim(), phone: `${phoneCode}${phone}`, party_size: size }); followedEntryStorage.set(entry.id); navigate(`/queue/${entry.id}`) }
    catch (caught) { setError(caught instanceof ApiError ? caught.message : 'No se pudo registrar tu ingreso. Revisa los datos e inténtalo nuevamente.') }
    finally { setLoading(false) }
  }
  return <section className="panel narrow"><p className="eyebrow">LISTA DE ESPERA</p><h1>{restaurantName}</h1><p className="intro">Lista de espera · hoy</p><form onSubmit={submit} noValidate><label>Nombre<input value={name} onChange={e => updateName(e.target.value)} placeholder="Tu nombre" autoComplete="name" /></label><label>Teléfono<div className="phone-input"><span>{phoneCode}</span><input aria-label="Número de teléfono" value={phone} onChange={e => updatePhone(e.target.value)} placeholder="987 654 321" inputMode="numeric" type="tel" maxLength={phoneLength} aria-describedby="phone-help" /></div><span id="phone-help" className="field-help">Ingresa 9 dígitos. Ejemplo: 987 654 321.</span></label><label>¿Cuántos son?<div className="party-stepper"><button type="button" aria-label="Disminuir cantidad" onClick={() => changePartySize(-1)} disabled={loading || Number(partySize) <= 1}>−</button><input aria-label="Cantidad de personas" type="number" min="1" max="20" value={partySize} onChange={e => setPartySize(e.target.value)} /><button type="button" aria-label="Aumentar cantidad" onClick={() => changePartySize(1)} disabled={loading || Number(partySize) >= 20}>+</button></div></label>{error && <ErrorMessage message={error} />}<button disabled={loading}>{loading ? 'Registrando…' : 'Entrar a la cola'}</button></form></section>
}
