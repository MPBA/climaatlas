from __future__ import absolute_import

from celery import Celery
from django.conf import settings
import os

app = Celery('dataupload',
             broker='amqp://',
             backend='amqp://',
             include=['tasks'])

# Optional configuration, see the application user guide.
app.config_from_object('celeryconfig')

if __name__ == '__main__':
    app.start()
