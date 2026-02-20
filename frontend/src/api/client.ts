import axios from 'axios'
import type { QuizSession, QuizQuestion, AnswerSubmission, ReviewList } from '@/types'

const api = axios.create({
  baseURL: '/api/v1',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Quiz API
export const quizApi = {
  start: async (count: number = 10) => {
    const { data } = await api.get<QuizSession>('/quiz/start', { params: { count } })
    return data
  },

  submit: async (submission: AnswerSubmission) => {
    const { data } = await api.post('/quiz/submit', submission)
    return data
  },
}

// Review API
export const reviewApi = {
  getList: async () => {
    const { data } = await api.get<ReviewList>('/review/list')
    return data
  },

  acknowledge: async (word: string) => {
    const { data } = await api.post('/review/acknowledge', null, { params: { word } })
    return data
  },
}

export default api
