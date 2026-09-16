import { act, render, screen } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { vi, describe, it, expect } from 'vitest'
import { EntryPage } from './EntryPage'
import { queueApi } from '../../infrastructure/api/queue_api'

vi.mock('../../infrastructure/api/queue_api', () => ({ queueApi: { getEntry: vi.fn() } }))
const waiting = { id: 7, restaurant_id: 1, name: 'Ana', phone: '9999999', party_size: 2, status: 'WAITING' as const, created_at: '', called_at: null, position: 2 }
describe('EntryPage', () => {
  it('shows position and reflects called status', async () => {
    vi.useFakeTimers(); vi.mocked(queueApi.getEntry).mockResolvedValueOnce(waiting).mockResolvedValueOnce({ ...waiting, status: 'CALLED', position: null, called_at: '2026-01-01T10:00:00Z' })
    render(<MemoryRouter initialEntries={['/queue/7']}><Routes><Route path="/queue/:entryId" element={<EntryPage />} /></Routes></MemoryRouter>)
    await act(async () => { await Promise.resolve() }); expect(screen.getByText('2')).toBeInTheDocument(); expect(screen.getByText('En espera')).toBeInTheDocument()
    await act(async () => { await vi.advanceTimersByTimeAsync(10000) }); expect(screen.getByText('¡Es tu turno!')).toBeInTheDocument(); vi.useRealTimers()
  })
})
