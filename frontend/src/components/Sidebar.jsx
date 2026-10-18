const FILTERS = [
  { key: '', label: 'All projects' },
  { key: 'idea', label: 'Ideas' },
  { key: 'building', label: 'Building' },
  { key: 'submitted', label: 'Submitted' },
  { key: 'won', label: 'Won' }
]

export default function Sidebar({ filter, onFilter }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <span className="brand-mark">HB</span>
        <span className="brand-name">HackBoard</span>
      </div>
      <div className="nav-section">Workspace</div>
      <nav>
        {FILTERS.map((f) => (
          <button
            key={f.key}
            className={`nav-item ${filter === f.key ? 'active' : ''}`}
            onClick={() => onFilter(f.key)}
          >
            {f.label}
          </button>
        ))}
      </nav>
      <div className="nav-section">Hackathons</div>
      <nav>
        <span className="nav-item muted">RIFT 2026</span>
        <span className="nav-item muted">ETHGlobal Mumbai</span>
        <span className="nav-item muted">Goa Hacks</span>
      </nav>
    </aside>
  )
}
