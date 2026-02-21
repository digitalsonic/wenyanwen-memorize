<script setup lang="ts">
import { computed } from 'vue'
import { useProgressStore } from '@/stores/progress'

const progressStore = useProgressStore()

const emit = defineEmits<{
  detail: []
}>()

const progress = computed(() => {
  const p = progressStore.progress
  if (!p) return null

  return {
    percentage: p.completion_percentage,
    learned: p.learned_words,
    total: p.total_words,
    mastered: p.mastered_words,
    cycle: p.cycle,
  }
})
</script>

<template>
  <div v-if="progress" class="progress-card">
    <div class="progress-header">
      <div class="title">学习进度</div>
      <div class="cycle-badge">第 {{ progress.cycle }} 轮</div>
    </div>

    <div class="progress-bar-container">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: `${progress.percentage}%` }"></div>
      </div>
      <div class="progress-text">{{ progress.percentage.toFixed(1) }}%</div>
    </div>

    <div class="stats-row">
      <div class="stat-item">
        <div class="stat-value">{{ progress.learned }}</div>
        <div class="stat-label">已学</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ progress.mastered }}</div>
        <div class="stat-label">已掌握</div>
      </div>
      <div class="stat-item">
        <div class="stat-value">{{ progress.total }}</div>
        <div class="stat-label">总词数</div>
      </div>
    </div>

    <button class="detail-btn" @click="emit('detail')">查看详情 →</button>
  </div>
</template>

<style scoped>
.progress-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.cycle-badge {
  background: #667eea;
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
}

.progress-bar-container {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
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
  text-align: right;
}

.stats-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #333;
}

.stat-label {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
}

.detail-btn {
  width: 100%;
  padding: 12px;
  background: #f5f5f5;
  border: none;
  border-radius: 8px;
  color: #667eea;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.detail-btn:hover {
  background: #ebebeb;
}
</style>
