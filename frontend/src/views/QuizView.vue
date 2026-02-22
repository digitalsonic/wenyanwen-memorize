<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useQuizStore } from '@/stores/quiz'
import MultipleChoiceQuestion from '@/components/MultipleChoiceQuestion.vue'
import type { QuizQuestion } from '@/types'
import { useQuizFeedbackWithIndex } from '@/composables/useQuizFeedback'

const router = useRouter()
const route = useRoute()
const quizStore = useQuizStore()

// 错题收集
interface WrongAnswer {
  word_id: string
  word: string
  user_answer: string
  correct_answer: string
  example_sentence: string
}

const wrongAnswers = ref<WrongAnswer[]>([])

// 保存会话中的题目，用于错题展示
const sessionQuestions = ref<QuizQuestion[]>([])

// 闪卡翻转状态
const flashcardFlipped = ref(false)

// Get mode from query param
const mode = computed(() => route.query.mode as string | null)
const level = computed(() => {
  const levelParam = route.query.level
  return levelParam ? Number(levelParam) : null
})

const currentQuestion = computed(() => quizStore.currentQuestion)
const progress = computed(() => quizStore.progress)

onMounted(() => {
  quizStore.startReview(level.value)
})

// 监听 session 变化，保存题目用于错题展示
const session = computed(() => quizStore.session)
watch(session, (newSession) => {
  if (newSession) {
    sessionQuestions.value = newSession.questions
  }
}, { immediate: true })

// 监听题目变化，重置闪卡翻转状态
watch(currentQuestion, () => {
  flashcardFlipped.value = false
})

const title = computed(() => {
  return mode.value === 'review' ? '今日复习' : '复习'
})

function goBack() {
  router.push('/')
}

// 提交答案到 store
function submitAnswer(answer: string | boolean | number, isCorrect: boolean) {
  const q = currentQuestion.value
  if (!q) return

  quizStore.submitAnswer({
    word_id: q.word_id,
    question_type: q.question_type,
    user_answer: answer,
    is_correct: isCorrect,
  })

  // 收集错题
  if (!isCorrect) {
    if (q.question_type === 'multiple_choice') {
      wrongAnswers.value.push({
        word_id: q.word_id,
        word: q.word,
        user_answer: String(answer),
        correct_answer: (q as any).correct_answer,
        example_sentence: q.example_sentence,
      })
    } else if (q.question_type === 'true_false') {
      const tfq = q as any
      const correctAnswer = tfq.is_correct ? '正确' : '错误'
      const userAnswer = answer ? '正确' : '错误'
      wrongAnswers.value.push({
        word_id: q.word_id,
        word: q.word,
        user_answer: userAnswer,
        correct_answer: correctAnswer,
        example_sentence: `${q.example_sentence}（释义：${tfq.given_meaning}）`,
      })
    } else if (q.question_type === 'flashcard') {
      const fc = q as any
      const assessmentLabels = ['模糊', '清晰', '不确定']
      wrongAnswers.value.push({
        word_id: q.word_id,
        word: q.word,
        user_answer: assessmentLabels[answer as number] || String(answer),
        correct_answer: fc.correct_meaning,
        example_sentence: q.example_sentence,
      })
    }
  }
}

// 进入下一题
function goToNext() {
  quizStore.goToNext()
  if (quizStore.isFinished) {
    submitQuiz()
  }
}

async function submitQuiz() {
  await quizStore.submitSession()
  if (quizStore.wrongAnswerIds.length > 0) {
    alert(`有 ${quizStore.wrongAnswerIds.length} 道题答错，请重做`)
  }
}

// 使用 composable 管理反馈状态
const feedback = useQuizFeedbackWithIndex(
  computed(() => quizStore.currentIndex),
  {
    onAnswer: submitAnswer,
    onNext: goToNext,
    onCorrectAutoAdvance: true,
    autoAdvanceDelay: 1000
  }
)

// 处理选项点击
function selectAnswer(answer: string | boolean) {
  const q = currentQuestion.value
  if (!q) return

  // 判断答案是否正确
  let isCorrect: boolean = false

  if (q.question_type === 'multiple_choice') {
    const mcq = q as any
    isCorrect = (answer as string) === mcq.correct_answer
    feedback.handleAnswer(answer, isCorrect)
  } else if (q.question_type === 'true_false') {
    const tfq = q as any
    isCorrect = (answer as boolean) === tfq.is_correct
    feedback.handleAnswer(answer, isCorrect)
  }
}

// 闪卡翻转
function flipFlashcard() {
  flashcardFlipped.value = true
}

