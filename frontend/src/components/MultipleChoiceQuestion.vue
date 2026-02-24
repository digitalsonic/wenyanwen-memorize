<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  word: string
  exampleSentence: string
  exampleSource: string
  options: string[]
  correctAnswer: string
  mode?: 'review' | 'learning'
  feedback?: {
    status: 'waiting' | 'showing_correct' | 'showing_wrong'
    selectedOption: string | boolean | null
  }
  disabled?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  mode: 'review',
  feedback: () => ({ status: 'waiting', selectedOption: null }),
  disabled: false
})

interface Emits {
  (e: 'answer', value: string): void
  (e: 'next'): void
}

const emit = defineEmits<Emits>()

// 当前题目的唯一 key，用于强制重渲染
const questionKey = computed(() => {
  return props.options.join('-')
})

function handleClick(option: string) {
  if (props.disabled) return
  emit('answer', option)
}

// 判断是否是正确答案
function isCorrectAnswer(option: string): boolean {
  return option === props.correctAnswer
}

// 判断用户是否选了此选项
function isUserSelected(option: string): boolean {
  return props.feedback?.selectedOption === option
}

// 判断是否应该显示正确答案徽章
function shouldShowCorrectBadge(option: string): boolean {
  return props.feedback?.status !== 'waiting' && isCorrectAnswer(option)
}

// 判断用户是否选错了
function isUserWrong(option: string): boolean {
  return props.feedback?.status === 'showing_wrong' && isUserSelected(option)
}
</script>

<template>
  <div class="multiple-choice-question">
    <div class="question-label">请选择正确的释义</div>
    <div class="word">{{ word }}</div>
    <div class="example">{{ exampleSentence }}</div>
    <div class="source">{{ exampleSource }}</div>

    <div class="options">
      <button
        v-for="(option, index) in options"
        :key="`${questionKey}-${index}`"
        class="option-btn"
        :class="{
          'disabled': disabled,
          'is-correct-answer': feedback && feedback.status !== 'waiting' && isCorrectAnswer(option),
          'user-selected': feedback && isUserSelected(option),
          'user-wrong': feedback && isUserWrong(option) && !isCorrectAnswer(option)
        }"
        @click="handleClick(option)"
      >
        <span class="option-letter">{{ String.fromCharCode(65 + index) }}</span>
        <span class="option-text">{{ option }}</span>

        <!-- 正确答案徽章 -->
        <span v-if="shouldShowCorrectBadge(option)" class="correct-answer-badge">正确答案</span>
      </button>
    </div>

    <!-- 反馈状态提示 -->
    <div v-if="feedback && feedback.status !== 'waiting'" class="feedback-message">
      <span v-if="feedback.status === 'showing_correct'" class="correct-text">回答正确！</span>
      <span v-else class="wrong-text">回答错误</span>
    </div>
  </div>
</template>

<style scoped>
.multiple-choice-question {
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
  font-family: 'Noto Serif SC', serif;
  font-size: 48px;
  font-weight: 700;
  color: #333;
  text-align: center;
  margin-bottom: 24px;
}

.example {
  font-family: 'Noto Serif SC', serif;
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

/* 反馈消息 */
.feedback-message {
  text-align: center;
  margin-top: 16px;
  font-size: 16px;
  font-weight: 600;
}

.correct-text {
  color: #4caf50;
}

.wrong-text {
  color: #f44336;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.option-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 12px;
  background: white;
  font-size: 16px;
  text-align: left;
  cursor: pointer;
  transition: all 0.2s;
  position: relative;
}

.option-btn:hover:not(.disabled) {
  border-color: #667eea;
  background: #f8f9ff;
}

.option-btn.disabled {
  cursor: not-allowed;
  pointer-events: none;
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

/* 用户选中但不是正确答案（等待状态时） */
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

.option-letter {
  font-weight: 600;
  color: #667eea;
  flex-shrink: 0;
  font-size: 14px;
}

.option-text {
  flex: 1;
}
</style>
