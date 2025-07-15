#!/usr/bin/env python3
"""
Скрипт для проверки интеграции между drill-edge и облачной системой
"""

import json
import time
import requests
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe
from datetime import datetime, timezone

# Конфигурация
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
API_BASE = "http://localhost:8000/api"

def check_mqtt_connection():
    """Проверка подключения к MQTT"""
    print("🔍 Проверка подключения к MQTT...")
    try:
        # Пробуем подключиться и подписаться на тестовый топик
        subscribe.simple("test/connection", hostname=MQTT_BROKER, port=MQTT_PORT, timeout=5)
        print("✅ MQTT подключение работает")
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения к MQTT: {e}")
        return False

def check_api_connection():
    """Проверка подключения к API"""
    print("🔍 Проверка подключения к API...")
    try:
        response = requests.get(f"{API_BASE}/thresholds/", timeout=5)
        if response.status_code == 200:
            print("✅ API подключение работает")
            return True
        else:
            print(f"❌ API недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к API: {e}")
        return False

def test_drill_edge_integration():
    """Тестирование интеграции drill-edge"""
    print("\n🔍 Тестирование интеграции drill-edge...")
    
    # Отправляем данные в формате drill-edge
    drill_data = {
        "value": 25.5,
        "unit": "bar",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Отправляем в drill-edge формат
        publish.single(
            "drill/equipment1/sensor/pressure",
            json.dumps(drill_data),
            hostname=MQTT_BROKER,
            port=MQTT_PORT
        )
        print("✅ Данные отправлены в drill-edge формат")
        
        # Ждем обработки
        time.sleep(2)
        
        # Проверяем, что данные появились в облачной системе
        response = requests.get(f"{API_BASE}/data/tags/")
        if response.status_code == 200:
            tags = response.json().get('tags', [])
            if 'equipment1_pressure' in tags:
                print("✅ Данные успешно обработаны drill-edge и переданы в облако")
                return True
            else:
                print("❌ Данные не появились в облачной системе")
                return False
        else:
            print(f"❌ Ошибка получения тегов: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования drill-edge: {e}")
        return False

def test_direct_telemetry():
    """Тестирование прямой отправки телеметрии"""
    print("\n🔍 Тестирование прямой отправки телеметрии...")
    
    telemetry_data = {
        "value": 35.2,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        # Отправляем напрямую в облачный формат
        publish.single(
            "telemetry/test_sensor",
            json.dumps(telemetry_data),
            hostname=MQTT_BROKER,
            port=MQTT_PORT
        )
        print("✅ Данные отправлены напрямую в облачный формат")
        
        # Ждем обработки
        time.sleep(2)
        
        # Проверяем данные
        response = requests.get(f"{API_BASE}/data/?tag=test_sensor&range=1h")
        if response.status_code == 200:
            data = response.json().get('results', [])
            if data:
                print(f"✅ Данные получены в облачной системе: {len(data)} записей")
                return True
            else:
                print("❌ Данные не найдены в облачной системе")
                return False
        else:
            print(f"❌ Ошибка получения данных: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Ошибка тестирования прямой телеметрии: {e}")
        return False

def check_node_red_status():
    """Проверка статуса Node-RED"""
    print("\n🔍 Проверка статуса Node-RED...")
    try:
        response = requests.get("http://localhost:1880", timeout=5)
        if response.status_code == 200:
            print("✅ Node-RED доступен")
            return True
        else:
            print(f"❌ Node-RED недоступен: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Ошибка подключения к Node-RED: {e}")
        return False

def main():
    print("🚀 Проверка интеграции системы DRILL Monitoring")
    print("=" * 60)
    
    # Проверки
    checks = [
        ("MQTT подключение", check_mqtt_connection),
        ("API подключение", check_api_connection),
        ("Node-RED статус", check_node_red_status),
        ("Drill-edge интеграция", test_drill_edge_integration),
        ("Прямая телеметрия", test_direct_telemetry),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ Ошибка в проверке {name}: {e}")
            results.append((name, False))
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("📊 ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ НЕ ПРОЙДЕН"
        print(f"{name:25} {status}")
        if result:
            passed += 1
    
    print(f"\nРезультат: {passed}/{total} проверок пройдено")
    
    if passed == total:
        print("🎉 Все проверки пройдены! Система работает корректно.")
        print("\n📊 Доступные интерфейсы:")
        print("   - Frontend: http://localhost:3000")
        print("   - Node-RED: http://localhost:1880")
        print("   - API: http://localhost:8000/api/")
    else:
        print("⚠️  Некоторые проверки не пройдены. Проверьте логи сервисов.")
        print("\n🔧 Рекомендации:")
        print("   - Убедитесь, что все контейнеры запущены: docker-compose ps")
        print("   - Проверьте логи: docker-compose logs")
        print("   - Перезапустите сервисы: docker-compose restart")

if __name__ == "__main__":
    main() 