// 闪卡评估选择（0=模糊/答错, 1=清晰/答对, 2=不确定/答错）
function selectFlashcardAnswer(assessment: number) {
  const q = currentQuestion.value
  if (!q || q.question_type !== 'flashcard') return

  const isCorrect = assessment === 1  // 只有"清晰"算对
  feedback.handleAnswer(assessment, isCorrect)
}

function getQuestionTitle(question: QuizQuestion): string {
  if (question.question_type === 'multiple_choice') {
    return '单选题'
  } else if (question.question_type === 'true_false') {
    return '判断题'
  } else if (question.question_type === 'flashcard') {
    return '闪卡回忆'
  }
  return '复习'
}
</script>

<template>
  <div class="quiz-view">
    <header class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <div class="title">{{ title }}</div>
      <div class="progress">{{ Math.round(progress) }}%</div>
    </header>

    <div class="progress-bar">
      <div class="progress-fill" :style="{ width: `${progress}%` }"></div>
    </div>

    <main class="main-content">
      <div v-if="quizStore.isLoading" class="loading">
        加载中...
      </div>

      <div v-else-if="quizStore.error" class="error">
        {{ quizStore.error }}
      </div>

      <!-- Multiple Choice Question -->
      <div v-else-if="currentQuestion && currentQuestion.question_type === 'multiple_choice'" class="question-wrapper">
        <MultipleChoiceQuestion
          :word="currentQuestion.word"
          :example-sentence="currentQuestion.example_sentence"
          :example-source="currentQuestion.example_source"
          :options="currentQuestion.options"
          :correct-answer="currentQuestion.correct_answer"
          mode="learning"
          :feedback="feedback.feedbackState.value"
          :disabled="feedback.feedbackState.value.status !== 'waiting'"
          @answer="selectAnswer"
        />

        <!-- 下一题按钮，只在答错时显示 -->
        <button
          v-if="feedback.feedbackState.value.status === 'showing_wrong'"
          class="next-btn"
          @click="feedback.advanceToNext"
        >
          下一题 →
        </button>
      </div>

      <!-- True/False Question -->
      <div
        v-else-if="currentQuestion && currentQuestion.question_type === 'true_false'"
        class="question-wrapper"
      >
        <div class="question true-false">
          <div class="question-title">{{ getQuestionTitle(currentQuestion) }}</div>
          <div class="word">{{ currentQuestion.word }}</div>
          <div class="example">
            {{ currentQuestion.example_sentence }}
          </div>
          <div class="source">{{ currentQuestion.example_source }}</div>

          <div class="statement">
            <span class="statement-label">释义：</span>
            {{ currentQuestion.given_meaning }}
          </div>

          <!-- 反馈状态提示 -->
          <div v-if="feedback.feedbackState.value.status !== 'waiting'" class="feedback-message">
            <span v-if="feedback.feedbackState.value.status === 'showing_correct'" class="correct-text">回答正确！</span>
            <span v-else class="wrong-text">回答错误</span>
          </div>

          <!-- 答错时显示正确释义 -->
          <div v-if="feedback.feedbackState.value.status === 'showing_wrong'" class="correct-meaning-box">
            <span class="correct-meaning-icon">✓</span>
            <span class="correct-meaning-label">正确释义：</span>
            <span class="correct-meaning-text">{{ currentQuestion.correct_meaning }}</span>
          </div>

          <div class="options">
            <button
              class="option-btn correct-option"
              :class="{
                'disabled': feedback.feedbackState.value.status !== 'waiting',
                'is-correct-answer': feedback.feedbackState.value.status !== 'waiting' && currentQuestion.is_correct === true,
                'user-selected': feedback.feedbackState.value.selectedOption === true,
                'user-wrong': feedback.feedbackState.value.status === 'showing_wrong' &&
                             feedback.feedbackState.value.selectedOption === true
              }"
              @click="selectAnswer(true)"
            >
              <span class="option-icon">✓</span>
              正确
              <span v-if="feedback.feedbackState.value.status !== 'waiting' && currentQuestion.is_correct === true" class="correct-answer-badge">正确答案</span>
            </button>
            <button
              class="option-btn wrong-option"
              :class="{
                'disabled': feedback.feedbackState.value.status !== 'waiting',
                'is-correct-answer': feedback.feedbackState.value.status !== 'waiting' && currentQuestion.is_correct === false,
                'user-selected': feedback.feedbackState.value.selectedOption === false,
                'user-wrong': feedback.feedbackState.value.status === 'showing_wrong' &&
                             feedback.feedbackState.value.selectedOption === false
              }"
              @click="selectAnswer(false)"
            >
              <span class="option-icon">✗</span>
              错误
              <span v-if="feedback.feedbackState.value.status !== 'waiting' && currentQuestion.is_correct === false" class="correct-answer-badge">正确答案</span>
            </button>
          </div>
        </div>

        <!-- 下一题按钮，只在答错时显示 -->
        <button
          v-if="feedback.feedbackState.value.status === 'showing_wrong'"
          class="next-btn"
          @click="feedback.advanceToNext"
        >
          下一题 →
        </button>
      </div>

      <!-- Flashcard Question -->
      <div
        v-else-if="currentQuestion && currentQuestion.question_type === 'flashcard'"
        class="question-wrapper flashcard-enhanced"
      >
        <!-- 正面（未翻转） -->
        <div v-if="!flashcardFlipped" class="flashcard-front">
          <div class="question-title">{{ getQuestionTitle(currentQuestion) }}</div>
          <div class="word">{{ currentQuestion.word }}</div>
          <div class="example">{{ currentQuestion.example_sentence }}</div>
          <div class="source">{{ currentQuestion.example_source }}</div>

          <button class="show-answer-btn" @click="flipFlashcard">
            显示答案 →
          </button>
        </div>

        <!-- 背面（已翻转 + 评估选项） -->
        <div v-else class="flashcard-back">
          <div class="question-title">{{ getQuestionTitle(currentQuestion) }}</div>
          <div class="word">{{ currentQuestion.word }}</div>
          <div class="example">{{ currentQuestion.example_sentence }}</div>
          <div class="source">{{ currentQuestion.example_source }}</div>

          <!-- 答案区域 -->
          <div class="answer-section">
            <div class="answer-label">正确释义</div>
            <div class="answer-text">{{ currentQuestion.correct_meaning }}</div>

            <!-- 助记口诀（可选） -->
            <div v-if="currentQuestion.mnemonics" class="mnemonics-box">
              <span class="mnemonics-icon">💡</span>
              {{ currentQuestion.mnemonics }}
            </div>
          </div>

          <!-- 评估选项 -->
          <div class="assessment-options">
            <button
              class="assessment-btn fuzzy"
              :class="{
                'disabled': feedback.feedbackState.value.status !== 'waiting',
                'selected': feedback.feedbackState.value.selectedOption === 0
              }"
              @click="selectFlashcardAnswer(0)"
            >
              <span class="assessment-icon">😕</span>
              <span class="assessment-text">模糊</span>
              <span class="assessment-hint">完全没想起</span>
            </button>
            <button
              class="assessment-btn clear"
              :class="{
                'disabled': feedback.feedbackState.value.status !== 'waiting',
                'selected': feedback.feedbackState.value.selectedOption === 1
              }"
              @click="selectFlashcardAnswer(1)"
            >
              <span class="assessment-icon">😊</span>
              <span class="assessment-text">清晰</span>
              <span class="assessment-hint">立即想起</span>
            </button>
            <button
              class="assessment-btn uncertain"
              :class="{
                'disabled': feedback.feedbackState.value.status !== 'waiting',
                'selected': feedback.feedbackState.value.selectedOption === 2
              }"
              @click="selectFlashcardAnswer(2)"
            >
              <span class="assessment-icon">🤔</span>
              <span class="assessment-text">不确定</span>
              <span class="assessment-hint">犹豫/看到才想起</span>
            </button>
          </div>
        </div>

        <!-- 下一题按钮，只在答错时显示 -->
        <button
          v-if="feedback.feedbackState.value.status === 'showing_wrong'"
          class="next-btn"
          @click="feedback.advanceToNext"
        >
          下一题 →
        </button>
      </div>

      <!-- Finished -->
      <div v-else-if="quizStore.isFinished" class="finished">
        <div class="finished-icon">📝</div>
        <h2>复习完成！</h2>
        <p>正确 {{ quizStore.correctCount }} / {{ quizStore.answers.length }} 题</p>

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

      <!-- No questions -->
      <div v-else class="no-questions">
        <div class="icon">😊</div>
        <h2>暂无到期复习</h2>
        <p>目前没有需要复习的词语</p>
        <button class="btn primary" @click="goBack">返回首页</button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.quiz-view {
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
  min-height: 60vh;
}

