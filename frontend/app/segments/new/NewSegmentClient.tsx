'use client'

import { useState } from "react"
import { NLCreator } from "@/components/segments/NLCreator"
import { FilterChips } from "@/components/segments/FilterChips"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { api } from "@/lib/api"
import type { SegmentPreview, FilterRules } from "@/lib/types"

interface NewSegmentClientProps {
  prefillGoal?: string
}

export function NewSegmentClient({ prefillGoal = "" }: NewSegmentClientProps) {
  const router = useRouter()
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [preview, setPreview] = useState<SegmentPreview | null>(null)
  const [name, setName] = useState("")

  const handleGenerate = async (query: string) => {
    setLoading(true)
    try {
      const result = await api.segments.preview(query)
      setPreview(result)
    } catch (error) {
      console.error("Preview failed:", error)
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!preview || !name.trim()) return

    setSaving(true)
    try {
      const segment = await api.segments.create({
        name: name.trim(),
        nl_query: preview.reasoning,
        filter_rules: preview.filter_rules,
        created_by: "manual",
      })
      router.push(`/segments/${segment.id}`)
    } catch (error) {
      console.error("Failed to save segment:", error)
    } finally {
      setSaving(false)
    }
  }

  const handleFilterChange = (rules: FilterRules) => {
    if (preview) {
      setPreview({ ...preview, filter_rules: rules })
    }
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <div>
        <Link href="/segments" className="text-sm text-graphite hover:text-ink flex items-center gap-1 mb-4">
          <ArrowLeft className="h-4 w-4" />
          Back to Segments
        </Link>
        <h1 className="text-2xl font-semibold text-ink">Create Segment</h1>
      </div>

      <section className="card-glass rounded-2xl p-6 top-highlight relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-accent/[0.03] to-transparent pointer-events-none" />
        <div className="relative">
          <h3 className="text-label font-medium uppercase tracking-wider text-fg-muted mb-4">
            Describe your audience
          </h3>
          <NLCreator
            placeholder="e.g., Customers who spent over ₹10,000 but haven't ordered in 90 days"
            initialValue={prefillGoal}
            onSubmit={handleGenerate}
            loading={loading}
          />
        </div>
      </section>

      {loading && (
        <div className="card-glass rounded-2xl p-6 top-highlight">
          <p className="text-sm text-fg-muted">Analyzing your request...</p>
        </div>
      )}

      {preview && !loading && (
        <div className="card-glass rounded-2xl p-6 top-highlight space-y-6">
          <div>
            <h3 className="text-label font-medium uppercase tracking-wider text-fg-muted mb-3">
              Filter Rules
            </h3>
            <FilterChips
              filterRules={preview.filter_rules}
              onChange={handleFilterChange}
              editable={true}
            />
          </div>

          <div>
            <h3 className="text-label font-medium uppercase tracking-wider text-fg-muted mb-3">
              Sample Customers ({preview.customer_count} total)
            </h3>
            {preview.sample_customers && preview.sample_customers.length > 0 ? (
              <div className="space-y-2">
                {preview.sample_customers.slice(0, 5).map((customer) => (
                  <div key={customer.id} className="rounded-[10px] bg-white/[0.03] px-4 py-2 text-sm border border-white/[0.06]">
                    <span className="font-medium text-fg">{customer.name}</span>
                    {customer.city && (
                      <span className="text-fg-muted ml-2">· {customer.city}</span>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <p className="text-sm text-fg-muted">No matching customers</p>
            )}
          </div>

          <div className="pt-4 border-t border-white/[0.06]">
            <Label htmlFor="segment-name" className="mb-2 block text-fg">Segment Name</Label>
            <Input
              id="segment-name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="e.g., High-value inactive customers"
            />
          </div>

          <div className="flex gap-3">
            <Button onClick={handleSave} disabled={saving || !name.trim()}>
              {saving ? "Saving..." : "Save Segment"}
            </Button>
            <Button variant="secondary" onClick={() => setPreview(null)}>
              Start Over
            </Button>
          </div>
        </div>
      )}
    </div>
  )
}
