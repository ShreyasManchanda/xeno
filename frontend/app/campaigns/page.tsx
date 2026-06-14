import { api } from "@/lib/api"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Plus } from "lucide-react"
import { StatusBadge } from "@/components/shared/StatusBadge"

interface PageProps {
  searchParams: Promise<{ status?: string }>
}

async function getCampaigns(status?: string) {
  try {
    return await api.campaigns.list(status)
  } catch (error) {
    return []
  }
}

export default async function CampaignsPage({ searchParams }: PageProps) {
  const { status } = await searchParams
  const normalizedStatus = status === "complete" ? "completed" : status
  const campaigns = await getCampaigns(normalizedStatus)

  const statusTabs = [
    { label: "All", value: undefined },
    { label: "Draft", value: "draft" },
    { label: "Running", value: "running" },
    { label: "Completed", value: "completed" },
  ]

  return (
    <div className="space-y-6 relative">
      <header className="flex items-center justify-between">
        <h1 className="font-display text-heading text-fg">Campaigns</h1>
        <Link href="/campaigns/new">
          <Button variant="primary">
            <Plus className="h-4 w-4 mr-2" />
            New Campaign
          </Button>
        </Link>
      </header>

      <div className="flex gap-2">
        {statusTabs.map((tab) => {
          const isActive = status === tab.value || (!status && !tab.value) || (status === "complete" && tab.value === "completed")
          return (
            <Link key={tab.label} href={`/campaigns${tab.value ? `?status=${tab.value}` : ""}`}>
              <button
                className={`rounded-full px-5 py-2 text-sm font-medium transition-all duration-150 active:scale-[0.97] ${
                  isActive
                    ? "bg-accent text-white shadow-glow"
                    : "bg-white/[0.03] text-fg-muted hover:bg-white/[0.06] hover:text-fg border border-white/[0.06]"
                }`}
              >
                {tab.label}
              </button>
            </Link>
          )
        })}
      </div>

      <div className="card-glass rounded-2xl overflow-hidden top-highlight">
        <table className="w-full">
          <thead className="bg-white/[0.02]">
            <tr>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                Name
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                Channel
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                Status
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                Segment
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                Launched
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.06]">
            {campaigns.map((campaign) => (
              <tr key={campaign.id} className="hover:bg-white/[0.02] transition-colors">
                <td className="px-5 py-3">
                  <Link
                    href={`/campaigns/${campaign.id}`}
                    className="text-sm font-medium text-fg hover:text-accent transition-colors"
                  >
                    {campaign.name || "Untitled Campaign"}
                  </Link>
                </td>
                <td className="px-5 py-3 text-sm text-fg-muted capitalize">{campaign.channel || "-"}</td>
                <td className="px-5 py-3">
                  <StatusBadge status={campaign.status as any} />
                </td>
                <td className="px-5 py-3 text-sm text-fg-muted">
                  {campaign.segment_id ? "Segment" : "-"}
                </td>
                <td className="px-5 py-3 text-sm text-fg-muted">
                  {campaign.launched_at
                    ? new Date(campaign.launched_at).toLocaleDateString()
                    : "-"}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {campaigns.length === 0 && (
          <div className="px-5 py-12 text-center">
            <p className="text-sm text-fg-muted mb-4">No campaigns yet.</p>
            <Link href="/campaigns/new" className="text-sm font-medium text-accent hover:text-accent-dim transition-colors">
              Create your first campaign →
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
