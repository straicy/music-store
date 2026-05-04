<template>
  <div class="detail-page">
    <div class="detail-page__orb detail-page__orb--1" />
    <div class="detail-page__orb detail-page__orb--2" />

    <!-- Завантаження -->
    <div v-if="loading" class="container detail-page__inner">
      <div class="detail-layout">
        <div class="detail-layout__left">
          <div class="skeleton" style="aspect-ratio:4/3;border-radius:18px;width:100%" />
          <div style="display:flex;gap:8px;margin-top:10px">
            <div v-for="n in 4" :key="n" class="skeleton" style="width:70px;height:70px;border-radius:10px;flex-shrink:0" />
          </div>
        </div>
        <div class="detail-layout__right">
          <div class="skeleton" style="height:32px;border-radius:8px;width:80%;margin-bottom:12px" />
          <div class="skeleton" style="height:20px;border-radius:6px;width:50%;margin-bottom:24px" />
          <div class="skeleton" style="height:48px;border-radius:12px;width:60%;margin-bottom:32px" />
          <div v-for="n in 5" :key="n" class="skeleton" style="height:16px;border-radius:4px;margin-bottom:10px" />
        </div>
      </div>
    </div>

    <!-- 404 -->
    <div v-else-if="!listing" class="container detail-page__not-found">
      <p class="detail-page__not-found-icon">🎵</p>
      <h2>Оголошення не знайдено</h2>
      <RouterLink to="/" class="detail-page__back-btn">← До каталогу</RouterLink>
    </div>

    <!-- Контент -->
    <div v-else class="container detail-page__inner">

      <!-- Хлібні крихти -->
      <nav class="breadcrumb">
        <RouterLink to="/" class="breadcrumb__item">Каталог</RouterLink>
        <span class="breadcrumb__sep">›</span>
        <span class="breadcrumb__item breadcrumb__item--active">{{ categoryLabel(listing.category) }}</span>
        <span class="breadcrumb__sep">›</span>
        <span class="breadcrumb__item breadcrumb__item--active">{{ listing.title }}</span>
      </nav>

      <div class="detail-layout">

        <!-- ЛІВА КОЛОНКА — галерея -->
        <div class="detail-layout__left">

          <!-- Головне фото -->
          <div class="gallery">
            <div class="gallery__main" @click="openLightbox(activeImg)">
              <img
                v-if="listing.images?.length"
                :src="listing.images[activeImg]"
                :alt="listing.title"
                class="gallery__main-img"
              />
              <div v-else class="gallery__main-empty">
                <span>🎸</span>
              </div>

              <!-- Стан товару -->
              <span class="gallery__condition" :style="{ color: conditionColor(listing.condition) }">
                {{ conditionLabel(listing.condition) }}
              </span>

              <!-- Кнопка збільшення -->
              <button class="gallery__zoom" v-if="listing.images?.length">
                <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>
                </svg>
              </button>

              <!-- Навігація -->
              <button v-if="listing.images?.length > 1" class="gallery__nav gallery__nav--prev" @click.stop="prevImg">‹</button>
              <button v-if="listing.images?.length > 1" class="gallery__nav gallery__nav--next" @click.stop="nextImg">›</button>
            </div>

            <!-- Мініатюри -->
            <div v-if="listing.images?.length > 1" class="gallery__thumbs">
              <button
                v-for="(img, idx) in listing.images"
                :key="idx"
                class="gallery__thumb"
                :class="{ active: activeImg === idx }"
                @click="activeImg = idx"
              >
                <img :src="img" :alt="`Фото ${idx + 1}`" />
              </button>
            </div>
          </div>

          <!-- Опис (мобайл — після галереї) -->
          <div class="detail-description glass">
            <h3 class="detail-description__title">Опис</h3>
            <p class="detail-description__text" :class="{ expanded: descExpanded }">
              {{ listing.description }}
            </p>
            <button
              v-if="listing.description.length > 300"
              class="detail-description__toggle"
              @click="descExpanded = !descExpanded"
            >
              {{ descExpanded ? 'Згорнути ▲' : 'Читати повністю ▼' }}
            </button>
          </div>
        </div>

        <!-- ПРАВА КОЛОНКА — деталі -->
        <div class="detail-layout__right">

          <!-- Основна інфо -->
          <div class="detail-info glass">
            <!-- Категорія і перегляди -->
            <div class="detail-info__top">
              <span class="detail-info__category">{{ categoryLabel(listing.category) }}</span>
              <span class="detail-info__views">
                <svg width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>
                </svg>
                {{ listing.views }} переглядів
              </span>
            </div>

            <h1 class="detail-info__title">{{ listing.title }}</h1>

            <div class="detail-info__price">{{ formatPrice(listing.price) }}</div>

            <!-- Мета-дані -->
            <div class="detail-info__tags">
              <span v-if="listing.brand" class="detail-tag">
                🏷️ {{ listing.brand }}
              </span>
              <span v-if="listing.city" class="detail-tag">
                📍 {{ listing.city }}
              </span>
              <span class="detail-tag" :style="{ color: conditionColor(listing.condition) }">
                ● {{ conditionLabel(listing.condition) }}
              </span>
            </div>

            <div class="detail-info__date">
              Опубліковано {{ formatDateShort(listing.created_at) }}
            </div>

            <!-- Кнопки дій -->
            <div class="detail-actions">
              <!-- Написати продавцю -->
              <button
                v-if="!isOwner"
                class="detail-actions__contact"
                @click="onContact"
              >
                <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                </svg>
                Написати продавцю
              </button>

              <!-- Обране -->
              <button
                class="detail-actions__fav"
                :class="{ active: listing.is_favorited }"
                @click="onToggleFav"
                :title="listing.is_favorited ? 'Видалити з обраного' : 'Додати до обраного'"
              >
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/>
                </svg>
              </button>

              <!-- Поділитись -->
              <button class="detail-actions__share" @click="onShare" title="Поділитись">
                <svg width="18" height="18" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
                  <circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/>
                  <line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/>
                </svg>
              </button>
            </div>

            <!-- Кнопки власника -->
            <div v-if="isOwner" class="detail-owner-actions">
              <RouterLink :to="`/listings/${listing.id}/edit`" class="detail-owner-actions__edit">
                ✏️ Редагувати
              </RouterLink>
              <button class="detail-owner-actions__delete" @click="onDelete">
                🗑️ Видалити
              </button>
            </div>
          </div>

          <!-- Картка продавця -->
          <div class="seller-card glass">
            <h3 class="seller-card__title">Продавець</h3>
            <div class="seller-card__body">
              <div class="seller-card__avatar">
                {{ listing.seller_name.charAt(0).toUpperCase() }}
              </div>
              <div class="seller-card__info">
                <p class="seller-card__name">{{ listing.seller_name }}</p>
                <p class="seller-card__listings">{{ sellerListingsCount }} оголошень</p>
              </div>
            </div>
            <button
              v-if="!isOwner"
              class="seller-card__btn"
              @click="onContact"
            >
              Написати
            </button>
          </div>

          <!-- Безпека -->
          <div class="safety-card glass">
            <p class="safety-card__title">🛡️ Безпечна угода</p>
            <ul class="safety-card__list">
              <li>Зустрічайся в публічному місці</li>
              <li>Перевіряй товар перед оплатою</li>
              <li>Не переводь гроші наперед</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- Lightbox -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="lightboxOpen" class="lightbox" @click="lightboxOpen = false">
          <button class="lightbox__close" @click="lightboxOpen = false">✕</button>
          <button class="lightbox__nav lightbox__nav--prev" @click.stop="prevImg">‹</button>
          <img
            :src="listing?.images?.[activeImg]"
            class="lightbox__img"
            @click.stop
          />
          <button class="lightbox__nav lightbox__nav--next" @click.stop="nextImg">›</button>
          <p class="lightbox__counter">{{ activeImg + 1 }} / {{ listing?.images?.length }}</p>
        </div>
      </Transition>
    </Teleport>

    <!-- Модалка: написати продавцю -->
    <Teleport to="body">
      <Transition name="fade">
        <div v-if="contactOpen" class="modal-overlay" @click.self="contactOpen = false">
          <Transition name="slide-up">
            <div v-if="contactOpen" class="contact-modal glass">
              <div class="contact-modal__header">
                <h3>Написати продавцю</h3>
                <button @click="contactOpen = false">✕</button>
              </div>
              <div class="contact-modal__listing">
                <img v-if="listing.images?.length" :src="listing.images[0]" class="contact-modal__img" />
                <div>
                  <p class="contact-modal__listing-title">{{ listing.title }}</p>
                  <p class="contact-modal__listing-price">{{ formatPrice(listing.price) }}</p>
                </div>
              </div>
              <textarea
                v-model="messageText"
                class="contact-modal__textarea"
                placeholder="Привіт! Чи ще актуальне оголошення?"
                rows="4"
                maxlength="1000"
              />
              <button
                class="contact-modal__send"
                :disabled="!messageText.trim() || sending"
                @click="sendMessage"
              >
                <span v-if="!sending">Надіслати</span>
                <span v-else class="mini-spinner" />
              </button>
            </div>
          </Transition>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { listingsApi, messagesApi, favoritesApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { useFormatters } from '@/composables/useFormatters'
import { useToast } from 'vue-toastification'

const route  = useRoute()
const router = useRouter()
const auth   = useAuthStore()
const toast  = useToast()
const { formatPrice, formatDateShort, conditionLabel, categoryLabel, conditionColor } = useFormatters()

const listing     = ref(null)
const loading     = ref(true)
const activeImg   = ref(0)
const descExpanded = ref(false)
const lightboxOpen = ref(false)
const contactOpen  = ref(false)
const messageText  = ref('Привіт! Чи ще актуальне оголошення?')
const sending      = ref(false)
const sellerListingsCount = ref(0)

const isOwner = computed(() =>
  auth.isLoggedIn && listing.value?.seller_id === auth.user?.id
)

function prevImg() {
  if (!listing.value?.images?.length) return
  activeImg.value = (activeImg.value - 1 + listing.value.images.length) % listing.value.images.length
}
function nextImg() {
  if (!listing.value?.images?.length) return
  activeImg.value = (activeImg.value + 1) % listing.value.images.length
}
function openLightbox(idx) {
  if (!listing.value?.images?.length) return
  activeImg.value = idx
  lightboxOpen.value = true
}

function onContact() {
  if (!auth.isLoggedIn) {
    toast.warning('Увійдіть щоб написати продавцю')
    router.push('/login')
    return
  }
  contactOpen.value = true
}

async function onToggleFav() {
  if (!auth.isLoggedIn) {
    toast.warning('Увійдіть щоб додавати до обраного')
    return
  }
  try {
    const { data } = await favoritesApi.toggle(listing.value.id)
    listing.value.is_favorited = data.is_favorited
    toast.success(data.is_favorited ? 'Додано до обраного' : 'Видалено з обраного')
  } catch { toast.error('Помилка') }
}

async function sendMessage() {
  if (!messageText.value.trim()) return
  sending.value = true
  try {
    const { data } = await messagesApi.send({
      receiver_id: listing.value.seller_id,
      listing_id:  listing.value.id,
      text:        messageText.value.trim(),
    })
    toast.success('Повідомлення надіслано!')
    contactOpen.value = false
    router.push(`/chat/${data.conversation_id}`)
  } catch (err) {
    toast.error(err.response?.data?.detail ?? 'Помилка надсилання')
  } finally {
    sending.value = false
  }
}

async function onDelete() {
  if (!confirm('Видалити оголошення? Це незворотна дія.')) return
  try {
    await listingsApi.delete(listing.value.id)
    toast.success('Оголошення видалено')
    router.push('/')
  } catch { toast.error('Помилка видалення') }
}

function onShare() {
  if (navigator.share) {
    navigator.share({ title: listing.value.title, url: location.href })
  } else {
    navigator.clipboard.writeText(location.href)
    toast.success('Посилання скопійовано!')
  }
}

onMounted(async () => {
  try {
    const { data } = await listingsApi.getOne(route.params.id)
    listing.value = data
  } catch {
    listing.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.detail-page {
  min-height: 100vh;
  padding: 32px 0 80px;
  position: relative;
}
.detail-page__orb {
  position: fixed; border-radius: 50%;
  filter: blur(100px); pointer-events: none; z-index: 0;
}
.detail-page__orb--1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(79,142,247,0.08) 0%, transparent 70%);
  top: -80px; left: -80px;
}
.detail-page__orb--2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(245,166,35,0.07) 0%, transparent 70%);
  bottom: 0; right: -80px;
}
.detail-page__inner { position: relative; z-index: 1; }

