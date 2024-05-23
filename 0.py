import boto3
import subprocess
import json
import pytest
from datetime import datetime, timedelta

class TestLambdaRegressionSuite:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.lambda_name = None
        self.inspector_client = boto3.client('inspector2')
        self.lambda_client = boto3.client('lambda')
        self.logs_client = boto3.client('logs')
        self.iam_client = boto3.client('iam')

    def set_lambda_name(self, lambda_name):
        self.lambda_name = lambda_name

    def get_today_date_range(self):
        now = datetime.utcnow()
        start_of_day = datetime(now.year, now.month, now.day)
        end_of_day = start_of_day + timedelta(days=1)
        return start_of_day.isoformat(), end_of_day.isoformat()

    def test_no_critical_high_severity_findings(self):
        start_of_day, end_of_day = self.get_today_date_range()
        findings = self.inspector_client.list_findings(
            filterCriteria={
                'resourceId': [{'comparison': 'EQUALS', 'value': self.lambda_name}],
                'severity': [{'comparison': 'EQUALS', 'value': 'HIGH'}, {'comparison': 'EQUALS', 'value': 'CRITICAL'}],
                'createdAt': [{'startInclusive': start_of_day, 'endExclusive': end_of_day}]
            }
        )['findings']
        
        assert len(findings) == 0, f"Critical or high severity findings found: {findings}"

    def test_no_unresolved_findings(self):
        start_of_day, end_of_day = self.get_today_date_range()
        findings = self.inspector_client.list_findings(
            filterCriteria={
                'resourceId': [{'comparison': 'EQUALS', 'value': self.lambda_name}],
                'status': [{'comparison': 'EQUALS', 'value': 'UNRESOLVED'}],
                'createdAt': [{'startInclusive': start_of_day, 'endExclusive': end_of_day}]
            }
        )['findings']
        
        assert len(findings) == 0, f"Unresolved findings found: {findings}"

    def test_no_exceeded_sla_findings(self):
        start_of_day, end_of_day = self.get_today_date_range()
        findings = self.inspector_client.list_findings(
            filterCriteria={
                'resourceId': [{'comparison': 'EQUALS', 'value': self.lambda_name}],
                'remediation': [{'comparison': 'EXCEEDED_SLA'}],
                'createdAt': [{'startInclusive': start_of_day, 'endExclusive': end_of_day}]
            }
        )['findings']
        
        assert len(findings) == 0, f"Findings with exceeded SLA found: {findings}"

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

    def test_combined_security_performance(self):
        self.test_no_critical_high_severity_findings()
        self.test_no_unresolved_findings()
        self.test_no_exceeded_sla_findings()
        self.test_lambda_performance()

    def test_inspector_rules_compliance(self):
        start_of_day, end_of_day = self.get_today_date_range()
        findings = self.inspector_client.list_findings(
            filterCriteria={
                'resourceId': [{'comparison': 'EQUALS', 'value': self.lambda_name}],
                'createdAt': [{'startInclusive': start_of_day, 'endExclusive': end_of_day}]
            }
        )['findings']
        
        rule_arns = set(finding['inspectorRuleArn'] for finding in findings)
        
        for rule_arn in rule_arns:
            rule_findings = [finding for finding in findings if finding['inspectorRuleArn'] == rule_arn]
            assert len(rule_findings) == 0, f"Non-compliance with rule {rule_arn} found: {rule_findings}"

    def test_valid_execution_role(self):
        response = self.lambda_client.get_function(
            FunctionName=self.lambda_name
        )
        role_arn = response['Configuration']['Role']
        assert role_arn is not None, "No execution role found for Lambda function"

    def test_valid_timeout(self):
        response = self.lambda_client.get_function(
            FunctionName=self.lambda_name
        )
        timeout = response['Configuration']['Timeout']
        assert timeout <= 300, "Lambda function timeout exceeds 300 seconds"

    def test_correct_memory_size(self):
        response = self.lambda_client.get_function(
            FunctionName=self.lambda_name
        )
        memory_size = response['Configuration']['MemorySize']
        assert 128 <= memory_size <= 3008, "Lambda function memory size is outside the valid range (128-3008 MB)"

    def test_inspector_vulnerability_absence(self):
        start_of_day, end_of_day = self.get_today_date_range()
        known_vulnerabilities = ['CVE-2021-44228', 'CVE-2021-45046']
        for vuln in known_vulnerabilities:
            findings = self.inspector_client.list_findings(
                filterCriteria={
                    'resourceId': [{'comparison': 'EQUALS', 'value': self.lambda_name}],
                    'vulnerabilityId': [{'comparison': 'EQUALS', 'value': vuln}],
                    'createdAt': [{'startInclusive': start_of_day, 'endExclusive': end_of_day}]
                }
            )['findings']
            assert len(findings) == 0, f"Vulnerability {vuln} found in Lambda function: {findings}"

    def test_no_high_risk_permissions(self):
        response = self.lambda_client.get_function(
            FunctionName=self.lambda_name
        )
        role_arn = response['Configuration']['Role']
        role_name = role_arn.split('/')[-1]
        policies = self.iam_client.list_attached_role_policies(
            RoleName=role_name
        )['AttachedPolicies']
        
        for policy in policies:
            policy_arn = policy['PolicyArn']
            policy_version = self.iam_client.get_policy(
                PolicyArn=policy_arn
            )['Policy']['DefaultVersionId']
            policy_document = self.iam_client.get_policy_version(
                PolicyArn=policy_arn,
                VersionId=policy_version
            )['PolicyVersion']['Document']
            
            statements = policy_document['Statement']
            for statement in statements:
                if statement['Effect'] == 'Allow' and 'Action' in statement and '*' in statement['Action']:
                    assert False, f"High risk permission '*' found in policy: {policy_arn}"

    def test_no_outdated_python_runtime(self):
        response = self.lambda_client.get_function(
            FunctionName=self.lambda_name
        )
        runtime = response['Configuration']['Runtime']
        assert runtime in ['python3.8', 'python3.9', 'python3.10'], "Lambda function is using an outdated Python runtime"

    def test_inspector_finding_count_below_threshold(self):
        start_of_day, end_of_day = self.get_today_date_range()
        findings = self.inspector_client.list_findings(
            filterCriteria={
                'resourceId': [{'comparison': 'EQUALS', 'value': self.lambda_name}],
                'createdAt': [{'startInclusive': start_of_day, 'endExclusive': end_of_day}]
            }
        )['findings']
        
        assert len(findings) < 10, "Lambda function has more than 10 Inspector findings"

    def test_valid_environment_variables(self):
        response = self.lambda_client.get_function(
            FunctionName=self.lambda_name
        )
        environment_variables = response['Configuration']['Environment']['Variables']
        assert 'ENV' in environment_variables, "Environment variable 'ENV' is missing"
        assert environment_variables['ENV'] in ['dev', 'test', 'prod'], "Environment variable 'ENV' has an invalid value"

    def test_inspector_finding_severity_distribution(self):
        start_of_day, end_of_day = self.get_today_date_range()
        findings = self.inspector_client.list_findings(
            filterCriteria={
                'resourceId': [{'comparison': 'EQUALS', 'value': self.lambda_name}],
                'createdAt': [{'startInclusive': start_of_day, 'endExclusive': end_of_day}]
            }
        )['findings']
        
        severity_count = {'LOW': 0, 'MEDIUM': 0, 'HIGH': 0, 'CRITICAL': 0}
        for finding in findings:
            severity_count[finding['severity']] += 1
        
        assert severity_count['HIGH'] < 5, "More than 5 high severity findings found"
        assert severity_count['CRITICAL'] == 0, "Critical severity findings found"

def lambda_handler(event, context):
    lambda_name = event['detail']['requestParameters']['functionName']
    
    test_class = TestLambdaRegressionSuite()
    test_class.set_lambda_name(lambda_name)
    
    # Run pytest programmatically
    result = subprocess.run(['pytest', '--tb=short', '-q'], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Tests failed:\n{result.stdout}\n{result.stderr}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Tests executed successfully')
    }
