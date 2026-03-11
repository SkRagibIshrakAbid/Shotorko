<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import CategoryBadge from '@/components/CategoryBadge.vue'
import VoteButtons from '@/components/VoteButtons.vue'
import TrustScore from '@/components/TrustScore.vue'
import CommunityNote from '@/components/CommunityNote.vue'
import MapComponent from '@/components/MapComponent.vue'
import { useCrimesStore } from '@/stores/crimes'
import { useAuthStore } from '@/stores/auth'
import { notesApi } from '@/services/api'

const route = useRoute()
const crimes = useCrimesStore()
const auth = useAuthStore()

const noteContent = ref('')
const noteAnon = ref(true)
const submittingNote = ref(false)
const noteError = ref('')

onMounted(async () => {
  await crimes.fetchCrime(route.params.id)
  await crimes.fetchNotes(route.params.id)
})

function formatTime(dt) {
  if (!dt) return ''
  return new Date(dt).toLocaleString('bn-BD', { dateStyle: 'long', timeStyle: 'short' })
}

async function submitNote() {
  if (!noteContent.value.trim()) return
  submittingNote.value = true
  noteError.value = ''
  try {
    await crimes.addNote(route.params.id, noteContent.value, noteAnon.value)
    noteContent.value = ''
  } catch (e) {
    noteError.value = e.response?.data?.detail || 'নোট যোগ করতে ব্যর্থ'
  } finally {
    submittingNote.value = false
  }
}

async function voteNote(noteId, voteType) {
  try {
    await notesApi.vote(route.params.id, noteId, voteType)
    await crimes.fetchNotes(route.params.id)
  } catch {}
}

const crimeAsArray = () =>
  crimes.currentCrime ? [crimes.currentCrime] : []
</script>

<template>
  <div class="detail-view">
    <div v-if="crimes.loading && !crimes.currentCrime" class="spinner-wrap">
      <div class="spinner"></div>
    </div>

    <template v-else-if="crimes.currentCrime">
      <div class="detail-inner">
        <!-- Header -->
        <div class="detail-header">
          <div class="header-top">
            <CategoryBadge :category="crimes.currentCrime.category" />
            <span class="anon-tag" v-if="crimes.currentCrime.is_anonymous">বেনামী</span>
            <span class="reporter" v-else-if="crimes.currentCrime.reporter_name">@{{ crimes.currentCrime.reporter_name }}</span>
            <time>{{ formatTime(crimes.currentCrime.incident_time) }}</time>
          </div>
          <div class="location">📍 {{ crimes.currentCrime.location?.name || `${crimes.currentCrime.location?.lat?.toFixed(3)}, ${crimes.currentCrime.location?.lng?.toFixed(3)}` }}</div>
          <TrustScore :score="crimes.currentCrime.trust_score" large />
        </div>

        <!-- Description -->
        <div class="section">
          <p class="description">{{ crimes.currentCrime.description }}</p>
        </div>

        <!-- Evidence -->
        <div class="section" v-if="crimes.currentCrime.evidence_urls?.length">
          <h3>📷 প্রমাণ</h3>
          <div class="evidence-list">
            <a
              v-for="(url, idx) in crimes.currentCrime.evidence_urls"
              :key="idx"
              :href="url"
              target="_blank"
              class="ev-link"
            >প্রমাণ #{{ idx + 1 }} ↗</a>
          </div>
        </div>

        <!-- Map -->
        <div class="section map-section">
          <h3>📍 মানচিত্র</h3>
          <div class="mini-map">
            <MapComponent
              :crimes="crimeAsArray()"
              :center="[crimes.currentCrime.location.lat, crimes.currentCrime.location.lng]"
              :zoom="15"
            />
          </div>
        </div>

        <!-- Votes -->
        <div class="section vote-section">
          <h3>বিশ্বাসযোগ্যতা যাচাই করুন</h3>
          <VoteButtons
            :crime-id="crimes.currentCrime.id"
            :upvotes="crimes.currentCrime.upvotes"
            :downvotes="crimes.currentCrime.downvotes"
            :user-vote="crimes.currentCrime.user_vote"
          />
        </div>

        <!-- Community Notes -->
        <div class="section">
          <h3>💬 সম্প্রদায়ের নোট ({{ crimes.notes.length }})</h3>

          <!-- Add note form -->
          <div class="add-note-form">
            <textarea
              v-model="noteContent"
              placeholder="প্রাসঙ্গিক তথ্য যোগ করুন…"
              rows="3"
            ></textarea>
            <div class="note-form-footer">
              <label class="anon-toggle">
                <input v-model="noteAnon" type="checkbox" />
                বেনামী ভাবে পোস্ট করুন
              </label>
              <button class="note-submit" @click="submitNote" :disabled="submittingNote || !noteContent.trim()">
                {{ submittingNote ? 'যোগ হচ্ছে…' : 'নোট যোগ করুন' }}
              </button>
            </div>
            <p v-if="noteError" class="error">{{ noteError }}</p>
          </div>

          <div class="notes-list">
            <CommunityNote
              v-for="note in crimes.notes"
              :key="note.id"
              :note="note"
              @vote="voteNote"
            />
            <div v-if="crimes.notes.length === 0" class="empty-notes">কোনো নোট নেই। প্রথম হোন!</div>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="not-found">রিপোর্ট খুঁজে পাওয়া যায়নি।</div>
  </div>
