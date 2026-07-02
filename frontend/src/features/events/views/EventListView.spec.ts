import { render, screen, waitFor, within } from '@testing-library/vue'
import userEvent from '@testing-library/user-event'
import { createMemoryHistory, createRouter } from 'vue-router'
import { describe, expect, it, vi } from 'vitest'
import EventListView from './EventListView.vue'

function jsonResponse(payload: unknown, status = 200): Response {
  return new Response(JSON.stringify(payload), {
    status,
    headers: {
      'Content-Type': 'application/json',
    },
  })
}

function formatLocalDate(date: Date): string {
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

async function renderEventList(initialPath = '/dogs/dog-1/events?date=today') {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [{ path: '/dogs/:dogId/events', name: 'dog-events', component: EventListView }],
  })
  await router.push(initialPath)
  await router.isReady()

  return render(EventListView, {
    global: {
      plugins: [router],
    },
  })
}

describe('EventListView', () => {
  it('犬名つきで遷移した場合は犬IDを表示せず犬名のイベント見出しを表示する', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ events: [] }))
    vi.stubGlobal('fetch', fetchMock)

    await renderEventList('/dogs/dog-1/events?period=month&date=2026-07-03&dog_name=Pochi')

    expect(await screen.findByRole('heading', { name: 'Pochiのイベント' })).toBeTruthy()
    expect(screen.queryByText('対象犬ID: dog-1')).toBeNull()
  })

  it('初期表示でweekと今日の日付を指定してイベントAPIを呼ぶ', async () => {
    const today = formatLocalDate(new Date())
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ events: [] }))
    vi.stubGlobal('fetch', fetchMock)

    await renderEventList()

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))
    expect(fetchMock).toHaveBeenCalledWith(
      `http://localhost:8010/events?dog_id=dog-1&period=week&date=${today}`,
      {
        headers: {
          'Content-Type': 'application/json',
        },
      },
    )
  })

  it('月/週タブ切り替えでAPI queryのperiodが変わる', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ events: [] }))
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    await renderEventList('/dogs/dog-1/events?period=month&date=2026-07-03')
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))

    await user.click(screen.getByRole('button', { name: '週' }))

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    expect(fetchMock).toHaveBeenLastCalledWith(
      'http://localhost:8010/events?dog_id=dog-1&period=week&date=2026-07-03',
      {
        headers: {
          'Content-Type': 'application/json',
        },
      },
    )
  })

  it('前月/翌月と前週/翌週ボタンでdateが変わる', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ events: [] }))
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    await renderEventList('/dogs/dog-1/events?period=month&date=2026-07-03')
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))

    await user.click(screen.getByRole('button', { name: '前月' }))
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    expect(fetchMock.mock.calls[1][0]).toBe(
      'http://localhost:8010/events?dog_id=dog-1&period=month&date=2026-06-03',
    )

    await user.click(screen.getByRole('button', { name: '翌月' }))
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
    expect(fetchMock.mock.calls[2][0]).toBe(
      'http://localhost:8010/events?dog_id=dog-1&period=month&date=2026-07-03',
    )

    await user.click(screen.getByRole('button', { name: '週' }))
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(4))
    await user.click(screen.getByRole('button', { name: '前週' }))
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(5))
    expect(fetchMock.mock.calls[4][0]).toBe(
      'http://localhost:8010/events?dog_id=dog-1&period=week&date=2026-06-26',
    )

    await user.click(screen.getByRole('button', { name: '翌週' }))
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(6))
    expect(fetchMock.mock.calls[5][0]).toBe(
      'http://localhost:8010/events?dog_id=dog-1&period=week&date=2026-07-03',
    )
  })

  it('カテゴリfilterでevent_type_codeが付与される', async () => {
    const fetchMock = vi.fn().mockResolvedValue(jsonResponse({ events: [] }))
    vi.stubGlobal('fetch', fetchMock)

    const user = userEvent.setup()
    await renderEventList('/dogs/dog-1/events?period=month&date=2026-07-03')
    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(1))

    await user.selectOptions(screen.getByLabelText('カテゴリ'), 'walk')

    await waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(2))
    expect(fetchMock).toHaveBeenLastCalledWith(
      'http://localhost:8010/events?dog_id=dog-1&period=month&date=2026-07-03&event_type_code=walk',
      {
        headers: {
          'Content-Type': 'application/json',
        },
      },
    )
  })

  it('日付ごとのグループとイベント詳細を表示する', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
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
            occurred_at: '2026-07-03T09:15:00+09:00',
            memo: '朝',
            detail: {
              distance_km: 1.5,
              duration_minutes: 30,
            },
          },
          {
            event_id: 'event-2',
            dog_id: 'dog-1',
            event_type: {
              event_type_id: 'event-type-2',
              code: 'food',
              display_name: 'ご飯',
            },
            occurred_at: '2026-07-04T08:00:00+09:00',
            memo: null,
            detail: {
              menu: 'ドライフード',
              amount_grams: 80,
            },
          },
        ],
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await renderEventList('/dogs/dog-1/events?period=month&date=2026-07-03')

    const firstGroup = await screen.findByRole('heading', { name: /2026年7月3日/ })
    const secondGroup = await screen.findByRole('heading', { name: /2026年7月4日/ })
    expect(firstGroup).toBeTruthy()
    expect(secondGroup).toBeTruthy()
    expect(screen.getAllByText('散歩')).toHaveLength(2)
    expect(
      screen.getAllByText('散歩')[1].compareDocumentPosition(screen.getByText('09:15')) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()
    expect(screen.getByText('メモ: 朝')).toBeTruthy()
    expect(screen.getByText('距離: 1.5km / 時間: 30分')).toBeTruthy()
    expect(screen.getAllByText('ご飯')).toHaveLength(2)
    expect(screen.getByText('メニュー: ドライフード / 量: 80g')).toBeTruthy()
  })

  it('週表示では月曜始まりの7日分を表示する', async () => {
    const fetchMock = vi.fn().mockResolvedValue(
      jsonResponse({
        events: [
          {
            event_id: 'event-1',
            dog_id: 'dog-1',
            event_type: {
              event_type_id: 'event-type-3',
              code: 'toilet',
              display_name: 'トイレ',
            },
            occurred_at: '2026-06-29T07:00:00+09:00',
            memo: null,
            detail: {
              type: 'おしっこ',
              condition: 'いつも通り',
            },
          },
        ],
      }),
    )
    vi.stubGlobal('fetch', fetchMock)

    await renderEventList('/dogs/dog-1/events?period=week&date=2026-07-03')

    const mondayGroup = await screen.findByRole('heading', { name: /2026年6月29日/ })
    expect(mondayGroup).toBeTruthy()
    expect(screen.getByRole('heading', { name: /2026年7月5日/ })).toBeTruthy()
    expect(screen.getAllByText('トイレ')).toHaveLength(2)
    expect(screen.getByText('種類: おしっこ / 状態: いつも通り')).toBeTruthy()
    expect(within(mondayGroup.closest('section') as HTMLElement).queryByText('イベントはありません。')).toBeNull()
  })
})
