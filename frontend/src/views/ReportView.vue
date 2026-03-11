<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import MapComponent from '@/components/MapComponent.vue'
import { useCrimesStore } from '@/stores/crimes'

const router = useRouter()
const crimes = useCrimesStore()

const CATEGORIES = ['চাঁদাবাজি', 'চুরি', 'ডাকাতি', 'হয়রানি', 'মাদক', 'হামলা', 'সন্দেহজনক']

const form = reactive({
  category: 'চাঁদাবাজি',
  description: '',
  location: { lat: 23.8103, lng: 90.4125, name: '' },
  incident_time: new Date().toISOString().slice(0, 16),
  is_anonymous: true,
  evidence_urls: [],
})

const submitting = ref(false)
const success = ref(false)
const error = ref('')
const locationPicked = ref(false)

function onLocationPicked(loc) {
  form.location.lat = loc.lat
  form.location.lng = loc.lng
  locationPicked.value = true
}

function addEvidenceUrl() {
  form.evidence_urls.push('')
}

function removeEvidence(i) {
  form.evidence_urls.splice(i, 1)
}

async function submit() {
  if (!form.description.trim()) {
    error.value = 'বিবরণ লিখুন'
    return
  }
  submitting.value = true
  error.value = ''
  try {
    const payload = {
      ...form,
      incident_time: new Date(form.incident_time).toISOString(),
      evidence_urls: form.evidence_urls.filter(Boolean),
    }
    const crime = await crimes.createCrime(payload)
    success.value = true
    setTimeout(() => router.push(`/crime/${crime.id}`), 1500)
  } catch (e) {
    error.value = e.response?.data?.detail || 'জমা দিতে ব্যর্থ হয়েছে'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="report-view">
    <div class="report-inner">
      <h1>ঘটনা রিপোর্ট করুন</h1>
      <p class="note">⚠️ মিথ্যা তথ্য দেবেন না। এই তথ্য সম্প্রদায় যাচাই করবে।</p>

      <div v-if="success" class="success-msg">
        ✅ রিপোর্ট জমা হয়েছে! পুনর্নির্দেশিত হচ্ছে…
      </div>

      <div v-if="!success" class="report-form">
        <!-- Category -->
        <div class="field">
          <label>ঘটনার ধরন *</label>
          <div class="cat-selector">
            <button
              v-for="cat in CATEGORIES"
              :key="cat"
              type="button"
              class="cat-btn"
              :class="{ selected: form.category === cat }"
              @click="form.category = cat"
            >{{ cat }}</button>
          </div>
        </div>

        <!-- Description -->
        <div class="field">
          <label>বিবরণ *</label>
          <textarea
            v-model="form.description"
            placeholder="ঘটনার বিস্তারিত লিখুন… (ব্যক্তির নাম উল্লেখ করবেন না)"
            rows="4"
          ></textarea>
        </div>

        <!-- Date/time -->
        <div class="field">
          <label>ঘটনার সময় *</label>
          <input v-model="form.incident_time" type="datetime-local" />
        </div>

        <!-- Location name -->
        <div class="field">
          <label>এলাকার নাম</label>
          <input
            v-model="form.location.name"
            type="text"
            placeholder="যেমন: মিরপুর ১০, ধানমণ্ডি ৩২"
          />
        </div>

        <!-- Map picker — intentionally OUTSIDE any <form> tag so Leaflet popup buttons never trigger submission -->
        <div class="field">
          <label>
            মানচিত্রে স্থান নির্বাচন করুন
            <span v-if="locationPicked" style="color:#22c55e"> ✓ নির্বাচিত</span>
          </label>
          <div class="map-picker">
            <MapComponent
              pick-mode
              :center="[form.location.lat, form.location.lng]"
              :zoom="13"
              @location-picked="onLocationPicked"
            />
          </div>
          <p class="hint">🖱 মানচিত্রে স্ক্রোল করুন ও পছন্দের জায়গায় ক্লিক করুন → <strong>"✔ এখানে নির্বাচন করুন"</strong> বাটনে চাপুন</p>
        </div>

        <!-- Evidence URLs -->
        <div class="field">
          <div class="ev-label">
            <label>প্রমাণের লিংক (ঐচ্ছিক)</label>
            <button type="button" class="add-ev" @click="addEvidenceUrl">+ যোগ করুন</button>
          </div>
          <div v-for="(url, i) in form.evidence_urls" :key="i" class="ev-row">
            <input v-model="form.evidence_urls[i]" type="url" placeholder="https://..." />
            <button type="button" class="rm-ev" @click="removeEvidence(i)">✕</button>
          </div>
        </div>

        <!-- Anonymous toggle -->
        <div class="field anon-field">
          <label class="toggle-label">
            <input v-model="form.is_anonymous" type="checkbox" />
            <span class="toggle-text">
              <span class="tog">বেনামী পোস্ট করুন</span>
              <span class="tog-desc">আপনার পরিচয় লুকানো থাকবে</span>
            </span>
          </label>
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="button" class="submit-btn" :disabled="submitting" @click="submit">
          {{ submitting ? 'জমা হচ্ছে…' : '📨 রিপোর্ট জমা দিন' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.report-view {
  padding: 1.5rem 1rem 3rem;
}
.report-inner {
  max-width: 680px;
  margin: 0 auto;
}
h1 {
  font-size: 1.4rem;
  color: #f1f5f9;
  margin-bottom: 0.5rem;
}
.note {
  font-size: 0.82rem;
  color: #f97316;
  margin-bottom: 1.5rem;
  background: rgba(249,115,22,0.08);
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border-left: 3px solid #f97316;
}
.report-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.field label {
  font-size: 0.85rem;
  color: #94a3b8;
  font-weight: 600;
}
.field input:not([type=checkbox]),
.field textarea,
.field select {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 7px;
  padding: 0.65rem 0.8rem;
  color: #f1f5f9;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
  font-family: inherit;
}
.field input:focus,
.field textarea:focus { border-color: #ef4444; }
.cat-selector {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
}
.cat-btn {
  padding: 0.35rem 0.8rem;
  border-radius: 999px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #64748b;
  font-size: 0.82rem;
  cursor: pointer;
  transition: all 0.2s;
}
.cat-btn.selected {
  background: rgba(239,68,68,0.15);
  border-color: #ef4444;
  color: #ef4444;
}
.map-picker {
  height: 280px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #334155;
}
.hint {
  font-size: 0.75rem;
  color: #475569;
  margin: 0;
}
.ev-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.add-ev {
  font-size: 0.78rem;
  color: #60a5fa;
  background: none;
  border: none;
  cursor: pointer;
}
.ev-row {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.3rem;
}
.ev-row input {
  flex: 1;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 0.5rem 0.7rem;
  color: #f1f5f9;
  font-size: 0.85rem;
  outline: none;
}
.rm-ev {
  background: none;
  border: 1px solid #334155;
  border-radius: 5px;
  color: #64748b;
  cursor: pointer;
  padding: 0 0.5rem;
}
.rm-ev:hover { color: #ef4444; border-color: #ef4444; }
.anon-field { flex-direction: row; align-items: flex-start; }
.toggle-label {
  display: flex;
  align-items: flex-start;
  gap: 0.6rem;
  cursor: pointer;
}
.toggle-label input { margin-top: 3px; accent-color: #ef4444; }
.tog { display: block; font-size: 0.9rem; color: #f1f5f9; }
.tog-desc { display: block; font-size: 0.78rem; color: #64748b; }
.error {
  color: #ef4444;
  font-size: 0.82rem;
  margin: 0;
}
.submit-btn {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.75rem;
  font-size: 1rem;
  cursor: pointer;
  transition: background 0.2s;
}
.submit-btn:hover { background: #dc2626; }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
.success-msg {
  background: rgba(34,197,94,0.12);
  border: 1px solid #22c55e;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: center;
  color: #22c55e;
  font-size: 1rem;
}
</style>
