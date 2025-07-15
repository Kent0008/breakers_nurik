-- Инициализация базы данных для системы мониторинга буровой установки

-- Создание таблицы для хранения данных сенсоров
CREATE TABLE IF NOT EXISTS sensor_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    tag VARCHAR(100) NOT NULL,
    value DECIMAL(10, 3) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы для хранения уставок
CREATE TABLE IF NOT EXISTS thresholds (
    id SERIAL PRIMARY KEY,
    tag VARCHAR(100) UNIQUE NOT NULL,
    min_value DECIMAL(10, 3),
    max_value DECIMAL(10, 3),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы для хранения инцидентов
CREATE TABLE IF NOT EXISTS incidents (
    id SERIAL PRIMARY KEY,
    tag VARCHAR(100) NOT NULL,
    value DECIMAL(10, 3) NOT NULL,
    threshold_min DECIMAL(10, 3),
    threshold_max DECIMAL(10, 3),
    violation_type VARCHAR(20) NOT NULL, -- 'min_violation' или 'max_violation'
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание индексов для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_sensor_data_timestamp ON sensor_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_sensor_data_tag ON sensor_data(tag);
CREATE INDEX IF NOT EXISTS idx_sensor_data_tag_timestamp ON sensor_data(tag, timestamp);
CREATE INDEX IF NOT EXISTS idx_incidents_timestamp ON incidents(timestamp);
CREATE INDEX IF NOT EXISTS idx_incidents_tag ON incidents(tag);

-- Вставка начальных уставок для тестирования
INSERT INTO thresholds (tag, min_value, max_value) VALUES
    ('pressure_1', 10.0, 25.0),
    ('temperature_1', 20.0, 80.0),
    ('flow_rate_1', 5.0, 15.0)
ON CONFLICT (tag) DO NOTHING; 