<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { clearCurrentOwner, useCurrentOwner } from './features/auth/session'

const currentOwner = useCurrentOwner()
const route = useRoute()
const router = useRouter()

const isLoggedIn = computed(() => currentOwner.value !== null)
const isDogsRoute = computed(() => route.name === 'dogs')

async function logout(): Promise<void> {
  clearCurrentOwner()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <RouterLink class="brand-title" to="/">DOG HEALTH RECORD</RouterLink>

      <nav class="topbar-nav">
        <template v-if="isLoggedIn">
          <span class="owner-chip">{{ currentOwner?.name }}</span>
          <RouterLink class="nav-link" :class="{ active: isDogsRoute }" to="/dogs">Dogs</RouterLink>
          <button class="ghost-button" type="button" @click="logout">Logout</button>
        </template>

        <template v-else>
          <RouterLink
            class="nav-link"
            :class="{ active: route.name === 'owner-register' }"
            to="/register"
          >
            Create user
          </RouterLink>
          <RouterLink class="nav-link" :class="{ active: route.name === 'login' }" to="/login">
            Login
          </RouterLink>
        </template>
      </nav>
    </header>

    <main class="page-frame">
      <RouterView />
    </main>
  </div>
</template>
