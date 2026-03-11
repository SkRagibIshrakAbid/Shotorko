<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

onMounted(() => {
  if (!auth.isLoggedIn) {
    router.push('/')
  }
})

function repPercent(rep) {
  return Math.min(100, (rep / 100) * 100)
}
</script>

<template>
  <div class="profile-view" v-if="auth.user">
    <div class="profile-card">
      <div class="avatar">
        {{ auth.user.username?.charAt(0).toUpperCase() }}
      </div>
      <h2>{{ auth.user.username }}</h2>
      <p class="email">{{ auth.user.email }}</p>
      <div class="badge-row">
        <span v-if="auth.user.trusted_reporter" class="trusted-badge">✅ বিশ্বস্ত রিপোর্টার</span>
      </div>
    </div>

    <div class="stats-grid">
      <div class="stat-card">
        <div class="stat-num">{{ auth.user.reports_submitted }}</div>
        <div class="stat-label">রিপোর্ট জমা</div>
      </div>
      <div class="stat-card">
        <div class="stat-num">{{ auth.user.reputation?.toFixed(1) }}</div>
        <div class="stat-label">রেপুটেশন</div>
      </div>
    </div>

    <div class="rep-section">
      <div class="rep-header">
        <span>রেপুটেশন স্কোর</span>
        <span class="rep-val">{{ auth.user.reputation?.toFixed(1) }} / ১০০</span>
      </div>
      <div class="rep-bar">
        <div class="rep-fill" :style="{ width: repPercent(auth.user.reputation) + '%' }"></div>
      </div>
      <p class="rep-hint">সঠিক রিপোর্ট এবং সহায়ক নোট যোগ করে রেপুটেশন বাড়ান।</p>
    </div>

    <button class="logout-btn" @click="auth.logout(); $router.push('/')">
      লগ আউট
    </button>
  </div>
</template>

<style scoped>
.profile-view {
  max-width: 500px;
  margin: 0 auto;
  padding: 2rem 1rem 3rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.profile-card {
  background: #1e293b;
  border: 1px solid #253347;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}
.avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: linear-gradient(135deg, #ef4444, #f97316);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  font-weight: 700;
  color: white;
}
h2 { margin: 0; font-size: 1.3rem; color: #f1f5f9; }
.email { margin: 0; font-size: 0.85rem; color: #64748b; }
.badge-row { display: flex; gap: 0.5rem; }
.trusted-badge {
  font-size: 0.78rem;
  background: rgba(34,197,94,0.12);
  border: 1px solid rgba(34,197,94,0.3);
  color: #22c55e;
  padding: 0.2em 0.6em;
  border-radius: 999px;
}
.stats-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}
.stat-card {
  background: #1e293b;
  border: 1px solid #253347;
  border-radius: 10px;
  padding: 1.25rem;
  text-align: center;
}
.stat-num { font-size: 2rem; font-weight: 700; color: #ef4444; }
.stat-label { font-size: 0.82rem; color: #64748b; margin-top: 0.25rem; }
.rep-section {
  background: #1e293b;
  border: 1px solid #253347;
  border-radius: 10px;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.rep-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.88rem;
  color: #94a3b8;
}
.rep-val { color: #f97316; font-weight: 600; }
.rep-bar {
  height: 8px;
  background: #0f172a;
  border-radius: 999px;
  overflow: hidden;
}
.rep-fill {
  height: 100%;
  background: linear-gradient(90deg, #ef4444, #f97316);
  border-radius: 999px;
  transition: width 0.5s ease;
}
.rep-hint { font-size: 0.78rem; color: #475569; margin: 0; }
.logout-btn {
  align-self: center;
  padding: 0.5rem 2rem;
  border-radius: 7px;
  border: 1px solid #334155;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.9rem;
}
.logout-btn:hover { color: #ef4444; border-color: #ef4444; }
</style>
