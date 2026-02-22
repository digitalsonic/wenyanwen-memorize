<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useProgressStore } from '@/stores/progress'
import { progressApi } from '@/api/client'

const router = useRouter()
const progressStore = useProgressStore()
const isResetting = ref(false)

onMounted(() => {
  progressStore.fetchProgress()
})

async function handleResetProgress() {
  if (!confirm('确定要重置学习进度吗？这将删除当前轮次的所有学习记录，且无法恢复。')) {
    return
  }

  isResetting.value = true
  try {
    const response = await progressApi.reset()
    if (response.success) {
      // 刷新进度数据
      await progressStore.fetchProgress()
      alert(response.message || '学习进度已重置')
    }
  } catch (error) {
    console.error('重置进度失败:', error)
    alert('重置进度失败，请稍后重试')
  } finally {
    isResetting.value = false
  }
}

function goBack() {
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
          <button
            class="action-btn danger"
            :disabled="isResetting"
            @click="handleResetProgress"
          >
            {{ isResetting ? '重置中...' : '重置学习进度' }}
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
  display: flex;
  justify-content: center;
}

.action-btn {
  min-width: 200px;
  padding: 16px 32px;
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s, opacity 0.2s;
}

.action-btn:hover:not(:disabled) {
  transform: scale(1.02);
}

.action-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.action-btn.danger {
  background: #f5576c;
  color: white;
}
</style>
