export default function ActivityFeed({ projects }) {
  const recent = [...projects]
    .sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at))
    .slice(0, 6)
  return (
    <aside className="card activity">
      <h2>Recent activity</h2>
      {recent.length === 0 ? (
        <p className="empty">Nothing yet.</p>
      ) : (
        <ul>
          {recent.map((p) => (
            <li key={p.id}>
              <span className={`dot status-${p.status}`}></span>
              <div>
                <strong>{p.title}</strong> is <em>{p.status}</em>
                <div className="activity-meta">
                  {p.team_name} · {p.hackathon}
                </div>
              </div>
            </li>
          ))}
        </ul>
      )}
    </aside>
  )
}
