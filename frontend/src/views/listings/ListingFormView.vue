<template>
  <div class="form-page">
    <div class="form-page__orb form-page__orb--1" />
    <div class="form-page__orb form-page__orb--2" />

    <div class="container form-page__inner">
      <!-- Заголовок -->
      <div class="form-page__header">
        <RouterLink to="/" class="form-page__back">
          <svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path d="M19 12H5M12 5l-7 7 7 7"/></svg>
          Назад
        </RouterLink>
        <h1 class="form-page__title">{{ isEdit ? 'Редагувати оголошення' : 'Нове оголошення' }}</h1>
        <p class="form-page__sub">Заповни деталі про інструмент</p>
      </div>

      <form @submit.prevent="onSubmit" class="listing-form">
        <div class="listing-form__layout">

          <!-- ЛІВА КОЛОНКА — основна інфо -->
          <div class="listing-form__main">

            <!-- Назва -->
            <div class="form-card glass">
              <h2 class="form-card__title">Основна інформація</h2>

              <div class="form-field" :class="{ error: errors.title }">
                <label class="form-field__label">Назва оголошення *</label>
                <input
                  v-model="form.title"
                  type="text"
                  placeholder="Наприклад: Fender Stratocaster American Standard 2019"
                  class="form-field__input"
                  maxlength="150"
                  @blur="validateField('title')"
                />
                <div class="form-field__meta">
                  <span class="form-field__error">{{ errors.title }}</span>
                  <span class="form-field__count">{{ form.title.length }}/150</span>
                </div>
              </div>

              <div class="form-field" :class="{ error: errors.description }">
                <label class="form-field__label">Опис *</label>
                <textarea
                  v-model="form.description"
                  placeholder="Детально опиши стан, комплектацію, історію інструменту..."
                  class="form-field__textarea"
                  rows="6"
                  maxlength="3000"
                  @blur="validateField('description')"
                />
                <div class="form-field__meta">
                  <span class="form-field__error">{{ errors.description }}</span>
                  <span class="form-field__count">{{ form.description.length }}/3000</span>
                </div>
              </div>
            </div>

            <!-- Категорія і стан -->
            <div class="form-card glass">
              <h2 class="form-card__title">Категорія та стан</h2>

              <div class="form-row">
                <div class="form-field" :class="{ error: errors.category }">
                  <label class="form-field__label">Категорія *</label>
                  <div class="form-field__chips">
                    <button
                      v-for="(label, key) in CATEGORY_LABELS"
                      :key="key"
                      type="button"
                      class="form-chip"
                      :class="{ active: form.category === key }"
                      @click="form.category = key; errors.category = ''"
                    >
                      {{ CATEGORY_ICONS[key] }} {{ label }}
                    </button>
                  </div>
                  <span class="form-field__error">{{ errors.category }}</span>
                </div>
              </div>

              <div class="form-field" :class="{ error: errors.condition }">
                <label class="form-field__label">Стан *</label>
                <div class="form-field__chips">
                  <button
                    v-for="(label, key) in CONDITION_LABELS"
                    :key="key"
                    type="button"
                    class="form-chip form-chip--condition"
                    :class="{ active: form.condition === key }"
                    :style="form.condition === key ? { borderColor: conditionColor(key), color: conditionColor(key), background: conditionColor(key) + '18' } : {}"
                    @click="form.condition = key; errors.condition = ''"
                  >
                    {{ label }}
                  </button>
                </div>
                <span class="form-field__error">{{ errors.condition }}</span>
              </div>
            </div>

            <!-- Деталі -->
            <div class="form-card glass">
              <h2 class="form-card__title">Деталі</h2>
              <div class="form-row">
                <div class="form-field">
                  <label class="form-field__label">Бренд</label>
                  <input v-model="form.brand" type="text" placeholder="Fender, Gibson, Yamaha..." class="form-field__input" />
                </div>
                <div class="form-field">
                  <label class="form-field__label">Місто</label>
                  <input v-model="form.city" type="text" placeholder="Київ, Львів..." class="form-field__input" />
                </div>
              </div>
            </div>
          </div>

          <!-- ПРАВА КОЛОНКА — фото і ціна -->
          <div class="listing-form__side">

            <!-- Ціна -->
            <div class="form-card glass">
              <h2 class="form-card__title">Ціна</h2>
              <div class="form-field" :class="{ error: errors.price }">
                <label class="form-field__label">Ціна (₴) *</label>
                <div class="form-field__price-wrap">
                  <span class="form-field__price-symbol">₴</span>
                  <input
                    v-model.number="form.price"
                    type="number"
                    placeholder="0"
                    class="form-field__input form-field__input--price"
                    min="1"
                    @blur="validateField('price')"
                  />
                </div>
                <span class="form-field__error">{{ errors.price }}</span>
              </div>
            </div>

            <!-- Фото -->
            <div class="form-card glass">
              <h2 class="form-card__title">
                Фотографії
                <span class="form-card__title-hint">{{ uploadedImages.length }}/10</span>
              </h2>

              <!-- Зона drag-and-drop -->
              <div
                class="photo-drop"
                :class="{ 'photo-drop--over': isDragging, 'photo-drop--full': uploadedImages.length >= 10 }"
                @dragover.prevent="isDragging = true"
                @dragleave="isDragging = false"
                @drop.prevent="onDrop"
                @click="uploadedImages.length < 10 && $refs.fileInput.click()"
              >
                <input
                  ref="fileInput"
                  type="file"
                  multiple
                  accept="image/jpeg,image/png,image/webp"
                  style="display:none"
                  @change="onFileSelect"
                />
                <div class="photo-drop__content">
                  <div class="photo-drop__icon">📸</div>
                  <p class="photo-drop__text">
                    {{ uploadedImages.length >= 10 ? 'Максимум 10 фото' : 'Перетягни або натисни щоб обрати' }}
                  </p>
                  <p class="photo-drop__hint">JPEG, PNG, WebP · до 5 МБ кожне</p>
                </div>
              </div>

              <!-- Прев'ю фото -->
              <div v-if="previewImages.length" class="photo-grid">
                <div
                  v-for="(img, idx) in previewImages"
                  :key="idx"
                  class="photo-item"
                  :class="{ 'photo-item--main': idx === 0 }"
                >
                  <img :src="img.url" :alt="`Фото ${idx + 1}`" class="photo-item__img" />
                  <div class="photo-item__overlay">
                    <span v-if="idx === 0" class="photo-item__main-badge">Головне</span>
                    <button type="button" class="photo-item__remove" @click="removePhoto(idx)">✕</button>
                  </div>
                  <!-- Прогрес завантаження -->
                  <div v-if="img.uploading" class="photo-item__progress">
                    <div class="photo-item__progress-bar" :style="{ width: img.progress + '%' }" />
                  </div>
                  <div v-if="img.uploaded" class="photo-item__done">✓</div>
                </div>
              </div>

              <p v-if="photoError" class="form-field__error" style="margin-top:8px">{{ photoError }}</p>
            </div>

            <!-- Кнопка публікації -->
            <button
              type="submit"
              class="form-submit"
              :class="{ loading: submitting }"
              :disabled="submitting"
            >
              <span v-if="!submitting">
                {{ isEdit ? '💾 Зберегти зміни' : '🚀 Опублікувати оголошення' }}
              </span>
              <span v-else class="form-submit__spinner" />
            </button>

            <p v-if="submitError" class="form-submit-error">{{ submitError }}</p>
          </div>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { listingsApi } from '@/api'
