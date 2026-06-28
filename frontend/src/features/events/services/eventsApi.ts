import { apiRequest } from '../../../lib/api'

export type EventTypeCode = 'walk' | 'food' | 'toilet'
export type ToiletType = 'おしっこ' | 'うんち'
export type ToiletCondition = '良好' | 'いつも通り' | '気になる'

export type WalkEventDetail = {
  distance_km: number | null
  duration_minutes: number | null
}

export type FoodEventDetail = {
  menu: string | null
  amount_grams: number | null
}

export type ToiletEventDetail = {
  type: ToiletType | null
  condition: ToiletCondition | null
}

export type EventDetail = WalkEventDetail | FoodEventDetail | ToiletEventDetail

export type CreateEventPayload = {
  dog_id: string
  event_type_code: EventTypeCode
  occurred_at: string
  memo: string | null
  detail: EventDetail
}

export type EventTypeResponse = {
  event_type_id: string
  code: EventTypeCode
  display_name: string
}

export type CreateEventResponse = {
  event_id: string
  dog_id: string
  event_type: EventTypeResponse
  occurred_at: string
  memo: string | null
  detail: EventDetail
}

export async function createEvent(payload: CreateEventPayload): Promise<CreateEventResponse> {
  return apiRequest<CreateEventResponse>('/events', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
