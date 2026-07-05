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

const japanTimeZone = 'Asia/Tokyo'
const weekdayLabels = ['日', '月', '火', '水', '木', '金', '土']

function parseDateKey(value: string): { year: number; month: number; day: number } | null {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(value)
  if (match === null) {
    return null
  }

  const [, year, month, day] = match
  return {
    year: Number(year),
    month: Number(month),
    day: Number(day),
  }
}

function getDatePartValue(parts: Intl.DateTimeFormatPart[], type: Intl.DateTimeFormatPartTypes): string {
  return parts.find((part) => part.type === type)?.value ?? ''
}

function getAppDateParts(date: Date): Intl.DateTimeFormatPart[] {
  return new Intl.DateTimeFormat('ja-JP', {
    timeZone: japanTimeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hourCycle: 'h23',
  }).formatToParts(date)
}

export function formatLocalDate(date: Date): string {
  const parts = getAppDateParts(date)
  const year = getDatePartValue(parts, 'year')
  const month = getDatePartValue(parts, 'month')
  const day = getDatePartValue(parts, 'day')

  return `${year}-${month}-${day}`
}

export function formatDatetimeLocalValue(date: Date): string {
  const parts = getAppDateParts(date)
  const year = getDatePartValue(parts, 'year')
  const month = getDatePartValue(parts, 'month')
  const day = getDatePartValue(parts, 'day')
  const hour = getDatePartValue(parts, 'hour')
  const minute = getDatePartValue(parts, 'minute')

  return `${year}-${month}-${day}T${hour}:${minute}`
}

export function toJapanTimeISOString(value: string): string {
  const match = /^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2})$/.exec(value)
  if (match === null) {
    throw new Error('Invalid datetime-local value')
  }

  const [, yearValue, monthValue, dayValue, hourValue, minuteValue] = match
  return new Date(Date.UTC(
    Number(yearValue),
    Number(monthValue) - 1,
    Number(dayValue),
    Number(hourValue) - 9,
    Number(minuteValue),
  )).toISOString()
}

export function formatDisplayDate(value: string): string {
  const dateKey = parseDateKey(value)
  if (dateKey !== null) {
    const weekday = new Date(Date.UTC(dateKey.year, dateKey.month - 1, dateKey.day)).getUTCDay()
    return `${dateKey.year}年${dateKey.month}月${dateKey.day}日(${weekdayLabels[weekday]})`
  }

  return new Intl.DateTimeFormat('ja-JP', {
    timeZone: japanTimeZone,
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'short',
  }).format(new Date(value))
}

export function formatDisplayTime(value: string): string {
  return new Intl.DateTimeFormat('ja-JP', {
    timeZone: japanTimeZone,
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
