import { cn } from "@/lib/utils"
import type { CommunicationStatus, CampaignStatus } from "@/lib/types"

type BadgeVariant = CommunicationStatus | CampaignStatus

const badgeStyles: Record<BadgeVariant, string> = {
  queued: "bg-white/[0.06] text-fg-muted",
  sent: "bg-accent/10 text-accent",
  delivered: "bg-accent/10 text-accent",
  read: "bg-accent/15 text-accent",
  clicked: "bg-accent/20 text-accent",
  order_attributed: "bg-accent text-white",
  failed: "bg-red-500/10 text-red-400",
  draft: "bg-white/[0.06] text-fg-muted",
  running: "bg-accent/10 text-accent animate-pulse",
  completed: "bg-success/10 text-success",
}

interface StatusBadgeProps {
  status: BadgeVariant
  className?: string
}

export function StatusBadge({ status, className }: StatusBadgeProps) {
  const displayStatus = status.replace(/_/g, " ")
  
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium",
        badgeStyles[status] || "bg-white/[0.06] text-fg-muted",
        className
      )}
    >
      {displayStatus}
    </span>
  )
}
