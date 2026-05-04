<template>
  <div class="dashboard">
    <div class="dashboard__header">
      <h1 class="dashboard__title">Дашборд</h1>
      <p class="dashboard__sub">Загальна статистика платформи</p>
    </div>

    <!-- Stat cards -->
    <div class="stat-grid" v-if="!loading">
      <div class="stat-card glass" v-for="s in stats" :key="s.label" :style="{ '--glow': s.glow }">
        <div class="stat-card__icon">{{ s.icon }}</div>
        <div class="stat-card__body">
          <p class="stat-card__value">{{ s.value }}</p>
          <p class="stat-card__label">{{ s.label }}</p>
        </div>
        <div class="stat-card__glow" />
      </div>
    </div>

    <!-- Skeleton -->
    <div class="stat-grid" v-else>
      <div class="stat-card glass" v-for="n in 5" :key="n">
        <div class="skeleton" style="width:40px;height:40px;border-radius:10px" />
        <div style="display:flex;flex-direction:column;gap:8px">
          <div class="skeleton" style="width:60px;height:28px;border-radius:6px" />
          <div class="skeleton" style="width:100px;height:14px;border-radius:4px" />
        </div>
      </div>
    </div>

    <!-- Останні оголошення -->
    <div class="dashboard__section">
      <div class="dashboard__section-header">
        <h2 class="dashboard__section-title">Останні оголошення</h2>
        <RouterLink to="/admin/listings" class="dashboard__section-link">Всі →</RouterLink>
      </div>

      <div class="admin-table glass">
        <table>
          <thead>
            <tr>
              <th>Назва</th>
              <th>Категорія</th>
              <th>Продавець</th>
              <th>Ціна</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingListings">
              <td colspan="5"><div class="skeleton" style="height:18px;border-radius:4px" /></td>
            </tr>
            <tr v-else v-for="l in recentListings" :key="l.id">
              <td class="admin-table__title">{{ l.title }}</td>
              <td><span class="admin-table__tag">{{ l.category }}</span></td>
              <td class="admin-table__muted">{{ l.seller_name }}</td>
              <td class="admin-table__price">{{ formatPrice(l.price) }}</td>
              <td><span class="admin-table__status" :class="l.status">{{ statusLabel(l.status) }}</span></td>
            </tr>
            <tr v-if="!loadingListings && !recentListings.length">
              <td colspan="5" class="admin-table__empty">Оголошень поки немає</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Останні юзери -->
    <div class="dashboard__section">
      <div class="dashboard__section-header">
        <h2 class="dashboard__section-title">Нові користувачі</h2>
        <RouterLink to="/admin/users" class="dashboard__section-link">Всі →</RouterLink>
      </div>

      <div class="admin-table glass">
        <table>
          <thead>
            <tr>
              <th>Ім'я</th>
              <th>Email</th>
              <th>Оголошення</th>
              <th>Роль</th>
              <th>Статус</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="loadingUsers">
              <td colspan="5"><div class="skeleton" style="height:18px;border-radius:4px" /></td>
            </tr>
            <tr v-else v-for="u in recentUsers" :key="u.id">
              <td class="admin-table__title">{{ u.name }}</td>
              <td class="admin-table__muted">{{ u.email }}</td>
              <td class="admin-table__muted">{{ u.listings_count }}</td>
              <td><span class="admin-table__tag" :class="{ accent: u.role === 'admin' }">{{ u.role }}</span></td>
              <td><span class="admin-table__status" :class="u.is_banned ? 'banned' : 'active'">{{ u.is_banned ? 'Заблоковано' : 'Активний' }}</span></td>
            </tr>
            <tr v-if="!loadingUsers && !recentUsers.length">
              <td colspan="5" class="admin-table__empty">Користувачів поки немає</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { adminApi } from '@/api'
import { useFormatters } from '@/composables/useFormatters'

const { formatPrice } = useFormatters()

const loading         = ref(true)
const loadingListings = ref(true)
const loadingUsers    = ref(true)
const statsData       = ref(null)
const recentListings  = ref([])
const recentUsers     = ref([])

