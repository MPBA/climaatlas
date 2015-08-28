from django.conf import settings


def custom_settings(request):
    return { 'SITE_NAME': settings.SITE_NAME }