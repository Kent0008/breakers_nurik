#!/usr/bin/env python
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drill_monitoring.settings")
    
    # Загружаем переменные окружения из .env файла
    from decouple import config
    
    # Получаем порт и хост из переменных окружения
    port = config('DJANGO_PORT', default=8000, cast=int)
    host = config('DJANGO_HOST', default='0.0.0.0')
    
    # Устанавливаем аргументы для запуска сервера
    sys.argv = ['manage.py', 'runserver', f'{host}:{port}']
    
    django.setup()
    execute_from_command_line(sys.argv) 