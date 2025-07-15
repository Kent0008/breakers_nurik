# DRILL INFRA - Инфраструктура системы мониторинга

## Описание

**DRILL INFRA** — это инфраструктурный слой системы мониторинга буровой установки, который обеспечивает работу всех компонентов системы.

## Архитектура

### Компоненты системы

#### 1. Mosquitto MQTT Broker
- **Порт**: 1883 (MQTT), 9001 (WebSocket)
- **Назначение**: Центральный MQTT брокер для обмена сообщениями
- **Конфигурация**: Без аутентификации, без TLS для MVP
- **Топики**:
  - `telemetry/<tag>` — данные телеметрии
  - `drill/+/sensor/+` — данные с drill-edge

#### 2. PostgreSQL Database
- **Порт**: 5432
- **База данных**: `drill_monitoring`
- **Пользователь**: `drill_user`
- **Пароль**: `drill_password`
- **Таблицы**:
  - `sensor_data` — данные сенсоров
  - `thresholds` — уставки параметров
  - `incidents` — инциденты нарушений

#### 3. Django Backend (drill-cloud/backend)
- **Порт**: 8000
- **Назначение**: API сервер, MQTT клиент
- **Функции**:
  - REST API для фронтенда
  - Подписка на MQTT топики
  - Сохранение данных в БД
  - Проверка уставок

#### 4. React Frontend (drill-cloud/frontend)
- **Порт**: 3000
- **Назначение**: Веб-интерфейс мониторинга
- **Функции**:
  - Графики параметров
  - Настройка уставок
  - Отображение инцидентов

## Схема связей

```
drill-edge (Node-RED)
    ↓ MQTT (1883)
Mosquitto Broker
    ↓ MQTT (1883)
Django Backend
    ↓ HTTP (8000)
React Frontend
    ↓ HTTP (3000)
    ↓ WebSocket
Browser

PostgreSQL ← Django Backend
```

## Запуск системы

### Предварительные требования
- Docker
- Docker Compose

### Команды запуска

```bash
# Переход в директорию инфраструктуры
cd drill-infra

# Запуск всех сервисов
docker-compose up -d

# Просмотр логов
docker-compose logs -f

# Остановка системы
docker-compose down
```

### Проверка работы

1. **Mosquitto**: `mosquitto_pub -h localhost -t "telemetry/test" -m '{"value": 15.5, "timestamp": "2025-07-09T16:45:00Z"}'`
2. **PostgreSQL**: `psql -h localhost -p 5432 -U drill_user -d drill_monitoring`
3. **Backend API**: `curl http://localhost:8000/api/thresholds/`
4. **Frontend**: Открыть http://localhost:3000

## Конфигурация

### Переменные окружения

- `DATABASE_URL` — строка подключения к PostgreSQL
- `MQTT_BROKER` — адрес MQTT брокера
- `MQTT_PORT` — порт MQTT брокера
- `DEBUG` — режим отладки Django

### Порты

- **1883** — MQTT (Mosquitto)
- **5432** — PostgreSQL
- **8000** — Django Backend
- **3000** — React Frontend

## Мониторинг

### Логи сервисов
```bash
# Логи Mosquitto
docker-compose logs mosquitto

# Логи PostgreSQL
docker-compose logs postgres

# Логи Backend
docker-compose logs backend

# Логи Frontend
docker-compose logs frontend
```

### Состояние контейнеров
```bash
docker-compose ps
```

## Устранение неполадок

### Проблемы с подключением к MQTT
1. Проверить, что Mosquitto запущен: `docker-compose ps mosquitto`
2. Проверить логи: `docker-compose logs mosquitto`
3. Проверить доступность порта: `telnet localhost 1883`

### Проблемы с базой данных
1. Проверить подключение: `docker-compose exec postgres psql -U drill_user -d drill_monitoring`
2. Проверить инициализацию: `docker-compose logs postgres`

### Проблемы с Backend
1. Проверить логи: `docker-compose logs backend`
2. Проверить миграции: `docker-compose exec backend python manage.py migrate`
3. Проверить API: `curl http://localhost:8000/api/health/` 