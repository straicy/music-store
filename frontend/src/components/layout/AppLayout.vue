<template>
  <div class="app-shell">
    <AppNavbar />
    <main class="main-content">
      <slot />
    </main>
    <AppFooter />
  </div>
</template>

<script setup>
import AppNavbar from './AppNavbar.vue'
import AppFooter from './AppFooter.vue'
</script>

<style scoped>
.app-shell {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex: 1;
  padding-top: 72px; /* висота navbar */
}
</style>
