import { apiRequest } from '../../../lib/api'

export type OwnerDog = {
  dog_id: string
  name: string
  birthday: string
  role: string | null
}

export type OwnerDogsResponse = {
  owner_id: string
  owner_name: string
  dogs: OwnerDog[]
}

export async function fetchOwnerDogs(ownerId: string): Promise<OwnerDogsResponse> {
  return apiRequest<OwnerDogsResponse>(`/owners/${ownerId}/dogs`)
}
