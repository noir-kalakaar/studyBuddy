import React, { useState } from 'react'
import { api } from '../api'
import './Chat.css'

function Chat() {
  const [question, setQuestion] = useState('')
  const [topK, setTopK] = useState(3)
  const [sources, setSources] = useState([])
  const [loading, setLoading] = useState(false)
  const [response, setResponse] = useState(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!question.trim()) {
      setError('Please enter a question')
      return
    }

    setLoading(true)
    setError('')
    setResponse(null)

    try {
      const result = await api.chat(
        question,
        topK,
        sources.length > 0 ? sources : null
      )
      setResponse(result)
    } catch (err) {
      setError(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  const handleSourceToggle = (source) => {
    setSources((prev) =>
      prev.includes(source)
        ? prev.filter((s) => s !== source)
        : [...prev, source]
    )
  }

  const handleFeedback = async (rating) => {
    if (!response) return

    try {
      await api.submitFeedback(
        question,
        response.answer,
        rating,
        null
      )
      alert('Feedback submitted!')
    } catch (err) {
      alert(`Error submitting feedback: ${err.message}`)
    }
  }

  return (
    <div className="chat-container">
      <h2>Chat with StudyBuddy</h2>

      <form onSubmit={handleSubmit} className="chat-form">
        <div className="form-group">
          <label htmlFor="question">Question:</label>
          <textarea
            id="question"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="Ask a question about your documents..."
            rows="3"
            disabled={loading}
          />
        </div>

        <div className="form-row">
          <div className="form-group">
            <label htmlFor="topK">Top K Results:</label>
            <input
              type="number"
              id="topK"
              value={topK}
              onChange={(e) => setTopK(parseInt(e.target.value) || 3)}
              min="1"
              max="10"
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Filter by Source (optional):</label>
            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes('user')}
                  onChange={() => handleSourceToggle('user')}
                  disabled={loading}
                />
                User
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={sources.includes('wikipedia')}
                  onChange={() => handleSourceToggle('wikipedia')}
                  disabled={loading}
                />
                Wikipedia
              </label>
            </div>
          </div>
        </div>

        <button type="submit" disabled={loading} className="submit-btn">
          {loading ? 'Thinking...' : 'Ask Question'}
        </button>
      </form>

      {error && <div className="message error">{error}</div>}

      {response && (
        <div className="response-container">
          <div className="answer-section">
            <h3>Answer:</h3>
            <p className="answer-text">{response.answer}</p>
            <div className="feedback-buttons">
              <button
                onClick={() => handleFeedback(1)}
                className="feedback-btn positive"
              >
                👍 Helpful
              </button>
              <button
                onClick={() => handleFeedback(-1)}
                className="feedback-btn negative"
              >
                👎 Not Helpful
              </button>
            </div>
          </div>

          {response.context && response.context.length > 0 && (
            <div className="context-section">
              <h3>Sources ({response.context.length}):</h3>
              <div className="context-list">
                {response.context.map((chunk, idx) => (
                  <div key={idx} className="context-item">
                    <div className="context-header">
                      <span className="context-source">{chunk.source}</span>
                      <span className="context-title">{chunk.meta.title}</span>
                      {chunk.score !== undefined && (
                        <span className="context-score">
                          Score: {chunk.score.toFixed(3)}
                        </span>
                      )}
                    </div>
                    <p className="context-text">{chunk.text}</p>
                    {chunk.meta.url && (
                      <a
                        href={chunk.meta.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="context-url"
                      >
                        View source
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default Chat

