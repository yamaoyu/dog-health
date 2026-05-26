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
  route.query.created === '1' ? 'ユーザーを登録しました。登録したログインIDでログインしてください。' : '',
)
const isSubmitting = ref(false)

function validate(): string {
  const normalizedLoginId = loginId.value.trim()
  if (!normalizedLoginId) {
    return 'ログインIDは必須です。'
  }
  if (normalizedLoginId.length < 4 || normalizedLoginId.length > 20) {
    return 'ログインIDは4文字以上20文字以下で入力してください。'
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
    errorMessage.value = toErrorMessage(error, 'ログインに失敗しました。')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="page-grid">
    <article class="panel strong">
      <p class="eyebrow">ログイン</p>
      <h2>登録済みのログインIDでログインしてください。</h2>
      <p class="lead">
        このMVPでは認証をシンプルにしています。パスワードは使わず、ログインIDで飼い主を特定します。
      </p>

      <form class="form" @submit.prevent="submit">
        <div class="field field-spacious">
          <label for="login-id">ログインID</label>
          <input id="login-id" v-model="loginId" autocomplete="username" maxlength="20" />
          <p class="hint">4文字以上20文字以下で入力してください。</p>
        </div>

        <p v-if="successMessage" class="success-text">{{ successMessage }}</p>
        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <div class="actions">
          <button class="primary-button" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? 'ログイン中...' : 'ログイン' }}
          </button>
          <RouterLink class="nav-link" to="/register">ユーザー登録をする</RouterLink>
        </div>
      </form>
    </article>

    <aside class="panel stack">
      <div class="callout">
        <h3>ログイン後の流れ</h3>
        <p class="meta-copy">
          ログイン後は、その飼い主に紐づく犬の一覧を読み込みます。新しく作成した飼い主では、最初は0件が表示されます。
        </p>
      </div>

      <ul class="meta-list">
        <li>
          <strong>パスワードなし</strong>
          <p class="meta-copy">MVPとして認証方式を簡略化しています。</p>
        </li>
        <li>
          <strong>メモリ上のセッションのみ</strong>
          <p class="meta-copy">このバージョンではページを再読み込みするとログイン状態は解除されます。</p>
        </li>
      </ul>
    </aside>
  </section>
</template>
