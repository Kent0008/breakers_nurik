import json
import logging
from datetime import datetime
from decimal import Decimal
from django.conf import settings
from django.utils import timezone
import paho.mqtt.client as mqtt
from .models import SensorData, Threshold, Incident

logger = logging.getLogger(__name__)


class MQTTClient:
    """MQTT клиент для подписки на топики телеметрии"""
    
    def __init__(self):
        self.client = mqtt.Client(client_id=settings.MQTT_CLIENT_ID)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
    def on_connect(self, client, userdata, flags, rc):
        """Обработчик подключения к MQTT брокеру"""
        if rc == 0:
            logger.info("Успешно подключен к MQTT брокеру")
            # Подписываемся на топики телеметрии
            client.subscribe("telemetry/#")
            client.subscribe("drill/+/sensor/+")
        else:
            logger.error(f"Ошибка подключения к MQTT брокеру: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """Обработчик отключения от MQTT брокера"""
        logger.warning(f"Отключен от MQTT брокера: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Обработчик входящих MQTT сообщений"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode('utf-8'))
            
            logger.info(f"Получено сообщение из топика {topic}: {payload}")
            
            # Извлекаем тег из топика
            tag = self.extract_tag_from_topic(topic)
            if not tag:
                logger.warning(f"Не удалось извлечь тег из топика: {topic}")
                return
            
            # Извлекаем значение и время
            value = payload.get('value')
            timestamp_str = payload.get('timestamp')
            
            if value is None:
                logger.warning(f"Отсутствует значение в payload: {payload}")
                return
            
            # Парсим время
            if timestamp_str:
                try:
                    timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    timestamp = timezone.make_aware(timestamp)
                except ValueError:
                    logger.warning(f"Неверный формат времени: {timestamp_str}")
                    timestamp = timezone.now()
            else:
                timestamp = timezone.now()
            
            # Сохраняем данные сенсора
            sensor_data = SensorData.objects.create(
                tag=tag,
                value=Decimal(str(value)),
                timestamp=timestamp
            )
            
            # Проверяем уставки
            self.check_thresholds(sensor_data)
            
        except json.JSONDecodeError:
            logger.error(f"Ошибка парсинга JSON: {msg.payload}")
        except Exception as e:
            logger.error(f"Ошибка обработки сообщения: {e}")
    
    def extract_tag_from_topic(self, topic):
        """Извлекает тег из MQTT топика"""
        parts = topic.split('/')
        
        # Формат: telemetry/<tag>
        if parts[0] == 'telemetry' and len(parts) == 2:
            return parts[1]
        
        # Формат: drill/<equipment>/sensor/<sensor_type>
        if parts[0] == 'drill' and len(parts) == 4 and parts[2] == 'sensor':
            return f"{parts[1]}_{parts[3]}"
        
        return None
    
    def check_thresholds(self, sensor_data):
        """Проверяет уставки для данных сенсора"""
        try:
            threshold = Threshold.objects.filter(tag=sensor_data.tag).first()
            if not threshold:
                return
            
            is_violated, violation_type = threshold.is_violated(sensor_data.value)
            
            if is_violated:
                # Создаем инцидент
                incident = Incident.objects.create(
                    tag=sensor_data.tag,
                    value=sensor_data.value,
                    threshold_min=threshold.min_value,
                    threshold_max=threshold.max_value,
                    violation_type=violation_type,
                    timestamp=sensor_data.timestamp
                )
                
                logger.warning(f"Создан инцидент: {incident}")
                
        except Exception as e:
            logger.error(f"Ошибка проверки уставок: {e}")
    
    def connect(self):
        """Подключение к MQTT брокеру"""
        try:
            self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
            self.client.loop_start()
        except Exception as e:
            logger.error(f"Ошибка подключения к MQTT брокеру: {e}")
    
    def disconnect(self):
        """Отключение от MQTT брокера"""
        self.client.loop_stop()
        self.client.disconnect()


# Глобальный экземпляр MQTT клиента
mqtt_client = None


def start_mqtt_client():
    """Запуск MQTT клиента"""
    global mqtt_client
    if mqtt_client is None:
        mqtt_client = MQTTClient()
        mqtt_client.connect()


def stop_mqtt_client():
    """Остановка MQTT клиента"""
    global mqtt_client
    if mqtt_client:
        mqtt_client.disconnect()
        mqtt_client = None 