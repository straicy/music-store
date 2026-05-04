import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  // ── Публічні ──────────────────────────────────────────
  {
    path: '/',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'Каталог інструментів' },
  },
  {
    path: '/listings/:id',
    component: () => import('@/views/listings/ListingDetailView.vue'),
    meta: { title: 'Оголошення' },
  },
  {
    path: '/login',
    component: () => import('@/views/auth/LoginView.vue'),
    meta: { title: 'Вхід', guestOnly: true },
  },
  {
    path: '/register',
    component: () => import('@/views/auth/RegisterView.vue'),
    meta: { title: 'Реєстрація', guestOnly: true },
  },

  // ── Захищені (потрібен login) ──────────────────────────
  {
    path: '/profile',
    component: () => import('@/views/user/ProfileView.vue'),
    meta: { title: 'Мій профіль', requiresAuth: true },
  },
  {
    path: '/my-listings',
    component: () => import('@/views/user/MyListingsView.vue'),
    meta: { title: 'Мої оголошення', requiresAuth: true },
  },
  {
    path: '/listings/create',
    component: () => import('@/views/listings/ListingFormView.vue'),
    meta: { title: 'Нове оголошення', requiresAuth: true },
  },
  {
    path: '/listings/:id/edit',
    component: () => import('@/views/listings/ListingFormView.vue'),
    meta: { title: 'Редагувати оголошення', requiresAuth: true },
  },
  {
    path: '/favorites',
    component: () => import('@/views/user/FavoritesView.vue'),
    meta: { title: 'Обране', requiresAuth: true },
  },
  {
    path: '/chat',
    component: () => import('@/views/chat/ChatView.vue'),
    meta: { title: 'Повідомлення', requiresAuth: true },
  },
  {
    path: '/chat/:convId',
    component: () => import('@/views/chat/ChatView.vue'),
    meta: { title: 'Чат', requiresAuth: true },
  },

  // ── Адмін ─────────────────────────────────────────────
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      {
        path: '',
        component: () => import('@/views/admin/AdminDashboard.vue'),
        meta: { title: 'Адмін — Дашборд' },
      },
      {
        path: 'users',
        component: () => import('@/views/admin/AdminUsers.vue'),
        meta: { title: 'Адмін — Користувачі' },
      },
      {
        path: 'listings',
        component: () => import('@/views/admin/AdminListings.vue'),
        meta: { title: 'Адмін — Оголошення' },
      },
    ],
  },

  // ── 404 ───────────────────────────────────────────────
  {
    path: '/:pathMatch(.*)*',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { title: '404' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0, behavior: 'smooth' }),
})

// ── Navigation Guards ──────────────────────────────────
router.beforeEach(async (to) => {
  const auth = useAuthStore()

  // Ініціалізуємо store один раз
  await auth.init()

  // Тільки для гостей (логін/реєстрація)
  if (to.meta.guestOnly && auth.isLoggedIn) {
    return { path: '/' }
  }

  // Потрібна авторизація
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { path: '/login', query: { redirect: to.fullPath } }
  }

  // Потрібен адмін
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { path: '/' }
  }

  // Оновлюємо title вкладки
  document.title = to.meta.title
    ? `${to.meta.title} | MusicStore`
    : 'MusicStore'
})

export default router
