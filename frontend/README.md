# 🎸 MusicStore — Frontend (Vue 3 + Vite)

## 📁 Структура проекту

```
frontend/
├── src/
│   ├── api/
│   │   ├── axios.js          # Axios інстанс + JWT interceptors + авто-refresh
│   │   └── index.js          # Всі API-модулі (auth, listings, favorites, messages, admin)
│   ├── stores/
│   │   ├── auth.js           # Pinia: авторизація, профіль, login/logout
│   │   ├── listings.js       # Pinia: каталог, фільтри, пагінація, обране
│   │   └── chat.js           # Pinia: WebSocket чат, розмови, повідомлення
│   ├── router/
│   │   └── index.js          # Vue Router: всі маршрути + navigation guards
│   ├── composables/
│   │   ├── useAsync.js       # Універсальний хук для async операцій
│   │   └── useFormatters.js  # Форматування ціни, дати, категорій
│   ├── components/
│   │   └── layout/
│   │       ├── AppLayout.vue # Обгортка: navbar + slot + footer
│   │       ├── AppNavbar.vue # Шапка: пошук, авторизація, меню профілю
│   │       └── AppFooter.vue # Підвал
│   ├── views/
│   │   ├── HomeView.vue           # Головна / каталог
│   │   ├── NotFoundView.vue       # 404
│   │   ├── auth/
│   │   │   ├── LoginView.vue      # Вхід
│   │   │   └── RegisterView.vue   # Реєстрація
│   │   ├── listings/
│   │   │   ├── ListingDetailView.vue # Сторінка оголошення
│   │   │   └── ListingFormView.vue   # Створення/редагування
│   │   ├── user/
│   │   │   ├── ProfileView.vue    # Профіль
│   │   │   ├── MyListingsView.vue # Мої оголошення
│   │   │   └── FavoritesView.vue  # Обране
│   │   ├── chat/
│   │   │   └── ChatView.vue       # Чат
│   │   └── admin/
│   │       ├── AdminLayout.vue    # Лейаут з сайдбаром
│   │       ├── AdminDashboard.vue # Статистика
│   │       ├── AdminUsers.vue     # Управління юзерами
│   │       └── AdminListings.vue  # Управління оголошеннями
│   ├── assets/styles/
│   │   └── main.css          # CSS-змінні, темна тема, глобальні стилі
│   ├── App.vue               # Кореневий компонент
│   └── main.js               # Точка входу
├── index.html
├── vite.config.js            # Proxy на FastAPI (/api → localhost:8000)
└── package.json
```

## ⚙️ Встановлення та запуск

```bash
cd frontend
npm install
npm run dev
```

Фронтенд буде на: **http://localhost:5173**

> Vite автоматично проксує `/api` і `/uploads` на `http://localhost:8000`,
> тому CORS не потрібен під час розробки.

## 🔑 Як працює авторизація

1. Після логіну `access_token` і `refresh_token` зберігаються в `localStorage`
2. Axios-interceptor чіпляє `Authorization: Bearer <token>` до кожного запиту автоматично
3. При отриманні 401 — axios автоматично робить `/auth/refresh` і повторює запит
4. Якщо refresh теж прострочений — редірект на `/login`

## 💬 WebSocket чат

Підключення відбувається в `App.vue` після логіну:
```
ws://localhost:5173/api/messages/ws?token=<access_token>
```
`chat store` слухає нові повідомлення і оновлює UI в реальному часі.

## 🎨 Темна тема

Всі кольори — через CSS-змінні в `main.css`:
- `--bg-base`, `--bg-surface`, `--bg-elevated` — рівні фону
- `--accent` — золотисто-жовтий (#f59e0b)
- `--text-primary`, `--text-secondary`, `--text-muted` — текст
- `--border` — межі елементів

## 🚀 Збірка для продакшену

```bash
npm run build
```
Результат у папці `dist/` — статичні файли для деплою на Render (Static Site).
