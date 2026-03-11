<script setup>
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import CategoryBadge from '@/components/CategoryBadge.vue'
import VoteButtons from '@/components/VoteButtons.vue'
import TrustScore from '@/components/TrustScore.vue'
import CommunityNote from '@/components/CommunityNote.vue'
import MapComponent from '@/components/MapComponent.vue'
import { useCrimesStore } from '@/stores/crimes'
import { useAuthStore } from '@/stores/auth'
import { notesApi } from '@/services/api'

const route = useRoute()
const router = useRouter()
const crimes = useCrimesStore()
const auth = useAuthStore()

const noteContent = ref('')
const noteAnon = ref(true)
const submittingNote = ref(false)
const noteError = ref('')

// ── Edit / Delete state ──────────────────────────────────────────────────────
const showEditForm = ref(false)
const deleting = ref(false)
const deleteConfirm = ref(false)
const saving = ref(false)
const editError = ref('')

const CATEGORIES = ['চাঁদাবাজি', 'চুরি', 'ডাকাতি', 'হয়রানি', 'মাদক', 'হামলা', 'সন্দেহজনক']

const editForm = reactive({
  category: '',
  description: '',
  incident_time: '',
  is_anonymous: true,
  evidence_urls: [],
})

const isOwner = computed(() =>
  auth.isLoggedIn &&
  crimes.currentCrime?.is_owner === true
)

function openEdit() {
  const c = crimes.currentCrime
  editForm.category = c.category
  editForm.description = c.description
  editForm.incident_time = new Date(c.incident_time).toISOString().slice(0, 16)
  editForm.is_anonymous = c.is_anonymous
  editForm.evidence_urls = [...(c.evidence_urls || [])]
  editError.value = ''
  showEditForm.value = true
}

async function saveEdit() {
  if (!editForm.description.trim()) { editError.value = 'বিবরণ লিখুন'; return }
  saving.value = true
  editError.value = ''
  try {
    const payload = {
      ...editForm,
      incident_time: new Date(editForm.incident_time).toISOString(),
      evidence_urls: editForm.evidence_urls.filter(Boolean),
    }
    await crimes.updateCrime(route.params.id, payload)
    showEditForm.value = false
  } catch (e) {
    editError.value = e.response?.data?.detail || 'সংরক্ষণ ব্যর্থ'
  } finally {
    saving.value = false
  }
}

async function confirmDelete() {
  deleting.value = true
  try {
    await crimes.deleteCrime(route.params.id)
    router.push('/feed')
  } catch (e) {
    alert(e.response?.data?.detail || 'মুছতে ব্যর্থ')
  } finally {
    deleting.value = false
    deleteConfirm.value = false
  }
}
// ────────────────────────────────────────────────────────────────────────────

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

          <!-- Owner actions -->
          <div v-if="isOwner" class="owner-actions">
            <button class="btn-edit" @click="openEdit">✏️ সম্পাদনা করুন</button>
            <button class="btn-delete" @click="deleteConfirm = true">🗑 মুছে ফেলুন</button>
          </div>
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

  <!-- ── Edit modal ───────────────────────────────────────────────────────────────── -->
  <div v-if="showEditForm" class="modal-overlay" @click.self="showEditForm = false">
    <div class="edit-modal">
      <div class="modal-head">
        <h3>✏️ রিপোর্ট সম্পাদনা</h3>
        <button class="modal-close" @click="showEditForm = false">✕</button>
      </div>

      <div class="modal-body">
        <!-- Category -->
        <div class="ef">
          <label>ধরন</label>
          <div class="cat-row">
            <button
              v-for="cat in CATEGORIES" :key="cat" type="button"
              class="cat-btn" :class="{ selected: editForm.category === cat }"
              @click="editForm.category = cat"
            >{{ cat }}</button>
          </div>
        </div>

        <!-- Description -->
        <div class="ef">
          <label>বিবরণ</label>
          <textarea v-model="editForm.description" rows="4"></textarea>
        </div>

        <!-- Time -->
        <div class="ef">
          <label>সময়</label>
          <input v-model="editForm.incident_time" type="datetime-local" />
        </div>

        <!-- Evidence -->
        <div class="ef">
          <div class="ev-label">
            <label>প্রমাণের লিংক</label>
            <button type="button" class="add-ev" @click="editForm.evidence_urls.push('')">+ যোগ</button>
          </div>
          <div v-for="(url, i) in editForm.evidence_urls" :key="i" class="ev-row">
            <input v-model="editForm.evidence_urls[i]" type="url" placeholder="https://..." />
            <button type="button" class="rm-ev" @click="editForm.evidence_urls.splice(i,1)">✕</button>
          </div>
        </div>

        <!-- Anonymous -->
        <div class="ef">
          <label class="toggle-label">
            <input v-model="editForm.is_anonymous" type="checkbox" />
            <span>বেনামী পোস্ট রাখুন</span>
          </label>
          <p class="anon-warn" v-if="editForm.is_anonymous">⚠️ বেনামী করলে সম্পাদনা সুবিধা হারাবেন।</p>
        </div>

        <p v-if="editError" class="error">{{ editError }}</p>
      </div>

      <div class="modal-footer">
        <button class="btn-cancel" @click="showEditForm = false">বাতিল</button>
        <button class="btn-save" @click="saveEdit" :disabled="saving">
          {{ saving ? 'সংরক্ষণ হচ্ছে…' : 'সংরক্ষণ করুন' }}
        </button>
      </div>
    </div>
  </div>

  <!-- ── Delete confirm ────────────────────────────────────────────────────────── -->
  <div v-if="deleteConfirm" class="modal-overlay" @click.self="deleteConfirm = false">
    <div class="confirm-modal">
      <h3>মুছে ফেলতে চান?</h3>
      <p>এই রিপোর্ট ও সকল নোট স্থায়ীভাবে মুছে যাবে।</p>
      <div class="confirm-btns">
        <button class="btn-cancel" @click="deleteConfirm = false">না, বাতিল</button>
        <button class="btn-delete-confirm" @click="confirmDelete" :disabled="deleting">
          {{ deleting ? 'মুছতে…' : 'হ্যাঁ, মুছুন' }}
        </button>
      </div>
    </div>
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

