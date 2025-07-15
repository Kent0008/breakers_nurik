# DRILL CLOUD - Облачная система мониторинга

## Описание

**DRILL CLOUD** — это облачная часть системы мониторинга буровой установки, состоящая из Django Backend API и React Frontend.

## Архитектура

### Backend (Django + DRF)

#### Технологии
- **Django 4.2.7** — веб-фреймворк
- **Django REST Framework** — API
- **PostgreSQL** — база данных
- **Paho MQTT** — MQTT клиент
- **Channels** — WebSocket поддержка
- **Redis** — брокер сообщений для WebSocket

#### Структура API

##### Данные сенсоров
- `GET /api/data/` — получение данных сенсоров
- `GET /api/data/?tag=<tag>&range=<range>` — фильтрация по тегу и времени
- `GET /api/data/tags/` — список всех тегов

Параметры:
- `tag` — идентификатор параметра (например, `pressure_1`)
- `range` — временной диапазон (`1h`, `24h`, `7d`)

##### Уставки
- `GET /api/thresholds/` — получение списка уставок
- `POST /api/thresholds/` — создание/обновление уставки
- `PUT /api/thresholds/{id}/` — обновление уставки
- `DELETE /api/thresholds/{id}/` — удаление уставки

Пример POST запроса:
```json
{
  "tag": "pressure_1",
  "min_value": 10.0,
  "max_value": 25.0
}
```

##### Инциденты
- `GET /api/incidents/` — получение списка инцидентов
- `GET /api/incidents/?tag=<tag>&range=<range>` — фильтрация

#### WebSocket API

Подключение: `ws://localhost:8000/ws/monitoring/`

Сообщения:
```json
// Подписка на сенсор
{
  "type": "subscribe_sensor",
  "tag": "pressure_1"
}

// Получение последних данных
{
  "type": "get_latest_data",
  "tag": "pressure_1"
}

// Получение уставок
{
  "type": "get_thresholds"
}
```

### Frontend (React + Vite)

#### Технологии
- **React 18** — UI библиотека
- **Vite** — сборщик
- **Material-UI** — компоненты интерфейса
- **Recharts** — графики
- **Axios** — HTTP клиент

#### Компоненты

##### Dashboard
- Отображение графиков параметров (до 3 на странице)
- Realtime обновления через WebSocket
- Отображение линий уставок
- Отображение инцидентов
- Выбор параметров для мониторинга

##### Thresholds
- Управление уставками параметров
- Создание, редактирование, удаление
- Валидация данных

## Запуск

### Предварительные требования
- Docker
- Docker Compose

### Запуск через Docker Compose

```bash
# Из корневой директории проекта
cd drill-infra
docker-compose up -d
```

### Ручной запуск

#### Backend
```bash
cd drill-cloud/backend

# Установка зависимостей
pip install -r requirements.txt

# Миграции
python manage.py makemigrations
python manage.py migrate

# Запуск сервера
python manage.py runserver 0.0.0.0:8000

# В отдельном терминале - MQTT клиент
python manage.py start_mqtt
```

#### Frontend
```bash
cd drill-cloud/frontend

# Установка зависимостей
npm install

# Запуск в режиме разработки
npm run dev
```

## Конфигурация

### Переменные окружения Backend

```bash
# База данных
POSTGRES_DB=drill_monitoring
POSTGRES_USER=drill_user
POSTGRES_PASSWORD=drill_password
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

# MQTT
MQTT_BROKER=mosquitto
MQTT_PORT=1883
MQTT_CLIENT_ID=drill-backend

# Django
DEBUG=True
SECRET_KEY=your-secret-key
```

### Конфигурация Frontend

В `vite.config.js` настроен прокси для API:
- `/api` → `http://backend:8000`
- `/ws` → `ws://backend:8000`

## Тестирование

### Отправка тестовых данных MQTT

```bash
# Установка mosquitto-clients
sudo apt-get install mosquitto-clients

# Отправка данных
mosquitto_pub -h localhost -t "telemetry/pressure_1" -m '{"value": 15.5, "timestamp": "2025-07-09T16:45:00Z"}'
mosquitto_pub -h localhost -t "telemetry/temperature_1" -m '{"value": 75.2, "timestamp": "2025-07-09T16:45:00Z"}'
```

### Тестирование API

```bash
# Получение уставок
curl http://localhost:8000/api/thresholds/

# Создание уставки
curl -X POST http://localhost:8000/api/thresholds/ \
  -H "Content-Type: application/json" \
  -d '{"tag": "test_sensor", "min_value": 10.0, "max_value": 20.0}'

# Получение данных
curl http://localhost:8000/api/data/?tag=pressure_1&range=1h
```

## Структура проекта

```
drill-cloud/
├── backend/
│   ├── drill_monitoring/     # Django проект
│   ├── monitoring/           # Django приложение
│   │   ├── models.py         # Модели данных
│   │   ├── views.py          # API представления
│   │   ├── serializers.py    # DRF сериализаторы
│   │   ├── mqtt_client.py    # MQTT клиент
│   │   ├── consumers.py      # WebSocket потребители
│   │   └── signals.py        # Django сигналы
│   ├── requirements.txt      # Python зависимости
│   └── Dockerfile           # Docker образ
└── frontend/
    ├── src/
    │   ├── components/       # React компоненты
    │   ├── hooks/           # React хуки
    │   ├── App.jsx          # Главный компонент
    │   └── main.jsx         # Точка входа
    ├── package.json         # Node.js зависимости
    ├── vite.config.js       # Конфигурация Vite
    └── Dockerfile          # Docker образ
```

## Мониторинг и логи

### Логи Backend
```bash
docker-compose logs backend
```

### Логи Frontend
```bash
docker-compose logs frontend
```

### Проверка состояния
```bash
docker-compose ps
```

## Устранение неполадок

### Проблемы с подключением к MQTT
1. Проверить, что Mosquitto запущен
2. Проверить логи: `docker-compose logs mosquitto`
3. Проверить подключение: `telnet localhost 1883`

### Проблемы с WebSocket
1. Проверить, что Redis запущен
2. Проверить логи Backend
3. Проверить консоль браузера на ошибки

### Проблемы с базой данных
1. Проверить подключение: `docker-compose exec postgres psql -U drill_user -d drill_monitoring`
2. Проверить миграции: `docker-compose exec backend python manage.py migrate` 