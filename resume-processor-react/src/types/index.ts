export interface User {
  id: number
  username: string
  email?: string
  created_at?: string
  last_login?: string
}

export interface ProcessingResult {
  step1_extracted_data: any
  step2_restructured_text: string
  step3_final_data: any
  step3_final_formatted: string
  processing_metadata: {
    original_filename: string
    target_role: string
    template_style: string
  }
  token_usage: {
    total_tokens: {
      input_tokens: number
      output_tokens: number
      total_tokens: number
    }
    cost_estimation: {
      input_cost_usd: number
      output_cost_usd: number
      total_cost_usd: number
      model: string
    }
  }
}

export interface ProcessingHistory {
  id: number
  filename: string
  processing_date: string
  status: string
  metadata?: any
}

export interface CustomPrompt {
  id: number
  name: string
  prompt_text: string
  created_at: string
}

export interface TokenUsage {
  id: number
  user_id: number
  history_id: number
  input_tokens: number
  output_tokens: number
  total_tokens: number
  input_cost_usd: number
  output_cost_usd: number
  total_cost_usd: number
  model: string
  created_at: string
}

export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  error?: string
  message?: string
}

export interface ProcessingStep {
  step: number
  name: string
  status: 'pending' | 'processing' | 'completed' | 'error'
  result?: any
  error?: string
}