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
    errorMessage.value = toErrorMessage(error, 'ユーザーの登録に失敗しました。')
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="page-grid">
    <article class="panel strong">
      <h2>飼い主登録</h2>
      <p class="lead">
        飼い主名とログインIDを登録します。登録したログインIDでログインしてください。
      </p>

      <form class="form" @submit.prevent="submit">
        <div class="field">
          <label for="owner-name">飼い主名</label>
          <input id="owner-name" v-model="name" autocomplete="name" maxlength="20" />
          <p class="hint">必須です。20文字以内で入力してください。</p>
        </div>

        <div class="field">
          <label for="owner-login-id">ログインID</label>
          <input id="owner-login-id" v-model="loginId" autocomplete="username" maxlength="20" />
          <p class="hint">必須です。4文字以上20文字以下で入力してください。</p>
        </div>

        <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

        <div class="actions">
          <button class="primary-button" type="submit" :disabled="isSubmitting">
            {{ isSubmitting ? '登録中...' : '飼い主を登録' }}
          </button>
          <RouterLink class="nav-link" to="/login">ログインIDをお持ちの方はこちら</RouterLink>
        </div>
      </form>
    </article>

    <aside class="panel stack">
      <div class="callout">
        <h3>現在のMVP範囲</h3>
        <p class="meta-copy">
          この段階ではまず基本的な登録とログインに絞っています。新しく作成した飼い主はすぐにログインでき、最初は空の犬一覧が表示されます。
        </p>
      </div>

      <ul class="meta-list">
        <li>
          <strong>明確な入力ルール</strong>
          <p class="meta-copy">バックエンドで両方の項目を検証し、重複するログインIDは拒否します。</p>
        </li>
        <li>
          <strong>シンプルな流れ</strong>
          <p class="meta-copy">最初に飼い主を登録し、その後同じログインIDでログインします。</p>
        </li>
      </ul>
    </aside>
  </section>
</template>
