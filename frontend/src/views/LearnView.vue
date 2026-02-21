<script setup lang="ts">
import { computed, onMounted, ref, watch, onUnmounted } from 'vue'
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

// 反馈状态
interface FeedbackState {
  status: 'waiting' | 'showing_correct' | 'showing_wrong'
  selectedOption: string | null
  autoAdvanceTimer: ReturnType<typeof setTimeout> | null
}

const feedbackState = ref<FeedbackState>({
  status: 'waiting',
  selectedOption: null,
  autoAdvanceTimer: null
})

// 错题收集
interface WrongAnswer {
  word_id: string
  word: string
  user_answer: string
  correct_answer: string
  example_sentence: string
}

const wrongAnswers = ref<WrongAnswer[]>([])

onMounted(() => {
  learnStore.startLearning()
})

// 清理定时器
onUnmounted(() => {
  clearAutoAdvance()
})

// 监听学习完成，自动进入测试阶段
watch(() => learnStore.isFinished, (isFinished) => {
  if (isFinished && learnStore.learnedWordIds.length > 0) {
    startTesting()
  }
})

// 监听测试索引变化，清理定时器和重置反馈状态
watch(() => currentTestIndex.value, () => {
  clearAutoAdvance()
  feedbackState.value = {
    status: 'waiting',
    selectedOption: null,
    autoAdvanceTimer: null
  }
})

