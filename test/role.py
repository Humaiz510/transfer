import boto3
import json

# Initialize the IAM client
iam_client = boto3.client('iam')

# Define role and policy names (example names)
role_name = 'MyExampleRole'
inline_policy_name = 'MyExampleInlinePolicy'
managed_policy_name = 'AmazonS3ReadOnlyAccess'

# Fetch assume role policy document
assume_role_policy = iam_client.get_role(RoleName=role_name)['Role']['AssumeRolePolicyDocument']

# Fetch inline policy document
inline_policy = iam_client.get_role_policy(RoleName=role_name, PolicyName=inline_policy_name)['PolicyDocument']

# Fetch managed policy ARN
managed_policy_arn = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
managed_policy_arn = [policy['PolicyArn'] for policy in managed_policy_arn if policy['PolicyName'] == managed_policy_name][0]

# Create CloudFormation template with parameters
cloudformation_template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Parameters": {
        "RoleName": {
            "Type": "String",
            "Default": role_name
        },
        "InlinePolicyName": {
            "Type": "String",
            "Default": inline_policy_name
        },
        "ManagedPolicyArn": {
            "Type": "String",
            "Default": managed_policy_arn
        }
    },
    "Resources": {
        "MyIAMRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "AssumeRolePolicyDocument": assume_role_policy,
                "Policies": [
                    {
                        "PolicyName": {
                            "Ref": "InlinePolicyName"
                        },
                        "PolicyDocument": inline_policy
                    }
                ],
                "ManagedPolicyArns": [
                    {
                        "Ref": "ManagedPolicyArn"
                    }
                ],
                "RoleName": {
                    "Ref": "RoleName"
                }
            }
        }
    }
}

# Save CloudFormation template to a JSON file
with open('cloudformation_template.json', 'w') as f:
    json.dump(cloudformation_template, f, indent=4)

print("CloudFormation template saved to cloudformation_template.json")