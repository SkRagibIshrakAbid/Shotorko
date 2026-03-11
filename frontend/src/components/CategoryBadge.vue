<script setup>
const CATEGORIES = {
  'চাঁদাবাজি': { color: '#f97316', bg: 'rgba(249,115,22,0.15)', icon: '💰' },
  'চুরি':       { color: '#3b82f6', bg: 'rgba(59,130,246,0.15)', icon: '🔵' },
  'ডাকাতি':     { color: '#ef4444', bg: 'rgba(239,68,68,0.15)',  icon: '🔴' },
  'হয়রানি':     { color: '#6b7280', bg: 'rgba(107,114,128,0.15)', icon: '⚫' },
  'মাদক':       { color: '#8b5cf6', bg: 'rgba(139,92,246,0.15)', icon: '🟣' },
  'হামলা':      { color: '#ef4444', bg: 'rgba(239,68,68,0.2)',   icon: '⚡' },
  'সন্দেহজনক':  { color: '#eab308', bg: 'rgba(234,179,8,0.15)',  icon: '🟡' },
}

const props = defineProps({
  category: { type: String, default: 'সন্দেহজনক' },
  small: Boolean,
})

const info = CATEGORIES[props.category] || { color: '#94a3b8', bg: 'rgba(148,163,184,0.15)', icon: '📍' }
</script>

<template>
  <span
    class="badge"
    :class="{ small }"
    :style="{ color: info.color, background: info.bg, borderColor: info.color + '40' }"
  >
    {{ info.icon }} {{ category }}
  </span>
</template>

<style scoped>
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3em;
  padding: 0.25em 0.65em;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
  border: 1px solid;
  white-space: nowrap;
}
.badge.small {
  font-size: 0.72rem;
  padding: 0.15em 0.5em;
}
</style>
