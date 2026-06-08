import { apiRequest } from '../../../lib/api'

export type DogGender = 'male' | 'female' | 'unknown'

export type CreateDogPayload = {
  owner_id: string
  name: string
  birthday?: string | null
  gender?: DogGender | null
}

export type CreateDogResponse = {
  dog_id: string
  owner_id: string
  name: string
  birthday: string | null
  gender: DogGender | null
}

export type UpdateDogPayload = {
  name?: string
  birthday?: string | null
  gender?: DogGender | null
}

export type UpdateDogResponse = {
  dog_id: string
  name: string
  birthday: string | null
  gender: DogGender | null
}

export type OwnerDog = {
  dog_id: string
  name: string
  birthday: string | null
  gender: DogGender | null
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

export async function updateDog(
  dogId: string,
  payload: UpdateDogPayload,
): Promise<UpdateDogResponse> {
  return apiRequest<UpdateDogResponse>(`/dogs/${dogId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export async function fetchOwnerDogs(ownerId: string): Promise<OwnerDogsResponse> {
  return apiRequest<OwnerDogsResponse>(`/owners/${ownerId}/dogs`)
}
