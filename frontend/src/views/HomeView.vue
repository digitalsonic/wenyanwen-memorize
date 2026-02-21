<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProgressStore } from '@/stores/progress'
import ProgressCard from '@/components/ProgressCard.vue'

const router = useRouter()
const progressStore = useProgressStore()

onMounted(() => {
  progressStore.fetchProgress()
})

function goToLearn() {
  router.push('/learn')
}

function goToReview() {
  router.push('/review')
}

function goToProgress() {
  router.push('/progress')
}
</script>

<template>
  <div class="home-view">
    <header class="header">
      <h1>文言文实词虚词记忆工具</h1>
      <p class="subtitle">基于艾宾浩斯遗忘曲线的智能复习</p>
    </header>

    <main class="main-content">
      <ProgressCard v-if="progressStore.progress" @detail="goToProgress" />

      <div class="action-grid">
        <button class="action-btn primary" @click="goToLearn">
          <div class="icon">📖</div>
          <div class="text">
            <div class="title">学新词</div>
            <div class="description">学习新的文言文词语</div>
          </div>
        </button>

        <button class="action-btn secondary" @click="goToReview">
          <div class="icon">🔄</div>
          <div class="text">
            <div class="title">今日复习</div>
            <div class="description">复习到期的词语</div>
          </div>
        </button>

        <button class="action-btn tertiary" @click="goToProgress">
          <div class="icon">📊</div>
          <div class="text">
            <div class="title">学习进度</div>
            <div class="description">查看详细进度</div>
          </div>
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.home-view {
  min-height: 100vh;
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  font-size: 28px;
  color: #333;
  margin-bottom: 8px;
}

.subtitle {
  color: #666;
  font-size: 14px;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.action-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  text-align: left;
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn.secondary {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.action-btn.tertiary {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.icon {
  font-size: 32px;
}

.text .title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 4px;
}

.text .description {
  font-size: 13px;
  opacity: 0.9;
}
</style>
