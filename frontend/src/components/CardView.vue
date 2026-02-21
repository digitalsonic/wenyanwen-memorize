<script setup lang="ts">
import { computed, ref, watch, nextTick } from 'vue'
import type { CardQuestion } from '@/types'

interface Props {
  card: CardQuestion
  isFlipped: boolean
}

interface Emits {
  (e: 'flip'): void
  (e: 'learned'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// Track heights for both sides
const frontHeight = ref<number>(280)
const backHeight = ref<number>(280)
const frontRef = ref<HTMLElement | null>(null)
const backRef = ref<HTMLElement | null>(null)

// Calculate card height based on current flip state
const cardHeight = computed(() => {
  const baseHeight = props.isFlipped ? backHeight.value : frontHeight.value
  // Add a little buffer for comfortable viewing
  return Math.max(baseHeight, 280)
})

// Measure a specific element's scroll height
const measureElement = (el: HTMLElement | null) => {
  if (!el) return 280
  // Get the actual content height
  const inner = el.querySelector('.card-inner') as HTMLElement
  if (inner) {
    return inner.scrollHeight
  }
  return el.scrollHeight
}

// Measure heights on mount and when content changes
const measureHeights = async () => {
  await nextTick()
  if (frontRef.value) {
    frontHeight.value = measureElement(frontRef.value)
  }
  if (backRef.value) {
    backHeight.value = measureElement(backRef.value)
  }
}

// Watch for card changes
watch(() => props.card, async () => {
  // Reset to default height first to allow proper shrinkage
  frontHeight.value = 280
  backHeight.value = 280
  // Wait for DOM to update with new height
  await nextTick()
  // Then measure actual content height
  measureHeights()
}, { immediate: true })

// Also measure after flip to ensure accuracy
watch(() => props.isFlipped, () => {
  nextTick(() => {
    measureHeights()
  })
})

// Measure on mount
measureHeights()
</script>

<template>
  <div class="card-wrapper">
    <div
      class="card-container"
      :class="{ flipped: isFlipped }"
      :style="{ height: `${cardHeight}px` }"
    >
      <!-- Front of card -->
      <div
        ref="frontRef"
        class="card-side card-front"
        @click="emit('flip')"
      >
        <div class="card-inner">
          <div class="word-character">{{ card.word }}</div>
          <div class="word-pinyin" v-if="card.pinyin">{{ card.pinyin }}</div>

          <div class="divider"></div>

          <div class="example-section">
            <p class="example-text">{{ card.front.sentence }}</p>
            <p class="example-source">——《 {{ card.front.source }} 》</p>
          </div>

          <div class="tap-hint">
            <span class="tap-icon">&#8635;</span>
            <span class="tap-text">轻触翻转</span>
          </div>
        </div>
      </div>

      <!-- Back of card -->
      <div
        ref="backRef"
        class="card-side card-back"
        @click="emit('flip')"
      >
        <div class="card-inner">
          <div class="word-character small">{{ card.word }}</div>

          <div class="meanings-section">
            <div class="meanings-list">
              <div
                v-for="(meaning, index) in card.back.meanings"
                :key="index"
                class="meaning-item"
              >
                <span class="meaning-number">{{ index + 1 }}.</span>
                <span class="meaning-text">{{ meaning }}</span>
              </div>
            </div>
          </div>

          <div class="mnemonics-section" v-if="card.back.mnemonics">
            <div class="mnemonics-header">
              <span class="seal">记</span>
              <span class="mnemonics-label">记忆口诀</span>
            </div>
            <p class="mnemonics-text">{{ card.back.mnemonics }}</p>
          </div>

          <div class="tap-hint">
            <span class="tap-icon">&#8634;</span>
            <span class="tap-text">轻触返回</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Action buttons -->
    <div class="actions" :class="{ visible: isFlipped }">
      <button class="action-btn primary" @click.stop="emit('learned')">
        <span class="btn-icon">✓</span>
        <span class="btn-text">记住了</span>
      </button>
    </div>
  </div>
</template>

<style scoped>
/* Import Chinese serif font for traditional feel */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600;700&family=ZCOOL+KuaiLe&display=swap');

.card-wrapper {
  width: 100%;
  max-width: 420px;
  margin: 0 auto;
}

.card-container {
  position: relative;
  width: 100%;
  transition: height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  transform-style: preserve-3d;
  perspective: 1200px;
}

.card-side {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  -webkit-backface-visibility: hidden;
  transition: transform 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  cursor: pointer;
  border-radius: 24px;
  overflow: hidden;
}

.card-front {
  background: linear-gradient(145deg, #faf9f6 0%, #f5f3ed 100%);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.02),
    0 12px 24px rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(0, 0, 0, 0.04);
}

.card-back {
  transform: rotateY(180deg);
  background: linear-gradient(145deg, #f0f4f8 0%, #e8eef5 100%);
  box-shadow:
    0 4px 6px rgba(0, 0, 0, 0.02),
    0 12px 24px rgba(0, 0, 0, 0.04),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  border: 1px solid rgba(102, 126, 234, 0.08);
}

.card-container.flipped .card-front {
  transform: rotateY(180deg);
}

.card-container.flipped .card-back {
  transform: rotateY(0deg);
}

.card-inner {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 28px;
  box-sizing: border-box;
  overflow-y: auto;
  /* Custom scrollbar */
  scrollbar-width: thin;
  scrollbar-color: rgba(0, 0, 0, 0.1) transparent;
}

.card-inner::-webkit-scrollbar {
  width: 4px;
}

.card-inner::-webkit-scrollbar-track {
  background: transparent;
}

.card-inner::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.1);
  border-radius: 2px;
}

/* Typography */
.word-character {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(42px, 10vw, 64px);
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.1;
  letter-spacing: 0.05em;
  margin-bottom: 4px;
}

.word-character.small {
  font-size: clamp(28px, 7vw, 36px);
  color: #2c3e50;
}

.word-pinyin {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(16px, 4vw, 20px);
  font-weight: 400;
  color: #8b7355;
  margin-bottom: 20px;
  letter-spacing: 0.1em;
}

.divider {
  width: 60px;
  height: 2px;
  background: linear-gradient(90deg, transparent, #c44d1d, transparent);
  margin: 8px 0 20px;
}

.example-section {
  text-align: center;
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  width: 100%;
  max-width: 280px;
}

.example-text {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(15px, 4vw, 18px);
  color: #2c2c2c;
  line-height: 1.8;
  margin-bottom: 12px;
  font-weight: 500;
}

.example-source {
  font-family: 'Noto Serif SC', serif;
  font-size: clamp(11px, 3vw, 13px);
  color: #888;
  font-style: italic;
}

.meanings-section {
  width: 100%;
  max-width: 300px;
  margin: 16px 0;
}

.meanings-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.meaning-item {
  display: flex;
  align-items: flex-start;
  padding: 12px 16px;
  background: rgba(255, 255, 255, 0.6);
  border-radius: 12px;
  border-left: 3px solid #c44d1d;
}

.meaning-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  color: #2c2c2c;
  line-height: 1.6;
  flex: 1;
}

.meaning-number {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  font-weight: 600;
  color: #c44d1d;
  margin-right: 8px;
  flex-shrink: 0;
}

.mnemonics-section {
  width: 100%;
  max-width: 300px;
  background: linear-gradient(135deg, rgba(196, 77, 29, 0.08) 0%, rgba(196, 77, 29, 0.04) 100%);
  border-radius: 16px;
  padding: 16px;
  margin: 12px 0 20px;
  border: 1px solid rgba(196, 77, 29, 0.1);
}

.mnemonics-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.seal {
  width: 24px;
  height: 24px;
  background: #c44d1d;
  color: white;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-family: 'ZCOOL KuaiLe', cursive;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 2px 4px rgba(196, 77, 29, 0.3);
}

.mnemonics-label {
  font-family: 'Noto Serif SC', serif;
  font-size: 12px;
  font-weight: 600;
  color: #c44d1d;
  letter-spacing: 0.05em;
}

.mnemonics-text {
  font-family: 'Noto Serif SC', serif;
  font-size: 14px;
  color: #4a4a4a;
  line-height: 1.7;
  margin: 0;
  font-style: italic;
}

.tap-hint {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: auto;
  padding-top: 16px;
  opacity: 0.5;
  transition: opacity 0.3s;
}

.card-side:hover .tap-hint {
  opacity: 0.8;
}

.tap-icon {
  font-size: 18px;
  color: #888;
  transition: transform 0.6s;
}

.card-container.flipped .tap-icon {
  transform: rotate(180deg);
}

.tap-text {
  font-size: 12px;
  color: #999;
  letter-spacing: 0.05em;
}

/* Actions */
.actions {
  margin-top: 20px;
  display: flex;
  justify-content: center;
  opacity: 0;
  visibility: hidden;
  transform: translateY(-10px);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}

.actions.visible {
  opacity: 1;
  visibility: visible;
  transform: translateY(0);
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 14px 36px;
  border: none;
  border-radius: 50px;
  font-family: 'Noto Serif SC', serif;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.action-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.action-btn:active {
  transform: translateY(0);
}

.action-btn.primary {
  background: linear-gradient(135deg, #c44d1d 0%, #a33d14 100%);
  color: white;
}

.btn-icon {
  font-size: 18px;
  font-weight: 600;
}

/* Responsive adjustments */
@media (max-width: 380px) {
  .card-inner {
    padding: 24px 20px;
  }

  .meaning-item {
    padding: 10px 12px;
  }

  .mnemonics-section {
    padding: 12px;
  }
}
</style>
