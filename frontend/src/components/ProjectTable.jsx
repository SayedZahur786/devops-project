const NEXT_STATUS = { idea: 'building', building: 'submitted', submitted: 'won' }

export default function ProjectTable({ projects, onStatusChange, onDelete }) {
  return (
    <section className="card table-card">
      <h2>Projects</h2>
      {projects.length === 0 ? (
        <p className="empty">No projects yet. Create your first one.</p>
      ) : (
        <table>
          <thead>
            <tr>
              <th>Project</th>
              <th>Team</th>
              <th>Hackathon</th>
              <th>Priority</th>
              <th>Status</th>
              <th>Deadline</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {projects.map((p) => (
              <tr key={p.id}>
                <td>
                  <div className="proj-title">{p.title}</div>
                  {p.description && <div className="proj-desc">{p.description}</div>}
                </td>
                <td>{p.team_name}</td>
                <td>{p.hackathon}</td>
                <td>
                  <span className={`badge prio-${p.priority}`}>{p.priority}</span>
                </td>
                <td>
                  <span className={`badge status-${p.status}`}>{p.status}</span>
                </td>
                <td>{p.deadline || '-'}</td>
                <td className="row-actions">
                  {NEXT_STATUS[p.status] && (
                    <button
                      className="link"
                      onClick={() => onStatusChange(p.id, NEXT_STATUS[p.status])}
                    >
                      move to {NEXT_STATUS[p.status]}
                    </button>
                  )}
                  <button className="link danger" onClick={() => onDelete(p.id)}>
                    delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}
