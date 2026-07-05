<script setup lang="ts">
import { computed, ref } from 'vue'
import { toErrorMessage } from '../../../lib/api'
import { formatDatetimeLocalValue, toJapanTimeISOString } from '../eventDisplay'
import {
  createEvent,
  type EventTypeCode,
  type FoodEventDetail,
  type ToiletCondition,
  type ToiletEventDetail,
  type ToiletType,
  type WalkEventDetail,
} from '../services/eventsApi'

type EventDog = {
  dog_id: string
  name: string
}

const props = defineProps<{
  dog: EventDog
}>()

const emit = defineEmits<{
  close: []
  created: [dogName: string]
  submitting: [isSubmitting: boolean]
}>()

const eventType = ref<EventTypeCode>('walk')
const occurredAt = ref(formatDatetimeLocalValue(new Date()))
const memo = ref('')
const walkDistance = ref('')
const walkHours = ref('')
const walkMinutes = ref('')
const foodMenu = ref('')
const foodAmountGrams = ref('')
const toiletType = ref<ToiletType>('おしっこ')
const toiletCondition = ref<ToiletCondition>('いつも通り')
const errorMessage = ref('')
const isSubmitting = ref(false)

const eventTypeLabel = computed(() => {
  if (eventType.value === 'walk') {
    return '散歩'
  }

  if (eventType.value === 'food') {
    return 'ご飯'
  }

  return 'トイレ'
})

function optionalText(value: string): string | null {
  const normalizedValue = value.trim()
  return normalizedValue || null
}

function optionalDistanceKm(value: string | number): number | null {
  const normalizedValue = String(value).trim()
  if (!normalizedValue) {
    return null
  }

  const distance = Number(normalizedValue)
  if (Number.isNaN(distance)) {
    return null
  }

  return Number(distance.toFixed(1))
}

function optionalWalkDurationMinutes(hoursValue: string | number, minutesValue: string | number): number | null {
  const normalizedHours = String(hoursValue).trim()
  const normalizedMinutes = String(minutesValue).trim()
  let totalMinutes = 0
  let hasValue = false

  if (normalizedHours) {
    const hours = Number(normalizedHours)
    if (!Number.isNaN(hours)) {
      totalMinutes += Math.trunc(hours) * 60
      hasValue = true
    }
  }

  if (normalizedMinutes) {
    const minutes = Number(normalizedMinutes)
    if (!Number.isNaN(minutes)) {
      totalMinutes += Math.trunc(minutes)
      hasValue = true
    }
  }

  return hasValue ? totalMinutes : null
}

function optionalInteger(value: string | number): number | null {
  const normalizedValue = String(value).trim()
  if (!normalizedValue) {
    return null
  }

  const amount = Number(normalizedValue)
  if (Number.isNaN(amount)) {
    return null
  }

  return Math.trunc(amount)
}

function buildDetail(): WalkEventDetail | FoodEventDetail | ToiletEventDetail {
  if (eventType.value === 'walk') {
    return {
      distance_km: optionalDistanceKm(walkDistance.value),
      duration_minutes: optionalWalkDurationMinutes(walkHours.value, walkMinutes.value),
    }
  }

  if (eventType.value === 'food') {
    return {
      menu: optionalText(foodMenu.value),
      amount_grams: optionalInteger(foodAmountGrams.value),
    }
  }

  return {
    type: toiletType.value,
    condition: toiletCondition.value,
  }
}

function closeModal(): void {
  if (isSubmitting.value) {
    return
  }

  emit('close')
}

async function submitEvent(): Promise<void> {
  errorMessage.value = ''

  if (!occurredAt.value) {
    errorMessage.value = '日時は必須です。'
    return
  }

  isSubmitting.value = true
  emit('submitting', true)
  try {
    await createEvent({
      dog_id: props.dog.dog_id,
      event_type_code: eventType.value,
      occurred_at: toJapanTimeISOString(occurredAt.value),
      memo: optionalText(memo.value),
      detail: buildDetail(),
    })
    emit('created', props.dog.name)
  } catch (error) {
    errorMessage.value = toErrorMessage(error, 'イベント登録に失敗しました。')
  } finally {
    isSubmitting.value = false
    emit('submitting', false)
  }
}
</script>

<template>
  <div class="modal-backdrop" @click.self="closeModal">
    <section class="modal-card" role="dialog" aria-modal="true" aria-labelledby="event-create-title">
      <div class="modal-header">
        <div>
          <h3 id="event-create-title">イベント作成</h3>
          <p class="meta-copy">{{ dog.name }}のイベントを登録します。</p>
        </div>
      </div>

      <form class="form" @submit.prevent="submitEvent">
        <div class="field">
          <label for="event-type">イベントの種類</label>
          <select id="event-type" v-model="eventType">
            <option value="walk">散歩</option>
            <option value="food">ご飯</option>
            <option value="toilet">トイレ</option>
          </select>
        </div>

        <div class="event-detail-section">
          <p class="event-detail-title">{{ eventTypeLabel }}の詳細</p>

          <template v-if="eventType === 'walk'">
            <div class="field">
              <label for="walk-distance">距離 (km)</label>
              <input
                id="walk-distance"
                v-model="walkDistance"
                type="number"
                inputmode="decimal"
                min="0"
                max="10"
                step="0.1"
              />
            </div>
            <div class="field">
              <label>時間</label>
              <div class="split-input-row">
                <label class="inline-number-field" for="walk-hours">
                  <input
                    id="walk-hours"
                    v-model="walkHours"
                    type="number"
                    inputmode="numeric"
                    min="0"
                    max="23"
                    step="1"
                    aria-label="時間の時"
                  />
                  <span>h</span>
                </label>
                <label class="inline-number-field" for="walk-minutes">
                  <input
                    id="walk-minutes"
                    v-model="walkMinutes"
                    type="number"
                    inputmode="numeric"
                    min="0"
                    max="59"
                    step="1"
                    aria-label="時間の分"
                  />
                  <span>min</span>
                </label>
              </div>
            </div>
          </template>

          <template v-else-if="eventType === 'food'">
            <div class="field">
              <label for="food-menu">メニュー</label>
              <input id="food-menu" v-model="foodMenu" />
            </div>
            <div class="field">
              <label for="food-amount-grams">量 (g)</label>
              <input
                id="food-amount-grams"
                v-model="foodAmountGrams"
                type="number"
                inputmode="numeric"
                min="0"
                max="1000"
                step="1"
              />
            </div>
          </template>

          <template v-else>
            <div class="field">
              <label for="toilet-type">種類</label>
              <select id="toilet-type" v-model="toiletType">
                <option value="おしっこ">おしっこ</option>
                <option value="うんち">うんち</option>
              </select>
            </div>
            <div class="field">
              <label for="toilet-condition">状態</label>
              <select id="toilet-condition" v-model="toiletCondition">
                <option value="良好">良好</option>
                <option value="いつも通り">いつも通り</option>
                <option value="気になる">気になる</option>
              </select>
            </div>
          </template>
        </div>

        <div class="field">
          <label for="event-occurred-at">日時</label>
          <input id="event-occurred-at" v-model="occurredAt" type="datetime-local" />
        </div>

        <div class="field">
          <label for="event-memo">メモ</label>
          <textarea id="event-memo" v-model="memo" maxlength="1000" rows="3" />
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <div class="actions">
          <button class="primary-button" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? '登録中...' : 'イベントを登録' }}
          </button>
          <button class="ghost-button" type="button" :disabled="isSubmitting" @click="closeModal">
            キャンセル
          </button>
        </div>
      </form>
    </section>
  </div>
</template>
