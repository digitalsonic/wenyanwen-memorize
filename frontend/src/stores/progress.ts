import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { LearningProgressSummary } from '@/types'
import { progressApi } from '@/api/client'

export const useProgressStore = defineStore('progress', () => {
  // State
  const progress = ref<LearningProgressSummary | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Computed
  const completionPercentage = computed(() => {
    return progress.value?.completion_percentage ?? 0
  })

  const masteredCount = computed(() => {
    return progress.value?.mastered_words ?? 0
  })

  const learnedCount = computed(() => {
    return progress.value?.learned_words ?? 0
  })

  const totalCount = computed(() => {
    return progress.value?.total_words ?? 0
  })

  const currentCycle = computed(() => {
    return progress.value?.cycle ?? 1
  })

  const levelCounts = computed(() => {
    return progress.value?.current_level_counts ?? {}
  })

  const levelNames = computed(() => {
    return progress.value?.level_names ?? {}
  })

  // Actions
  async function fetchProgress() {
    isLoading.value = true
    error.value = null
    try {
      progress.value = await progressApi.get()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch progress'
    } finally {
      isLoading.value = false
    }
  }

  function reset() {
    progress.value = null
    error.value = null
  }

  return {
    // State
    progress,
    isLoading,
    error,
    // Computed
    completionPercentage,
    masteredCount,
    learnedCount,
    totalCount,
    currentCycle,
    levelCounts,
    levelNames,
    // Actions
    fetchProgress,
    reset,
  }
})
