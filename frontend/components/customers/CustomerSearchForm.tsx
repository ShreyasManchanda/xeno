'use client'

import { useRouter, useSearchParams } from 'next/navigation'
import { useState } from 'react'
import { Button } from '@/components/ui/button'

export function CustomerSearchForm() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [search, setSearch] = useState(searchParams.get('search') ?? '')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const params = new URLSearchParams()
    if (search.trim()) params.set('search', search.trim())
    const query = params.toString()
    router.push(query ? `/customers?${query}` : '/customers')
  }

  return (
    <form onSubmit={handleSubmit} className="flex gap-3">
      <input
        type="search"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        placeholder="Search by name or email..."
        className="flex-1 rounded-xl border border-white/[0.08] bg-white/[0.03] px-4 py-2 text-sm text-fg placeholder:text-fg-muted focus:outline-none focus:ring-1 focus:ring-accent/50"
      />
      <Button type="submit" variant="ghost">
        Search
      </Button>
    </form>
  )
}
