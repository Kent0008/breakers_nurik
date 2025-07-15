# DRILL Monitoring - Система мониторинга буровой установки

## 📋 Описание проекта

**DRILL Monitoring** — это MVP система мониторинга параметров буровой установки в реальном времени. Система состоит из трех основных компонентов:

- **drill-edge** — edge-устройство на буровой (Node-RED + PostgreSQL)
- **drill-infra** — инфраструктура (Mosquitto + PostgreSQL + Redis)
- **drill-cloud** — облачная часть (Django Backend + React Frontend)

## 🏗️ Архитектура системы

```
┌─────────────────┐    MQTT     ┌─────────────────┐
│   drill-edge    │ ──────────► │   Mosquitto     │
│   (Node-RED)    │             │   (MQTT Broker) │
│                │             │                │
│ ┌─────────────┐│             │                │
│ │ Equipment   ││             │                │
│ │ Sensors     ││             │                │
│ └─────────────┘│             │                │
└─────────────────┘             └─────────────────┘
                                         │
                                         ▼
┌─────────────────┐    MQTT     ┌─────────────────┐    HTTP     ┌─────────────────┐
│   React         │ ◄────────── │   Django        │ ◄────────── │   PostgreSQL    │
│   Frontend      │   WebSocket │   Backend       │             │   Database      │
│                │             │                │             │                │
│ ┌─────────────┐│             │ ┌─────────────┐ │             │ ┌─────────────┐ │
│ │ Dashboard   ││             │ │ MQTT Client │ │             │ │ Sensor Data │ │
│ │ Thresholds  ││             │ │ WebSocket   │ │             │ │ Thresholds  │ │
│ └─────────────┘│             │ │ API         │ │             │ │ Incidents   │ │
└─────────────────┘             └─────────────┘ │             └─────────────┘ │
                                         │      │                             │
                                         ▼      │                             │
                                ┌─────────────────┐                            │
                                │   Redis         │                            │
                                │   (WebSocket)   │                            │
                                └─────────────────┘                            │
                                                                               │
┌─────────────────┐    HTTP     ┌─────────────────┐                            │
│   Drill-edge    │ ◄────────── │   PostgreSQL    │ ◄─────────────────────────┘
│   PostgreSQL    │             │   (Local)       │
└─────────────────┘             └─────────────────┘
```

### Поток данных

1. **Оборудование** → **drill-edge (Node-RED)** → **MQTT топики**
2. **MQTT** → **Django Backend** → **PostgreSQL (Cloud)**
3. **PostgreSQL** → **Django API** → **React Frontend**
4. **WebSocket** → **Realtime обновления** → **Dashboard**

## 🚀 Быстрый старт

### Предварительные требования
- Docker
- Docker Compose
- Python 3.11+ (для тестирования)

### Запуск системы

1. **Клонирование репозитория**
```bash
git clone <repository-url>
cd Breakers
```

2. **Запуск инфраструктуры**
```bash
cd drill-infra
docker-compose up -d
```

3. **Проверка работы**
```bash
# Проверка контейнеров
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

4. **Тестирование системы**
```bash
# Установка зависимостей для тестирования
pip install requests paho-mqtt

