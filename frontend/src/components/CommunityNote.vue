<script setup>
const props = defineProps({
  note: { type: Object, required: true },
})
const emit = defineEmits(['vote'])

function formatTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('bn-BD', { dateStyle: 'short', timeStyle: 'short' })
}
</script>

<template>
  <div class="note">
    <div class="note-header">
      <span class="note-author">
        <span v-if="note.is_anonymous" class="anon">বেনামী</span>
        <span v-else class="named">@{{ note.author_name }}</span>
      </span>
      <time>{{ formatTime(note.created_at) }}</time>
    </div>
    <p class="note-content">{{ note.content }}</p>
    <div class="note-footer">
      <button class="note-vote up" @click="emit('vote', note.id, 'up')">👍 {{ note.upvotes }}</button>
      <button class="note-vote down" @click="emit('vote', note.id, 'down')">👎 {{ note.downvotes }}</button>
    </div>
  </div>
</template>

<style scoped>
.note {
  background: #0f172a;
  border: 1px solid #1e293b;
  border-radius: 8px;
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.note-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.78rem;
}
.anon { color: #64748b; }
.named { color: #60a5fa; }
time { color: #475569; }
.note-content {
  color: #cbd5e1;
  font-size: 0.88rem;
  line-height: 1.5;
  margin: 0;
}
.note-footer {
  display: flex;
  gap: 0.5rem;
}
.note-vote {
  background: none;
  border: 1px solid #1e293b;
  border-radius: 5px;
  color: #64748b;
  font-size: 0.78rem;
  padding: 0.15rem 0.5rem;
  cursor: pointer;
  transition: all 0.15s;
}
.note-vote:hover { border-color: #334155; color: #94a3b8; }
</style>
