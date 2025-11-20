import React, { useRef, useState } from 'react'
import { api } from '../api'
import './Upload.css'

function Upload() {
  const [textTitle, setTextTitle] = useState('')
  const [pdfTitle, setPdfTitle] = useState('')
  const [text, setText] = useState('')
  const [source, setSource] = useState('user')
  const [wikiQuery, setWikiQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [pdfFile, setPdfFile] = useState(null)
  const pdfInputRef = useRef(null)

  const handleTextUpload = async (e) => {
    e.preventDefault()
    if (!textTitle.trim() || !text.trim()) {
      setMessage('Please fill in both title and text')
      return
    }

    setLoading(true)
    setMessage('')
    try {
      await api.uploadText(textTitle, text, source)
      setMessage('Text uploaded successfully!')
      setTextTitle('')
      setText('')
    } catch (error) {
      setMessage(`Error: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handlePdfUpload = async (e) => {
    e.preventDefault()
    if (!pdfTitle.trim() || !pdfFile) {
      setMessage('Please provide a title and select a PDF file')
      return
    }

    setLoading(true)
    setMessage('')
    try {
      await api.uploadPdf(pdfTitle, pdfFile)
      setMessage('PDF uploaded and processed successfully!')
      setPdfTitle('')
      setPdfFile(null)
      if (pdfInputRef.current) {
        pdfInputRef.current.value = ''
      }
    } catch (error) {
      setMessage(`Error: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleWikiImport = async (e) => {
    e.preventDefault()
    if (!wikiQuery.trim()) {
      setMessage('Please enter a Wikipedia query')
      return
    }

    setLoading(true)
    setMessage('')
    try {
      const result = await api.importWiki(wikiQuery)
      setMessage(`Wikipedia article "${result.title}" imported successfully!`)
      setWikiQuery('')
    } catch (error) {
      setMessage(`Error: ${error.message}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="upload-container">
      <h2>Upload Documents</h2>
      
      <div className="upload-section">
        <h3>Upload Text</h3>
        <form onSubmit={handleTextUpload} className="upload-form">
          <div className="form-group">
            <label htmlFor="title">Title:</label>
            <input
              type="text"
              id="title"
              value={textTitle}
              onChange={(e) => setTextTitle(e.target.value)}
              placeholder="Enter document title"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="source">Source:</label>
            <select
              id="source"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              disabled={loading}
            >
              <option value="user">User</option>
              <option value="wikipedia">Wikipedia</option>
            </select>
          </div>
          <div className="form-group">
            <label htmlFor="text">Text:</label>
            <textarea
              id="text"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Enter document text"
              rows="10"
              disabled={loading}
            />
          </div>
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Uploading...' : 'Upload Text'}
          </button>
        </form>
      </div>

      <div className="upload-section">
        <h3>Upload PDF</h3>
        <form onSubmit={handlePdfUpload} className="upload-form">
          <div className="form-group">
            <label htmlFor="pdf-title">Title:</label>
            <input
              type="text"
              id="pdf-title"
              value={pdfTitle}
              onChange={(e) => setPdfTitle(e.target.value)}
              placeholder="Enter document title"
              disabled={loading}
            />
          </div>
          <div className="form-group">
            <label htmlFor="pdf-file">PDF File:</label>
            <input
              type="file"
              id="pdf-file"
              accept="application/pdf"
              onChange={(e) => setPdfFile(e.target.files[0] || null)}
              ref={pdfInputRef}
              disabled={loading}
            />
          </div>
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Uploading...' : 'Upload PDF'}
          </button>
        </form>
      </div>

      <div className="upload-section">
        <h3>Import from Wikipedia</h3>
        <form onSubmit={handleWikiImport} className="upload-form">
          <div className="form-group">
            <label htmlFor="wiki-query">Search Query:</label>
            <input
              type="text"
              id="wiki-query"
              value={wikiQuery}
              onChange={(e) => setWikiQuery(e.target.value)}
              placeholder="Enter Wikipedia article name"
              disabled={loading}
            />
          </div>
          <button type="submit" disabled={loading} className="submit-btn">
            {loading ? 'Importing...' : 'Import from Wikipedia'}
          </button>
        </form>
      </div>

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}
    </div>
  )
}

export default Upload

