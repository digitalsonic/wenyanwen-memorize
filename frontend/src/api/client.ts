import axios from 'axios'
import type {
  QuizSession,
  AnswerSubmission,
  ReviewList,
  LearnSession,
  LearningProgressSummary,
  APIResponse,
} from '@/types'

/**
 * 根据环境变量确定 API baseURL
 *
 * VITE_API_BASE_URL 支持三种格式：
 * 1. 完整 URL: "https://example.com/api" → "https://example.com/api/v1"
 * 2. 相对路径: "/wenyanwen/api" → "/wenyanwen/api/v1"
 * 3. 空值或未设置: "" → "/api/v1" (默认)
 */
const getBaseURL = () => {
  // 读取环境变量
  const apiBase = import.meta.env.VITE_API_BASE_URL || ''

  if (!apiBase) {
    // 空值：使用默认路径
    return '/api/v1'
  }

  // 完整 URL (https://...) 或相对路径 (/path/to/api)
  // 统一追加 /v1 后缀
  return apiBase.endsWith('/') ? `${apiBase}v1` : `${apiBase}/v1`
}

const api = axios.create({
  baseURL: getBaseURL(),
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Quiz API (Review session)
export const quizApi = {
  review: async (level: number | null = null) => {
    const { data } = await api.get<QuizSession>('/quiz/review', { params: { level } })
    return data
  },

  submit: async (submission: AnswerSubmission) => {
    const { data } = await api.post<APIResponse>('/quiz/submit', submission)
    return data
  },
}

// Learn API (New words)
export const learnApi = {
  start: async (count: number = 10, mode: 'sequential' | 'random' = 'sequential') => {
    const { data } = await api.post<LearnSession>('/quiz/learn', { count, mode })
    return data
  },

  complete: async (wordIds: string[]) => {
    const { data } = await api.post<APIResponse>('/quiz/learn/complete', wordIds)
    return data
  },
}

// Review API (List)
export const reviewApi = {
  getList: async () => {
    const { data } = await api.get<ReviewList>('/review/list')
    return data
  },
}

// Progress API
export const progressApi = {
  get: async () => {
    const { data } = await api.get<LearningProgressSummary>('/review/progress')
    return data
  },

  reset: async () => {
    const { data } = await api.post<APIResponse>('/review/reset-progress')
    return data
  },

  startNewCycle: async () => {
    const { data } = await api.post<APIResponse>('/review/start-new-cycle')
    return data
  },
}

export default api
