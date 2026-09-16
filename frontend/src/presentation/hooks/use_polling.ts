import { useEffect } from 'react'
import { POLLING_INTERVAL_MS } from '../../app/config/api'

export function usePolling(callback: () => void | Promise<void>, enabled = true) {
  useEffect(() => {
    if (!enabled) return
    const timer = window.setInterval(() => { void callback() }, POLLING_INTERVAL_MS)
    return () => window.clearInterval(timer)
  }, [callback, enabled])
}
