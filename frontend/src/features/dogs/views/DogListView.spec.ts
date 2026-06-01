import { render, screen, waitFor, within } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { clearCurrentOwner, setCurrentOwner } from '../../auth/session'
import DogListView from './DogListView.vue'

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

function setLoggedInOwner(): void {
  setCurrentOwner({
    owner_id: 'owner-1',
    name: 'Hanako',
    login_id: 'hanako',
  })
}

describe('DogListView', () => {
  beforeEach(() => {
    clearCurrentOwner()
  })

  it('犬一覧画面の初期表示で犬一覧APIが呼ばれる', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        owner_id: 'owner-1',
        owner_name: 'Hanako',
        dogs: [],
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    render(DogListView)

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
    expect(fetchMock).toHaveBeenCalledWith('http://localhost:8010/owners/owner-1/dogs', {
      headers: {
        'Content-Type': 'application/json',
      },
    })
  })

  it('一覧を更新ボタンをクリックすると犬一覧APIが再度呼ばれる', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        owner_id: 'owner-1',
        owner_name: 'Hanako',
        dogs: [],
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(DogListView)
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
    const reloadButton = await screen.findByRole('button', { name: '一覧を更新' })

    await user.click(reloadButton)

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    expect(fetchMock).toHaveBeenLastCalledWith('http://localhost:8010/owners/owner-1/dogs', {
      headers: {
        'Content-Type': 'application/json',
      },
    })
  })

  it('犬登録ボタンをクリックすると犬作成APIが呼ばれる', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/dogs') && init?.method === 'POST') {
        return Promise.resolve(
          jsonResponse({
            dog_id: 'dog-1',
            owner_id: 'owner-1',
            name: 'Pochi',
            birthday: '2020-01-01',
          }),
        )
      }

      return Promise.resolve(
        jsonResponse({
          owner_id: 'owner-1',
          owner_name: 'Hanako',
          dogs: [],
        }),
      )
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(DogListView)
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))

    await user.click(screen.getByRole('button', { name: '犬を登録' }))
    const dialog = screen.getByRole('dialog')
    await user.type(within(dialog).getByLabelText('犬の名前'), 'Pochi')
    await user.type(within(dialog).getByLabelText('誕生日'), '2020-01-01')
    await user.click(within(dialog).getByRole('button', { name: '犬を登録' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://localhost:8010/dogs', {
      method: 'POST',
      body: JSON.stringify({
        owner_id: 'owner-1',
        name: 'Pochi',
        birthday: '2020-01-01',
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
  })

  it('犬登録フォームで入力エラーがある場合は犬作成APIを呼ばない', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        owner_id: 'owner-1',
        owner_name: 'Hanako',
        dogs: [],
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(DogListView)
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))

    await user.click(screen.getByRole('button', { name: '犬を登録' }))
    const dialog = screen.getByRole('dialog')
    await user.click(within(dialog).getByRole('button', { name: '犬を登録' }))

    expect(await within(dialog).findByText('犬の名前は必須です。')).toBeTruthy()
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
})
