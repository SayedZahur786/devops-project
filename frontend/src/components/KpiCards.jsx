export default function KpiCards({ stats }) {
  if (!stats) return null
  const cards = [
    { label: 'Total projects', value: stats.total },
    { label: 'Building now', value: stats.by_status?.building || 0 },
    { label: 'Submitted', value: stats.by_status?.submitted || 0 },
    { label: 'Won', value: stats.by_status?.won || 0 },
    { label: 'High priority open', value: stats.high_priority_open }
  ]
  return (
    <div className="kpi-grid">
      {cards.map((c) => (
        <div className="kpi-card" key={c.label}>
          <div className="kpi-value">{c.value}</div>
          <div className="kpi-label">{c.label}</div>
        </div>
      ))}
    </div>
  )
}
