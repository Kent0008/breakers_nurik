#!/usr/bin/env python3
"""
Скрипт для тестирования системы мониторинга DRILL
Отправляет тестовые данные в MQTT и проверяет API
"""

import json
import time
import requests
import paho.mqtt.publish as publish
from datetime import datetime, timezone

# Конфигурация
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
API_BASE = "http://localhost:8000/api"

def send_mqtt_data(topic, value):
    """Отправка данных в MQTT"""
    payload = {
        "value": value,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        publish.single(
            topic,
            json.dumps(payload),
            hostname=MQTT_BROKER,
            port=MQTT_PORT
        )
        print(f"✅ Отправлено в {topic}: {payload}")
        return True
    except Exception as e:
        print(f"❌ Ошибка отправки в {topic}: {e}")
        return False

def test_api_endpoint(endpoint, method="GET", data=None):
    """Тестирование API endpoint"""
    url = f"{API_BASE}{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data, headers={"Content-Type": "application/json"})
        else:
            print(f"❌ Неподдерживаемый метод: {method}")
            return False
            
        if response.status_code in [200, 201]:
            print(f"✅ {method} {endpoint}: {response.status_code}")
            if response.content:
                print(f"   Ответ: {response.json()}")
            return True
        else:
            print(f"❌ {method} {endpoint}: {response.status_code}")
            print(f"   Ошибка: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка запроса {method} {endpoint}: {e}")
        return False

def main():
    print("🚀 Тестирование системы мониторинга DRILL")
    print("=" * 50)
    
    # Тест 1: Проверка доступности API
    print("\n1. Проверка доступности API...")
    if not test_api_endpoint("/thresholds/"):
        print("❌ API недоступен. Убедитесь, что backend запущен.")
        return
    
    # Тест 2: Создание тестовых уставок
    print("\n2. Создание тестовых уставок...")
    thresholds = [
        {"tag": "pressure_1", "min_value": 10.0, "max_value": 25.0},
        {"tag": "temperature_1", "min_value": 20.0, "max_value": 80.0},
        {"tag": "flow_rate_1", "min_value": 5.0, "max_value": 15.0}
    ]
    
    for threshold in thresholds:
        test_api_endpoint("/thresholds/", "POST", threshold)
    
    # Тест 3: Отправка тестовых данных MQTT
    print("\n3. Отправка тестовых данных MQTT...")
    
    # Нормальные значения
    send_mqtt_data("telemetry/pressure_1", 15.5)
    send_mqtt_data("telemetry/temperature_1", 45.2)
    send_mqtt_data("telemetry/flow_rate_1", 8.7)
    
    time.sleep(2)
    
    # Значения, нарушающие уставки
    send_mqtt_data("telemetry/pressure_1", 30.0)  # Превышает максимум
    send_mqtt_data("telemetry/temperature_1", 15.0)  # Ниже минимума
    send_mqtt_data("telemetry/flow_rate_1", 20.0)  # Превышает максимум
    
    time.sleep(2)
    
    # Тест 4: Проверка данных через API
    print("\n4. Проверка данных через API...")
    test_api_endpoint("/data/tags/")
    test_api_endpoint("/data/?tag=pressure_1&range=1h")
    test_api_endpoint("/incidents/")
    
    # Тест 5: Проверка уставок
    print("\n5. Проверка уставок...")
    test_api_endpoint("/thresholds/")
    
    print("\n✅ Тестирование завершено!")
    print("\n📊 Для просмотра результатов откройте:")
    print("   - Frontend: http://localhost:3000")
    print("   - API: http://localhost:8000/api/")

if __name__ == "__main__":
    main() 