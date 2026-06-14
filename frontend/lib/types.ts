export interface Customer {
  id: string
  name: string
  email: string | null
  phone: string | null
  city: string | null
  region: string | null
  gender: string | null
  age_group: string | null
  signup_date: string | null
  total_spent: number
  order_count: number
  last_order_date: string | null
  preferred_channel: string
  preferred_categories: string[] | null
  created_at: string
}

export interface OrderItem {
  name: string
  category: string
  price: number
  qty: number
}

export interface Order {
  id: string
  amount: number
  items: OrderItem[]
  order_date: string | null
  season: string | null
  category_tags: string[] | null
}

export interface CampaignHistory {
  campaign_id: string
  campaign_name: string
  channel: string
  status: string
  sent_at: string | null
  variant_id: string
}

export interface CustomerDetail {
  customer: Customer
  orders: Order[]
  campaign_history: CampaignHistory[]
}

export interface PaginatedCustomers {
  customers: Customer[]
  total: number
  page: number
  limit: number
}

export interface FilterRule {
  field: string
  op: string
  value: string | number | string[]
}

export interface FilterRules {
  operator: string
  rules: FilterRule[]
}

export interface Segment {
  id: string
  name: string | null
  nl_query: string | null
  filter_rules: FilterRules | null
  customer_count: number | null
  created_by: string | null
  created_at: string
}

export interface SegmentPreview {
  filter_rules: FilterRules
  customer_count: number
  reasoning: string
  sample_customers: Customer[]
}

export interface SegmentPerformance {
  campaigns_run: number
  avg_read_rate: number
  avg_click_rate: number
  avg_order_rate: number
}

export interface SegmentDetail {
  segment: Segment
  customers: Array<{
    id: string
    name: string
    email: string | null
    city: string | null
    total_spent: number
  }>
  performance: SegmentPerformance
}

export interface MessageVariant {
  id: string
  targets: Record<string, string>
  message: string
}

export interface Campaign {
  id: string
  name: string | null
  goal: string | null
  segment_id: string | null
  channel: string | null
  status: string
  message_variants: MessageVariant[] | null
  ai_reasoning: string | null
  trend_context: string | null
  insight_summary: string | null
  launched_at: string | null
  completed_at: string | null
  created_at: string
}

export interface CampaignStats {
  sent: number
  delivered: number
  failed: number
  read: number
  clicked: number
  orders: number
  revenue: number
}

export interface VariantStats {
  variant_id: string
  targeting: Record<string, string>
  sent: number
  read: number
  clicked: number
  orders: number
}

export interface CampaignEvent {
  customer_name: string
  event: string
  variant_id: string
  timestamp: string | null
  revenue?: number
}

export interface CampaignDetail {
  campaign: Campaign
  stats: CampaignStats
  variant_breakdown: VariantStats[]
  recent_events: CampaignEvent[]
}

export interface DashboardKPIs {
  total_customers: number
  active_segments: number
  campaigns_run: number
  avg_read_rate: number
}

export interface Nudge {
  title: string
  body: string
  cta: string
  segment_id: string | null
  prefill_goal?: string | null
}

export interface DashboardStats {
  kpis: DashboardKPIs
  nudges: Nudge[]
}

export type AgentName = 'analyst' | 'strategist' | 'executor'

export type SSEEventType = 
  | 'agent_start'
  | 'agent_complete'
  | 'agent_stream'
  | 'agent_progress'
  | 'proposal_ready'
  | 'error'
  | 'fatal_error'
  | 'stats_update'
  | 'comm_event'
  | 'campaign_complete'

export interface SSEEvent {
  type: SSEEventType
  agent?: AgentName
  message?: string
  delta?: string
  data?: Record<string, unknown>
}

export interface ProposalData {
  segment_name: string
  segment: FilterRules
  customer_count: number
  channel: string
  message_variants: MessageVariant[]
  reasoning: string
  channel_reasoning?: string
  message_style?: string
  trend_highlights?: string[]
  trend_context?: string
  predicted_open_rate?: string
  sample_customers?: Array<{
    id: string
    name: string
    city?: string
    total_spent?: number
    age_group?: string
    region?: string
  }>
}

export type CommunicationStatus = 
  | 'queued'
  | 'sent'
  | 'delivered'
  | 'read'
  | 'clicked'
  | 'order_attributed'
  | 'failed'

export type CampaignStatus = 'draft' | 'running' | 'completed' | 'failed'
