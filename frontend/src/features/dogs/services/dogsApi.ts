import { apiRequest } from '../../../lib/api'

export type CreateDogPayload = {
  owner_id: string
  name: string
  birthday: string
}

export type CreateDogResponse = {
  dog_id: string
  owner_id: string
  name: string
  birthday: string
}

export type OwnerDog = {
  dog_id: string
  name: string
  birthday: string
}

export type OwnerDogsResponse = {
  owner_id: string
  owner_name: string
  dogs: OwnerDog[]
}

export async function createDog(payload: CreateDogPayload): Promise<CreateDogResponse> {
  return apiRequest<CreateDogResponse>('/dogs', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function fetchOwnerDogs(ownerId: string): Promise<OwnerDogsResponse> {
  return apiRequest<OwnerDogsResponse>(`/owners/${ownerId}/dogs`)
}
