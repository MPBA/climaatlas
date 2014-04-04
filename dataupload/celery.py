from __future__ import absolute_import

from celery import Celery
from django.conf import settings
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'climatlas.settings')

app = Celery('dataupload',
             broker='amqp://',
             backend='amqp://',
             include=['dataupload.tasks'])

# Optional configuration, see the application user guide.
app.conf.update(
    CELERY_TASK_RESULT_EXPIRES=3600,
)

if __name__ == '__main__':
    app.start()
