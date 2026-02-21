<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { reviewApi } from '@/api/client'
import type { ReviewList } from '@/types'

const router = useRouter()
const reviewList = ref<ReviewList | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

onMounted(() => {
  fetchReviewList()
})

async function fetchReviewList() {
  isLoading.value = true
  error.value = null
  try {
    const data = await reviewApi.getList()
    console.log('Review data:', data)
    reviewList.value = data
  } catch (e) {
    console.error('Failed to fetch review list:', e)
    error.value = e instanceof Error ? e.message : '加载失败'
  } finally {
    isLoading.value = false
  }
}

function startReview(level: number | null = null) {
  // Navigate to quiz view with level filter
  router.push(`/?level=${level}`)
}

function goBack() {
  router.push('/')
}

function getQuizTypeName(type: string): string {
  const names: Record<string, string> = {
    card: '卡片',
    flashcard: '闪卡',
    multiple_choice: '单选',
    true_false: '判断',
  }
  return names[type] || type
}

function getLevelName(level: number): string {
  const names: Record<number, string> = {
    0: '初学',
    1: '第1天复习',
    2: '第2天复习',
    3: '第4天复习',
    4: '第7天复习',
    5: '第15天复习',
    6: '第30天复习',
  }
  return names[level] || `第${level}级`
}

// Get grouped entries as array for easier iteration
const groupedEntries = computed(() => {
  if (!reviewList.value?.grouped) return []
  return Object.entries(reviewList.value.grouped)
    .map(([level, items]) => ({ level: Number(level), items }))
    .sort((a, b) => a.level - b.level)
})
</script>

<template>
  <div class="review-view">
    <header class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <div class="title">今日复习</div>
      <button class="refresh-btn" @click="fetchReviewList">刷新</button>
    </header>

    <main class="main-content">
      <div v-if="isLoading" class="loading">加载中...</div>

      <div v-else-if="error" class="error">{{ error }}</div>

      <div v-else-if="!reviewList || reviewList.total_count === 0" class="empty">
        <div class="icon">😊</div>
        <h2>暂无到期复习</h2>
        <p>目前没有需要复习的词语</p>
        <button class="btn primary" @click="goBack">返回首页</button>
      </div>

      <div v-else class="review-content">
        <div class="summary">
          共 <strong>{{ reviewList.total_count }}</strong> 个词需要复习
        </div>

        <!-- No items in grouped -->
        <div v-if="groupedEntries.length === 0" class="empty-groups">
          <p>没有找到分组数据</p>
        </div>

        <!-- Group by level -->
        <div
          v-for="{ level, items } in groupedEntries"
          :key="level"
          class="level-group"
        >
          <div class="level-header">
            <span class="level-title">{{ getLevelName(level) }}</span>
            <span class="level-count">{{ items.length }} 个词</span>
          </div>

          <div class="review-cards">
            <div
              v-for="item in items"
              :key="item.word_id"
              class="review-card"
            >
              <div class="card-header">
                <span class="word">{{ item.word }}</span>
                <span class="quiz-type-badge">{{ getQuizTypeName(item.quiz_type) }}</span>
              </div>

              <div class="card-meta">
                <span class="error-count" v-if="item.error_count > 0">
                  错误 {{ item.error_count }} 次
                </span>
              </div>

              <div class="meanings-preview">
                <div
                  v-for="meaning in (item.word_data?.meanings || []).slice(0, 2)"
                  :key="meaning.id"
                  class="meaning-item"
                >
                  {{ meaning.definition }}
                </div>
              </div>

              <button class="start-btn" @click="startReview(level)">
                开始复习 →
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.review-view {
  min-height: 100vh;
  padding: 16px;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}

.back-btn,
.refresh-btn {
  background: none;
  border: none;
  font-size: 16px;
  color: #667eea;
  cursor: pointer;
  padding: 8px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.loading,
.error,
.empty {
  text-align: center;
  padding: 40px 20px;
}

.icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.empty h2 {
  font-size: 20px;
  color: #333;
  margin-bottom: 8px;
}

.empty p {
  color: #999;
  margin-bottom: 24px;
}

.empty-groups {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.summary {
  text-align: center;
  font-size: 16px;
  color: #666;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 12px;
}

.level-group {
  margin-bottom: 24px;
}

.level-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 0 4px;
}

.level-title {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.level-count {
  font-size: 14px;
  color: #999;
}

.review-cards {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
  gap: 12px;
}

.review-card {
  background: white;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  flex-direction: column;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.word {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.quiz-type-badge {
  font-size: 12px;
  padding: 4px 8px;
  background: #f0f0f0;
  border-radius: 8px;
  color: #666;
}

.card-meta {
  margin-bottom: 12px;
}

.error-count {
  font-size: 12px;
  color: #f44336;
}

.meanings-preview {
  flex: 1;
  margin-bottom: 12px;
}

.meaning-item {
  font-size: 14px;
  color: #666;
  padding: 4px 0;
  line-height: 1.4;
}

.start-btn {
  width: 100%;
  padding: 10px;
  border: none;
  border-radius: 8px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: opacity 0.2s;
}

.start-btn:hover {
  opacity: 0.9;
}

.btn {
  padding: 12px 32px;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
}

.btn:hover {
  transform: scale(1.05);
}

.btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
</style>
