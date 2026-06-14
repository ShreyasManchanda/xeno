import { NewSegmentClient } from "./NewSegmentClient"

interface PageProps {
  searchParams: Promise<{ goal?: string }>
}

export default async function NewSegmentPage({ searchParams }: PageProps) {
  const params = await searchParams
  return <NewSegmentClient prefillGoal={params.goal ?? ""} />
}
