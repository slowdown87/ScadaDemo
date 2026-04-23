import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes = [
  {
    path: '/',
    redirect: '/home'
  },
  {
    path: '/home',
    name: 'Home',
    component: HomeView
  },
  {
    path: '/twin',
    name: 'Twin',
    component: () => import('../views/TwinView.vue')
  },
  {
    path: '/perf',
    name: 'Perf',
    component: () => import('../views/PerfView.vue')
  },
  {
    path: '/trend',
    name: 'Trend',
    component: () => import('../views/TrendView.vue')
  },
  {
    path: '/about',
    name: 'About',
    component: () => import('../views/AboutView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
