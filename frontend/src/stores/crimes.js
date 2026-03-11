import { defineStore } from 'pinia'
import { ref } from 'vue'
import { crimesApi, notesApi } from '@/services/api'

export const useCrimesStore = defineStore('crimes', () => {
  const crimes = ref([])
  const total = ref(0)
  const currentCrime = ref(null)
  const notes = ref([])
  const heatmapPoints = ref([])
  const loading = ref(false)
  const filters = ref({
    category: '',
    lat: null,
    lng: null,
    radius_km: 50,
    page: 1,
    limit: 20,
  })

  async function fetchCrimes(extra = {}) {
    loading.value = true
    try {
      const params = { ...filters.value, ...extra }
      // Remove empty values
      Object.keys(params).forEach((k) => (params[k] === '' || params[k] === null) && delete params[k])
      const { data } = await crimesApi.list(params)
      crimes.value = data.crimes
      total.value = data.total
    } finally {
      loading.value = false
    }
  }

  async function fetchCrime(id) {
    loading.value = true
    try {
      const { data } = await crimesApi.get(id)
      currentCrime.value = data
    } finally {
      loading.value = false
    }
  }

  async function createCrime(payload) {
    const { data } = await crimesApi.create(payload)
    crimes.value.unshift(data)
    return data
  }

  async function voteCrime(id, voteType) {
    const { data } = await crimesApi.vote(id, voteType)
    // Update in list
    const idx = crimes.value.findIndex((c) => c.id === id)
    if (idx !== -1) crimes.value[idx] = data
    if (currentCrime.value?.id === id) currentCrime.value = data
    return data
  }

  async function fetchHeatmap(category = '') {
    const params = category ? { category } : {}
    const { data } = await crimesApi.heatmap(params)
    heatmapPoints.value = data
  }

  async function fetchNotes(crimeId) {
    const { data } = await notesApi.list(crimeId)
    notes.value = data
  }

  async function addNote(crimeId, content, isAnonymous) {
    const { data } = await notesApi.create(crimeId, { content, is_anonymous: isAnonymous })
    notes.value.unshift(data)
    if (currentCrime.value?.id === crimeId) {
      currentCrime.value.notes_count = (currentCrime.value.notes_count || 0) + 1
    }
    return data
  }

  return {
    crimes,
    total,
    currentCrime,
    notes,
    heatmapPoints,
    loading,
    filters,
    fetchCrimes,
    fetchCrime,
    createCrime,
    voteCrime,
    fetchHeatmap,
    fetchNotes,
    addNote,
  }
})
