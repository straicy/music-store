<template>
  <div v-if="pages > 1" class="pagination">
    <button
      class="pagination__btn"
      :disabled="current <= 1"
      @click="emit('change', current - 1)"
    >
      ‹
    </button>

    <template v-for="p in visiblePages" :key="p">
      <span v-if="p === '...'" class="pagination__dots">…</span>
      <button
        v-else
        class="pagination__btn"
        :class="{ active: p === current }"
        @click="emit('change', p)"
      >
        {{ p }}
      </button>
    </template>

    <button
      class="pagination__btn"
      :disabled="current >= pages"
      @click="emit('change', current + 1)"
    >
      ›
    </button>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  current: { type: Number, required: true },
  pages:   { type: Number, required: true },
})
const emit = defineEmits(['change'])

const visiblePages = computed(() => {
  const { current, pages } = props
  if (pages <= 7) return Array.from({ length: pages }, (_, i) => i + 1)

  const result = []
  const add = (n) => { if (!result.includes(n) && n >= 1 && n <= pages) result.push(n) }

  add(1)
  if (current > 3) result.push('...')
  for (let i = Math.max(2, current - 1); i <= Math.min(pages - 1, current + 1); i++) add(i)
  if (current < pages - 2) result.push('...')
  add(pages)

  return result
})
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  padding: 24px 0;
}
.pagination__btn {
  min-width: 36px; height: 36px;
  padding: 0 8px;
  border-radius: var(--radius-md);
  background: var(--bg-surface);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  font-size: 0.875rem;
  transition: all var(--transition);
}
.pagination__btn:hover:not(:disabled) {
  border-color: var(--accent);
  color: var(--accent);
}
.pagination__btn.active {
  background: var(--accent);
  border-color: var(--accent);
  color: #000;
  font-weight: 700;
}
.pagination__btn:disabled { opacity: 0.35; cursor: not-allowed; }
.pagination__dots { color: var(--text-muted); padding: 0 4px; }
</style>
