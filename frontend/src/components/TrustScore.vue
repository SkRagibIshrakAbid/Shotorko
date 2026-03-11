<script setup>
const props = defineProps({
  score: { type: Number, default: 0 },
  large: Boolean,
})

function label(s) {
  if (s >= 10) return { text: 'অত্যন্ত বিশ্বাসযোগ্য', color: '#22c55e' }
  if (s >= 5)  return { text: 'সম্প্রদায় নিশ্চিত', color: '#eab308' }
  if (s >= 1)  return { text: 'যাচাইকরণ চলছে', color: '#f97316' }
  return { text: 'অযাচাইকৃত', color: '#64748b' }
}

const info = label(props.score)
const pct = Math.min(100, Math.max(0, (props.score / 20) * 100))
</script>

<template>
  <div class="trust" :class="{ large }">
    <span class="label" :style="{ color: info.color }">{{ info.text }}</span>
    <div class="bar-track">
      <div class="bar-fill" :style="{ width: pct + '%', background: info.color }"></div>
    </div>
    <span class="score" :style="{ color: info.color }">{{ score.toFixed(1) }}</span>
  </div>
</template>

<style scoped>
.trust {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.78rem;
}
.trust.large { font-size: 0.9rem; }
.label { white-space: nowrap; font-weight: 600; }
.bar-track {
  flex: 1;
  height: 4px;
  background: #1e293b;
  border-radius: 9999px;
  overflow: hidden;
  min-width: 40px;
}
.bar-fill {
  height: 100%;
  border-radius: 9999px;
  transition: width 0.4s ease;
}
.score { color: #64748b; }
</style>
