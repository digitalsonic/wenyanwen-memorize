/** Type definitions for the application */

export type QuizType = 'card' | 'flashcard' | 'multiple_choice' | 'true_false'

export interface ExampleItem {
  sentence: string
  source: string
  level?: 'core' | 'secondary'
}

export interface MeaningItem {
  id: string
  definition: string
  examples: ExampleItem[]
}

export interface WordData {
  id: string
  word: string
  type: string
  pinyin?: string
  meanings: MeaningItem[]
  mnemonics?: string | null
}

export interface WordLibrary {
  words: WordData[]
  metadata?: {
    version: string
    total_words: number
    last_updated: string
  }
}

// Question types
export interface MultipleChoiceQuestion {
  word_id: string
  word: string
  question_type: 'multiple_choice'
  example_sentence: string
  example_source: string
  options: string[]
  correct_answer: string
  correct_meaning_id: string
}

export interface TrueFalseQuestion {
  word_id: string
  word: string
  question_type: 'true_false'
  example_sentence: string
  example_source: string
  given_meaning: string
  is_correct: boolean
  correct_meaning: string  // The actual correct meaning for the example
}

export interface CardQuestion {
  word_id: string
  word: string
  question_type: 'card'
  pinyin?: string | null
  front: {
    sentence: string
    source: string
  }
  back: {
    meanings: string[]
    mnemonics?: string | null
  }
}

export interface FlashcardQuestion {
  word_id: string
  word: string
  question_type: 'flashcard'
  example_sentence: string
  example_source: string
  correct_meaning: string
  meaning_id: string
  mnemonics?: string | null
}

export type QuizQuestion = MultipleChoiceQuestion | TrueFalseQuestion | CardQuestion | FlashcardQuestion

// Quiz session
export interface QuizSession {
  session_id: string
  level: number
  questions: QuizQuestion[]
  total_count: number
}

export interface QuizAnswer {
  word_id: string
  question_type: QuizType
  user_answer: string | boolean | number  // number for flashcard assessment (0=fuzzy, 1=clear, 2=uncertain)
  is_correct: boolean
  time_spent_seconds?: number
}

export interface AnswerSubmission {
  level: number
  answers: QuizAnswer[]
}

// Learning
export interface LearnSession {
  session_id: string
  words: CardQuestion[]
  total_count: number
  remaining_count: number
}

export interface LearnRequest {
  count: number
  mode: 'sequential' | 'random'
}

// Review
export interface ReviewItem {
  word_id: string
  word: string
  level: number
  quiz_type: QuizType
  error_count: number
  last_review_at: string | null
  next_review_at: string
  word_data: WordData
}

export interface ReviewList {
  items: ReviewItem[]
  total_count: number
  grouped: Record<number, ReviewItem[]>
}

// Progress
export interface LearningProgressSummary {
  cycle: number
  total_words: number
  learned_words: number
  mastered_words: number
  completion_percentage: number
  current_level_counts: Record<number, number>
  level_names: Record<number, string>
}

// API Response
export interface APIResponse {
  success: boolean
  message?: string | null
  data?: {
    correct_count?: number
    total_count?: number
    wrong_answer_ids?: string[]
    has_wrong?: boolean
  } | null
}
