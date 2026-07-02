<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { toErrorMessage } from '../../../lib/api'
import {
  formatDisplayDate,
  formatDisplayTime,
  formatLocalDate,
  getEventDetailLabels,
  getEventTypeLabel,
  groupEventsByLocalDate,
} from '../eventDisplay'
import {
  fetchEvents,
  type EventPeriod,
  type EventResponse,
  type EventTypeCode,
} from '../services/eventsApi'

type EventTypeFilter = EventTypeCode | 'all'

const route = useRoute()
const dogId = computed(() => String(route.params.dogId ?? ''))
const dogName = computed(() => {
  const value = route.query.dog_name
  return typeof value === 'string' ? value : ''
})
const eventHeading = computed(() => (dogName.value ? `${dogName.value}のイベント` : '犬のイベント'))
const period = ref<EventPeriod>(normalizePeriod(route.query.period))
const currentDate = ref(normalizeDate(route.query.date))
const eventTypeFilter = ref<EventTypeFilter>('all')
const events = ref<EventResponse[]>([])
const isLoading = ref(false)
const errorMessage = ref('')

const groupedEvents = computed(() => {
  if (period.value === 'week') {
    return weekDates.value.map((date) => ({
      date,
      events: events.value.filter((event) => formatLocalDate(new Date(event.occurred_at)) === date),
    }))
  }

  return groupEventsByLocalDate(events.value)
})

const pageTitle = computed(() => {
  if (period.value === 'week') {
    const firstDay = weekDates.value[0]
    const lastDay = weekDates.value[6]
    return `${formatDisplayDate(firstDay)} - ${formatDisplayDate(lastDay)}`
  }

  const date = new Date(`${currentDate.value}T00:00:00`)
  return `${date.getFullYear()}年${date.getMonth() + 1}月`
})

const weekDates = computed(() => {
  const start = getWeekStart(new Date(`${currentDate.value}T00:00:00`))

  return Array.from({ length: 7 }, (_, index) => {
    const date = new Date(start)
    date.setDate(start.getDate() + index)
    return formatLocalDate(date)
  })
})

function normalizePeriod(value: unknown): EventPeriod {
  return value === 'month' ? 'month' : 'week'
}

function normalizeDate(value: unknown): string {
  if (typeof value === 'string' && value !== 'today') {
    return value
  }

  return formatLocalDate(new Date())
}

function getWeekStart(date: Date): Date {
  const start = new Date(date)
  const day = start.getDay()
  const diff = day === 0 ? -6 : 1 - day
  start.setDate(start.getDate() + diff)
  return start
}

function setPeriod(nextPeriod: EventPeriod): void {
  period.value = nextPeriod
}

function movePeriod(amount: number): void {
  const nextDate = new Date(`${currentDate.value}T00:00:00`)

  if (period.value === 'month') {
    nextDate.setMonth(nextDate.getMonth() + amount)
  } else {
    nextDate.setDate(nextDate.getDate() + amount * 7)
  }

  currentDate.value = formatLocalDate(nextDate)
}

async function loadEvents(): Promise<void> {
  if (!dogId.value) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetchEvents({
      dog_id: dogId.value,
      period: period.value,
      date: currentDate.value,
      event_type_code: eventTypeFilter.value === 'all' ? undefined : eventTypeFilter.value,
    })
    events.value = response.events
  } catch (error) {
    events.value = []
    errorMessage.value = toErrorMessage(error, 'イベント一覧の取得に失敗しました。')
  } finally {
    isLoading.value = false
  }
}

watch([period, currentDate, eventTypeFilter], () => {
  void loadEvents()
}, { immediate: true })
</script>

<template>
  <section class="events-page">
    <article class="panel strong">
      <p class="eyebrow">イベント一覧</p>
      <h2>{{ eventHeading }}</h2>

      <div class="event-toolbar">
        <div class="segmented-control" aria-label="表示期間">
          <button
            type="button"
            :class="{ active: period === 'month' }"
            @click="setPeriod('month')"
          >
            月
          </button>
          <button
            type="button"
            :class="{ active: period === 'week' }"
            @click="setPeriod('week')"
          >
            週
          </button>
        </div>

        <div class="event-period-controls">
          <button class="ghost-button" type="button" @click="movePeriod(-1)">
            {{ period === 'month' ? '前月' : '前週' }}
          </button>
          <p class="event-period-title">{{ pageTitle }}</p>
          <button class="ghost-button" type="button" @click="movePeriod(1)">
            {{ period === 'month' ? '翌月' : '翌週' }}
          </button>
        </div>

        <label class="event-filter">
          <span>カテゴリ</span>
          <select v-model="eventTypeFilter">
            <option value="all">すべて</option>
            <option value="walk">散歩</option>
            <option value="food">ご飯</option>
            <option value="toilet">トイレ</option>
          </select>
        </label>
      </div>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <div v-else-if="isLoading" class="callout">
        <p class="meta-copy">イベントを読み込んでいます...</p>
      </div>

      <div v-else-if="events.length === 0" class="callout">
        <p class="empty-copy">この期間のイベントはありません。</p>
      </div>

      <div v-else class="event-groups">
        <section v-for="group in groupedEvents" :key="group.date" class="event-group">
          <h3>{{ formatDisplayDate(group.date) }}</h3>
          <p v-if="group.events.length === 0" class="meta-copy">イベントはありません。</p>
          <ul v-else class="event-list">
            <li v-for="event in group.events" :key="event.event_id" class="event-item">
              <div class="event-item-header">
                <span class="event-type">{{ event.event_type.display_name || getEventTypeLabel(event.event_type.code) }}</span>
                <span class="event-time">{{ formatDisplayTime(event.occurred_at) }}</span>
              </div>
              <p v-if="event.memo" class="meta-copy">メモ: {{ event.memo }}</p>
              <p class="meta-copy">{{ getEventDetailLabels(event).join(' / ') }}</p>
            </li>
          </ul>
        </section>
      </div>
    </article>
  </section>
</template>
