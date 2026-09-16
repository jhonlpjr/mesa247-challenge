import { API_BASE_URL } from '../../app/config/api'

export class ApiError extends Error {
  constructor(public readonly status: number, message: string) { super(message); this.name = 'ApiError' }
}

export async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response
  try { response = await fetch(`${API_BASE_URL}${path}`, { headers: { 'Content-Type': 'application/json', ...options?.headers }, ...options }) }
  catch { throw new ApiError(0, 'No se pudo conectar con el servidor.') }
  if (!response.ok) {
    let message = 'Ocurrió un error. Intenta nuevamente.'
    try { const body = await response.json() as { detail?: string | Array<{ msg?: string }> }; message = typeof body.detail === 'string' ? body.detail : body.detail?.[0]?.msg || message } catch { /* empty response */ }
    throw new ApiError(response.status, message)
  }
  return response.json() as Promise<T>
}
