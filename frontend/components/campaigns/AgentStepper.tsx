'use client'

import { useMemo } from "react"
import { motion, useReducedMotion } from "motion/react"
import { cn } from "@/lib/utils"
import { Check, Loader2 } from "lucide-react"
import type { AgentName, SSEEvent } from "@/lib/types"

interface AgentStep {
  name: AgentName
  label: string
  status: 'pending' | 'running' | 'complete' | 'error'
  message?: string
  streamText?: string
  completeDetail?: string
}

interface AgentStepperProps {
  events: SSEEvent[]
}

const agentConfig: Record<AgentName, { label: string }> = {
  analyst: { label: "Audience Analyst" },
  strategist: { label: "Campaign Strategist" },
  executor: { label: "Preparing Variants" },
}

function buildSteps(events: SSEEvent[]): AgentStep[] {
  const steps: AgentStep[] = [
    { name: 'analyst', label: agentConfig.analyst.label, status: 'pending' },
    { name: 'strategist', label: agentConfig.strategist.label, status: 'pending' },
    { name: 'executor', label: agentConfig.executor.label, status: 'pending' },
  ]

  const streamByAgent: Record<string, string> = {}

  for (const event of events) {
    if (event.type === 'agent_start' && event.agent) {
      const step = steps.find(s => s.name === event.agent)
      if (step) {
        step.status = 'running'
        step.message = event.message
        streamByAgent[event.agent] = ''
        step.streamText = ''
      }
    }

    if (event.type === 'agent_stream' && event.agent && event.delta) {
      streamByAgent[event.agent] = (streamByAgent[event.agent] || '') + event.delta
      const step = steps.find(s => s.name === event.agent)
      if (step) {
        step.streamText = streamByAgent[event.agent]
      }
    }

    if (event.type === 'agent_progress' && event.agent) {
      const step = steps.find(s => s.name === event.agent)
      if (step) {
        step.message = event.message
      }
    }

    if (event.type === 'agent_complete' && event.agent) {
      const step = steps.find(s => s.name === event.agent)
      if (step) {
        step.status = 'complete'
        if (event.agent === 'analyst' && event.data?.customer_count != null) {
          step.completeDetail = `Found ${event.data.customer_count} matching customers`
        } else if (event.agent === 'strategist' && event.data?.variant_count != null) {
          step.completeDetail = `${event.data.variant_count} message variants ready`
        } else if (event.agent === 'executor' && event.data?.assignments_count != null) {
          step.completeDetail = `${event.data.assignments_count} messages personalized`
        }
      }
    }

    if (event.type === 'error' && event.agent) {
      const step = steps.find(s => s.name === event.agent)
      if (step) {
        step.status = 'error'
        step.message = event.message
      }
    }
  }

  return steps
}

export function AgentStepper({ events }: AgentStepperProps) {
  const shouldReduceMotion = useReducedMotion()
  const steps = useMemo(() => buildSteps(events), [events])
  const completedCount = steps.filter(s => s.status === 'complete').length
  const progress = (completedCount / steps.length) * 100

  return (
    <motion.div
      initial={shouldReduceMotion ? false : { opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
      className="card-glass rounded-2xl p-6 top-highlight"
    >
      <div className="mb-6">
        <div className="flex items-center justify-between text-xs text-fg-muted mb-2">
          <span className="uppercase tracking-wider font-medium">Agent Progress</span>
          <span>{completedCount}/{steps.length}</span>
        </div>
        <div className="h-1 bg-white/[0.06] rounded-full overflow-hidden">
          <motion.div
            className="h-full bg-accent rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      </div>

      <div className="relative">
        <div className="absolute left-[15px] top-8 bottom-8 w-px bg-white/[0.06]" />

        <ul className="space-y-6">
          {steps.map((step, index) => (
            <motion.li
              key={step.name}
              initial={shouldReduceMotion ? false : { opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: index * 0.1, duration: 0.3 }}
              className="flex items-start gap-4 relative"
            >
              <div className="relative z-10">
                {step.status === 'complete' ? (
                  <div className="w-8 h-8 rounded-lg bg-accent/20 border border-accent/30 flex items-center justify-center">
                    <Check className="h-4 w-4 text-accent" />
                  </div>
                ) : step.status === 'running' ? (
                  <div className="w-8 h-8 rounded-lg bg-accent/10 border border-accent/20 flex items-center justify-center animate-pulse-glow">
                    <Loader2 className="h-4 w-4 text-accent animate-spin" />
                  </div>
                ) : step.status === 'error' ? (
                  <div className="w-8 h-8 rounded-lg bg-red-500/10 border border-red-500/20 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-red-500" />
                  </div>
                ) : (
                  <div className="w-8 h-8 rounded-lg bg-white/[0.03] border border-white/[0.06] flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-fg-muted/30" />
                  </div>
                )}
              </div>

              <div className="flex-1 pt-1 min-w-0">
                <p className={cn(
                  "text-[15px] font-medium",
                  step.status === 'pending' ? "text-fg-muted" : "text-fg"
                )}>
                  {step.label}
                </p>
                {step.status === 'running' && step.message && (
                  <p className="text-xs text-fg-muted mt-1">{step.message}</p>
                )}
                {step.status === 'running' && step.streamText && (
                  <div className="mt-2 rounded-lg bg-white/[0.02] border border-white/[0.04] p-3 max-h-24 overflow-y-auto">
                    <p className="text-xs text-fg-muted font-mono whitespace-pre-wrap break-all leading-relaxed">
                      {step.streamText.slice(-400)}
                      <span className="inline-block w-1.5 h-3 bg-accent/70 ml-0.5 animate-pulse align-middle" />
                    </p>
                  </div>
                )}
                {step.status === 'complete' && step.completeDetail && (
                  <p className="text-xs text-accent mt-1">{step.completeDetail}</p>
                )}
                {step.status === 'complete' && !step.completeDetail && (
                  <p className="text-xs text-accent mt-1">Complete</p>
                )}
                {step.status === 'error' && step.message && (
                  <p className="text-xs text-red-400 mt-1">{step.message}</p>
                )}
              </div>
            </motion.li>
          ))}
        </ul>
      </div>
    </motion.div>
  )
}
