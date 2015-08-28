from __future__ import absolute_import
from . import celeryconfig

from celery import Celery

app = Celery('dataupload')

# Optional configuration, see the application user guide.
app.config_from_object(celeryconfig)

if __name__ == '__main__':
    app.start()
