import { api } from "@/lib/api"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { CustomerSearchForm } from "@/components/customers/CustomerSearchForm"
import { Suspense } from "react"

interface PageProps {
  searchParams: Promise<{
    search?: string
    city?: string
    age_group?: string
    page?: string
  }>
}

async function getCustomers(params: { search?: string; city?: string; age_group?: string; page?: string }) {
  try {
    return await api.customers.list({
      search: params.search,
      city: params.city,
      age_group: params.age_group,
      page: params.page ? parseInt(params.page) : 1,
    })
  } catch (error) {
    return { customers: [], total: 0, page: 1, limit: 20 }
  }
}

export default async function CustomersPage({ searchParams }: PageProps) {
  const params = await searchParams
  const data = await getCustomers(params)
  const totalPages = Math.ceil(data.total / data.limit)

  return (
    <div className="space-y-6 relative">
      <header>
        <h1 className="font-display text-heading text-fg">Customers</h1>
      </header>

      <Suspense fallback={null}>
        <CustomerSearchForm />
      </Suspense>

      <div className="card-glass rounded-2xl overflow-hidden top-highlight">
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
                Age Group
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                Total Spent
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                Orders
              </th>
              <th className="px-5 py-3 text-left text-xs font-medium uppercase tracking-wider text-fg-muted">
                Channel
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/[0.06]">
            {data.customers.map((customer) => (
              <tr key={customer.id} className="hover:bg-white/[0.02] transition-colors">
                <td className="px-5 py-3">
                  <Link
                    href={`/customers/${customer.id}`}
                    className="text-sm font-medium text-fg hover:text-accent transition-colors"
                  >
                    {customer.name}
                  </Link>
                </td>
                <td className="px-5 py-3 text-sm text-fg-muted">{customer.email || "-"}</td>
                <td className="px-5 py-3 text-sm text-fg-muted">{customer.city || "-"}</td>
                <td className="px-5 py-3 text-sm text-fg-muted">{customer.age_group || "-"}</td>
                <td className="px-5 py-3 text-sm font-medium text-fg">
                  ₹{customer.total_spent.toLocaleString()}
                </td>
                <td className="px-5 py-3 text-sm text-fg-muted">{customer.order_count}</td>
                <td className="px-5 py-3 text-sm text-fg-muted capitalize">
                  {customer.preferred_channel}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {data.customers.length === 0 && (
          <div className="px-5 py-12 text-center text-sm text-fg-muted">
            No customers found.
          </div>
        )}

        {totalPages > 1 && (
          <div className="flex items-center justify-between px-5 py-4 border-t border-white/[0.06]">
            <span className="text-sm text-fg-muted">
              Showing {((data.page - 1) * data.limit) + 1} to {Math.min(data.page * data.limit, data.total)} of {data.total}
            </span>
            <div className="flex gap-2">
              {data.page > 1 && (
                <Link
                  href={`/customers?${new URLSearchParams({
                    ...(params.search ? { search: params.search } : {}),
                    ...(params.city ? { city: params.city } : {}),
                    ...(params.age_group ? { age_group: params.age_group } : {}),
                    page: String(data.page - 1),
                  }).toString()}`}
                >
                  <Button variant="ghost">Previous</Button>
                </Link>
              )}
              {data.page < totalPages && (
                <Link
                  href={`/customers?${new URLSearchParams({
                    ...(params.search ? { search: params.search } : {}),
                    ...(params.city ? { city: params.city } : {}),
                    ...(params.age_group ? { age_group: params.age_group } : {}),
                    page: String(data.page + 1),
                  }).toString()}`}
                >
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
