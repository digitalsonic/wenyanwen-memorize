<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProgressStore } from '@/stores/progress'

const router = useRouter()
const progressStore = useProgressStore()

onMounted(() => {
  progressStore.fetchProgress()
})

function goBack() {
  router.push('/')
}

function startReview() {
  router.push('/')
}
</script>

<template>
  <div class="progress-view">
    <header class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <div class="title">学习进度</div>
      <div class="placeholder"></div>
    </header>

    <main class="main-content">
      <div v-if="progressStore.isLoading" class="loading">
        加载中...
      </div>

      <div v-else-if="progressStore.error" class="error">
        {{ progressStore.error }}
      </div>

      <div v-else-if="progressStore.progress" class="progress-content">
        <!-- Cycle Info -->
        <div class="card cycle-card">
          <div class="card-title">当前轮次</div>
          <div class="cycle-number">第 {{ progressStore.currentCycle }} 轮</div>
          <div class="progress-bar-container">
            <div class="progress-bar">
              <div
                class="progress-fill"
                :style="{ width: `${progressStore.completionPercentage}%` }"
              ></div>
            </div>
            <div class="progress-text">{{ progressStore.completionPercentage.toFixed(1) }}%</div>
          </div>
        </div>

        <!-- Stats -->
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">{{ progressStore.learnedCount }}</div>
            <div class="stat-label">已学词语</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ progressStore.masteredCount }}</div>
            <div class="stat-label">已掌握</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ progressStore.totalCount }}</div>
            <div class="stat-label">总词数</div>
          </div>
          <div class="stat-card">
            <div class="stat-value">{{ progressStore.totalCount - progressStore.learnedCount }}</div>
            <div class="stat-label">未学</div>
          </div>
        </div>

        <!-- Level Breakdown -->
        <div class="card level-card">
          <div class="card-title">各阶段词语数量</div>
          <div class="level-list">
            <div
              v-for="(count, level) in progressStore.levelCounts"
              :key="level"
              class="level-item"
            >
              <span class="level-name">{{ progressStore.levelNames[level] }}</span>
              <span class="level-count">{{ count }}</span>
            </div>
          </div>
        </div>

        <!-- Actions -->
        <div class="actions">
          <button class="action-btn primary" @click="router.push('/learn')">
            学新词
          </button>
          <button class="action-btn secondary" @click="startReview">
            今日复习
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.progress-view {
  min-height: 100vh;
  padding: 16px;
  max-width: 600px;
  margin: 0 auto;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 0;
}

.back-btn {
  background: none;
  border: none;
  font-size: 18px;
  color: #667eea;
  cursor: pointer;
  padding: 8px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.placeholder {
  width: 50px;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.loading,
.error {
  text-align: center;
  padding: 40px 20px;
  color: #999;
}

.card {
  background: white;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.card-title {
  font-size: 14px;
  color: #999;
  margin-bottom: 16px;
}

.cycle-card {
  text-align: center;
}

.cycle-number {
  font-size: 32px;
  font-weight: 700;
  color: #667eea;
  margin-bottom: 20px;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 12px;
  background: #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  border-radius: 6px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
  min-width: 50px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  text-align: center;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #333;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #999;
}

.level-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.level-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 8px;
}

.level-name {
  font-size: 14px;
  color: #333;
}

.level-count {
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
}

.actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.action-btn {
  padding: 16px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
}

.action-btn:hover {
  transform: scale(1.02);
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-btn.secondary {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}
</style>
