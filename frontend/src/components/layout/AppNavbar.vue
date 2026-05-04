<template>
  <header class="navbar glass">
    <div class="container navbar__inner">

      <RouterLink to="/" class="navbar__logo">
        <span class="navbar__logo-icon">🎸</span>
        <span class="navbar__logo-text">Music<span class="accent">Store</span></span>
      </RouterLink>

      <div class="navbar__search" :class="{ focused: searchFocused }">
        <svg class="navbar__search-icon" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Пошук інструментів..."
          class="navbar__search-input"
          @keyup.enter="onSearch"
          @focus="searchFocused = true"
          @blur="searchFocused = false"
        />
        <button v-if="searchQuery" class="navbar__search-clear" @click="searchQuery = ''">✕</button>
      </div>

      <nav class="navbar__actions">
        <template v-if="auth.isLoggedIn">
          <RouterLink to="/listings/create" class="navbar__btn-primary">
            <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="M12 5v14M5 12h14"/></svg>
            Додати
          </RouterLink>

          <RouterLink to="/chat" class="navbar__icon-btn" title="Повідомлення">
            <svg width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
            <span v-if="chat.unreadTotal > 0" class="navbar__badge">{{ chat.unreadTotal > 9 ? '9+' : chat.unreadTotal }}</span>
          </RouterLink>

          <RouterLink to="/favorites" class="navbar__icon-btn" title="Обране">
            <svg width="19" height="19" fill="none" stroke="currentColor" stroke-width="1.8" viewBox="0 0 24 24"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
          </RouterLink>

          <div class="navbar__profile" ref="profileMenuRef">
            <button class="navbar__avatar-btn" @click="menuOpen = !menuOpen">
              <span class="navbar__avatar">{{ auth.userName.charAt(0).toUpperCase() }}</span>
              <svg class="navbar__chevron" :class="{ open: menuOpen }" width="12" height="12" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><path d="m6 9 6 6 6-6"/></svg>
            </button>

            <Transition name="slide-up">
              <div v-if="menuOpen" class="navbar__dropdown glass">
                <div class="navbar__dropdown-header">
                  <div class="navbar__dropdown-avatar">{{ auth.userName.charAt(0).toUpperCase() }}</div>
                  <div>
                    <p class="navbar__dropdown-name">{{ auth.userName }}</p>
                    <p class="navbar__dropdown-email">{{ auth.user?.email }}</p>
                  </div>
                </div>
                <div class="navbar__dropdown-body">
                  <RouterLink to="/profile" class="navbar__dropdown-item" @click="menuOpen = false">
                    <span class="navbar__dropdown-item-icon">👤</span> Профіль
                  </RouterLink>
                  <RouterLink to="/my-listings" class="navbar__dropdown-item" @click="menuOpen = false">
                    <span class="navbar__dropdown-item-icon">📋</span> Мої оголошення
                  </RouterLink>
                  <RouterLink to="/favorites" class="navbar__dropdown-item" @click="menuOpen = false">
                    <span class="navbar__dropdown-item-icon">❤️</span> Обране
                  </RouterLink>
                  <RouterLink v-if="auth.isAdmin" to="/admin" class="navbar__dropdown-item" @click="menuOpen = false">
                    <span class="navbar__dropdown-item-icon">⚙️</span> Адмін-панель
                  </RouterLink>
                  <div class="navbar__dropdown-divider" />
                  <button class="navbar__dropdown-item navbar__dropdown-item--danger" @click="handleLogout">
                    <span class="navbar__dropdown-item-icon">🚪</span> Вийти
                  </button>
                </div>
              </div>
            </Transition>
          </div>
        </template>

        <template v-else>
          <RouterLink to="/login" class="navbar__btn-ghost">Вхід</RouterLink>
          <RouterLink to="/register" class="navbar__btn-primary">Реєстрація</RouterLink>
        </template>
      </nav>
    </div>
  </header>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { onClickOutside } from '@vueuse/core'
import { useAuthStore } from '@/stores/auth'
import { useChatStore } from '@/stores/chat'
import { useListingsStore } from '@/stores/listings'

const auth     = useAuthStore()
const chat     = useChatStore()
const listings = useListingsStore()
const router   = useRouter()

const searchQuery   = ref('')
const searchFocused = ref(false)
const menuOpen      = ref(false)
const profileMenuRef = ref(null)

onClickOutside(profileMenuRef, () => { menuOpen.value = false })

function onSearch() {
  if (!searchQuery.value.trim()) return
  listings.setFilter('q', searchQuery.value.trim())
  router.push('/')
}

async function handleLogout() {
  menuOpen.value = false
  await auth.logout()
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0; left: 0; right: 0;
  height: 68px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  z-index: 100;
}

.navbar__inner {
  display: flex;
  align-items: center;
  gap: 14px;
  height: 100%;
}

/* Лого */
.navbar__logo {
  display: flex; align-items: center; gap: 8px;
  font-size: 1.2rem; font-weight: 800;
  white-space: nowrap; flex-shrink: 0;
  letter-spacing: -0.02em;
}
.navbar__logo-icon { font-size: 1.4rem; }
.accent { color: var(--accent); }

