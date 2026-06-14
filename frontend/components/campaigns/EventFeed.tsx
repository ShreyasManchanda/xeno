'use client'

import { useState, useEffect, useRef } from "react"
import { motion, AnimatePresence } from "motion/react"
import { cn } from "@/lib/utils"
import { StatusBadge } from "@/components/shared/StatusBadge"
import type { CampaignEvent } from "@/lib/types"

interface EventFeedProps {
  events: CampaignEvent[]
  isLive?: boolean
}

interface EventWithFlag extends CampaignEvent {
  isNew?: boolean
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map(n => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

export function EventFeed({ events, isLive }: EventFeedProps) {
  const [eventsWithFlags, setEventsWithFlags] = useState<EventWithFlag[]>([])
  const prevLengthRef = useRef(0)

  useEffect(() => {
    const prevLength = prevLengthRef.current
    const newLength = events.length

    if (newLength > prevLength) {
      const newEvents = events.slice(prevLength).map(e => ({ ...e, isNew: true }))
      const existingEvents = events.slice(0, prevLength).map(e => ({ ...e, isNew: false }))
      const allEvents = [...existingEvents, ...newEvents]
      setEventsWithFlags(allEvents)

      setTimeout(() => {
        setEventsWithFlags(prev => prev.map(e => ({ ...e, isNew: false })))
      }, 600)
    } else if (newLength < prevLength) {
      setEventsWithFlags(events.map(e => ({ ...e, isNew: false })))
    }

    prevLengthRef.current = newLength
  }, [events])

  return (
    <div className="card-glass rounded-2xl overflow-hidden top-highlight flex flex-col h-full">
      <div className="flex items-center justify-between px-5 py-3 border-b border-white/[0.06]">
        <h3 className="text-xs font-medium uppercase tracking-wider text-fg-muted">Delivery Events</h3>
        {isLive && (
          <div className="flex items-center gap-2">
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-accent opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-accent"></span>
            </span>
            <span className="text-xs text-accent font-medium">Live</span>
          </div>
        )}
      </div>
      <div className="flex-1 overflow-y-auto max-h-[400px]">
        {eventsWithFlags.length === 0 ? (
          <div className="px-5 py-12 text-center">
            <p className="text-sm text-fg-muted">Waiting for delivery events...</p>
          </div>
        ) : (
          <ul className="divide-y divide-white/[0.04]">
            <AnimatePresence mode="popLayout">
              {eventsWithFlags.map((event, index) => (
                <motion.li
                  key={`${event.customer_name}-${index}-${event.timestamp}`}
                  layout
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.2 }}
                  className={cn(
                    "flex items-center gap-3 px-5 py-3 transition-colors",
                    "hover:bg-white/[0.02]"
                  )}
                >
                  <div className="h-8 w-8 rounded-lg bg-accent/10 flex items-center justify-center text-xs font-medium text-accent">
                    {getInitials(event.customer_name)}
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-fg truncate">
                      {event.customer_name}
                    </p>
                  </div>
                  <StatusBadge status={event.event as any} />
                  {event.revenue && (
                    <span className="text-xs font-medium text-accent">
                      ₹{event.revenue.toLocaleString()}
                    </span>
                  )}
                  <span className="text-xs text-fg-muted tabular-nums">
                    {event.timestamp ? new Date(event.timestamp).toLocaleTimeString() : ''}
                  </span>
                </motion.li>
              ))}
            </AnimatePresence>
          </ul>
        )}
      </div>
    </div>
  )
}
