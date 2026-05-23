<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { toErrorMessage } from '../../../lib/api'
import { createOwner } from '../services/ownersApi'

const router = useRouter()

const name = ref('')
const loginId = ref('')
const errorMessage = ref('')
const isSubmitting = ref(false)

function validate(): string {
  const normalizedName = name.value.trim()
  const normalizedLoginId = loginId.value.trim()

  if (!normalizedName) {
    return 'User name is required.'
  }
  if (normalizedName.length > 20) {
    return 'User name must be 20 characters or fewer.'
  }
  if (!normalizedLoginId) {
    return 'Login ID is required.'
  }
  if (normalizedLoginId.length < 4 || normalizedLoginId.length > 20) {
    return 'Login ID must be between 4 and 20 characters.'
  }

  return ''
}

async function submit(): Promise<void> {
  errorMessage.value = ''

  const validationMessage = validate()
  if (validationMessage) {
    errorMessage.value = validationMessage
    return
  }

  isSubmitting.value = true
  try {
    const owner = await createOwner({
      name: name.value.trim(),
      login_id: loginId.value.trim(),
    })
    await router.push({
      name: 'login',
      query: {
        loginId: owner.login_id,
        created: '1',
      },
    })
  } catch (error) {
    errorMessage.value = toErrorMessage(error, 'Failed to create user.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="page-grid">
    <article class="panel strong">
      <p class="eyebrow">Owner Setup</p>
      <h2>Create a user before tracking any dogs.</h2>
      <p class="lead">
        Register the owner name and login ID first. This app uses the login ID later to enter the
        dogs screen.
      </p>

      <form class="form" @submit.prevent="submit">
        <div class="field">
          <label for="owner-name">User name</label>
          <input id="owner-name" v-model="name" autocomplete="name" maxlength="20" />
          <p class="hint">Required. Up to 20 characters.</p>
        </div>

        <div class="field">
          <label for="owner-login-id">Login ID</label>
          <input id="owner-login-id" v-model="loginId" autocomplete="username" maxlength="20" />
          <p class="hint">Required. Use 4-20 characters.</p>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <div class="actions">
          <button class="primary-button" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Creating user...' : 'Create user' }}
          </button>
          <RouterLink class="nav-link" to="/login">Already have a login ID</RouterLink>
        </div>
      </form>
    </article>

    <aside class="panel stack">
      <div class="callout">
        <h3>Current MVP scope</h3>
        <p class="meta-copy">
          Dog creation is intentionally out of scope. A newly created user can log in right away and
          see an empty dogs list.
        </p>
      </div>

      <ul class="meta-list">
        <li>
          <strong>Explicit contract</strong>
          <p class="meta-copy">The backend validates both fields and rejects duplicate login IDs.</p>
        </li>
        <li>
          <strong>Simple flow</strong>
          <p class="meta-copy">Create the user first, then move to login with the same ID.</p>
        </li>
      </ul>
    </aside>
  </section>
</template>
