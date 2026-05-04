# 🎸 MusicStore — Backend (FastAPI + MongoDB)

REST API для маркетплейсу музичних інструментів.

---

## 📁 Структура проекту

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py       # Налаштування (.env)
│   │   ├── database.py     # Підключення до MongoDB
│   │   └── security.py     # JWT, хешування паролів, dependencies
│   ├── routers/
│   │   ├── auth.py         # /api/auth — реєстрація, вхід, профіль
│   │   ├── listings.py     # /api/listings — оголошення, пошук, фото
│   │   ├── favorites.py    # /api/favorites — обране
│   │   ├── messages.py     # /api/messages — чат (REST + WebSocket)
│   │   └── admin.py        # /api/admin — адмін-панель
│   ├── schemas/
│   │   ├── user.py         # Pydantic-схеми для юзера
│   │   ├── listing.py      # Pydantic-схеми для оголошень
│   │   └── message.py      # Pydantic-схеми для чату і обраного
│   └── main.py             # Точка входу FastAPI
├── uploads/                # Зображення (створюється автоматично)
├── create_admin.py         # Скрипт створення першого адміна
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## ⚙️ Встановлення та запуск

### 1. Клонуй репозиторій і перейди в папку backend

```bash
cd backend
```

### 2. Створи та активуй віртуальне середовище

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Встанови залежності

```bash
pip install -r requirements.txt
```

### 4. Налаштуй змінні середовища

```bash
# Скопіюй приклад і заповни своїми даними
cp .env.example .env
```

Відкрий `.env` і вкажи:

```env
MONGODB_URL=mongodb://localhost:27017   # або MongoDB Atlas URL
DATABASE_NAME=music_store
SECRET_KEY=your-very-long-secret-key-here-minimum-32-chars
```

### 5. Запусти MongoDB локально

Якщо MongoDB встановлена локально:
```bash
mongod
```

Або використай **MongoDB Atlas** (безкоштовно):
1. Зареєструйся на [mongodb.com/atlas](https://www.mongodb.com/atlas)
2. Створи кластер M0 (безкоштовний)
3. Скопіюй Connection String і вставте в `.env`:
   ```
   MONGODB_URL=mongodb+srv://user:password@cluster.mongodb.net/
   ```

### 6. Запусти сервер

```bash
uvicorn app.main:app --reload --port 8000
```

Сервер буде доступний на: **http://localhost:8000**

### 7. Створи першого адміністратора

```bash
python create_admin.py
```

---

## 📖 API Документація

Після запуску сервера:

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

---

## 🔌 Всі ендпоінти

### Auth — `/api/auth`
| Метод | URL | Опис | Авторизація |
|-------|-----|------|-------------|
| POST | `/register` | Реєстрація | — |
| POST | `/login` | Вхід | — |
| POST | `/refresh` | Оновлення токена | — |
| GET | `/me` | Мій профіль | ✅ |
| PUT | `/me` | Оновити профіль | ✅ |
| DELETE | `/me` | Видалити акаунт | ✅ |

### Listings — `/api/listings`
| Метод | URL | Опис | Авторизація |
|-------|-----|------|-------------|
| GET | `/` | Каталог з пошуком і фільтрами | — |
| GET | `/my` | Мої оголошення | ✅ |
| GET | `/{id}` | Детальна сторінка | — |
| POST | `/` | Створити оголошення | ✅ |
| PUT | `/{id}` | Оновити оголошення | ✅ (власник) |
| DELETE | `/{id}` | Видалити оголошення | ✅ (власник) |
| POST | `/{id}/images` | Завантажити фото | ✅ (власник) |
| DELETE | `/{id}/images/{name}` | Видалити фото | ✅ (власник) |

### Favorites — `/api/favorites`
| Метод | URL | Опис | Авторизація |
|-------|-----|------|-------------|
| POST | `/{listing_id}` | Додати/видалити з обраного | ✅ |
| GET | `/` | Моє обране | ✅ |

### Messages — `/api/messages`
| Метод | URL | Опис | Авторизація |
|-------|-----|------|-------------|
| GET | `/conversations` | Список розмов | ✅ |
| GET | `/conversation/{id}` | Повідомлення розмови | ✅ |
| POST | `/` | Надіслати повідомлення | ✅ |
| WS | `/ws?token=<jwt>` | WebSocket чат | ✅ |

### Admin — `/api/admin`
| Метод | URL | Опис | Авторизація |
|-------|-----|------|-------------|
| GET | `/stats` | Статистика | 👑 Admin |
| GET | `/users` | Список юзерів | 👑 Admin |
| PATCH | `/users/{id}/ban` | Бан/розбан | 👑 Admin |
| PATCH | `/users/{id}/role` | Змінити роль | 👑 Admin |
| GET | `/listings` | Всі оголошення | 👑 Admin |
| PATCH | `/listings/{id}/status` | Змінити статус | 👑 Admin |
| DELETE | `/listings/{id}` | Видалити | 👑 Admin |

---

## 🔐 Авторизація в запитах

Додавай заголовок до кожного захищеного запиту:
```
Authorization: Bearer <access_token>
```

---

## 🔍 Параметри пошуку (GET /api/listings)

```
?q=gibson          # текстовий пошук
&category=guitars  # guitars | bass | keyboards | drums | wind | strings | dj | studio | accessories | other
&condition=good    # new | like_new | good | fair | for_parts
&brand=Fender
&city=Київ
&price_min=1000
&price_max=50000
&sort=newest       # newest | price_asc | price_desc | views
&page=1
&limit=20
```

---

## 🌐 Деплой на Render.com

1. Запушити код на GitHub
2. Зайти на [render.com](https://render.com) → New → Web Service
3. Підключити репозиторій
4. Налаштування:
   - **Runtime**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. В Environment Variables додати всі змінні з `.env`
6. MongoDB — використовувати Atlas (зовнішній хмарний кластер)

---

## 📦 Технологічний стек

| Компонент | Технологія |
|-----------|------------|
| Фреймворк | FastAPI 0.111 |
| БД | MongoDB (Motor async driver) |
| Авторизація | JWT (python-jose) |
| Паролі | bcrypt (passlib) |
| Валідація | Pydantic v2 |
| Реалтайм | WebSocket (вбудований у FastAPI) |
| Зображення | Pillow (оптимізація) |
| Сервер | Uvicorn (ASGI) |