import { useFormatters } from '@/composables/useFormatters'
import { useToast } from 'vue-toastification'

const router = useRouter()
const route  = useRoute()
const toast  = useToast()
const { CATEGORY_LABELS, CONDITION_LABELS, conditionColor } = useFormatters()

const isEdit = computed(() => !!route.params.id)

const CATEGORY_ICONS = {
  guitars: '🎸', bass: '🎸', keyboards: '🎹', drums: '🥁',
  wind: '🎺', strings: '🎻', dj: '🎧', studio: '🎙️',
  accessories: '🎵', other: '📦',
}

// ── Форма ─────────────────────────────────────────
const form = reactive({
  title: '', description: '', price: '',
  category: '', condition: '', brand: '', city: '',
})

const errors = reactive({
  title: '', description: '', price: '', category: '', condition: '',
})

// ── Фото ──────────────────────────────────────────
const fileInput     = ref(null)
const previewImages = ref([])   // { url, file, uploading, progress, uploaded, serverUrl }
const uploadedImages = computed(() => previewImages.value.filter(i => i.uploaded))
const isDragging    = ref(false)
const photoError    = ref('')
const createdListingId = ref(null)

// ── Submit ─────────────────────────────────────────
const submitting  = ref(false)
const submitError = ref('')

// ── Валідація ──────────────────────────────────────
function validateField(field) {
  if (field === 'title') {
    errors.title = form.title.trim().length < 5 ? 'Мінімум 5 символів' : ''
  }
  if (field === 'description') {
    errors.description = form.description.trim().length < 20 ? 'Мінімум 20 символів' : ''
  }
  if (field === 'price') {
    errors.price = (!form.price || form.price <= 0) ? 'Вкажи ціну' : ''
  }
}

