import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LearnSession, CardQuestion } from '@/types'
import { learnApi } from '@/api/client'

export const useLearnStore = defineStore('learn', () => {
  // State
  const session = ref<LearnSession | null>(null)
  const currentIndex = ref(0)
  const learnedWordIds = ref<string[]>([])
  const isFlipped = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const currentCard = computed(() => {
    if (!session.value || currentIndex.value >= session.value.words.length) {
      return null
    }
    return session.value.words[currentIndex.value]
  })

  const progress = computed(() => {
    if (!session.value) return 0
    return (currentIndex.value / session.value.total_count) * 100
  })

  const isFinished = computed(() => {
    if (!session.value) return false
    return currentIndex.value >= session.value.words.length
  })

  const remainingCount = computed(() => {
    return session.value?.remaining_count ?? 0
  })

  // Actions
  async function startLearning(count: number = 10, mode: 'sequential' | 'random' = 'sequential') {
    isLoading.value = true
    error.value = null
    try {
      session.value = await learnApi.start(count, mode)
      currentIndex.value = 0
      learnedWordIds.value = []
      isFlipped.value = false
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to start learning'
    } finally {
      isLoading.value = false
    }
  }

  function flipCard() {
    isFlipped.value = !isFlipped.value
  }

  function markAsLearned() {
    const card = currentCard.value
    if (card) {
      learnedWordIds.value.push(card.word_id)
    }
    nextCard()
  }

  function nextCard() {
    isFlipped.value = false
    currentIndex.value++
  }

  async function completeLearning() {
    if (learnedWordIds.value.length === 0) return
    isLoading.value = true
    try {
      await learnApi.complete(learnedWordIds.value)
      return true
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to complete learning'
      return false
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    session.value = null
    currentIndex.value = 0
    learnedWordIds.value = []
    isFlipped.value = false
    error.value = null
  }

  return {
    // State
    session,
    currentIndex,
    learnedWordIds,
    isFlipped,
    isLoading,
    error,
    // Computed
    currentCard,
    progress,
    isFinished,
    remainingCount,
    // Actions
    startLearning,
    flipCard,
    markAsLearned,
    nextCard,
    completeLearning,
    reset,
  }
})