/* Not found */
.detail-page__not-found {
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
  min-height: 60vh; gap: 12px; text-align: center;
}
.detail-page__not-found-icon { font-size: 4rem; }
.detail-page__back-btn {
  margin-top: 8px; padding: 10px 22px;
  background: var(--accent); color: #000;
  border-radius: var(--radius-lg); font-weight: 700;
}

/* Breadcrumb */
.breadcrumb {
  display: flex; align-items: center; gap: 6px;
  font-size: 0.8rem; color: var(--text-muted);
  margin-bottom: 24px; flex-wrap: wrap;
}
.breadcrumb__item { transition: color var(--transition); }
.breadcrumb__item:not(.breadcrumb__item--active):hover { color: var(--accent); }
.breadcrumb__item--active { color: var(--text-secondary); }
.breadcrumb__sep { color: var(--text-muted); }

/* Layout */
.detail-layout {
  display: grid;
  grid-template-columns: 1fr 380px;
  gap: 28px;
  align-items: start;
}
@media (max-width: 960px) {
  .detail-layout { grid-template-columns: 1fr; }
}
.detail-layout__left  { display: flex; flex-direction: column; gap: 20px; }
.detail-layout__right { display: flex; flex-direction: column; gap: 16px; position: sticky; top: 88px; }

/* Gallery */
.gallery { display: flex; flex-direction: column; gap: 10px; }
.gallery__main {
  position: relative;
  aspect-ratio: 4/3;
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: rgba(255,255,255,0.04);
  border: 1px solid rgba(255,255,255,0.08);
  cursor: zoom-in;
}
.gallery__main-img {
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}
.gallery__main:hover .gallery__main-img { transform: scale(1.02); }
.gallery__main-empty {
  display: flex; align-items: center; justify-content: center;
  height: 100%; font-size: 5rem; opacity: 0.2;
}
.gallery__condition {
  position: absolute; top: 14px; left: 14px;
  background: rgba(0,0,0,0.65); backdrop-filter: blur(8px);
  padding: 4px 12px; border-radius: var(--radius-sm);
  font-size: 0.78rem; font-weight: 600;
}
.gallery__zoom {
  position: absolute; bottom: 12px; right: 12px;
  background: rgba(0,0,0,0.55); backdrop-filter: blur(8px);
  width: 36px; height: 36px; border-radius: var(--radius-sm);
  display: flex; align-items: center; justify-content: center;
  color: #fff; opacity: 0; transition: opacity var(--transition);
}
.gallery__main:hover .gallery__zoom { opacity: 1; }
.gallery__nav {
  position: absolute; top: 50%; transform: translateY(-50%);
  background: rgba(0,0,0,0.55); backdrop-filter: blur(8px);
  width: 40px; height: 40px; border-radius: 50%;
  color: #fff; font-size: 1.4rem;
  display: flex; align-items: center; justify-content: center;
  transition: all var(--transition);
  opacity: 0;
}
.gallery__main:hover .gallery__nav { opacity: 1; }
.gallery__nav--prev { left: 12px; }
.gallery__nav--next { right: 12px; }
.gallery__nav:hover { background: rgba(0,0,0,0.8); }

.gallery__thumbs {
  display: flex; gap: 8px; overflow-x: auto;
  scrollbar-width: none;
}
.gallery__thumbs::-webkit-scrollbar { display: none; }
.gallery__thumb {
  width: 72px; height: 72px; flex-shrink: 0;
  border-radius: var(--radius-md); overflow: hidden;
  border: 2px solid transparent;
  transition: all var(--transition); cursor: pointer;
}
.gallery__thumb img { width: 100%; height: 100%; object-fit: cover; }
.gallery__thumb.active { border-color: var(--accent); box-shadow: 0 0 12px rgba(245,166,35,0.3); }
.gallery__thumb:hover:not(.active) { border-color: rgba(255,255,255,0.3); }

/* Description */
.detail-description {
  border-radius: var(--radius-lg); padding: 24px;
  display: flex; flex-direction: column; gap: 12px;
}
.detail-description__title { font-size: 0.9rem; font-weight: 700; }
.detail-description__text {
  font-size: 0.9rem; color: var(--text-secondary);
  line-height: 1.7; white-space: pre-wrap;
  max-height: 120px; overflow: hidden;
  transition: max-height 0.4s ease;
}
.detail-description__text.expanded { max-height: 2000px; }
.detail-description__toggle {
  font-size: 0.8rem; color: var(--accent);
  align-self: flex-start; transition: opacity var(--transition);
}
.detail-description__toggle:hover { opacity: 0.75; }

/* Info card */
.detail-info {
  border-radius: var(--radius-lg); padding: 24px;
  display: flex; flex-direction: column; gap: 14px;
}
.detail-info__top {
  display: flex; align-items: center; justify-content: space-between;
}
.detail-info__category {
  font-size: 0.75rem; font-weight: 700;
  color: var(--accent); text-transform: uppercase; letter-spacing: 0.06em;
}
.detail-info__views {
  display: flex; align-items: center; gap: 4px;
  font-size: 0.78rem; color: var(--text-muted);
}
.detail-info__title {
  font-size: 1.35rem; font-weight: 800;
  letter-spacing: -0.02em; line-height: 1.3;
}
.detail-info__price {
  font-size: 1.9rem; font-weight: 900;
  letter-spacing: -0.03em; color: var(--text-primary);
}
.detail-info__tags { display: flex; gap: 8px; flex-wrap: wrap; }
.detail-tag {
  padding: 4px 12px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: var(--radius-sm);
  font-size: 0.8rem; color: var(--text-secondary);
}
.detail-info__date { font-size: 0.76rem; color: var(--text-muted); }

/* Actions */
.detail-actions {
  display: flex; gap: 10px; align-items: center;
  padding-top: 4px;
}
.detail-actions__contact {
  flex: 1; height: 48px;
  display: flex; align-items: center; justify-content: center; gap: 8px;
  background: linear-gradient(135deg, var(--accent), #ff9f0a);
  color: #000; font-weight: 800; font-size: 0.9rem;
  border-radius: var(--radius-lg);
  transition: all var(--transition-slow);
  box-shadow: 0 4px 20px rgba(245,166,35,0.3);
}
.detail-actions__contact:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 32px rgba(245,166,35,0.45);
}
.detail-actions__fav,
.detail-actions__share {
  width: 48px; height: 48px;
  display: flex; align-items: center; justify-content: center;
  border-radius: var(--radius-lg);
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  color: var(--text-secondary);
  transition: all var(--transition);
}
.detail-actions__fav:hover,
.detail-actions__share:hover {
  background: rgba(255,255,255,0.09);
  color: var(--text-primary);
}
.detail-actions__fav.active { color: var(--accent); }
.detail-actions__fav.active svg { fill: var(--accent); }

/* Owner actions */
.detail-owner-actions {
  display: flex; gap: 8px;
  padding-top: 4px; border-top: 1px solid rgba(255,255,255,0.07);
}
.detail-owner-actions__edit,
.detail-owner-actions__delete {
  flex: 1; height: 40px;
  display: flex; align-items: center; justify-content: center; gap: 6px;
  border-radius: var(--radius-md); font-size: 0.85rem; font-weight: 600;
  transition: all var(--transition);
  border: 1px solid rgba(255,255,255,0.09);
}
.detail-owner-actions__edit {
  background: rgba(255,255,255,0.05); color: var(--text-secondary);
}
.detail-owner-actions__edit:hover {
  background: rgba(255,255,255,0.09); color: var(--text-primary);
}
.detail-owner-actions__delete {
  background: rgba(248,113,113,0.08); color: var(--error);
  border-color: rgba(248,113,113,0.2);
}
.detail-owner-actions__delete:hover { background: rgba(248,113,113,0.15); }

/* Seller card */
.seller-card {
  border-radius: var(--radius-lg); padding: 20px;
  display: flex; flex-direction: column; gap: 14px;
}
.seller-card__title { font-size: 0.78rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.05em; }
.seller-card__body  { display: flex; align-items: center; gap: 12px; }
.seller-card__avatar {
  width: 44px; height: 44px; border-radius: 50%;
  background: linear-gradient(135deg, var(--accent), #ff6b35);
  display: flex; align-items: center; justify-content: center;
  font-weight: 700; font-size: 1.1rem; color: #000; flex-shrink: 0;
}
.seller-card__name     { font-weight: 600; }
.seller-card__listings { font-size: 0.8rem; color: var(--text-muted); margin-top: 2px; }
.seller-card__btn {
  width: 100%; height: 40px;
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: var(--radius-md);
  color: var(--text-secondary); font-size: 0.875rem; font-weight: 600;
  transition: all var(--transition);
}
.seller-card__btn:hover {
  background: rgba(255,255,255,0.10);
  color: var(--text-primary);
}

/* Safety */
.safety-card {
  border-radius: var(--radius-lg); padding: 16px 20px;
  display: flex; flex-direction: column; gap: 8px;
}
.safety-card__title { font-size: 0.85rem; font-weight: 600; }
.safety-card__list {
  list-style: none; display: flex; flex-direction: column; gap: 4px;
}
.safety-card__list li {
  font-size: 0.78rem; color: var(--text-muted);
  padding-left: 12px; position: relative;
}
.safety-card__list li::before {
  content: '✓'; position: absolute; left: 0;
  color: var(--success); font-size: 0.7rem;
}

/* Lightbox */
.lightbox {
  position: fixed; inset: 0; z-index: 999;
  background: rgba(0,0,0,0.92); backdrop-filter: blur(12px);
  display: flex; align-items: center; justify-content: center;
  cursor: zoom-out;
}
.lightbox__img {
  max-width: 90vw; max-height: 90vh;
  object-fit: contain; border-radius: var(--radius-lg);
  cursor: default;
}
.lightbox__close {
  position: absolute; top: 20px; right: 20px;
  width: 40px; height: 40px; border-radius: 50%;
  background: rgba(255,255,255,0.1);
  color: #fff; font-size: 1rem;
  display: flex; align-items: center; justify-content: center;
  transition: background var(--transition);
}
.lightbox__close:hover { background: rgba(255,255,255,0.2); }
.lightbox__nav {
  position: absolute; top: 50%; transform: translateY(-50%);
  width: 48px; height: 48px; border-radius: 50%;
  background: rgba(255,255,255,0.1); color: #fff; font-size: 1.6rem;
  display: flex; align-items: center; justify-content: center;
  transition: background var(--transition);
}
.lightbox__nav:hover { background: rgba(255,255,255,0.2); }
.lightbox__nav--prev { left: 20px; }
.lightbox__nav--next { right: 20px; }
.lightbox__counter {
  position: absolute; bottom: 20px; left: 50%; transform: translateX(-50%);
  color: rgba(255,255,255,0.6); font-size: 0.875rem;
}

/* Contact modal */
.modal-overlay {
  position: fixed; inset: 0; z-index: 500;
  background: rgba(0,0,0,0.7); backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center; padding: 24px;
}
.contact-modal {
  width: 100%; max-width: 440px;
  border-radius: var(--radius-2xl); padding: 28px;
  display: flex; flex-direction: column; gap: 18px;
  box-shadow: var(--shadow-lg);
}
.contact-modal__header {
  display: flex; align-items: center; justify-content: space-between;
}
.contact-modal__header h3 { font-size: 1rem; font-weight: 700; }
.contact-modal__header button { color: var(--text-muted); font-size: 1rem; transition: color var(--transition); }
.contact-modal__header button:hover { color: var(--text-primary); }
.contact-modal__listing {
  display: flex; gap: 12px; align-items: center;
  padding: 12px; background: rgba(255,255,255,0.04);
  border-radius: var(--radius-md);
}
.contact-modal__img {
  width: 52px; height: 52px; border-radius: var(--radius-sm);
  object-fit: cover; flex-shrink: 0;
}
.contact-modal__listing-title { font-size: 0.875rem; font-weight: 500; }
.contact-modal__listing-price { font-size: 0.8rem; color: var(--accent); font-weight: 700; margin-top: 2px; }
.contact-modal__textarea {
  width: 100%; background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: var(--radius-md); color: var(--text-primary);
  padding: 12px 14px; font-size: 0.9rem; outline: none;
  resize: none; transition: border-color 0.25s ease;
}
.contact-modal__textarea:focus { border-color: rgba(245,166,35,0.5); }
.contact-modal__textarea::placeholder { color: var(--text-muted); }
.contact-modal__send {
  width: 100%; height: 48px;
  background: linear-gradient(135deg, var(--accent), #ff9f0a);
  color: #000; font-weight: 800; font-size: 0.9rem;
  border-radius: var(--radius-lg);
  display: flex; align-items: center; justify-content: center;
  transition: all var(--transition-slow);
  box-shadow: 0 4px 20px rgba(245,166,35,0.3);
}
.contact-modal__send:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 28px rgba(245,166,35,0.4);
}
.contact-modal__send:disabled { opacity: 0.5; cursor: not-allowed; }
.mini-spinner {
  display: block; width: 18px; height: 18px;
  border: 2px solid rgba(0,0,0,0.2); border-top-color: #000;
  border-radius: 50%; animation: spin 0.6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }
</style>
