import { useState, useCallback } from 'react'
import { Upload, X, FileText, AlertCircle } from 'lucide-react'

const ACCEPTED_TYPES = {
  'application/pdf': '.pdf',
  'text/plain': '.txt',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '.docx',
  'application/msword': '.doc'
}

const DocumentUpload = ({ onUpload, onClose }) => {
  const [isDragging, setIsDragging] = useState(false)
  const [files, setFiles] = useState([])
  const [error, setError] = useState(null)

  const validateFile = (file) => {
    if (!Object.keys(ACCEPTED_TYPES).includes(file.type)) {
      return `${file.name} is not a supported file type`
    }
    if (file.size > 50 * 1024 * 1024) {
      return `${file.name} exceeds 50MB limit`
    }
    return null
  }

  const handleFiles = useCallback((fileList) => {
    const validFiles = []
    let errorMsg = null

    Array.from(fileList).forEach(file => {
      const err = validateFile(file)
      if (err) {
        errorMsg = err
      } else {
        validFiles.push(file)
      }
    })

    if (errorMsg) {
      setError(errorMsg)
    } else {
      setError(null)
    }

    setFiles(prev => [...prev, ...validFiles])
  }, [])

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    handleFiles(e.dataTransfer.files)
  }

  const handleInputChange = (e) => {
    handleFiles(e.target.files)
  }

  const removeFile = (index) => {
    setFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleUpload = () => {
    if (files.length > 0) {
      onUpload(files)
    }
  }

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>Upload Documents</h2>
          <button className="btn btn-ghost btn-icon" onClick={onClose}>
            <X size={20} />
          </button>
        </div>

        <div className="modal-body">
          <div 
            className={`upload-zone ${isDragging ? 'dragging' : ''}`}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <input
              type="file"
              id="file-input"
              multiple
              accept=".pdf,.txt,.docx,.doc"
              onChange={handleInputChange}
              className="upload-input"
            />
            <label htmlFor="file-input" className="upload-label">
              <Upload size={40} />
              <span className="upload-title">
                Drop files here or <strong>browse</strong>
              </span>
              <span className="upload-subtitle">
                Supports PDF, TXT, DOCX up to 50MB
              </span>
            </label>
          </div>

          {error && (
            <div className="upload-error">
              <AlertCircle size={16} />
              <span>{error}</span>
            </div>
          )}

          {files.length > 0 && (
            <ul className="upload-files">
              {files.map((file, index) => (
                <li key={index} className="upload-file">
                  <FileText size={18} />
                  <span className="upload-file-name">{file.name}</span>
                  <span className="upload-file-size">
                    {(file.size / 1024).toFixed(1)} KB
                  </span>
                  <button 
                    className="btn btn-ghost btn-icon"
                    onClick={() => removeFile(index)}
                  >
                    <X size={14} />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>

        <div className="modal-footer">
          <button className="btn btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button 
            className="btn btn-primary"
            onClick={handleUpload}
            disabled={files.length === 0}
          >
            Upload {files.length > 0 && `(${files.length})`}
          </button>
        </div>
      </div>
    </div>
  )
}

export default DocumentUpload

