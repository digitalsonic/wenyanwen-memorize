<template>
  <div class="quiz-view">
    <div v-if="!quizStore.session && !quizStore.isLoading" class="quiz-start">
      <h2>开始练习</h2>
      <p>选择题数量：</p>
      <div class="quiz-options">
        <button @click="quizStore.startQuiz(10)">10 题</button>
        <button @click="quizStore.startQuiz(20)">20 题</button>
        <button @click="quizStore.startQuiz(50)">50 题</button>
      </div>
    </div>

    <div v-if="quizStore.isLoading" class="quiz-loading">
      <p>加载中...</p>
    </div>

    <div v-if="quizStore.error" class="quiz-error">
      <p>{{ quizStore.error }}</p>
      <button @click="quizStore.reset()">重试</button>
    </div>

    <div v-if="quizStore.session && !quizStore.isFinished" class="quiz-progress">
      <div class="progress-bar">
        <div class="progress-fill" :style="{ width: quizStore.progress + '%' }"></div>
      </div>
      <p class="progress-text">
        {{ quizStore.currentIndex + 1 }} / {{ quizStore.session?.total_count }}
      </p>
    </div>

    <div v-if="quizStore.currentQuestion" class="quiz-card">
      <h2 class="quiz-word">{{ quizStore.currentQuestion.word }}</h2>
      <p class="quiz-type">{{ quizStore.currentQuestion.question_type }}</p>
      <div class="quiz-options">
        <button
          v-for="(option, index) in quizStore.currentQuestion.options"
          :key="index"
          @click="selectAnswer(option)"
          class="option-button"
        >
          {{ option }}
        </button>
      </div>
    </div>

    <div v-if="quizStore.isFinished && quizStore.session" class="quiz-results">
      <h2>练习完成！</h2>
      <div class="results-summary">
        <p>答对：{{ quizStore.correctCount }} 题</p>
        <p>答错：{{ quizStore.answers.length - quizStore.correctCount }} 题</p>
        <p>正确率：{{ ((quizStore.correctCount / quizStore.answers.length) * 100).toFixed(1) }}%</p>
      </div>
      <button @click="quizStore.reset()" class="restart-button">再来一局</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useQuizStore } from '@/stores/quiz'

const quizStore = useQuizStore()

function selectAnswer(option: string) {
  if (!quizStore.currentQuestion) return
  const isCorrect = option === quizStore.currentQuestion.correct_answer
  quizStore.submitAnswer({
    question_id: quizStore.currentQuestion.word,
    user_answer: option,
    is_correct: isCorrect,
  })
}
</script>

<style scoped>
.quiz-view {
  max-width: 600px;
  margin: 0 auto;
}

.quiz-start,
.quiz-loading,
.quiz-error,
.quiz-results {
  text-align: center;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.quiz-options {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-top: 1.5rem;
}

.quiz-options button {
  padding: 0.75rem 1.5rem;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.2s;
}

.quiz-options button:hover {
  background: #667eea;
  color: white;
}

.quiz-progress {
  margin-bottom: 1.5rem;
}

.progress-bar {
  height: 8px;
  background: #e5e7eb;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text {
  text-align: center;
  margin-top: 0.5rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.quiz-card {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.quiz-word {
  font-size: 2.5rem;
  text-align: center;
  margin-bottom: 0.5rem;
  color: #1f2937;
}

.quiz-type {
  text-align: center;
  color: #6b7280;
  margin-bottom: 2rem;
}

.option-button {
  display: block;
  width: 100%;
  padding: 1rem;
  margin-bottom: 0.75rem;
  border: 2px solid #e5e7eb;
  background: white;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
  text-align: left;
  transition: all 0.2s;
}

.option-button:hover {
  border-color: #667eea;
  background: #f9fafb;
}

.results-summary {
  margin: 1.5rem 0;
  font-size: 1.125rem;
}

.restart-button {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1rem;
}
</style>
