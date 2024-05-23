import boto3
import pytest
from datetime import datetime, timedelta

inspector_client = boto3.client('inspector2')

def test_lambda_vulnerabilities(lambda_function_arn):
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)

    response = inspector_client.list_findings(
        filterCriteria={
            'awsAccountId': [
                {
                    'comparison': 'EQUALS',
                    'value': boto3.client('sts').get_caller_identity().get('Account')
                }
            ],
            'resourceId': [
                {
                    'comparison': 'EQUALS',
                    'value': lambda_function_arn
                }
            ],
            'severity': [
                {
                    'comparison': 'EQUALS',
                    'value': 'CRITICAL'
                },
                {
                    'comparison': 'EQUALS',
                    'value': 'HIGH'
                }
            ],
            'updatedAt': [
                {
                    'startInclusive': start_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ'),
                    'endInclusive': end_time.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
                }
            ]
        },
        maxResults=50  # Adjust the number of results based on your needs
    )
    
    findings = response.get('findings', [])
    assert len(findings) == 0, f"New vulnerabilities found in the last day: {findings}"

@pytest.mark.parametrize("lambda_function_arn", ["arn:aws:lambda:region:account-id:function:your-function-name"])
def test_check_lambda_vulnerabilities(lambda_function_arn):
    test_lambda_vulnerabilities(lambda_function_arn)