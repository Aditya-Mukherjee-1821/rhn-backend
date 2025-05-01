import zipfile
import sys
import os

# Path to your ZIP file
zip_file_path = 'pandapipes-develop.zip'
# Directory where the model should be extracted
extract_to_path = './custom_pandapipes/'

# Ensure the extraction folder exists
if not os.path.exists(extract_to_path):
    os.makedirs(extract_to_path)

# Extract the ZIP file
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    zip_ref.extractall(extract_to_path)

# Add the extracted directory to sys.path to use the custom pandapipes model
sys.path.append(extract_to_path)

print(f"Custom pandapipes model extracted to {extract_to_path}")
