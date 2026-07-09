import React from 'react'
import ReactMarkdown from 'react-markdown'
import { Bot, User } from 'lucide-react'

/**
 * Renders a single chat message bubble (user or assistant).
 * AI messages are rendered with Markdown support.
 */
export default function MessageBubble({ role, content, isStreaming }) {
  const isUser = role === 'user'

  return (
    <div className={`message ${role}`}>
      <div className="message-avatar">
        {isUser ? <User size={16} /> : <Bot size={16} />}
      </div>
      <div className="message-content">
        {isUser ? (
          <p>{content}</p>
        ) : (
          <>
            <ReactMarkdown
              components={{
                // Override default element rendering for cleaner output
                h1: ({ children }) => <h2>{children}</h2>,
                h2: ({ children }) => <h2>{children}</h2>,
                h3: ({ children }) => <h3>{children}</h3>,
                a: ({ href, children }) => (
                  <a href={href} target="_blank" rel="noopener noreferrer">
                    {children}
                  </a>
                ),
              }}
            >
              {content}
            </ReactMarkdown>
            {isStreaming && <span className="streaming-cursor" />}
          </>
        )}
      </div>
    </div>
  )
}