function validate() {
  validateField('title')
  validateField('description')
  validateField('price')
  errors.category  = !form.category  ? 'Оберіть категорію' : ''
  errors.condition = !form.condition ? 'Оберіть стан' : ''
  return !Object.values(errors).some(e => e)
}

// ── Фото: вибір файлів ─────────────────────────────
function onFileSelect(e) {
  handleFiles(Array.from(e.target.files))
  e.target.value = ''
}

function onDrop(e) {
  isDragging.value = false
  handleFiles(Array.from(e.dataTransfer.files))
}

function handleFiles(files) {
  photoError.value = ''
  const allowed = ['image/jpeg', 'image/png', 'image/webp']
  const maxSize = 5 * 1024 * 1024

  for (const file of files) {
    if (previewImages.value.length >= 10) {
      photoError.value = 'Максимум 10 фото'
      break
    }
    if (!allowed.includes(file.type)) {
      photoError.value = 'Тільки JPEG, PNG, WebP'
      continue
    }
    if (file.size > maxSize) {
      photoError.value = `Файл "${file.name}" більше 5 МБ`
      continue
    }

    const url = URL.createObjectURL(file)
    previewImages.value.push({ url, file, uploading: false, progress: 0, uploaded: false, serverUrl: null })
  }
}

function removePhoto(idx) {
  URL.revokeObjectURL(previewImages.value[idx].url)
  previewImages.value.splice(idx, 1)
}

// ── Завантаження фото після створення ─────────────
async function uploadPhotos(listingId) {
  const toUpload = previewImages.value.filter(i => !i.uploaded && i.file)
  if (!toUpload.length) return

  for (const img of toUpload) {
    img.uploading = true
    img.progress  = 30
    try {
      const { data } = await listingsApi.uploadImages(listingId, [img.file])
      img.progress  = 100
      img.uploaded  = true
      img.uploading = false
      img.serverUrl = data.images[0]
    } catch {
      img.uploading = false
      photoError.value = 'Помилка завантаження деяких фото'
    }
  }
}

// ── Submit форми ───────────────────────────────────
async function onSubmit() {
  if (!validate()) {
    window.scrollTo({ top: 0, behavior: 'smooth' })
    return
  }

  submitting.value  = true
  submitError.value = ''

  try {
    const payload = {
      title:       form.title.trim(),
      description: form.description.trim(),
      price:       Number(form.price),
      category:    form.category,
      condition:   form.condition,
      brand:       form.brand.trim() || undefined,
      city:        form.city.trim()  || undefined,
      attributes:  {},
    }

    let listingId

    if (isEdit.value) {
      await listingsApi.update(route.params.id, payload)
      listingId = route.params.id
      toast.success('Оголошення оновлено!')
    } else {
      const { data } = await listingsApi.create(payload)
      listingId = data.id
      createdListingId.value = listingId
      toast.success('Оголошення створено!')
    }

    // Завантажуємо фото
    if (previewImages.value.length) {
      await uploadPhotos(listingId)
    }

    router.push(`/listings/${listingId}`)
  } catch (err) {
    submitError.value = err.response?.data?.detail ?? 'Помилка збереження'
  } finally {
    submitting.value = false
  }
}

// ── Завантаження для редагування ───────────────────
onMounted(async () => {
  if (isEdit.value) {
    try {
      const { data } = await listingsApi.getOne(route.params.id)
      form.title       = data.title
      form.description = data.description
      form.price       = data.price
      form.category    = data.category
      form.condition   = data.condition
      form.brand       = data.brand ?? ''
      form.city        = data.city  ?? ''
      // Існуючі фото
      if (data.images?.length) {
        previewImages.value = data.images.map(url => ({
          url, file: null, uploading: false, progress: 0, uploaded: true, serverUrl: url,
        }))
      }
    } catch {
      toast.error('Не вдалось завантажити оголошення')
      router.push('/')
    }
  }
})
</script>

