<template>
  <div class="home">

    <!-- Hero секція -->
    <section class="hero">
      <div class="container hero__inner">
        <div class="hero__text">
          <h1 class="hero__title">
            Знайди свій<br />
            <span class="hero__title-accent">ідеальний інструмент</span>
          </h1>
          <p class="hero__sub">
            Тисячі оголошень від продавців по всій Україні
          </p>
        </div>

        <div class="hero__search-wrap">
          <div class="hero__search">
            <input
              v-model="searchInput"
              type="text"
              placeholder="Гітара, синтезатор, барабани..."
              class="hero__search-input"
              @keyup.enter="onSearch"
            />
            <button class="hero__search-btn" @click="onSearch">
              <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
              </svg>
              Пошук
            </button>
          </div>

          <div class="hero__tags">
            <button
              v-for="tag in popularTags"
              :key="tag.value"
              class="hero__tag"
              :class="{ active: store.filters.category === tag.value }"
              @click="onTagClick(tag)"
            >
              {{ tag.icon }} {{ tag.label }}
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Каталог -->
    <section class="catalog">
      <div class="container catalog__inner">

        <CatalogFilters class="catalog__filters" />

        <div class="catalog__main">
          <!-- Топ-бар -->
          <div class="catalog__topbar">
            <p class="catalog__count">
              <template v-if="!store.loading">
                <strong>{{ store.total }}</strong>
                {{ pluralize(store.total) }}
                <span v-if="store.filters.q" class="catalog__query">
                  по «{{ store.filters.q }}»
                </span>
              </template>
              <span v-else class="skeleton" style="width:120px;height:18px;border-radius:4px;display:inline-block" />
            </p>

            <div class="catalog__active-filters">
              <span v-if="store.filters.q" class="catalog__filter-badge" @click="clearFilter('q')">
                "{{ store.filters.q }}" ✕
              </span>
              <span v-if="store.filters.category" class="catalog__filter-badge" @click="clearFilter('category')">
                {{ categoryLabel(store.filters.category) }} ✕
              </span>
              <span v-if="store.filters.condition" class="catalog__filter-badge" @click="clearFilter('condition')">
                {{ conditionLabel(store.filters.condition) }} ✕
              </span>
            </div>
          </div>

          <!-- Сітка -->
          <div class="catalog__grid">
            <template v-if="store.loading">
              <ListingCardSkeleton v-for="n in 12" :key="n" />
            </template>

            <template v-else-if="store.items.length">
              <ListingCard
                v-for="listing in store.items"
                :key="listing.id"
                :listing="listing"
              />
            </template>

            <div v-else class="catalog__empty">
              <span class="catalog__empty-icon">🎵</span>
              <p class="catalog__empty-title">Нічого не знайдено</p>
              <p class="catalog__empty-sub">Спробуй інші фільтри або пошуковий запит</p>
              <button class="catalog__empty-btn" @click="resetAndFetch">Скинути фільтри</button>
            </div>
          </div>

          <AppPagination
            :current="store.currentPage"
            :pages="store.pages"
            @change="onPageChange"
          />
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useListingsStore } from '@/stores/listings'
import { useFormatters } from '@/composables/useFormatters'
import CatalogFilters from '@/components/listing/CatalogFilters.vue'
import ListingCard from '@/components/listing/ListingCard.vue'
import ListingCardSkeleton from '@/components/listing/ListingCardSkeleton.vue'
import AppPagination from '@/components/ui/AppPagination.vue'

const store = useListingsStore()
const { categoryLabel, conditionLabel } = useFormatters()
const searchInput = ref('')

const popularTags = [
  { label: 'Гітари',   value: 'guitars',   icon: '🎸' },
  { label: 'Клавішні', value: 'keyboards', icon: '🎹' },
  { label: 'Ударні',   value: 'drums',     icon: '🥁' },
  { label: 'Духові',   value: 'wind',      icon: '🎺' },
  { label: 'DJ',       value: 'dj',        icon: '🎧' },
  { label: 'Студійне', value: 'studio',    icon: '🎙️' },
]

onMounted(() => { store.fetchListings() })

watch(() => store.filters.q, (val) => { searchInput.value = val ?? '' })

function onSearch() {
  store.setFilter('q', searchInput.value.trim() || null)
  store.fetchListings()
}

function onTagClick(tag) {
  store.setFilter('category', store.filters.category === tag.value ? null : tag.value)
  store.fetchListings()
}

function clearFilter(key) {
  store.setFilter(key, null)
  if (key === 'q') searchInput.value = ''
  store.fetchListings()
}