async function startTesting() {
  // 开始对刚才学习的词进行测试
  learnPhase.value = 'testing'
  currentTestIndex.value = 0
  testAnswers.value = []
  wrongAnswers.value = []
  feedbackState.value = {
    status: 'waiting',
    selectedOption: null,
    autoAdvanceTimer: null
  }

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

function handleTestAnswer(answer: string) {
  // 防止重复点击
  if (feedbackState.value.status !== 'waiting') return

  const question = testQuestions.value[currentTestIndex.value]
  const is_correct = answer === question.correct_answer

  // 清理现有定时器
  clearAutoAdvance()

  // 更新反馈状态
  feedbackState.value = {
    status: is_correct ? 'showing_correct' : 'showing_wrong',
    selectedOption: answer,
    autoAdvanceTimer: null
  }

  // 记录答案
  testAnswers.value.push({
    word_id: question.word_id,
    question_type: question.question_type,
    user_answer: answer,
    is_correct,
  })

  // 收集错题
  if (!is_correct) {
    wrongAnswers.value.push({
      word_id: question.word_id,
      word: question.word,
      user_answer: answer,
      correct_answer: question.correct_answer,
      example_sentence: question.example_sentence,
    })
  }

  // 答对时1秒后自动跳转
  if (is_correct) {
    feedbackState.value.autoAdvanceTimer = setTimeout(() => {
      advanceToNext()
    }, 1000)
  }
}

function advanceToNext() {
  clearAutoAdvance()

  // 重置反馈状态
  feedbackState.value = {
    status: 'waiting',
    selectedOption: null,
    autoAdvanceTimer: null
  }

  // 进入下一题
  currentTestIndex.value++

  // 检查是否完成
  if (currentTestIndex.value >= testQuestions.value.length) {
    submitTestResults()
  }
}

function clearAutoAdvance() {
  if (feedbackState.value.autoAdvanceTimer) {
    clearTimeout(feedbackState.value.autoAdvanceTimer)
    feedbackState.value.autoAdvanceTimer = null
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

const correctRate = computed(() => {
  if (testAnswers.value.length === 0) return 0
  return Math.round((testAnswers.value.filter(a => a.is_correct).length / testAnswers.value.length) * 100)
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
              :class="{
                'selected': feedbackState.selectedOption === option,
                'correct': feedbackState.status === 'showing_correct' && feedbackState.selectedOption === option,
                'wrong': feedbackState.status === 'showing_wrong' && feedbackState.selectedOption === option,
                'correct-answer': feedbackState.status === 'showing_wrong' && option === currentTestQuestion.correct_answer,
                'disabled': feedbackState.status !== 'waiting'
              }"
              @click="handleTestAnswer(option)"
            >
              <span class="option-letter">{{ String.fromCharCode(65 + index) }}</span>
              <span class="option-text">{{ option }}</span>
              <span v-if="feedbackState.status === 'showing_correct' && feedbackState.selectedOption === option"
                    class="feedback-icon correct-icon">✓</span>
              <span v-if="feedbackState.status === 'showing_wrong' && feedbackState.selectedOption === option"
                    class="feedback-icon wrong-icon">✗</span>
              <span v-if="feedbackState.status === 'showing_wrong' && option === currentTestQuestion.correct_answer"
                    class="feedback-icon correct-icon">✓</span>
            </button>
          </div>

          <!-- 下一题按钮，只在答错时显示 -->
          <button
            v-if="feedbackState.status === 'showing_wrong'"
            class="next-btn"
            @click="advanceToNext"
          >
            下一题 →
          </button>
        </div>
      </template>

      <!-- 完成阶段 -->
      <template v-else-if="learnPhase === 'finished'">
        <div class="finished">
          <div class="finished-icon">🎉</div>
          <h2>今日学习完成！</h2>
          <p>已学习 {{ learnStore.learnedWordIds.length }} 个新词</p>
          <p v-if="testAnswers.length > 0" class="test-result">
            测试正确率：{{ correctRate }}%
          </p>
          <p class="remaining">剩余新词：{{ learnStore.remainingCount }} 个</p>

          <!-- 错题汇总 -->
          <div v-if="wrongAnswers.length > 0" class="wrong-answers-summary">
            <h3>答错的词</h3>
            <div class="wrong-answers-list">
              <div v-for="(answer, index) in wrongAnswers" :key="index" class="wrong-answer-item">
                <div class="wrong-word">{{ answer.word }}</div>
                <div class="wrong-details">
                  <div class="wrong-example">"{{ answer.example_sentence }}"</div>
                  <div class="wrong-answers-comparison">
                    <span class="user-answer">你的答案：{{ answer.user_answer }}</span>
                    <span class="correct-answer-highlight">正确答案：{{ answer.correct_answer }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

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

/* 选项按钮状态 */
.option-btn.disabled {
  cursor: not-allowed;
  pointer-events: none;
}

.option-btn.selected {
  border-color: #667eea;
}

.option-btn.correct {
  background: #e8f5e9;
  border-color: #4caf50;
  color: #2e7d32;
}

.option-btn.wrong {
  background: #ffebee;
  border-color: #f44336;
  color: #c62828;
}

.option-btn.correct-answer {
  background: #e8f5e9;
  border-color: #4caf50;
  color: #2e7d32;
}

/* 选项按钮内部布局 */
.option-btn {
  display: flex;
  align-items: center;
  gap: 12px;
}

.option-letter {
  font-weight: 600;
  color: #667eea;
  flex-shrink: 0;
  font-size: 14px;
}

.option-text {
  flex: 1;
}

/* 反馈图标 */
.feedback-icon {
  margin-left: auto;
  font-size: 20px;
  font-weight: 700;
}

.correct-icon {
  color: #4caf50;
}

.wrong-icon {
  color: #f44336;
}

/* 下一题按钮 */
.next-btn {
  width: 100%;
  max-width: 300px;
  margin: 24px auto 0;
  padding: 14px 32px;
  border: none;
  border-radius: 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.next-btn:hover {
  transform: scale(1.05);
}

/* 错题汇总 */
.wrong-answers-summary {
  width: 100%;
  max-width: 500px;
  margin: 24px 0;
  text-align: left;
}

.wrong-answers-summary h3 {
  font-size: 18px;
  color: #333;
  margin-bottom: 16px;
  text-align: center;
}

.wrong-answers-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.wrong-answer-item {
  background: #fff5f5;
  border-radius: 12px;
  padding: 16px;
  border-left: 4px solid #f44336;
}

.wrong-word {
  font-size: 24px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.wrong-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.wrong-example {
  font-size: 14px;
  color: #666;
  font-style: italic;
}

.wrong-answers-comparison {
  display: flex;
  flex-direction: column;
  gap: 4px;
  font-size: 14px;
}

.user-answer {
  color: #f44336;
}

.correct-answer-highlight {
  color: #4caf50;
  font-weight: 600;
}
</style>
