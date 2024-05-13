import os
import time
import pytest
import boto3
import requests
import zipfile
import io
import re
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = os.getenv('AWS_REGION')
SNS_TOPIC_ARN = os.getenv('SNS_TOPIC_ARN')
LAMBDA_FUNCTION_NAME = os.getenv('LAMBDA_FUNCTION_NAME')

# Initialize boto3 clients
@pytest.fixture(scope='module')
def aws_clients():
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )
    clients = {
        's3': session.client('s3'),
        'sns': session.client('sns'),
        'lambda': session.client('lambda')
    }
    return clients

@pytest.fixture(scope='module', autouse=True)
def setup_lambda(aws_clients):
    # Invoke the Lambda function before running the tests
    response = aws_clients['lambda'].invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType='Event'  # Change to 'RequestResponse' if you want to wait for a response
    )
    return response

def get_lambda_code(lambda_client, lambda_function_name):
    response = lambda_client.get_function(FunctionName=lambda_function_name)
    code_url = response['Code']['Location']
    code_response = requests.get(code_url)
    
    # Extract the zip file from the response content
    zip_file = zipfile.ZipFile(io.BytesIO(code_response.content))
    
    # Read and return the content of the Lambda function file (assume it's a single .py file)
    lambda_code = ""
    for file_name in zip_file.namelist():
        if file_name.endswith('.py'):
            with zip_file.open(file_name) as f:
                lambda_code += f.read().decode('utf-8')
    return lambda_code

def extract_s3_details(lambda_code):
    # Regex pattern to match s3.Object(BUCKET_NAME, KEY)
    pattern = re.compile(r's3\.Object\s*\(\s*[\'"]([^\'"]+)[\'"]\s*,\s*[\'"]([^\'"]+)[\'"]\s*\)', re.IGNORECASE)
    match = pattern.search(lambda_code)
    
    bucket_name = match.group(1) if match else None
    key = match.group(2) if match else None
    
    # Debug information
    print("Lambda Code:\n", lambda_code)
    print("Extracted Bucket Name: ", bucket_name)
    print("Extracted Key: ", key)
    
    return bucket_name, key

def check_s3_for_file(s3_client, bucket_name, prefix=''):
    response = s3_client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
    return response.get('Contents', [])

def download_file(s3_client, bucket_name, key, download_path):
    s3_client.download_file(bucket_name, key, download_path)

def send_sns_notification(sns_client, message):
    response = sns_client.publish(
        TopicArn=SNS_TOPIC_ARN,
        Message=message,
        Subject='Lambda Regression Test Failure'
    )
    return response

def test_lambda_output(aws_clients):
    lambda_client = aws_clients['lambda']
    s3_client = aws_clients['s3']
    
    # Get Lambda code
    lambda_code = get_lambda_code(lambda_client, LAMBDA_FUNCTION_NAME)
    
    # Extract S3 bucket name and key
    bucket_name, key = extract_s3_details(lambda_code)
    
    assert bucket_name is not None, "Could not extract S3 bucket name from Lambda code."
    assert key is not None, "Could not extract S3 key from Lambda code."
    
    # Check if the Lambda wrote a file to S3
    files = check_s3_for_file(s3_client, bucket_name, key)
    assert files, "No files found in S3 bucket. The Lambda function may not have executed correctly."

    # Assume we're interested in the first file
    s3_key = files[0]['Key']
    download_path = f"/tmp/{os.path.basename(s3_key)}"

    try:
        # Download the file
        download_file(s3_client, bucket_name, s3_key, download_path)

        # Check if the file is viewable (can be opened and read)
        with open(download_path, 'r') as file:
            content = file.read()
            assert content, "The file is empty or unreadable."

    except Exception as e:
        # Send an SNS notification if there is an exception
        send_sns_notification(aws_clients['sns'], f"Test failed with error: {e}")
        raise e

def test_lambda_performance(aws_clients):
    start_time = time.time()
    
    # Invoke the Lambda function
    response = aws_clients['lambda'].invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType='RequestResponse'
    )
    
    end_time = time.time()
    execution_time = end_time - start_time
    
    # Assert that the execution time is within acceptable limits (e.g., 1 second)
    assert execution_time < 1, f"Lambda function took too long to execute: {execution_time} seconds"

def test_lambda_integration_dynamodb():
    # This is a placeholder; you need to add your actual DynamoDB check logic here
    assert True

def test_lambda_error_handling(aws_clients):
    # Modify the invocation to trigger an error
    response = aws_clients['lambda'].invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType='RequestResponse'
    )
    
    # Check the response for error handling
    payload = response['Payload'].read().decode('utf-8')
    assert 'FunctionError' in response or 'errorMessage' in payload, "Lambda function did not handle error correctly"

def test_lambda_environment_variables(aws_clients):
    lambda_client = aws_clients['lambda']
    
    # Retrieve the Lambda function configuration
    response = lambda_client.get_function_configuration(FunctionName=LAMBDA_FUNCTION_NAME)
    environment_variables = response['Environment']['Variables']
    
    # Check that required environment variables are set
    required_vars = ['ENV_VAR1', 'ENV_VAR2']
    for var in required_vars:
        assert var in environment_variables, f"Environment variable {var} is missing"

def test_lambda_security(aws_clients):
    lambda_client = aws_clients['lambda']
    
    # Retrieve the Lambda function policy
    response = lambda_client.get_policy(FunctionName=LAMBDA_FUNCTION_NAME)
    policy = response['Policy']
    
    # Check for least privilege
    # Add your IAM policy verification logic here
    assert 'LeastPrivilegePolicy' in policy, "Lambda function does not have least privilege policy"

def test_lambda_load(aws_clients):
    lambda_client = aws_clients['lambda']
    
    # Simulate high load by invoking the Lambda function multiple times
    for _ in range(100):  # Adjust the number as needed
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType='Event'
        )
    
    # Add your verification logic for load testing here
    assert True  # Replace with actual verification logic

def test_lambda_input_validation(aws_clients):
    lambda_client = aws_clients['lambda']
    
    # Test various inputs to ensure the Lambda function validates inputs correctly
    invalid_inputs = [
        {},  # Empty input
        {"key": "value"},  # Missing required fields
        # Add more invalid inputs as needed
    ]
    
    for input_data in invalid_inputs:
        response = lambda_client.invoke(
            FunctionName=LAMBDA_FUNCTION_NAME,
            InvocationType='RequestResponse',
            Payload=json.dumps(input_data)
        )
        payload = response['Payload'].read().decode('utf-8')
        assert 'ValidationError' in payload, f"Lambda function did not handle invalid input: {input_data}"

def test_lambda_output_validation(aws_clients):
    lambda_client = aws_clients['lambda']
    
    # Test the Lambda function with various inputs and verify the output
    valid_input = {"key": "value"}
    response = lambda_client.invoke(
        FunctionName=LAMBDA_FUNCTION_NAME,
        InvocationType='RequestResponse',
        Payload=json.dumps(valid_input)
    )
    payload = response['Payload'].read().decode('utf-8')
    expected_output = {"expected_key": "expected_value"}
    assert json.loads(payload) == expected_output, f"Lambda function output did not match expected output: {payload}"
