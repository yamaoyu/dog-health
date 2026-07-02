import type {
  EventResponse,
  EventTypeCode,
  FoodEventDetail,
  ToiletEventDetail,
  WalkEventDetail,
} from './services/eventsApi'

export type EventGroup = {
  date: string
  events: EventResponse[]
}

export function formatLocalDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

export function formatDisplayDate(value: string): string {
  return new Intl.DateTimeFormat('ja-JP', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  }).format(new Date(value))
}

export function formatDisplayTime(value: string): string {
  return new Intl.DateTimeFormat('ja-JP', {
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value))
}

export function groupEventsByLocalDate(events: EventResponse[]): EventGroup[] {
  const groups = new Map<string, EventResponse[]>()

  for (const event of events) {
    const date = formatLocalDate(new Date(event.occurred_at))
    groups.set(date, [...(groups.get(date) ?? []), event])
  }

  return Array.from(groups, ([date, groupedEvents]) => ({
    date,
    events: groupedEvents,
  }))
}

export function getEventDetailLabels(event: EventResponse): string[] {
  if (event.event_type.code === 'walk') {
    const detail = event.detail as WalkEventDetail
    return [
      `距離: ${detail.distance_km ?? '-'}km`,
      `時間: ${detail.duration_minutes ?? '-'}分`,
    ]
  }

  if (event.event_type.code === 'food') {
    const detail = event.detail as FoodEventDetail
    return [
      `メニュー: ${detail.menu ?? '-'}`,
      `量: ${detail.amount_grams ?? '-'}g`,
    ]
  }

  const detail = event.detail as ToiletEventDetail
  return [
    `種類: ${detail.type ?? '-'}`,
    `状態: ${detail.condition ?? '-'}`,
  ]
}

export function getEventTypeLabel(code: EventTypeCode): string {
  if (code === 'walk') {
    return '散歩'
  }

  if (code === 'food') {
    return 'ご飯'
  }

  return 'トイレ'
}
