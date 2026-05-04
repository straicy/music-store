import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api'
import { tokenStorage } from '@/api/axios'
import { useRouter } from 'vue-router'
import { useToast } from 'vue-toastification'

export const useAuthStore = defineStore('auth', () => {
  const router = useRouter()
  const toast  = useToast()

  // ── State ──────────────────────────────────────────────
  const user    = ref(null)
  const loading = ref(false)
  const initialized = ref(false)

  // ── Getters ────────────────────────────────────────────
  const isLoggedIn = computed(() => !!user.value)
  const isAdmin    = computed(() => user.value?.role === 'admin')
  const userName   = computed(() => user.value?.name ?? '')

  // ── Actions ────────────────────────────────────────────

  // Ініціалізація при старті — відновлюємо сесію з токена
  async function init() {
    if (initialized.value) return
    initialized.value = true

    const token = tokenStorage.getAccess()
    if (!token) return

    try {
      const { data } = await authApi.getMe()
      user.value = data
    } catch {
      tokenStorage.clear()
    }
  }

  async function register(payload) {
    loading.value = true
    try {
      const { data } = await authApi.register(payload)
      tokenStorage.set(data.access_token, data.refresh_token)
      user.value = data.user
      toast.success(`Ласкаво просимо, ${data.user.name}!`)
      router.push('/')
    } catch (err) {
      const msg = err.response?.data?.detail ?? 'Помилка реєстрації'
      toast.error(msg)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function login(payload) {
    loading.value = true
    try {
      const { data } = await authApi.login(payload)
      tokenStorage.set(data.access_token, data.refresh_token)
      user.value = data.user
      toast.success(`З поверненням, ${data.user.name}!`)
      // Редіректимо на попередню сторінку або на головну
      const redirect = router.currentRoute.value.query.redirect || '/'
      router.push(redirect)
    } catch (err) {
      const msg = err.response?.data?.detail ?? 'Невірний email або пароль'
      toast.error(msg)
      throw err
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    user.value = null
    tokenStorage.clear()
    router.push('/login')
    toast.info('Ви вийшли з акаунту')
  }

  async function updateProfile(payload) {
    loading.value = true
    try {
      const { data } = await authApi.updateMe(payload)
      user.value = data
      toast.success('Профіль оновлено')
      return data
    } catch (err) {
      const msg = err.response?.data?.detail ?? 'Помилка оновлення'
      toast.error(msg)
      throw err
    } finally {
      loading.value = false
    }
  }

  // Оновлення user після зовнішніх дій (наприклад, завантаження аватара)
  function setUser(data) {
    user.value = data
  }

  return {
    user, loading, initialized,
    isLoggedIn, isAdmin, userName,
    init, register, login, logout, updateProfile, setUser,
  }
})
