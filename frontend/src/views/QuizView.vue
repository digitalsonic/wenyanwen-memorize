<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useQuizStore } from '@/stores/quiz'
import MultipleChoiceQuestion from '@/components/MultipleChoiceQuestion.vue'
import type { QuizQuestion } from '@/types'

const router = useRouter()
const quizStore = useQuizStore()

onMounted(() => {
  quizStore.startReview()
})

const currentQuestion = computed(() => quizStore.currentQuestion)
const progress = computed(() => quizStore.progress)

function goBack() {
  router.push('/')
}

function selectAnswer(answer: string | boolean) {
  const q = currentQuestion.value
  if (!q) return

  let isCorrect = false
  if (q.question_type === 'multiple_choice') {
    isCorrect = answer === q.correct_answer
  } else if (q.question_type === 'true_false') {
    isCorrect = answer === q.is_correct
  } else if (q.question_type === 'flashcard') {
    isCorrect = true // Self-graded
  }

  quizStore.submitAnswer({
    word_id: q.word_id,
    question_type: q.question_type,
    user_answer: answer,
    is_correct,
  })

  // Check if finished
  if (quizStore.isFinished) {
    submitQuiz()
  }
}

async function submitQuiz() {
  await quizStore.submitSession()
  if (quizStore.wrongAnswerIds.length > 0) {
    // Handle retry logic
    alert(`有 ${quizStore.wrongAnswerIds.length} 道题答错，请重做`)
  }
}

function getQuestionTitle(question: QuizQuestion): string {
  if (question.question_type === 'multiple_choice') {
    return '单选题'
  } else if (question.question_type === 'true_false') {
    return '判断题'
  } else if (question.question_type === 'flashcard') {
    return '闪卡'
  }
  return '复习'
}
</script>

<template>
  <div class="quiz-view">
    <header class="header">
      <button class="back-btn" @click="goBack">← 返回</button>
      <div class="title">复习</div>
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
      <MultipleChoiceQuestion
        v-else-if="currentQuestion && currentQuestion.question_type === 'multiple_choice'"
        :word="currentQuestion.word"
        :example-sentence="currentQuestion.example_sentence"
        :example-source="currentQuestion.example_source"
        :options="currentQuestion.options"
        :correct-answer="currentQuestion.correct_answer"
        mode="review"
        @answer="selectAnswer"
      />

      <!-- True/False Question -->
      <div
        v-else-if="currentQuestion && currentQuestion.question_type === 'true_false'"
        class="question true-false"
      >
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

        <div class="options">
          <button class="option-btn correct" @click="selectAnswer(true)">
            ✓ 正确
          </button>
          <button class="option-btn wrong" @click="selectAnswer(false)">
            ✗ 错误
          </button>
        </div>
      </div>

      <!-- Flashcard Question -->
      <div
        v-else-if="currentQuestion && currentQuestion.question_type === 'flashcard'"
        class="question flashcard"
      >
        <div class="question-title">{{ getQuestionTitle(currentQuestion) }}</div>
        <div class="word">{{ currentQuestion.word }}</div>
        <div class="example">
          {{ currentQuestion.example_sentence }}
        </div>
        <div class="source">{{ currentQuestion.example_source }}</div>

        <div class="flashcard-actions">
          <button class="option-btn" @click="selectAnswer(true)">
            我想起来了
          </button>
        </div>
      </div>

      <!-- Finished -->
      <div v-else-if="quizStore.isFinished" class="finished">
        <div class="finished-icon">📝</div>
        <h2>复习完成！</h2>
        <p>正确 {{ quizStore.correctCount }} / {{ quizStore.answers.length }} 题</p>
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

.flashcard-actions {
  display: flex;
  justify-content: center;
}

.flashcard-actions .option-btn {
  text-align: center;
  min-width: 200px;
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
</style>
