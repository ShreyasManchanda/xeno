'use client'

import { cn } from "@/lib/utils"
import type { CampaignStats } from "@/lib/types"

interface DeliveryFunnelProps {
  stats: CampaignStats
}

const steps: Array<{ key: keyof CampaignStats; label: string }> = [
  { key: 'sent', label: 'Sent' },
  { key: 'delivered', label: 'Delivered' },
  { key: 'read', label: 'Read' },
  { key: 'clicked', label: 'Clicked' },
  { key: 'orders', label: 'Orders' },
]

export function DeliveryFunnel({ stats }: DeliveryFunnelProps) {
  const total = stats.sent || 1

  return (
    <div className="space-y-4">
      {steps.map((step) => {
        const value = stats[step.key] || 0
        const percent = (value / total) * 100
        
        return (
          <div key={step.key}>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-sm text-fg-muted">{step.label}</span>
              <span className="text-sm font-medium text-fg">
                {value.toLocaleString()} ({percent.toFixed(1)}%)
              </span>
            </div>
            <div className="h-2 bg-white/[0.06] rounded-full overflow-hidden">
              <div
                className="h-full bg-accent rounded-full transition-all duration-500"
                style={{ width: `${Math.min(percent, 100)}%` }}
              />
            </div>
          </div>
        )
      })}
    </div>
  )
}
