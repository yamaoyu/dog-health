<script setup lang="ts">
import { ref } from 'vue'
import { RouterLink, useRoute, useRouter } from 'vue-router'
import { toErrorMessage } from '../../../lib/api'
import { login } from '../services/loginApi'
import { setCurrentOwner } from '../session'

const route = useRoute()
const router = useRouter()

const loginId = ref(typeof route.query.loginId === 'string' ? route.query.loginId : '')
const errorMessage = ref('')
const successMessage = ref(
  route.query.created === '1' ? 'User created. Log in with the registered login ID.' : '',
)
const isSubmitting = ref(false)

function validate(): string {
  const normalizedLoginId = loginId.value.trim()
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
  successMessage.value = ''

  const validationMessage = validate()
  if (validationMessage) {
    errorMessage.value = validationMessage
    return
  }

  isSubmitting.value = true
  try {
    const owner = await login({ login_id: loginId.value.trim() })
    setCurrentOwner(owner)
    await router.push({ name: 'dogs' })
  } catch (error) {
    errorMessage.value = toErrorMessage(error, 'Failed to log in.')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="page-grid">
    <article class="panel strong">
      <p class="eyebrow">Temporary Login</p>
      <h2>Log in with your registered login ID.</h2>
      <p class="lead">
        This MVP keeps authentication intentionally simple. No password, no persistence, just owner
        resolution by login ID.
      </p>

      <form class="form" @submit.prevent="submit">
        <div class="field field-spacious">
          <label for="login-id">Login ID</label>
          <input id="login-id" v-model="loginId" autocomplete="username" maxlength="20" />
          <p class="hint">Use 4-20 characters. Spaces around the value are trimmed.</p>
        </div>

        <p v-if="successMessage" class="success-text">{{ successMessage }}</p>
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <div class="actions">
          <button class="primary-button" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'Logging in...' : 'Login' }}
          </button>
          <RouterLink class="nav-link" to="/register">Create user first</RouterLink>
        </div>
      </form>
    </article>

    <aside class="panel stack">
      <div class="callout">
        <h3>What happens next</h3>
        <p class="meta-copy">
          After login, the app loads the dogs linked to the selected owner. A newly created owner is
          expected to see 0 dogs for now.
        </p>
      </div>

      <ul class="meta-list">
        <li>
          <strong>No password</strong>
          <p class="meta-copy">This follows the simplified MVP authentication approach.</p>
        </li>
        <li>
          <strong>Memory-only session</strong>
          <p class="meta-copy">Refreshing the page clears the login state in this version.</p>
        </li>
      </ul>
    </aside>
  </section>
</template>
