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
    selectedOption: string | null
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

function getOptionClass(option: string): Record<string, boolean> {
  const classes: Record<string, boolean> = {
    disabled: props.disabled
  }

  if (props.mode === 'learning' && props.feedback) {
    // 学习模式：显示反馈状态
    return {
      ...classes,
      selected: props.feedback.status !== 'waiting' && props.feedback.selectedOption === option,
      correct: props.feedback.status === 'showing_correct' && props.feedback.selectedOption === option,
      wrong: props.feedback.status === 'showing_wrong' && props.feedback.selectedOption === option,
      'correct-answer': props.feedback.status === 'showing_wrong' && option === props.correctAnswer
    }
  }

  // 复习模式：无特殊样式
  return classes
}

function shouldShowCorrectIcon(option: string): boolean {
  if (props.mode !== 'learning' || !props.feedback) return false
  if (props.feedback.status === 'showing_correct' && props.feedback.selectedOption === option) return true
  if (props.feedback.status === 'showing_wrong' && option === props.correctAnswer) return true
  return false
}

function shouldShowWrongIcon(option: string): boolean {
  if (props.mode !== 'learning' || !props.feedback) return false
  return props.feedback.status === 'showing_wrong' && props.feedback.selectedOption === option
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
        :class="getOptionClass(option)"
        @click="handleClick(option)"
      >
        <span class="option-letter">{{ String.fromCharCode(65 + index) }}</span>
        <span class="option-text">{{ option }}</span>

        <!-- 学习模式的反馈图标 -->
        <span v-if="shouldShowCorrectIcon(option)" class="feedback-icon correct-icon">✓</span>
        <span v-if="shouldShowWrongIcon(option)" class="feedback-icon wrong-icon">✗</span>
      </button>
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
}

.option-btn:hover:not(.disabled) {
  border-color: #667eea;
  background: #f8f9ff;
}

.option-btn.disabled {
  cursor: not-allowed;
  pointer-events: none;
}

/* 学习模式 - 选中状态（反馈中） */
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

.option-letter {
  font-weight: 600;
  color: #667eea;
  flex-shrink: 0;
  font-size: 14px;
}

.option-text {
  flex: 1;
}

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
</style>
