'use client'

import { useState, useRef, useCallback, useMemo } from "react"
import { NLCreator } from "@/components/segments/NLCreator"
import { AgentStepper } from "@/components/campaigns/AgentStepper"
import { ProposalCard } from "@/components/campaigns/ProposalCard"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import { useSSE } from "@/lib/sse"
import { normalizeTrendHighlight } from "@/lib/trend-utils"
import type { SSEEvent, ProposalData, FilterRules } from "@/lib/types"

function normalizeProposal(raw: Record<string, unknown>): ProposalData {
  const segment = (raw.segment as FilterRules) || { operator: "AND", rules: [] }
  const rawHighlights = (raw.trend_highlights as string[] | undefined) || []
  const trend_highlights = rawHighlights
    .map((h) => normalizeTrendHighlight(h))
    .filter(Boolean)

  return {
    segment_name: (raw.segment_name as string) || "Campaign segment",
    segment,
    customer_count: (raw.customer_count as number) || 0,
    channel: (raw.channel as string) || "whatsapp",
    message_variants: (raw.message_variants as ProposalData["message_variants"]) || [],
    reasoning: (raw.reasoning as string) || "",
    channel_reasoning: raw.channel_reasoning as string | undefined,
    message_style: raw.message_style as string | undefined,
    trend_highlights,
    trend_context: raw.trend_context as string | undefined,
    predicted_open_rate: raw.predicted_open_rate as string | undefined,
    sample_customers: raw.sample_customers as ProposalData["sample_customers"],
  }
}

interface NewCampaignClientProps {
  prefillGoal?: string
}

export function NewCampaignClient({ prefillGoal = "" }: NewCampaignClientProps) {
  const router = useRouter()
  const [sessionId] = useState(() => crypto.randomUUID())
  const [events, setEvents] = useState<SSEEvent[]>([])
  const [proposal, setProposal] = useState<ProposalData | null>(null)
  const [goal, setGoal] = useState("")
  const [loading, setLoading] = useState(false)
  const [launching, setLaunching] = useState(false)
  const [pendingGoal, setPendingGoal] = useState<string | null>(null)
  const copilotStarted = useRef(false)

  const streamUrl = useMemo(() => {
    if (!pendingGoal) return null
    const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
    return `${base}/api/campaigns/copilot/stream/${sessionId}`
  }, [sessionId, pendingGoal])

  const handleSSEEvent = useCallback((data: SSEEvent) => {
    setEvents((prev) => [...prev, data])

    if (data.type === 'proposal_ready' && data.data) {
      setProposal(normalizeProposal(data.data as Record<string, unknown>))
      setLoading(false)
      setPendingGoal(null)
    }

    if (data.type === 'fatal_error') {
      setLoading(false)
      setPendingGoal(null)
    }
  }, [])

  const handleSSEOpen = useCallback(async () => {
    if (!pendingGoal || copilotStarted.current) return
    copilotStarted.current = true

    try {
      await api.campaigns.startCopilot(pendingGoal, sessionId)
    } catch (error) {
      console.error("Failed to start copilot:", error)
      setLoading(false)
      setPendingGoal(null)
      copilotStarted.current = false
    }
  }, [pendingGoal, sessionId])

  const { close: closeSSE } = useSSE(streamUrl, handleSSEEvent, { onOpen: handleSSEOpen })

  const handleGoal = (submittedGoal: string) => {
    setGoal(submittedGoal)
    setLoading(true)
    setEvents([])
    setProposal(null)
    copilotStarted.current = false
    setPendingGoal(submittedGoal)
  }

  const handleEdit = (updatedProposal: ProposalData) => {
    setProposal(updatedProposal)
  }

  const handleApprove = async () => {
    if (!proposal) return

    setLaunching(true)
    try {
      const segment = await api.segments.create({
        name: proposal.segment_name || "Campaign segment",
        nl_query: goal,
        filter_rules: proposal.segment || { operator: "AND", rules: [] },
        created_by: "ai",
      })

      const campaign = await api.campaigns.create({
        name: proposal.segment_name || "New Campaign",
        goal,
        segment_id: segment.id,
        channel: proposal.channel,
        message_variants: proposal.message_variants,
        ai_reasoning: proposal.reasoning,
        trend_context: proposal.trend_context,
      })

      await api.campaigns.launch(campaign.id)
      closeSSE()
      router.push(`/campaigns/${campaign.id}`)
    } catch (error) {
      console.error("Failed to launch campaign:", error)
    } finally {
      setLaunching(false)
    }
  }

  const handleBack = () => {
    setProposal(null)
    setLoading(false)
    setPendingGoal(null)
    copilotStarted.current = false
    closeSSE()
  }

  return (
    <div className="space-y-8 max-w-3xl relative">
      <div className="glow-orb-small top-0 right-0 opacity-30" aria-hidden="true" />

      <header>
        <Link
          href="/campaigns"
          className="text-sm text-fg-muted hover:text-fg flex items-center gap-1 mb-6 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to Campaigns
        </Link>
        <h1 className="font-display text-heading text-fg">New Campaign</h1>
      </header>

      {!proposal && (
        <section className="card-glass rounded-2xl p-6 top-highlight relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-b from-accent/[0.03] to-transparent pointer-events-none" />
          <div className="relative">
            <h3 className="text-label font-medium uppercase tracking-wider text-fg-muted mb-4">
              What&apos;s your campaign goal?
            </h3>
            <NLCreator
              placeholder="e.g., Win back customers who haven't ordered in 90 days with a festive offer"
              initialValue={prefillGoal}
              onSubmit={handleGoal}
              loading={loading}
            />
          </div>
        </section>
      )}

      {loading && events.length > 0 && (
        <AgentStepper events={events} />
      )}

      {proposal && (
        <ProposalCard
          proposal={proposal}
          onApprove={handleApprove}
          onEdit={handleEdit}
          onBack={handleBack}
          loading={launching}
        />
      )}
    </div>
  )
}
