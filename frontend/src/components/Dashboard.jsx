import React, { useState, useEffect } from 'react'
import { api } from '../api'
import './Dashboard.css'

function Dashboard() {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await api.getStats()
      setStats(data)
    } catch (err) {
      setError(`Error: ${err.message}`)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="dashboard-container">
        <h2>Dashboard</h2>
        <div className="loading">Loading statistics...</div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dashboard-container">
        <h2>Dashboard</h2>
        <div className="message error">{error}</div>
        <button onClick={loadStats} className="retry-btn">
          Retry
        </button>
      </div>
    )
  }

  if (!stats) {
    return (
      <div className="dashboard-container">
        <h2>Dashboard</h2>
        <div className="message">No statistics available</div>
      </div>
    )
  }

  const positivePercentage =
    stats.total_feedback > 0
      ? ((stats.positive_feedback / stats.total_feedback) * 100).toFixed(1)
      : 0

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <button onClick={loadStats} className="refresh-btn">
          🔄 Refresh
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-icon">📚</div>
          <div className="stat-value">{stats.total_questions}</div>
          <div className="stat-label">Total Questions</div>
        </div>

        <div className="stat-card">
          <div className="stat-icon">💬</div>
          <div className="stat-value">{stats.total_feedback}</div>
          <div className="stat-label">Total Feedback</div>
        </div>

        <div className="stat-card positive">
          <div className="stat-icon">👍</div>
          <div className="stat-value">{stats.positive_feedback}</div>
          <div className="stat-label">Positive Feedback</div>
        </div>

        <div className="stat-card negative">
          <div className="stat-icon">👎</div>
          <div className="stat-value">{stats.negative_feedback}</div>
          <div className="stat-label">Negative Feedback</div>
        </div>
      </div>

      {stats.total_feedback > 0 && (
        <div className="feedback-summary">
          <h3>Feedback Summary</h3>
          <div className="progress-bar">
            <div
              className="progress-fill"
              style={{ width: `${positivePercentage}%` }}
            >
              {positivePercentage}% Positive
            </div>
          </div>
          <div className="summary-text">
            {positivePercentage}% of feedback is positive
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard

