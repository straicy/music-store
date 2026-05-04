<template>
  <article class="card" @click="goToListing">
    <!-- Зображення -->
    <div class="card__image-wrap">
      <img
        v-if="listing.images?.length"
        :src="listing.images[0]"
        :alt="listing.title"
        class="card__image"
        loading="lazy"
      />
      <div v-else class="card__image card__image--empty">
        <span class="card__image-icon">🎸</span>
      </div>

      <!-- Стан товару -->
      <span class="card__condition" :style="{ color: conditionColor(listing.condition) }">
        {{ conditionLabel(listing.condition) }}
      </span>

      <!-- Кнопка обраного -->
      <button
        class="card__fav-btn"
        :class="{ 'card__fav-btn--active': listing.is_favorited }"
        @click.stop="onToggleFav"
        :title="listing.is_favorited ? 'Видалити з обраного' : 'Додати до обраного'"
      >
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
        </svg>
      </button>
    </div>

    <!-- Контент -->
    <div class="card__body">
      <p class="card__category">{{ categoryLabel(listing.category) }}</p>
      <h3 class="card__title">{{ listing.title }}</h3>

      <div class="card__meta">
        <span v-if="listing.brand" class="card__brand">{{ listing.brand }}</span>
        <span v-if="listing.city" class="card__city">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/>
          </svg>
          {{ listing.city }}
        </span>
      </div>

      <div class="card__footer">
        <span class="card__price">{{ formatPrice(listing.price) }}</span>
        <span class="card__views">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
          </svg>
          {{ listing.views }}
        </span>
      </div>
    </div>
  </article>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { useFormatters } from '@/composables/useFormatters'
import { useListingsStore } from '@/stores/listings'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'vue-toastification'

const props = defineProps({
  listing: { type: Object, required: true },
})

const router   = useRouter()
const store    = useListingsStore()
const auth     = useAuthStore()
const toast    = useToast()
const { formatPrice, conditionLabel, categoryLabel, conditionColor } = useFormatters()

function goToListing() {
  router.push(`/listings/${props.listing.id}`)
}

async function onToggleFav() {
  if (!auth.isLoggedIn) {
    toast.warning('Увійдіть, щоб додавати до обраного')
    return
  }
  await store.toggleFavorite(props.listing.id)
}
</script>

<style scoped>
.card {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  cursor: pointer;
  transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
  display: flex;
  flex-direction: column;
}
.card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-md);
  border-color: var(--bg-hover);
}

/* Зображення */
.card__image-wrap {
  position: relative;
  aspect-ratio: 4/3;
  overflow: hidden;
  background: var(--bg-elevated);
  flex-shrink: 0;
}
.card__image {
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.card:hover .card__image { transform: scale(1.04); }
.card__image--empty {
  display: flex;
  align-items: center;
  justify-content: center;
}
.card__image-icon { font-size: 3rem; opacity: 0.3; }

/* Бейдж стану */
.card__condition {
  position: absolute;
  top: 10px; left: 10px;
  background: rgba(0,0,0,0.65);
  backdrop-filter: blur(6px);
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  font-size: 0.72rem;
  font-weight: 600;
}

/* Кнопка обраного */
.card__fav-btn {
  position: absolute;
  top: 8px; right: 8px;
  width: 34px; height: 34px;
  background: rgba(0,0,0,0.55);
  backdrop-filter: blur(6px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  transition: all var(--transition);
}
.card__fav-btn:hover { background: rgba(0,0,0,0.8); color: var(--accent); }
.card__fav-btn--active { color: var(--accent); }
.card__fav-btn--active svg { fill: var(--accent); }

/* Контент */
.card__body {
  padding: 14px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  flex: 1;
}
.card__category {
  font-size: 0.72rem;
  color: var(--accent);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.card__title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  line-height: 1.35;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.card__meta {
  display: flex;
  align-items: center;
  gap: 10px;
  flex-wrap: wrap;
}
.card__brand {
  font-size: 0.8rem;
  color: var(--text-secondary);
  background: var(--bg-elevated);
  padding: 2px 8px;
  border-radius: var(--radius-sm);
}
.card__city {
  display: flex;
  align-items: center;
  gap: 3px;
  font-size: 0.78rem;
  color: var(--text-muted);
}
.card__footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: auto;
  padding-top: 8px;
  border-top: 1px solid var(--border);
}
.card__price {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
}
.card__views {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.78rem;
  color: var(--text-muted);
}
</style>
