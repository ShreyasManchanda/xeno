'use client'

import { useState, useEffect } from "react"
import { motion } from "motion/react"
import { ArrowRight, Loader2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { cn } from "@/lib/utils"

interface NLCreatorProps {
  placeholder: string
  initialValue?: string
  onSubmit: (query: string) => void
  loading?: boolean
}

export function NLCreator({ placeholder, initialValue = "", onSubmit, loading }: NLCreatorProps) {
  const [value, setValue] = useState(initialValue)

  useEffect(() => {
    if (initialValue) {
      setValue(initialValue)
    }
  }, [initialValue])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (value.trim()) {
      onSubmit(value.trim())
    }
  }

  return (
    <form onSubmit={handleSubmit} className="relative w-full flex items-center">
      <Input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        placeholder={placeholder}
        disabled={loading}
        className="pr-14 h-12 text-[15px]"
      />
      <motion.button
        type="submit"
        disabled={loading || !value.trim()}
        whileHover={!loading && value.trim() ? { scale: 1.05 } : {}}
        whileTap={!loading && value.trim() ? { scale: 0.95 } : {}}
        className={cn(
          "absolute right-2 top-1/2 -translate-y-1/2 h-9 w-9 rounded-full flex items-center justify-center transition-all duration-200",
          value.trim() && !loading
            ? "bg-accent text-white shadow-glow"
            : "bg-white/[0.06] text-fg-muted cursor-not-allowed"
        )}
      >
        {loading ? (
          <Loader2 className="h-4 w-4 animate-spin" />
        ) : (
          <ArrowRight className="h-4 w-4" />
        )}
      </motion.button>
    </form>
  )
}
