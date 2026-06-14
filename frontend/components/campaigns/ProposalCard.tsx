'use client'

import { useState, useEffect } from "react"
import { motion, useReducedMotion } from "motion/react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { FilterChips } from "@/components/segments/FilterChips"
import { ChevronDown, ChevronUp, ArrowLeft, Sparkles } from "lucide-react"
import { normalizeTrendHighlight } from "@/lib/trend-utils"
import type { ProposalData, FilterRules } from "@/lib/types"

interface ProposalCardProps {
  proposal: ProposalData
  onApprove: () => void
  onEdit?: (proposal: ProposalData) => void
  onBack?: () => void
  loading?: boolean
}

export function ProposalCard({ proposal, onApprove, onEdit, onBack, loading }: ProposalCardProps) {
  const [mounted, setMounted] = useState(false)
  const [editing, setEditing] = useState(false)
  const [editProposal, setEditProposal] = useState<ProposalData>(proposal)
  const [showReasoning, setShowReasoning] = useState(false)
  const shouldReduceMotion = useReducedMotion()

  useEffect(() => {
    setEditProposal(proposal)
  }, [proposal])

  useEffect(() => {
    setMounted(true)
  }, [])

  const display = editing ? editProposal : proposal

  const handleFilterChange = (rules: FilterRules) => {
    const updated = { ...editProposal, segment: rules }
    setEditProposal(updated)
    onEdit?.(updated)
  }

  const handleMessageChange = (index: number, message: string) => {
    const variants = [...(editProposal.message_variants || [])]
    variants[index] = { ...variants[index], message }
    const updated = { ...editProposal, message_variants: variants }
    setEditProposal(updated)
    onEdit?.(updated)
  }

  const handleChannelChange = (channel: string) => {
    const updated = { ...editProposal, channel }
    setEditProposal(updated)
    onEdit?.(updated)
  }

  return (
    <motion.div
      initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="card-glass rounded-2xl border-[1.5px] border-white/[0.08] shadow-panel p-8 top-highlight relative overflow-hidden"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-accent/[0.03] to-transparent pointer-events-none" />

      <div className="relative">
        <header className="mb-8">
          <h2 className="font-display text-heading text-fg mb-2">
            {display.segment_name || "Campaign Proposal"}
          </h2>
          <p className="text-sm text-fg-muted">
            Review and edit before launching
          </p>
        </header>

        <div className="space-y-6">
          <section className="rounded-xl bg-white/[0.02] p-5 top-highlight">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-label font-medium uppercase tracking-wider text-fg-muted">
                Segment
              </h3>
              <span className="text-xs px-2 py-1 rounded-full bg-accent/10 text-accent font-medium">
                {display.customer_count || 0} customers
              </span>
            </div>
            <FilterChips
              filterRules={display.segment || { operator: "AND", rules: [] }}
              onChange={handleFilterChange}
              editable={editing}
            />
          </section>

          <section>
            <h3 className="text-label font-medium uppercase tracking-wider text-fg-muted mb-3">
              Channel
            </h3>
            <div className="flex gap-2">
              {['whatsapp', 'sms', 'email'].map((ch) => (
                <button
                  key={ch}
                  onClick={() => editing && handleChannelChange(ch)}
                  disabled={!editing}
                  className={cn(
                    "rounded-full px-5 py-2 text-sm font-medium transition-all duration-150 active:scale-[0.97] capitalize",
                    display.channel === ch
                      ? "bg-accent text-white shadow-glow"
                      : "bg-white/[0.03] text-fg-muted hover:bg-white/[0.06] hover:text-fg border border-white/[0.06]",
                    !editing && "cursor-default"
                  )}
                >
                  {ch}
                </button>
              ))}
            </div>
            {display.channel_reasoning && (
              <p className="text-xs text-fg-muted mt-2">{display.channel_reasoning}</p>
            )}
          </section>

          <section>
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="h-4 w-4 text-accent" />
              <h3 className="text-label font-medium uppercase tracking-wider text-fg-muted">
                Message Variants
              </h3>
            </div>
            <div className="space-y-3">
              {display.message_variants?.map((variant, index) => (
                <motion.div
                  key={variant.id}
                  initial={shouldReduceMotion ? false : { opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05, duration: 0.3 }}
                  whileHover={shouldReduceMotion ? {} : { y: -1 }}
                  className="rounded-xl bg-white/[0.02] p-4 top-highlight border border-white/[0.04] hover:border-white/[0.08] transition-colors"
                >
                  <div className="flex items-center gap-2 mb-3">
                    <span className="rounded-full bg-accent/10 px-2.5 py-0.5 text-xs font-medium text-accent">
                      Variant {variant.id}
                    </span>
                    <span className="text-caption text-fg-muted">
                      {Object.entries(variant.targets || {}).map(([k, v]) => `${k}: ${v}`).join(' • ') || 'All customers'}
                    </span>
                  </div>
                  {editing ? (
                    <Textarea
                      value={variant.message}
                      onChange={(e) => handleMessageChange(index, e.target.value)}
                      className="min-h-[100px]"
                    />
                  ) : (
                    <p className="text-body text-fg leading-relaxed">{variant.message}</p>
                  )}
                </motion.div>
              ))}
            </div>
          </section>

          {display.reasoning && (
            <section>
              <button
                onClick={() => setShowReasoning(!showReasoning)}
                className="flex items-center gap-2 text-label font-medium text-fg-muted hover:text-fg transition-colors"
              >
                Why this approach
                {showReasoning ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
              </button>
              {showReasoning && (
                <motion.p
                  initial={shouldReduceMotion ? false : { opacity: 0 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-3 text-body text-fg-muted p-4 rounded-xl bg-white/[0.02]"
                >
                  {display.reasoning}
                </motion.p>
              )}
            </section>
          )}

          {display.trend_highlights && display.trend_highlights.length > 0 && (
            <section className="rounded-xl bg-accent/[0.04] p-5 top-highlight border border-accent/10">
              <h3 className="text-label font-medium uppercase tracking-wider text-fg-muted mb-3">
                Trend Highlights
              </h3>
              <ul className="space-y-2">
                {display.trend_highlights.map((highlight, index) => {
                  const text = normalizeTrendHighlight(highlight)
                  if (!text) return null
                  return (
                  <li key={index} className="text-body text-fg flex gap-2">
                    <span className="text-accent shrink-0">•</span>
                    <span>{text}</span>
                  </li>
                  )
                })}
              </ul>
            </section>
          )}

          <footer className="flex items-center gap-3 pt-6 border-t border-white/[0.06]">
            <Button variant="primary" onClick={onApprove} disabled={loading}>
              {loading ? 'Launching...' : 'Approve & Launch'}
            </Button>
            <Button variant="secondary" onClick={() => setEditing(!editing)}>
              {editing ? 'Done Editing' : 'Edit'}
            </Button>
            {onBack && (
              <Button variant="ghost" onClick={onBack}>
                <ArrowLeft className="h-4 w-4 mr-1" />
                Start Over
              </Button>
            )}
          </footer>
        </div>
      </div>
    </motion.div>
  )
}
