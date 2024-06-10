import boto3
import json

# Initialize the IAM client
iam_client = boto3.client('iam')

# Define role name (example name)
role_name = 'MyExampleRole'

# Fetch role details
role = iam_client.get_role(RoleName=role_name)['Role']
assume_role_policy = role['AssumeRolePolicyDocument']

# Fetch inline policies
inline_policies = iam_client.list_role_policies(RoleName=role_name)['PolicyNames']
inline_policies_docs = {}
for policy_name in inline_policies:
    policy_doc = iam_client.get_role_policy(RoleName=role_name, PolicyName=policy_name)['PolicyDocument']
    inline_policies_docs[policy_name] = policy_doc

# Fetch managed policies
managed_policies = iam_client.list_attached_role_policies(RoleName=role_name)['AttachedPolicies']
managed_policy_arns = [policy['PolicyArn'] for policy in managed_policies]

# Create CloudFormation template with parameters
cloudformation_template = {
    "AWSTemplateFormatVersion": "2010-09-09",
    "Parameters": {
        "RoleName": {
            "Type": "String",
            "Default": role_name
        }
    },
    "Resources": {
        "MyIAMRole": {
            "Type": "AWS::IAM::Role",
            "Properties": {
                "AssumeRolePolicyDocument": assume_role_policy,
                "RoleName": {
                    "Ref": "RoleName"
                },
                "ManagedPolicyArns": managed_policy_arns,
                "Policies": []
            }
        }
    }
}

# Add inline policies to the template
for policy_name, policy_doc in inline_policies_docs.items():
    policy = {
        "PolicyName": policy_name,
        "PolicyDocument": policy_doc
    }
    cloudformation_template["Resources"]["MyIAMRole"]["Properties"]["Policies"].append(policy)

# Save CloudFormation template to a JSON file
with open('cloudformation_template.json', 'w') as f:
    json.dump(cloudformation_template, f, indent=4)

print("CloudFormation template saved to cloudformation_template.json")