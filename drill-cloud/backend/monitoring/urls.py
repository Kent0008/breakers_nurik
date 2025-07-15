from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SensorDataViewSet, ThresholdViewSet, IncidentViewSet

router = DefaultRouter()
router.register(r'data', SensorDataViewSet, basename='sensor-data')
router.register(r'thresholds', ThresholdViewSet, basename='thresholds')
router.register(r'incidents', IncidentViewSet, basename='incidents')

urlpatterns = [
    path('', include(router.urls)),
] 