# core/celery.py
from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Django settings modulini o'rnatish
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

# Celery instansiyasini yaratish
app = Celery('core')

# Celery konfiguratsiyasini Django settings.py faylidan olish
app.config_from_object('django.conf:settings', namespace='CELERY')


# Celery task'larini avtomatik aniqlash
app.autodiscover_tasks(['core'])


celery_app = Celery(
    'tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

celery_app.conf.timezone = 'Asia/Tashkent'


