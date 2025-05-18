import os
from celery import Celery
from django.conf import settings
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'service.settings')

app = Celery('service')

# Загрузка настроек из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Установка брокера, если в Django настройки с именем CELERY_BROKER_URL
app.conf.broker_url = settings.CELERY_BROKER_URL

# Автозагрузка задач
app.autodiscover_tasks()

@app.task
def debug_task():
    time.sleep(20)
    print('Hello from debug_task')