<style scoped>
/* ── Сторінка ──────────────────────────────────── */
.form-page {
  min-height: 100vh;
  padding: 40px 0 80px;
  position: relative;
}
.form-page__orb {
  position: fixed; border-radius: 50%; filter: blur(100px);
  pointer-events: none; z-index: 0;
}
.form-page__orb--1 {
  width: 500px; height: 500px;
  background: radial-gradient(circle, rgba(245,166,35,0.08) 0%, transparent 70%);
  top: -100px; right: -100px;
}
.form-page__orb--2 {
  width: 400px; height: 400px;
  background: radial-gradient(circle, rgba(79,142,247,0.08) 0%, transparent 70%);
  bottom: 0; left: -100px;
}
.form-page__inner { position: relative; z-index: 1; }

.form-page__header { margin-bottom: 32px; }
.form-page__back {
  display: inline-flex; align-items: center; gap: 6px;
  color: var(--text-muted); font-size: 0.875rem;
  margin-bottom: 16px;
  transition: color var(--transition);
}
.form-page__back:hover { color: var(--accent); }
.form-page__title { font-size: 2rem; font-weight: 800; letter-spacing: -0.03em; }
.form-page__sub   { color: var(--text-secondary); margin-top: 4px; }

/* ── Layout ────────────────────────────────────── */
.listing-form__layout {
  display: grid;
  grid-template-columns: 1fr 360px;
  gap: 24px;
  align-items: start;
}
@media (max-width: 900px) {
  .listing-form__layout { grid-template-columns: 1fr; }
}
.listing-form__main { display: flex; flex-direction: column; gap: 20px; }
.listing-form__side { display: flex; flex-direction: column; gap: 20px; position: sticky; top: 88px; }

/* ── Form Card ─────────────────────────────────── */
.form-card {
  border-radius: var(--radius-lg);
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}
.form-card__title {
  font-size: 0.95rem; font-weight: 700;
  display: flex; align-items: center; justify-content: space-between;
}
.form-card__title-hint {
  font-size: 0.78rem; font-weight: 400;
  color: var(--text-muted);
}

/* ── Form Fields ───────────────────────────────── */
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}
@media (max-width: 600px) { .form-row { grid-template-columns: 1fr; } }

.form-field {
  display: flex; flex-direction: column; gap: 8px;
}
.form-field__label {
  font-size: 0.78rem; font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase; letter-spacing: 0.05em;
}
.form-field__input,
.form-field__textarea {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: var(--radius-md);
  color: var(--text-primary);
  padding: 12px 14px;
  font-size: 0.9rem;
  outline: none;
  transition: all 0.25s ease;
  width: 100%;
}
.form-field__input:focus,
.form-field__textarea:focus {
  border-color: rgba(245,166,35,0.5);
  background: rgba(255,255,255,0.07);
  box-shadow: 0 0 0 3px rgba(245,166,35,0.08), 0 0 16px rgba(245,166,35,0.06);
}
.form-field__input::placeholder,
.form-field__textarea::placeholder { color: var(--text-muted); }
.form-field__textarea { resize: vertical; min-height: 140px; }
.form-field.error .form-field__input,
.form-field.error .form-field__textarea {
  border-color: rgba(248,113,113,0.5);
}
.form-field__meta {
  display: flex; justify-content: space-between; align-items: center;
}
.form-field__error { font-size: 0.76rem; color: var(--error); }
.form-field__count { font-size: 0.72rem; color: var(--text-muted); }

/* Ціна */
.form-field__price-wrap {
  display: flex; align-items: center;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  border-radius: var(--radius-md);
  overflow: hidden;
  transition: all 0.25s ease;
}
.form-field__price-wrap:focus-within {
  border-color: rgba(245,166,35,0.5);
  box-shadow: 0 0 0 3px rgba(245,166,35,0.08);
}
.form-field__price-symbol {
  padding: 0 14px;
  font-size: 1.1rem; font-weight: 700;
  color: var(--accent);
  border-right: 1px solid rgba(255,255,255,0.09);
}
.form-field__input--price {
  border: none; background: none;
  padding: 13px 14px;
  font-size: 1.1rem; font-weight: 700;
}
.form-field__input--price:focus { box-shadow: none; }
input[type=number]::-webkit-outer-spin-button,
input[type=number]::-webkit-inner-spin-button { -webkit-appearance: none; }

