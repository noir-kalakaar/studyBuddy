const API_BASE_URL = 'http://localhost:8000';

const buildError = async (response) => {
  let message = `Request failed with status ${response.status}`;
  try {
    const data = await response.json();
    if (typeof data === 'string') {
      message = data;
    } else if (data.detail) {
      message = data.detail;
    } else if (data.error) {
      message = data.error;
    }
  } catch (err) {
    // ignore JSON parse errors
  }
  throw new Error(message);
};

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
      await buildError(response);
    }
    return response.json();
  },

  async uploadPdf(title, file) {
    const formData = new FormData();
    formData.append('title', title);
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/upload-pdf`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      await buildError(response);
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
      await buildError(response);
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
      await buildError(response);
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
      await buildError(response);
    }
    return response.json();
  },

  async getStats() {
    const response = await fetch(`${API_BASE_URL}/api/stats`);
    if (!response.ok) {
      await buildError(response);
    }
    return response.json();
  },
};

