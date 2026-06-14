'use client'

import { motion, useReducedMotion } from "motion/react"
import { Sparkles } from "lucide-react"
import Link from "next/link"
import { cn } from "@/lib/utils"
import type { Nudge } from "@/lib/types"

interface NudgeCardProps {
  nudge: Nudge
  index: number
}

function getNudgeHref(nudge: Nudge): string {
  const goal = nudge.prefill_goal
    ? `?goal=${encodeURIComponent(nudge.prefill_goal)}`
    : ""

  if (nudge.cta === "Launch Campaign") {
    return `/campaigns/new${goal}`
  }
  if (nudge.segment_id && nudge.cta === "View Segment") {
    return `/segments/${nudge.segment_id}`
  }
  return `/segments/new${goal}`
}

export function NudgeCard({ nudge, index }: NudgeCardProps) {
  const shouldReduceMotion = useReducedMotion()
  const isHero = index === 0
  const href = getNudgeHref(nudge)

  const hoverAnimation = shouldReduceMotion ? {} : { y: -2 }

  return (
    <Link href={href} className="block group">
      <motion.div
        initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 + index * 0.08, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
        whileHover={hoverAnimation}
        className={cn(
          "rounded-2xl card-glass top-highlight relative overflow-hidden cursor-pointer",
          "transition-colors group-hover:border-white/[0.12]",
          isHero ? "p-6" : "p-4"
        )}
      >
        <div className={cn(
          "absolute inset-0 pointer-events-none",
          isHero && "bg-gradient-to-br from-accent/8 to-transparent"
        )} />

        <div className="relative">
          <div className="flex items-center gap-2 mb-3">
            <Sparkles className={cn("h-4 w-4 text-accent", isHero && "h-5 w-5")} />
            <span className="text-[11px] font-medium uppercase tracking-wider text-accent">
              AI Suggestion
            </span>
          </div>

          <h4 className={cn(
            "font-semibold text-fg mb-2",
            isHero ? "text-lg" : "text-[15px]"
          )}>
            {nudge.title}
          </h4>

          <p className={cn(
            "text-fg-muted line-clamp-2",
            isHero ? "text-sm mb-5" : "text-[13px] mb-3"
          )}>
            {nudge.body}
          </p>

          <span className={cn(
            "font-medium text-accent group-hover:text-accent-dim transition-colors",
            isHero ? "text-sm" : "text-[13px]"
          )}>
            {nudge.cta} →
          </span>
        </div>
      </motion.div>
    </Link>
  )
}
