import os
import sys

# Add the directory that contains the 'pandapipes' module to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
custom_pandapipes_path = os.path.join(BASE_DIR, 'custom_pandapipes')
if custom_pandapipes_path not in sys.path:
    sys.path.insert(0, custom_pandapipes_path)

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
