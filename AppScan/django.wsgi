import os
import sys

path = '/var/www/AppScan'
if path not in sys.path:
    sys.path.append('/var/www/AppScan')

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "AppScan.settings")

import django.core.handlers.wsgi
    application = django.core.handlers.wsgi.WSGIHandler()
