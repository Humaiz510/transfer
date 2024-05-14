import os
import time
import pytest
import boto3
import requests
import zipfile
import io
import re
import json
from dotenv import load_dotenv

load_dotenv()

# Fixture to initialize boto3 clients
@pytest.fixture(scope='module')
def aws_clients():
    session = boto3.Session(
        aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
        aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY'),
        region_name=os.getenv('AWS_REGION')
    )
    return {
        's3': session.client('s3'),
        'sns': session.client('sns'),
        'lambda': session.client('lambda')
    }

# Fixture to ensure the Lambda function is invoked before tests
@pytest.fixture(scope='module', autouse=True)
def setup_lambda(aws_clients):
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse'
    )
    return response

# Test Lambda execution time performance
def test_lambda_performance(aws_clients):
    start_time = time.time()
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse'
    )
    duration = time.time() - start_time
    assert duration < 1, "Lambda function took too long to execute."

# Test Lambda integration with DynamoDB
def test_lambda_integration_dynamodb(aws_clients):
    # Assuming there's a DynamoDB interaction in the Lambda function
    dynamodb_client = aws_clients['s3'].meta.client
    table_name = "YourDynamoDBTable"
    response = dynamodb_client.scan(TableName=table_name)
    assert 'Items' in response, "Lambda did not interact correctly with DynamoDB."

# Test Lambda error handling
def test_lambda_error_handling(aws_clients):
    try:
        aws_clients['lambda'].invoke(
            FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
            InvocationType='RequestResponse',
            Payload=json.dumps({"test": "error_triggering_input"})  # Assuming this input triggers an error
        )
    except Exception as e:
        assert "Error" in str(e), "Lambda did not handle errors as expected."

# Test environment variables are set and accessible in Lambda
def test_lambda_environment_variables(aws_clients):
    response = aws_clients['lambda'].get_function_configuration(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME')
    )
    env_vars = response['Environment']['Variables']
    assert 'MY_REQUIRED_ENV_VAR' in env_vars, "Required environment variable is missing."

# Test security policy of Lambda
def test_lambda_security(aws_clients):
    response = aws_clients['lambda'].get_policy(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME')
    )
    policy_document = json.loads(response['Policy'])
    assert 'Statement' in policy_document, "Lambda IAM policy is not correctly set."

# Test Lambda under load
def test_lambda_load(aws_clients):
    for _ in range(100):
        aws_clients['lambda'].invoke(
            FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
            InvocationType='Event'
        )
    assert True, "Lambda could not handle the load."

# Test Lambda input validation
def test_lambda_input_validation(aws_clients):
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"invalid": "data"})
    )
    assert "error" in response['Payload'].read().decode(), "Lambda did not validate input properly."

# Test Lambda output correctness
def test_lambda_output_validation(aws_clients):
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"valid": "input"})
    )
    output = json.loads(response['Payload'].read().decode())
    expected_output = {"result": "expected_value"}
    assert output == expected_output, "Lambda output did not match expected output."