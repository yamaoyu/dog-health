import { render, screen, waitFor } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import type { Component } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import DogListView from '../../dogs/views/DogListView.vue'
import OwnerRegistrationView from '../../owners/views/OwnerRegistrationView.vue'
import { clearCurrentOwner } from '../session'
import LoginView from './LoginView.vue'

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

async function renderWithRouter(component: Component, initialPath: string) {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/register', name: 'owner-register', component: OwnerRegistrationView },
      { path: '/login', name: 'login', component: LoginView },
      { path: '/dogs', name: 'dogs', component: DogListView },
    ],
  })

  await router.push(initialPath)
  render(component, {
    global: {
      plugins: [router],
    },
  })
  await router.isReady()

  return { router }
}

describe('LoginView', () => {
  beforeEach(() => {
    clearCurrentOwner()
  })

  it('ログインボタンをクリックするとログインAPIが呼ばれる', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        owner_id: 'owner-1',
        name: 'Hanako',
        login_id: 'hanako',
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    const { router } = await renderWithRouter(LoginView, '/login')

    await user.type(screen.getByLabelText('ログインID'), ' hanako ')
    await user.click(screen.getByRole('button', { name: 'ログイン' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8010/sessions', {
      method: 'POST',
      body: JSON.stringify({
        login_id: 'hanako',
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
    await waitFor(() => expect(router.currentRoute.value.path).toBe('/dogs'))
  })

  it('ログインフォームで入力エラーがある場合はAPIを呼ばない', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    await renderWithRouter(LoginView, '/login')

    await user.click(screen.getByRole('button', { name: 'ログイン' }))

    expect(await screen.findByText('ログインIDは必須です。')).toBeTruthy()
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
