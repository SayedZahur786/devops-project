import { useState } from 'react'

const EMPTY = {
  title: '',
  team_name: '',
  hackathon: '',
  track: 'open',
  status: 'idea',
  priority: 'medium',
  description: '',
  deadline: ''
}

export default function CreateProjectModal({ onClose, onCreate }) {
  const [form, setForm] = useState(EMPTY)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value })

  const submit = async (e) => {
    e.preventDefault()
    setSaving(true)
    setError(null)
    try {
      const payload = { ...form }
      if (!payload.deadline) delete payload.deadline
      if (!payload.description) delete payload.description
      await onCreate(payload)
    } catch (err) {
      setError('Could not create project. Check the fields and try again.')
      setSaving(false)
    }
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>New project</h2>
        <form onSubmit={submit}>
          <label>
            Title
            <input required value={form.title} onChange={set('title')} />
          </label>
          <label>
            Team
            <input required value={form.team_name} onChange={set('team_name')} />
          </label>
          <label>
            Hackathon
            <input required value={form.hackathon} onChange={set('hackathon')} />
          </label>
          <label>
            Track
            <input value={form.track} onChange={set('track')} />
          </label>
          <div className="form-row">
            <label>
              Priority
              <select value={form.priority} onChange={set('priority')}>
                <option value="low">low</option>
                <option value="medium">medium</option>
                <option value="high">high</option>
              </select>
            </label>
            <label>
              Deadline
              <input type="date" value={form.deadline} onChange={set('deadline')} />
            </label>
          </div>
          <label>
            Description
            <textarea rows="3" value={form.description} onChange={set('description')} />
          </label>
          {error && <div className="error-banner">{error}</div>}
          <div className="modal-actions">
            <button type="button" className="link" onClick={onClose}>
              cancel
            </button>
            <button type="submit" className="primary" disabled={saving}>
              {saving ? 'Saving...' : 'Create project'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
