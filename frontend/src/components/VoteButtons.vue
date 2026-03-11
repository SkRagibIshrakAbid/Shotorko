<script setup>
import { ref } from 'vue'
import { useCrimesStore } from '@/stores/crimes'
import { useAuthStore } from '@/stores/auth'

const props = defineProps({
  crimeId: String,
  upvotes: { type: Number, default: 0 },
  downvotes: { type: Number, default: 0 },
  userVote: { type: String, default: null },
})

const emit = defineEmits(['voted'])
const crimes = useCrimesStore()
const auth = useAuthStore()
const voting = ref(false)

async function vote(type) {
  if (voting.value) return
  voting.value = true
  try {
    await crimes.voteCrime(props.crimeId, type)
    emit('voted')
  } finally {
    voting.value = false
  }
}
</script>

<template>
  <div class="votes">
    <button
      class="vote-btn up"
      :class="{ active: userVote === 'up', loading: voting }"
      @click.stop="vote('up')"
      title="বিশ্বাসযোগ্য"
    >
      👍 <span>{{ upvotes }}</span>
    </button>
    <button
      class="vote-btn down"
      :class="{ active: userVote === 'down', loading: voting }"
      @click.stop="vote('down')"
      title="মিথ্যা রিপোর্ট"
    >
      👎 <span>{{ downvotes }}</span>
    </button>
  </div>
</template>

<style scoped>
.votes {
  display: flex;
  gap: 0.5rem;
}
.vote-btn {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.7rem;
  border-radius: 6px;
  border: 1px solid #1e293b;
  background: #0f172a;
  color: #64748b;
  font-size: 0.85rem;
  cursor: pointer;
  transition: all 0.2s;
}
.vote-btn:hover {
  border-color: #334155;
  color: #94a3b8;
}
.vote-btn.up.active {
  background: rgba(34, 197, 94, 0.15);
  border-color: #22c55e;
  color: #22c55e;
}
.vote-btn.down.active {
  background: rgba(239, 68, 68, 0.15);
  border-color: #ef4444;
  color: #ef4444;
}
.vote-btn.loading {
  opacity: 0.6;
  pointer-events: none;
}
</style>
