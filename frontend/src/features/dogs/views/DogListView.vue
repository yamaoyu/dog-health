<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { toErrorMessage } from '../../../lib/api'
import { getCurrentOwner } from '../../auth/session'
import { fetchOwnerDogs, type OwnerDogsResponse } from '../services/dogsApi'

const owner = getCurrentOwner()
const dogsResponse = ref<OwnerDogsResponse | null>(null)
const errorMessage = ref('')
const isLoading = ref(true)

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

onMounted(() => {
  void loadDogs()
})
</script>

<template>
  <section>
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
          No dogs are linked to this owner yet. That is expected for this step because dog creation
          is not part of the current scope.
        </p>
      </div>

      <ul v-else class="dog-list">
        <li v-for="dog in dogsResponse?.dogs" :key="dog.dog_id">
          <div class="dog-list-title">{{ dog.name }}</div>
          <p class="meta-copy">Birthday: {{ dog.birthday }}</p>
          <p class="meta-copy">Role: {{ dog.role ?? 'not set' }}</p>
        </li>
      </ul>

      <div class="actions actions-spacious">
        <button class="ghost-button" type="button" @click="loadDogs" :disabled="isLoading">
          {{ isLoading ? 'Refreshing...' : 'Refresh list' }}
        </button>
      </div>
    </article>
  </section>
</template>
