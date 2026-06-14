import { api } from "@/lib/api"
import { notFound } from "next/navigation"
import { StatusBadge } from "@/components/shared/StatusBadge"
import { ArrowLeft } from "lucide-react"
import Link from "next/link"

interface PageProps {
  params: Promise<{ id: string }>
}

async function getCustomer(id: string) {
  try {
    return await api.customers.get(id)
  } catch (error) {
    return null
  }
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map(n => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()
}

export default async function CustomerDetailPage({ params }: PageProps) {
  const { id } = await params
  const data = await getCustomer(id)

  if (!data) {
    notFound()
  }

  return (
    <div className="space-y-6 relative">
      <header>
        <Link href="/customers" className="text-sm text-fg-muted hover:text-fg flex items-center gap-1 mb-6 transition-colors">
          <ArrowLeft className="h-4 w-4" />
          Back to Customers
        </Link>
      </header>

      <div className="card-glass rounded-2xl p-6 top-highlight relative overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-br from-accent/[0.04] to-transparent pointer-events-none" />
        <div className="relative">
          <div className="flex items-start gap-5">
            <div className="h-14 w-14 rounded-xl bg-accent/10 flex items-center justify-center text-xl font-medium text-accent">
              {getInitials(data.customer.name)}
            </div>
            <div className="flex-1">
              <h1 className="text-xl font-semibold text-fg">{data.customer.name}</h1>
              <div className="flex items-center gap-2 mt-1 text-sm text-fg-muted">
                <span>{data.customer.city}</span>
                {data.customer.city && data.customer.age_group && <span>·</span>}
                <span>{data.customer.age_group}</span>
                <span>·</span>
                <span className="capitalize">{data.customer.preferred_channel}</span>
              </div>
              <div className="flex items-center gap-6 mt-4">
                <div>
                  <span className="text-2xl font-semibold text-accent">
                    ₹{data.customer.total_spent.toLocaleString()}
                  </span>
                  <span className="text-sm text-fg-muted ml-2">total spent</span>
                </div>
                <div>
                  <span className="text-2xl font-semibold text-fg">{data.customer.order_count}</span>
                  <span className="text-sm text-fg-muted ml-2">orders</span>
                </div>
              </div>
            </div>
          </div>

          {data.customer.preferred_categories && data.customer.preferred_categories.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {data.customer.preferred_categories.map((category) => (
                <span
                  key={category}
                  className="rounded-full bg-accent/10 border border-accent/20 px-3 py-1 text-sm font-medium text-accent"
                >
                  {category}
                </span>
              ))}
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-5">
        <div className="card-glass rounded-2xl top-highlight">
          <div className="px-6 py-4 border-b border-white/[0.06]">
            <h3 className="text-xs font-medium uppercase tracking-wider text-fg-muted">Orders</h3>
          </div>
          <div className="px-6 py-4">
            {data.orders.length === 0 ? (
              <p className="text-sm text-fg-muted">No orders yet</p>
            ) : (
              <div className="space-y-4">
                {data.orders.map((order) => (
                  <div key={order.id} className="border-b border-white/[0.04] last:border-0 pb-4 last:pb-0">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-fg">
                        ₹{order.amount.toLocaleString()}
                      </span>
                      <span className="text-xs text-fg-muted">
                        {order.order_date ? new Date(order.order_date).toLocaleDateString() : "-"}
                      </span>
                    </div>
                    <div className="text-xs text-fg-muted">
                      {order.items.map((item) => `${item.name} (₹${item.price})`).join(", ")}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        <div className="card-glass rounded-2xl top-highlight">
          <div className="px-6 py-4 border-b border-white/[0.06]">
            <h3 className="text-xs font-medium uppercase tracking-wider text-fg-muted">Campaign History</h3>
          </div>
          <div className="px-6 py-4">
            {data.campaign_history.length === 0 ? (
              <p className="text-sm text-fg-muted">No campaign history</p>
            ) : (
              <div className="space-y-3">
                {data.campaign_history.slice(0, 5).map((h, index) => (
                  <div key={index} className="flex items-center justify-between">
                    <Link
                      href={`/campaigns/${h.campaign_id}`}
                      className="text-sm font-medium text-fg hover:text-accent transition-colors"
                    >
                      {h.campaign_name}
                    </Link>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-fg-muted">Variant {h.variant_id}</span>
                      <StatusBadge status={h.status as any} />
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
