import { NewCampaignClient } from "./NewCampaignClient"

interface PageProps {
  searchParams: Promise<{ goal?: string }>
}

export default async function NewCampaignPage({ searchParams }: PageProps) {
  const params = await searchParams
  return <NewCampaignClient prefillGoal={params.goal ?? ""} />
}