.loading,
.error,
.finished,
.no-questions {
  text-align: center;
}

.icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.question {
  width: 100%;
  max-width: 500px;
}

.question-title {
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

.statement {
  background: #f5f5f5;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 24px;
  font-size: 16px;
  line-height: 1.6;
}

.statement-label {
  font-weight: 600;
  color: #667eea;
}

.options {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.option-btn {
  padding: 14px 24px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  font-size: 16px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.option-btn:hover:not(.disabled) {
  border-color: #667eea;
  background: #f8f9ff;
}

.option-btn.disabled {
  cursor: not-allowed;
  pointer-events: none;
}

/* 判断题专用样式 */
.feedback-message {
  text-align: center;
  margin-bottom: 16px;
  font-size: 16px;
  font-weight: 600;
}

.correct-text {
  color: #4caf50;
}

.wrong-text {
  color: #f44336;
}

.option-btn {
  position: relative;
}

.option-icon {
  font-weight: 700;
  font-size: 18px;
}

/* 正确答案标识 - 绿色背景和边框 */
.option-btn.is-correct-answer {
  background: #e8f5e9;
  border-color: #4caf50;
  color: #2e7d32;
}

/* 用户选错时的标识 - 红色背景和边框 */
.option-btn.user-wrong {
  background: #ffebee;
  border-color: #f44336;
  color: #c62828;
}

/* 用户选中的视觉反馈（用于正确答案或非正确答案按钮） */
.option-btn.user-selected:not(.is-correct-answer):not(.user-wrong) {
  border-color: #667eea;
  background: #f8f9ff;
}

/* 正确答案徽章 */
.correct-answer-badge {
  position: absolute;
  top: -8px;
  right: -8px;
  background: #4caf50;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 8px;
  font-weight: 600;
}

/* 正确释义提示框 */
.correct-meaning-box {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  background: #e8f5e9;
  border: 1px solid #4caf50;
  border-radius: 12px;
  padding: 16px;
  margin-bottom: 20px;
}

.correct-meaning-icon {
  color: #4caf50;
  font-weight: 700;
  font-size: 20px;
  flex-shrink: 0;
}

.correct-meaning-label {
  font-weight: 600;
  color: #4caf50;
  flex-shrink: 0;
}

.correct-meaning-text {
  color: #2e7d32;
  line-height: 1.5;
}

/* 闪卡增强样式 */
.flashcard-enhanced {
  width: 100%;
  max-width: 500px;
}

.flashcard-front,
.flashcard-back {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.show-answer-btn {
  width: 100%;
  padding: 16px;
  margin-top: 32px;
  border: 2px dashed #667eea;
  border-radius: 12px;
  background: #f8f9ff;
  color: #667eea;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.show-answer-btn:hover {
  background: #667eea;
  color: white;
  border-style: solid;
}

.answer-section {
  background: #e8f5e9;
  border-radius: 12px;
  padding: 20px;
  margin: 24px 0;
  border-left: 4px solid #4caf50;
}

.answer-label {
  font-size: 12px;
  color: #4caf50;
  font-weight: 700;
  margin-bottom: 8px;
  text-transform: uppercase;
}

.answer-text {
  font-size: 18px;
  color: #2e7d32;
  line-height: 1.6;
}

.mnemonics-box {
  margin-top: 16px;
  padding: 12px;
  background: #fff9c4;
  border-radius: 8px;
  font-size: 14px;
  color: #827717;
  display: flex;
  align-items: center;
  gap: 8px;
}

.mnemonics-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.assessment-options {
  display: flex;
  gap: 12px;
  justify-content: center;
  flex-wrap: wrap;
}

.assessment-btn {
  flex: 1;
  min-width: 90px;
  padding: 16px 12px;
  border: 2px solid;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.assessment-btn:hover:not(.disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.assessment-btn.disabled {
  cursor: not-allowed;
  pointer-events: none;
}

.assessment-btn.selected {
  opacity: 1;
  transform: scale(1.05);
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.3);
}

.assessment-btn.selected.disabled {
  transform: scale(1);
}

.assessment-btn.fuzzy {
  border-color: #f44336;
}

.assessment-btn.fuzzy:hover:not(.disabled) {
  background: #ffebee;
}

.assessment-btn.clear {
  border-color: #4caf50;
}

.assessment-btn.clear:hover:not(.disabled) {
  background: #e8f5e9;
}

.assessment-btn.uncertain {
  border-color: #ff9800;
}

.assessment-btn.uncertain:hover:not(.disabled) {
  background: #fff3e0;
}

.assessment-icon {
  font-size: 24px;
}

.assessment-text {
  font-size: 16px;
  font-weight: 600;
}

.assessment-hint {
  font-size: 11px;
  opacity: 0.7;
  text-align: center;
}

.flashcard-actions {
  display: flex;
  justify-content: center;
}

.flashcard-actions .option-btn {
  text-align: center;
  min-width: 200px;
}

.question-wrapper {
  width: 100%;
  max-width: 500px;
}

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

.finished h2,
.no-questions h2 {
  font-size: 24px;
  color: #333;
  margin-bottom: 8px;
}

.finished p,
.no-questions p {
  color: #666;
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
