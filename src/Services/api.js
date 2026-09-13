import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_URL || "http://192.168.1.87:8000";

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
  try {
    const response = await api.get("/");

    return response.data;
  } catch (error) {
    console.error("Server health check failed:", error);
    throw error;
  }
};

// --------------------------------------------------
// Authentication
// --------------------------------------------------

export const loginUser = async (credentials) => {
  try {
    const response = await api.post("/login", credentials);

    return response.data;
  } catch (error) {
    console.error("Login failed:", error);
    throw error;
  }
};

// --------------------------------------------------
// Spill Detection
// --------------------------------------------------

export const detectSpill = async (formData) => {
  try {
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
  } catch (error) {
    console.error("Spill detection failed:", error);
    throw error;
  }
};

// --------------------------------------------------
// Spill Analysis
// --------------------------------------------------

export const analyzeSpill = async (payload) => {
  try {
    const response = await api.post(
      "/analyze-spill",
      payload
    );

    return response.data;
  } catch (error) {
    console.error("Spill analysis failed:", error);
    throw error;
  }
};

// --------------------------------------------------
// Drift Prediction
// --------------------------------------------------

export const predictDrift = async (payload) => {
  try {
    const response = await api.post(
      "/predict-drift",
      payload
    );

    return response.data;
  } catch (error) {
    console.error("Drift prediction failed:", error);
    throw error;
  }
};

// --------------------------------------------------
// Vessel Attribution
// --------------------------------------------------

export const attributeVessels = async (payload) => {
  try {
    const response = await api.post(
      "/vessel-attribution",
      payload
    );

    return response.data;
  } catch (error) {
    console.error("Vessel attribution failed:", error);
    throw error;
  }
};

// --------------------------------------------------
// AIS Vessel Search
// --------------------------------------------------

export const searchVessels = async (params = {}) => {
  try {
    const response = await api.get(
      "/vessels",
      {
        params,
      }
    );

    return response.data;
  } catch (error) {
    console.error("Vessel search failed:", error);
    throw error;
  }
};

// --------------------------------------------------
// Reports
// --------------------------------------------------

export const generateReport = async (payload) => {
  try {
    const response = await api.post(
      "/reports/generate",
      payload
    );

    return response.data;
  } catch (error) {
    console.error("Report generation failed:", error);
    throw error;
  }
};

export const getRemoteReports = async () => {
  try {
    const response = await api.get("/reports");

    return response.data;
  } catch (error) {
    console.error("Fetching reports failed:", error);
    throw error;
  }
};

export const getRemoteReportById = async (id) => {
  try {
    const response = await api.get(
      `/reports/${id}`
    );

    return response.data;
  } catch (error) {
    console.error("Fetching report failed:", error);
    throw error;
  }
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