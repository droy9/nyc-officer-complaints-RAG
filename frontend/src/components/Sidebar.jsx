import { Plus, FileText, Trash2, MessageSquare, Upload } from 'lucide-react'

const Sidebar = ({ 
  chatHistory, 
  documents, 
  onNewChat, 
  onSelectChat, 
  onShowUpload,
  onRemoveDocument,
  currentChatId 
}) => {
  const formatDate = (date) => {
    const d = new Date(date)
    const now = new Date()
    const diff = now - d
    
    if (diff < 86400000) {
      return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    if (diff < 604800000) {
      return d.toLocaleDateString([], { weekday: 'short' })
    }
    return d.toLocaleDateString([], { month: 'short', day: 'numeric' })
  }

  const formatSize = (bytes) => {
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / 1048576).toFixed(1) + ' MB'
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <button className="btn btn-primary btn-full" onClick={onNewChat}>
          <Plus size={18} />
          <span>New Query</span>
        </button>
      </div>

      <div className="sidebar-section">
        <div className="sidebar-header">
          <h3>Documents</h3>
          <button className="btn btn-ghost btn-sm" onClick={onShowUpload}>
            <Upload size={16} />
          </button>
        </div>
        
        {documents.length === 0 ? (
          <div className="sidebar-empty">
            <FileText size={24} />
            <p>No documents uploaded</p>
            <button className="btn btn-ghost btn-sm" onClick={onShowUpload}>
              Upload files
            </button>
          </div>
        ) : (
          <ul className="document-list">
            {documents.map(doc => (
              <li key={doc.id} className={`document-item ${doc.status}`}>
                <div className="document-icon">
                  <FileText size={16} />
                  {doc.status === 'processing' && (
                    <span className="document-processing" />
                  )}
                </div>
                <div className="document-info">
                  <span className="document-name">{doc.name}</span>
                  <span className="document-meta">
                    {formatSize(doc.size)} • {doc.status === 'ready' ? 'Ready' : 'Processing...'}
                  </span>
                </div>
                <button 
                  className="btn btn-ghost btn-icon"
                  onClick={() => onRemoveDocument(doc.id)}
                  aria-label="Remove document"
                >
                  <Trash2 size={14} />
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="sidebar-section sidebar-section-grow">
        <div className="sidebar-header">
          <h3>History</h3>
        </div>
        
        {chatHistory.length === 0 ? (
          <div className="sidebar-empty">
            <MessageSquare size={24} />
            <p>No previous queries</p>
          </div>
        ) : (
          <ul className="chat-history">
            {chatHistory.map(chat => (
              <li key={chat.id}>
                <button 
                  className={`chat-history-item ${currentChatId === chat.id ? 'active' : ''}`}
                  onClick={() => onSelectChat(chat)}
                >
                  <span className="chat-title">{chat.title}</span>
                  <span className="chat-date">{formatDate(chat.date)}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="sidebar-footer">
        <p>Powered by RAG</p>
      </div>
    </aside>
  )
}

export default Sidebar

