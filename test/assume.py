import boto3

def assume_role(account_id, role_name):
    sts_client = boto3.client('sts')
    role_arn = f'arn:aws:iam::{account_id}:role/{role_name}'
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName='DeployCloudFormationSession'
    )
    return response['Credentials']

def deploy_stack(template_body, stack_name, region, credentials):
    cf_client = boto3.client(
        'cloudformation',
        aws_access_key_id=credentials['AccessKeyId'],
        aws_secret_access_key=credentials['SecretAccessKey'],
        aws_session_token=credentials['SessionToken'],
        region_name=region
    )

    response = cf_client.create_stack(
        StackName=stack_name,
        TemplateBody=template_body,
        Capabilities=['CAPABILITY_NAMED_IAM', 'CAPABILITY_AUTO_EXPAND']
    )

    return response

# Configuration
target_account_id = 'TARGET_ACCOUNT_ID'
role_name = 'ROLE_NAME'
template_file_path = 'path_to_template_file.yaml'
stack_name = 'MyStack'
region = 'us-east-1'

# Assume role and deploy stack
credentials = assume_role(target_account_id, role_name)
template_body = open(template_file_path, 'r').read()
response = deploy_stack(template_body, stack_name, region, credentials)
print(response)
