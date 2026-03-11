<script setup>
import { ref, onMounted } from 'vue'
import CrimeCard from '@/components/CrimeCard.vue'
import { useCrimesStore } from '@/stores/crimes'
import { useAuthStore } from '@/stores/auth'

const crimes = useCrimesStore()
const auth = useAuthStore()

const CATEGORIES = ['', 'চাঁদাবাজি', 'চুরি', 'ডাকাতি', 'হয়রানি', 'মাদক', 'হামলা', 'সন্দেহজনক']
const LABELS = {
  '': 'সব',
  'চাঁদাবাজি': 'চাঁদাবাজি',
  'চুরি': 'চুরি',
  'ডাকাতি': 'ডাকাতি',
  'হয়রানি': 'হয়রানি',
  'মাদক': 'মাদক',
  'হামলা': 'হামলা',
  'সন্দেহজনক': 'সন্দেহজনক',
}

const selectedCategory = ref('')
const myPostsOnly = ref(false)
const currentPage = ref(1)

onMounted(() => fetchData())

async function fetchData() {
  crimes.filters.category = selectedCategory.value
  crimes.filters.my_posts = myPostsOnly.value
  crimes.filters.page = currentPage.value
  await crimes.fetchCrimes()
}

async function setCategory(cat) {
  selectedCategory.value = cat
  currentPage.value = 1
  await fetchData()
}

async function toggleMyPosts() {
  myPostsOnly.value = !myPostsOnly.value
  currentPage.value = 1
  await fetchData()
}

async function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    await fetchData()
  }
}

async function nextPage() {
  const maxPage = Math.ceil(crimes.total / crimes.filters.limit)
  if (currentPage.value < maxPage) {
    currentPage.value++
    await fetchData()
  }
}

const totalPages = () => Math.max(1, Math.ceil(crimes.total / crimes.filters.limit))
</script>

<template>
  <div class="feed-view">
    <div class="feed-header">
      <h1>ঘটনার ফিড</h1>
      <p class="subtitle">মোট {{ crimes.total }} টি রিপোর্ট</p>
    </div>

    <!-- Category filter tabs -->
    <div class="cat-tabs">
      <button
        v-for="cat in CATEGORIES"
        :key="cat"
        class="tab"
        :class="{ active: selectedCategory === cat }"
        @click="setCategory(cat)"
      >
        {{ LABELS[cat] }}
      </button>
      <button
        v-if="auth.isLoggedIn"
        class="tab my-posts-tab"
        :class="{ active: myPostsOnly }"
        @click="toggleMyPosts"
      >👤 আমার পোস্ট</button>
    </div>

    <!-- Loading -->
    <div v-if="crimes.loading" class="loader">
      <div class="spinner"></div>
    </div>

    <!-- Crime list -->
    <div v-else class="feed-list">
      <div v-if="crimes.crimes.length === 0" class="empty">
        এই ক্যাটাগরিতে কোনো রিপোর্ট নেই।
      </div>
      <CrimeCard
        v-for="crime in crimes.crimes"
        :key="crime.id"
        :crime="crime"
      />
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="crimes.total > crimes.filters.limit">
      <button @click="prevPage" :disabled="currentPage <= 1">← আগে</button>
      <span>{{ currentPage }} / {{ totalPages() }}</span>
      <button @click="nextPage" :disabled="currentPage >= totalPages()">পরে →</button>
    </div>
  </div>
</template>

<style scoped>
.feed-view {
  max-width: 720px;
  margin: 0 auto;
  padding: 1.5rem 1rem 3rem;
}
.feed-header {
  margin-bottom: 1rem;
}
.feed-header h1 {
  font-size: 1.4rem;
  color: #f1f5f9;
  margin: 0;
}
.subtitle {
  font-size: 0.82rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}
.cat-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-bottom: 1.25rem;
}
.tab {
  padding: 0.3rem 0.8rem;
  border-radius: 999px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #64748b;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
}
.tab:hover { color: #94a3b8; border-color: #475569; }
.tab.active {
  background: rgba(239,68,68,0.15);
  border-color: #ef4444;
  color: #ef4444;
}
.my-posts-tab {
  margin-left: auto;
}
.my-posts-tab.active {
  background: rgba(59,130,246,0.15);
  border-color: #3b82f6;
  color: #3b82f6;
}
.loader {
  display: flex;
  justify-content: center;
  padding: 3rem;
}
.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid #1e293b;
  border-top-color: #ef4444;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.feed-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}
.empty {
  text-align: center;
  padding: 3rem;
  color: #475569;
  font-size: 0.9rem;
}
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 2rem;
  color: #64748b;
  font-size: 0.88rem;
}
.pagination button {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  border: 1px solid #334155;
  background: #1e293b;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}
.pagination button:disabled { opacity: 0.4; cursor: not-allowed; }
.pagination button:hover:not(:disabled) { border-color: #ef4444; color: #ef4444; }
</style>
