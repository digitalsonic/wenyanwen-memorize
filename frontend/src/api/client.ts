import axios from 'axios'
import type {
  QuizSession,
  AnswerSubmission,
  ReviewList,
  LearnSession,
  LearningProgressSummary,
  APIResponse,
} from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
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
