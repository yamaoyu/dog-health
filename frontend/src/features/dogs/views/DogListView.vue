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

const dogCountLabel = computed(() => `${dogsResponse.value?.dogs.length ?? 0} dogs`)

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
    errorMessage.value = toErrorMessage(error, 'Failed to load dogs.')
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
    return 'Dog name is required.'
  }
  if (normalizedDogName.length < 2 || normalizedDogName.length > 20) {
    return 'Dog name must be between 2 and 20 characters.'
  }
  if (!dogBirthday.value) {
    return 'Birthday is required.'
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
    createErrorMessage.value = toErrorMessage(error, 'Failed to register dog.')
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
      <p class="eyebrow">Dog List</p>
      <h2>{{ dogsResponse?.owner_name ?? owner?.name ?? 'Owner' }}'s dogs</h2>
      <p class="lead">This screen loads the dogs linked to the logged-in owner.</p>

      <div class="stat-grid stat-card-spacious">
        <div class="stat-card">
          <p class="hint">Login ID</p>
          <p class="stat-value">{{ owner?.login_id ?? '-' }}</p>
        </div>
        <div class="stat-card">
          <p class="hint">Current list</p>
          <p class="stat-value">{{ isLoading ? 'Loading...' : dogCountLabel }}</p>
        </div>
      </div>

      <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

      <div v-else-if="isLoading" class="callout">
        <p class="meta-copy">Loading dogs from the backend...</p>
      </div>

      <div v-else-if="(dogsResponse?.dogs.length ?? 0) === 0" class="callout">
        <h3>0 dogs yet</h3>
        <p class="empty-copy">
          No dogs are linked to this owner yet. Use the register dog button at the bottom right to
          add the first one.
        </p>
      </div>

      <ul v-else class="dog-list">
        <li v-for="dog in dogsResponse?.dogs" :key="dog.dog_id">
          <div class="dog-list-title">{{ dog.name }}</div>
          <p class="meta-copy">Birthday: {{ dog.birthday }}</p>
        </li>
      </ul>

      <div class="actions actions-spacious">
        <button class="primary-button" type="button" @click="openDogModal">
          Register dog
        </button>
        <button class="ghost-button" type="button" @click="loadDogs" :disabled="isLoading">
          {{ isLoading ? 'Refreshing...' : 'Refresh list' }}
        </button>
      </div>
    </article>

    <div v-if="isModalOpen" class="modal-backdrop" @click.self="closeDogModal">
      <section class="modal-card">
        <div class="modal-header">
          <div>
            <p class="eyebrow">Dog Registration</p>
            <h3>Add a dog for {{ owner?.name ?? 'this owner' }}</h3>
          </div>
          <button class="ghost-button modal-close-button" type="button" @click="closeDogModal">
            Close
          </button>
        </div>

        <form class="form" @submit.prevent="submitDog">
          <div class="field">
            <label for="dog-name">Dog name</label>
            <input id="dog-name" v-model="dogName" maxlength="20" />
            <p class="hint">Required. Use 2-20 characters.</p>
          </div>

          <div class="field field-spacious">
            <label for="dog-birthday">Birthday</label>
            <input id="dog-birthday" v-model="dogBirthday" type="date" />
          </div>

          <p v-if="createErrorMessage" class="error-text">{{ createErrorMessage }}</p>

          <div class="actions">
            <button class="primary-button" type="submit" :disabled="isCreatingDog">
              {{ isCreatingDog ? 'Registering...' : 'Register dog' }}
            </button>
            <button class="ghost-button" type="button" :disabled="isCreatingDog" @click="closeDogModal">
              Cancel
            </button>
          </div>
        </form>
      </section>
    </div>
  </section>
</template>
