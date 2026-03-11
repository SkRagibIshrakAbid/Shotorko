<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'

const props = defineProps({
  crimes: { type: Array, default: () => [] },
  heatmapPoints: { type: Array, default: () => [] },
  showHeatmap: { type: Boolean, default: false },
  pickMode: { type: Boolean, default: false },   // for report form location pick
  pickedLocation: { type: Object, default: null },
  center: { type: Array, default: () => [23.8103, 90.4125] }, // Dhaka
  zoom: { type: Number, default: 12 },
})

const emit = defineEmits(['crime-click', 'location-picked'])

const mapEl = ref(null)
let L = null
let map = null
let markersLayer = null
let heatLayer = null
let pendingMarker = null   // clicked but not yet confirmed
let confirmedMarker = null // confirmed pick marker

// ── Pick mode helpers ──────────────────────────────────────────────────────
function makePendingIcon() {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:18px;height:18px;
      background:#ef4444;
      border:3px solid #fff;
      border-radius:50%;
      box-shadow:0 2px 6px rgba(0,0,0,0.5);
    "></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  })
}

function makeConfirmedIcon() {
  return L.divIcon({
    className: '',
    html: `<div style="
      width:22px;height:22px;
      background:#22c55e;
      border:3px solid #fff;
      border-radius:50%;
      box-shadow:0 2px 8px rgba(0,0,0,0.5);
      display:flex;align-items:center;justify-content:center;
      color:#fff;font-size:12px;line-height:1;
    ">✓</div>`,
    iconSize: [22, 22],
    iconAnchor: [11, 11],
  })
}

function showConfirmPopup(marker, lat, lng) {
  const popupContent = document.createElement('div')
  popupContent.style.cssText = 'font-family:sans-serif;text-align:center;min-width:160px;'
  popupContent.innerHTML = `
    <div style="font-size:12px;color:#374151;margin-bottom:8px;">
      📍 ${lat.toFixed(5)}, ${lng.toFixed(5)}
    </div>
    <button id="ce-confirm-btn" style="
      background:#ef4444;color:#fff;border:none;border-radius:6px;
      padding:7px 16px;font-size:13px;cursor:pointer;width:100%;
      font-weight:600;
    ">✔ এখানে নির্বাচন করুন</button>
  `
  const popup = L.popup({ closeButton: false, offset: [0, -6] })
    .setContent(popupContent)
  marker.bindPopup(popup).openPopup()

  marker.on('popupopen', () => {
    const btn = document.getElementById('ce-confirm-btn')
    if (!btn) return
    btn.onclick = () => {
      map.removeLayer(marker)
      pendingMarker = null
      if (confirmedMarker) map.removeLayer(confirmedMarker)
      confirmedMarker = L.marker([lat, lng], { icon: makeConfirmedIcon() }).addTo(map)
      confirmedMarker.bindPopup(
        `<div style="font-family:sans-serif;font-size:12px;color:#374151;">
          ✅ নির্বাচিত স্থান<br>
          <span style="color:#6b7280">${lat.toFixed(5)}, ${lng.toFixed(5)}</span>
        </div>`
      ).openPopup()
      emit('location-picked', { lat, lng })
    }
  })
}

function handleMapClick(e) {
  const { lat, lng } = e.latlng
  if (pendingMarker) { map.removeLayer(pendingMarker); pendingMarker = null }
  pendingMarker = L.marker([lat, lng], { icon: makePendingIcon() }).addTo(map)
  showConfirmPopup(pendingMarker, lat, lng)
}
// ──────────────────────────────────────────────────────────────────────────

const CATEGORY_COLORS = {
  'চাঁদাবাজি': '#f97316',
  'চুরি':       '#3b82f6',
  'ডাকাতি':     '#ef4444',
  'হয়রানি':     '#6b7280',
  'মাদক':       '#8b5cf6',
  'হামলা':      '#ef4444',
  'সন্দেহজনক':  '#eab308',
}

function getCategoryColor(cat) {
  return CATEGORY_COLORS[cat] || '#94a3b8'
}

function createCircleMarker(crime) {
  const color = getCategoryColor(crime.category)
  const radius = Math.max(6, Math.min(18, 6 + crime.trust_score * 0.8))
  const marker = L.circleMarker([crime.location.lat, crime.location.lng], {
    radius,
    color,
    fillColor: color,
    fillOpacity: 0.7,
    weight: 2,
    opacity: 1,
  })
  const locName = crime.location.name || `${crime.location.lat.toFixed(3)}, ${crime.location.lng.toFixed(3)}`
  marker.bindPopup(`
    <div style="font-family:sans-serif;min-width:180px">
      <div style="font-weight:700;color:${color};margin-bottom:4px">${crime.category}</div>
      <div style="color:#444;font-size:12px;margin-bottom:4px">📍 ${locName}</div>
      <div style="font-size:12px;color:#333;margin-bottom:8px">${crime.description.slice(0, 100)}${crime.description.length > 100 ? '…' : ''}</div>
      <div style="font-size:11px;color:#666">👍 ${crime.upvotes} &nbsp; 👎 ${crime.downvotes}</div>
    </div>
  `)
  marker.on('click', () => emit('crime-click', crime))
  return marker
}

function renderMarkers() {
  if (!markersLayer) return
  markersLayer.clearLayers()
  if (props.showHeatmap) return
  props.crimes.forEach((c) => {
    if (c.location?.lat != null) {
      markersLayer.addLayer(createCircleMarker(c))
    }
  })
}

function renderHeatmap() {
  if (!map) return
  if (heatLayer) {
    map.removeLayer(heatLayer)
    heatLayer = null
  }
  if (!props.showHeatmap || !props.heatmapPoints.length) return

  // Simulate heatmap with semi-transparent circles
  const group = L.featureGroup()
  props.heatmapPoints.forEach((pt) => {
    const color = getCategoryColor(pt.category)
    const r = Math.max(20, Math.min(80, pt.weight * 8))
    L.circle([pt.lat, pt.lng], {
      radius: r * 15,
      color: 'transparent',
      fillColor: color,
      fillOpacity: 0.07,
      weight: 0,
    }).addTo(group)
  })
  group.addTo(map)
  heatLayer = group
}

onMounted(async () => {
  L = (await import('leaflet')).default
  await import('leaflet/dist/leaflet.css')

  // Fix default icon paths broken by bundlers
  delete L.Icon.Default.prototype._getIconUrl
  L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
    iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
    shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
  })

  await nextTick()

  map = L.map(mapEl.value, {
    center: props.center,
    zoom: props.zoom,
    zoomControl: true,
  })

  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19,
  }).addTo(map)

  markersLayer = L.featureGroup().addTo(map)

  if (props.pickMode) {
    map.on('click', handleMapClick)
  }

  renderMarkers()
  renderHeatmap()
})

onUnmounted(() => {
  if (map) {
    map.remove()
    map = null
  }
})

watch(() => props.crimes, renderMarkers, { deep: true })
watch(() => props.showHeatmap, () => { renderMarkers(); renderHeatmap() })
watch(() => props.heatmapPoints, renderHeatmap, { deep: true })

defineExpose({ map: () => map })
</script>

<template>
  <div ref="mapEl" class="map-container"></div>
</template>

<style scoped>
.map-container {
  width: 100%;
  height: 100%;
  min-height: 300px;
}
</style>
