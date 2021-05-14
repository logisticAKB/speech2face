import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speech2face.settings')

app = Celery('speech2face')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
