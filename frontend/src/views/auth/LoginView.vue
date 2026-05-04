<template>
  <div class="auth-page">
    <!-- Декоративні orb-и на фоні -->
    <div class="auth-page__orb auth-page__orb--1" />
    <div class="auth-page__orb auth-page__orb--2" />

    <div class="auth-card glass">
      <!-- Лого -->
      <div class="auth-card__logo">
        <span class="auth-card__logo-icon">🎸</span>
        <span class="auth-card__logo-text">Music<span class="accent">Store</span></span>
      </div>

      <div class="auth-card__header">
        <h1 class="auth-card__title">З поверненням</h1>
        <p class="auth-card__sub">Увійдіть у свій акаунт</p>
      </div>

      <!-- Форма -->
      <form class="auth-form" @submit.prevent="onSubmit">

        <!-- Email -->
        <div class="auth-form__field" :class="{ error: errors.email }">
          <label class="auth-form__label">Email</label>
          <div class="auth-form__input-wrap" :class="{ focused: focused === 'email' }">
            <svg class="auth-form__input-icon" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/><polyline points="22,6 12,13 2,6"/>
            </svg>
            <input
              v-model="form.email"
              type="email"
              placeholder="your@email.com"
              class="auth-form__input"
              autocomplete="email"
              @focus="focused = 'email'"
              @blur="focused = null; validateEmail()"
            />
          </div>
          <p v-if="errors.email" class="auth-form__error">{{ errors.email }}</p>
        </div>

        <!-- Пароль -->
        <div class="auth-form__field" :class="{ error: errors.password }">
          <label class="auth-form__label">Пароль</label>
          <div class="auth-form__input-wrap" :class="{ focused: focused === 'password' }">
            <svg class="auth-form__input-icon" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>
            </svg>
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              placeholder="Мінімум 8 символів"
              class="auth-form__input"
              autocomplete="current-password"
              @focus="focused = 'password'"
              @blur="focused = null"
            />
            <button type="button" class="auth-form__eye" @click="showPassword = !showPassword">
              <svg v-if="!showPassword" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
          <p v-if="errors.password" class="auth-form__error">{{ errors.password }}</p>
        </div>

        <!-- Кнопка -->
        <button
          type="submit"
          class="auth-form__submit"
          :class="{ loading: auth.loading }"
          :disabled="auth.loading"
        >
          <span v-if="!auth.loading">Увійти</span>
          <span v-else class="auth-form__spinner" />
        </button>

        <!-- Розділювач -->
        <div class="auth-form__divider">
          <span>або</span>
        </div>

        <!-- Посилання на реєстрацію -->
        <p class="auth-form__switch">
          Ще немає акаунту?
          <RouterLink to="/register" class="auth-form__link">Зареєструватись</RouterLink>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()

const form = reactive({ email: '', password: '' })
const errors = reactive({ email: '', password: '' })
const focused = ref(null)
const showPassword = ref(false)

function validateEmail() {
  if (!form.email) { errors.email = 'Email обовʼязковий'; return false }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) { errors.email = 'Невірний формат email'; return false }
  errors.email = ''
  return true
}

function validate() {
  let ok = validateEmail()
  if (!form.password) { errors.password = 'Пароль обовʼязковий'; ok = false }
  else errors.password = ''
  return ok
}

async function onSubmit() {
  if (!validate()) return
  try {
    await auth.login({ email: form.email, password: form.password })
  } catch {
    // помилка вже показана через toast в store
  }
}
</script>

<style scoped>
/* ── Сторінка ────────────────────────────────────────────── */
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 24px;
  position: relative;
  overflow: hidden;
}

/* Фонові orb-и */
.auth-page__orb {
  position: fixed;
  border-radius: 50%;
  filter: blur(80px);
  pointer-events: none;
  z-index: 0;
}
.auth-page__orb--1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(79,142,247,0.18) 0%, transparent 70%);
  top: -100px; left: -100px;
  animation: float 8s ease-in-out infinite alternate;
}
.auth-page__orb--2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(245,166,35,0.15) 0%, transparent 70%);
  bottom: -80px; right: -80px;
  animation: float 10s ease-in-out infinite alternate-reverse;
}
@keyframes float {
  from { transform: translate(0, 0) scale(1); }
  to   { transform: translate(30px, 20px) scale(1.05); }
}

