import React, { useState, useEffect, useCallback } from 'react'
import Sidebar from './components/Sidebar'
import ChatInterface from './components/ChatInterface'
import TicketDashboard from './components/TicketDashboard'
import NewIssueForm from './components/NewIssueForm'
import {
  createConversation,
  listConversations,
  getConversation,
} from './services/api'

/**
 * Root application component.
 * Manages global state: conversations, active view, and modals.
 */
export default function App() {
  const [conversations, setConversations] = useState([])
  const [activeConversationId, setActiveConversationId] = useState(null)
  const [activeConversation, setActiveConversation] = useState(null)
  const [activeView, setActiveView] = useState('chat') // 'chat' | 'tickets'
  const [showNewIssue, setShowNewIssue] = useState(false)

  // Load conversations on mount
  useEffect(() => {
    loadConversations()
  }, [])

  const loadConversations = async () => {
    try {
      const data = await listConversations()
      setConversations(data)
    } catch (err) {
      console.error('Failed to load conversations:', err)
    }
  }

  const loadConversation = useCallback(async (id) => {
    try {
      const data = await getConversation(id)
      setActiveConversation(data)
    } catch (err) {
      console.error('Failed to load conversation:', err)
    }
  }, [])

  // Load full conversation when selection changes
  useEffect(() => {
    if (activeConversationId) {
      loadConversation(activeConversationId)
    } else {
      setActiveConversation(null)
    }
  }, [activeConversationId, loadConversation])

  const handleNewIssue = async (vehicleId, description) => {
    const conv = await createConversation(vehicleId, description)
    setShowNewIssue(false)
    setActiveView('chat')
    await loadConversations()
    setActiveConversationId(conv.id)
  }

  const handleConversationUpdate = async () => {
    await loadConversations()
    if (activeConversationId) {
      await loadConversation(activeConversationId)
    }
  }

  const handleSelectConversation = (id) => {
    setActiveConversationId(id)
    setActiveView('chat')
  }

  return (
    <div className="app-layout">
      <Sidebar
        conversations={conversations}
        activeConversationId={activeConversationId}
        activeView={activeView}
        onSelectConversation={handleSelectConversation}
        onNewIssue={() => setShowNewIssue(true)}
        onViewChange={setActiveView}
      />

      {activeView === 'chat' ? (
        <ChatInterface
          conversation={activeConversation}
          onConversationUpdate={handleConversationUpdate}
          onNewIssue={() => setShowNewIssue(true)}
        />
      ) : (
        <TicketDashboard />
      )}

      {showNewIssue && (
        <NewIssueForm
          onSubmit={handleNewIssue}
          onClose={() => setShowNewIssue(false)}
        />
      )}
    </div>
  )
}
