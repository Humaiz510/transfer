import boto3
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

    def test_specific_vulnerabilities_absent(self, vulnerability_ids):
        start_of_day, end_of_day = self.get_today_date_range()
        findings = self.inspector_client.list_findings(
            filterCriteria={
                'resourceId': [{'comparison': 'EQUALS', 'value': self.lambda_name}],
                'vulnerabilityId': [{'comparison': 'EQUALS', 'value': vid} for vid in vulnerability_ids],
                'createdAt': [{'startInclusive': start_of_day, 'endExclusive': end_of_day}]
            }
        )['findings']
        
        assert len(findings) == 0, f"Specific vulnerabilities found: {findings}"
