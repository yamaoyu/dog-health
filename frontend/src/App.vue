<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { clearCurrentOwner, setCurrentOwner, useCurrentOwner } from './features/auth/session'
import UserMenu from './features/owners/components/UserMenu.vue'
import type { Owner } from './features/owners/services/ownersApi'

const currentOwner = useCurrentOwner()
const route = useRoute()
const router = useRouter()

const isLoggedIn = computed(() => currentOwner.value !== null)
const isDogsRoute = computed(() => route.name === 'dogs')

async function logout(): Promise<void> {
  clearCurrentOwner()
  await router.push({ name: 'login' })
}

function updateCurrentOwner(owner: Owner): void {
  setCurrentOwner(owner)
}
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <RouterLink class="brand-title" to="/">DOG HEALTH RECORD</RouterLink>

      <nav class="topbar-nav">
        <template v-if="isLoggedIn">
          <RouterLink class="nav-link" :class="{ active: isDogsRoute }" to="/dogs">犬一覧</RouterLink>
          <UserMenu
            v-if="currentOwner"
            :owner="currentOwner"
            @updated="updateCurrentOwner"
            @logout="logout"
          />
        </template>

        <template v-else>
          <RouterLink
            class="nav-link"
            :class="{ active: route.name === 'owner-register' }"
            to="/register"
          >
            飼い主登録
          </RouterLink>
          <RouterLink class="nav-link" :class="{ active: route.name === 'login' }" to="/login">
            ログイン
          </RouterLink>
        </template>
      </nav>
    </header>

    <main class="page-frame">
      <RouterView />
    </main>
  </div>
</template>