const stats = computed(() => {
  if (!statsData.value) return []
  const s = statsData.value
  return [
    { icon: '👥', label: 'Всього користувачів', value: s.users.total,      glow: 'rgba(79,142,247,0.3)' },
    { icon: '🚫', label: 'Заблоковано',          value: s.users.banned,     glow: 'rgba(248,113,113,0.3)' },
    { icon: '📋', label: 'Всього оголошень',     value: s.listings.total,   glow: 'rgba(245,166,35,0.3)' },
    { icon: '✅', label: 'Активні оголошення',   value: s.listings.active,  glow: 'rgba(52,211,153,0.3)' },
    { icon: '💬', label: 'Повідомлень',          value: s.messages.total,   glow: 'rgba(167,139,250,0.3)' },
  ]
})

function statusLabel(s) {
  return { active: 'Активне', sold: 'Продано', deactivated: 'Знято' }[s] ?? s
}

onMounted(async () => {
  try {
    const [statsRes, listingsRes, usersRes] = await Promise.all([
      adminApi.getStats(),
      adminApi.getListings({ limit: 5, page: 1 }),
      adminApi.getUsers({ limit: 5, page: 1 }),
    ])
    statsData.value      = statsRes.data
    recentListings.value = listingsRes.data.items
    recentUsers.value    = usersRes.data.items
  } finally {
    loading.value = loadingListings.value = loadingUsers.value = false
  }
})
</script>

<style scoped>
.dashboard__header { margin-bottom: 28px; }
.dashboard__title  { font-size: 1.6rem; font-weight: 800; letter-spacing: -0.03em; }
.dashboard__sub    { color: var(--text-secondary); font-size: 0.9rem; margin-top: 4px; }

/* Stat grid */
.stat-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
  margin-bottom: 36px;
}

.stat-card {
  position: relative;
  border-radius: var(--radius-lg);
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  overflow: hidden;
  transition: all var(--transition-slow);
}
.stat-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 32px rgba(0,0,0,0.4), 0 0 24px var(--glow);
  border-color: rgba(255,255,255,0.14);
}
.stat-card__glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at 0% 0%, var(--glow) 0%, transparent 60%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}
.stat-card:hover .stat-card__glow { opacity: 1; }

.stat-card__icon { font-size: 2rem; flex-shrink: 0; }
.stat-card__value {
  font-size: 1.8rem; font-weight: 800;
  letter-spacing: -0.04em; line-height: 1;
}
.stat-card__label { font-size: 0.78rem; color: var(--text-muted); margin-top: 4px; }

/* Секції */
.dashboard__section { margin-bottom: 32px; }
.dashboard__section-header {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: 14px;
}
.dashboard__section-title { font-size: 1rem; font-weight: 700; }
.dashboard__section-link {
  font-size: 0.825rem; color: var(--accent);
  transition: opacity var(--transition);
}
.dashboard__section-link:hover { opacity: 0.75; }

/* Таблиця */
.admin-table {
  border-radius: var(--radius-lg);
  overflow: hidden;
}
.admin-table table {
  width: 100%; border-collapse: collapse;
  font-size: 0.875rem;
}
.admin-table thead tr {
  border-bottom: 1px solid rgba(255,255,255,0.07);
}
.admin-table th {
  padding: 12px 16px;
  text-align: left;
  font-size: 0.75rem; font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase; letter-spacing: 0.05em;
}
.admin-table td {
  padding: 13px 16px;
  border-bottom: 1px solid rgba(255,255,255,0.04);
  color: var(--text-secondary);
}
.admin-table tr:last-child td { border-bottom: none; }
.admin-table tr:hover td { background: rgba(255,255,255,0.03); }

.admin-table__title { color: var(--text-primary); font-weight: 500; }
.admin-table__muted { color: var(--text-muted); }
.admin-table__price { color: var(--accent); font-weight: 600; }
.admin-table__empty { text-align: center; color: var(--text-muted); padding: 24px !important; }

.admin-table__tag {
  display: inline-block;
  padding: 2px 8px;
  background: rgba(255,255,255,0.06);
  border-radius: var(--radius-sm);
  font-size: 0.78rem; font-weight: 500;
}
.admin-table__tag.accent { background: var(--accent-dim); color: var(--accent); }

.admin-table__status {
  display: inline-block; padding: 3px 10px;
  border-radius: 99px; font-size: 0.75rem; font-weight: 600;
}
.admin-table__status.active   { background: rgba(52,211,153,0.12); color: var(--success); }
.admin-table__status.sold     { background: rgba(79,142,247,0.12); color: var(--info); }
.admin-table__status.deactivated { background: rgba(255,255,255,0.06); color: var(--text-muted); }
.admin-table__status.banned   { background: rgba(248,113,113,0.12); color: var(--error); }
</style>
