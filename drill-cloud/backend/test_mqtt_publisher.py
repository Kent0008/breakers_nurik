#!/usr/bin/env python
import json
import time
import random
from datetime import datetime
import paho.mqtt.client as mqtt

# MQTT настройки
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_CLIENT_ID = "test-publisher"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Подключен к MQTT брокеру")
    else:
        print(f"Ошибка подключения: {rc}")

def publish_sensor_data(client, tag, value):
    """Отправляет данные сенсора в MQTT"""
    topic = f"telemetry/{tag}"
    payload = {
        "value": value,
        "timestamp": datetime.now().isoformat()
    }
    
    client.publish(topic, json.dumps(payload))
    print(f"Отправлено: {topic} = {payload}")

def main():
    # Создаем MQTT клиент
    client = mqtt.Client(client_id=MQTT_CLIENT_ID)
    client.on_connect = on_connect
    
    # Подключаемся к брокеру
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_start()
        
        # Ждем подключения
        time.sleep(2)
        
        # Теги сенсоров
        tags = ['DC_out_100ms_140_9', 'DC_out_100ms_140_10', 'DC_out_100ms_165', 'DC_out_100ms_148']
        
        # Базовые значения
        base_values = {
            'DC_out_100ms_140_9': 127.0,
            'DC_out_100ms_140_10': 0.6,
            'DC_out_100ms_165': 14.9,
            'DC_out_100ms_148': 35.7
        }
        
        print("Начинаем отправку тестовых данных...")
        print("Нажмите Ctrl+C для остановки")
        
        while True:
            for tag in tags:
                # Генерируем случайное значение вокруг базового
                base_value = base_values[tag]
                variation = random.uniform(-0.1, 0.1) * base_value
                value = round(base_value + variation, 3)
                
                # Отправляем данные
                publish_sensor_data(client, tag, value)
                
                # Небольшая пауза между отправками
                time.sleep(0.5)
            
            # Пауза между циклами
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nОстановка...")
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        client.loop_stop()
        client.disconnect()

if __name__ == "__main__":
    main() 