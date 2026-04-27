import { createRouter, createWebHashHistory } from 'vue-router'
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
    path: '/test',
    name: 'Test',
    component: () => import('../views/TestView.vue')
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
  },
  {
    path: '/simulation',
    name: 'Simulation',
    component: () => import('../views/SimulationView.vue')
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
