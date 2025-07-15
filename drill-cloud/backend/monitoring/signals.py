from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import SensorData, Incident


@receiver(post_save, sender=SensorData)
def send_sensor_update(sender, instance, created, **kwargs):
    """Отправка обновления сенсора через WebSocket"""
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"sensor_{instance.tag}",
            {
                'type': 'sensor_update',
                'tag': instance.tag,
                'data': {
                    'timestamp': instance.timestamp.isoformat(),
                    'value': float(instance.value),
                    'tag': instance.tag
                }
            }
        )


@receiver(post_save, sender=Incident)
def send_incident_alert(sender, instance, created, **kwargs):
    """Отправка уведомления об инциденте через WebSocket"""
    if created:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "incidents",
            {
                'type': 'incident_alert',
                'incident': {
                    'id': instance.id,
                    'tag': instance.tag,
                    'value': float(instance.value),
                    'threshold_min': float(instance.threshold_min) if instance.threshold_min else None,
                    'threshold_max': float(instance.threshold_max) if instance.threshold_max else None,
                    'violation_type': instance.violation_type,
                    'timestamp': instance.timestamp.isoformat()
                }
            }
        ) 