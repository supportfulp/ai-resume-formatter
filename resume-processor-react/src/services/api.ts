import axios from 'axios'
import { ApiResponse, User, ProcessingResult, ProcessingHistory, CustomPrompt, TokenUsage } from '../types'

// Use relative URL when running behind nginx proxy, otherwise use environment variable
const API_BASE_URL = process.env.NODE_ENV === 'production' ? '/api' : (process.env.REACT_APP_API_URL || 'http://localhost:8000')

// Debug logging
console.log('NODE_ENV:', process.env.NODE_ENV)
console.log('REACT_APP_API_URL:', process.env.REACT_APP_API_URL)
console.log('API_BASE_URL:', API_BASE_URL)

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Auth APIs
export const authAPI = {
  login: async (username: string, password: string): Promise<ApiResponse<User>> => {
    const response = await api.post('/auth/login', { username, password })
    return response.data
  },

  register: async (username: string, password: string, email?: string): Promise<ApiResponse<User>> => {
    const response = await api.post('/auth/register', { username, password, email })
    return response.data
  },

  verifyApiKey: async (apiKey: string): Promise<ApiResponse<boolean>> => {
    const response = await api.post('/auth/verify-api-key', { api_key: apiKey })
    return response.data
  },

  saveApiKey: async (userId: number, apiKey: string): Promise<ApiResponse<any>> => {
    const response = await api.post('/auth/save-api-key', { user_id: userId, api_key: apiKey })
    return response.data
  },

  getApiKey: async (userId: number): Promise<ApiResponse<any>> => {
    const response = await api.get(`/auth/get-api-key/${userId}`)
    return response.data
  },

  createSession: async (userId: number, expiresInHours?: number): Promise<ApiResponse<any>> => {
    const response = await api.post('/auth/create-session', { user_id: userId, expires_in_hours: expiresInHours })
    return response.data
  },

  validateSession: async (sessionToken: string): Promise<ApiResponse<any>> => {
    const response = await api.post('/auth/validate-session', { session_token: sessionToken })
    return response.data
  },

  logout: async (sessionToken: string): Promise<ApiResponse<any>> => {
    const response = await api.post('/auth/logout', { session_token: sessionToken })
    return response.data
  },
}

// Resume Processing APIs
export const processingAPI = {
  processResume: async (
    file: File,
    apiKey?: string,
    customPrompt?: string,
    userId?: number,
    customPromptName?: string
  ): Promise<ApiResponse<ProcessingResult>> => {
    const formData = new FormData()
    formData.append('file', file)
    if (apiKey) {
      formData.append('api_key', apiKey)
    }
    if (customPrompt) {
      formData.append('custom_prompt', customPrompt)
    }
    if (userId) {
      formData.append('user_id', userId.toString())
    }
    if (customPromptName) {
      formData.append('custom_prompt_name', customPromptName)
    }

    const response = await api.post('/process/resume', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })
    return response.data
  },

  startResumeProcess: async (
    file: File,
    apiKey?: string,
    customPrompt?: string,
    userId?: number,
    customPromptName?: string
  ): Promise<ApiResponse<{ job_id: string }>> => {
    const formData = new FormData()
    formData.append('file', file)
    if (apiKey) formData.append('api_key', apiKey)
    if (customPrompt) formData.append('custom_prompt', customPrompt)
    if (userId) formData.append('user_id', String(userId))
    if (customPromptName) formData.append('custom_prompt_name', customPromptName)

    const response = await api.post('/process/start', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  getProcessStatus: async (
    jobId: string
  ): Promise<ApiResponse<any>> => {
    const response = await api.get(`/process/status/${jobId}`)
    return response.data
  },

  exportDocx: async (data: any, filename: string): Promise<Blob> => {
    const response = await api.post('/export/docx', { data, filename }, {
      responseType: 'blob',
    })
    return response.data
  },
}

// History APIs
export const historyAPI = {
  getProcessingHistory: async (userId: number, limit: number = 10): Promise<ApiResponse<ProcessingHistory[]>> => {
    const response = await api.get(`/history/${userId}?limit=${limit}`)
    return response.data
  },

  getProcessingResult: async (historyId: number): Promise<ApiResponse<any>> => {
    const response = await api.get(`/history/result/${historyId}`)
    return response.data
  },

  deleteHistory: async (historyId: number, userId: number): Promise<ApiResponse<boolean>> => {
    const response = await api.delete(`/history/${historyId}?user_id=${userId}`)
    return response.data
  },
}

// Prompts APIs
export const promptsAPI = {
  getCustomPrompts: async (userId: number): Promise<ApiResponse<CustomPrompt[]>> => {
    const response = await api.get(`/prompts/${userId}`)
    return response.data
  },

  saveCustomPrompt: async (
    userId: number,
    name: string,
    promptText: string
  ): Promise<ApiResponse<CustomPrompt>> => {
    const response = await api.post('/prompts', { user_id: userId, name, prompt_text: promptText })
    return response.data
  },

  deleteCustomPrompt: async (promptId: number, userId: number): Promise<ApiResponse<boolean>> => {
    const response = await api.delete(`/prompts/${promptId}?user_id=${userId}`)
    return response.data
  },
}

// Token Usage APIs
export const tokenAPI = {
  getTokenUsage: async (userId: number): Promise<ApiResponse<TokenUsage[]>> => {
    const response = await api.get(`/tokens/${userId}`)
    return response.data
  },

  getTokenStats: async (userId: number): Promise<ApiResponse<any>> => {
    const response = await api.get(`/tokens/stats/${userId}`)
    return response.data
  },
}

// Health check for debugging
export const healthAPI = {
  check: async (): Promise<any> => {
    try {
      console.log('Testing health endpoint at:', API_BASE_URL + '/health')
      const response = await api.get('/health')
      console.log('Health check response:', response.data)
      return response.data
    } catch (error) {
      console.error('Health check failed:', error)
      throw error
    }
  },
}

export default api