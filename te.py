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
        's3': boto3.client('s3'),
        'logs': boto3.client('logs'),
        'dynamodb': boto3.client('dynamodb'),
        'iam': boto3.client('iam'),
        'sns': boto3.client('sns'),
        'sqs': boto3.client('sqs')
    }

def test_api_contract(aws_clients):
    """Ensure Lambda returns expected output for given inputs."""
    test_input = {"action": "test"}
    expected_output = {"status": "success", "message": "Test executed"}
    
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps(test_input)
    )
    response_payload = json.loads(response['Payload'].read())
    
    assert response_payload == expected_output, f"Expected {expected_output}, got {response_payload}"

def test_error_handling(aws_clients):
    """Verify Lambda handles different error scenarios correctly."""
    invalid_input = {"action": "invalid"}
    
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps(invalid_input)
    )
    response_payload = json.loads(response['Payload'].read())
    
    assert response_payload.get('statusCode') == 400, "Expected status code 400 for invalid input"
    assert 'error' in response_payload, "Expected error message in response"

def test_performance_metrics(aws_clients):
    """Ensure Lambda meets performance benchmarks."""
    start_time = datetime.utcnow()
    aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"action": "performance_test"})
    )
    end_time = datetime.utcnow()
    
    duration = (end_time - start_time).total_seconds()
    assert duration < 2, "Lambda execution exceeded performance benchmark of 2 seconds"

def test_resource_cleanup(aws_clients):
    """Check that Lambda cleans up resources correctly after execution."""
    aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='Event',
        Payload=json.dumps({"action": "resource_cleanup"})
    )
    
    # Simulate a delay for resource cleanup
    time.sleep(5)
    
    # Verify resource cleanup (Example: checking if a temporary S3 object is deleted)
    test_bucket = os.getenv('TEST_S3_BUCKET')
    temp_key = 'temp-key'
    s3_client = aws_clients['s3']
    
    try:
        s3_client.head_object(Bucket=test_bucket, Key=temp_key)
        assert False, "Temporary S3 object was not deleted"
    except s3_client.exceptions.ClientError as e:
        assert e.response['Error']['Code'] == '404', "Expected 404 error for missing S3 object"

def test_integration_with_dynamodb(aws_clients):
    """Test Lambda integration with DynamoDB."""
    test_table = os.getenv('TEST_DYNAMODB_TABLE')
    
    # Put an item in the DynamoDB table
    aws_clients['dynamodb'].put_item(
        TableName=test_table,
        Item={'id': {'S': 'test-id'}, 'value': {'S': 'test-value'}}
    )
    
    # Invoke Lambda to process the item
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"action": "process_dynamodb", "id": "test-id"})
    )
    
    response_payload = json.loads(response['Payload'].read())
    assert response_payload['status'] == 'success', "DynamoDB integration failed"

def test_environment_variables(aws_clients):
    """Verify Lambda correctly uses environment variables."""
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"action": "check_env"})
    )
    response_payload = json.loads(response['Payload'].read())
    
    assert response_payload['env_var'] == os.getenv('EXPECTED_ENV_VAR'), "Environment variable mismatch"

def test_iam_roles_and_permissions(aws_clients):
    """Ensure Lambda has correct IAM roles and permissions."""
    function_name = os.getenv('LAMBDA_FUNCTION_NAME')
    
    response = aws_clients['lambda'].get_function(
        FunctionName=function_name
    )
    role_arn = response['Configuration']['Role']
    
    role_name = role_arn.split('/')[-1]
    policy_response = aws_clients['iam'].list_attached_role_policies(
        RoleName=role_name
    )
    
    expected_policy_arn = os.getenv('EXPECTED_POLICY_ARN')
    attached_policies = [policy['PolicyArn'] for policy in policy_response['AttachedPolicies']]
    
    assert expected_policy_arn in attached_policies, f"Expected policy {expected_policy_arn} not attached to the role"

def test_logging(aws_clients):
    """Verify that Lambda logs events correctly."""
    log_group_name = f"/aws/lambda/{os.getenv('LAMBDA_FUNCTION_NAME')}"
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"action": "generate_log"})
    )
    
    log_events = aws_clients['logs'].filter_log_events(
        logGroupName=log_group_name,
        startTime=int((datetime.utcnow() - timedelta(minutes=1)).timestamp() * 1000)
    )
    
    assert any("Log message" in event['message'] for event in log_events['events']), "Expected log message not found"

def test_response_time(aws_clients):
    """Ensure the response time is within acceptable limits."""
    start_time = datetime.utcnow()
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"action": "test_response_time"})
    )
    end_time = datetime.utcnow()
    
    duration = (end_time - start_time).total_seconds()
    assert duration < 1, "Response time exceeded 1 second"

def test_sns_integration(aws_clients):
    """Test Lambda integration with SNS."""
    sns_topic_arn = os.getenv('SNS_TOPIC_ARN')
    
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"action": "sns_publish", "message": "Test message", "topic_arn": sns_topic_arn})
    )
    
    response_payload = json.loads(response['Payload'].read())
    assert response_payload['status'] == 'success', "SNS integration failed"

def test_sqs_integration(aws_clients):
    """Test Lambda integration with SQS."""
    sqs_queue_url = os.getenv('SQS_QUEUE_URL')
    
    response = aws_clients['lambda'].invoke(
        FunctionName=os.getenv('LAMBDA_FUNCTION_NAME'),
        InvocationType='RequestResponse',
        Payload=json.dumps({"action": "sqs_send_message", "message": "Test message", "queue_url": sqs_queue_url})
    )
    
    response_payload = json.loads(response['Payload'].read())
    assert response_payload['status'] == 'success', "SQS integration failed"

def test_lambda_timeout(aws_clients):
    """Test Lambda respects its timeout setting."""
    start_time = datetime.now()
    try:
        aws_clients['lambda'].invoke(
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
    """Test Lambda does not exceed its memory allocation."""
    aws_clients['lambda'].invoke(
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

def