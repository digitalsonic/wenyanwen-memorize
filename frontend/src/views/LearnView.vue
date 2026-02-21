<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useLearnStore } from '@/stores/learn'
import { useQuizStore } from '@/stores/quiz'
import CardView from '@/components/CardView.vue'
import type { QuizQuestion } from '@/types'

const router = useRouter()
const learnStore = useLearnStore()
const quizStore = useQuizStore()

// 学习阶段: 'learning' | 'testing' | 'finished'
const learnPhase = ref<'learning' | 'testing' | 'finished'>('learning')
const testQuestions = ref<QuizQuestion[]>([])
const currentTestIndex = ref(0)
const testAnswers = ref<Array<{ word_id: string; question_type: string; user_answer: string | boolean; is_correct: boolean }>>([])

onMounted(() => {
  learnStore.startLearning()
})

// 监听学习完成，自动进入测试阶段
watch(() => learnStore.isFinished, (isFinished) => {
  if (isFinished && learnStore.learnedWordIds.length > 0) {
    startTesting()
  }
})

async function startTesting() {
  // 开始对刚才学习的词进行测试
  learnPhase.value = 'testing'
  currentTestIndex.value = 0
  testAnswers.value = []

  // 为每个学习的词生成单选题
  const words = learnStore.session?.words || []
  testQuestions.value = words.map((card) => ({
    word_id: card.word_id,
    word: card.word,
    question_type: 'multiple_choice' as const,
    example_sentence: card.front.sentence,
    example_source: card.front.source,
    options: card.back.meanings,  // meanings 已经是 string[] 类型
    correct_answer: card.back.meanings[0] || '',
    correct_meaning_id: '',  // CardQuestion 类型没有 meaning_id，暂时留空
  }))
}

function submitTestAnswer(answer: string) {
  const question = testQuestions.value[currentTestIndex.value]
  const isCorrect = answer === question.correct_answer

  testAnswers.value.push({
    word_id: question.word_id,
    question_type: question.question_type,
    user_answer: answer,
    is_correct,
  })

  currentTestIndex.value++

  // 测试完成，提交结果
  if (currentTestIndex.value >= testQuestions.value.length) {
    submitTestResults()
  }
}

async function submitTestResults() {
  // 提交测试结果到后端
  if (testAnswers.value.length > 0) {
    await quizStore.submitDirectAnswers(testAnswers.value)
  }

  // 完成学习
  await learnStore.completeLearning()

  // 进入完成状态
  learnPhase.value = 'finished'
}

function goBack() {
  if (learnStore.learnedWordIds.length > 0 && learnPhase.value !== 'finished') {
    // 确认退出
    if (confirm('确定要退出吗？学习进度将被保存。')) {
      if (learnPhase.value === 'testing') {
        // 提交当前测试结果
        submitTestResults()
      } else {
        learnStore.completeLearning().then(() => {
          router.push('/')
        })
      }
      router.push('/')
    }
  } else {
    router.push('/')
  }
}

const currentTestQuestion = computed(() => testQuestions.value[currentTestIndex.value])
const testProgress = computed(() => {
  if (testQuestions.value.length === 0) return 0
  return (currentTestIndex.value / testQuestions.value.length) * 100
})
</script>

<template>
  <div class="learn-view">
    <header class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <div class="title">{{ learnPhase === 'testing' ? '初学测试' : '学新词' }}</div>
      <div class="progress">
        <span v-if="learnPhase === 'learning'">
          {{ learnStore.currentIndex }} / {{ learnStore.session?.total_count ?? 0 }}
        </span>
        <span v-else-if="learnPhase === 'testing'">
          {{ currentTestIndex }} / {{ testQuestions.length }}
        </span>
      </div>
    </header>

    <!-- 学习进度条 -->
    <div v-if="learnPhase === 'testing'" class="progress-bar">
      <div class="progress-fill" :style="{ width: `${testProgress}%` }"></div>
    </div>

    <main class="main-content">
      <!-- 学习阶段 -->
      <template v-if="learnPhase === 'learning'">
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

        <div v-else-if="learnStore.isFinished && testQuestions.length === 0" class="finished">
          <div class="finished-icon">🎉</div>
          <h2>今日学习完成！</h2>
          <p>已学习 {{ learnStore.learnedWordIds.length }} 个新词</p>
          <p class="remaining">剩余新词：{{ learnStore.remainingCount }} 个</p>
          <button class="btn primary" @click="goBack">返回首页</button>
        </div>

        <div v-else-if="learnStore.isFinished" class="transition">
          <div class="transition-icon">✓</div>
          <h2>学习完成</h2>
          <p>接下来进行简单的测试，帮助巩固记忆</p>
          <button class="btn primary" @click="startTesting">开始测试</button>
        </div>
      </template>

      <!-- 测试阶段 -->
      <template v-else-if="learnPhase === 'testing'">
        <div v-if="currentTestQuestion" class="test-question">
          <div class="question-label">请选择正确的释义</div>
          <div class="word">{{ currentTestQuestion.word }}</div>
          <div class="example">
            {{ currentTestQuestion.example_sentence }}
          </div>
          <div class="source">{{ currentTestQuestion.example_source }}</div>

          <div class="options">
            <button
              v-for="(option, index) in currentTestQuestion.options"
              :key="index"
              class="option-btn"
              @click="submitTestAnswer(option)"
            >
              {{ String.fromCharCode(65 + index) }}. {{ option }}
            </button>
          </div>
        </div>
      </template>

      <!-- 完成阶段 -->
      <template v-else-if="learnPhase === 'finished'">
        <div class="finished">
          <div class="finished-icon">🎉</div>
          <h2>今日学习完成！</h2>
          <p>已学习 {{ learnStore.learnedWordIds.length }} 个新词</p>
          <p v-if="testAnswers.length > 0" class="test-result">
            测试正确：{{ testAnswers.filter(a => a.is_correct).length }} / {{ testAnswers.length }}
          </p>
          <p class="remaining">剩余新词：{{ learnStore.remainingCount }} 个</p>
          <button class="btn primary" @click="goBack">返回首页</button>
        </div>
      </template>
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
  color: #667eea;
  font-weight: 600;
}

.progress-bar {
  height: 4px;
  background: #f0f0f0;
  border-radius: 2px;
  overflow: hidden;
  margin-bottom: 24px;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
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
.finished,
.transition {
  text-align: center;
}

.finished-icon,
.transition-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.transition-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 16px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
}

.finished h2,
.transition h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.finished p,
.transition p {
  color: #666;
  margin-bottom: 8px;
}

.test-result {
  font-size: 18px;
  color: #667eea;
  font-weight: 600;
  margin: 16px 0;
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

/* 测试阶段样式 */
.test-question {
  width: 100%;
  max-width: 500px;
}

.question-label {
  font-size: 14px;
  color: #999;
  margin-bottom: 16px;
  text-align: center;
}

.word {
  font-size: 48px;
  font-weight: 700;
  color: #333;
  text-align: center;
  margin-bottom: 24px;
}

.example {
  font-size: 20px;
  color: #333;
  text-align: center;
  margin-bottom: 12px;
  line-height: 1.6;
}

.source {
  font-size: 12px;
  color: #999;
  text-align: center;
  margin-bottom: 32px;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-btn {
  width: 100%;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  font-size: 16px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
}

.option-btn:hover {
  border-color: #667eea;
  background: #f8f9ff;
}
</style>
