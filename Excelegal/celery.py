import os

from celery import Celery

from env import DEBUG

if DEBUG:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Excelegal.settings.development')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Excelegal.settings.production')

app = Celery('excelegal', broker="redis://127.0.0.1:6379/0",
             backend="redis://127.0.0.1:6379/0", )
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request}')
