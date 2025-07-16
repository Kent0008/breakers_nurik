from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import SensorData, Threshold, Incident
from .serializers import (
    SensorDataSerializer, ThresholdSerializer, IncidentSerializer,
    ThresholdCreateUpdateSerializer
)


class SensorDataViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для данных сенсоров"""
    serializer_class = SensorDataSerializer
    
    def get_queryset(self):
        queryset = SensorData.objects.all()
        
        # Фильтрация по тегу
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tag=tag)
        
        # Фильтрация по временному диапазону
        range_param = self.request.query_params.get('range', None)
        if range_param:
            now = timezone.now()
            if range_param == '1h':
                start_time = now - timedelta(hours=1)
            elif range_param == '24h':
                start_time = now - timedelta(days=1)
            elif range_param == '7d':
                start_time = now - timedelta(days=7)
            else:
                # По умолчанию последний час
                start_time = now - timedelta(hours=1)
            
            queryset = queryset.filter(timestamp__gte=start_time)
        
        # Ограничиваем все запросы максимум 200 записями для производительности
        latest_records = list(queryset.order_by('-timestamp')[:200])
        latest_records.reverse()  # Разворачиваем для хронологического порядка
        return SensorData.objects.filter(id__in=[r.id for r in latest_records]).order_by('timestamp')

    @action(detail=False, methods=['get'])
    def tags(self, request):
        """Получение списка всех тегов"""
        # Получаем только теги, которые имеют данные за последние 24 часа
        from datetime import timedelta
        from django.db.models import Count
        
        recent_time = timezone.now() - timedelta(hours=24)
        
        # Используем агрегацию для быстрого подсчета
        recent_tags = SensorData.objects.filter(
            timestamp__gte=recent_time
        ).values('tag').annotate(
            count=Count('id')
        ).order_by('-count')[:20]
        
        # Извлекаем только названия тегов
        top_tags = [item['tag'] for item in recent_tags]
        
        return Response({'tags': top_tags})


class ThresholdViewSet(viewsets.ModelViewSet):
    """ViewSet для уставок"""
    queryset = Threshold.objects.all()
    serializer_class = ThresholdSerializer
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ThresholdCreateUpdateSerializer
        return ThresholdSerializer

    def create(self, request, *args, **kwargs):
        """Создание или обновление уставки"""
        tag = request.data.get('tag')
        if tag:
            # Если уставка уже существует, обновляем её
            threshold, created = Threshold.objects.get_or_create(
                tag=tag,
                defaults=request.data
            )
            if not created:
                serializer = self.get_serializer(threshold, data=request.data, partial=True)
                serializer.is_valid(raise_exception=True)
                serializer.save()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return super().create(request, *args, **kwargs)


class IncidentViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet для инцидентов"""
    serializer_class = IncidentSerializer
    
    def get_queryset(self):
        queryset = Incident.objects.all()
        
        # Фильтрация по тегу
        tag = self.request.query_params.get('tag', None)
        if tag:
            queryset = queryset.filter(tag=tag)
        
        # Фильтрация по временному диапазону
        range_param = self.request.query_params.get('range', None)
        if range_param:
            now = timezone.now()
            if range_param == '1h':
                start_time = now - timedelta(hours=1)
            elif range_param == '24h':
                start_time = now - timedelta(days=1)
            elif range_param == '7d':
                start_time = now - timedelta(days=7)
            else:
                start_time = now - timedelta(hours=1)
            
            queryset = queryset.filter(timestamp__gte=start_time)
        
        return queryset.order_by('-timestamp') 