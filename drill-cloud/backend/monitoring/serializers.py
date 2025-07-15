from rest_framework import serializers
from .models import SensorData, Threshold, Incident


class SensorDataSerializer(serializers.ModelSerializer):
    """Сериализатор для данных сенсоров"""
    
    class Meta:
        model = SensorData
        fields = ['id', 'timestamp', 'tag', 'value', 'created_at']


class ThresholdSerializer(serializers.ModelSerializer):
    """Сериализатор для уставок"""
    
    class Meta:
        model = Threshold
        fields = ['id', 'tag', 'min_value', 'max_value', 'created_at', 'updated_at']


class IncidentSerializer(serializers.ModelSerializer):
    """Сериализатор для инцидентов"""
    
    class Meta:
        model = Incident
        fields = ['id', 'tag', 'value', 'threshold_min', 'threshold_max', 
                 'violation_type', 'timestamp', 'created_at']


class ThresholdCreateUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания/обновления уставок"""
    
    class Meta:
        model = Threshold
        fields = ['tag', 'min_value', 'max_value']

    def validate(self, data):
        """Валидация данных уставки"""
        min_value = data.get('min_value')
        max_value = data.get('max_value')
        
        if min_value is not None and max_value is not None:
            if min_value >= max_value:
                raise serializers.ValidationError(
                    "Минимальное значение должно быть меньше максимального"
                )
        
        return data 