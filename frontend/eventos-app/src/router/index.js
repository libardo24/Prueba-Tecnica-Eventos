import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';
import EventDetailView from '../views/EventDetailView.vue';
import EventCreateView from '../views/EventCreateView.vue';
import LoginView from '../views/LoginView.vue';
import RegisterView from '../views/RegisterView.vue';
import ProfileView from '../views/ProfileView.vue';
import SessionCreateView from '../views/SessionCreateView.vue';
import SessionUpdateView from '../views/SessionUpdateView.vue';
import SessionAssistantsView from '../views/SessionAssistantsView.vue';
import { useAuthStore } from '../stores/auth';
const routes = [
  { path: '/', name: 'Home', component: HomeView },
  { path: '/event/:id', name: 'EventDetail', component: EventDetailView },
  {
    path: '/event/create',
    name: 'EventCreate',
    component: EventCreateView,
    meta: { requiresAuth: true },
  },
  {
    path: '/session/create',
    name: 'SessionCreate',
    component: SessionCreateView,
    meta: { requiresAuth: true },
  },
  { path: '/session/update/:id', name: 'SessionUpdate', component: SessionUpdateView },
  { path: '/session/assistants', name: 'SessionAssistants', component: SessionAssistantsView },
  { path: '/login', name: 'Login', component: LoginView },
  { path: '/register', name: 'Register', component: RegisterView },
  {
    path: '/profile',
    name: 'Profile',
    component: ProfileView,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  if (to.meta.requiresAuth && !authStore.token) {
    next({ name: 'Login' });
  } else {
    next();
  }
});

export default router;