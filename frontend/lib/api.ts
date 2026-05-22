/**
 * API Client for BizFlow AI Backend
 * Handles all communication with the FastAPI backend
 */

import axios, { AxiosInstance } from 'axios';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'https://google-hackathon-nyvj.vercel.app';

// Create axios instance with default config
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60 seconds for agent processing
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
apiClient.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Types
export interface WorkflowStep {
  agent: string;
  stage: string;
  status: 'in_progress' | 'completed' | 'failed';
  timestamp: string;
  action: string;
  error?: string;
}

export interface ScheduleRequest {
  message: string;
  session_id?: string;
}

export interface ScheduleResponse {
  status: string;
  final_output: string;
  workflow_complete: boolean;
  session_id: string;
  workflow_steps?: WorkflowStep[];
  error?: string;
}

export interface Manager {
  id: number;
  name: string;
  email: string;
  role: string;
  department: string;
  availability: Record<string, string[]>;
  timezone: string;
}

export interface Meeting {
  id: number;
  meeting_type: string;
  participants: string[];
  participant_emails: string[];
  day: string;
  time: string;
  status: string;
  reasoning?: string;
  created_at: string;
}

// API Functions
export const api = {
  /**
   * Schedule a meeting using natural language
   */
  async scheduleRequest(message: string, sessionId?: string): Promise<ScheduleResponse> {
    const response = await apiClient.post<ScheduleResponse>('/api/schedule', {
      message,
      session_id: sessionId,
    });
    return response.data;
  },

  /**
   * Get all managers
   */
  async getManagers(): Promise<{ managers: Manager[]; total: number }> {
    const response = await apiClient.get('/api/managers');
    return response.data;
  },

  /**
   * Get specific manager by ID
   */
  async getManager(managerId: number): Promise<Manager> {
    const response = await apiClient.get(`/api/managers/${managerId}`);
    return response.data;
  },

  /**
   * Get all meetings
   */
  async getMeetings(): Promise<{ meetings: Meeting[]; total: number }> {
    const response = await apiClient.get('/api/meetings');
    return response.data;
  },

  /**
   * Get specific meeting by ID
   */
  async getMeeting(meetingId: number): Promise<Meeting> {
    const response = await apiClient.get(`/api/meetings/${meetingId}`);
    return response.data;
  },

  /**
   * Get database statistics
   */
  async getStatistics(): Promise<any> {
    const response = await apiClient.get('/api/statistics');
    return response.data;
  },

  /**
   * Get all departments
   */
  async getDepartments(): Promise<{ departments: string[]; total: number }> {
    const response = await apiClient.get('/api/departments');
    return response.data;
  },

  /**
   * Health check
   */
  async healthCheck(): Promise<any> {
    const response = await apiClient.get('/');
    return response.data;
  },
};

export default api;
