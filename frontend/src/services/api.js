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

  // Patients & Medication History (SIH PS 26047)
  getPatients: (search = '', skip = 0, limit = 50) => {
    const params = new URLSearchParams();
    if (search) params.append('search', search);
    params.append('skip', skip.toString());
    params.append('limit', limit.toString());
    return fetchJSON(`/api/patients?${params.toString()}`);
  },
  getDemoPatients: () => fetchJSON('/api/patients/demo/list'),
  getPatientById: (patientId) => fetchJSON(`/api/patients/${patientId}`),
  createPatient: (patientData) =>
    fetchJSON('/api/patients', {
      method: 'POST',
      body: JSON.stringify(patientData),
    }),
  updatePatient: (patientId, updateData) =>
    fetchJSON(`/api/patients/${patientId}`, {
      method: 'PUT',
      body: JSON.stringify(updateData),
    }),
  deletePatient: (patientId) =>
    fetchJSON(`/api/patients/${patientId}`, { method: 'DELETE' }),
  addPatientMedication: (patientId, medData) =>
    fetchJSON(`/api/patients/${patientId}/medications`, {
      method: 'POST',
      body: JSON.stringify(medData),
    }),
  removePatientMedication: (patientId, medId) =>
    fetchJSON(`/api/patients/${patientId}/medications/${medId}`, { method: 'DELETE' }),
  screenPatientMedications: (patientId) =>
    fetchJSON(`/api/patients/${patientId}/screen-medications`, { method: 'POST' }),
  getPatientSafetySummary: (patientId) =>
    fetchJSON(`/api/patients/${patientId}/safety-summary`),

  // Medical Documents & OCR Intake (SIH PS 26047)
  uploadDocument: async (file, patientId = '') => {
    const url = `${API_BASE}/api/documents/upload`;
    const formData = new FormData();
    formData.append('file', file);
    if (patientId) formData.append('patient_id', patientId);

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      let errorDetail = `Upload failed with status ${response.status}`;
      try {
        const errJson = await response.json();
        if (errJson.detail) errorDetail = errJson.detail;
      } catch {}
      throw new Error(errorDetail);
    }
    return await response.json();
  },
  loadDemoSamplePrescription: async (patientId = 'DEMO-PT-1001') => {
    const url = `${API_BASE}/api/documents/demo-sample`;
    const formData = new FormData();
    formData.append('patient_id', patientId);

    const response = await fetch(url, {
      method: 'POST',
      body: formData,
    });
    if (!response.ok) {
      let errorDetail = `Demo sample load failed`;
      try {
        const errJson = await response.json();
        if (errJson.detail) errorDetail = errJson.detail;
      } catch {}
      throw new Error(errorDetail);
    }
    return await response.json();
  },
  getDocumentById: (docId) => fetchJSON(`/api/documents/${docId}`),
  getPatientDocuments: (patientId) => fetchJSON(`/api/documents/patient/${patientId}`),
  confirmMedications: (docId, patientId, medications) =>
    fetchJSON(`/api/documents/${docId}/confirm-medications`, {
      method: 'POST',
      body: JSON.stringify({ patient_id: patientId, medications }),
    }),
};
