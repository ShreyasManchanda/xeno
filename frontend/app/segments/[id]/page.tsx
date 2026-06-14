import { api } from "@/lib/api"
import { notFound } from "next/navigation"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"
import { Button } from "@/components/ui/button"

interface PageProps {
  params: Promise<{ id: string }>
  searchParams: Promise<{ page?: string }>
}

async function getSegment(id: string, page: number) {
  try {
    return await api.segments.get(id, page)
  } catch (error) {
    return null
  }
}

export default async function SegmentDetailPage({ params, searchParams }: PageProps) {
  const { id } = await params
  const { page } = await searchParams
  const data = await getSegment(id, parseInt(page || "1"))

  if (!data) {
    notFound()
  }

  const currentPage = parseInt(page || "1")
  const limit = 20
  const totalPages = Math.ceil((data.segment.customer_count || 0) / limit)

  return (
    <div className="space-y-6 relative">
      <header>
        <Link href="/segments" className="text-sm text-fg-muted hover:text-fg flex items-center gap-1 mb-6 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          Back to Segments
        </Link>
      </header>

      <div className="flex items-start justify-between">
        <div>
          <h1 className="font-display text-heading text-fg">{data.segment.name}</h1>
          <div className="flex items-center gap-2 mt-2">
            <span className="text-lg text-fg">{data.segment.customer_count || 0} customers</span>
            {data.segment.created_by && (
              <>
                <span className="text-fg-muted">·</span>
                <span className="text-sm text-fg-muted capitalize">Created by {data.segment.created_by}</span>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <div className="card-glass rounded-2xl p-5 top-highlight">
          <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-2">Campaigns</p>
          <p className="text-3xl font-semibold text-fg">{data.performance.campaigns_run}</p>
        </div>
        <div className="card-glass rounded-2xl p-5 top-highlight relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-br from-accent/[0.06] to-transparent pointer-events-none" />
          <div className="relative">
            <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-2">Avg Read Rate</p>
            <p className="text-3xl font-semibold text-accent">{(data.performance.avg_read_rate * 100).toFixed(1)}%</p>
          </div>
        </div>
        <div className="card-glass rounded-2xl p-5 top-highlight">
          <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-2">Avg Click Rate</p>
          <p className="text-3xl font-semibold text-fg">{(data.performance.avg_click_rate * 100).toFixed(1)}%</p>
        </div>
        <div className="card-glass rounded-2xl p-5 top-highlight">
          <p className="text-xs font-medium uppercase tracking-wider text-fg-muted mb-2">Avg Order Rate</p>
          <p className="text-3xl font-semibold text-fg">{(data.performance.avg_order_rate * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div className="card-glass rounded-2xl overflow-hidden top-highlight">
        <div className="px-6 py-4 border-b border-white/[0.06]">
          <h3 className="text-xs font-medium uppercase tracking-wider text-fg-muted">Customers</h3>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-white/[0.02]">
              <tr>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                  Name
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                  Email
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                  City
                </th>
                <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                  Total Spent
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/[0.06]">
              {data.customers.map((customer) => (
                <tr key={customer.id} className="hover:bg-white/[0.02] transition-colors">
                  <td className="px-5 py-3 text-sm font-medium text-fg">{customer.name}</td>
                  <td className="px-5 py-3 text-sm text-fg-muted">{customer.email || "-"}</td>
                  <td className="px-5 py-3 text-sm text-fg-muted">{customer.city || "-"}</td>
                  <td className="px-5 py-3 text-sm text-fg">₹{customer.total_spent.toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {data.customers.length === 0 && (
          <div className="px-5 py-12 text-center text-sm text-fg-muted">
            No customers in this segment.
          </div>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-between px-5 py-4 border-t border-white/[0.06]">
            <span className="text-sm text-fg-muted">
              Page {currentPage} of {totalPages}
            </span>
            <div className="flex gap-2">
              {currentPage > 1 && (
                <Link href={`/segments/${id}?page=${currentPage - 1}`}>
                  <Button variant="ghost">Previous</Button>
                </Link>
              )}
              {currentPage < totalPages && (
                <Link href={`/segments/${id}?page=${currentPage + 1}`}>
                  <Button variant="ghost">Next</Button>
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