/* ── Chips ─────────────────────────────────────── */
.form-field__chips { display: flex; flex-wrap: wrap; gap: 8px; }
.form-chip {
  padding: 7px 13px;
  border-radius: var(--radius-xl);
  font-size: 0.825rem;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.09);
  color: var(--text-secondary);
  transition: all var(--transition);
  cursor: pointer;
}
.form-chip:hover { border-color: rgba(245,166,35,0.4); color: var(--text-primary); }
.form-chip.active {
  background: var(--accent-dim);
  border-color: rgba(245,166,35,0.5);
  color: var(--accent);
  font-weight: 600;
  box-shadow: 0 0 12px rgba(245,166,35,0.1);
}

/* ── Photo Drop Zone ───────────────────────────── */
.photo-drop {
  border: 2px dashed rgba(255,255,255,0.12);
  border-radius: var(--radius-lg);
  padding: 32px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.25s ease;
  background: rgba(255,255,255,0.02);
}
.photo-drop:hover:not(.photo-drop--full) {
  border-color: rgba(245,166,35,0.4);
  background: rgba(245,166,35,0.03);
}
.photo-drop--over {
  border-color: var(--accent);
  background: rgba(245,166,35,0.06);
  box-shadow: 0 0 24px rgba(245,166,35,0.1);
}
.photo-drop--full { cursor: default; opacity: 0.5; }
.photo-drop__icon { font-size: 2.2rem; margin-bottom: 10px; }
.photo-drop__text { font-size: 0.875rem; color: var(--text-secondary); font-weight: 500; }
.photo-drop__hint { font-size: 0.75rem; color: var(--text-muted); margin-top: 4px; }

/* ── Photo Grid ────────────────────────────────── */
.photo-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
  margin-top: 12px;
}
.photo-item {
  position: relative;
  aspect-ratio: 1;
  border-radius: var(--radius-md);
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.09);
}
.photo-item--main {
  grid-column: span 2;
  grid-row: span 2;
  border-color: rgba(245,166,35,0.4);
  box-shadow: 0 0 16px rgba(245,166,35,0.1);
}
.photo-item__img {
  width: 100%; height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}
.photo-item:hover .photo-item__img { transform: scale(1.05); }
.photo-item__overlay {
  position: absolute; inset: 0;
  background: rgba(0,0,0,0);
  display: flex; align-items: flex-start; justify-content: space-between;
  padding: 6px;
  transition: background 0.2s ease;
}
.photo-item:hover .photo-item__overlay { background: rgba(0,0,0,0.3); }
.photo-item__main-badge {
  background: var(--accent); color: #000;
  font-size: 0.65rem; font-weight: 700;
  padding: 2px 7px; border-radius: 99px;
}
.photo-item__remove {
  width: 22px; height: 22px;
  background: rgba(0,0,0,0.7);
  color: #fff; border-radius: 50%;
  font-size: 0.7rem;
  display: flex; align-items: center; justify-content: center;
  opacity: 0; transition: opacity var(--transition);
  margin-left: auto;
}
.photo-item:hover .photo-item__remove { opacity: 1; }
.photo-item__progress {
  position: absolute; bottom: 0; left: 0; right: 0;
  height: 3px; background: rgba(0,0,0,0.3);
}
.photo-item__progress-bar {
  height: 100%; background: var(--accent);
  transition: width 0.3s ease;
}
.photo-item__done {
  position: absolute; bottom: 4px; right: 4px;
  background: var(--success); color: #000;
  width: 18px; height: 18px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 700;
}

/* ── Submit ────────────────────────────────────── */
.form-submit {
  width: 100%; height: 54px;
  background: linear-gradient(135deg, var(--accent) 0%, #ff9f0a 100%);
  color: #000; font-weight: 800; font-size: 1rem;
  border-radius: var(--radius-lg);
  transition: all var(--transition-slow);
  box-shadow: 0 4px 24px rgba(245,166,35,0.3);
  display: flex; align-items: center; justify-content: center;
  letter-spacing: 0.01em;
}
.form-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 36px rgba(245,166,35,0.45);
}
.form-submit:disabled { opacity: 0.7; cursor: not-allowed; }
.form-submit__spinner {
  display: block; width: 22px; height: 22px;
  border: 2px solid rgba(0,0,0,0.2); border-top-color: #000;
  border-radius: 50%; animation: spin 0.7s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.form-submit-error {
  text-align: center; font-size: 0.825rem;
  color: var(--error); margin-top: 8px;
}
</style>