function resetAndFetch() {
  store.resetFilters()
  searchInput.value = ''
  store.fetchListings()
}

function onPageChange(page) {
  store.setFilter('page', page)
  store.fetchListings()
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function pluralize(n) {
  const m10 = n % 10, m100 = n % 100
  if (m100 >= 11 && m100 <= 19) return 'оголошень'
  if (m10 === 1) return 'оголошення'
  if (m10 >= 2 && m10 <= 4) return 'оголошення'
  return 'оголошень'
}
</script>

<style scoped>
.hero {
  background: linear-gradient(135deg, var(--bg-surface) 0%, var(--bg-elevated) 100%);
  border-bottom: 1px solid var(--border);
  padding: 56px 0 48px;
  position: relative;
  overflow: hidden;
}
.hero::before {
  content: '';
  position: absolute;
  top: -60px; right: -60px;
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(245,158,11,0.08) 0%, transparent 70%);
  pointer-events: none;
}
.hero__inner { display: flex; flex-direction: column; gap: 28px; max-width: 720px; }
.hero__title {
  font-size: clamp(1.8rem, 4vw, 2.8rem);
  font-weight: 800;
  line-height: 1.2;
}
.hero__title-accent { color: var(--accent); }
.hero__sub { color: var(--text-secondary); font-size: 1.05rem; margin-top: 8px; }
.hero__search-wrap { display: flex; flex-direction: column; gap: 14px; }
.hero__search {
  display: flex;
  background: var(--bg-base);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  overflow: hidden;
  transition: border-color var(--transition), box-shadow var(--transition);
}
.hero__search:focus-within { border-color: var(--accent); box-shadow: var(--shadow-accent); }
.hero__search-input {
  flex: 1; background: none; border: none; outline: none;
  padding: 14px 20px; font-size: 1rem; color: var(--text-primary);
}
.hero__search-input::placeholder { color: var(--text-muted); }
.hero__search-btn {
  display: flex; align-items: center; gap: 8px;
  padding: 0 22px; background: var(--accent); color: #000;
  font-weight: 700; font-size: 0.9rem; flex-shrink: 0;
  transition: background var(--transition);
}
.hero__search-btn:hover { background: var(--accent-hover); }
.hero__tags { display: flex; gap: 8px; flex-wrap: wrap; }
.hero__tag {
  padding: 6px 14px; border-radius: var(--radius-xl);
  background: var(--bg-elevated); border: 1px solid var(--border);
  font-size: 0.82rem; color: var(--text-secondary);
  transition: all var(--transition);
}
.hero__tag:hover, .hero__tag.active {
  border-color: var(--accent); color: var(--accent); background: var(--accent-dim);
}

.catalog { padding: 32px 0 48px; }
.catalog__inner {
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 28px;
  align-items: start;
}
@media (max-width: 900px) {
  .catalog__inner { grid-template-columns: 1fr; }
  .catalog__filters { display: none; }
}
.catalog__topbar {
  display: flex; align-items: center; gap: 12px;
  flex-wrap: wrap; margin-bottom: 20px;
}
.catalog__count { font-size: 0.9rem; color: var(--text-secondary); }
.catalog__count strong { color: var(--text-primary); }
.catalog__query { color: var(--accent); }
.catalog__active-filters { display: flex; gap: 8px; flex-wrap: wrap; }
.catalog__filter-badge {
  display: inline-flex; align-items: center; gap: 6px;
  padding: 4px 10px; background: var(--accent-dim);
  border: 1px solid var(--accent); color: var(--accent);
  border-radius: var(--radius-sm); font-size: 0.8rem;
  cursor: pointer; transition: opacity var(--transition);
}
.catalog__filter-badge:hover { opacity: 0.75; }
.catalog__grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(230px, 1fr));
  gap: 20px;
}
.catalog__empty {
  grid-column: 1 / -1; display: flex; flex-direction: column;
  align-items: center; padding: 80px 0; gap: 12px; text-align: center;
}
.catalog__empty-icon { font-size: 3.5rem; opacity: 0.4; }
.catalog__empty-title { font-size: 1.1rem; font-weight: 600; }
.catalog__empty-sub { color: var(--text-muted); font-size: 0.9rem; }
.catalog__empty-btn {
  margin-top: 8px; padding: 9px 20px; border-radius: var(--radius-md);
  background: var(--accent); color: #000; font-weight: 600;
  transition: background var(--transition);
}
.catalog__empty-btn:hover { background: var(--accent-hover); }
</style>
