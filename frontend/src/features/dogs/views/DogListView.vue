<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'
import { toErrorMessage } from '../../../lib/api'
import { getCurrentOwner } from '../../auth/session'
import {
  createDog,
  fetchOwnerDogs,
  updateDog,
  type DogGender,
  type OwnerDog,
  type OwnerDogsResponse,
} from '../services/dogsApi'

const owner = getCurrentOwner()
const dogsResponse = ref<OwnerDogsResponse | null>(null)
const errorMessage = ref('')
const isLoading = ref(true)
const isModalOpen = ref(false)
const dogName = ref('')
const dogBirthday = ref('')
const createErrorMessage = ref('')
const isCreatingDog = ref(false)
const selectedDog = ref<OwnerDog | null>(null)
const updateDogName = ref('')
const updateDogBirthday = ref('')
const updateDogGender = ref<DogGender | ''>('')
const updateErrorMessage = ref('')
const isUpdatingDog = ref(false)

const dogCountLabel = computed(() => `${dogsResponse.value?.dogs.length ?? 0}匹`)
const isUpdateModalOpen = computed(() => selectedDog.value !== null)

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

function openDogUpdateModal(dog: OwnerDog): void {
  selectedDog.value = dog
  updateDogName.value = dog.name
  updateDogBirthday.value = dog.birthday ?? ''
  updateDogGender.value = dog.gender ?? ''
  updateErrorMessage.value = ''
}

function closeDogUpdateModal(): void {
  if (isUpdatingDog.value) {
    return
  }

  selectedDog.value = null
  updateErrorMessage.value = ''
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

function validateDogUpdateForm(): string {
  const normalizedDogName = updateDogName.value.trim()

  if (!normalizedDogName) {
    return '犬の名前は必須です。'
  }
  if (normalizedDogName.length < 2 || normalizedDogName.length > 20) {
    return '犬の名前は2文字以上20文字以下で入力してください。'
  }

  return ''
}

function formatDogGender(gender: DogGender | null): string {
  if (gender === 'male') {
    return '♂'
  }

  if (gender === 'female') {
    return '♀'
  }

  return '不明'
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

async function submitDogUpdate(): Promise<void> {
  if (!selectedDog.value) {
    return
  }

  updateErrorMessage.value = ''

  const validationMessage = validateDogUpdateForm()
  if (validationMessage) {
    updateErrorMessage.value = validationMessage
    return
  }

  isUpdatingDog.value = true
  try {
    await updateDog(selectedDog.value.dog_id, {
      name: updateDogName.value.trim(),
      birthday: updateDogBirthday.value || null,
      gender: updateDogGender.value || null,
    })
    selectedDog.value = null
    await loadDogs()
  } catch (error) {
    updateErrorMessage.value = toErrorMessage(error, '犬のプロフィール更新に失敗しました。')
  } finally {
    isUpdatingDog.value = false
  }
}

function handleEscape(event: KeyboardEvent): void {
  if (event.key !== 'Escape') {
    return
  }

  if (isModalOpen.value && !isCreatingDog.value) {
    closeDogModal()
    return
  }

  if (isUpdateModalOpen.value && !isUpdatingDog.value) {
    closeDogUpdateModal()
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
          <p class="meta-copy">誕生日: {{ dog.birthday ?? '未登録' }}</p>
          <p class="meta-copy">性別: {{ formatDogGender(dog.gender) }}</p>
          <div class="actions actions-spacious">
            <button class="ghost-button" type="button" @click="openDogUpdateModal(dog)">
              プロフィール更新
            </button>
          </div>
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
      <section class="modal-card" role="dialog">
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

    <div v-if="isUpdateModalOpen" class="modal-backdrop" @click.self="closeDogUpdateModal">
      <section class="modal-card" role="dialog" aria-modal="true" aria-labelledby="dog-update-title">
        <div class="modal-header">
          <div>
            <h3 id="dog-update-title">犬プロフィール更新</h3>
          </div>
        </div>

        <form class="form" @submit.prevent="submitDogUpdate">
          <div class="field">
            <label for="dog-update-name">犬の名前</label>
            <input id="dog-update-name" v-model="updateDogName" maxlength="20" />
            <p class="hint">必須です。2文字以上20文字以下で入力してください。</p>
          </div>

          <div class="field">
            <label for="dog-update-birthday">誕生日</label>
            <input id="dog-update-birthday" v-model="updateDogBirthday" type="date" />
          </div>

          <div class="field field-spacious">
            <label for="dog-update-gender">性別</label>
            <select id="dog-update-gender" v-model="updateDogGender">
              <option value="">未登録</option>
              <option value="male">おす</option>
              <option value="female">めす</option>
              <option value="unknown">不明</option>
            </select>
          </div>

          <p v-if="updateErrorMessage" class="error-text">{{ updateErrorMessage }}</p>

          <div class="actions">
            <button class="primary-button" type="submit" :disabled="isUpdatingDog">
              {{ isUpdatingDog ? '更新中...' : 'プロフィールを更新' }}
            </button>
            <button
              class="ghost-button"
              type="button"
              :disabled="isUpdatingDog"
              @click="closeDogUpdateModal"
            >
              キャンセル
            </button>
          </div>
        </form>
      </section>
    </div>
  </section>
</template>
