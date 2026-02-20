<template>
  <div class="review-view">
    <div class="review-header">
      <h2>复习列表</h2>
      <button @click="userStore.fetchReviewList()" class="refresh-button">刷新</button>
    </div>

    <div v-if="userStore.isLoading" class="review-loading">
      <p>加载中...</p>
    </div>

    <div v-if="userStore.error" class="review-error">
      <p>{{ userStore.error }}</p>
    </div>

    <div v-if="userStore.reviewList" class="review-info">
      <p>总计：{{ userStore.reviewList.total_count }} 项</p>
      <p>待复习：{{ userStore.reviewList.due_now }} 项</p>
    </div>

    <div v-if="userStore.reviewList?.items.length === 0 && !userStore.isLoading" class="review-empty">
      <p>暂无需要复习的内容</p>
    </div>

    <div class="review-list">
      <div
        v-for="item in userStore.reviewList?.items"
        :key="item.word"
        class="review-card"
      >
        <h3>{{ item.word }}</h3>
        <div class="review-meta">
          <span>错误次数：{{ item.error_count }}</span>
        </div>
        <div class="review-meanings">
          <div v-for="(meaning, index) in item.weak_meanings" :key="index" class="meaning-item">
            <p>{{ meaning.meaning }}</p>
            <div v-if="meaning.examples.length > 0" class="examples">
              <p v-for="(example, i) in meaning.examples" :key="i" class="example">
                {{ example }}
              </p>
            </div>
          </div>
        </div>
        <button @click="userStore.acknowledgeReview(item.word)" class="acknowledge-button">
          确认已复习
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

onMounted(() => {
  userStore.fetchReviewList()
})
</script>

<style scoped>
.review-view {
  max-width: 800px;
  margin: 0 auto;
}

.review-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.refresh-button {
  padding: 0.5rem 1rem;
  border: 1px solid #e5e7eb;
  background: white;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.refresh-button:hover {
  background: #f9fafb;
  border-color: #667eea;
}

.review-loading,
.review-error,
.review-empty {
  text-align: center;
  padding: 2rem;
  color: #6b7280;
}

.review-info {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  color: #6b7280;
}

.review-list {
  display: grid;
  gap: 1rem;
}

.review-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.review-card h3 {
  margin: 0 0 0.5rem 0;
  font-size: 1.5rem;
  color: #1f2937;
}

.review-meta {
  color: #6b7280;
  font-size: 0.875rem;
  margin-bottom: 1rem;
}

.review-meanings {
  margin-bottom: 1rem;
}

.meaning-item {
  padding: 0.75rem;
  background: #f9fafb;
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.meaning-item > p {
  margin: 0 0 0.5rem 0;
  font-weight: 500;
}

.example {
  margin: 0.25rem 0;
  padding-left: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.acknowledge-button {
  padding: 0.5rem 1rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.acknowledge-button:hover {
  opacity: 0.9;
}
</style>
