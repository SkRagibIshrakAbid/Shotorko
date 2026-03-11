<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import MapComponent from '@/components/MapComponent.vue'
import CategoryBadge from '@/components/CategoryBadge.vue'
import { useCrimesStore } from '@/stores/crimes'

const crimes = useCrimesStore()
const router = useRouter()
const showHeatmap = ref(false)
const selectedCategory = ref('')

const CATEGORIES = ['চাঁদাবাজি', 'চুরি', 'ডাকাতি', 'হয়রানি', 'মাদক', 'হামলা', 'সন্দেহজনক']

onMounted(async () => {
  await crimes.fetchCrimes({ limit: 200 })
  await crimes.fetchHeatmap()
})

const filteredCrimes = computed(() => {
  if (!selectedCategory.value) return crimes.crimes
  return crimes.crimes.filter((c) => c.category === selectedCategory.value)
})

const filteredHeatmap = computed(() => {
  if (!selectedCategory.value) return crimes.heatmapPoints
  return crimes.heatmapPoints.filter((p) => p.category === selectedCategory.value)
})

async function filterCategory(cat) {
  selectedCategory.value = cat === selectedCategory.value ? '' : cat
}

function onCrimeClick(crime) {
  router.push(`/crime/${crime.id}`)
}
</script>

<template>
  <div class="map-view">
    <!-- Controls -->
    <div class="map-controls">
      <div class="controls-row">
        <button
          class="ctrl-btn"
          :class="{ active: !showHeatmap }"
          @click="showHeatmap = false"
        >📍 পিন</button>
        <button
          class="ctrl-btn"
          :class="{ active: showHeatmap }"
          @click="showHeatmap = true"
        >🔥 হিটম্যাপ</button>
        <span class="divider" />
        <button
          v-for="cat in CATEGORIES"
          :key="cat"
          class="cat-filter"
          :class="{ active: selectedCategory === cat }"
          @click="filterCategory(cat)"
        >
          <CategoryBadge :category="cat" small />
        </button>
        <button v-if="selectedCategory" class="clear-btn" @click="selectedCategory = ''">✕ সব</button>
      </div>
    </div>

    <!-- Map -->
    <div class="map-wrap">
      <MapComponent
        :crimes="filteredCrimes"
        :heatmap-points="filteredHeatmap"
        :show-heatmap="showHeatmap"
        @crime-click="onCrimeClick"
      />
    </div>

    <!-- Stats overlay -->
    <div class="stats-overlay">
      <span>মোট রিপোর্ট: <strong>{{ filteredCrimes.length }}</strong></span>
    </div>

    <div v-if="crimes.loading" class="loading-overlay">লোড হচ্ছে…</div>
  </div>
</template>

<style scoped>
.map-view {
  position: relative;
  height: calc(100vh - 56px);
  display: flex;
  flex-direction: column;
}
.map-controls {
  background: rgba(15, 23, 42, 0.95);
  border-bottom: 1px solid #1e293b;
  padding: 0.5rem 1rem;
  z-index: 10;
}
.controls-row {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}
.ctrl-btn {
  padding: 0.3rem 0.8rem;
  border-radius: 6px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #64748b;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
}
.ctrl-btn.active { background: rgba(239,68,68,0.2); color: #ef4444; border-color: #ef4444; }
.divider { width: 1px; height: 20px; background: #1e293b; margin: 0 0.2rem; }
.cat-filter { background: none; border: none; cursor: pointer; padding: 0; }
.cat-filter.active { outline: 2px solid rgba(255,255,255,0.3); border-radius: 999px; }
.clear-btn {
  padding: 0.25rem 0.5rem;
  border-radius: 5px;
  border: 1px solid #334155;
  background: #1e293b;
  color: #94a3b8;
  font-size: 0.78rem;
  cursor: pointer;
}
.map-wrap { flex: 1; }
.stats-overlay {
  position: absolute;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(15, 23, 42, 0.85);
  border: 1px solid #334155;
  border-radius: 999px;
  padding: 0.3rem 1rem;
  font-size: 0.8rem;
  color: #94a3b8;
  pointer-events: none;
  z-index: 10;
}
.stats-overlay strong { color: #f1f5f9; }
.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #f1f5f9;
  font-size: 1rem;
  z-index: 20;
}
</style>
