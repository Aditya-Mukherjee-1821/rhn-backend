import zipfile
import sys
import os

# Absolute path where the ZIP file and model will be located
zip_file_path = os.path.join(os.path.dirname(__file__), 'pandapipes.zip')
extract_to_path = os.path.join(os.path.dirname(__file__), 'custom_pandapipes')

# Ensure the extraction folder exists
if not os.path.exists(extract_to_path):
    os.makedirs(extract_to_path)

# Extract the ZIP file
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to_path)

# Add the extracted folder to sys.path
sys.path.append(extract_to_path)

print(f"Custom pandapipes model extracted to {extract_to_path}")
