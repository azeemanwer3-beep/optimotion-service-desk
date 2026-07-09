import React, { useState } from 'react'
import { AlertCircle, Car, X, Send } from 'lucide-react'

/**
 * Modal form for reporting a new EV issue.
 * Collects Vehicle ID and issue description.
 */
export default function NewIssueForm({ onSubmit, onClose }) {
  const [vehicleId, setVehicleId] = useState('')
  const [description, setDescription] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')

    if (!vehicleId.trim()) {
      setError('Please enter a Vehicle ID')
      return
    }
    if (!description.trim() || description.trim().length < 5) {
      setError('Please describe your issue (at least 5 characters)')
      return
    }

    setLoading(true)
    try {
      await onSubmit(vehicleId.trim(), description.trim())
    } catch (err) {
      setError(err.message || 'Failed to create conversation')
      setLoading(false)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Report an Issue</h2>
          <button className="modal-close" onClick={onClose} aria-label="Close">
            <X size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="modal-body">
            {error && (
              <div style={{
                padding: '10px 14px',
                background: 'var(--error-bg)',
                color: 'var(--error)',
                borderRadius: 'var(--radius-sm)',
                fontSize: '13px',
                marginBottom: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
              }}>
                <AlertCircle size={16} />
                {error}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="vehicle-id">
                <Car size={14} style={{ display: 'inline', verticalAlign: '-2px', marginRight: '6px' }} />
                Vehicle ID
              </label>
              <input
                id="vehicle-id"
                type="text"
                className="form-input"
                placeholder="e.g., EV-2024-0042"
                value={vehicleId}
                onChange={(e) => setVehicleId(e.target.value)}
                autoFocus
                disabled={loading}
              />
            </div>

            <div className="form-group">
              <label htmlFor="issue-description">
                <AlertCircle size={14} style={{ display: 'inline', verticalAlign: '-2px', marginRight: '6px' }} />
                Describe Your Issue
              </label>
              <textarea
                id="issue-description"
                className="form-input"
                placeholder="Tell us what's happening with your vehicle. Be as detailed as possible — include any error messages, warning lights, or symptoms you've noticed."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                disabled={loading}
              />
            </div>
          </div>

          <div className="modal-footer">
            <button type="button" className="btn-secondary" onClick={onClose} disabled={loading}>
              Cancel
            </button>
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <span className="spinner" />
                  Creating...
                </>
              ) : (
                <>
                  <Send size={16} />
                  Start Troubleshooting
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
