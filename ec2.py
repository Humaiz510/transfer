import boto3
import pytest
from datetime import datetime, timedelta
import subprocess

class TestEC2RegressionSuite:
    
    @pytest.fixture(autouse=True)
    def setup(self):
        self.ec2_client = boto3.client('ec2')
        self.cloudwatch_client = boto3.client('cloudwatch')
        self.iam_client = boto3.client('iam')
        self.instance_id = None

    def set_instance_id(self, instance_id):
        self.instance_id = instance_id

    def test_instance_running(self):
        response = self.ec2_client.describe_instance_status(InstanceIds=[self.instance_id])
        statuses = response['InstanceStatuses']
        assert len(statuses) > 0, "Instance status not found"
        instance_state = statuses[0]['InstanceState']['Name']
        assert instance_state == 'running', f"Instance is not running, current state: {instance_state}"

    def test_valid_instance_type(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        instance_type = response['Reservations'][0]['Instances'][0]['InstanceType']
        valid_instance_types = ['t2.micro', 't2.small', 't2.medium', 't3.micro', 't3.small', 't3.medium']
        assert instance_type in valid_instance_types, f"Instance type {instance_type} is not valid"

    def test_instance_in_vpc(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        vpc_id = response['Reservations'][0]['Instances'][0].get('VpcId', None)
        assert vpc_id is not None, "Instance is not in a VPC"

    def test_security_groups_assigned(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        security_groups = response['Reservations'][0]['Instances'][0]['SecurityGroups']
        assert len(security_groups) > 0, "No security groups assigned to the instance"

    def test_no_public_ip(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        public_ip = response['Reservations'][0]['Instances'][0].get('PublicIpAddress', None)
        assert public_ip is None, "Instance has a public IP address"

    def test_instance_monitoring_enabled(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        monitoring_state = response['Reservations'][0]['Instances'][0]['Monitoring']['State']
        assert monitoring_state == 'enabled', "Instance monitoring is not enabled"

    def test_instance_has_iam_role(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        iam_instance_profile = response['Reservations'][0]['Instances'][0].get('IamInstanceProfile', None)
        assert iam_instance_profile is not None, "Instance does not have an IAM role assigned"

    def test_ebs_optimized(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        ebs_optimized = response['Reservations'][0]['Instances'][0].get('EbsOptimized', False)
        assert ebs_optimized, "Instance is not EBS optimized"

    def test_instance_tags(self):
        response = self.ec2_client.describe_tags(Filters=[{'Name': 'resource-id', 'Values': [self.instance_id]}])
        tags = {tag['Key']: tag['Value'] for tag in response['Tags']}
        assert 'Name' in tags, "Instance does not have a 'Name' tag"
        assert 'Project' in tags, "Instance does not have a 'Project' tag"
        assert 'Owner' in tags, "Instance does not have an 'Owner' tag"

    def test_instance_uptime(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        launch_time = response['Reservations'][0]['Instances'][0]['LaunchTime']
        now = datetime.utcnow()
        uptime = now - launch_time.replace(tzinfo=None)
        assert uptime.days <= 365, "Instance uptime exceeds 365 days"

    def test_instance_has_elastic_ip(self):
        response = self.ec2_client.describe_addresses(Filters=[{'Name': 'instance-id', 'Values': [self.instance_id]}])
        elastic_ips = response['Addresses']
        assert len(elastic_ips) == 0, "Instance has an Elastic IP assigned"

    def test_instance_cpu_utilization(self):
        response = self.cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='CPUUtilization',
            Dimensions=[{'Name': 'InstanceId', 'Value': self.instance_id}],
            StartTime=datetime.utcnow() - timedelta(days=1),
            EndTime=datetime.utcnow(),
            Period=300,
            Statistics=['Average']
        )
        datapoints = response['Datapoints']
        assert len(datapoints) > 0, "No CPU utilization data found"
        average_cpu_utilization = sum(dp['Average'] for dp in datapoints) / len(datapoints)
        assert average_cpu_utilization < 80, "Average CPU utilization exceeds 80%"

    def test_instance_network_in(self):
        response = self.cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkIn',
            Dimensions=[{'Name': 'InstanceId', 'Value': self.instance_id}],
            StartTime=datetime.utcnow() - timedelta(days=1),
            EndTime=datetime.utcnow(),
            Period=300,
            Statistics=['Sum']
        )
        datapoints = response['Datapoints']
        assert len(datapoints) > 0, "No NetworkIn data found"
        total_network_in = sum(dp['Sum'] for dp in datapoints)
        assert total_network_in < 100 * 1024 * 1024 * 1024, "Total NetworkIn exceeds 100 GB"

    def test_instance_network_out(self):
        response = self.cloudwatch_client.get_metric_statistics(
            Namespace='AWS/EC2',
            MetricName='NetworkOut',
            Dimensions=[{'Name': 'InstanceId', 'Value': self.instance_id}],
            StartTime=datetime.utcnow() - timedelta(days=1),
            EndTime=datetime.utcnow(),
            Period=300,
            Statistics=['Sum']
        )
        datapoints = response['Datapoints']
        assert len(datapoints) > 0, "No NetworkOut data found"
        total_network_out = sum(dp['Sum'] for dp in datapoints)
        assert total_network_out < 100 * 1024 * 1024 * 1024, "Total NetworkOut exceeds 100 GB"

    def test_instance_status_checks(self):
        response = self.ec2_client.describe_instance_status(InstanceIds=[self.instance_id])
        instance_status = response['InstanceStatuses'][0]['InstanceStatus']['Status']
        system_status = response['InstanceStatuses'][0]['SystemStatus']['Status']
        assert instance_status == 'ok', f"Instance status check failed: {instance_status}"
        assert system_status == 'ok', f"System status check failed: {system_status}"

    def test_instance_root_volume_encryption(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        root_device_name = response['Reservations'][0]['Instances'][0]['RootDeviceName']
        block_devices = response['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
        for device in block_devices:
            if device['DeviceName'] == root_device_name:
                ebs = device['Ebs']
                volume_id = ebs['VolumeId']
                volume = self.ec2_client.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
                assert volume['Encrypted'], "Root volume is not encrypted"

    def test_instance_attached_volumes_encryption(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        block_devices = response['Reservations'][0]['Instances'][0]['BlockDeviceMappings']
        for device in block_devices:
            volume_id = device['Ebs']['VolumeId']
            volume = self.ec2_client.describe_volumes(VolumeIds=[volume_id])['Volumes'][0]
            assert volume['Encrypted'], f"Volume {volume_id} is not encrypted"

    def test_instance_termination_protection(self):
        response = self.ec2_client.describe_instance_attribute(InstanceId=self.instance_id, Attribute='disableApiTermination')
        termination_protection = response['DisableApiTermination']['Value']
        assert termination_protection, "Instance termination protection is not enabled"

    def test_instance_backup(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        backup_tag = next((tag['Value'] for tag in tags if tag['Key'] == 'Backup'), None)
        assert backup_tag == 'True', "Instance does not have a backup tag set to 'True'"

    def test_instance_auto_scaling_group(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        asg_tag = next((tag['Value'] for tag in tags if tag['Key'] == 'aws:autoscaling:groupName'), None)
        assert asg_tag is not None, "Instance is not part of an Auto Scaling group"

    def test_instance_has_cloudwatch_logs_agent(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        tags = response['Reservations'][0]['Instances'][0]['Tags']
        cw_agent_tag = next((tag['Value'] for tag in tags if tag['Key'] == 'CloudWatchAgent'), None)
        assert cw_agent_tag == 'True', "Instance does not have CloudWatch Logs agent installed"

    def test_instance_accessibility(self):
        response = self.ec2_client.describe_instances(InstanceIds=[self.instance_id])
        state_reason = response['Reservations'][0]['Instances'][0].get('StateReason', {}).get('Message', '')
        assert state_reason == '', f"Instance is not accessible: {state_reason}"


def lambda_handler(event, context):
    instance_id = event['detail']['requestParameters']['instanceId']
    
    # Create an instance of the test class
    test_class = TestEC2RegressionSuite()
    test_class.setup()
    test_class.set_instance_id(instance_id)
    
    # Run pytest programmatically and capture the results
    result = subprocess.run(['pytest', '--tb=short', '-q'], capture_output=True, text=True)
    
    if result.returncode != 0:
        raise Exception(f"Tests failed:\n{result.stdout}\n{result.stderr}")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Tests executed successfully')
    }



"""
event bridge rule
{
  "source": ["aws.ec2"],
  "detail-type": ["AWS API Call via CloudTrail"],
  "detail": {
    "eventName": ["StartInstances", "StopInstances", "TerminateInstances", "RebootInstances"]
  }
}
"""
