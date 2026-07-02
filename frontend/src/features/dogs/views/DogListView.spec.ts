import { render, screen, waitFor, within } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { clearCurrentOwner, setCurrentOwner } from '../../auth/session'
import EventListView from '../../events/views/EventListView.vue'
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

function formatLocalDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'プロフィール更新' }))
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'プロフィール更新' }))
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'プロフィール更新' }))
    const dialog = screen.getByRole('dialog', { name: '犬プロフィール更新' })
    await user.clear(within(dialog).getByLabelText('犬の名前'))
    await user.click(within(dialog).getByRole('button', { name: 'プロフィールを更新' }))

    expect(await within(dialog).findByText('犬の名前は必須です。')).toBeTruthy()
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('犬メニューから飼い主追加フォームを送信すると飼い主追加APIが呼ばれる', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/dogs/dog-1/owners') && init?.method === 'POST') {
        return Promise.resolve(
          jsonResponse({
            dog: {
              dog_id: 'dog-1',
              name: 'Pochi',
            },
            owner: {
              owner_id: 'owner-2',
              name: 'Taro',
            },
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: '飼い主追加' }))
    const dialog = screen.getByRole('dialog', { name: '飼い主追加' })
    await user.type(within(dialog).getByLabelText('飼い主のログインID'), ' taro ')
    await user.click(within(dialog).getByRole('button', { name: '飼い主を追加' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://localhost:8010/dogs/dog-1/owners', {
      method: 'POST',
      body: JSON.stringify({
        login_id: 'taro',
      }),
      headers: {
        'Content-Type': 'application/json',
      },
    })
    expect(await screen.findByText('TaroさんをPochiに紐づけました。')).toBeTruthy()
  })

  it('飼い主追加フォームで入力エラーがある場合は飼い主追加APIを呼ばない', async () => {
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: '飼い主追加' }))
    const dialog = screen.getByRole('dialog', { name: '飼い主追加' })
    await user.click(within(dialog).getByRole('button', { name: '飼い主を追加' }))

    expect(await within(dialog).findByText('ログインIDは必須です。')).toBeTruthy()
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('既に紐づけられている場合飼い主追加APIのエラーをフォーム内に表示する', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/dogs/dog-1/owners') && init?.method === 'POST') {
        return Promise.resolve(jsonResponse({ detail: '既に紐づけられています' }, 409))
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: '飼い主追加' }))
    const dialog = screen.getByRole('dialog', { name: '飼い主追加' })
    await user.type(within(dialog).getByLabelText('飼い主のログインID'), 'taro')
    await user.click(within(dialog).getByRole('button', { name: '飼い主を追加' }))

    expect(await within(dialog).findByText('既に紐づけられています')).toBeTruthy()
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('犬メニューからイベント作成モーダルを開ける', async () => {
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))

    expect(screen.getByRole('menuitem', { name: 'イベント作成' })).toBeTruthy()

    await user.click(screen.getByRole('menuitem', { name: 'イベント作成' }))

    const dialog = screen.getByRole('dialog', { name: 'イベント作成' })
    expect(within(dialog).getByText('Pochiのイベントを登録します。')).toBeTruthy()
    expect(within(dialog).getByLabelText('イベントの種類')).toBeTruthy()
    expect(within(dialog).getByLabelText('日時')).toBeTruthy()
    expect(within(dialog).getByLabelText('距離 (km)')).toBeTruthy()
    expect((within(dialog).getByLabelText('距離 (km)') as HTMLInputElement).value).toBe('0')
    expect(within(dialog).getByLabelText('距離 (km)').getAttribute('max')).toBe('10')
    expect(within(dialog).getByText('時間')).toBeTruthy()
    expect((within(dialog).getByLabelText('時間の時') as HTMLInputElement).value).toBe('0')
    expect(within(dialog).getByLabelText('時間の時').getAttribute('max')).toBe('23')
    expect((within(dialog).getByLabelText('時間の分') as HTMLInputElement).value).toBe('0')
    expect(within(dialog).getByLabelText('時間の分').getAttribute('max')).toBe('59')
    expect(
      within(dialog).getByText('散歩の詳細').compareDocumentPosition(within(dialog).getByLabelText('メモ')) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()
    expect(
      within(dialog).getByText('散歩の詳細').compareDocumentPosition(within(dialog).getByLabelText('日時')) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()
    expect(
      within(dialog).getByLabelText('日時').compareDocumentPosition(within(dialog).getByLabelText('メモ')) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()
  })

  it('散歩イベントを入力して送信するとイベント作成APIが呼ばれる', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/events') && init?.method === 'POST') {
        return Promise.resolve(
          jsonResponse({
            event_id: 'event-1',
            dog_id: 'dog-1',
            event_type: {
              event_type_id: 'event-type-1',
              code: 'walk',
              display_name: '散歩',
            },
            occurred_at: '2026-06-27T12:00:00Z',
            memo: '夕方の散歩',
            detail: {
              distance_km: 2.0,
              duration_minutes: 90,
            },
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'イベント作成' }))
    const dialog = screen.getByRole('dialog', { name: 'イベント作成' })
    await user.clear(within(dialog).getByLabelText('日時'))
    await user.type(within(dialog).getByLabelText('日時'), '2026-06-27T21:00')
    await user.type(within(dialog).getByLabelText('メモ'), ' 夕方の散歩 ')
    await user.type(within(dialog).getByLabelText('距離 (km)'), '2')
    await user.clear(within(dialog).getByLabelText('時間の時'))
    await user.type(within(dialog).getByLabelText('時間の時'), '1')
    await user.clear(within(dialog).getByLabelText('時間の分'))
    await user.type(within(dialog).getByLabelText('時間の分'), '30')
    await user.click(within(dialog).getByRole('button', { name: 'イベントを登録' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    const requestBody = JSON.parse(fetchMock.mock.calls[1][1]?.body as string)
    expect(fetchMock).toHaveBeenNthCalledWith(2, 'http://localhost:8010/events', {
      method: 'POST',
      body: expect.any(String),
      headers: {
        'Content-Type': 'application/json',
      },
    })
    expect(requestBody).toEqual({
      dog_id: 'dog-1',
      event_type_code: 'walk',
      occurred_at: new Date('2026-06-27T21:00').toISOString(),
      memo: '夕方の散歩',
      detail: {
        distance_km: 2.0,
        duration_minutes: 90,
      },
    })
    expect(await screen.findByText('Pochiのイベントを登録しました。')).toBeTruthy()
  })

  it('イベント種別をご飯に変更すると詳細欄とpayloadが切り替わる', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/events') && init?.method === 'POST') {
        return Promise.resolve(
          jsonResponse({
            event_id: 'event-1',
            dog_id: 'dog-1',
            event_type: {
              event_type_id: 'event-type-2',
              code: 'food',
              display_name: 'ご飯',
            },
            occurred_at: '2026-06-27T00:00:00Z',
            memo: null,
            detail: {
              menu: 'ドライフード',
              amount_grams: 80,
            },
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'イベント作成' }))
    const dialog = screen.getByRole('dialog', { name: 'イベント作成' })
    await user.selectOptions(within(dialog).getByLabelText('イベントの種類'), 'food')

    expect(within(dialog).queryByLabelText('距離 (km)')).toBeNull()
    expect(within(dialog).queryByLabelText('時間の時')).toBeNull()
    expect(within(dialog).queryByLabelText('時間の分')).toBeNull()
    expect(within(dialog).getByLabelText('メニュー')).toBeTruthy()
    expect(within(dialog).getByLabelText('量 (g)')).toBeTruthy()
    expect((within(dialog).getByLabelText('量 (g)') as HTMLInputElement).value).toBe('0')
    expect(within(dialog).getByLabelText('量 (g)').getAttribute('max')).toBe('1000')

    await user.clear(within(dialog).getByLabelText('日時'))
    await user.type(within(dialog).getByLabelText('日時'), '2026-06-27T08:00')
    await user.type(within(dialog).getByLabelText('メニュー'), ' ドライフード ')
    await user.type(within(dialog).getByLabelText('量 (g)'), '80')
    await user.click(within(dialog).getByRole('button', { name: 'イベントを登録' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    const requestBody = JSON.parse(fetchMock.mock.calls[1][1]?.body as string)
    expect(requestBody).toEqual({
      dog_id: 'dog-1',
      event_type_code: 'food',
      occurred_at: new Date('2026-06-27T08:00').toISOString(),
      memo: null,
      detail: {
        menu: 'ドライフード',
        amount_grams: 80,
      },
    })
  })

  it('イベント種別をトイレに変更するとトイレ用の詳細欄を表示する', async () => {
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'イベント作成' }))
    const dialog = screen.getByRole('dialog', { name: 'イベント作成' })
    await user.selectOptions(within(dialog).getByLabelText('イベントの種類'), 'toilet')

    expect(within(dialog).queryByLabelText('距離 (km)')).toBeNull()
    expect(within(dialog).queryByLabelText('メニュー')).toBeNull()
    expect(within(dialog).getByLabelText('種類')).toBeTruthy()
    expect(within(dialog).getByLabelText('状態')).toBeTruthy()
  })

  it('トイレイベントを選択して送信すると選択した種類と状態がpayloadに入る', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/events') && init?.method === 'POST') {
        return Promise.resolve(
          jsonResponse({
            event_id: 'event-1',
            dog_id: 'dog-1',
            event_type: {
              event_type_id: 'event-type-3',
              code: 'toilet',
              display_name: 'トイレ',
            },
            occurred_at: '2026-06-27T00:00:00Z',
            memo: null,
            detail: {
              type: 'うんち',
              condition: '気になる',
            },
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'イベント作成' }))
    const dialog = screen.getByRole('dialog', { name: 'イベント作成' })
    await user.selectOptions(within(dialog).getByLabelText('イベントの種類'), 'toilet')
    await user.selectOptions(within(dialog).getByLabelText('種類'), 'うんち')
    await user.selectOptions(within(dialog).getByLabelText('状態'), '気になる')
    await user.clear(within(dialog).getByLabelText('日時'))
    await user.type(within(dialog).getByLabelText('日時'), '2026-06-27T09:00')
    await user.click(within(dialog).getByRole('button', { name: 'イベントを登録' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    const requestBody = JSON.parse(fetchMock.mock.calls[1][1]?.body as string)
    expect(requestBody).toEqual({
      dog_id: 'dog-1',
      event_type_code: 'toilet',
      occurred_at: new Date('2026-06-27T09:00').toISOString(),
      memo: null,
      detail: {
        type: 'うんち',
        condition: '気になる',
      },
    })
  })

  it('イベント作成フォームで日時が未入力の場合はイベント作成APIを呼ばない', async () => {
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'イベント作成' }))
    const dialog = screen.getByRole('dialog', { name: 'イベント作成' })
    await user.clear(within(dialog).getByLabelText('日時'))
    await user.click(within(dialog).getByRole('button', { name: 'イベントを登録' }))

    expect(await within(dialog).findByText('日時は必須です。')).toBeTruthy()
    expect(fetchMock).toHaveBeenCalledTimes(1)
  })

  it('イベント作成APIのエラーをフォーム内に表示する', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string, init?: RequestInit) => {
      if (url.endsWith('/events') && init?.method === 'POST') {
        return Promise.resolve(jsonResponse({ detail: 'イベント種別が見つかりません' }, 404))
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

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'イベント作成' }))
    const dialog = screen.getByRole('dialog', { name: 'イベント作成' })
    await user.click(within(dialog).getByRole('button', { name: 'イベントを登録' }))

    expect(await within(dialog).findByText('イベント種別が見つかりません')).toBeTruthy()
    expect(fetchMock).toHaveBeenCalledTimes(2)
  })

  it('犬メニューからイベント一覧をクリックすると対象犬のイベントページへ遷移する', async () => {
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
    const router = createRouter({
      history: createMemoryHistory(),
      routes: [
        { path: '/dogs', name: 'dogs', component: DogListView },
        { path: '/dogs/:dogId/events', name: 'dog-events', component: EventListView },
      ],
    })
    await router.push('/dogs')
    await router.isReady()

    const user = userEvent.setup()
    render(DogListView, {
      global: {
        plugins: [router],
      },
    })
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))

    await user.click(await screen.findByRole('button', { name: 'Pochiのメニュー' }))
    await user.click(screen.getByRole('menuitem', { name: 'イベント一覧' }))

    await waitFor(() => {
      expect(router.currentRoute.value.fullPath).toBe('/dogs/dog-1/events?period=week&date=today&dog_name=Pochi')
    })
  })

  it('犬カードに今日のイベント欄を表示し、クリックするとday APIの結果をモーダルに表示する', async () => {
    setLoggedInOwner()
    const today = formatLocalDate(new Date())
    const fetchMock = vi.fn((url: string) => {
      if (url.includes('/events?')) {
        return Promise.resolve(
          jsonResponse({
            events: [
              {
                event_id: 'event-1',
                dog_id: 'dog-1',
                event_type: {
                  event_type_id: 'event-type-1',
                  code: 'walk',
                  display_name: '散歩',
                },
                occurred_at: `${today}T09:15:00+09:00`,
                memo: '朝の散歩',
                detail: {
                  distance_km: 1.5,
                  duration_minutes: 30,
                },
              },
            ],
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
    await screen.findByRole('button', { name: '今日のイベント' })

    await user.click(screen.getByRole('button', { name: '今日のイベント' }))

    const dialog = await screen.findByRole('dialog', { name: 'Pochiの今日のイベント' })
    expect(fetchMock).toHaveBeenNthCalledWith(
      2,
      `http://localhost:8010/events?dog_id=dog-1&period=day&date=${today}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      },
    )
    expect(within(dialog).getByText('散歩')).toBeTruthy()
    expect(
      within(dialog).getByText('散歩').compareDocumentPosition(within(dialog).getByText('09:15')) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()
    expect(within(dialog).getByText('メモ: 朝の散歩')).toBeTruthy()
    expect(within(dialog).getByText('距離: 1.5km / 時間: 30分')).toBeTruthy()
  })

  it('今日のイベントが0件の場合はempty stateを表示する', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string) => {
      if (url.includes('/events?')) {
        return Promise.resolve(jsonResponse({ events: [] }))
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
    await screen.findByRole('button', { name: '今日のイベント' })

    await user.click(screen.getByRole('button', { name: '今日のイベント' }))

    const dialog = await screen.findByRole('dialog', { name: 'Pochiの今日のイベント' })
    expect(await within(dialog).findByText('今日のイベントはありません。')).toBeTruthy()
  })

  it('今日のイベントAPIエラー時はモーダル内にエラーを表示する', async () => {
    setLoggedInOwner()
    const fetchMock = vi.fn((url: string) => {
      if (url.includes('/events?')) {
        return Promise.resolve(jsonResponse({ detail: 'イベント取得に失敗しました' }, 500))
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
    await screen.findByRole('button', { name: '今日のイベント' })

    await user.click(screen.getByRole('button', { name: '今日のイベント' }))

    const dialog = await screen.findByRole('dialog', { name: 'Pochiの今日のイベント' })
    expect(await within(dialog).findByText('イベント取得に失敗しました')).toBeTruthy()
  })
})
