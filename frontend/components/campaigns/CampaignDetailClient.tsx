'use client'

import { useState, useEffect, useCallback } from "react"
import { motion, useReducedMotion } from "motion/react"
import { api } from "@/lib/api"
import { useSSE } from "@/lib/sse"
import { notFound } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { StatusBadge } from "@/components/shared/StatusBadge"
import { DeliveryFunnel } from "@/components/campaigns/DeliveryFunnel"
import { VariantBreakdown } from "@/components/campaigns/VariantBreakdown"
import { EventFeed } from "@/components/campaigns/EventFeed"
import type { CampaignDetail, CampaignEvent, SSEEvent } from "@/lib/types"

interface CampaignDetailClientProps {
  id: string
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export function CampaignDetailClient({ id }: CampaignDetailClientProps) {
  const [data, setData] = useState<CampaignDetail | null>(null)
  const [loading, setLoading] = useState(true)
  const [isLive, setIsLive] = useState(false)
  const shouldReduceMotion = useReducedMotion()

  useEffect(() => {
    const fetchData = async () => {
      try {
        const result = await api.campaigns.get(id)
        setData(result)
        setIsLive(result.campaign.status === 'running')
      } catch (error) {
        console.error("Failed to fetch campaign:", error)
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [id])

  const handleSSE = useCallback((event: SSEEvent) => {
    if (event.type === 'stats_update') {
      api.campaigns.get(id).then((fresh) => {
        setData(fresh)
      }).catch((err) => console.error('Failed to refresh campaign:', err))
    }

    if (event.type === 'comm_event' && event.data) {
      const commEvent = event.data as unknown as CampaignEvent
      setData((prev) => {
        if (!prev) return prev
        const recent_events = [commEvent, ...prev.recent_events].slice(0, 20)
        return { ...prev, recent_events }
      })
    }

    if (event.type === 'campaign_complete') {
      setIsLive(false)
      api.campaigns.get(id).then((fresh) => {
        setData(fresh)
      }).catch((err) => console.error('Failed to refresh campaign:', err))
    }
  }, [id])

  const streamUrl = isLive ? `${API_BASE}/api/campaigns/${id}/stream` : null
  useSSE(streamUrl, handleSSE)

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-10 w-64 bg-white/[0.03] rounded-lg" />
        <div className="grid grid-cols-7 gap-4">
          {[...Array(7)].map((_, i) => (
            <div key={i} className="h-24 bg-white/[0.03] rounded-2xl" />
          ))}
        </div>
      </div>
    )
  }

  if (!data) {
    notFound()
  }

  const readPercent = data.stats.sent > 0 ? ((data.stats.read / data.stats.sent) * 100).toFixed(1) : '0'
  const clickPercent = data.stats.read > 0 ? ((data.stats.clicked / data.stats.read) * 100).toFixed(1) : '0'
  const summary = data.campaign.insight_summary

  return (
    <div className="space-y-6 relative">
      <div className="glow-orb-small top-0 right-0 opacity-20" aria-hidden="true" />
      
      <header>
        <Link href="/campaigns" className="text-sm text-fg-muted hover:text-fg flex items-center gap-1 mb-6 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          Back to Campaigns
        </Link>
        <div className="flex items-center gap-3">
          <h1 className="font-display text-heading text-fg">{data.campaign.name}</h1>
          <StatusBadge status={data.campaign.status as any} />
        </div>
        {data.campaign.launched_at && (
          <p className="text-sm text-fg-muted mt-2">
            Launched {new Date(data.campaign.launched_at).toLocaleString()}
          </p>
        )}
      </header>

      <div className="grid grid-cols-7 gap-3">
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0, duration: 0.3 }}
          className="card-glass rounded-2xl p-4 top-highlight"
        >
          <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-1">Sent</p>
          <p className="text-2xl font-semibold text-fg">{data.stats.sent}</p>
        </motion.div>
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05, duration: 0.3 }}
          className="card-glass rounded-2xl p-4 top-highlight"
        >
          <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-1">Delivered</p>
          <p className="text-2xl font-semibold text-fg">{data.stats.delivered}</p>
        </motion.div>
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1, duration: 0.3 }}
          className="card-glass rounded-2xl p-4 top-highlight"
        >
          <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-1">Failed</p>
          <p className="text-2xl font-semibold text-red-400">{data.stats.failed}</p>
        </motion.div>
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15, duration: 0.3 }}
          className="card-glass rounded-2xl p-4 top-highlight relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-accent/[0.06] to-transparent pointer-events-none" />
          <div className="relative">
            <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-1">Read</p>
            <p className="text-2xl font-semibold text-accent">{readPercent}%</p>
          </div>
        </motion.div>
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2, duration: 0.3 }}
          className="card-glass rounded-2xl p-4 top-highlight relative overflow-hidden"
        >
          <div className="absolute inset-0 bg-gradient-to-br from-accent/[0.04] to-transparent pointer-events-none" />
          <div className="relative">
            <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-1">Clicked</p>
            <p className="text-2xl font-semibold text-accent">{clickPercent}%</p>
          </div>
        </motion.div>
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.25, duration: 0.3 }}
          className="card-glass rounded-2xl p-4 top-highlight"
        >
          <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-1">Orders</p>
          <p className="text-2xl font-semibold text-success">{data.stats.orders}</p>
        </motion.div>
        <motion.div
          initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.3 }}
          className="card-glass rounded-2xl p-4 top-highlight"
        >
          <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-1">Revenue</p>
          <p className="text-2xl font-semibold text-fg">₹{data.stats.revenue.toLocaleString()}</p>
        </motion.div>
      </div>

      <div className="grid grid-cols-2 gap-5">
        <div className="space-y-5">
          <div className="card-glass rounded-2xl p-6 top-highlight">
            <h3 className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-4">
              Delivery Funnel
            </h3>
            <DeliveryFunnel stats={data.stats} />
          </div>

          <div className="card-glass rounded-2xl p-6 top-highlight">
            <VariantBreakdown variants={data.variant_breakdown} />
          </div>
        </div>

        <div>
          <EventFeed events={data.recent_events} isLive={isLive} />
        </div>
      </div>

      {data.campaign.status === 'completed' && summary && (
        <div className="card-glass rounded-2xl p-6 top-highlight border border-accent/10">
          <h3 className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-3">
            Campaign Insights
          </h3>
          <p className="text-sm text-fg leading-relaxed">{summary}</p>
        </div>
      )}
    </div>
  )
}
