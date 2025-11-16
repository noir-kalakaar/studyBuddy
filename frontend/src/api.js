const API_BASE_URL = 'http://localhost:8000';

export const api = {
  async uploadText(title, text, source = 'user') {
    const response = await fetch(`${API_BASE_URL}/api/upload-text`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ title, text, source }),
    });
    if (!response.ok) {
      throw new Error('Failed to upload text');
    }
    return response.json();
  },

  async importWiki(query) {
    const response = await fetch(`${API_BASE_URL}/api/import-wiki`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });
    if (!response.ok) {
      throw new Error('Failed to import Wikipedia article');
    }
    return response.json();
  },

  async chat(question, topK = 3, sources = null) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question, top_k: topK, sources }),
    });
    if (!response.ok) {
      throw new Error('Failed to get chat response');
    }
    return response.json();
  },

  async submitFeedback(question, answer, rating, comment = null) {
    const response = await fetch(`${API_BASE_URL}/api/feedback`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ question, answer, rating, comment }),
    });
    if (!response.ok) {
      throw new Error('Failed to submit feedback');
    }
    return response.json();
  },

  async getStats() {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    if (!response.ok) {
      throw new Error('Failed to get stats');
    }
    return response.json();
  },
};

