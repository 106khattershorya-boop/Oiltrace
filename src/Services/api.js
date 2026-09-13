import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("oceanwatch_token");

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    return config;
  },
  (error) => Promise.reject(error)
);

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("oceanwatch_token");
      localStorage.removeItem("isLoggedIn");
    }

    return Promise.reject(error);
  }
);

// --------------------------------------------------
// Health
// --------------------------------------------------

export const checkServerHealth = async () => {
  const response = await api.get("/");
  return response.data;
};

// --------------------------------------------------
// Authentication
// --------------------------------------------------

export const loginUser = async (credentials) => {
  const response = await api.post("/login", credentials);
  return response.data;
};

// --------------------------------------------------
// Incident APIs
// --------------------------------------------------

export const getIncident = async (incidentId = 1) => {
  const response = await api.get(`/incidents/${incidentId}`);
  return response.data;
};

export const getIncidentCandidates = async (incidentId = 1) => {
  const response = await api.get(
    `/incidents/${incidentId}/candidates`
  );
  return response.data;
};

export const getIncidentEvidence = async (incidentId = 1) => {
  const response = await api.get(
    `/incidents/${incidentId}/evidence`
  );
  return response.data;
};

export const getIncidentInvestigation = async (
  incidentId = 1
) => {
  const response = await api.get(
    `/incidents/${incidentId}/investigation`
  );
  return response.data;
};

// --------------------------------------------------
// Vessel APIs
// --------------------------------------------------

export const getVesselBehaviour = async (mmsi) => {
  const response = await api.get(
    `/vessels/${mmsi}/behaviour`
  );
  return response.data;
};

export const searchVessels = async (params = {}) => {
  const response = await api.get("/vessels", {
    params,
  });

  return response.data;
};

// --------------------------------------------------
// Existing compatibility APIs
// --------------------------------------------------

export const detectSpill = async (formData) => {
  const response = await api.post(
    "/detect-spill",
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );

  return response.data;
};

export const analyzeSpill = async (payload) => {
  const response = await api.post(
    "/analyze-spill",
    payload
  );

  return response.data;
};

export const predictDrift = async (payload) => {
  const response = await api.post(
    "/predict-drift",
    payload
  );

  return response.data;
};

export const attributeVessels = async (payload) => {
  const response = await api.post(
    "/vessel-attribution",
    payload
  );

  return response.data;
};

// --------------------------------------------------
// Reports
// --------------------------------------------------

export const generateReport = async (payload) => {
  const response = await api.post(
    "/reports/generate",
    payload
  );

  return response.data;
};

export const getRemoteReports = async () => {
  const response = await api.get("/reports");
  return response.data;
};

export const getRemoteReportById = async (id) => {
  const response = await api.get(`/reports/${id}`);
  return response.data;
};

// --------------------------------------------------
// Generic API helpers
// --------------------------------------------------

export const getRequest = async (url, config = {}) => {
  const response = await api.get(url, config);
  return response.data;
};

export const postRequest = async (
  url,
  data = {},
  config = {}
) => {
  const response = await api.post(
    url,
    data,
    config
  );

  return response.data;
};

export const putRequest = async (
  url,
  data = {},
  config = {}
) => {
  const response = await api.put(
    url,
    data,
    config
  );

  return response.data;
};

export const deleteRequest = async (
  url,
  config = {}
) => {
  const response = await api.delete(
    url,
    config
  );

  return response.data;
};

export default api;