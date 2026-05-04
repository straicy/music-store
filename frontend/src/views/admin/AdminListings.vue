<template>
  <div class="admin-listings">
    <div class="admin-page-header">
      <div>
        <h1 class="admin-page-title">Оголошення</h1>
        <p class="admin-page-sub">Всього: <strong>{{ total }}</strong></p>
      </div>
      <div class="admin-controls">
        <!-- Фільтр статусу -->
        <select v-model="statusFilter" class="admin-select glass" @change="onFilterChange">
          <option value="">Всі статуси</option>
          <option value="active">Активні</option>
          <option value="sold">Продані</option>
          <option value="deactivated">Знято</option>
        </select>
        <!-- Пошук -->
        <div class="admin-search glass">
          <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
            <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
          </svg>
          <input v-model="searchQ" type="text" placeholder="Пошук..."
            class="admin-search__input" @input="onSearch" />
        </div>
      </div>
    </div>

    <!-- Таблиця -->
    <div class="admin-table glass">
      <table>
        <thead>
          <tr>
            <th>Фото</th>
            <th>Назва</th>
            <th>Категорія</th>
            <th>Продавець</th>
            <th>Ціна</th>
            <th>Перегляди</th>
            <th>Статус</th>
            <th>Дії</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="8">
              <div v-for="n in 8" :key="n" class="skeleton" style="height:20px;border-radius:4px;margin:10px 0" />
            </td>
          </tr>
          <tr v-else v-for="l in listings" :key="l.id">
            <td>
              <div class="listing-thumb">
                <img v-if="l.images?.length" :src="l.images[0]" :alt="l.title" />
                <span v-else>🎸</span>
              </div>
            </td>
            <td class="listing-title-cell">
              <RouterLink :to="`/listings/${l.id}`" class="listing-title-link" target="_blank">
                {{ l.title }}
              </RouterLink>
            </td>
            <td><span class="admin-table__tag">{{ l.category }}</span></td>
            <td class="admin-table__muted">{{ l.seller_name }}</td>
            <td class="admin-table__price">{{ formatPrice(l.price) }}</td>
            <td class="admin-table__muted">{{ l.views }}</td>
            <td>
              <select
                class="status-select"
                :class="l.status"
                :value="l.status"
                :disabled="actionLoading === l.id"
                @change="onStatusChange(l, $event.target.value)"
              >
                <option value="active">Активне</option>
                <option value="sold">Продано</option>
                <option value="deactivated">Знято</option>
              </select>
            </td>
            <td>
              <button
                class="action-btn action-btn--danger"
                :disabled="actionLoading === l.id"
                @click="deleteListing(l)"
                title="Видалити"
              >
                <span v-if="actionLoading === l.id" class="mini-spinner" />
                <svg v-else width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14H6L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4h6v2"/>
                </svg>
              </button>
            </td>
          </tr>
          <tr v-if="!loading && !listings.length">
            <td colspan="8" class="admin-table__empty">Нічого не знайдено</td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppPagination :current="page" :pages="pages" @change="onPage" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { useFormatters } from '@/composables/useFormatters'
import { useToast } from 'vue-toastification'
import AppPagination from '@/components/ui/AppPagination.vue'

const toast = useToast()
const { formatPrice } = useFormatters()

const listings      = ref([])
const loading       = ref(true)
const actionLoading = ref(null)
const searchQ       = ref('')
const statusFilter  = ref('')
const page          = ref(1)
const pages         = ref(1)
const total         = ref(0)
let searchTimer     = null

async function load() {
  loading.value = true
  try {
    const params = { page: page.value, limit: 15 }
    if (statusFilter.value) params.status = statusFilter.value
    const { data } = await adminApi.getListings(params)
    listings.value = data.items
    total.value    = data.total
    pages.value    = Math.ceil(data.total / 15) || 1
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; load() }, 400)
}
function onFilterChange() { page.value = 1; load() }
function onPage(p) { page.value = p; load() }

async function onStatusChange(listing, newStatus) {
  actionLoading.value = listing.id
  try {
    await adminApi.setStatus(listing.id, newStatus)
    listing.status = newStatus
    toast.success('Статус оновлено')
  } catch { toast.error('Помилка') }
  finally { actionLoading.value = null }
}

