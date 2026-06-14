'use client'

import { motion } from "motion/react"
import { cn } from "@/lib/utils"
import type { VariantStats } from "@/lib/types"

interface VariantBreakdownProps {
  variants: VariantStats[]
}

export function VariantBreakdown({ variants }: VariantBreakdownProps) {
  if (!variants || variants.length === 0) {
    return (
      <div className="text-sm text-fg-muted">
        No variant data available
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <h3 className="text-xs font-medium uppercase tracking-wider text-fg-muted">
        Variant Performance
      </h3>
      <div className="space-y-3">
        {variants.map((variant, index) => {
          const readRate = variant.sent > 0 ? ((variant.read / variant.sent) * 100).toFixed(1) : '0'
          const clickRate = variant.read > 0 ? ((variant.clicked / variant.read) * 100).toFixed(1) : '0'
          const targeting = Object.entries(variant.targeting || {})
            .map(([k, v]) => `${k}: ${v}`)
            .join(' • ') || 'All'

          return (
            <motion.div
              key={variant.variant_id}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.05, duration: 0.3 }}
              className="rounded-xl bg-white/[0.02] p-4 top-highlight border border-white/[0.04] hover:border-white/[0.08] transition-colors"
            >
              <div className="flex items-center gap-2 mb-3">
                <span className="rounded-full bg-accent/10 px-2.5 py-0.5 text-xs font-medium text-accent">
                  Variant {variant.variant_id}
                </span>
                <span className="text-xs text-fg-muted">{targeting}</span>
              </div>
              <div className="grid grid-cols-4 gap-4 text-sm">
                <div>
                  <span className="text-xs text-fg-muted block mb-0.5">Sent</span>
                  <p className="font-medium text-fg">{variant.sent}</p>
                </div>
                <div>
                  <span className="text-xs text-fg-muted block mb-0.5">Read</span>
                  <p className="font-medium text-accent">{readRate}%</p>
                </div>
                <div>
                  <span className="text-xs text-fg-muted block mb-0.5">Clicked</span>
                  <p className="font-medium text-fg">{clickRate}%</p>
                </div>
                <div>
                  <span className="text-xs text-fg-muted block mb-0.5">Orders</span>
                  <p className="font-medium text-success">{variant.orders}</p>
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
