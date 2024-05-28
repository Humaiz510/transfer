import boto3
import pytest
from datetime import datetime, timedelta
import json
import paramiko

# Initialize AWS clients
lambda_client = boto3.client('lambda')
securityhub_client = boto3.client('securityhub')

# Existing Lambda regression tests
def test_basic_invocation(lambda_function_name, payload):
    response = lambda_client.invoke(
        FunctionName=lambda_function_name,
        Payload=json.dumps(payload),
    )
    response_payload = json.loads(response['Payload'].read().decode('utf-8'))
    
    assert response['StatusCode'] == 200, "Invocation failed"
    assert 'errorMessage' not in response_payload, "Unexpected error in response"

def test_iam_roles_permissions(lambda_function_name):
    response = lambda_client.get_function(FunctionName=lambda_function_name)
    role_arn = response['Configuration']['Role']
    assert role_arn is not None, "IAM role is not attached"

def test_log_group_exists(lambda_function_name):
    logs_client = boto3.client('logs')
    log_group_name = f"/aws/lambda/{lambda_function_name}"
    response = logs_client.describe_log_groups(logGroupNamePrefix=log_group_name)
    log_groups = response.get('logGroups', [])
    
    assert any(lg['logGroupName'] == log_group_name for lg in log_groups), "Log group does not exist"

def test_unusual_duration_memory(lambda_function_name):
    cloudwatch_client = boto3.client('cloudwatch')
    response = cloudwatch_client.get_metric_statistics(
        Namespace='AWS/Lambda',
        MetricName='Duration',
        Dimensions=[{'Name': 'FunctionName', 'Value': lambda_function_name}],
        StartTime=datetime.utcnow() - timedelta(days=1),
        EndTime=datetime.utcnow(),
        Period=3600,
        Statistics=['Average'],
    )
    
    assert 'Datapoints' in response and len(response['Datapoints']) > 0, "No duration metrics found"
    for datapoint in response['Datapoints']:
        assert datapoint['Average'] < 5000, "Function duration is unusually high"

# New Security Hub findings test
def test_lambda_security_findings(lambda_function_arn):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    
    response = securityhub_client.get_findings(
        Filters={
            'ResourceId': [{'Value': lambda_function_arn, 'Comparison': 'EQUALS'}],
            'SeverityLabel': [{'Value': 'CRITICAL', 'Comparison': 'EQUALS'},
                              {'Value': 'HIGH', 'Comparison': 'EQUALS'}],
            'UpdatedAt': [{'Start': start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                           'End': end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')}]
        }
    )
    
    findings = response.get('Findings', [])
    assert len(findings) == 0, f"New security findings found in the last day: {findings}"

# Example test parameters
@pytest.mark.parametrize("lambda_function_name, payload", [
    ("your_lambda_function_name", {"key": "value"})
])
def test_lambda_basic_invocation(lambda_function_name, payload):
    test_basic_invocation(lambda_function_name, payload)

@pytest.mark.parametrize("lambda_function_name", ["your_lambda_function_name"])
def test_lambda_iam_roles_permissions(lambda_function_name):
    test_iam_roles_permissions(lambda_function_name)

@pytest.mark.parametrize("lambda_function_name", ["your_lambda_function_name"])
def test_lambda_log_group_exists(lambda_function_name):
    test_log_group_exists(lambda_function_name)

@pytest.mark.parametrize("lambda_function_name", ["your_lambda_function_name"])
def test_lambda_unusual_duration_memory(lambda_function_name):
    test_unusual_duration_memory(lambda_function_name)

@pytest.mark.parametrize("lambda_function_arn", ["arn:aws:lambda:region:account-id:function:your-function-name"])
def test_check_lambda_security_findings(lambda_function_arn):
    test_lambda_security_findings(lambda_function_arn)