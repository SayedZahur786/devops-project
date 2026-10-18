export default function Header({ onNewProject, backendUp }) {
  return (
    <header className="header">
      <div>
        <h1>Hackathon projects</h1>
        <p className="subtitle">Track ideas, builds and submissions in one place</p>
      </div>
      <div className="header-right">
        <span className={`pipeline ${backendUp ? 'up' : 'down'}`}>
          {backendUp ? 'pipeline: green' : 'backend: down'}
        </span>
        <button className="primary" onClick={onNewProject}>
          + New project
        </button>
      </div>
    </header>
  )
}
