import { api } from "@/lib/api"
import { KPICards } from "@/components/dashboard/KPICards"
import { NudgeCard } from "@/components/dashboard/NudgeCard"
import { Button } from "@/components/ui/button"
import Link from "next/link"
import { Megaphone } from "lucide-react"
import { StatusBadge } from "@/components/shared/StatusBadge"

async function getDashboardData() {
  try {
    const [stats, campaigns] = await Promise.all([
      api.dashboard.getStats(),
      api.campaigns.list(),
    ])
    return { ...stats, recentCampaigns: campaigns.slice(0, 5) }
  } catch (error) {
    console.error("Failed to fetch dashboard:", error)
    return {
      kpis: { total_customers: 0, active_segments: 0, campaigns_run: 0, avg_read_rate: 0 },
      nudges: [],
      recentCampaigns: [],
    }
  }
}

export default async function DashboardPage() {
  const data = await getDashboardData()
  const greeting = getGreeting()

  return (
    <div className="space-y-12 relative">
      <div className="glow-orb top-0 left-1/4 opacity-50" aria-hidden="true" />
      
      <header className="relative">
        <p className="text-base text-fg-muted mb-2">
          {greeting},
        </p>
        <h1 className="font-serif text-display text-fg italic">
          Tana &amp; Co.
        </h1>
      </header>

      <section className="relative">
        <KPICards kpis={data.kpis} />
      </section>

      <section className="grid grid-cols-3 gap-6 relative">
        <div className="col-span-1 space-y-4">
          {data.nudges.map((nudge, index) => (
            <NudgeCard key={index} nudge={nudge} index={index} />
          ))}
          {data.nudges.length === 0 && (
            <div className="card-glass rounded-2xl p-6 top-highlight">
              <p className="text-sm text-fg-muted">
                No suggestions yet. Create more segments to unlock AI recommendations.
              </p>
            </div>
          )}
        </div>

        <div className="col-span-2">
          <div className="card-glass rounded-2xl top-highlight">
            <div className="px-6 py-4 border-b border-white/[0.06] flex items-center justify-between">
              <h3 className="text-label font-medium text-fg-muted uppercase tracking-wider">
                Recent Campaigns
              </h3>
              {data.recentCampaigns.length > 0 && (
                <Link href="/campaigns" className="text-sm text-accent hover:text-accent-dim transition-colors">
                  View all
                </Link>
              )}
            </div>
            {data.recentCampaigns.length > 0 ? (
              <table className="w-full">
                <tbody className="divide-y divide-white/[0.06]">
                  {data.recentCampaigns.map((campaign) => (
                    <tr key={campaign.id} className="hover:bg-white/[0.02] transition-colors">
                      <td className="px-6 py-4">
                        <Link
                          href={`/campaigns/${campaign.id}`}
                          className="text-sm font-medium text-fg hover:text-accent transition-colors"
                        >
                          {campaign.name || "Untitled Campaign"}
                        </Link>
                        <p className="text-xs text-fg-muted mt-1 capitalize">{campaign.channel || "—"}</p>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <StatusBadge status={campaign.status as any} />
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
            <div className="px-6 py-16 flex flex-col items-center justify-center text-center">
              <div className="w-14 h-14 rounded-xl bg-white/[0.03] flex items-center justify-center mb-5 top-highlight">
                <Megaphone className="h-7 w-7 text-fg-muted" />
              </div>
              <p className="text-body text-fg-muted mb-6">
                No campaigns yet
              </p>
              <Link href="/campaigns/new">
                <Button variant="primary">
                  Create your first campaign
                </Button>
              </Link>
            </div>
            )}
          </div>
        </div>
      </section>
    </div>
  )
}

function getGreeting(): string {
  const hour = new Date().getHours()
  if (hour < 12) return "Good morning"
  if (hour < 18) return "Good afternoon"
  return "Good evening"
}
