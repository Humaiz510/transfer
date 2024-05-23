import boto3
import json
import pytest
from datetime import datetime, timedelta
import subprocess

class TestLambdaRegressionSuite:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.lambda_name = None
        self.lambda_client = boto3.client('lambda')
        self.logs_client = boto3.client('logs')
        self.iam_client = boto3.client('iam')
        self.cloudwatch_client = boto3.client('cloudwatch')

    def set_lambda_name(self, lambda_name):
        self.lambda_name = lambda_name

    def test_valid_execution_role(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        role_arn = response['Configuration']['Role']
        assert role_arn is not None, "No execution role found for Lambda function"

    def test_valid_timeout(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        timeout = response['Configuration']['Timeout']
        assert timeout <= 300, "Lambda function timeout exceeds 300 seconds"

    def test_correct_memory_size(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        memory_size = response['Configuration']['MemorySize']
        assert 128 <= memory_size <= 3008, "Lambda function memory size is outside the valid range (128-3008 MB)"

    def test_lambda_performance(self):
        response = self.lambda_client.invoke(
            FunctionName=self.lambda_name,
            InvocationType='RequestResponse',
            Payload=json.dumps({"test_key": "test_value"})
        )
        assert response['StatusCode'] == 200
        
        log_group_name = f'/aws/lambda/{self.lambda_name}'
        log_streams = self.logs_client.describe_log_streams(
            logGroupName=log_group_name,
            orderBy='LastEventTime',
            descending=True,
            limit=1
        )['logStreams']
        
        assert len(log_streams) > 0
        log_stream_name = log_streams[0]['logStreamName']
        
        log_events = self.logs_client.get_log_events(
            logGroupName=log_group_name,
            logStreamName=log_stream_name,
            limit=5
        )['events']
        
        for event in log_events:
            message = event['message']
            if 'REPORT RequestId' in message:
                duration = float(message.split('Duration: ')[1].split(' ms')[0])
                memory_used = float(message.split('Max Memory Used: ')[1].split(' MB')[0])
                assert duration < 1000  # Example threshold
                assert memory_used < 128  # Example threshold

    def test_no_high_risk_permissions(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        role_arn = response['Configuration']['Role']
        role_name = role_arn.split('/')[-1]
        policies = self.iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
        
        for policy in policies:
            policy_arn = policy['PolicyArn']
            policy_version = self.iam_client.get_policy(PolicyArn=policy_arn)['Policy']['DefaultVersionId']
            policy_document = self.iam_client.get_policy_version(PolicyArn=policy_arn, VersionId=policy_version)['PolicyVersion']['Document']
            
            statements = policy_document['Statement']
            for statement in statements:
                if statement['Effect'] == 'Allow' and 'Action' in statement and '*' in statement['Action']:
                    assert False, f"High risk permission '*' found in policy: {policy_arn}"

    def test_no_outdated_python_runtime(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        runtime = response['Configuration']['Runtime']
        assert runtime in ['python3.8', 'python3.9', 'python3.10'], "Lambda function is using an outdated Python runtime"

    def test_valid_environment_variables(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        environment_variables = response['Configuration']['Environment']['Variables']
        assert 'ENV' in environment_variables, "Environment variable 'ENV' is missing"
        assert environment_variables['ENV'] in ['dev', 'test', 'prod'], "Environment variable 'ENV' has an invalid value"

    def test_concurrent_execution_limits(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        function_concurrency = self.lambda_client.get_function_concurrency(FunctionName=self.lambda_name)
        assert function_concurrency['ReservedConcurrentExecutions'] <= 1000, "Reserved concurrent executions exceed 1000"

    def test_metric_alarms(self):
        alarms = self.cloudwatch_client.describe_alarms(
            AlarmNamePrefix=self.lambda_name
        )['MetricAlarms']
        
        assert len(alarms) > 0, "No CloudWatch alarms found for Lambda function"

    def test_provisioned_concurrency(self):
        response = self.lambda_client.list_provisioned_concurrency_configs(
            FunctionName=self.lambda_name
        )
        provisioned_configs = response.get('ProvisionedConcurrencyConfigs', [])
        if provisioned_configs:
            for config in provisioned_configs:
                assert config['AllocatedProvisionedConcurrentExecutions'] > 0, "Provisioned concurrency not allocated properly"

    def test_no_excessive_log_retention(self):
        log_group_name = f'/aws/lambda/{self.lambda_name}'
        response = self.logs_client.describe_log_groups(
            logGroupNamePrefix=log_group_name
        )['logGroups']
        
        assert len(response) > 0, "No log group found for Lambda function"
        
        for log_group in response:
            retention_in_days = log_group.get('retentionInDays', None)
            assert retention_in_days is None or retention_in_days <= 30, "Log retention exceeds 30 days"

    def test_no_unrestricted_environment_variables(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        environment_variables = response['Configuration']['Environment']['Variables']
        
        unrestricted_keys = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        for key in unrestricted_keys:
            assert key not in environment_variables, f"Environment variable {key} should not be set"

    def test_tracing_enabled(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        tracing_config = response['Configuration'].get('TracingConfig', {})
        assert tracing_config.get('Mode') == 'Active', "X-Ray tracing is not enabled"

    def test_vpc_configuration(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        vpc_config = response['Configuration'].get('VpcConfig', {})
        if vpc_config:
            assert 'VpcId' in vpc_config, "Lambda function is configured for VPC but no VpcId found"
            assert len(vpc_config.get('SubnetIds', [])) > 0, "No SubnetIds found in VpcConfig"
            assert len(vpc_config.get('SecurityGroupIds', [])) > 0, "No SecurityGroupIds found in VpcConfig"

    def test_layers_configuration(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        layers = response['Configuration'].get('Layers', [])
        if layers:
            for layer in layers:
                layer_arn = layer['Arn']
                layer_version = self.lambda_client.get_layer_version(
                    Arn=layer_arn
                )
                assert layer_version['Version'] > 0, f"Layer version for {layer_arn} is invalid"

    def test_deployment_package_size(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        package_size = response['Configuration']['CodeSize']
        assert package_size < 50 * 1024 * 1024, "Lambda function deployment package size exceeds 50MB"

    def test_reserved_concurrent_executions(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        reserved_executions = response.get('Concurrency', {}).get('ReservedConcurrentExecutions', None)
        assert reserved_executions is None or reserved_executions <= 1000, "Reserved concurrent executions exceed 1000"

    def test_function_url_configuration(self):
        try:
            response = self.lambda_client.get_function_url_config(
                FunctionName=self.lambda_name
            )
            url_config = response.get('FunctionUrlConfig', {})
            if url_config:
                assert 'AuthType' in url_config, "Function URL AuthType is not set"
                assert url_config['AuthType'] in ['NONE', 'AWS_IAM'], "Function URL AuthType is invalid"
        except self.lambda_client.exceptions.ResourceNotFoundException:
            pass

    def test_proper_runtime(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        runtime = response['Configuration']['Runtime']
        valid_runtimes = [
            'nodejs14.x', 'nodejs16.x', 'nodejs18.x', 
            'python3.8', 'python3.9', 'python3.10', 
            'java11', 'java8.al2', 
            'provided.al2'
        ]
        assert runtime in valid_runtimes, f"Lambda function uses an invalid runtime: {runtime}"

    def test_function_tags(self):
        response = self.lambda_client.list_tags(Resource=self.lambda_name)
        tags = response.get('Tags', {})
        assert 'Project' in tags, "Lambda function does not have a 'Project' tag"
        assert 'Owner' in tags, "Lambda function does not have an 'Owner' tag"

    def test_maximum_execution_timeout(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        timeout = response['Configuration']['Timeout']
        assert timeout <= 900, "Lambda function timeout exceeds 900 seconds"

    def test_minimum_memory_size(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        memory_size = response['Configuration']['MemorySize']
        assert memory_size >= 128, "Lambda function memory size is less than 128 MB"

    def test_environment_variable_sanitization(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        environment_variables = response['Configuration']['Environment']['Variables']
        for key, value in environment_variables.items():
            assert value.isprintable(), f"Environment variable {key} contains non-printable characters"

    def test_code_storage_location(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        code_location = response['Code']['Location']
        assert code_location.startswith('https://'), "Lambda function code storage location is not secure"

    def test_dead_letter_config(self):
        response = self.lambda_client.get_function(FunctionName=self.lambda_name)
        dlq_config = response['Configuration'].get('DeadLetterConfig', {})
        if dlq_config:
            assert 'TargetArn' in dlq_config, "Dead letter queue is configured but no TargetArn found"

    def test_retries_on_failure(self):
        response = self.lambda_client.get_function_event_invoke_config(FunctionName=self.lambda_name)
        retry_config = response.get('MaximumRetryAttempts', None)
        assert retry_config is not None, "Retry configuration is not set"
        assert retry_config <= 2, "Retry configuration exceeds 2 attempts"

    def test_log_subscription_filters(self):
        log_group_name = f'/aws/lambda/{self.lambda_name}'
        response = self.logs_client.describe_subscription_filters(
            logGroupName=log_group_name
        )['subscriptionFilters']
        assert len(response) > 0, "No log subscription filters found for Lambda function"

def lambda_handler(event, context):
    lambda_name = event['detail']['requestParameters']['functionName']
    
    # Create an instance of the test class
    test_class = TestLambdaRegressionSuite()
    test_class.setup()
    test_class.set_lambda_name(lambda_name)
    
    # Run pytest programmatically and capture the results
    result = subprocess.run(['pytest', '--tb=short', '-q'], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Tests failed:\n{result.stdout}\n{result.stderr}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Tests executed successfully')
    }
