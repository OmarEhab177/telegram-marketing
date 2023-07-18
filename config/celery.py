import os
from celery import Celery


# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# Create the Celery app
app = Celery('config', broker='amqp://localhost', backend='django-db', include=['marketing.tasks'])

# Load the Celery configuration from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover and register Celery tasks from all installed apps
app.autodiscover_tasks()
