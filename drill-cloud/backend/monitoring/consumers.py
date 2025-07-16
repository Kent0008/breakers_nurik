import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SensorData, Threshold, Incident


class MonitoringConsumer(AsyncWebsocketConsumer):
    """WebSocket потребитель для realtime мониторинга"""
    
    async def connect(self):
        """Обработчик подключения WebSocket"""
        await self.accept()
        
        # Подписываемся на группу инцидентов
        await self.channel_layer.group_add(
            'incidents',
            self.channel_name
        )
        
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Подключен к системе мониторинга'
        }))
    
    async def disconnect(self, close_code):
        """Обработчик отключения WebSocket"""
        pass
    
    async def receive(self, text_data):
        """Обработчик входящих WebSocket сообщений"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe_sensor':
                # Подписка на обновления конкретного сенсора
                tag = data.get('tag')
                if tag:
                    await self.channel_layer.group_add(
                        f"sensor_{tag}",
                        self.channel_name
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'subscribed',
                        'tag': tag
                    }))
            
            elif message_type == 'unsubscribe_sensor':
                # Отписка от обновлений сенсора
                tag = data.get('tag')
                if tag:
                    await self.channel_layer.group_discard(
                        f"sensor_{tag}",
                        self.channel_name
                    )
                    await self.send(text_data=json.dumps({
                        'type': 'unsubscribed',
                        'tag': tag
                    }))
            
            elif message_type == 'get_latest_data':
                # Получение последних данных
                tag = data.get('tag')
                if tag:
                    latest_data = await self.get_latest_sensor_data(tag)
                    await self.send(text_data=json.dumps({
                        'type': 'latest_data',
                        'tag': tag,
                        'data': latest_data
                    }))
            
            elif message_type == 'get_thresholds':
                # Получение уставок
                thresholds = await self.get_thresholds()
                await self.send(text_data=json.dumps({
                    'type': 'thresholds',
                    'data': thresholds
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Неверный формат JSON'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Ошибка: {str(e)}'
            }))
    
    async def sensor_update(self, event):
        """Отправка обновлений сенсора клиенту"""
        await self.send(text_data=json.dumps({
            'type': 'sensor_update',
            'tag': event['tag'],
            'data': event['data']
        }))
    
    async def incident_alert(self, event):
        """Отправка уведомления об инциденте"""
        await self.send(text_data=json.dumps({
            'type': 'incident_alert',
            'incident': event['incident']
        }))
    
    @database_sync_to_async
    def get_latest_sensor_data(self, tag):
        """Получение последних данных сенсора"""
        try:
            latest = SensorData.objects.filter(tag=tag).order_by('-timestamp').first()
            if latest:
                return {
                    'timestamp': latest.timestamp.isoformat(),
                    'value': float(latest.value),
                    'tag': latest.tag
                }
            return None
        except Exception:
            return None
    
    @database_sync_to_async
    def get_thresholds(self):
        """Получение всех уставок"""
        try:
            thresholds = Threshold.objects.all()
            return [
                {
                    'tag': t.tag,
                    'min_value': float(t.min_value) if t.min_value else None,
                    'max_value': float(t.max_value) if t.max_value else None
                }
                for t in thresholds
            ]
        except Exception:
            return [] 