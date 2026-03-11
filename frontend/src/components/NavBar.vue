<script setup>
import { ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import LoginModal from './LoginModal.vue'
import { useRouter, useRoute } from 'vue-router'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const showLogin = ref(false)
const menuOpen = ref(false)

function isActive(path) {
  return route.path === path || route.path.startsWith(path + '/')
}

function logout() {
  auth.logout()
  router.push('/')
}
</script>

<template>
  <header class="navbar">
    <div class="navbar-inner">
      <router-link to="/" class="brand" @click="menuOpen = false">
        <span class="brand-eye">👁</span>
        <span class="brand-name">CrimeEye</span>
      </router-link>

      <nav class="nav-links" :class="{ open: menuOpen }">
        <router-link to="/" :class="{ active: isActive('/') && route.path === '/' }" @click="menuOpen = false">
          🗺 মানচিত্র
        </router-link>
        <router-link to="/feed" :class="{ active: isActive('/feed') }" @click="menuOpen = false">
          📋 ফিড
        </router-link>
        <router-link to="/report" :class="{ active: isActive('/report') }" @click="menuOpen = false">
          ➕ রিপোর্ট করুন
        </router-link>
        <template v-if="auth.isLoggedIn">
          <router-link to="/profile" :class="{ active: isActive('/profile') }" @click="menuOpen = false">
            👤 {{ auth.user?.username }}
          </router-link>
          <button class="btn-logout" @click="logout(); menuOpen = false">লগ আউট</button>
        </template>
        <template v-else>
          <button class="btn-login" @click="showLogin = true; menuOpen = false">লগইন / নিবন্ধন</button>
        </template>
      </nav>

      <button class="hamburger" @click="menuOpen = !menuOpen" aria-label="Menu">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>

  <LoginModal v-if="showLogin" @close="showLogin = false" />
</template>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background: rgba(15, 23, 42, 0.97);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(239, 68, 68, 0.3);
}
.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
  height: 56px;
  display: flex;
  align-items: center;
  gap: 2rem;
}
.brand {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  text-decoration: none;
  flex-shrink: 0;
}
.brand-eye {
  font-size: 1.4rem;
}
.brand-name {
  font-size: 1.2rem;
  font-weight: 700;
  color: #ef4444;
  letter-spacing: 0.05em;
}
.nav-links {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex: 1;
}
.nav-links a {
  color: #94a3b8;
  text-decoration: none;
  padding: 0.4rem 0.8rem;
  border-radius: 6px;
  font-size: 0.9rem;
  transition: all 0.2s;
  white-space: nowrap;
}
.nav-links a:hover,
.nav-links a.active {
  color: #f1f5f9;
  background: rgba(239, 68, 68, 0.15);
}
.nav-links a.active {
  color: #ef4444;
}
.btn-login,
.btn-logout {
  margin-left: auto;
  padding: 0.4rem 1rem;
  border-radius: 6px;
  font-size: 0.85rem;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}
.btn-login {
  background: #ef4444;
  color: white;
}
.btn-login:hover {
  background: #dc2626;
}
.btn-logout {
  background: transparent;
  color: #64748b;
  border: 1px solid #334155;
}
.btn-logout:hover {
  color: #ef4444;
  border-color: #ef4444;
}
.hamburger {
  display: none;
  flex-direction: column;
  gap: 5px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px;
  margin-left: auto;
}
.hamburger span {
  display: block;
  width: 22px;
  height: 2px;
  background: #94a3b8;
  border-radius: 2px;
}

@media (max-width: 680px) {
  .hamburger { display: flex; }
  .nav-links {
    display: none;
    position: absolute;
    top: 56px;
    left: 0;
    right: 0;
    flex-direction: column;
    align-items: flex-start;
    background: #0f172a;
    border-bottom: 1px solid #1e293b;
    padding: 0.75rem;
    gap: 0.25rem;
  }
  .nav-links.open { display: flex; }
  .nav-links a { width: 100%; }
  .btn-login, .btn-logout { width: 100%; text-align: center; margin-left: 0; }
}
</style>
