import { render, screen, waitFor } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import type { Component } from 'vue'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import LoginView from '../../auth/views/LoginView.vue'
import { clearCurrentOwner } from '../../auth/session'
import DogListView from '../../dogs/views/DogListView.vue'
import OwnerRegistrationView from './OwnerRegistrationView.vue'

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

describe('OwnerRegistrationView', () => {
  beforeEach(() => {
    clearCurrentOwner()
  })

  it('飼い主登録ボタンをクリックすると飼い主作成APIが呼ばれる', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        owner_id: 'owner-1',
        name: 'Hanako',
        login_id: 'hanako',
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    const { router } = await renderWithRouter(OwnerRegistrationView, '/register')

    await user.type(screen.getByLabelText('飼い主名'), ' Hanako ')
    await user.type(screen.getByLabelText('ログインID'), ' hanako ')
    await user.click(screen.getByRole('button', { name: '飼い主を登録' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8010/owners', {
      method: 'POST',
      body: JSON.stringify({
        name: 'Hanako',
        login_id: 'hanako',
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
    await waitFor(() => {
      expect(router.currentRoute.value.path).toBe('/login')
      expect(router.currentRoute.value.query).toEqual({
        loginId: 'hanako',
        created: '1',
      })
    })
  })

  it('飼い主登録フォームで入力エラーがある場合はAPIを呼ばない', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    await renderWithRouter(OwnerRegistrationView, '/register')

    await user.click(screen.getByRole('button', { name: '飼い主を登録' }))

    expect(await screen.findByText('ユーザー名は必須です。')).toBeTruthy()
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
