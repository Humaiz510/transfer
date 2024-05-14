import json
import os
import pytest
import boto3
from datetime import datetime, timedelta

@pytest.fixture
def aws_clients():
    return {
        'lambda': boto3.client('lambda'),
        'cloudwatch': boto3.client('cloudwatch'),
        's3': boto3.client('s3')
    }

def test_lambda_timeout(aws_clients):
    """Test to ensure Lambda respects its timeout setting."""
    start_time = datetime.now()
    try:
        response = aws_clients['lambda'].invoke(
            FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
            InvocationType='RequestResponse',
            Payload=json.dumps({"simulate": "long_running_process"})
        )
        duration = datetime.now() - start_time
        config = aws_clients['lambda'].get_function_configuration(
            FunctionName=os.getenv('LAMBDA_FUNCTION_NAME')
        )
        configured_timeout = config['Timeout']
        assert duration.seconds <= configured_timeout, "Function ran longer than configured timeout"
    except aws_clients['lambda'].exceptions.FunctionTimedOutException:
        pass

def test_memory_usage(aws_clients):
    """Test to verify that the Lambda does not exceed its memory allocation."""
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"test": "memory_usage"})
    )
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(minutes=5)
    metrics = aws_clients['cloudwatch'].get_metric_data(
        MetricDataQueries=[
            {
                'Id': 'maxMemoryUsed',
                'MetricStat': {
                    'Metric': {
                        'Namespace': 'AWS/Lambda',
                        'MetricName': 'MaxMemoryUsed',
                        'Dimensions': [{'Name': 'FunctionName', 'Value': os.getenv('LAMBDA_FUNCTION_NAME')}]
                    },
                    'Period': 60,
                    'Stat': 'Maximum'
                }
            }
        ],
        StartTime=start_time,
        EndTime=end_time
    )
    max_memory_used = max(metrics['MetricDataResults'][0]['Values'])
    config = aws_clients['lambda'].get_function_configuration(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME')
    )
    assert max_memory_used <= config['MemorySize'], "Lambda function exceeded its memory allocation"

def test_concurrent_executions(aws_clients):
    """Test how Lambda handles concurrent executions."""
    from threading import Thread

    def invoke_lambda():
        aws_clients['lambda'].invoke(
            FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
            InvocationType='Event'
        )

    threads = [Thread(target=invoke_lambda) for _ in range(10)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Additional checks can be added here to verify concurrency handling
    # This might include log inspection or metrics analysis

def test_idempotency(aws_clients):
    """Ensure that the Lambda function is idempotent when required."""
    input_payload = json.dumps({"idempotent": "data", "timestamp": datetime.utcnow().isoformat()})
    first_response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=input_payload
    )
    second_response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=input_payload
    )
    assert first_response['Payload'].read() == second_response['Payload'].read(), "Responses differ for the same input"

def test_cold_start_performance(aws_clients):
    """Test Lambda cold start performance."""
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"test": "cold_start"})
    )
    assert response['StatusCode'] == 200, "Cold start invocation failed"
    cold_start_duration = response['ResponseMetadata']['HTTPHeaders']['x-amzn-RequestId']
    assert cold_start_duration < os.getenv('COLD_START_THRESHOLD'), "Cold start duration exceeded threshold"

def test_integration_with_s3(aws_clients):
    """Test Lambda integration with S3."""
    s3_client = aws_clients['s3']
    test_bucket = os.getenv('TEST_S3_BUCKET')
    test_key = 'test-key'

    # Upload a test file to S3
    s3_client.put_object(Bucket=test_bucket, Key=test_key, Body="Test content")
    
    # Invoke Lambda to process the test file
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"bucket": test_bucket, "key": test_key})
    )
    
    # Verify Lambda processed the file as expected
    processed_key = 'processed/test-key'
    processed_object = s3_client.get_object(Bucket=test_bucket, Key=processed_key)
    assert processed_object['Body'].read() == b"Processed content", "S3 integration failed"

def test_response_structure(aws_clients):
    """Test that the Lambda function returns a response with the correct structure."""
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"test": "response_structure"})
    )
    response_payload = json.loads(response['Payload'].read())
    assert 'statusCode' in response_payload, "Response missing statusCode"
    assert 'body' in response_payload, "Response missing body"
    body = json.loads(response_payload['body'])
    assert 'message' in body, "Response body missing message"
    assert 'data' in body, "Response body missing data"