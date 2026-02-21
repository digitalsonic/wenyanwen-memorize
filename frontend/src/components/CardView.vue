<script setup lang="ts">
import type { CardQuestion } from '@/types'

interface Props {
  card: CardQuestion
  isFlipped: boolean
}

interface Emits {
  (e: 'flip'): void
  (e: 'learned'): void
}

defineProps<Props>()
const emit = defineEmits<Emits>()
</script>

<template>
  <div class="card-container" :class="{ flipped: isFlipped }">
    <div class="card" @click="emit('flip')">
      <!-- Front of card -->
      <div class="card-front" v-if="!isFlipped">
        <div class="word">{{ card.word }}</div>
        <div class="pinyin" v-if="card.pinyin">{{ card.pinyin }}</div>
        <div class="example">
          <p class="example-text">{{ card.front.sentence }}</p>
          <p class="example-source">—— {{ card.front.source }}</p>
        </div>
        <div class="hint">点击翻转查看释义</div>
      </div>

      <!-- Back of card -->
      <div class="card-back" v-else>
        <div class="word">{{ card.word }}</div>
        <div class="meanings">
          <div v-for="(meaning, index) in card.back.meanings" :key="index" class="meaning-item">
            {{ meaning }}
          </div>
        </div>
        <div class="mnemonics" v-if="card.back.mnemonics">
          <div class="mnemonics-label">记忆口诀</div>
          <div class="mnemonics-text">{{ card.back.mnemonics }}</div>
        </div>
        <div class="hint">点击返回正面</div>
      </div>
    </div>

    <!-- Action buttons -->
    <div class="actions" v-if="isFlipped">
      <button class="action-btn primary" @click.stop="emit('learned')">
        记住了 ✓
      </button>
    </div>
  </div>
</template>

<style scoped>
.card-container {
  perspective: 1000px;
  width: 100%;
  max-width: 400px;
}

.card {
  width: 100%;
  min-height: 320px;
  background: white;
  border-radius: 20px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.6s;
  transform-style: preserve-3d;
  position: relative;
}

.card-container.flipped .card {
  transform: rotateY(180deg);
}

.card-front,
.card-back {
  position: absolute;
  width: 100%;
  height: 100%;
  backface-visibility: hidden;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 32px;
  box-sizing: border-box;
  border-radius: 20px;
}

.card-back {
  transform: rotateY(180deg);
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.word {
  font-size: 48px;
  font-weight: 700;
  color: #333;
  margin-bottom: 8px;
}

.pinyin {
  font-size: 20px;
  color: #999;
  margin-bottom: 32px;
}

.example {
  text-align: center;
  margin: 16px 0;
}

.example-text {
  font-size: 18px;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.6;
}

.example-source {
  font-size: 12px;
  color: #999;
}

.meanings {
  width: 100%;
  margin: 16px 0;
}

.meaning-item {
  font-size: 16px;
  color: #333;
  padding: 8px 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  line-height: 1.6;
}

.meaning-item:last-child {
  border-bottom: none;
}

.mnemonics {
  width: 100%;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 12px;
  padding: 16px;
  margin-top: 16px;
}

.mnemonics-label {
  font-size: 12px;
  color: #667eea;
  margin-bottom: 8px;
}

.mnemonics-text {
  font-size: 14px;
  color: #333;
  font-style: italic;
}

.hint {
  position: absolute;
  bottom: 16px;
  font-size: 12px;
  color: #999;
}

.actions {
  margin-top: 24px;
  display: flex;
  justify-content: center;
  gap: 16px;
}

.action-btn {
  padding: 14px 32px;
  border: none;
  border-radius: 24px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: transform 0.2s;
}

.action-btn:hover {
  transform: scale(1.05);
}

.action-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}
</style>
