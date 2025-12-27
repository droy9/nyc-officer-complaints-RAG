import { useState, useRef, useEffect } from 'react'
import { Send, FileText, AlertCircle } from 'lucide-react'
import Logo from './Logo'

const ChatInterface = ({ messages, isLoading, error, onSubmit, documentsCount }) => {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef(null)
  const textareaRef = useRef(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto'
      textareaRef.current.style.height = Math.min(textareaRef.current.scrollHeight, 200) + 'px'
    }
  }, [input])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return
    onSubmit(input)
    setInput('')
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <div className="chat-interface">
      <div className="messages-container">
        {messages.length === 0 && !isLoading ? (
          <div className="welcome-screen">
            <Logo size={80} />
            <h2>What would you like to explore?</h2>
            <p>
              Ask questions about your uploaded documents. The system will analyze 
              and cross-reference your corpus to provide informed responses.
            </p>
            {documentsCount > 0 ? (
              <div className="welcome-status ready">
                <FileText size={16} />
                <span>{documentsCount} document{documentsCount !== 1 ? 's' : ''} ready for analysis</span>
              </div>
            ) : (
              <div className="welcome-status empty">
                <FileText size={16} />
                <span>Upload documents to begin</span>
              </div>
            )}
          </div>
        ) : (
          <div className="messages">
            {messages.map((message, index) => (
              <div key={index} className={`message message-${message.role}`}>
                {message.role === 'assistant' && (
                  <div className="message-avatar">
                    <Logo size={24} />
                  </div>
                )}
                <div className="message-content">
                  <div className="message-text">
                    {message.content.split('\n').map((line, i) => (
                      <p key={i}>{line || '\u00A0'}</p>
                    ))}
                  </div>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message message-assistant">
                <div className="message-avatar">
                  <Logo size={24} spinning />
                </div>
                <div className="message-content">
                  <div className="loading-indicator">
                    <span>Analyzing documents</span>
                    <span className="loading-dots">
                      <span>.</span><span>.</span><span>.</span>
                    </span>
                  </div>
                </div>
              </div>
            )}
            
            {error && (
              <div className="message message-error">
                <AlertCircle size={20} />
                <span>{error}</span>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <form className="input-form" onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <textarea
            ref={textareaRef}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about your documents..."
            rows={1}
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="btn btn-send"
            disabled={!input.trim() || isLoading}
            aria-label="Send message"
          >
            <Send size={20} />
          </button>
        </div>
        <p className="input-hint">
          Press Enter to send, Shift+Enter for new line
        </p>
      </form>
    </div>
  )
}

export default ChatInterface