/* ── Картка ──────────────────────────────────────────────── */
.auth-card {
  position: relative; z-index: 1;
  width: 100%; max-width: 420px;
  border-radius: var(--radius-2xl);
  padding: 40px 36px;
  box-shadow: var(--shadow-lg), 0 0 0 1px rgba(255,255,255,0.04);
  animation: cardIn 0.5s cubic-bezier(0.16,1,0.3,1);
}
@keyframes cardIn {
  from { opacity: 0; transform: translateY(24px) scale(0.97); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

.auth-card__logo {
  display: flex; align-items: center; justify-content: center;
  gap: 8px; margin-bottom: 28px;
  font-size: 1.4rem; font-weight: 800; letter-spacing: -0.02em;
}
.auth-card__logo-icon { font-size: 1.6rem; }
.accent { color: var(--accent); }

.auth-card__header { text-align: center; margin-bottom: 32px; }
.auth-card__title {
  font-size: 1.6rem; font-weight: 800;
  letter-spacing: -0.03em; line-height: 1.2;
}
.auth-card__sub { color: var(--text-secondary); font-size: 0.9rem; margin-top: 6px; }

/* ── Форма ────────────────────────────────────────────────── */
.auth-form { display: flex; flex-direction: column; gap: 18px; }

.auth-form__field { display: flex; flex-direction: column; gap: 8px; }
.auth-form__label {
  font-size: 0.8rem; font-weight: 600;
  color: var(--text-secondary);
  letter-spacing: 0.04em; text-transform: uppercase;
}

.auth-form__input-wrap {
  display: flex; align-items: center; gap: 10px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: var(--radius-lg);
  padding: 0 14px;
  transition: all 0.25s ease;
}
.auth-form__input-wrap.focused {
  background: rgba(255,255,255,0.08);
  border-color: rgba(245,166,35,0.5);
  box-shadow: 0 0 0 3px rgba(245,166,35,0.1), 0 0 20px rgba(245,166,35,0.08);
}
.auth-form__field.error .auth-form__input-wrap {
  border-color: rgba(248,113,113,0.5);
  box-shadow: 0 0 0 3px rgba(248,113,113,0.1);
}
.auth-form__input-icon { color: var(--text-muted); flex-shrink: 0; }
.auth-form__input {
  flex: 1; background: none; border: none; outline: none;
  color: var(--text-primary); font-size: 0.9rem;
  padding: 13px 0;
}
.auth-form__input::placeholder { color: var(--text-muted); }
.auth-form__eye {
  color: var(--text-muted); flex-shrink: 0;
  transition: color var(--transition);
}
.auth-form__eye:hover { color: var(--text-secondary); }

.auth-form__error {
  font-size: 0.78rem; color: var(--error);
  padding-left: 4px;
}

/* Кнопка submit */
.auth-form__submit {
  width: 100%; height: 50px;
  background: linear-gradient(135deg, var(--accent) 0%, #ff9f0a 100%);
  color: #000; font-weight: 800; font-size: 0.95rem;
  border-radius: var(--radius-lg);
  transition: all var(--transition-slow);
  box-shadow: 0 4px 20px rgba(245,166,35,0.3);
  margin-top: 4px;
  display: flex; align-items: center; justify-content: center;
  letter-spacing: 0.01em;
}
.auth-form__submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(245,166,35,0.45);
}
.auth-form__submit:active:not(:disabled) { transform: translateY(0); }
.auth-form__submit.loading { opacity: 0.75; cursor: not-allowed; }

/* Spinner */
.auth-form__spinner {
  display: block;
  width: 20px; height: 20px;
  border: 2px solid rgba(0,0,0,0.25);
  border-top-color: #000;
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Розділювач */
.auth-form__divider {
  display: flex; align-items: center; gap: 12px;
  color: var(--text-muted); font-size: 0.8rem;
}
.auth-form__divider::before,
.auth-form__divider::after {
  content: ''; flex: 1;
  height: 1px; background: rgba(255,255,255,0.08);
}

/* Посилання */
.auth-form__switch {
  text-align: center;
  font-size: 0.875rem; color: var(--text-secondary);
}
.auth-form__link {
  color: var(--accent); font-weight: 600;
  transition: opacity var(--transition);
}
.auth-form__link:hover { opacity: 0.8; }
</style>
