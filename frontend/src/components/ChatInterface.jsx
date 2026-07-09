import React, { useState, useRef, useEffect, useCallback } from 'react'
import {
  Car, Send, CheckCircle, XCircle, AlertTriangle,
  Ticket, Bot, Zap, MessageSquare
} from 'lucide-react'
import MessageBubble from './MessageBubble'
import { sendMessage, resolveConversation, escalateConversation } from '../services/api'

/**
 * Main chat interface with message streaming, input, and resolution controls.
 */
export default function ChatInterface({
  conversation,
  onConversationUpdate,
  onNewIssue,
}) {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const [streamingContent, setStreamingContent] = useState('')
  const [showResolution, setShowResolution] = useState(false)
  const [resolving, setResolving] = useState(false)
  const [escalatedTicket, setEscalatedTicket] = useState(null)
  const messagesEndRef = useRef(null)
  const inputRef = useRef(null)
  const doneCalledRef = useRef(false)

  // Load messages when conversation changes
  useEffect(() => {
    if (conversation?.messages) {
      setMessages(conversation.messages)
      setShowResolution(false)
      setStreamingContent('')
      setIsStreaming(false)
      setEscalatedTicket(null)
      doneCalledRef.current = false

      // Check if we should show resolution bar
      const msgs = conversation.messages
      if (
        msgs.length > 0 &&
        msgs[msgs.length - 1].role === 'assistant' &&
        conversation.status === 'active'
      ) {
        setShowResolution(true)
      }

      // If this is a new conversation with only a user message, auto-send first AI response
      if (msgs.length === 1 && msgs[0].role === 'user' && conversation.status === 'active') {
        triggerAIResponse(conversation.id, conversation.issue_description)
      }
    }
  }, [conversation?.id])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, streamingContent])

  const triggerAIResponse = useCallback(async (convId, content) => {
    setIsStreaming(true)
    setShowResolution(false)
    setStreamingContent('')
    doneCalledRef.current = false

    await sendMessage(
      convId,
      content,
      // onChunk
      (chunk) => {
        setStreamingContent((prev) => prev + chunk)
      },
      // onDone
      () => {
        if (doneCalledRef.current) return
        doneCalledRef.current = true
        setIsStreaming(false)
        setStreamingContent((finalContent) => {
          if (finalContent) {
            setMessages((prev) => [
              ...prev,
              {
                id: `ai-${Date.now()}`,
                role: 'assistant',
                content: finalContent,
                created_at: new Date().toISOString(),
              },
            ])
          }
          return ''
        })
        setShowResolution(true)
      },
      // onError
      (error) => {
        console.error('Streaming error:', error)
        setIsStreaming(false)
        setStreamingContent('')
      }
    )
  }, [])

  const handleSendMessage = async (e) => {
    e.preventDefault()
    if (!inputValue.trim() || isStreaming || !conversation) return

    const content = inputValue.trim()
    setInputValue('')
    setShowResolution(false)

    // Add user message locally
    const userMsg = {
      id: `user-${Date.now()}`,
      role: 'user',
      content,
      created_at: new Date().toISOString(),
    }
    setMessages((prev) => [...prev, userMsg])

    // Trigger AI response (the sendMessage API call also saves the user message)
    triggerAIResponse(conversation.id, content)
  }

  const handleResolve = async () => {
    if (!conversation) return
    setResolving(true)
    try {
      await resolveConversation(conversation.id)
      onConversationUpdate?.()
    } catch (err) {
      console.error('Failed to resolve:', err)
    } finally {
      setResolving(false)
    }
  }

  const handleEscalate = async () => {
    if (!conversation) return
    setResolving(true)
    try {
      const result = await escalateConversation(conversation.id)
      setEscalatedTicket(result.ticket)
      setShowResolution(false)
      onConversationUpdate?.()
    } catch (err) {
      console.error('Failed to escalate:', err)
    } finally {
      setResolving(false)
    }
  }

  // Empty state — no conversation selected
  if (!conversation) {
    return (
      <div className="main-content">
        <div className="empty-state">
          <div className="empty-state-icon">
            <Zap size={36} />
          </div>
          <h2>Welcome to Optimotion Support</h2>
          <p>
            Our AI assistant can help troubleshoot issues with your electric vehicle.
            Click "Report an Issue" to get started.
          </p>
          <button
            className="btn-primary"
            onClick={onNewIssue}
            style={{ marginTop: '24px' }}
          >
            <MessageSquare size={18} />
            Report an Issue
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="main-content">
      {/* Header */}
      <div className="chat-header">
        <div className="chat-header-info">
          <div className="chat-header-icon">
            <Car size={20} />
          </div>
          <div className="chat-header-text">
            <h2>Vehicle {conversation.vehicle_id}</h2>
            <p>
              {conversation.category && (
                <span className="category-badge" style={{ marginRight: '8px' }}>
                  {conversation.category}
                </span>
              )}
              <span className={`status-badge ${conversation.status}`}>
                {conversation.status}
              </span>
            </p>
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="chat-messages">
        {messages.map((msg) => (
          <MessageBubble key={msg.id} role={msg.role} content={msg.content} />
        ))}

        {/* Streaming message */}
        {isStreaming && streamingContent && (
          <MessageBubble role="assistant" content={streamingContent} isStreaming />
        )}

        {/* Typing indicator */}
        {isStreaming && !streamingContent && (
          <div className="message assistant">
            <div className="message-avatar" style={{
              background: 'var(--accent-gradient)',
              color: 'var(--text-inverse)',
            }}>
              <Bot size={16} />
            </div>
            <div className="message-content" style={{ background: 'var(--bg-elevated)', border: '1px solid var(--border-primary)' }}>
              <div className="typing-indicator">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
              </div>
            </div>
          </div>
        )}

        {/* Escalated ticket info */}
        {escalatedTicket && (
          <div className="ticket-info-card">
            <h3>
              <Ticket size={16} />
              Service Ticket Created
            </h3>
            <p><strong>Title:</strong> {escalatedTicket.title}</p>
            <p><strong>Priority:</strong>{' '}
              <span className={`priority-badge ${escalatedTicket.priority}`}>
                {escalatedTicket.priority}
              </span>
            </p>
            <p><strong>Category:</strong>{' '}
              <span className="category-badge">{escalatedTicket.category}</span>
            </p>
            <p className="ticket-id">Ticket ID: {escalatedTicket.id}</p>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Status Banners */}
      {conversation.status === 'resolved' && (
        <div className="status-banner resolved">
          <CheckCircle size={18} />
          Issue resolved! Glad we could help.
        </div>
      )}

      {conversation.status === 'escalated' && !escalatedTicket && (
        <div className="status-banner escalated">
          <AlertTriangle size={18} />
          This issue has been escalated to a service ticket.
        </div>
      )}

      {/* Resolution Bar */}
      {showResolution && conversation.status === 'active' && !isStreaming && (
        <div className="resolution-bar">
          <p>Did this resolve your issue?</p>
          <button
            className="btn-resolve yes"
            onClick={handleResolve}
            disabled={resolving}
          >
            <CheckCircle size={16} />
            Yes, Resolved
          </button>
          <button
            className="btn-resolve no"
            onClick={handleEscalate}
            disabled={resolving}
          >
            <XCircle size={16} />
            No, Create Ticket
          </button>
        </div>
      )}

      {/* Input Area */}
      {conversation.status === 'active' && (
        <div className="chat-input-area">
          <form className="chat-input-wrapper" onSubmit={handleSendMessage}>
            <textarea
              ref={inputRef}
              className="chat-input"
              placeholder="Describe what's happening or follow up..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault()
                  handleSendMessage(e)
                }
              }}
              disabled={isStreaming}
              rows={1}
            />
            <button
              type="submit"
              className="btn-send"
              disabled={!inputValue.trim() || isStreaming}
              aria-label="Send message"
            >
              <Send size={18} />
            </button>
          </form>
        </div>
      )}
    </div>
  )
}
