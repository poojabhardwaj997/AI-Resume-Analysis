import axios from 'axios';
import { supabase } from './supabaseClient';

// Public frontend environment variable in Vite
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000, // 45 seconds for LLM analysis operations
});

// Request interceptor to automatically attach authenticated Supabase JWT
apiClient.interceptors.request.use(
  async (config) => {
    try {
      const { data: { session } } = await supabase.auth.getSession();
      if (session?.access_token) {
        config.headers.Authorization = `Bearer ${session.access_token}`;
      }
    } catch (err) {
      console.warn('[API Client] Failed to attach Supabase session token:', err);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for consistent error handling
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    let friendlyMessage = 'An unexpected error occurred while communicating with the backend server.';
    
    if (error.response) {
      // Backend returned HTTP error status (4xx, 5xx)
      const data = error.response.data;
      friendlyMessage = data?.detail || data?.message || `Server returned error (${error.response.status})`;
    } else if (error.request) {
      // No response received from server
      friendlyMessage = 'Unable to connect to the FastAPI backend. Please check if the backend server is running on ' + API_BASE_URL;
    } else {
      friendlyMessage = error.message;
    }

    console.error('[API Error]:', friendlyMessage);
    return Promise.reject(new Error(friendlyMessage));
  }
);

export const apiService = {
  // Health check endpoint
  checkHealth: () => apiClient.get('/api/health'),

  // Upload resume file (PDF/DOCX)
  uploadResume: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return apiClient.post('/api/resumes/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Analyze job description text
  analyzeJob: (jobData) => apiClient.post('/api/job/analyze', jobData),

  // Full unified analysis: upload file + JD text
  createAnalysis: (file, jobDescriptionText, jobTitle = '', companyName = '') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('job_description_text', jobDescriptionText);
    if (jobTitle) formData.append('job_title', jobTitle);
    if (companyName) formData.append('company_name', companyName);
    
    return apiClient.post('/api/analysis/create', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Get specific analysis by ID
  getAnalysis: (analysisId) => apiClient.get(`/api/analysis/${analysisId}`),

  // Get user-scoped analysis history
  getHistory: () => apiClient.get('/api/analysis/history'),

  // Delete analysis by ID
  deleteAnalysis: (analysisId) => apiClient.delete(`/api/analysis/${analysisId}`),
};

export default apiService;