</template>

<style scoped>
.detail-view {
  padding: 1.5rem 1rem 3rem;
}
.detail-inner {
  max-width: 720px;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.detail-header {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.header-top {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.anon-tag { font-size: 0.78rem; color: #64748b; }
.reporter { font-size: 0.82rem; color: #60a5fa; }
time { margin-left: auto; font-size: 0.8rem; color: #475569; }
.location { font-size: 0.9rem; color: #94a3b8; }

.section {
  background: #1e293b;
  border: 1px solid #253347;
  border-radius: 10px;
  padding: 1rem;
}
.section h3 {
  margin: 0 0 0.75rem;
  font-size: 0.95rem;
  color: #94a3b8;
}
.description {
  color: #cbd5e1;
  font-size: 0.95rem;
  line-height: 1.7;
  margin: 0;
}
.evidence-list { display: flex; flex-wrap: wrap; gap: 0.5rem; }
.ev-link {
  color: #60a5fa;
  font-size: 0.85rem;
  padding: 0.25rem 0.6rem;
  border: 1px solid rgba(96,165,250,0.3);
  border-radius: 5px;
  text-decoration: none;
}
.ev-link:hover { background: rgba(96,165,250,0.1); }
.mini-map { height: 260px; border-radius: 7px; overflow: hidden; }
.vote-section .section { background: transparent; border: none; padding: 0; }
.add-note-form {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.add-note-form textarea {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 7px;
  padding: 0.6rem;
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
  resize: vertical;
  font-family: inherit;
  transition: border-color 0.2s;
}
.add-note-form textarea:focus { border-color: #ef4444; }
.note-form-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}
.anon-toggle {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.8rem;
  color: #64748b;
  cursor: pointer;
}
.anon-toggle input { accent-color: #ef4444; }
.note-submit {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  border: none;
  background: #ef4444;
  color: white;
  font-size: 0.85rem;
  cursor: pointer;
  transition: background 0.2s;
}
.note-submit:hover { background: #dc2626; }
.note-submit:disabled { opacity: 0.5; cursor: not-allowed; }
.error { color: #ef4444; font-size: 0.8rem; margin: 0; }
.notes-list { display: flex; flex-direction: column; gap: 0.6rem; }
.empty-notes { text-align: center; padding: 1.5rem; color: #475569; font-size: 0.88rem; }
.spinner-wrap { display: flex; justify-content: center; padding: 4rem; }
.spinner {
  width: 36px; height: 36px;
  border: 3px solid #1e293b;
  border-top-color: #ef4444;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
.not-found { text-align: center; padding: 3rem; color: #475569; }
</style>
