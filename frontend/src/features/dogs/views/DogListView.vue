<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { toErrorMessage } from '../../../lib/api'
import { getCurrentOwner } from '../../auth/session'
import { createDog, fetchOwnerDogs, type OwnerDogsResponse } from '../services/dogsApi'

const owner = getCurrentOwner()
const dogsResponse = ref<OwnerDogsResponse | null>(null)
const errorMessage = ref('')
const isLoading = ref(true)
const isModalOpen = ref(false)
const dogName = ref('')
const dogBirthday = ref('')
const createErrorMessage = ref('')
const isCreatingDog = ref(false)

const dogCountLabel = computed(() => `${dogsResponse.value?.dogs.length ?? 0}匹`)

async function loadDogs(): Promise<void> {
  if (!owner) {
    return
  }

  isLoading.value = true
  errorMessage.value = ''

  try {
    dogsResponse.value = await fetchOwnerDogs(owner.owner_id)
  } catch (error) {
    dogsResponse.value = null
    errorMessage.value = toErrorMessage(error, '犬一覧の取得に失敗しました。')
  } finally {
    isLoading.value = false
  }
}

function openDogModal(): void {
  createErrorMessage.value = ''
  isModalOpen.value = true
}

function closeDogModal(): void {
  isModalOpen.value = false
  createErrorMessage.value = ''
}

function resetDogForm(): void {
  dogName.value = ''
  dogBirthday.value = ''
}

function validateDogForm(): string {
  const normalizedDogName = dogName.value.trim()

  if (!normalizedDogName) {
    return '犬の名前は必須です。'
  }
  if (normalizedDogName.length < 2 || normalizedDogName.length > 20) {
    return '犬の名前は2文字以上20文字以下で入力してください。'
  }
  if (!dogBirthday.value) {
    return '誕生日は必須です。'
  }

  return ''
}

async function submitDog(): Promise<void> {
  if (!owner) {
    return
  }

  createErrorMessage.value = ''

  const validationMessage = validateDogForm()
  if (validationMessage) {
    createErrorMessage.value = validationMessage
    return
  }

  isCreatingDog.value = true
  try {
    await createDog({
      owner_id: owner.owner_id,
      name: dogName.value.trim(),
      birthday: dogBirthday.value,
    })
    closeDogModal()
    resetDogForm()
    await loadDogs()
  } catch (error) {
    createErrorMessage.value = toErrorMessage(error, '犬の登録に失敗しました。')
  } finally {
    isCreatingDog.value = false
  }
}

function handleEscape(event: KeyboardEvent): void {
  if (event.key === 'Escape' && isModalOpen.value && !isCreatingDog.value) {
    closeDogModal()
  }
}

onMounted(() => {
  void loadDogs()
  window.addEventListener('keydown', handleEscape)
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', handleEscape)
})
</script>

<template>
  <section class="dogs-page">
    <article class="panel strong">
      <p class="eyebrow">犬一覧</p>
      <h2>{{ dogsResponse?.owner_name ?? owner?.name ?? '飼い主' }}さんの犬一覧</h2>

      <div class="stat-grid stat-card-spacious">
        <div class="stat-card">
          <p class="hint">ログインID</p>
          <p class="stat-value">{{ owner?.login_id ?? '-' }}</p>
        </div>
        <div class="stat-card">
          <p class="hint">現在の登録数</p>
          <p class="stat-value">{{ isLoading ? '読み込み中...' : dogCountLabel }}</p>
        </div>
      </div>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <div v-else-if="isLoading" class="callout">
        <p class="meta-copy">バックエンドから犬一覧を読み込んでいます...</p>
      </div>

      <div v-else-if="(dogsResponse?.dogs.length ?? 0) === 0" class="callout">
        <h3>まだ犬は登録されていません</h3>
        <p class="empty-copy">
          この飼い主にはまだ犬が紐づいていません。右下の犬を登録ボタンから最初の1匹を追加してください。
        </p>
      </div>

      <ul v-else class="dog-list">
        <li v-for="dog in dogsResponse?.dogs" :key="dog.dog_id">
          <div class="dog-list-title">{{ dog.name }}</div>
          <p class="meta-copy">誕生日: {{ dog.birthday }}</p>
        </li>
      </ul>

      <div class="actions actions-spacious">
        <button class="primary-button" type="button" @click="openDogModal">
          犬を登録
        </button>
        <button class="ghost-button" type="button" @click="loadDogs" :disabled="isLoading">
          {{ isLoading ? '更新中...' : '一覧を更新' }}
        </button>
      </div>
    </article>

    <div v-if="isModalOpen" class="modal-backdrop" @click.self="closeDogModal">
      <section class="modal-card">
        <div class="modal-header">
          <div>
            <p class="eyebrow">犬の登録</p>
            <h3>{{ owner?.name ?? 'この飼い主' }}の犬を追加</h3>
          </div>
          <button class="ghost-button modal-close-button" type="button" @click="closeDogModal">
            閉じる
          </button>
        </div>

        <form class="form" @submit.prevent="submitDog">
          <div class="field">
            <label for="dog-name">犬の名前</label>
            <input id="dog-name" v-model="dogName" maxlength="20" />
            <p class="hint">必須です。2文字以上20文字以下で入力してください。</p>
          </div>

          <div class="field field-spacious">
            <label for="dog-birthday">誕生日</label>
            <input id="dog-birthday" v-model="dogBirthday" type="date" />
          </div>

          <p v-if="createErrorMessage" class="error-text">{{ createErrorMessage }}</p>

          <div class="actions">
            <button class="primary-button" type="submit" :disabled="isCreatingDog">
              {{ isCreatingDog ? '登録中...' : '犬を登録' }}
            </button>
            <button class="ghost-button" type="button" :disabled="isCreatingDog" @click="closeDogModal">
              キャンセル
            </button>
          </div>
        </form>
      </section>
    </div>
  </section>
</template>
