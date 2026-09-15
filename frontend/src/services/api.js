const API_BASE = import.meta.env.VITE_API_URL || '';

async function fetchJSON(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      let errorDetail = `Request failed with status ${response.status}`;
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorDetail = typeof errorData.detail === 'string' 
            ? errorData.detail 
            : JSON.stringify(errorData.detail);
        }
      } catch {
        // use default errorDetail
      }
      throw new Error(errorDetail);
    }

    return await response.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  // Health
  getHealth: () => fetchJSON('/api/health'),

  // Drugs
  searchDrugs: (q, limit = 15) => fetchJSON(`/api/drugs/search?q=${encodeURIComponent(q)}&limit=${limit}`),
  getAllDrugs: (skip = 0, limit = 100) => fetchJSON(`/api/drugs?skip=${skip}&limit=${limit}`),
  getDrugById: (id) => fetchJSON(`/api/drugs/${id}`),

  // Interaction Prediction
  checkInteraction: (drugA, drugB) =>
    fetchJSON('/api/interactions/check', {
      method: 'POST',
      body: JSON.stringify({ drug_a: drugA, drug_b: drugB }),
    }),

  // Alerts History
  getAlerts: (severity = '', search = '', skip = 0, limit = 50) => {
    const params = new URLSearchParams();
    if (severity && severity !== 'All') params.append('severity', severity);
    if (search) params.append('search', search);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return fetchJSON(`/api/alerts?${params.toString()}`);
  },
  getAlertById: (id) => fetchJSON(`/api/alerts/${id}`),
  deleteAlert: (id) => fetchJSON(`/api/alerts/${id}`, { method: 'DELETE' }),

  // Analytics & Stats
  getDashboardStats: () => fetchJSON('/api/dashboard/stats'),

  // Model Metadata
  getModelInfo: () => fetchJSON('/api/model/info'),
};
