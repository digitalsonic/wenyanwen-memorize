import axios from 'axios'
import type {
  QuizSession,
  AnswerSubmission,
  ReviewList,
  LearnSession,
  LearningProgressSummary,
  APIResponse,
} from '@/types'

// 根据环境确定 API baseURL
// 开发环境: 通过 Vite proxy 代理到后端
// 生产环境: 直接使用完整路径
const getBaseURL = () => {
  // 开发环境使用相对路径，由 Vite proxy 处理
  if (import.meta.env.DEV) {
    return '/api/v1'
  }
  // 生产环境使用完整 URL
  const apiBase = import.meta.env.VITE_API_BASE_URL || ''
  return apiBase ? `${apiBase}/v1` : '/api/v1'
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
}

export default api
