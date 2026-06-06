<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { toErrorMessage } from '../../../lib/api'
import type { Owner } from '../services/ownersApi'
import { updateOwner } from '../services/ownersApi'

const props = defineProps<{
  owner: Owner
}>()

const emit = defineEmits<{
  updated: [owner: Owner]
  logout: []
}>()

const userMenuRef = ref<HTMLElement | null>(null)
const isUserMenuOpen = ref(false)
const isProfileModalOpen = ref(false)
const profileName = ref('')
const profileLoginId = ref('')
const profileErrorMessage = ref('')
const isUpdatingProfile = ref(false)

function toggleUserMenu(): void {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

function openProfileModal(): void {
  profileName.value = props.owner.name
  profileLoginId.value = props.owner.login_id
  profileErrorMessage.value = ''
  isUserMenuOpen.value = false
  isProfileModalOpen.value = true
}

function closeProfileModal(): void {
  if (isUpdatingProfile.value) {
    return
  }

  isProfileModalOpen.value = false
  profileErrorMessage.value = ''
}

function validateProfileForm(): string {
  const normalizedName = profileName.value.trim()
  const normalizedLoginId = profileLoginId.value.trim()

  if (!normalizedName) {
    return 'ユーザー名は必須です。'
  }
  if (normalizedName.length > 20) {
    return 'ユーザー名は20文字以内で入力してください。'
  }
  if (!normalizedLoginId) {
    return 'ログインIDは必須です。'
  }
  if (normalizedLoginId.length < 4 || normalizedLoginId.length > 20) {
    return 'ログインIDは4文字以上20文字以下で入力してください。'
  }

  return ''
}

async function submitProfile(): Promise<void> {
  profileErrorMessage.value = ''

  const validationMessage = validateProfileForm()
  if (validationMessage) {
    profileErrorMessage.value = validationMessage
    return
  }

  isUpdatingProfile.value = true
  try {
    const updatedOwner = await updateOwner(props.owner.owner_id, {
      name: profileName.value.trim(),
      login_id: profileLoginId.value.trim(),
    })
    emit('updated', updatedOwner)
    isProfileModalOpen.value = false
  } catch (error) {
    profileErrorMessage.value = toErrorMessage(error, 'プロフィールの更新に失敗しました。')
  } finally {
    isUpdatingProfile.value = false
  }
}

function emitLogout(): void {
  isUserMenuOpen.value = false
  isProfileModalOpen.value = false
  emit('logout')
}

function handleDocumentClick(event: MouseEvent): void {
  if (!isUserMenuOpen.value || !userMenuRef.value) {
    return
  }

  if (!userMenuRef.value.contains(event.target as Node)) {
    isUserMenuOpen.value = false
  }
}

function handleEscape(event: KeyboardEvent): void {
  if (event.key !== 'Escape') {
    return
  }

  if (isProfileModalOpen.value && !isUpdatingProfile.value) {
    closeProfileModal()
    return
  }

  if (isUserMenuOpen.value) {
    isUserMenuOpen.value = false
  }
}

onMounted(() => {
  window.addEventListener('click', handleDocumentClick)
  window.addEventListener('keydown', handleEscape)
})

onBeforeUnmount(() => {
  window.removeEventListener('click', handleDocumentClick)
  window.removeEventListener('keydown', handleEscape)
})
</script>

<template>
  <div ref="userMenuRef" class="user-menu">
    <button
      class="user-icon-button"
      type="button"
      aria-label="ユーザーメニュー"
      :aria-expanded="isUserMenuOpen"
      @click.stop="toggleUserMenu"
    >
      {{ owner.name.slice(0, 1) }}
    </button>

    <div v-if="isUserMenuOpen" class="user-menu-panel" role="menu">
      <p class="user-menu-name">{{ owner.name }}</p>
      <button class="menu-button" type="button" role="menuitem" @click="openProfileModal">
        プロフィール更新
      </button>
      <button class="menu-button" type="button" role="menuitem" @click="emitLogout">
        ログアウト
      </button>
    </div>
  </div>

  <div v-if="isProfileModalOpen" class="modal-backdrop" @click.self="closeProfileModal">
    <section class="modal-card" role="dialog" aria-modal="true" aria-labelledby="profile-title">
      <div class="modal-header">
        <div>
          <h3 id="profile-title">プロフィール更新</h3>
        </div>
      </div>

      <form class="form" @submit.prevent="submitProfile">
        <div class="field">
          <label for="profile-name">飼い主名</label>
          <input id="profile-name" v-model="profileName" autocomplete="name" maxlength="20" />
          <p class="hint">必須です。20文字以内で入力してください。</p>
        </div>

        <div class="field">
          <label for="profile-login-id">ログインID</label>
          <input
            id="profile-login-id"
            v-model="profileLoginId"
            autocomplete="username"
            maxlength="20"
          />
          <p class="hint">必須です。4文字以上20文字以下で入力してください。</p>
        </div>

        <p v-if="profileErrorMessage" class="error-text">{{ profileErrorMessage }}</p>

        <div class="actions">
          <button class="primary-button" type="submit" :disabled="isUpdatingProfile">
            {{ isUpdatingProfile ? '更新中...' : 'プロフィールを更新' }}
          </button>
          <button
            class="ghost-button"
            type="button"
            :disabled="isUpdatingProfile"
            @click="closeProfileModal"
          >
            キャンセル
          </button>
        </div>
      </form>
    </section>
  </div>
</template>
