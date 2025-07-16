# Настройка переменных окружения

## Фронтенд (React + Vite)

### 1. Создайте файл `.env.local` в папке `frontend/`:

```bash
# Frontend Environment Variables
VITE_API_BASE_URL=http://localhost:8000
VITE_WS_BASE_URL=ws://localhost:8000
VITE_FRONTEND_PORT=3000
```

### 2. Для Docker окружения используйте:

```bash
# Frontend Environment Variables (Docker)
VITE_API_BASE_URL=http://backend:8000
VITE_WS_BASE_URL=ws://backend:8000
VITE_FRONTEND_PORT=3000
```

**Примечание:** В Docker окружении фронтенд обращается к бэкенду напрямую через Docker сеть, поэтому прокси не используется.

## Бэкенд (Django)

### 1. Создайте файл `.env` в папке `backend/`:

```bash
# Django Backend Environment Variables
DEBUG=True
SECRET_KEY=django-insecure-drill-monitoring-key

# Database
POSTGRES_DB=drill_monitoring
POSTGRES_USER=drill_user
POSTGRES_PASSWORD=drill_password
POSTGRES_HOST=localhost
POSTGRES_PORT=5432

# MQTT Configuration
MQTT_BROKER=localhost
MQTT_PORT=1883
MQTT_CLIENT_ID=drill-backend

# Server Configuration
DJANGO_PORT=8000
DJANGO_HOST=0.0.0.0
```

### 2. Для Docker окружения используйте:

```bash
# Django Backend Environment Variables (Docker)
DEBUG=True
SECRET_KEY=django-insecure-drill-monitoring-key

# Database
POSTGRES_DB=drill_monitoring
POSTGRES_USER=drill_user
POSTGRES_PASSWORD=drill_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# MQTT Configuration
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_CLIENT_ID=drill-backend

# Server Configuration
DJANGO_PORT=8000
DJANGO_HOST=0.0.0.0
```

## Запуск

### Локальная разработка:

1. **Бэкенд:**
```bash
cd drill-cloud/backend
python run_server.py
```

2. **Фронтенд:**
```bash
cd drill-cloud/frontend
npm run dev
```

### Docker:

```bash
docker-compose up
```

## Переменные окружения

### Фронтенд (VITE_*):
- `VITE_API_BASE_URL` - URL API бэкенда
- `VITE_WS_BASE_URL` - URL WebSocket бэкенда  
- `VITE_FRONTEND_PORT` - Порт фронтенда

### Бэкенд:
- `DJANGO_PORT` - Порт Django сервера
- `DJANGO_HOST` - Хост Django сервера
- `POSTGRES_HOST` - Хост базы данных
- `MQTT_BROKER` - Хост MQTT брокера 