/* Пошук */
.navbar__search {
  flex: 1; max-width: 460px;
  display: flex; align-items: center; gap: 8px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-xl);
  padding: 0 14px;
  transition: all 0.25s ease;
}
.navbar__search.focused {
  background: rgba(255,255,255,0.08);
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(245,166,35,0.1), var(--shadow-glow-sm);
}
.navbar__search-icon { color: var(--text-muted); flex-shrink: 0; }
.navbar__search-input {
  flex: 1; background: none; border: none; outline: none;
  color: var(--text-primary); font-size: 0.875rem;
  padding: 10px 0;
}
.navbar__search-input::placeholder { color: var(--text-muted); }
.navbar__search-clear {
  color: var(--text-muted); font-size: 0.75rem;
  transition: color var(--transition);
}
.navbar__search-clear:hover { color: var(--text-primary); }

/* Дії */
.navbar__actions {
  display: flex; align-items: center; gap: 6px;
  flex-shrink: 0; margin-left: auto;
}

/* Іконки */
.navbar__icon-btn {
  position: relative;
  display: flex; align-items: center; justify-content: center;
  width: 38px; height: 38px;
  border-radius: var(--radius-md);
  color: var(--text-secondary);
  transition: all var(--transition);
  border: 1px solid transparent;
}
.navbar__icon-btn:hover {
  background: rgba(255,255,255,0.07);
  border-color: rgba(255,255,255,0.10);
  color: var(--text-primary);
  box-shadow: 0 0 12px rgba(255,255,255,0.04);
}
.navbar__badge {
  position: absolute; top: 4px; right: 4px;
  background: var(--accent); color: #000;
  font-size: 0.6rem; font-weight: 800;
  min-width: 15px; height: 15px;
  border-radius: 99px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 3px;
}

/* Аватар */
.navbar__profile { position: relative; }
.navbar__avatar-btn {
  display: flex; align-items: center; gap: 6px;
  padding: 5px 10px 5px 5px;
  border-radius: var(--radius-xl);
  border: 1px solid transparent;
  transition: all var(--transition);
}
.navbar__avatar-btn:hover {
  background: rgba(255,255,255,0.07);
  border-color: rgba(255,255,255,0.10);
}
.navbar__avatar {
  width: 30px; height: 30px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #ff6b35);
  display: flex; align-items: center; justify-content: center;
  font-size: 0.8rem; font-weight: 700; color: #000;
  flex-shrink: 0;
}
.navbar__chevron {
  color: var(--text-muted);
  transition: transform 0.25s ease;
}
.navbar__chevron.open { transform: rotate(180deg); }

/* Dropdown */
.navbar__dropdown {
  position: absolute; top: calc(100% + 10px); right: 0;
  min-width: 240px;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-lg), 0 0 0 1px rgba(255,255,255,0.05);
  z-index: 200;
}
.navbar__dropdown-header {
  display: flex; align-items: center; gap: 12px;
  padding: 16px;
  border-bottom: 1px solid rgba(255,255,255,0.07);
  background: rgba(255,255,255,0.03);
}
.navbar__dropdown-avatar {
  width: 36px; height: 36px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #ff6b35);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; color: #000; flex-shrink: 0;
}
.navbar__dropdown-name { font-size: 0.875rem; font-weight: 600; }
.navbar__dropdown-email { font-size: 0.75rem; color: var(--text-muted); margin-top: 1px; }
.navbar__dropdown-body { padding: 6px; }
.navbar__dropdown-item {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 12px;
  border-radius: var(--radius-md);
  font-size: 0.875rem; color: var(--text-secondary);
  transition: all var(--transition);
  width: 100%; text-align: left;
}
.navbar__dropdown-item:hover {
  background: rgba(255,255,255,0.07);
  color: var(--text-primary);
}
.navbar__dropdown-item-icon { font-size: 0.95rem; }
.navbar__dropdown-item--danger:hover { color: var(--error); }
.navbar__dropdown-divider {
  height: 1px; background: rgba(255,255,255,0.06);
  margin: 4px 0;
}

/* Кнопки */
.navbar__btn-primary {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--accent), #ff9f0a);
  color: #000; font-weight: 700; font-size: 0.825rem;
  border-radius: var(--radius-xl);
  transition: all var(--transition);
  box-shadow: 0 2px 12px rgba(245,166,35,0.25);
  white-space: nowrap;
}
.navbar__btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(245,166,35,0.4);
}
.navbar__btn-ghost {
  display: inline-flex; align-items: center;
  padding: 7px 14px;
  background: transparent;
  color: var(--text-secondary); font-size: 0.825rem; font-weight: 500;
  border-radius: var(--radius-xl);
  border: 1px solid rgba(255,255,255,0.10);
  transition: all var(--transition);
  white-space: nowrap;
}
.navbar__btn-ghost:hover {
  background: rgba(255,255,255,0.06);
  color: var(--text-primary);
  border-color: rgba(255,255,255,0.18);
}
</style>