async function deleteListing(listing) {
  if (!confirm(`Видалити «${listing.title}»? Це незворотна дія.`)) return
  actionLoading.value = listing.id
  try {
    await adminApi.deleteListing(listing.id)
    listings.value = listings.value.filter(l => l.id !== listing.id)
    total.value--
    toast.success('Оголошення видалено')
  } catch { toast.error('Помилка') }
  finally { actionLoading.value = null }
}

onMounted(load)
</script>

<style scoped>
.admin-page-header {
  display: flex; align-items: flex-start; justify-content: space-between;
  gap: 16px; flex-wrap: wrap; margin-bottom: 24px;
}
.admin-page-title  { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; }
.admin-page-sub    { color: var(--text-muted); font-size: 0.875rem; margin-top: 4px; }
.admin-page-sub strong { color: var(--text-secondary); }

.admin-controls { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }

.admin-select {
  padding: 9px 14px; border-radius: var(--radius-lg);
  border: 1px solid rgba(255,255,255,0.09);
  color: var(--text-secondary); font-size: 0.875rem;
  background: rgba(255,255,255,0.05);
  backdrop-filter: blur(20px);
  cursor: pointer; outline: none;
}
.admin-select option { background: #1a1d27; }

.admin-search {
  display: flex; align-items: center; gap: 8px;
  padding: 0 14px; border-radius: var(--radius-lg);
}
.admin-search svg { color: var(--text-muted); flex-shrink: 0; }
.admin-search__input {
  background: none; border: none; outline: none;
  color: var(--text-primary); font-size: 0.875rem;
  padding: 10px 0; width: 200px;
}
.admin-search__input::placeholder { color: var(--text-muted); }

/* Таблиця */
.admin-table { border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 8px; }
.admin-table table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.admin-table thead tr { border-bottom: 1px solid rgba(255,255,255,0.07); }
.admin-table th {
  padding: 12px 14px; text-align: left;
  font-size: 0.72rem; font-weight: 600;
  color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em;
}
.admin-table td {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: var(--text-secondary);
  vertical-align: middle;
}
.admin-table tr:last-child td { border-bottom: none; }
.admin-table tr:hover td { background: rgba(255,255,255,0.025); }
.admin-table__muted { color: var(--text-muted); }
.admin-table__price { color: var(--accent); font-weight: 600; }
.admin-table__empty { text-align: center; color: var(--text-muted); padding: 32px !important; }

.admin-table__tag {
  display: inline-block; padding: 2px 9px;
  background: rgba(255,255,255,0.06); border-radius: var(--radius-sm);
  font-size: 0.78rem; font-weight: 500;
}

/* Мініатюра */
.listing-thumb {
  width: 40px; height: 40px; border-radius: var(--radius-sm);
  overflow: hidden; background: rgba(255,255,255,0.06);
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2rem; flex-shrink: 0;
}
.listing-thumb img { width: 100%; height: 100%; object-fit: cover; }

.listing-title-cell { max-width: 200px; }
.listing-title-link {
  color: var(--text-primary); font-weight: 500;
  display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
  overflow: hidden; transition: color var(--transition);
}
.listing-title-link:hover { color: var(--accent); }

/* Select статусу прямо в таблиці */
.status-select {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-sm);
  color: var(--text-secondary); font-size: 0.78rem; font-weight: 600;
  padding: 4px 8px; cursor: pointer; outline: none;
  transition: all var(--transition);
}
.status-select option { background: #1a1d27; }
.status-select.active      { color: var(--success); border-color: rgba(52,211,153,0.25); }
.status-select.sold        { color: var(--info);    border-color: rgba(79,142,247,0.25); }
.status-select.deactivated { color: var(--text-muted); }

/* Кнопки дій */
.action-btn {
  width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-sm); font-size: 0.85rem;
  transition: all var(--transition);
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
}
.action-btn:hover:not(:disabled) { transform: scale(1.1); }
.action-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.action-btn--danger:hover { background: rgba(248,113,113,0.15); border-color: rgba(248,113,113,0.3); }

.mini-spinner {
  display: block; width: 12px; height: 12px;
  border: 2px solid rgba(255,255,255,0.15);
  border-top-color: var(--text-primary);
  border-radius: 50%; animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
