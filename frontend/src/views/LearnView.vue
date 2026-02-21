<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useLearnStore } from '@/stores/learn'
import { useQuizStore } from '@/stores/quiz'
import { progressApi } from '@/api/client'
import CardView from '@/components/CardView.vue'
import MultipleChoiceQuestion from '@/components/MultipleChoiceQuestion.vue'
import type { QuizQuestion } from '@/types'
import { useQuizFeedbackWithIndex } from '@/composables/useQuizFeedback'

const router = useRouter()
const learnStore = useLearnStore()
const quizStore = useQuizStore()

// 学习阶段: 'learning' | 'testing' | 'finished'
const learnPhase = ref<'learning' | 'testing' | 'finished'>('learning')
const testQuestions = ref<QuizQuestion[]>([])
const currentTestIndex = ref(0)
const testAnswers = ref<Array<{ word_id: string; question_type: string; user_answer: string | boolean; is_correct: boolean }>>([])

// 错题收集
interface WrongAnswer {
  word_id: string
  word: string
  user_answer: string
  correct_answer: string
  example_sentence: string
}

const wrongAnswers = ref<WrongAnswer[]>([])

// 完成后的实际剩余词数（全局剩余量）
const actualRemainingCount = ref<number>(0)

onMounted(() => {
  learnStore.startLearning()
})

// 监听学习完成，自动进入测试阶段
watch(() => learnStore.isFinished, (isFinished) => {
  if (isFinished && learnStore.learnedWordIds.length > 0) {
    startTesting()
  }
})

// 使用 composable 管理测试阶段的反馈
const testFeedback = useQuizFeedbackWithIndex(
  currentTestIndex,
  {
    onAnswer: (answer: string | boolean) => {
      // 记录答案
      const question = testQuestions.value[currentTestIndex.value]
      const is_correct = (answer as string) === question.correct_answer

      testAnswers.value.push({
        word_id: question.word_id,
        question_type: question.question_type,
        user_answer: answer as string,
        is_correct,
      })

      // 收集错题
      if (!is_correct) {
        wrongAnswers.value.push({
          word_id: question.word_id,
          word: question.word,
          user_answer: answer as string,
          correct_answer: question.correct_answer,
          example_sentence: question.example_sentence,
        })
      }
    },
    onNext: () => {
      // 进入下一题
      currentTestIndex.value++

      // 检查是否完成
      if (currentTestIndex.value >= testQuestions.value.length) {
        submitTestResults()
      }
    },
  }
)

// Fisher-Yates shuffle 算法
function shuffleArray<T>(array: T[]): T[] {
  const shuffled = [...array]
  for (let i = shuffled.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]]
  }
  return shuffled
}

// 从其他词中随机选取释义作为干扰项
function getRandomDistractors(excludeWordId: string, count: number, allWords: any[]): string[] {
  const distractors: string[] = []
  const used = new Set<string>()

  for (const word of allWords) {
    if (word.word_id === excludeWordId) continue
    for (const meaning of (word.back?.meanings || [])) {
      if (!used.has(meaning) && distractors.length < count) {
        distractors.push(meaning)
        used.add(meaning)
      }
    }
    if (distractors.length >= count) break
  }

  return distractors
}

async function startTesting() {
  // 开始对刚才学习的词进行测试
  learnPhase.value = 'testing'
  currentTestIndex.value = 0
  testAnswers.value = []
  wrongAnswers.value = []
  testFeedback.resetFeedback()

  // 为每个学习的词生成单选题
  const words = learnStore.session?.words || []
  const allWords = words  // 本次学习的所有词，用于获取干扰项

  testQuestions.value = words.map((card) => {
    const meanings = card.back.meanings || []
    let options: string[]

    if (meanings.length >= 2) {
      // 多义词：使用该词的其他释义作为干扰项
      options = shuffleArray([...meanings])
    } else {
      // 单义词：从其他学习的词中随机选取释义作为干扰项
      const distractors = getRandomDistractors(card.word_id, 3, allWords)
      options = shuffleArray([meanings[0], ...distractors])
    }

    return {
      word_id: card.word_id,
      word: card.word,
      question_type: 'multiple_choice' as const,
      example_sentence: card.front.sentence,
      example_source: card.front.source,
      options,
      correct_answer: meanings[0] || '',
      correct_meaning_id: '',
    }
  })
}

function handleTestAnswer(answer: string) {
  const question = testQuestions.value[currentTestIndex.value]
  const is_correct = answer === question.correct_answer

  // 使用 composable 处理反馈
  testFeedback.handleAnswer(answer, is_correct)
}

async function submitTestResults() {
  // 提交测试结果到后端
  if (testAnswers.value.length > 0) {
    await quizStore.submitDirectAnswers(testAnswers.value)
  }

  // 完成学习
  await learnStore.completeLearning()

  // 获取全局剩余词数
  try {
    const progress = await progressApi.get()
    actualRemainingCount.value = progress.total_words - progress.learned_words
  } catch (e) {
    // 如果获取失败，使用 session 的剩余量作为备选
    actualRemainingCount.value = learnStore.remainingCount
  }

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
          <MultipleChoiceQuestion
            :word="currentTestQuestion.word"
            :example-sentence="currentTestQuestion.example_sentence"
            :example-source="currentTestQuestion.example_source"
            :options="currentTestQuestion.options"
            :correct-answer="currentTestQuestion.correct_answer"
            mode="learning"
            :feedback="testFeedback.feedbackState.value"
            :disabled="testFeedback.feedbackState.value.status !== 'waiting'"
            @answer="handleTestAnswer"
          />

          <!-- 下一题按钮，只在答错时显示 -->
          <button
            v-if="testFeedback.feedbackState.value.status === 'showing_wrong'"
            class="next-btn"
            @click="testFeedback.advanceToNext"
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
          <p class="remaining">剩余新词：{{ actualRemainingCount }} 个</p>

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
