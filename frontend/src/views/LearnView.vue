<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useLearnStore } from '@/stores/learn'
import CardView from '@/components/CardView.vue'

const router = useRouter()
const learnStore = useLearnStore()

onMounted(() => {
  learnStore.startLearning()
})

onUnmounted(() => {
  if (learnStore.learnedWordIds.length > 0) {
    learnStore.completeLearning()
  }
})

function goBack() {
  if (learnStore.learnedWordIds.length > 0) {
    learnStore.completeLearning().then(() => {
      router.push('/')
    })
  } else {
    router.push('/')
  }
}
</script>

<template>
  <div class="learn-view">
    <header class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <div class="title">学新词</div>
      <div class="progress">
        {{ learnStore.currentIndex }} / {{ learnStore.session?.total_count ?? 0 }}
      </div>
    </header>

    <main class="main-content">
      <div v-if="learnStore.isLoading" class="loading">
        加载中...
      </div>

      <div v-else-if="learnStore.error" class="error">
        {{ learnStore.error }}
      </div>

      <CardView
        v-else-if="learnStore.currentCard && !learnStore.isFinished"
        :card="learnStore.currentCard"
        :is-flipped="learnStore.isFlipped"
        @flip="learnStore.flipCard"
        @learned="learnStore.markAsLearned"
      />

      <div v-else-if="learnStore.isFinished" class="finished">
        <div class="finished-icon">🎉</div>
        <h2>今日学习完成！</h2>
        <p>已学习 {{ learnStore.learnedWordIds.length }} 个新词</p>
        <p class="remaining">剩余新词：{{ learnStore.remainingCount }} 个</p>
        <button class="btn primary" @click="goBack">返回首页</button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.learn-view {
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

.progress {
  font-size: 14px;
  color: #999;
}

.main-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.loading,
.error,
.finished {
  text-align: center;
}

.finished-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.finished h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.finished p {
  color: #666;
  margin-bottom: 8px;
}

.remaining {
  font-size: 14px;
  color: #999;
  margin-bottom: 24px;
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