/* ── Owner action buttons ───────────────────────────────────────────────────────── */
.owner-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.25rem;
}
.btn-edit, .btn-delete {
  padding: 0.35rem 0.9rem;
  border-radius: 6px;
  font-size: 0.82rem;
  cursor: pointer;
  border: 1px solid;
  transition: all 0.2s;
}
.btn-edit {
  background: rgba(59,130,246,0.1);
  border-color: rgba(59,130,246,0.4);
  color: #60a5fa;
}
.btn-edit:hover { background: rgba(59,130,246,0.2); }
.btn-delete {
  background: rgba(239,68,68,0.08);
  border-color: rgba(239,68,68,0.3);
  color: #f87171;
}
.btn-delete:hover { background: rgba(239,68,68,0.18); }

/* ── Modals ────────────────────────────────────────────────────────────────────── */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.edit-modal {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  width: 100%;
  max-width: 560px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.modal-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #253347;
}
.modal-head h3 { margin: 0; font-size: 1rem; color: #f1f5f9; }
.modal-close {
  background: none; border: none; color: #64748b;
  font-size: 1rem; cursor: pointer;
}
.modal-close:hover { color: #f1f5f9; }
.modal-body {
  padding: 1rem 1.25rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  flex: 1;
}
.modal-footer {
  padding: 0.75rem 1.25rem;
  border-top: 1px solid #253347;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
.ef { display: flex; flex-direction: column; gap: 0.35rem; }
.ef label { font-size: 0.82rem; color: #94a3b8; font-weight: 600; }
.ef input:not([type=checkbox]), .ef textarea, .ef select {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 0.6rem 0.75rem;
  color: #f1f5f9;
  font-size: 0.88rem;
  outline: none;
  font-family: inherit;
  transition: border-color 0.2s;
}
.ef input:focus, .ef textarea:focus { border-color: #ef4444; }
.cat-row { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.cat-btn {
  padding: 0.3rem 0.7rem;
  border-radius: 999px;
  border: 1px solid #334155;
  background: #0f172a;
  color: #64748b;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s;
}
.cat-btn.selected { background: rgba(239,68,68,0.15); border-color: #ef4444; color: #ef4444; }
.ev-label { display: flex; justify-content: space-between; align-items: center; }
.add-ev { font-size: 0.78rem; color: #60a5fa; background: none; border: none; cursor: pointer; }
.ev-row { display: flex; gap: 0.5rem; }
.ev-row input { flex: 1; background: #0f172a; border: 1px solid #334155; border-radius: 6px; padding: 0.5rem; color: #f1f5f9; font-size: 0.85rem; outline: none; }
.rm-ev { background: none; border: 1px solid #334155; border-radius: 5px; color: #64748b; cursor: pointer; padding: 0 0.5rem; }
.rm-ev:hover { color: #ef4444; border-color: #ef4444; }
.toggle-label { display: flex; align-items: center; gap: 0.5rem; cursor: pointer; font-size: 0.88rem; color: #f1f5f9; }
.toggle-label input { accent-color: #ef4444; }
.anon-warn { font-size: 0.78rem; color: #f97316; margin: 0; }
.btn-cancel {
  padding: 0.4rem 1rem;
  border-radius: 6px;
  border: 1px solid #334155;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.88rem;
  transition: all 0.2s;
}
.btn-cancel:hover { border-color: #475569; color: #f1f5f9; }
.btn-save {
  padding: 0.4rem 1.2rem;
  border-radius: 6px;
  border: none;
  background: #3b82f6;
  color: white;
  font-size: 0.88rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-save:hover { background: #2563eb; }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

/* Delete confirm */
.confirm-modal {
  background: #1e293b;
  border: 1px solid rgba(239,68,68,0.4);
  border-radius: 12px;
  padding: 1.5rem;
  max-width: 380px;
  width: 100%;
  text-align: center;
}
.confirm-modal h3 { margin: 0 0 0.75rem; font-size: 1.1rem; color: #f87171; }
.confirm-modal p { font-size: 0.88rem; color: #94a3b8; margin: 0 0 1.25rem; }
.confirm-btns { display: flex; gap: 0.75rem; justify-content: center; }
.btn-delete-confirm {
  padding: 0.45rem 1.2rem;
  border-radius: 6px;
  border: none;
  background: #ef4444;
  color: white;
  font-size: 0.88rem;
  cursor: pointer;
  transition: background 0.2s;
}
.btn-delete-confirm:hover { background: #dc2626; }
.btn-delete-confirm:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
