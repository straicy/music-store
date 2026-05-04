<template>
  <aside class="filters">
    <div class="filters__header">
      <h3 class="filters__title">Фільтри</h3>
      <button v-if="hasActiveFilters" class="filters__reset" @click="onReset">
        Скинути
      </button>
    </div>

    <!-- Категорія -->
    <div class="filters__group">
      <p class="filters__label">Категорія</p>
      <div class="filters__options">
        <button
          v-for="(label, key) in CATEGORY_LABELS"
          :key="key"
          class="filters__chip"
          :class="{ active: store.filters.category === key }"
          @click="toggle('category', key)"
        >
          {{ label }}
        </button>
      </div>
    </div>

    <!-- Стан -->
    <div class="filters__group">
      <p class="filters__label">Стан</p>
      <div class="filters__options">
        <button
          v-for="(label, key) in CONDITION_LABELS"
          :key="key"
          class="filters__chip"
          :class="{ active: store.filters.condition === key }"
          @click="toggle('condition', key)"
        >
          {{ label }}
        </button>
      </div>
    </div>

    <!-- Ціна -->
    <div class="filters__group">
      <p class="filters__label">Ціна (₴)</p>
      <div class="filters__price-row">
        <input
          v-model.number="priceMin"
          type="number"
          placeholder="від"
          class="filters__input"
          min="0"
          @change="applyPrice"
        />
        <span class="filters__price-sep">—</span>
        <input
          v-model.number="priceMax"
          type="number"
          placeholder="до"
          class="filters__input"
          min="0"
          @change="applyPrice"
        />
      </div>
    </div>

    <!-- Бренд -->
    <div class="filters__group">
      <p class="filters__label">Бренд</p>
      <input
        v-model="brand"
        type="text"
        placeholder="Fender, Gibson..."
        class="filters__input filters__input--full"
        @keyup.enter="applyBrand"
        @blur="applyBrand"
      />
    </div>

    <!-- Місто -->
    <div class="filters__group">
      <p class="filters__label">Місто</p>
      <input
        v-model="city"
        type="text"
        placeholder="Київ, Харків..."
        class="filters__input filters__input--full"
        @keyup.enter="applyCity"
        @blur="applyCity"
      />
    </div>

    <!-- Сортування -->
    <div class="filters__group">
      <p class="filters__label">Сортування</p>
      <select class="filters__select" v-model="sortVal" @change="applySort">
        <option value="newest">Новіші спочатку</option>
        <option value="price_asc">Ціна: від низької</option>
        <option value="price_desc">Ціна: від високої</option>
        <option value="views">За переглядами</option>
      </select>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useListingsStore } from '@/stores/listings'
import { useFormatters } from '@/composables/useFormatters'

const store = useListingsStore()
const { CATEGORY_LABELS, CONDITION_LABELS } = useFormatters()

// Локальні стани для полів з debounce-логікою
const priceMin = ref(store.filters.price_min ?? '')
const priceMax = ref(store.filters.price_max ?? '')
const brand    = ref(store.filters.brand ?? '')
const city     = ref(store.filters.city ?? '')
const sortVal  = ref(store.filters.sort ?? 'newest')

const hasActiveFilters = computed(() =>
  store.filters.category || store.filters.condition ||
  store.filters.price_min || store.filters.price_max ||
  store.filters.brand || store.filters.city
)

// Тогл для category / condition (клік по тому ж — скидає)
function toggle(key, value) {
  const current = store.filters[key]
  store.setFilter(key, current === value ? null : value)
  store.fetchListings()
}

function applyPrice() {
  store.setFilter('price_min', priceMin.value || null)
  store.setFilter('price_max', priceMax.value || null)
  store.fetchListings()
}

function applyBrand() {
  store.setFilter('brand', brand.value.trim() || null)
  store.fetchListings()
}

function applyCity() {
  store.setFilter('city', city.value.trim() || null)
  store.fetchListings()
}

function applySort() {
  store.setFilter('sort', sortVal.value)
  store.fetchListings()
}

function onReset() {
  store.resetFilters()
  priceMin.value = ''
  priceMax.value = ''
  brand.value    = ''
  city.value     = ''
  sortVal.value  = 'newest'
  store.fetchListings()
}
</script>

<style scoped>
.filters {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  position: sticky;
  top: 88px; /* navbar + gap */
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.filters__header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.filters__title {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--text-primary);
}
.filters__reset {
  font-size: 0.8rem;
  color: var(--accent);
  transition: opacity var(--transition);
}
.filters__reset:hover { opacity: 0.75; }

.filters__group { display: flex; flex-direction: column; gap: 8px; }
.filters__label {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

/* Чіпи для вибору категорії / стану */
.filters__options { display: flex; flex-wrap: wrap; gap: 6px; }
.filters__chip {
  padding: 5px 11px;
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  color: var(--text-secondary);
  transition: all var(--transition);
}
.filters__chip:hover { border-color: var(--accent); color: var(--text-primary); }
.filters__chip.active {
  background: var(--accent-dim);
  border-color: var(--accent);
  color: var(--accent);
  font-weight: 600;
}

/* Інпути */
.filters__input {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  padding: 8px 10px;
  font-size: 0.85rem;
  outline: none;
  transition: border-color var(--transition);
  width: 100%;
}
.filters__input:focus { border-color: var(--accent); }
.filters__input::placeholder { color: var(--text-muted); }
.filters__input--full { width: 100%; }

.filters__price-row {
  display: flex;
  align-items: center;
  gap: 8px;
}
.filters__price-row .filters__input { width: 0; flex: 1; }
.filters__price-sep { color: var(--text-muted); flex-shrink: 0; }

/* Select */
.filters__select {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  color: var(--text-primary);
  padding: 8px 10px;
  font-size: 0.85rem;
  outline: none;
  width: 100%;
  cursor: pointer;
  transition: border-color var(--transition);
}
.filters__select:focus { border-color: var(--accent); }
.filters__select option { background: var(--bg-elevated); }
</style>
