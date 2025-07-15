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
        
        return queryset.order_by('timestamp')

    @action(detail=False, methods=['get'])
    def tags(self, request):
        """Получение списка всех тегов"""
        tags = SensorData.objects.values_list('tag', flat=True).distinct()
        return Response({'tags': list(tags)})


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