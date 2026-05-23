import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import App from './App.vue'
import { getCurrentOwner } from './features/auth/session'
import DogListView from './features/dogs/views/DogListView.vue'
import LoginView from './features/auth/views/LoginView.vue'
import OwnerRegistrationView from './features/owners/views/OwnerRegistrationView.vue'
import './styles.css'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: () => (getCurrentOwner() ? '/dogs' : '/register'),
    },
    {
      path: '/register',
      name: 'owner-register',
      component: OwnerRegistrationView,
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
    },
    {
      path: '/dogs',
      name: 'dogs',
      component: DogListView,
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !getCurrentOwner()) {
    return { name: 'login' }
  }

  return true
})

createApp(App).use(router).mount('#app')
