import { apiRequest } from '../../../lib/api'

export type Owner = {
  owner_id: string
  name: string
  login_id: string
}

export type CreateOwnerPayload = {
  name: string
  login_id: string
}

export async function createOwner(payload: CreateOwnerPayload): Promise<Owner> {
  return apiRequest<Owner>('/owners', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
