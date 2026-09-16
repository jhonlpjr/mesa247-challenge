import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { MemoryRouter } from 'react-router-dom'
import { vi, describe, it, expect } from 'vitest'
import { JoinPage } from './JoinPage'
import { queueApi } from '../../infrastructure/api/queue_api'

vi.mock('../../infrastructure/api/queue_api', () => ({ queueApi: { join: vi.fn(), getRestaurant: vi.fn() } }))

describe('JoinPage', () => {
  it('validates and submits the queue form', async () => {
    vi.mocked(queueApi.join).mockResolvedValue({ id: 7, restaurant_id: 1, name: 'Ana', phone: '9999999', party_size: 2, status: 'WAITING', created_at: '', called_at: null, position: 1 })
    vi.mocked(queueApi.getRestaurant).mockResolvedValue({ id: 1, name: 'La Terraza Azul', country_code: 'PE', phone_country_code: '+51', timezone: 'America/Lima' })
    const user = userEvent.setup(); render(<MemoryRouter initialEntries={['/restaurants/1/join']}><JoinPage /></MemoryRouter>)
    await user.click(screen.getByRole('button', { name: /entrar/i })); expect(screen.getByRole('alert')).toHaveTextContent('Completa')
    await user.type(screen.getByLabelText('Nombre'), 'Ana'); await user.type(screen.getByLabelText(/número de teléfono/i), '999999999'); await user.click(screen.getByRole('button', { name: /entrar/i }))
    expect(queueApi.join).toHaveBeenCalledWith(1, { name: 'Ana', phone: '+51999999999', party_size: 2 })
  })
})
