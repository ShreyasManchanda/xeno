'use client'

import { motion, useReducedMotion } from "motion/react"
import { TrendingUp, Users, Target, Megaphone } from "lucide-react"
import { cn } from "@/lib/utils"
import type { DashboardKPIs } from "@/lib/types"

interface KPICardsProps {
  kpis: DashboardKPIs
}

const kpiConfig = [
  { 
    key: "avg_read_rate" as const, 
    label: "Avg Read Rate", 
    icon: TrendingUp, 
    isHero: true,
    isPercent: true,
  },
  { 
    key: "total_customers" as const, 
    label: "Total Customers", 
    icon: Users, 
    isHero: false,
  },
  { 
    key: "active_segments" as const, 
    label: "Active Segments", 
    icon: Target, 
    isHero: false,
  },
  { 
    key: "campaigns_run" as const, 
    label: "Campaigns Run", 
    icon: Megaphone, 
    isHero: false,
  },
]

export function KPICards({ kpis }: KPICardsProps) {
  const shouldReduceMotion = useReducedMotion()

  const springConfig = { type: "spring", stiffness: 300, damping: 25 }
  const hoverAnimation = shouldReduceMotion ? {} : { y: -2 }

  return (
    <div className="grid grid-cols-4 gap-4">
      {kpiConfig.map((config, index) => {
        const Icon = config.icon
        const value = kpis[config.key]
        const formattedValue = config.isPercent 
          ? `${(value * 100).toFixed(1)}%` 
          : value.toLocaleString()

        if (config.isHero) {
          return (
            <motion.div
              key={config.key}
              initial={shouldReduceMotion ? false : { opacity: 0, y: 24 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              whileHover={hoverAnimation}
              transition-hover={springConfig}
              className="col-span-2 row-span-2 card-glass rounded-2xl p-6 top-highlight relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-br from-accent/5 to-transparent pointer-events-none" />
              <div className="relative">
                <div className="flex items-center gap-2 mb-4">
                  <Icon className="h-5 w-5 text-accent" />
                  <span className="text-sm font-medium uppercase tracking-wider text-fg-muted">
                    {config.label}
                  </span>
                </div>
                <div className="text-display font-semibold text-fg">
                  {formattedValue}
                </div>
                <p className="text-sm text-fg-muted mt-2">
                  Campaign health indicator
                </p>
              </div>
            </motion.div>
          )
        }

        return (
          <motion.div
            key={config.key}
            initial={shouldReduceMotion ? false : { opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: (index + 1) * 0.08, duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
            whileHover={hoverAnimation}
            transition-hover={springConfig}
            className={cn(
              "card-glass rounded-2xl p-5 top-highlight",
              index === 1 && "col-span-1",
              index === 2 && "col-span-1",
              index === 3 && "col-span-2"
            )}
          >
            <div className="flex items-center gap-2 mb-3">
              <Icon className="h-4 w-4 text-fg-muted" />
              <span className="text-xs font-medium uppercase tracking-wider text-fg-muted">
                {config.label}
              </span>
            </div>
            <div className="text-heading font-semibold text-fg">
              {formattedValue}
            </div>
          </motion.div>
        )
      })}
    </div>
  )
}
