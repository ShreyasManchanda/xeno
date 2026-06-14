import type {
  DashboardStats,
  PaginatedCustomers,
  CustomerDetail,
  Segment,
  SegmentPreview,
  SegmentDetail,
  Campaign,
  CampaignDetail,
  FilterRules,
  MessageVariant,
} from './types'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

async function fetchJSON<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
  })
  if (!res.ok) {
    throw new Error(`API Error: ${res.status} ${res.statusText}`)
  }
  return res.json()
}

export const api = {
  dashboard: {
    getStats: () => fetchJSON<DashboardStats>('/api/dashboard/stats'),
  },

  customers: {
    list: (params: {
      search?: string
      city?: string
      age_group?: string
      page?: number
      limit?: number
    }) => {
      const searchParams = new URLSearchParams()
      if (params.search) searchParams.set('search', params.search)
      if (params.city) searchParams.set('city', params.city)
      if (params.age_group) searchParams.set('age_group', params.age_group)
      if (params.page) searchParams.set('page', String(params.page))
      if (params.limit) searchParams.set('limit', String(params.limit))
      return fetchJSON<PaginatedCustomers>(`/api/customers?${searchParams.toString()}`)
    },
    get: (id: string) => fetchJSON<CustomerDetail>(`/api/customers/${id}`),
  },

  segments: {
    list: () => fetchJSON<Segment[]>('/api/segments'),
    get: (id: string, page = 1, limit = 20) =>
      fetchJSON<SegmentDetail>(`/api/segments/${id}?page=${page}&limit=${limit}`),
    create: (data: {
      name: string
      nl_query?: string
      filter_rules: FilterRules
      created_by?: string
    }) =>
      fetchJSON<Segment>('/api/segments', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    update: (id: string, data: { filter_rules: FilterRules }) =>
      fetchJSON<Segment>(`/api/segments/${id}`, {
        method: 'PUT',
        body: JSON.stringify(data),
      }),
    delete: (id: string) =>
      fetchJSON<{ deleted: boolean }>(`/api/segments/${id}`, { method: 'DELETE' }),
    preview: (nlQuery: string) =>
      fetchJSON<SegmentPreview>('/api/segments/preview', {
        method: 'POST',
        body: JSON.stringify({ nl_query: nlQuery }),
      }),
  },

  campaigns: {
    list: (status?: string) => {
      const params = status ? `?status=${status}` : ''
      return fetchJSON<Campaign[]>(`/api/campaigns${params}`)
    },
    get: (id: string) => fetchJSON<CampaignDetail>(`/api/campaigns/${id}`),
    create: (data: {
      name: string
      goal: string
      segment_id: string
      channel: string
      message_variants: MessageVariant[]
      ai_reasoning?: string
      trend_context?: string
    }) =>
      fetchJSON<Campaign>('/api/campaigns', {
        method: 'POST',
        body: JSON.stringify(data),
      }),
    launch: (id: string) =>
      fetchJSON<{ launched: boolean; total_queued: number }>(
        `/api/campaigns/${id}/launch`,
        { method: 'POST' }
      ),
    delete: (id: string) =>
      fetchJSON<{ deleted: boolean }>(`/api/campaigns/${id}`, { method: 'DELETE' }),
    startCopilot: (goal: string, sessionId: string) =>
      fetchJSON<{ session_id: string }>('/api/campaigns/copilot', {
        method: 'POST',
        body: JSON.stringify({ goal, session_id: sessionId }),
      }),
  },
}
