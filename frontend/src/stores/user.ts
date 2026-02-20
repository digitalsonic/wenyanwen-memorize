import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ReviewList } from '@/types'
import { reviewApi } from '@/api/client'

export const useUserStore = defineStore('user', () => {
  // State
  const reviewList = ref<ReviewList | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function fetchReviewList() {
    isLoading.value = true
    error.value = null
    try {
      reviewList.value = await reviewApi.getList()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch review list'
    } finally {
      isLoading.value = false
    }
  }

  async function acknowledgeReview(word: string) {
    try {
      await reviewApi.acknowledge(word)
      // Refresh the list after acknowledging
      await fetchReviewList()
    } catch (e) {
      error.value = e instanceof Error ? e.message : 'Failed to acknowledge review'
    }
  }

  return {
    // State
    reviewList,
    isLoading,
    error,
    // Actions
    fetchReviewList,
    acknowledgeReview,
  }
})
