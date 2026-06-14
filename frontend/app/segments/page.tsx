import { api } from "@/lib/api"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { StatusBadge } from "@/components/shared/StatusBadge"

async function getSegments() {
  try {
    return await api.segments.list()
  } catch (error) {
    return []
  }
}

export default async function SegmentsPage() {
  const segments = await getSegments()

  return (
    <div className="space-y-6 relative">
      <header className="flex items-center justify-between">
        <h1 className="font-display text-heading text-fg">Segments</h1>
        <Link href="/segments/new">
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-2" />
            New Segment
          </Button>
        </Link>
      </header>

      {segments.length === 0 ? (
        <div className="card-glass rounded-2xl p-12 text-center top-highlight">
          <p className="text-sm text-fg-muted mb-4">No segments yet.</p>
          <Link href="/segments/new" className="text-sm font-medium text-accent hover:text-accent-dim transition-colors">
            Create your first segment →
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-3 gap-5">
          {segments.map((segment, index) => (
            <Link key={segment.id} href={`/segments/${segment.id}`}>
              <div className="card-glass rounded-2xl p-5 top-highlight hover:border-white/[0.1] transition-all duration-200 hover:shadow-card-hover">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-lg font-medium text-fg">{segment.name || "Unnamed Segment"}</h3>
                  <StatusBadge status={segment.created_by === "ai" ? "draft" : "completed"} />
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-semibold text-fg">{segment.customer_count || 0}</span>
                  <span className="text-sm text-fg-muted">customers</span>
                </div>
                {segment.created_by && (
                  <p className="text-xs text-fg-muted mt-4 capitalize">
                    Created by {segment.created_by}
                  </p>
                )}
              </div>
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}
