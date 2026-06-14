'use client'

import { useState } from "react"
import { X } from "lucide-react"
import { cn } from "@/lib/utils"
import type { FilterRule, FilterRules } from "@/lib/types"

interface FilterChipsProps {
  filterRules: FilterRules
  onChange: (rules: FilterRules) => void
  editable?: boolean
}

const fieldLabels: Record<string, string> = {
  total_spent: "Total Spent",
  order_count: "Orders",
  last_order_date: "Last Order",
  city: "City",
  region: "Region",
  age_group: "Age Group",
  preferred_categories: "Categories",
}

const opLabels: Record<string, string> = {
  gt: ">",
  lt: "<",
  gte: "≥",
  lte: "≤",
  eq: "=",
  neq: "≠",
  in: "in",
  lt_days_ago: "days ago <",
  gt_days_ago: "days ago >",
  contains: "has",
}

function formatValue(rule: FilterRule): string {
  if (rule.op === "lt_days_ago" || rule.op === "gt_days_ago") {
    return `${rule.value} days`
  }
  if (Array.isArray(rule.value)) {
    return rule.value.join(", ")
  }
  if (rule.field === "total_spent" && typeof rule.value === "number") {
    return `₹${rule.value.toLocaleString()}`
  }
  return String(rule.value)
}

export function FilterChips({ filterRules, onChange, editable = false }: FilterChipsProps) {
  const rules = filterRules.rules || []

  const handleRemove = (index: number) => {
    const newRules = rules.filter((_, i) => i !== index)
    onChange({ operator: filterRules.operator, rules: newRules })
  }

  if (rules.length === 0) {
    return (
      <span className="text-sm text-graphite">No filters applied</span>
    )
  }

  return (
    <div className="flex flex-wrap gap-2">
      {rules.map((rule, index) => (
        <span
          key={index}
          className="inline-flex items-center gap-1 rounded-full bg-rust-dim border border-rust/25 px-2.5 py-1 text-[13px] font-medium text-rust"
        >
          <span>{fieldLabels[rule.field] || rule.field}</span>
          <span className="text-rust/70">{opLabels[rule.op] || rule.op}</span>
          <span>{formatValue(rule)}</span>
          {editable && (
            <button
              onClick={() => handleRemove(index)}
              className="ml-1 hover:text-ink"
            >
              <X className="h-3 w-3" />
            </button>
          )}
        </span>
      ))}
    </div>
  )
}
