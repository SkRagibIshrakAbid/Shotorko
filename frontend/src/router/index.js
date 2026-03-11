import { createRouter, createWebHistory } from 'vue-router'
import MapView from '@/views/MapView.vue'
import FeedView from '@/views/FeedView.vue'
import ReportView from '@/views/ReportView.vue'
import CrimeDetailView from '@/views/CrimeDetailView.vue'
import ProfileView from '@/views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', name: 'map', component: MapView },
    { path: '/feed', name: 'feed', component: FeedView },
    { path: '/report', name: 'report', component: ReportView },
    { path: '/crime/:id', name: 'crime-detail', component: CrimeDetailView },
    { path: '/profile', name: 'profile', component: ProfileView },
  ],
  scrollBehavior: () => ({ top: 0 }),
})

export default router
