<template>
  <div class="admin-users">
    <div class="admin-page-header">
      <div>
        <h1 class="admin-page-title">Користувачі</h1>
        <p class="admin-page-sub">Всього: <strong>{{ total }}</strong></p>
      </div>
      <!-- Пошук -->
      <div class="admin-search glass">
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input v-model="searchQ" type="text" placeholder="Пошук по імені або email..."
          class="admin-search__input" @input="onSearch" />
      </div>
    </div>

    <!-- Таблиця -->
    <div class="admin-table glass">
      <table>
        <thead>
          <tr>
            <th>Користувач</th>
            <th>Email</th>
            <th>Оголошення</th>
            <th>Роль</th>
            <th>Статус</th>
            <th>Дії</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loading">
            <td colspan="6">
              <div v-for="n in 8" :key="n" class="skeleton" style="height:20px;border-radius:4px;margin:10px 0" />
            </td>
          </tr>
          <tr v-else v-for="u in users" :key="u.id" :class="{ banned: u.is_banned }">
            <td>
              <div class="user-cell">
                <div class="user-cell__avatar">{{ u.name.charAt(0).toUpperCase() }}</div>
                <span class="user-cell__name">{{ u.name }}</span>
              </div>
            </td>
            <td class="admin-table__muted">{{ u.email }}</td>
            <td class="admin-table__muted">{{ u.listings_count }}</td>
            <td>
              <span class="admin-table__tag" :class="{ accent: u.role === 'admin' }">
                {{ u.role === 'admin' ? '👑 Admin' : 'User' }}
              </span>
            </td>
            <td>
              <span class="admin-table__status" :class="u.is_banned ? 'banned' : 'active'">
                {{ u.is_banned ? 'Заблоковано' : 'Активний' }}
              </span>
            </td>
            <td>
              <div class="action-btns">
                <button
                  class="action-btn"
                  :class="u.is_banned ? 'action-btn--success' : 'action-btn--danger'"
                  :disabled="actionLoading === u.id"
                  @click="toggleBan(u)"
                  :title="u.is_banned ? 'Розблокувати' : 'Заблокувати'"
                >
                  <span v-if="actionLoading === u.id" class="mini-spinner" />
                  <span v-else>{{ u.is_banned ? '🔓' : '🔒' }}</span>
                </button>
                <button
                  v-if="u.role !== 'admin'"
                  class="action-btn action-btn--info"
                  :disabled="actionLoading === u.id + '_role'"
                  @click="makeAdmin(u)"
                  title="Зробити адміном"
                >
                  👑
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!loading && !users.length">
            <td colspan="6" class="admin-table__empty">Нічого не знайдено</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Пагінація -->
    <AppPagination :current="page" :pages="pages" @change="onPage" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminApi } from '@/api'
import { useToast } from 'vue-toastification'
import AppPagination from '@/components/ui/AppPagination.vue'

const toast = useToast()
const users         = ref([])
const loading       = ref(true)
const actionLoading = ref(null)
const searchQ       = ref('')
const page          = ref(1)
const pages         = ref(1)
const total         = ref(0)
let searchTimer     = null

async function load() {
  loading.value = true
  try {
    const { data } = await adminApi.getUsers({ page: page.value, limit: 15, q: searchQ.value || undefined })
    users.value = data.items
    total.value = data.total
    pages.value = Math.ceil(data.total / 15) || 1
  } finally {
    loading.value = false
  }
}

function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(() => { page.value = 1; load() }, 400)
}

function onPage(p) { page.value = p; load() }

async function toggleBan(u) {
  actionLoading.value = u.id
  try {
    const { data } = await adminApi.toggleBan(u.id)
    u.is_banned = data.is_banned
    toast.success(data.is_banned ? `${u.name} заблоковано` : `${u.name} розблоковано`)
  } catch { toast.error('Помилка') }
  finally { actionLoading.value = null }
}

async function makeAdmin(u) {
  if (!confirm(`Зробити ${u.name} адміністратором?`)) return
  actionLoading.value = u.id + '_role'
  try {
    await adminApi.changeRole(u.id, 'admin')
    u.role = 'admin'
    toast.success(`${u.name} тепер адмін`)
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

.admin-search {
  display: flex; align-items: center; gap: 8px;
  padding: 0 14px; border-radius: var(--radius-lg);
  min-width: 280px;
}
.admin-search svg { color: var(--text-muted); flex-shrink: 0; }
.admin-search__input {
  background: none; border: none; outline: none;
  color: var(--text-primary); font-size: 0.875rem;
  padding: 10px 0; width: 100%;
}
.admin-search__input::placeholder { color: var(--text-muted); }

/* Таблиця */
.admin-table { border-radius: var(--radius-lg); overflow: hidden; margin-bottom: 8px; }
.admin-table table { width: 100%; border-collapse: collapse; font-size: 0.875rem; }
.admin-table thead tr { border-bottom: 1px solid rgba(255,255,255,0.07); }
.admin-table th {
  padding: 12px 16px; text-align: left;
  font-size: 0.72rem; font-weight: 600;
  color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.06em;
}
.admin-table td {
  padding: 13px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: var(--text-secondary);
}
.admin-table tr:last-child td { border-bottom: none; }
.admin-table tr:hover td { background: rgba(255,255,255,0.025); }
.admin-table tr.banned td { opacity: 0.6; }
.admin-table__muted { color: var(--text-muted); }
.admin-table__empty { text-align: center; color: var(--text-muted); padding: 32px !important; }

.admin-table__tag {
  display: inline-block; padding: 2px 9px;
  background: rgba(255,255,255,0.06); border-radius: var(--radius-sm);
  font-size: 0.78rem; font-weight: 500;
}
.admin-table__tag.accent { background: var(--accent-dim); color: var(--accent); }

.admin-table__status {
  display: inline-block; padding: 3px 10px;
  border-radius: 99px; font-size: 0.75rem; font-weight: 600;
}
.admin-table__status.active  { background: rgba(52,211,153,0.12); color: var(--success); }
.admin-table__status.banned  { background: rgba(248,113,113,0.12); color: var(--error); }

/* User cell */
.user-cell { display: flex; align-items: center; gap: 10px; }
.user-cell__avatar {
  width: 30px; height: 30px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #ff6b35);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.75rem; font-weight: 700; color: #000; flex-shrink: 0;
}
.user-cell__name { font-weight: 500; color: var(--text-primary); }

/* Кнопки дій */
.action-btns { display: flex; gap: 6px; }
.action-btn {
  width: 30px; height: 30px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-sm);
  font-size: 0.85rem;
  transition: all var(--transition);
  border: 1px solid rgba(255,255,255,0.08);
  background: rgba(255,255,255,0.04);
}
.action-btn:hover:not(:disabled) { transform: scale(1.1); }
.action-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.action-btn--danger:hover  { background: rgba(248,113,113,0.15); border-color: rgba(248,113,113,0.3); }
.action-btn--success:hover { background: rgba(52,211,153,0.15);  border-color: rgba(52,211,153,0.3); }
.action-btn--info:hover    { background: rgba(79,142,247,0.15);  border-color: rgba(79,142,247,0.3); }

.mini-spinner {
  display: block; width: 14px; height: 14px;
  border: 2px solid rgba(255,255,255,0.2);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
