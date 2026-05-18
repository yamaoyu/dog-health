<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

type HealthResponse = {
  status: string
  app: string
  environment: string
  database: {
    connected: boolean
    host: string
    port: number
    name: string
    user: string
  }
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8010'
const appTitle = import.meta.env.VITE_APP_TITLE ?? 'Dog Health MVP'
const health = ref<HealthResponse | null>(null)
const errorMessage = ref('')
const isLoading = ref(true)

const connectionLabel = computed(() => {
  if (isLoading.value) {
    return 'Checking backend...'
  }

  if (errorMessage.value) {
    return 'Backend unreachable'
  }

  return 'Backend connected'
})

const architectureSummary = computed(() => {
  if (!health.value) {
    return 'Frontend, backend, and database are configured as separate services.'
  }

  return `Frontend and backend are connected, database connection is ${
    health.value.database.connected ? 'confirmed' : 'not confirmed'
  }.`
})

async function loadHealth(): Promise<void> {
  isLoading.value = true
  errorMessage.value = ''

  try {
    const response = await fetch(`${apiBaseUrl}/health`)

    if (!response.ok) {
      throw new Error(`Request failed with status ${response.status}`)
    }

    health.value = (await response.json()) as HealthResponse
  } catch (error) {
    health.value = null
    errorMessage.value =
      error instanceof Error ? error.message : 'Unknown error while loading health status'
  } finally {
    isLoading.value = false
  }
}

onMounted(() => {
  void loadHealth()
})
</script>

<template>
  <main class="layout">
    <section class="hero">
      <p class="eyebrow">{{ appTitle }}</p>
      <h1>Frontend, backend, and database are separated from day one.</h1>
      <p class="lead">{{ architectureSummary }}</p>
    </section>

    <section class="grid">
      <article class="panel status-panel">
        <div class="panel-header">
          <h2>API status</h2>
          <span class="badge" :class="{ danger: !!errorMessage }">
            {{ connectionLabel }}
          </span>
        </div>

        <p class="muted">Configured API base URL: <code>{{ apiBaseUrl }}</code></p>

        <dl v-if="health" class="details">
          <div>
            <dt>App</dt>
            <dd>{{ health.app }}</dd>
          </div>
          <div>
            <dt>Environment</dt>
            <dd>{{ health.environment }}</dd>
          </div>
          <div>
            <dt>Database host</dt>
            <dd>{{ health.database.host }}:{{ health.database.port }}</dd>
          </div>
          <div>
            <dt>Database name</dt>
            <dd>{{ health.database.name }}</dd>
          </div>
          <div>
            <dt>Database status</dt>
            <dd>{{ health.database.connected ? 'Connected' : 'Unavailable' }}</dd>
          </div>
        </dl>

        <p v-else-if="errorMessage" class="error">{{ errorMessage }}</p>
        <p v-else class="muted">Waiting for backend response.</p>

        <button class="refresh" type="button" @click="loadHealth" :disabled="isLoading">
          Refresh health check
        </button>
      </article>

      <article class="panel">
        <h2>Service split</h2>
        <ul class="service-list">
          <li><strong>frontend</strong><span>Vue 3 + TypeScript + Vite</span></li>
          <li><strong>backend</strong><span>FastAPI with explicit response schema</span></li>
          <li><strong>db</strong><span>PostgreSQL managed by Docker Compose</span></li>
        </ul>
      </article>
    </section>
  </main>
</template>
