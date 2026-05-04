<template>
  <footer class="footer">
    <div class="container footer__inner">
      <div class="footer__brand">
        <span class="footer__logo">🎸 Music<span class="accent">Store</span></span>
        <p class="footer__tagline">Маркетплейс музичних інструментів України</p>
      </div>
      <div class="footer__links">
        <RouterLink to="/">Каталог</RouterLink>
        <RouterLink to="/listings/create">Продати</RouterLink>
        <RouterLink to="/favorites">Обране</RouterLink>
      </div>
      <p class="footer__copy">© {{ year }} MusicStore</p>
    </div>
  </footer>
</template>

<script setup>
const year = new Date().getFullYear()
</script>

<style scoped>
.footer {
  background: var(--bg-surface);
  border-top: 1px solid var(--border);
  padding: 32px 0;
  margin-top: auto;
}
.footer__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  flex-wrap: wrap;
}
.footer__logo { font-weight: 700; font-size: 1.1rem; }
.accent { color: var(--accent); }
.footer__tagline { color: var(--text-muted); font-size: 0.8rem; margin-top: 4px; }
.footer__links {
  display: flex;
  gap: 20px;
}
.footer__links a {
  color: var(--text-secondary);
  font-size: 0.875rem;
  transition: color var(--transition);
}
.footer__links a:hover { color: var(--accent); }
.footer__copy { color: var(--text-muted); font-size: 0.8rem; }
</style>
