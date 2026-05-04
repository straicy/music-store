import { ref } from 'vue'

/**
 * Універсальний composable для async операцій.
 * Автоматично керує loading, error, data.
 *
 * Використання:
 *   const { data, loading, error, execute } = useAsync(listingsApi.getOne)
 *   await execute(id)
 */
export function useAsync(fn) {
  const data    = ref(null)
  const loading = ref(false)
  const error   = ref(null)

  async function execute(...args) {
    loading.value = true
    error.value   = null
    try {
      const response = await fn(...args)
      data.value = response.data
      return response.data
    } catch (err) {
      error.value = err.response?.data?.detail ?? err.message ?? 'Невідома помилка'
      throw err
    } finally {
      loading.value = false
    }
  }

  function reset() {
    data.value    = null
    error.value   = null
    loading.value = false
  }

  return { data, loading, error, execute, reset }
}
