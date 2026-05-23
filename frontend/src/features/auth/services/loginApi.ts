import { apiRequest } from '../../../lib/api'
import type { CurrentOwner } from '../session'

export type LoginPayload = {
  login_id: string
}

export async function login(payload: LoginPayload): Promise<CurrentOwner> {
  return apiRequest<CurrentOwner>('/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
