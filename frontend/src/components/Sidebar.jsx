import React from 'react'
import {
  Zap, MessageSquare, Ticket, Car, Clock,
  MessagesSquare
} from 'lucide-react'

/**
 * Left sidebar with branding, navigation, and conversation list.
 */
export default function Sidebar({
  conversations,
  activeConversationId,
  activeView,
  onSelectConversation,
  onNewIssue,
  onViewChange,
}) {
  const formatTime = (dateStr) => {
    const date = new Date(dateStr)
    const now = new Date()
    const diff = now - date

    if (diff < 60000) return 'Just now'
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`
    return date.toLocaleDateString()
  }

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-header">
        <div className="sidebar-logo">
          <div className="logo-icon">
            <Zap size={22} />
          </div>
          <div className="logo-text">
            <span>Optimotion</span>
          </div>
        </div>
        <button className="btn-new-issue" onClick={onNewIssue}>
          <MessageSquare size={18} />
          Report an Issue
        </button>
      </div>

      {/* Navigation */}
      <div className="sidebar-nav">
        <button
          className={`nav-tab ${activeView === 'chat' ? 'active' : ''}`}
          onClick={() => onViewChange('chat')}
        >
          <MessagesSquare size={16} />
          Chats
        </button>
        <button
          className={`nav-tab ${activeView === 'tickets' ? 'active' : ''}`}
          onClick={() => onViewChange('tickets')}
        >
          <Ticket size={16} />
          Tickets
        </button>
      </div>

      {/* Conversation List */}
      <div className="conversation-list">
        {conversations.length === 0 ? (
          <div className="conversation-list-empty">
            <MessageSquare size={32} />
            <p>No conversations yet.<br />Report an issue to get started.</p>
          </div>
        ) : (
          conversations.map((conv) => (
            <div
              key={conv.id}
              className={`conversation-item ${conv.id === activeConversationId ? 'active' : ''}`}
              onClick={() => onSelectConversation(conv.id)}
            >
              <div className="conversation-item-header">
                <span className="conversation-vehicle">
                  <Car size={14} />
                  {conv.vehicle_id}
                </span>
                <span className={`status-badge ${conv.status}`}>
                  {conv.status}
                </span>
              </div>
              <div className="conversation-preview">
                {conv.issue_description}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px', marginTop: '6px' }}>
                <Clock size={10} color="var(--text-tertiary)" />
                <span className="conversation-time">{formatTime(conv.created_at)}</span>
                {conv.category && (
                  <span className="category-badge" style={{ marginLeft: 'auto' }}>
                    {conv.category}
                  </span>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </aside>
  )
}
