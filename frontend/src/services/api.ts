import axios from 'axios';
import { HealthResponse, ChatRequest, ChatResponse, IngestionResult, CollectionStats, SearchRequest, SearchResponse } from '../types/api';

// Create axios instance with default configuration
const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  timeout: 30000, // 30 seconds timeout
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for logging and error handling
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error);
    
    // Handle common error scenarios
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (status === 401) {
        console.error('Unauthorized access');
      } else if (status === 404) {
        console.error('Resource not found');
      } else if (status >= 500) {
        console.error('Server error:', data);
      }
    } else if (error.request) {
      // Network error
      console.error('Network error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

export const apiService = {
  // Health check endpoints
  async getHealth(): Promise<HealthResponse> {
    const response = await api.get('/health/');
    return response.data;
  },

  async getDetailedHealth(): Promise<any> {
    const response = await api.get('/health/detailed');
    return response.data;
  },

  async getReady(): Promise<any> {
    const response = await api.get('/ready');
    return response.data;
  },

  // Chat endpoints
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await api.post('/chat/', request);
    return response.data;
  },

  async getWorkflowStatus(workflowId: string): Promise<any> {
    const response = await api.get(`/chat/status/${workflowId}`);
    return response.data;
  },

  async clearSession(sessionId: string): Promise<any> {
    const response = await api.delete(`/chat/sessions/${sessionId}`);
    return response.data;
  },

  // Document ingestion endpoints
  async uploadDocument(
    file: File,
    chunkSize: number = 1000,
    chunkOverlap: number = 200,
    metadata: Record<string, any> = {}
  ): Promise<IngestionResult> {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('chunk_size', chunkSize.toString());
    formData.append('chunk_overlap', chunkOverlap.toString());
    formData.append('metadata', JSON.stringify(metadata));

    const response = await api.post('/ingestion/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async uploadDocuments(
    files: File[],
    chunkSize: number = 1000,
    chunkOverlap: number = 200,
    parallelProcessing: boolean = true
  ): Promise<any> {
    const formData = new FormData();
    files.forEach(file => formData.append('files', file));
    formData.append('chunk_size', chunkSize.toString());
    formData.append('chunk_overlap', chunkOverlap.toString());
    formData.append('parallel_processing', parallelProcessing.toString());

    const response = await api.post('/ingestion/batch', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getCollectionStats(): Promise<CollectionStats> {
    const response = await api.get('/ingestion/stats');
    return response.data;
  },

  async deleteCollection(confirmation: string = 'DELETE_ALL'): Promise<any> {
    const response = await api.delete('/ingestion/collection', {
      data: { confirmation }
    });
    return response.data;
  },

  async searchDocuments(request: SearchRequest): Promise<SearchResponse> {
    const response = await api.post('/ingestion/search', request);
    return response.data;
  },
};

export default api;
