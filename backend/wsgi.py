import os
import sys

# Absolute path where the ZIP file and model will be located
zip_file_path = os.path.join(os.path.dirname(__file__), 'pandapipes-develop.zip')
extract_to_path = os.path.join(os.path.dirname(__file__), 'custom_pandapipes')

# Ensure the extraction folder exists
if not os.path.exists(extract_to_path):
    os.makedirs(extract_to_path)

# Extract the ZIP file
if os.path.exists(zip_file_path):
    import zipfile
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to_path)

    # Add the extracted folder to sys.path so pandapipes can be found
    sys.path.append(extract_to_path)
    print(f"Custom pandapipes model extracted to {extract_to_path}")
else:
    print(f"Error: The file {zip_file_path} does not exist!")

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Import and call the application after the setup
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
