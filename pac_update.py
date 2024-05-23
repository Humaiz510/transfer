import boto3
import zipfile
import os
import subprocess
import requests

def download_lambda_function(function_name, download_path):
    client = boto3.client('lambda')
    response = client.get_function(FunctionName=function_name)
    code_location = response['Code']['Location']
    
    response = requests.get(code_location)
    with open(download_path, 'wb') as f:
        f.write(response.content)
    print(f"Downloaded {function_name} to {download_path}")

def update_node_packages(zip_file_path, extracted_path):
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_path)
    
    os.chdir(extracted_path)
    subprocess.run(['npm', 'install'])
    subprocess.run(['npm', 'update'])

def package_updated_code(extracted_path, updated_zip_file):
    with zipfile.ZipFile(updated_zip_file, 'w') as zipf:
        for root, dirs, files in os.walk(extracted_path):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join(extracted_path, '..')))
    print(f"Packaged updated code to {updated_zip_file}")

def upload_updated_function(function_name, zip_file_path):
    client = boto3.client('lambda')
    
    with open(zip_file_path, 'rb') as f:
        zipped_code = f.read()
    
    response = client.update_function_code(
        FunctionName=function_name,
        ZipFile=zipped_code,
    )
    print(f"Updated {function_name} with the new code")

# Parameters
function_name = 'your_lambda_function_name'
download_path = 'function.zip'
extracted_path = 'function_code'
updated_zip_file = 'updated_function.zip'

# Process
download_lambda_function(function_name, download_path)
update_node_packages(download_path, extracted_path)
package_updated_code(extracted_path, updated_zip_file)
upload_updated_function(function_name, updated_zip_file)
