import React, { useState, useEffect } from 'react'
import {
  Ticket, Car, Clock, AlertTriangle, CheckCircle2,
  Tag, BarChart3, Inbox
} from 'lucide-react'
import { listTickets } from '../services/api'

/**
 * Dashboard view showing all service tickets with stats.
 */
export default function TicketDashboard() {
  const [tickets, setTickets] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadTickets()
  }, [])

  const loadTickets = async () => {
    try {
      const data = await listTickets()
      setTickets(data)
    } catch (err) {
      console.error('Failed to load tickets:', err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (dateStr) => {
    return new Date(dateStr).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    })
  }

  // Compute stats
  const stats = {
    total: tickets.length,
    open: tickets.filter((t) => t.status === 'open').length,
    inProgress: tickets.filter((t) => t.status === 'in_progress').length,
    high: tickets.filter((t) => ['high', 'critical'].includes(t.priority)).length,
  }

  if (loading) {
    return (
      <div className="ticket-dashboard" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div className="spinner" style={{ width: 32, height: 32, color: 'var(--accent-primary)' }} />
      </div>
    )
  }

  return (
    <div className="ticket-dashboard">
      <div className="ticket-dashboard-header">
        <h1>Service Tickets</h1>
        <p>Track and manage escalated service issues</p>
      </div>

      {/* Stats */}
      <div className="ticket-stats">
        <div className="stat-card">
          <div className="stat-card-label">Total Tickets</div>
          <div className="stat-card-value accent">{stats.total}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">Open</div>
          <div className="stat-card-value" style={{ color: 'var(--info)' }}>{stats.open}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">In Progress</div>
          <div className="stat-card-value" style={{ color: 'var(--warning)' }}>{stats.inProgress}</div>
        </div>
        <div className="stat-card">
          <div className="stat-card-label">High Priority</div>
          <div className="stat-card-value" style={{ color: 'var(--error)' }}>{stats.high}</div>
        </div>
      </div>

      {/* Ticket List */}
      {tickets.length === 0 ? (
        <div className="empty-tickets">
          <Inbox size={48} />
          <h3>No Service Tickets</h3>
          <p>Tickets will appear here when issues are escalated from AI troubleshooting.</p>
        </div>
      ) : (
        <div className="ticket-list">
          {tickets.map((ticket) => (
            <div key={ticket.id} className="ticket-card">
              <div className="ticket-card-header">
                <div className="ticket-card-title">{ticket.title}</div>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexShrink: 0 }}>
                  <span className={`priority-badge ${ticket.priority}`}>
                    {ticket.priority === 'critical' && <AlertTriangle size={12} />}
                    {ticket.priority}
                  </span>
                  <span className={`status-badge ${ticket.status === 'open' ? 'active' : ticket.status === 'resolved' ? 'resolved' : 'escalated'}`}>
                    {ticket.status === 'open' && <Ticket size={10} />}
                    {ticket.status === 'resolved' && <CheckCircle2 size={10} />}
                    {ticket.status.replace('_', ' ')}
                  </span>
                </div>
              </div>

              <div className="ticket-card-meta">
                <span>
                  <Car size={13} />
                  {ticket.vehicle_id}
                </span>
                {ticket.category && (
                  <span>
                    <Tag size={13} />
                    {ticket.category}
                  </span>
                )}
                <span>
                  <Clock size={13} />
                  {formatDate(ticket.created_at)}
                </span>
              </div>

              <div className="ticket-card-description">{ticket.description}</div>

              {ticket.ai_summary && (
                <div className="ticket-card-summary">
                  <div className="ticket-card-summary-label">
                    <BarChart3 size={12} style={{ display: 'inline', verticalAlign: '-2px', marginRight: '4px' }} />
                    AI Analysis
                  </div>
                  {ticket.ai_summary}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
