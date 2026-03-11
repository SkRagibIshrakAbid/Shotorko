<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

const emit = defineEmits(['close'])
const auth = useAuthStore()
const mode = ref('login') // 'login' | 'register'
const form = ref({ username: '', email: '', password: '' })
const error = ref('')

async function submit() {
  error.value = ''
  try {
    if (mode.value === 'login') {
      await auth.login(form.value.email, form.value.password)
    } else {
      await auth.register(form.value.username, form.value.email, form.value.password)
    }
    emit('close')
  } catch (e) {
    error.value = auth.error || 'Something went wrong'
  }
}
</script>

<template>
  <div class="overlay" @click.self="emit('close')">
    <div class="modal">
      <button class="close-btn" @click="emit('close')">✕</button>

      <div class="modal-tabs">
        <button :class="{ active: mode === 'login' }" @click="mode = 'login'">লগইন</button>
        <button :class="{ active: mode === 'register' }" @click="mode = 'register'">নিবন্ধন</button>
      </div>

      <form @submit.prevent="submit" class="modal-form">
        <div v-if="mode === 'register'" class="field">
          <label>ব্যবহারকারীর নাম</label>
          <input v-model="form.username" type="text" placeholder="username" required />
        </div>
        <div class="field">
          <label>ইমেইল</label>
          <input v-model="form.email" type="email" placeholder="email@example.com" required />
        </div>
        <div class="field">
          <label>পাসওয়ার্ড</label>
          <input v-model="form.password" type="password" placeholder="••••••••" required minlength="6" />
        </div>

        <p v-if="error" class="error">{{ error }}</p>

        <button type="submit" class="submit-btn" :disabled="auth.loading">
          {{ auth.loading ? 'অপেক্ষা করুন…' : mode === 'login' ? 'লগইন করুন' : 'নিবন্ধন করুন' }}
        </button>
      </form>
    </div>
  </div>
</template>

<style scoped>
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.7);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.modal {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 12px;
  padding: 1.5rem;
  width: 100%;
  max-width: 400px;
  position: relative;
}
.close-btn {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  color: #64748b;
  font-size: 1rem;
  cursor: pointer;
}
.close-btn:hover { color: #f1f5f9; }
.modal-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
}
.modal-tabs button {
  flex: 1;
  padding: 0.5rem;
  border-radius: 6px;
  border: none;
  background: #0f172a;
  color: #64748b;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.2s;
}
.modal-tabs button.active {
  background: rgba(239,68,68,0.2);
  color: #ef4444;
}
.modal-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.field label {
  font-size: 0.82rem;
  color: #94a3b8;
}
.field input {
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 6px;
  padding: 0.6rem 0.75rem;
  color: #f1f5f9;
  font-size: 0.9rem;
  outline: none;
  transition: border-color 0.2s;
}
.field input:focus { border-color: #ef4444; }
.error {
  color: #ef4444;
  font-size: 0.82rem;
  margin: 0;
}
.submit-btn {
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 7px;
  padding: 0.65rem;
  font-size: 0.95rem;
  cursor: pointer;
  transition: background 0.2s;
}
.submit-btn:hover { background: #dc2626; }
.submit-btn:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
