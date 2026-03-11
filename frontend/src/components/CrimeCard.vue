<script setup>
import { useRouter } from 'vue-router'
import CategoryBadge from './CategoryBadge.vue'
import VoteButtons from './VoteButtons.vue'
import TrustScore from './TrustScore.vue'

const props = defineProps({
  crime: { type: Object, required: true },
})

const router = useRouter()

function formatTime(dt) {
  if (!dt) return ''
  const d = new Date(dt)
  return d.toLocaleString('bn-BD', { dateStyle: 'medium', timeStyle: 'short' })
}

function truncate(str, n = 120) {
  return str && str.length > n ? str.slice(0, n) + '…' : str
}

function go() {
  router.push(`/crime/${props.crime.id}`)
}
</script>

<template>
  <article class="crime-card" @click="go">
    <div class="card-header">
      <CategoryBadge :category="crime.category" />
      <span class="anon-tag" v-if="crime.is_anonymous">বেনামী</span>
      <span class="reporter" v-else-if="crime.reporter_name">@{{ crime.reporter_name }}</span>
      <time class="time">{{ formatTime(crime.incident_time) }}</time>
    </div>

    <div class="location">
      📍 {{ crime.location?.name || `${crime.location?.lat?.toFixed(4)}, ${crime.location?.lng?.toFixed(4)}` }}
    </div>

    <p class="description">{{ truncate(crime.description) }}</p>

    <div class="evidence-row" v-if="crime.evidence_urls?.length">
      <span class="ev-icon">📷 {{ crime.evidence_urls.length }} প্রমাণ</span>
    </div>

    <div class="card-footer">
      <TrustScore :score="crime.trust_score" />
      <div class="footer-right">
        <VoteButtons
          :crime-id="crime.id"
          :upvotes="crime.upvotes"
          :downvotes="crime.downvotes"
          :user-vote="crime.user_vote"
        />
        <span class="notes-count">💬 {{ crime.notes_count || 0 }}</span>
      </div>
    </div>
  </article>
</template>

<style scoped>
.crime-card {
  background: #1e293b;
  border: 1px solid #253347;
  border-radius: 10px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.crime-card:hover {
  border-color: rgba(239, 68, 68, 0.4);
  background: #1e293b;
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(0,0,0,0.3);
}
.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
.anon-tag {
  font-size: 0.72rem;
  color: #64748b;
  background: #0f172a;
  padding: 0.15em 0.5em;
  border-radius: 4px;
}
.reporter {
  font-size: 0.78rem;
  color: #60a5fa;
}
.time {
  margin-left: auto;
  font-size: 0.75rem;
  color: #475569;
}
.location {
  font-size: 0.85rem;
  color: #94a3b8;
}
.description {
  color: #cbd5e1;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}
.ev-icon {
  font-size: 0.78rem;
  color: #60a5fa;
  background: rgba(96,165,250,0.1);
  padding: 0.15em 0.5em;
  border-radius: 4px;
}
.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.25rem;
}
.footer-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.notes-count {
  font-size: 0.82rem;
  color: #64748b;
}
</style>
