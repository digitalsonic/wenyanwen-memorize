/** Type definitions for the application */

export interface MeaningItem {
  meaning: string
  examples: string[]
}

export interface WordData {
  word: string
  type: string
  meanings: MeaningItem[]
  level: string
}

export interface QuizQuestion {
  word: string
  question_type: string
  options: string[]
  correct_answer: string
  context_example?: string
}

export interface QuizSession {
  session_id: string
  questions: QuizQuestion[]
  total_count: number
}

export interface QuizAnswer {
  question_id: string
  user_answer: string
  is_correct: boolean
  time_spent_seconds?: number
}

export interface AnswerSubmission {
  session_id: string
  answers: QuizAnswer[]
}

export interface ReviewItem {
  word: string
  weak_meanings: MeaningItem[]
  error_count: number
  last_error_at: string
  next_review_at: string
}

export interface ReviewList {
  items: ReviewItem[]
  total_count: number
  due_now: number
}

export interface APIResponse {
  success: boolean
  message?: string
  data?: Record<string, unknown>
}
