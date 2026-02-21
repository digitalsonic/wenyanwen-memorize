import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { QuizSession, QuizAnswer } from '@/types'
import { quizApi } from '@/api/client'

export const useQuizStore = defineStore('quiz', () => {
  // State
  const session = ref<QuizSession | null>(null)
  const currentIndex = ref(0)
  const answers = ref<QuizAnswer[]>([])
  const wrongAnswerIds = ref<string[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const currentQuestion = computed(() => {
    if (!session.value || currentIndex.value >= session.value.questions.length) {
      return null
    }
    return session.value.questions[currentIndex.value]
  })

  const progress = computed(() => {
    if (!session.value) return 0
    return (currentIndex.value / session.value.total_count) * 100
  })

  const isFinished = computed(() => {
    if (!session.value) return false
    return currentIndex.value >= session.value.questions.length
  })

  const correctCount = computed(() => {
    return answers.value.filter((a) => a.is_correct).length
  })

  // Actions
  async function startReview(level: number | null = null) {
    isLoading.value = true
    error.value = null
    try {
      session.value = await quizApi.review(level)
      currentIndex.value = 0
      answers.value = []
      wrongAnswerIds.value = []
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to start review'
    } finally {
      isLoading.value = false
    }
  }

  function submitAnswer(answer: QuizAnswer) {
    answers.value.push(answer)
    currentIndex.value++
  }

  async function submitSession() {
    if (!session.value) return
    isLoading.value = true
    try {
      const result = await quizApi.submit({
        level: session.value.level,
        answers: answers.value,
      })
      if (result?.wrong_answer_ids) {
        wrongAnswerIds.value = result.wrong_answer_ids
      }
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to submit answers'
    } finally {
      isLoading.value = false
    }
  }

  // Directly submit answers without a session (for initial learning test)
  async function submitDirectAnswers(directAnswers: QuizAnswer[]) {
    isLoading.value = true
    error.value = null
    try {
      const result = await quizApi.submit({
        level: 1, // Level 1 for first review after learning
        answers: directAnswers,
      })
      if (result?.wrong_answer_ids) {
        wrongAnswerIds.value = result.wrong_answer_ids
      }
      return result
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to submit answers'
      throw e
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    session.value = null
    currentIndex.value = 0
    answers.value = []
    wrongAnswerIds.value = []
    error.value = null
  }

  return {
    // State
    session,
    currentIndex,
    answers,
    wrongAnswerIds,
    isLoading,
    error,
    // Computed
    currentQuestion,
    progress,
    isFinished,
    correctCount,
    // Actions
    startReview,
    submitAnswer,
    submitSession,
    submitDirectAnswers,
    reset,
  }
})
