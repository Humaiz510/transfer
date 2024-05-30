import boto3
import json

def get_resource_arns_by_application(tag_key, tag_value):
    client = boto3.client('resourcegroupstaggingapi')
    response = client.get_resources(
        TagFilters=[
            {
                'Key': tag_key,
                'Values': [tag_value]
            }
        ]
    )
    resource_arns = [resource['ResourceARN'] for resource in response['ResourceTagMappingList']]
    return resource_arns

def get_lambda_function_details(lambda_client, function_arn):
    response = lambda_client.get_function(FunctionName=function_arn)
    configuration = response['Configuration']
    code = response['Code']
    
    return {
        'FunctionName': configuration['FunctionName'],
        'Handler': configuration['Handler'],
        'Role': configuration['Role'],
        'Runtime': configuration['Runtime'],
        'Code': {
            'S3Bucket': code['Location'].split('/')[-2],  # Extract S3 bucket name from code location URL
            'S3Key': code['Location'].split('/')[-1]  # Extract S3 key from code location URL
        }
    }

def get_s3_bucket_details(s3_client, bucket_name):
    response = s3_client.get_bucket_location(Bucket=bucket_name)
    location = response['LocationConstraint']
    
    return {
        'BucketName': bucket_name,
        'LocationConstraint': location
    }

def get_ec2_instance_details(ec2_client, instance_id):
    response = ec2_client.describe_instances(InstanceIds=[instance_id])
    instance = response['Reservations'][0]['Instances'][0]
    
    return {
        'InstanceId': instance['InstanceId'],
        'InstanceType': instance['InstanceType'],
        'KeyName': instance['KeyName'],
        'SubnetId': instance['SubnetId'],
        'SecurityGroupIds': [sg['GroupId'] for sg in instance['SecurityGroups']],
        'IamInstanceProfile': instance.get('IamInstanceProfile', {}).get('Arn')
    }

def create_cloudformation_template(resource_arns):
    resources = {}
    lambda_client = boto3.client('lambda')
    s3_client = boto3.client('s3')
    ec2_client = boto3.client('ec2')
    
    for arn in resource_arns:
        resource_type, resource_name = arn.split(':')[2], arn.split('/')[-1]
        
        if resource_type == 'lambda':
            lambda_details = get_lambda_function_details(lambda_client, arn)
            resources[resource_name] = {
                'Type': 'AWS::Lambda::Function',
                'Properties': lambda_details
            }
        elif resource_type == 's3':
            bucket_name = arn.split(':::')[-1]
            s3_details = get_s3_bucket_details(s3_client, bucket_name)
            resources[bucket_name] = {
                'Type': 'AWS::S3::Bucket',
                'Properties': {
                    'BucketName': s3_details['BucketName'],
                    'BucketEncryption': {
                        'ServerSideEncryptionConfiguration': [
                            {
                                'ServerSideEncryptionByDefault': {
                                    'SSEAlgorithm': 'AES256'
                                }
                            }
                        ]
                    }
                }
            }
        elif resource_type == 'ec2':
            instance_id = arn.split('/')[-1]
            ec2_details = get_ec2_instance_details(ec2_client, instance_id)
            resources[instance_id] = {
                'Type': 'AWS::EC2::Instance',
                'Properties': {
                    'InstanceType': ec2_details['InstanceType'],
                    'KeyName': ec2_details['KeyName'],
                    'SubnetId': ec2_details['SubnetId'],
                    'SecurityGroupIds': ec2_details['SecurityGroupIds'],
                    'IamInstanceProfile': ec2_details['IamInstanceProfile']
                }
            }
    
    cloudformation_template = {
        'AWSTemplateFormatVersion': '2010-09-09',
        'Resources': resources
    }
    
    return cloudformation_template

def deploy_cloudformation_stack(template_body, stack_name):
    client = boto3.client('cloudformation')
    response = client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Capabilities=['CAPABILITY_NAMED_IAM']
    )
    return response

# Example usage
application_tag_key = 'Application'
application_tag_value = 'MyApp'
resource_arns = get_resource_arns_by_application(application_tag_key, application_tag_value)
print("Resource ARNs:", resource_arns)

cloudformation_template = create_cloudformation_template(resource_arns)
cloud
