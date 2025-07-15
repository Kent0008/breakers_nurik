from django.db import models
from django.utils import timezone


class SensorData(models.Model):
    """Модель для хранения данных сенсоров"""
    timestamp = models.DateTimeField('Время измерения')
    tag = models.CharField('Идентификатор параметра', max_length=100)
    value = models.DecimalField('Значение', max_digits=10, decimal_places=3)
    created_at = models.DateTimeField('Время создания', auto_now_add=True)

    class Meta:
        db_table = 'sensor_data'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['tag']),
            models.Index(fields=['tag', 'timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.tag}: {self.value} at {self.timestamp}"


class Threshold(models.Model):
    """Модель для хранения уставок параметров"""
    tag = models.CharField('Идентификатор параметра', max_length=100, unique=True)
    min_value = models.DecimalField('Минимальное значение', max_digits=10, decimal_places=3, null=True, blank=True)
    max_value = models.DecimalField('Максимальное значение', max_digits=10, decimal_places=3, null=True, blank=True)
    created_at = models.DateTimeField('Время создания', auto_now_add=True)
    updated_at = models.DateTimeField('Время обновления', auto_now=True)

    class Meta:
        db_table = 'thresholds'
        ordering = ['tag']

    def __str__(self):
        return f"{self.tag}: {self.min_value} - {self.max_value}"

    def is_violated(self, value):
        """Проверяет, нарушена ли уставка для данного значения"""
        if self.min_value is not None and value < self.min_value:
            return True, 'min_violation'
        if self.max_value is not None and value > self.max_value:
            return True, 'max_violation'
        return False, None


class Incident(models.Model):
    """Модель для хранения инцидентов нарушений уставок"""
    VIOLATION_TYPES = [
        ('min_violation', 'Нарушение минимума'),
        ('max_violation', 'Нарушение максимума'),
    ]

    tag = models.CharField('Идентификатор параметра', max_length=100)
    value = models.DecimalField('Значение', max_digits=10, decimal_places=3)
    threshold_min = models.DecimalField('Минимум уставки', max_digits=10, decimal_places=3, null=True, blank=True)
    threshold_max = models.DecimalField('Максимум уставки', max_digits=10, decimal_places=3, null=True, blank=True)
    violation_type = models.CharField('Тип нарушения', max_length=20, choices=VIOLATION_TYPES)
    timestamp = models.DateTimeField('Время нарушения')
    created_at = models.DateTimeField('Время создания', auto_now_add=True)

    class Meta:
        db_table = 'incidents'
        indexes = [
            models.Index(fields=['timestamp']),
            models.Index(fields=['tag']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.tag} {self.violation_type}: {self.value} at {self.timestamp}" 