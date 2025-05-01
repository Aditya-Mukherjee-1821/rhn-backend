import os
import sys

# Path to the custom pandapipes folder that contains pandapipes/
custom_pandapipes_path = os.path.join(os.path.dirname(__file__), 'custom_pandapipes')
if custom_pandapipes_path not in sys.path:
    sys.path.insert(0, custom_pandapipes_path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
