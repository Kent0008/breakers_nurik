from django.core.management.base import BaseCommand
from monitoring.mqtt_client import start_mqtt_client, stop_mqtt_client
import signal
import sys


class Command(BaseCommand):
    help = 'Запуск MQTT клиента для подписки на топики телеметрии'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Запуск MQTT клиента...')
        )
        
        # Обработчик сигналов для корректного завершения
        def signal_handler(sig, frame):
            self.stdout.write(
                self.style.WARNING('\nОстановка MQTT клиента...')
            )
            stop_mqtt_client()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        try:
            # Запуск MQTT клиента
            start_mqtt_client()
            
            self.stdout.write(
                self.style.SUCCESS('MQTT клиент запущен. Нажмите Ctrl+C для остановки.')
            )
            
            # Бесконечный цикл для поддержания работы клиента
            while True:
                signal.pause()
                
        except KeyboardInterrupt:
            self.stdout.write(
                self.style.WARNING('\nОстановка MQTT клиента...')
            )
            stop_mqtt_client()
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Ошибка: {e}')
            )
            stop_mqtt_client() 