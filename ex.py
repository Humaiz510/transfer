import boto3
import pytest
import paramiko
import json

# Initialize AWS clients
ec2_client = boto3.client('ec2')

def test_security_group_rules(instance_id, allowed_ip_ranges):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    security_groups = response['Reservations'][0]['Instances'][0]['SecurityGroups']
    
    for sg in security_groups:
        sg_id = sg['GroupId']
        sg_response = ec2_client.describe_security_groups(GroupIds=[sg_id])
        ingress_rules = sg_response['SecurityGroups'][0]['IpPermissions']
        
        for rule in ingress_rules:
            for ip_range in rule['IpRanges']:
                assert ip_range['CidrIp'] in allowed_ip_ranges, f"Unauthorized IP range found: {ip_range['CidrIp']}"

def test_network_acls(vpc_id, allowed_acl_entries):
    response = ec2_client.describe_network_acls(Filters=[{'Name': 'vpc-id', 'Values': [vpc_id]}])
    acls = response['NetworkAcls']
    
    for acl in acls:
        for entry in acl['Entries']:
            rule_action = entry['RuleAction']
            cidr_block = entry['CidrBlock']
            assert (cidr_block, rule_action) in allowed_acl_entries, f"Unexpected ACL entry found: {cidr_block} - {rule_action}"

def test_public_accessibility(instance_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    public_ip = instance.get('PublicIpAddress', None)
    
    assert public_ip is None, "Instance has a public IP address, making it publicly accessible"

def test_private_accessibility(instance_id, private_key_path, username, private_ip):
    key = paramiko.RSAKey(filename=private_key_path)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh_client.connect(private_ip, username=username, pkey=key)
        stdin, stdout, stderr = ssh_client.exec_command('echo "Hello, World!"')
        result = stdout.read().decode().strip()
        assert result == "Hello, World!", "Failed to access EC2 instance via private IP"
    finally:
        ssh_client.close()

def test_subnet_configuration(instance_id, expected_subnet_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    subnet_id = response['Reservations'][0]['Instances'][0]['SubnetId']
    
    assert subnet_id == expected_subnet_id, f"Instance is in subnet {subnet_id}, expected {expected_subnet_id}"

def test_route_table_configuration(subnet_id, expected_routes):
    response = ec2_client.describe_route_tables(Filters=[{'Name': 'association.subnet-id', 'Values': [subnet_id]}])
    route_table = response['RouteTables'][0]
    routes = route_table['Routes']
    
    for route in routes:
        destination_cidr = route['DestinationCidrBlock']
        target = route.get('GatewayId') or route.get('InstanceId') or route.get('NatGatewayId')
        assert (destination_cidr, target) in expected_routes, f"Unexpected route found: {destination_cidr} - {target}"

def test_elastic_ip_association(instance_id, expected_elastic_ip):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    public_ip = response['Reservations'][0]['Instances'][0].get('PublicIpAddress', None)
    
    assert public_ip == expected_elastic_ip, f"Instance has public IP {public_ip}, expected {expected_elastic_ip}"

def test_vpn_direct_connect_configuration(instance_id, remote_ip, private_key_path, username):
    key = paramiko.RSAKey(filename=private_key_path)
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh_client.connect(remote_ip, username=username, pkey=key)
        stdin, stdout, stderr = ssh_client.exec_command('ping -c 4 10.0.0.1')
        result = stdout.read().decode().strip()
        assert "4 packets transmitted, 4 received" in result, "Failed to communicate through VPN/Direct Connect"
    finally:
        ssh_client.close()

# Example test parameters
@pytest.mark.parametrize("instance_id, allowed_ip_ranges", [
    ("i-0abcd1234efgh5678", ["203.0.113.0/24", "198.51.100.0/24"])
])
def test_ec2_security_group_rules(instance_id, allowed_ip_ranges):
    test_security_group_rules(instance_id, allowed_ip_ranges)

@pytest.mark.parametrize("vpc_id, allowed_acl_entries", [
    ("vpc-0abcd1234efgh5678", [("203.0.113.0/24", "allow"), ("198.51.100.0/24", "deny")])
])
def test_ec2_network_acls(vpc_id, allowed_acl_entries):
    test_network_acls(vpc_id, allowed_acl_entries)

@pytest.mark.parametrize("instance_id", ["i-0abcd1234efgh5678"])
def test_ec2_public_accessibility(instance_id):
    test_public_accessibility(instance_id)

@pytest.mark.parametrize("instance_id, private_key_path, username, private_ip", [
    ("i-0abcd1234efgh5678", "/path/to/private-key.pem", "ec2-user", "10.0.0.1")
])
def test_ec2_private_accessibility(instance_id, private_key_path, username, private_ip):
    test_private_accessibility(instance_id, private_key_path, username, private_ip)

@pytest.mark.parametrize("instance_id, expected_subnet_id", [
    ("i-0abcd1234efgh5678", "subnet-0abcd1234efgh5678")
])
def test_ec2_subnet_configuration(instance_id, expected_subnet_id):
    test_subnet_configuration(instance_id, expected_subnet_id)

@pytest.mark.parametrize("subnet_id, expected_routes", [
    ("subnet-0abcd1234efgh5678", [("0.0.0.0/0", "igw-0abcd1234efgh5678")])
])
def test_ec2_route_table_configuration(subnet_id, expected_routes):
    test_route_table_configuration(subnet_id, expected_routes)

@pytest.mark.parametrize("instance_id, expected_elastic_ip", [
    ("i-0abcd1234efgh5678", "203.0.113.1")
])
def test_ec2_elastic_ip_association(instance_id, expected_elastic_ip):
    test_elastic_ip_association(instance_id, expected_elastic_ip)

@pytest.mark.parametrize("instance_id, remote_ip, private_key_path, username", [
    ("i-0abcd1234efgh5678", "198.51.100.1", "/path/to/private-key.pem", "ec2-user")
])
def test_ec2_vpn_direct_connect_configuration(instance_id, remote_ip, private_key_path, username):
    test_vpn_direct_connect_configuration(instance_id, remote_ip, private_key_path, username)