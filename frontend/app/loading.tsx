export default function Loading() {
  return (
    <div className="animate-pulse space-y-6">
      <div className="h-10 w-64 bg-fog rounded" />
      <div className="grid grid-cols-4 gap-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="h-32 bg-fog rounded-2xl" />
        ))}
      </div>
    </div>
  )
}
