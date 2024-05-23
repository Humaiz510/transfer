import boto3
import zipfile
import os
import subprocess

def create_lambda_layer():
    # Setup directories and install packages
    os.makedirs('lambda_layer/nodejs', exist_ok=True)
    os.chdir('lambda_layer/nodejs')
    subprocess.run(['npm', 'init', '-y'])
    subprocess.run(['npm', 'install', '<your-package>'])
    os.chdir('..')

    # Zip the content
    with zipfile.ZipFile('lambda_layer.zip', 'w') as zipf:
        for root, dirs, files in os.walk('nodejs'):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file),
                                           os.path.join('nodejs', '..')))
    os.chdir('..')
    print("Layer package created: lambda_layer.zip")

def upload_lambda_layer():
    client = boto3.client('lambda')

    with open('lambda_layer.zip', 'rb') as f:
        zipped_code = f.read()

    response = client.publish_layer_version(
        LayerName='your-layer-name',
        Content={'ZipFile': zipped_code},
        CompatibleRuntimes=['nodejs14.x', 'nodejs16.x'],
    )
    layer_arn = response['LayerVersionArn']
    print(f"Layer ARN: {layer_arn}")
    return layer_arn

def update_lambda_function(function_name, layer_arn):
    client = boto3.client('lambda')
    
    response = client.update_function_configuration(
        FunctionName=function_name,
        Layers=[layer_arn],
    )
    print(f"Updated {function_name} with the new layer")

# Process
create_lambda_layer()
layer_arn = upload_lambda_layer()
update_lambda_function('your_lambda_function_name', layer_arn)


"""
1. setup directory for layer
mkdir lambda_layer
cd lambda_layer
mkdir nodejs
cd nodejs

2. Initialize a new Node.js project and install/update packages:
npm init -y
npm install <your-package>  # or `npm update <your-package>`

3. zip content
cd ..
zip -r lambda_layer.zip .
"""
