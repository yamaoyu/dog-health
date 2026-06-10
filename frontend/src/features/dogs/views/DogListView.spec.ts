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

  it('犬一覧APIを呼び、取得した犬情報を表示する', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        owner_id: 'owner-1',
        owner_name: 'Hanako',
        dogs: [
          {
            dog_id: 'dog-1',
            name: 'Pochi',
            birthday: null,
            gender: 'male',
          },
          {
            dog_id: 'dog-2',
            name: 'Hana',
            birthday: '2021-02-03',
            gender: 'female',
          },
          {
            dog_id: 'dog-3',
            name: 'Mugi',
            birthday: null,
            gender: null,
          },
        ],
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
    expect(await screen.findByText('Pochi')).toBeTruthy()
    expect(screen.getByText('Hana')).toBeTruthy()
    expect(screen.getByText('Mugi')).toBeTruthy()
    expect(screen.getAllByText('誕生日: 未登録')).toHaveLength(2)
    expect(screen.getByText('性別: ♂')).toBeTruthy()
    expect(screen.getByText('性別: ♀')).toBeTruthy()
    expect(screen.getByText('性別: 不明')).toBeTruthy()
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

  it('現在の飼い主が更新されると飼い主情報の表示を更新する', async () => {
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

    setCurrentOwner({
      owner_id: 'owner-1',
      name: 'Taro',
      login_id: 'taro',
    })

    expect(await screen.findByText('Taroさんの犬一覧')).toBeTruthy()
    expect(screen.getByText('taro')).toBeTruthy()
    expect(fetchMock).toHaveBeenCalledTimes(1)
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
            gender: 'female',
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
    await user.selectOptions(within(dialog).getByLabelText('性別'), 'female')
    await user.click(within(dialog).getByRole('button', { name: '犬を登録' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://localhost:8010/dogs', {
      method: 'POST',
      body: JSON.stringify({
        owner_id: 'owner-1',
        name: 'Pochi',
        birthday: '2020-01-01',
        gender: 'female',
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
  })

  it('犬登録フォームは誕生日と性別が未入力でも犬作成APIを呼ぶ', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/dogs') && init?.method === 'POST') {
        return Promise.resolve(
          jsonResponse({
            dog_id: 'dog-1',
            owner_id: 'owner-1',
            name: 'Pochi',
            birthday: null,
            gender: null,
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
    await user.click(within(dialog).getByRole('button', { name: '犬を登録' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://localhost:8010/dogs', {
      method: 'POST',
      body: JSON.stringify({
        owner_id: 'owner-1',
        name: 'Pochi',
        birthday: null,
        gender: null,
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

  it('プロフィール更新から編集して保存すると犬更新APIが正しいpayloadで呼ばれる', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/dogs/dog-1') && init?.method === 'PATCH') {
        return Promise.resolve(
          jsonResponse({
            dog_id: 'dog-1',
            name: 'Hachi',
            birthday: null,
            gender: 'female',
          }),
        )
      }

      return Promise.resolve(
        jsonResponse({
          owner_id: 'owner-1',
          owner_name: 'Hanako',
          dogs: [
            {
              dog_id: 'dog-1',
              name: 'Pochi',
              birthday: '2020-01-01',
              gender: 'male',
            },
          ],
        }),
      )
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(DogListView)
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))

    await user.click(await screen.findByRole('button', { name: 'プロフィール更新' }))
    const dialog = screen.getByRole('dialog', { name: '犬プロフィール更新' })
    await user.clear(within(dialog).getByLabelText('犬の名前'))
    await user.type(within(dialog).getByLabelText('犬の名前'), ' Hachi ')
    await user.clear(within(dialog).getByLabelText('誕生日'))
    await user.selectOptions(within(dialog).getByLabelText('性別'), 'female')
    await user.click(within(dialog).getByRole('button', { name: 'プロフィールを更新' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://localhost:8010/dogs/dog-1', {
      method: 'PATCH',
      body: JSON.stringify({
        name: 'Hachi',
        birthday: null,
        gender: 'female',
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
  })

  it('犬プロフィール更新成功後に犬一覧APIが再取得される', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/dogs/dog-1') && init?.method === 'PATCH') {
        return Promise.resolve(
          jsonResponse({
            dog_id: 'dog-1',
            name: 'Hachi',
            birthday: '2021-02-03',
            gender: 'female',
          }),
        )
      }

      return Promise.resolve(
        jsonResponse({
          owner_id: 'owner-1',
          owner_name: 'Hanako',
          dogs: [
            {
              dog_id: 'dog-1',
              name: 'Pochi',
              birthday: '2020-01-01',
              gender: 'male',
            },
          ],
        }),
      )
    })
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(DogListView)
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))

    await user.click(await screen.findByRole('button', { name: 'プロフィール更新' }))
    const dialog = screen.getByRole('dialog', { name: '犬プロフィール更新' })
    await user.clear(within(dialog).getByLabelText('犬の名前'))
    await user.type(within(dialog).getByLabelText('犬の名前'), 'Hachi')
    await user.click(within(dialog).getByRole('button', { name: 'プロフィールを更新' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
    expect(fetchMock).toHaveBeenNthCalledWith(3, 'http://localhost:8010/owners/owner-1/dogs', {
      headers: {
        'Content-Type': 'application/json',
      },
    })
  })

  it('犬プロフィール更新フォームで入力エラーがある場合は犬更新APIを呼ばない', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        owner_id: 'owner-1',
        owner_name: 'Hanako',
        dogs: [
          {
            dog_id: 'dog-1',
            name: 'Pochi',
            birthday: '2020-01-01',
            gender: 'male',
          },
        ],
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    render(DogListView)
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))

    await user.click(await screen.findByRole('button', { name: 'プロフィール更新' }))
    const dialog = screen.getByRole('dialog', { name: '犬プロフィール更新' })
    await user.clear(within(dialog).getByLabelText('犬の名前'))
    await user.click(within(dialog).getByRole('button', { name: 'プロフィールを更新' }))

    expect(await within(dialog).findByText('犬の名前は必須です。')).toBeTruthy()
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })
})
