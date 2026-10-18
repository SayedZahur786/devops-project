import { useCallback, useEffect, useState } from 'react'
import { api } from './api'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import KpiCards from './components/KpiCards'
import ProjectTable from './components/ProjectTable'
import ActivityFeed from './components/ActivityFeed'
import CreateProjectModal from './components/CreateProjectModal'

export default function App() {
  const [projects, setProjects] = useState([])
  const [stats, setStats] = useState(null)
  const [filter, setFilter] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [modalOpen, setModalOpen] = useState(false)
  const [backendUp, setBackendUp] = useState(true)

  const load = useCallback(async () => {
    try {
      const [rows, s] = await Promise.all([
        api.listProjects(filter || undefined),
        api.stats()
      ])
      setProjects(rows)
      setStats(s)
      setError(null)
      setBackendUp(true)
    } catch (e) {
      setError('Backend is unreachable. Is the API container running?')
      setBackendUp(false)
    } finally {
      setLoading(false)
    }
  }, [filter])

  useEffect(() => {
    setLoading(true)
    load()
  }, [load])

  const handleCreate = async (data) => {
    await api.createProject(data)
    setModalOpen(false)
    load()
  }

  const handleStatusChange = async (id, status) => {
    await api.updateProject(id, { status })
    load()
  }

  const handleDelete = async (id) => {
    await api.deleteProject(id)
    load()
  }

  return (
    <div className="layout">
      <Sidebar filter={filter} onFilter={setFilter} />
      <main className="main">
        <Header onNewProject={() => setModalOpen(true)} backendUp={backendUp} />
        {error && <div className="error-banner">{error}</div>}
        {loading ? (
          <div className="loading">Loading projects...</div>
        ) : (
          <>
            <KpiCards stats={stats} />
            <div className="content-grid">
              <ProjectTable
                projects={projects}
                onStatusChange={handleStatusChange}
                onDelete={handleDelete}
              />
              <ActivityFeed projects={projects} />
            </div>
          </>
        )}
        {modalOpen && (
          <CreateProjectModal
            onClose={() => setModalOpen(false)}
            onCreate={handleCreate}
          />
        )}
      </main>
    </div>
  )
}
