import { defineStore } from 'pinia'
import { ref } from 'vue'
import { listingsApi, favoritesApi } from '@/api'
import { useToast } from 'vue-toastification'

export const useListingsStore = defineStore('listings', () => {
  const toast = useToast()

  // ── State ──────────────────────────────────────────────
  const items       = ref([])
  const total       = ref(0)
  const pages       = ref(1)
  const currentPage = ref(1)
  const loading     = ref(false)
  const filters     = ref({
    q: '',
    category: null,
    condition: null,
    brand: '',
    city: '',
    price_min: null,
    price_max: null,
    sort: 'newest',
    page: 1,
    limit: 20,
  })

  // ── Actions ────────────────────────────────────────────

  async function fetchListings(overrides = {}) {
    loading.value = true
    try {
      // Прибираємо порожні значення з фільтрів
      const params = Object.fromEntries(
        Object.entries({ ...filters.value, ...overrides })
          .filter(([, v]) => v !== null && v !== '' && v !== undefined)
      )
      const { data } = await listingsApi.getAll(params)
      items.value       = data.items
      total.value       = data.total
      pages.value       = data.pages
      currentPage.value = data.page
    } catch (err) {
      toast.error('Помилка завантаження оголошень')
    } finally {
      loading.value = false
    }
  }

  function setFilter(key, value) {
    filters.value[key] = value
    filters.value.page = 1  // скидаємо на першу сторінку при зміні фільтра
  }

  function resetFilters() {
    filters.value = {
      q: '', category: null, condition: null,
      brand: '', city: '', price_min: null,
      price_max: null, sort: 'newest', page: 1, limit: 20,
    }
  }

  async function toggleFavorite(listingId) {
    try {
      const { data } = await favoritesApi.toggle(listingId)
      // Оновлюємо локально щоб не робити повторний запит
      const item = items.value.find((l) => l.id === listingId)
      if (item) item.is_favorited = data.is_favorited
      return data
    } catch {
      toast.error('Помилка. Увійдіть в акаунт')
    }
  }

  async function deleteListing(id) {
    try {
      await listingsApi.delete(id)
      items.value = items.value.filter((l) => l.id !== id)
      toast.success('Оголошення видалено')
    } catch {
      toast.error('Помилка видалення')
    }
  }

  return {
    items, total, pages, currentPage, loading, filters,
    fetchListings, setFilter, resetFilters,
    toggleFavorite, deleteListing,
  }
})
