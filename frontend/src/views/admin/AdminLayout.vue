<template>
  <div class="admin-shell">
    <aside class="admin-sidebar glass">
      <div class="admin-sidebar__brand">
        <span>⚙️</span>
        <span>Адмін-панель</span>
      </div>

      <nav class="admin-sidebar__nav">
        <RouterLink to="/admin" class="admin-sidebar__link" :class="{ active: isExact('/admin') }">
          <svg width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/></svg>
          Дашборд
        </RouterLink>
        <RouterLink to="/admin/users" class="admin-sidebar__link" :class="{ active: isActive('/admin/users') }">
          <svg width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
          Користувачі
        </RouterLink>
        <RouterLink to="/admin/listings" class="admin-sidebar__link" :class="{ active: isActive('/admin/listings') }">
          <svg width="17" height="17" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/></svg>
          Оголошення
        </RouterLink>
      </nav>

      <RouterLink to="/" class="admin-sidebar__back">
        <svg width="15" height="15" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
        На сайт
      </RouterLink>
    </aside>

    <main class="admin-content">
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
const isExact  = (p) => route.path === p
const isActive = (p) => route.path.startsWith(p)
</script>

<style scoped>
.admin-shell {
  display: flex;
  min-height: calc(100vh - 68px);
}

.admin-sidebar {
  width: 230px;
  flex-shrink: 0;
  border-right: 1px solid rgba(255,255,255,0.07);
  padding: 24px 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
  position: sticky;
  top: 68px;
  height: calc(100vh - 68px);
}

.admin-sidebar__brand {
  display: flex; align-items: center; gap: 8px;
  font-weight: 700; font-size: 0.9rem;
  color: var(--text-secondary);
  padding: 0 10px;
  margin-bottom: 16px;
}

.admin-sidebar__nav {
  display: flex; flex-direction: column; gap: 3px;
  flex: 1;
}

.admin-sidebar__link {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  font-size: 0.875rem; font-weight: 500;
  transition: all var(--transition);
  border: 1px solid transparent;
}
.admin-sidebar__link:hover {
  background: rgba(255,255,255,0.06);
  color: var(--text-primary);
}
.admin-sidebar__link.active {
  background: var(--accent-dim);
  border-color: rgba(245,166,35,0.2);
  color: var(--accent);
  font-weight: 600;
  box-shadow: 0 0 12px rgba(245,166,35,0.08);
}

.admin-sidebar__back {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  color: var(--text-muted);
  font-size: 0.825rem;
  transition: all var(--transition);
  border: 1px solid transparent;
  margin-top: auto;
}
.admin-sidebar__back:hover {
  background: rgba(255,255,255,0.05);
  color: var(--text-secondary);
}

.admin-content {
  flex: 1;
  padding: 32px 36px;
  overflow-y: auto;
}
</style>