# Запуск тестов
python test_system.py
```

5. **Доступ к интерфейсам**
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api/
- **Node-RED**: http://localhost:1880
- **PostgreSQL**: localhost:5432

## 📊 Функциональность

### ✅ Реализованные возможности

#### Backend (Django + DRF)
- ✅ Модели данных: SensorData, Threshold, Incident
- ✅ REST API для всех сущностей
- ✅ MQTT клиент для подписки на топики
- ✅ WebSocket поддержка для realtime обновлений
- ✅ Автоматическая проверка уставок
- ✅ Создание инцидентов при нарушениях

#### Frontend (React + Vite)
- ✅ Дашборд с графиками (до 3 на странице)
- ✅ Realtime обновления через WebSocket
- ✅ Отображение линий уставок на графиках
- ✅ Отображение инцидентов
- ✅ Управление уставками (CRUD)
- ✅ Современный Material-UI интерфейс

#### Инфраструктура
- ✅ Docker Compose для всех сервисов
- ✅ Mosquitto MQTT брокер
- ✅ PostgreSQL база данных
- ✅ Redis для WebSocket
- ✅ Автоматическая инициализация БД

### 🔧 API Endpoints

#### Данные сенсоров
```
GET /api/data/                    # Все данные
GET /api/data/?tag=pressure_1     # Фильтр по тегу
GET /api/data/?range=1h           # Фильтр по времени
GET /api/data/tags/               # Список тегов
```

#### Уставки
```
GET    /api/thresholds/           # Список уставок
POST   /api/thresholds/           # Создание уставки
PUT    /api/thresholds/{id}/      # Обновление уставки
DELETE /api/thresholds/{id}/      # Удаление уставки
```

#### Инциденты
```
GET /api/incidents/               # Список инцидентов
GET /api/incidents/?tag=pressure_1 # Фильтр по тегу
```

### 📡 MQTT Топики

Система поддерживает два формата топиков:

1. **Простой формат**: `telemetry/<tag>`
   ```json
   {
     "value": 15.5,
     "timestamp": "2025-07-09T16:45:00Z"
   }
   ```

2. **Совместимость с drill-edge**: `drill/<equipment>/sensor/<sensor_type>`
   ```json
   {
     "value": 15.5,
     "unit": "bar",
     "timestamp": "2025-07-09T16:45:00Z"
   }
   ```

## 🧪 Тестирование

### Отправка тестовых данных

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

## 📁 Структура проекта

```
Breakers/
├── drill-edge/           # Edge-устройство (Node-RED)
│   ├── docker-compose.yaml
│   ├── init/
│   │   ├── flows_mqtt.json
│   │   └── db.sql
│   └── README.md
├── drill-infra/          # Инфраструктура
│   ├── docker-compose.yaml
│   ├── init-db.sql
│   └── README.md
├── drill-cloud/          # Облачная часть
│   ├── backend/          # Django Backend
│   │   ├── drill_monitoring/
│   │   ├── monitoring/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   ├── frontend/         # React Frontend
│   │   ├── src/
│   │   ├── package.json
│   │   └── Dockerfile
│   └── README.md
├── test_system.py        # Скрипт тестирования
└── README.md
```

## 🔧 Конфигурация

### Порты
- **3000** — React Frontend
- **8000** — Django Backend
- **1883** — Mosquitto MQTT
- **5432** — PostgreSQL
- **6379** — Redis
- **1880** — Node-RED

### Переменные окружения
Основные переменные настроены в `drill-infra/docker-compose.yaml`:
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
- `MQTT_BROKER`, `MQTT_PORT`, `MQTT_CLIENT_ID`
- `DEBUG`, `SECRET_KEY`

## 📈 Мониторинг и логи

### Просмотр логов
```bash
# Все сервисы
docker-compose logs -f

# Конкретный сервис
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mosquitto
```

### Проверка состояния
```bash
docker-compose ps
```

## 🐛 Устранение неполадок

### Проблемы с подключением к MQTT
1. Проверить, что Mosquitto запущен: `docker-compose ps mosquitto`
2. Проверить логи: `docker-compose logs mosquitto`
3. Проверить доступность порта: `telnet localhost 1883`

### Проблемы с Backend
1. Проверить логи: `docker-compose logs backend`
2. Проверить миграции: `docker-compose exec backend python manage.py migrate`
3. Проверить API: `curl http://localhost:8000/api/thresholds/`

### Проблемы с Frontend
1. Проверить логи: `docker-compose logs frontend`
2. Проверить консоль браузера на ошибки
3. Проверить прокси в `vite.config.js`

### Проблемы с базой данных
1. Проверить подключение: `docker-compose exec postgres psql -U drill_user -d drill_monitoring`
2. Проверить инициализацию: `docker-compose logs postgres`

## 📚 Документация

- [drill-edge/README.md](drill-edge/README.md) — Документация edge-устройства
- [drill-infra/README.md](drill-infra/README.md) — Документация инфраструктуры
- [drill-cloud/README.md](drill-cloud/README.md) — Документация облачной части

## 🤝 Разработка

### Добавление новых параметров
1. Отправить данные в MQTT топик `telemetry/<new_tag>`
2. Создать уставку через API или интерфейс
3. Добавить параметр на дашборд

### Расширение функциональности
- Добавление новых типов уставок
- Реализация уведомлений (email, SMS)
- Интеграция с внешними системами
- Добавление аналитики и отчетов

## 📄 Лицензия

Проект разработан для внутреннего использования. 