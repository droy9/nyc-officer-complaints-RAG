import { useState, useCallback, useEffect } from 'react'
import Sidebar from './components/Sidebar'
import ChatInterface from './components/ChatInterface'
import DocumentUpload from './components/DocumentUpload'
import Logo from './components/Logo'

function App() {
  const [messages, setMessages] = useState([])
  const [documents, setDocuments] = useState([])
  const [chatHistory, setChatHistory] = useState([])
  const [currentChatId, setCurrentChatId] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [showUpload, setShowUpload] = useState(false)

  // Load existing documents on mount
  useEffect(() => {
    const loadDocuments = async () => {
      try {
        const response = await fetch('/api/documents')
        if (response.ok) {
          const data = await response.json()
          const docs = data.documents.map(doc => ({
            id: doc.document_id,
            name: doc.filename,
            size: doc.char_count,
            chunks: doc.chunks,
            status: doc.status,
            uploadedAt: new Date()
          }))
          setDocuments(docs)
        }
      } catch (err) {
        console.log('Could not load documents:', err)
      }
    }
    loadDocuments()
  }, [])

  const handleNewChat = useCallback(() => {
    if (messages.length > 0) {
      const chatSummary = messages[0]?.content?.slice(0, 50) + '...' || 'New conversation'
      setChatHistory(prev => [
        { id: Date.now(), title: chatSummary, messages: messages, date: new Date() },
        ...prev
      ])
    }
    setMessages([])
    setCurrentChatId(Date.now())
    setError(null)
  }, [messages])

  const handleSelectChat = useCallback((chat) => {
    setMessages(chat.messages)
    setCurrentChatId(chat.id)
    setError(null)
  }, [])

  const handleSubmit = useCallback(async (query) => {
    if (!query.trim()) return

    const userMessage = { role: 'user', content: query }
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    setError(null)

    try {
      const response = await fetch('/api/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, k: 4 })
      })

      const data = await response.json()
      
      if (!response.ok || !data.success) {
        throw new Error(data.error || 'Failed to get response')
      }

      // Format response with citations
      let answerText = data.answer
      if (data.citations && data.citations.length > 0) {
        answerText += '\n\n---\n**Sources:**\n'
        data.citations.forEach(c => {
          answerText += `• ${c.filename} (chunk ${c.chunk}, relevance: ${(c.score * 100).toFixed(0)}%)\n`
        })
      }

      const assistantMessage = { role: 'assistant', content: answerText }
      setMessages(prev => [...prev, assistantMessage])
    } catch (err) {
      console.error('Query error:', err)
      setError(err.message || 'Failed to query documents')
    }

    setIsLoading(false)
  }, [])

  const handleDocumentUpload = useCallback(async (files) => {
    setShowUpload(false)
    
    for (const file of files) {
      // Add document with processing status
      const tempId = Date.now() + Math.random()
      const newDoc = {
        id: tempId,
        name: file.name,
        type: file.type,
        size: file.size,
        status: 'processing',
        uploadedAt: new Date()
      }
      
      setDocuments(prev => [...prev, newDoc])
      
      try {
        const formData = new FormData()
        formData.append('file', file)
        
        const response = await fetch('/api/upload', {
          method: 'POST',
          body: formData
        })
        
        const data = await response.json()
        
        if (!response.ok || !data.success) {
          throw new Error(data.error || 'Upload failed')
        }
        
        // Update document with server response
        setDocuments(prev => 
          prev.map(d => 
            d.id === tempId 
              ? { 
                  ...d, 
                  id: data.document.document_id,
                  status: 'ready',
                  chunks: data.document.chunks
                } 
              : d
          )
        )
      } catch (err) {
        console.error('Upload error:', err)
        // Mark as failed
        setDocuments(prev => 
          prev.map(d => 
            d.id === tempId ? { ...d, status: 'error', error: err.message } : d
          )
        )
      }
    }
  }, [])

  const handleRemoveDocument = useCallback((docId) => {
    setDocuments(prev => prev.filter(d => d.id !== docId))
  }, [])

  return (
    <div className="app">
      <Sidebar
        chatHistory={chatHistory}
        documents={documents}
        onNewChat={handleNewChat}
        onSelectChat={handleSelectChat}
        onShowUpload={() => setShowUpload(true)}
        onRemoveDocument={handleRemoveDocument}
        currentChatId={currentChatId}
      />
      
      <main className="main-content">
        <header className="header">
          <div className="header-brand">
            <Logo size={32} />
            <div className="header-text">
              <h1>Decarceration Lab</h1>
              <span className="header-subtitle">Document Study & Reference</span>
            </div>
          </div>
        </header>

        <ChatInterface
          messages={messages}
          isLoading={isLoading}
          error={error}
          onSubmit={handleSubmit}
          documentsCount={documents.filter(d => d.status === 'ready').length}
        />
      </main>

      {showUpload && (
        <DocumentUpload
          onUpload={handleDocumentUpload}
          onClose={() => setShowUpload(false)}
        />
      )}
    </div>
  )
}

export default App

