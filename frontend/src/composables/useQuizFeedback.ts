import { ref, watch, nextTick, onUnmounted } from 'vue'

export interface FeedbackState {
  status: 'waiting' | 'showing_correct' | 'showing_wrong'
  selectedOption: string | boolean | null
  autoAdvanceTimer: ReturnType<typeof setTimeout> | null
}

export interface QuizFeedbackOptions {
  onAnswer: (answer: string | boolean, isCorrect: boolean) => void  // 添加 isCorrect 参数
  onNext?: () => void  // 下一题回调
  onCorrectAutoAdvance?: boolean  // 答对后是否自动跳转，默认 true
  autoAdvanceDelay?: number  // 自动跳转延迟，默认 1000ms
}

export function useQuizFeedback(options: QuizFeedbackOptions) {
  const {
    onAnswer,
    onNext,
    onCorrectAutoAdvance = true,
    autoAdvanceDelay = 1000
  } = options

  const feedbackState = ref<FeedbackState>({
    status: 'waiting',
    selectedOption: null,
    autoAdvanceTimer: null
  })

  // 清理定时器
  function clearAutoAdvance() {
    if (feedbackState.value.autoAdvanceTimer) {
      clearTimeout(feedbackState.value.autoAdvanceTimer)
      feedbackState.value.autoAdvanceTimer = null
    }
  }

  // 组件卸载时清理
  onUnmounted(() => {
    clearAutoAdvance()
  })

  // 重置反馈状态
  function resetFeedback() {
    clearAutoAdvance()
    feedbackState.value = {
      status: 'waiting',
      selectedOption: null,
      autoAdvanceTimer: null
    }
  }

  // 处理答案
  function handleAnswer(answer: string | boolean, isCorrect: boolean) {
    // 防止重复点击
    if (feedbackState.value.status !== 'waiting') return

    // 清理现有定时器
    clearAutoAdvance()

    // 更新反馈状态
    feedbackState.value = {
      status: isCorrect ? 'showing_correct' : 'showing_wrong',
      selectedOption: answer,
      autoAdvanceTimer: null
    }

    // 调用外部回调，传递 answer 和 isCorrect（立即提交答案）
    onAnswer(answer, isCorrect)

    // 答对时自动跳转下一题（延迟后重置状态并进入下一题）
    // 答错时等待用户手动点击下一题
    if (isCorrect && onCorrectAutoAdvance) {
      feedbackState.value.autoAdvanceTimer = setTimeout(() => {
        resetFeedback()
        onNext?.()
      }, autoAdvanceDelay)
    }
    // 注意：答错时不调用 onNext()，等待用户点击下一题按钮
  }

  // 进入下一题（手动，用于答错后）
  function advanceToNext() {
    clearAutoAdvance()
    resetFeedback()
    onNext?.()
  }

  return {
    feedbackState,
    handleAnswer,
    advanceToNext,
    resetFeedback,
    clearAutoAdvance
  }
}

// 扩展版本：监听索引变化自动重置
export function useQuizFeedbackWithIndex(
  currentIndexRef: { value: number },
  options: QuizFeedbackOptions
) {
  const feedback = useQuizFeedback(options)

  // 监听索引变化，重置反馈状态
  watch(() => currentIndexRef.value, async () => {
    feedback.resetFeedback()
    await nextTick()
  })

  return feedback
}
