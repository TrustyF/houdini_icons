import {createRouter, createWebHistory} from 'vue-router'
import {log_event} from "@/scripts/log_events.js";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('../views/HomeView.vue'),

    },
    {
      path: '/help',
      name: 'help',
      component: () => import('../views/HelpView.vue'),

    },
    // {
    //   path: '/about',
    //   name: 'about',
    //   component: () => import('../views/AboutView.vue'),
    //
    // },
  ],
})

router.afterEach((to, from, next) => {
  if (to.name !== 'home') log_event("page_nav", 'nav', to.name)
})

export default router
