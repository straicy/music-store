// Форматування ціни: 15000 → "15 000 ₴"
export function useFormatters() {
  function formatPrice(value) {
    if (!value && value !== 0) return '—'
    return new Intl.NumberFormat('uk-UA', {
      style: 'currency',
      currency: 'UAH',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value)
  }

  function formatDate(dateStr) {
    if (!dateStr) return '—'
    return new Intl.DateTimeFormat('uk-UA', {
      day: 'numeric',
      month: 'long',
      year: 'numeric',
    }).format(new Date(dateStr))
  }

  function formatDateShort(dateStr) {
    if (!dateStr) return '—'
    const date = new Date(dateStr)
    const now  = new Date()
    const diff = now - date
    const mins = Math.floor(diff / 60000)
    const hours = Math.floor(diff / 3600000)
    const days  = Math.floor(diff / 86400000)

    if (mins < 1)    return 'щойно'
    if (mins < 60)   return `${mins} хв тому`
    if (hours < 24)  return `${hours} год тому`
    if (days < 7)    return `${days} дн тому`
    return new Intl.DateTimeFormat('uk-UA', { day: 'numeric', month: 'short' }).format(date)
  }

  const CONDITION_LABELS = {
    new:       'Новий',
    like_new:  'Як новий',
    good:      'Хороший',
    fair:      'Задовільний',
    for_parts: 'На запчастини',
  }

  const CATEGORY_LABELS = {
    guitars:     'Гітари',
    bass:        'Бас-гітари',
    keyboards:   'Клавішні',
    drums:       'Ударні',
    wind:        'Духові',
    strings:     'Струнні',
    dj:          'DJ обладнання',
    studio:      'Студійне обладнання',
    accessories: 'Аксесуари',
    other:       'Інше',
  }

  const CONDITION_COLORS = {
    new:       'var(--success)',
    like_new:  '#4ade80',
    good:      'var(--accent)',
    fair:      'var(--warning)',
    for_parts: 'var(--error)',
  }

  function conditionLabel(key)  { return CONDITION_LABELS[key]  ?? key }
  function categoryLabel(key)   { return CATEGORY_LABELS[key]   ?? key }
  function conditionColor(key)  { return CONDITION_COLORS[key]  ?? 'var(--text-muted)' }

  return {
    formatPrice, formatDate, formatDateShort,
    conditionLabel, categoryLabel, conditionColor,
    CONDITION_LABELS, CATEGORY_LABELS,
  }
}
