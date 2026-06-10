import { render, screen, waitFor, within } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi } from 'vitest'
import UserMenu from './UserMenu.vue'

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

function renderUserMenu() {
  return render(UserMenu, {
    props: {
      owner: {
        owner_id: 'owner-1',
        name: 'Hanako',
        login_id: 'hanako',
      },
    },
  })
}

describe('UserMenu', () => {
  it('プロフィール更新ボタンを押すと飼い主更新APIが呼ばれる', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        owner_id: 'owner-1',
        name: 'Taro',
        login_id: 'taro',
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    const { emitted } = renderUserMenu()

    await user.click(screen.getByRole('button', { name: 'ユーザーメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'プロフィール更新' }))
    const dialog = screen.getByRole('dialog', { name: 'プロフィール更新' })
    await user.clear(within(dialog).getByLabelText('飼い主名'))
    await user.type(within(dialog).getByLabelText('飼い主名'), ' Taro ')
    await user.clear(within(dialog).getByLabelText('ログインID'))
    await user.type(within(dialog).getByLabelText('ログインID'), ' taro ')
    await user.click(within(dialog).getByRole('button', { name: 'プロフィールを更新' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8010/owners/owner-1', {
      method: 'PATCH',
      body: JSON.stringify({
        name: 'Taro',
        login_id: 'taro',
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
    expect(emitted('updated')).toEqual([
      [
        {
          owner_id: 'owner-1',
          name: 'Taro',
          login_id: 'taro',
        },
      ],
    ])
  })

  it('プロフィール更新フォームで入力エラーがある場合はAPIを呼ばない', async () => {
    const fetchMock = vi.fn()
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    renderUserMenu()

    await user.click(screen.getByRole('button', { name: 'ユーザーメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'プロフィール更新' }))
    const dialog = screen.getByRole('dialog', { name: 'プロフィール更新' })
    await user.clear(within(dialog).getByLabelText('飼い主名'))
    await user.click(within(dialog).getByRole('button', { name: 'プロフィールを更新' }))

    expect(await within(dialog).findByText('ユーザー名は必須です。')).toBeTruthy()
    expect(fetchMock).not.toHaveBeenCalled()
  })
})
